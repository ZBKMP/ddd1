import logging
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from flask import Flask, current_app
from injector import inject
from networkx.classes import nodes
from redis import Redis
from sqlalchemy import func
from transformers.testing_utils import set_model_for_less_flaky_test

from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from internal.model import Document, Segment, KeywordTable, DatasetQuery, ProcessRule
from langchain_core.documents import Document as LCDocument
from .process_rule_service import ProcessRuleService
from .embeddings_service import EmbeddingsService
from .jieba_service import JiebaService
from .keyword_table_service import KeywordTableService
from .vector_store_service_new import WeaviateVectorStoreService
from internal.exception import NotFoundException
from weaviate.collections.classes.filters import Filter

from internal.core.file_extractor import FileExtractor
from internal.entity.dataset_entity import DocumentStatus, SegmentStatus
from internal.lib import generate_text_hash
from ..entity.cache_entity import LOCK_DOCUMENT_UPDATE_ENABLED


# 索引构建业务服务类
@inject
@dataclass
class IndexingService(BaseService):
    """索引构建服务"""
    db: SQLAlchemy
    file_extractor: FileExtractor
    process_rule_service: ProcessRuleService
    embeddings_service: EmbeddingsService
    jieba_service: JiebaService
    keyword_table_service: KeywordTableService
    vector_store_service: WeaviateVectorStoreService
    redis_client: Redis

    # 根据传递的文档id列表构建知识库文档
    def build_documents(
            self, document_ids: list[UUID]
    ) -> None:
        """根据传递的文档id列表构建知识库文档，
                           涵盖了加载、分割、索引构建、数据存储等内容"""
        # 1 根据传递的文档ID列表 查询文档数据
        documents = self.db.session.query(Document).filter(
            Document.id.in_(document_ids)
        ).all()

        # 2 循环遍历每个Document进行文档构建
        for document in documents:
            try:
                # 3 更新状态为 解析中 并记录开始处理的时间
                self.update(
                    document,
                    status=DocumentStatus.PARSING,
                    processing_started_at=datetime.now(),
                )

                # 4 执行文档解析 将Document(db.Model)转为Langchain中的Document列表
                lc_documents = self._parsing(document)
                # 5.执行文档分割步骤,将lc_documents分割再分割成片段,
                #   并更新文档(Document(db.Model))状态与时间，涵盖了片段的信息
                lc_segments = self._splitting(document, lc_documents)
                # 6 执行文档索引构建 关键词提取与存储,并更新文档数据状态
                self._indexing(document, lc_segments)
                # 7 存储操作，涵盖文档状态更新，以及向量数据库的存储 (多线程实现方案)
                self._completed_thread(document, lc_segments)

            except Exception as e:
                # 日志记录错误信息
                # logging.exception(f"构建文档发生错误，错误信息：{str(e)}")
                logging.exception("构建文档发生错误，错误信息：{err}".format(err=str(e)))

                # 修改文档状态为不可用
                self.update(
                    document,
                    status=DocumentStatus.ERROR,
                    error=str(e),
                    stopped_at=datetime.now(),
                )

    # 文档加载功能函数 : 读取Document(db.Model)对象,
    #                返回langchain_Document文档列表
    def _parsing(self, document: Document) -> list[LCDocument]:
        # 1 获取对应的UploadFile
        upload_file = document.upload_file
        # 使用之前定义的文档加载工具加载UploadFile生成LC文档列表
        # 实际只有一个Document对象,但被文档加载器加载后生成的是list[LCDocument]
        # COS云端文件下载 根据不同的文件使用不同加载器 得到LC文档列表
        lc_documents = self.file_extractor.load(
            upload_file=upload_file,
            return_text=False,
            is_unstructured=True,
        )

        # 2 循环处理Langchain 清理文本中的控制字符、无效的Unicode标记以及某些特定的格式符号，以保证文本的整洁性
        for lc_document in lc_documents:
            lc_document.page_content = self._clean_extra_text(
                lc_document.page_content,
            )

        # 3 更新文档状态并记录时间
        self.update(
            document,
            character_count=sum(
                [
                    len(lc_document.page_content)  # 错误修改
                    for lc_document in lc_documents
                ]
            ),  # 去掉多余空格之后统计该文档的字符数
            status=DocumentStatus.SPLITTING,  # 解析完成之后进入分割流程
            parsing_completed_at=datetime.now(),  # 记录解析完成的时间
        )
        # 最终返回list[LCDocument] 本质只有一个元素
        return lc_documents

    # 类方法 清理文本中的控制字符、无效的Unicode标记以及某些特定的格式符号，以保证文本的整洁性
    @classmethod
    def _clean_extra_text(cls, text: str) -> str:
        """清除过滤传递的多余空白字符串"""
        text = re.sub(r'<\|', '<', text)
        text = re.sub(r'\|>', '>', text)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F\xEF\xBF\xBE]', '', text)
        text = re.sub('\uFFFE', '', text)  # 删除零宽非标记字符
        return text

    # 文档分割功能函数
    def _splitting(
            self,
            document: Document,
            lc_documents: list[LCDocument]
    ) -> list[LCDocument]:
        # 1 得到该文档的处理规则 以及文档粉格子
        process_rule = document.process_rule  # 只读属性
        # 通过process_rule_service根据process_rule创建递归文本文档分割器
        text_splitter = self.process_rule_service.get_text_splitter_by_process_rule(
            # 传递处理规则
            process_rule=process_rule,
            # 传递文本长度计算函数(token长度)
            length_function=self.embeddings_service.calculate_token_count,
        )

        # 2 预处理规则:去掉空格 以及URL和email
        for lc_document in lc_documents:
            lc_document.page_content = self.process_rule_service.clean_text_by_process_rule(
                text=lc_document.page_content,
                process_rule=process_rule,
            )

        # 3 执行文档分割 获得片段文档列表[LCDocument]
        lc_segments = text_splitter.split_documents(lc_documents)

        # 4 获取当前文档下所有片段的最大位置
        position = self.db.session.query(
            func.coalesce(func.max(Segment.position), 0)
        ).filter(
            Segment.document_id == document.id,
        ).scalar()

        # 5 将每个片段信息Segment(Model)存储于数据表
        segments = []
        for lc_segment in lc_segments:
            position += 1
            # 获取片段内容
            content = lc_segment.page_content  # 错误修改
            # 存储至数据库
            segment = self.create(
                Segment,
                # 账号ID
                account_id=document.account_id,
                # 知识库ID
                dataset_id=document.dataset_id,
                # 文档ID
                document_id=document.id,
                # 节点ID (存储于向量库的ID)
                node_id=uuid.uuid4(),
                # 排序位置
                position=position,
                # 内容
                content=content,
                # 字符长度
                character_count=len(content),
                # token数量
                token_count=self.embeddings_service.calculate_token_count(content),
                # HASH值(作为数字签名)
                hash=generate_text_hash(content),
                # 状态 默认为等待中 此时还未处理完此文档片段
                status=SegmentStatus.WAITING,
            )
            # 加入到segments (Document)
            segments.append(segment)
            # 针对每个lc_segment(LCDocument)增加对应的元数据
            lc_segment.metadata = {
                "account_id": str(document.account_id),  # 数据库_账号ID
                "dataset_id": str(document.dataset_id),  # 数据库_知识库ID
                "document_id": str(document.id),  # 数据库_文档ID
                "segment_id": str(segment.id),  # 数据库_片段ID
                "node_id": str(segment.node_id),  # 节点ID
                "document_enabled": False,  # 文档状态 索引构建后改为True
                "segment_enabled": False,  # 片段状态
            }

        # 6 针对当前Document文档的分割处理已经完成
        self.update(
            document,
            # 统计该文档的token长度
            token_count=sum([
                segment.token_count for segment in segments
            ]),
            # 状态
            status=DocumentStatus.INDEXING,
            # 分割完成时间
            splitting_completed_at=datetime.now(),
        )

        # 7 返回LCDocument片段列表
        return lc_segments

    # 根据传递的信息构建索引:提取每个片段的关键词,并更新关键词表中
    #   对应当前知识库的关键词表信息,以便后续使用全文检索功能
    #   (以关键词去检索文档而非向量相似度).
    def _indexing(self,
                  document: Document,
                  lc_segments: list[LCDocument]
                  ) -> None:
        for lc_segment in lc_segments:
            # 1 遍历LCDocument列表 从其中的page_content提取出关键词
            segment_keywords = self.jieba_service.extract_keywords(
                text=lc_segment.page_content,
                max_keyword_pre_chunk=10,
            )

            # 2 逐条更新文档片段实体的关键词 使用update方法实现修改操作
            self.db.session.query(Segment).filter(
                Segment.id == lc_segment.metadata["segment_id"],
            ).update({
                # 关键词
                "keywords": segment_keywords,
                # 片段状态
                "status": SegmentStatus.INDEXING,
                # 索引构建完成时间
                "indexing_completed_at": datetime.now(),
            })

            # 3.调用keyword_table_service获取当前知识库的关键词表
            '''
                关键词表中keyword_table字段模拟数据:
                                {
                                  "2024": [  -- 关键词
                                    "68a6df4a-d102-4a25-80ed-16d11fe23a9d" -- 出现该关键词的片段ID
                                  ],
                                  "4o": [
                                    "9e4ea176-e4d9-4bee-92dd-7acf69fa7376"
                                  ],
                                  "GPT": [
                                    "9e4ea176-e4d9-4bee-92dd-7acf69fa7376",
                                    "68a6df4a-d102-4a25-80ed-16d11fe23a9d",
                                    "663fca2a-f986-471a-84a9-6606b2b25ed2",
                                    "551e2389-62d8-4be9-afef-e91fb28fb07b"
                                  ]
                                }
            '''
            keyword_table_record = self.keyword_table_service.get_keyword_table_from_dataset_id(
                document.dataset_id
            )

            # 重构keyword_table_record中的keyword_table属性(JSON-DICT),
            # 将该属性中的每一个value(list)转为set 以去除其中的重复数据
            keyword_table = {
                field: set(value)
                for field, value in keyword_table_record.keyword_table.items()
            }

            # 4 将当前片段的关键词表数据 记录到 知识库的关键词表数据中去
            '''
            segment_keywords=[1,2,3]
            
            keyword_table = {
                "1":[ ,segment_id],
                "2":[ ,segment_id],
                "4":[],
                "3":[segment_id]
            }
            '''
            for keyword in segment_keywords:
                if keyword not in keyword_table:
                    # 如果该关键词不在原有的关键词表keyword_table中,则为该关键词创建一个空集合
                    keyword_table[keyword] = set()
                # 从LCDocument中的元数据提取数据库中片段ID
                keyword_table[keyword].add(lc_segment.metadata["segment_id"])

            # 5 将添加了新内容的关键词表数据写回数据库 新加入的集合要转换成列表
            self.update(
                keyword_table_record,
                keyword_table={
                    field: list(value)
                    for field, value in keyword_table.items()
                },
            )

            # 6 更新文档状态
            self.update(
                document,
                # 更新索引构建完成时间
                indexing_completed_at=datetime.now(),
            )

    # 存储文档片段到向量数据库，并完成状态更新  多线程池方案实现
    def _completed_thread(
            self,
            document: Document,
            lc_segments: list[LCDocument]
    ) -> None:
        # 1 循环遍历片段列表 将元数据中文档状态和片段状态改为可使用
        for lc_segment in lc_segments:
            lc_segment.metadata["document_enabled"] = True
            lc_segment.metadata["segment_enabled"] = True

        # 2.调用向量数据库，每次存储10条数据，避免一次传递过多的数据--改造为多线程版本
        # 2.1 定义线程执行函数 参数包含当前flask应用对象,片段列表,片段ID列表
        def thread_func(
                flask_app: Flask,  # 当前Flask对象
                chunks: list[LCDocument],  # 文档列表切割后的片段
                ids: list[UUID],  # 存储于向量库的数据ID
        ) -> None:
            ''' 线程函数 执行向量数据库与postgres数据存储 '''
            # 以flask应用上下文执行以下代码 可以访问与flask绑定的db对象
            with flask_app.app_context():
                # 调用向量数据库服务 存储对应的数据
                self.vector_store_service.vector_store.add_documents(
                    documents=chunks,
                    ids=ids,  # 自定义向量数据的id
                )
                # 更新数据库中片段的状态以及完成时间
                with self.db.auto_commit():
                    # 执行一次批量修改
                    self.db.session.query(Segment).filter(
                        # Segment.node_id表示该片段存储于向量库的id
                        Segment.node_id.in_(ids)
                    ).update({
                        "status": SegmentStatus.COMPLETED,
                        "completed_at": datetime.now(),
                        "enabled": True,
                    })  # 更新这一批次的片段数据库信息

        # 2.2 将整个lc_segments 分割成多个子列表,每个子列表长度为10,每个子列表启动单独线程去完成
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []  # 保存所有要执行的任务的列表
            # 切割原始的lc_segments列表
            for i in range(0, len(lc_segments), 10):
                chunks = lc_segments[i:i + 10]
                ids = [chunk.metadata["node_id"] for chunk in chunks]
                # 创建一个线程执行的Future对象 参数包含线程要执行的方法,以及该方法需要的参数
                # 将每个返回的Future对象存入到futures列表
                futures.append(executor.submit(
                    # 子线程要执行的函数
                    thread_func,
                    # 函数需要的参数
                    current_app._get_current_object(), chunks, ids
                ))
            # 同时执行每个子线程
            for future in futures:
                future.result()

        # 3 更新文档的最终状态
        self.update(
            document,
            status=DocumentStatus.COMPLETED,
            completed_at=datetime.now(),
            enabled=True,
        )

    # 根据传递的文档id更新文档状态,同时修改weaviate向量数据库中的记录,
    # 同时修改关键词表中的关键词与片段ID
    def update_document_enabled_keyword_service(
            self,
            document_id: UUID
    ) -> None:
        # 1.构建缓存键  DocumentService.update_document_enabled方法
        #  在redis内创建了该缓存键,此处更新数据成功后,要删除该缓存键
        cache_key = LOCK_DOCUMENT_UPDATE_ENABLED.format(
            document_id=document_id
        )

        # 2 根据传递document_id查询Document数据对象
        document = self.get(Document, document_id)
        if document is None:
            logging.exception(f"当前文档不存在,文档ID:{document_id}")
            raise NotFoundException("当前文档不存在")

        # 3 查询文档下所有片段的node_id(向量库内的ID)
        segments = self.db.session.query(Segment).with_entities(
            Segment.id,
            Segment.node_id,
            Segment.enabled,
        ).filter(
            Segment.document_id == document_id,
            Segment.status == SegmentStatus.COMPLETED,  # 必须是已完成的状态才能修改enabled
        ).all()
        # 获取片段ID列表
        segment_ids = [id for id, _, _ in segments]
        # 获取片段Node_id列表
        node_ids = [node_id for _, node_id, _ in segments]

        try:
            # 4 遍历node_ids列表 更新向量库数据 获取向量库数据集操作
            collection = self.vector_store_service.collection
            for node_id in node_ids:
                # 修改片段信息发生异常则更新片段的数据
                try:
                    # 修改向量库数据的元数据
                    collection.data.update(
                        uuid=node_id,
                        properties={
                            "document_enabled": document.enabled,
                        }
                    )
                except Exception as e:
                    # 如果当前片段向量库操作发生异常 立即处理 不会影响到整体操作
                    # 标记该片段数据不可用 状态为ERROR
                    with self.db.auto_commit():
                        self.db.session.query(Segment).filter(
                            Segment.node_id == node_id,
                        ).update({
                            "error": str(e),
                            "status": SegmentStatus.ERROR,
                            "enabled": False,
                            "disabled_at": datetime.now(),
                            "stopped_at": datetime.now(),
                        })

            # 5.更新关键词表对应的数据 keyword_table 列
            #   enabled为false表示从关键词表中删除数据，
            #   enabled为true表示在关键词表中新增数据
            if document.enabled:  # false->ture
                # 6.从禁用改为启用，需要新增关键词
                # 找到片段数据中 所有为启用的片段 再生成对应关键词表数据
                enabled_segment_ids = [
                    id for id, _, enabled in segments if enabled is True
                ]
                self.keyword_table_service.add_keyword_table_from_ids(
                    dataset_id=document.dataset_id,
                    segment_ids=enabled_segment_ids,
                )

            else:  # true->false
                # 7.从启用改为禁用，需要剔除关键词
                # 将该Document下所有segment_ids都改为禁用
                self.keyword_table_service.delete_keyword_table_from_ids(
                    dataset_id=document.dataset_id,
                    segment_ids=segment_ids,
                )


        except Exception as e:
            # 修改文档信息发生异常则更新文档的数据
            # 5.记录日志并将状态修改回原来的状态
            logging.exception(
                f"修改向量数据库文档启用状态失败，"
                f"文档id：{document_id}，错误信息：{str(e)}"
            )
            # 将文档状态改回原来的状态
            origin_enabled = not document.enabled
            self.update(
                document,
                enabled=origin_enabled,
                disabled_at=None if origin_enabled else datetime.now(),
            )
        finally:
            # 6 最终执行redis锁的释放
            self.redis_client.delete(cache_key)

    # 根据传递的知识库id+文档id删除文档信息
    def delete_document_keyword_service(
            self,
            dataset_id: UUID,
            document_id: UUID
    ) -> None:
        # 1.查找该文档下的所有片段id列表
        segment_ids = [
            id for id, in self.db.session.query(Segment)
            .with_entities(Segment.id)
            .filter(
                Segment.document_id == document_id,
            ).all()
        ]

        # 2.调用向量数据库删除其关联记录
        # 只读属性 collection 获取向量库中项目使用的数据集
        collection = self.vector_store_service.collection
        # 删除该文档下所有向量库数据
        collection.data.delete_many(
            where=Filter.by_property("document_id").equal(document_id)
        )

        # 3.删除数据库中该文档包含的片段
        with self.db.auto_commit():
            self.db.session.query(Segment).filter(
                Segment.document_id == document_id,
            ).delete()

        # 4.删除片段id对应的关键词记录
        self.keyword_table_service.delete_keyword_table_from_ids(
            dataset_id,
            segment_ids,
        )

    # 根据传递的知识库id执行相应的删除操作
    def delete_dataset(self, dataset_id: UUID) -> None:
        try:
            with self.db.auto_commit():
                # 1.删除关联的文档记录
                self.db.session.query(Document).filter(
                    Document.dataset_id == dataset_id,
                ).delete()

                # 2.删除关联的片段记录
                self.db.session.query(Segment).filter(
                    Segment.dataset_id == dataset_id,
                ).delete()

                # 3.删除关联的关键词表记录
                self.db.session.query(KeywordTable).filter(
                    KeywordTable.dataset_id == dataset_id,
                ).delete()

                # 4.删除知识库查询记录
                self.db.session.query(DatasetQuery).filter(
                    DatasetQuery.dataset_id == dataset_id,
                ).delete()

            # 5. 删除向量库相关数据
            self.vector_store_service.collection.data.delete_many(
                where=Filter.by_property("dataset_id").equal(
                    str(dataset_id)
                )
            )

        except Exception as  e:
            logging.exception(
                f"异步删除知识库关联内容出错, dataset_id: {dataset_id}, 错误信息: {str(e)}"
            )


