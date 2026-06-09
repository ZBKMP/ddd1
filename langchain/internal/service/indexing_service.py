import logging
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from flask import Flask, current_app
from injector import inject
from redis import Redis
from sqlalchemy import func
from weaviate.collections.classes.filters import Filter

from pkg.sqlalchemy import SQLAlchemy
from . import WeaviateVectorStoreService

from .jieba_service import JiebaService
from .embeddings_service import EmbeddingsService
from .process_rule_service import ProcessRuleService
from .base_service import BaseService
from .keyword_table_service import KeywordTableService

from internal.entity.dataset_entity import DocumentStatus, SegmentStatus
from internal.model import Document, ProcessRule, Segment, KeywordTable, DatasetQuery
from langchain_core.documents import Document as LCDocument
from internal.core.file_extractor import FileExtractor
from internal.lib import generate_text_hash
from internal.entity.cache_entity import LOCK_DOCUMENT_UPDATE_ENABLED
from internal.exception import NotFoundException


# 索引构建业务服务类
@inject
@dataclass
class IndexingService(BaseService):
    """索引构建服务"""
    # 依赖注入
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
        # 1.根据传递的文档id列表获取所有文档
        documents = self.db.session.query(Document).filter(
            Document.id.in_(document_ids)
        ).all()

        # 2.执行循环遍历所有文档完成对每个文档的构建
        for document in documents:
            try:

                # 3.更新当前状态为解析中，并记录开始处理的时间
                self.update(
                    model_instance=document,
                    status=DocumentStatus.PARSING,
                    processing_started_at=datetime.now(),
                )

                # 4.执行文档加载步骤,将Document(db.Model)转为langchian中的Document列表,
                #   并更新文档的状态与时间
                lc_documents = self._parsing(document)

                # 5.执行文档分割步骤,将lc_documents分割再分割成片段,
                #   并更新文档(Document(db.Model))状态与时间，涵盖了片段的信息
                lc_segments = self._splitting(document, lc_documents)

                # 6.执行文档索引构建，涵盖关键词提取、向量，并更新数据状态
                self._indexing(document, lc_segments)

                # 7.存储操作，涵盖文档状态更新，以及向量数据库的存储
                self._completed_thread(document, lc_segments)


            except Exception as e:
                # 日志记录错误信息
                # logging.exception(f"构建文档发生错误，错误信息：{str(e)}")
                # 运维优化配置:优化日志输出 格式化输出替代f-string,
                #            仅在要输出该级别日志时才回去运行字符串内容计算,而f-string永远会计算
                logging.exception("构建文档发生错误，错误信息:%(error)s", {"error": e})

                # 修改文档数据 更新状态为不可用
                self.update(
                    document,
                    # 定义internal.entity.dataset_entity.DocumentStatus
                    # 包含多个文档状态常量的枚举类
                    status=DocumentStatus.ERROR,
                    error=str(e),
                    stopped_at=datetime.now(),
                )

    ###########################################################################################################

    # 文档加载功能函数 : 读取Document(db.Model)对象,
    #                返回langchain_Document文档列表
    def _parsing(
            self, document: Document
    ) -> list[LCDocument]:
        """解析传递的文档为LangChain文档列表"""
        # 1.获取upload_file并加载LangChain文档
        # Document.upload_file只读属性,得到UploadFile对象
        upload_file = document.upload_file
        # 使用自定义的通用文件提取器 加载腾讯云COS云端文件
        lc_documents = self.file_extractor.load(
            upload_file=upload_file,
            return_text=False,  # 返回langchain的Document列表
            is_unstructured=True,
        )

        # 2.循环处理LangChain文档，并删除多余的特殊字符串
        for lc_document in lc_documents:
            #  方法_clean_extra_text 去除多余空格
            lc_document.page_content = self._clean_extra_text(
                lc_document.page_content
            )

        # 3.更新文档状态并记录时间
        self.update(
            model_instance=document,
            # 统计字符数 统计lc_documents 中所有文档内容的长度
            character_count=sum([
                len(lc_document.page_content)
                for lc_document in lc_documents
            ]),
            # 更新状态为分割中
            status=DocumentStatus.SPLITTING,
            # 解析完成时间
            parsing_completed_at=datetime.now(),
        )

        # 返回 lc_documents 文档列表
        return lc_documents

    # 类方法 清理文本中的控制字符、无效的Unicode标记以及某些特定的格式符号，以保证文本的整洁性
    @classmethod
    def _clean_extra_text(cls, text: str) -> str:
        """清除过滤传递的多余空白字符串"""
        # 将传入的text中 符合pattern的文字部分 替换成repl对应的值
        text = re.sub(r'<\|', '<', text)
        text = re.sub(r'\|>', '>', text)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F\xEF\xBF\xBE]', '', text)
        text = re.sub('\uFFFE', '', text)  # 删除零宽非标记字符
        return text

    # 文档分割功能函数
    def _splitting(
            self,
            document: Document,  # 数据库中的文档对象 以获取处理规则
            lc_documents: list[LCDocument]  # 需要进行分割的langchain文档列表
    ) -> list[LCDocument]:
        """根据传递的信息进行文档分割，拆分成小块片段"""
        # 1.根据process_rule获取文本分割器
        # Document.process_rule只读属性,读取处理规则信息
        process_rule = document.process_rule

        # 通过process_rule_service获取文本分割器,得到一个递归文本分割器
        text_splitter = self.process_rule_service.get_text_splitter_by_process_rule(
            process_rule=process_rule,
            length_function=self.embeddings_service.calculate_token_count,
        )

        # 2.按照process_rule规则清除多余的字符串
        for lc_document in lc_documents:
            # 处理每个lc_document 清除多余内容(空格 邮箱 url地址)
            lc_document.page_content = self.process_rule_service.clean_text_by_process_rule(
                text=lc_document.page_content,
                process_rule=process_rule,
            )

        # 3.进行文档分割  结果为片段 segments
        lc_documents = text_splitter.split_documents(lc_documents)

        # 4.获取对应文档下得到最大片段位置 (func.coalesce 没有结果返回0)
        position = self.db.session.query(
            func.coalesce(func.max(Segment.position), 0)
        ).filter(
            Segment.document_id == document.id,
        ).scalar()  # 查询结果的第一行第一列

        # 5.循环处理片段数据并添加元数据，同时存储到postgres数据库中
        segments = []
        for lc_document in lc_documents:
            # 片段位置
            position += 1  # 每个片段的位置 都在当前文档下最后片段位置+1
            # 片段内容
            content = lc_document.page_content
            # 将片段信息存储到数据
            segment = self.create(
                Segment,
                account_id=document.account_id,  # 账号ID
                dataset_id=document.dataset_id,  # 知识库ID
                document_id=document.id,  # 文档ID
                node_id=uuid.uuid4(),  # 后续存到向量库时 这个lc_document的ID
                position=position,  # 顺序位置
                content=content,  # 内容
                character_count=len(content),  # 字符长度
                token_count=self.embeddings_service.calculate_token_count(content),  # token长度
                hash=generate_text_hash(content),  # 内容hash值
                status=SegmentStatus.WAITING,  # 片段的初始状态
                processing_started_at=datetime.now(),  # 片段开始处理时间
            )
            # 加入到片段列表
            segments.append(segment)

            ## 为langchain文档片段生成向量库中的元数据信息
            lc_document.metadata = {
                "account_id": str(document.account_id),  # 账号ID
                "dataset_id": str(document.dataset_id),  # 知识库ID
                "document_id": str(document.id),  # 文档ID
                "segment_id": str(segment.id),  # 片段ID
                "node_id": str(segment.node_id),  # 向量库 节点ID
                "document_enabled": False,  # 文档状态 索引构建后改为True
                "segment_enabled": False,  # 片段状态
            }

        # 6.更新文档实体的数据，涵盖状态、token数等内容
        self.update(
            document,
            token_count=sum([
                segment.token_count for segment in segments
            ]),  # 每个文档的token总数
            status=DocumentStatus.INDEXING,  # 状态改为 全文检索构建中
            splitting_completed_at=datetime.now(),  # 记录文档分割完成时间
        )

        # 返回langchain文档列表
        return lc_documents

    # 根据传递的信息构建索引:提取每个片段的关键词,并更新关键词表中
    #   对应当前知识库的关键词表信息,以便后续使用全文检索功能
    #   (以关键词去检索文档而非向量相似度).
    def _indexing(
            self,
            document: Document,  # 文档数据库数据
            lc_segments: list[LCDocument]  # 分割之后的langchain文档片段
    ) -> None:
        """根据传递的信息构建索引，涵盖关键词提取、词表构建"""
        for lc_segment in lc_segments:
            # 1.使用 jieba_service 提取每一个片段对应的关键词，
            #   关键词的数量最多不超过10个  ['k1','k2',.....]
            keywords = self.jieba_service.extract_keywords(
                text=lc_segment.page_content,
                max_keyword_pre_chunk=10,
            )

            # 2.逐条更新文档片段实体的关键词
            self.db.session.query(Segment).filter(
                Segment.id == lc_segment.metadata["segment_id"],
            ).update({
                "keywords": keywords,  # 数据值为多个关键词组成的字符列表
                "status": SegmentStatus.INDEXING,  # 更新片段的数据状态为 关键词索引构建中
            })  # 根据条件查询数据,更新查询到的数据

            # 3.调用keyword_table_service获取当前知识库的关键词表
            keyword_table_record = self.keyword_table_service.get_keyword_table_from_dataset_id(
                dataset_id=document.dataset_id,
            )
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
                      ],
                      ....
                    }
            '''

            # 重构keyword_table_record中的keyword_table属性(JSON-DICT),
            # 将该属性中的每一个value(list)转为set 以去除其中的重复数据
            keyword_table = {
                field: set(value)
                for field, value in keyword_table_record.keyword_table.items()
            }

            # 4 将当前片段的关键词列表keywords 的数据 填入到该片段所在知识库的关键词表数据keyword_table中
            for keyword in keywords:
                # 该关键词之前在整个知识库中从未出现过,则在该知识库的关键词表数据中添加一个新key
                if keyword not in keyword_table:
                    keyword_table[keyword] = set()
                # 将片段ID存储到 keyword_table[keyword] 对应的set集合中
                keyword_table[keyword].add(lc_segment.metadata["segment_id"])

            # 5 将添加好数据的keyword_table更新回关键词表
            self.update(
                keyword_table_record,
                # 更新 keyword_table,存储到数据库时再将set改回list
                keyword_table={
                    field: list(value)
                    for field, value in keyword_table.items()
                }
            )

            # 片段状态修改
            self.db.session.query(Segment).filter(
                Segment.id == lc_segment.metadata["segment_id"],
            ).update({
                "indexing_completed_at": datetime.now(),  # 索引构建完成时间
            })  # 根据条件查询数据,更新查询到的数据

        # 6.更新文档状态
        self.update(
            document,
            # 更新索引构建完成时间
            indexing_completed_at=datetime.now(),
        )

    # 存储文档片段到向量数据库，并完成状态更新  基于多线程实现
    def _completed_thread(
            self,
            document: Document,  # 文档数据库数据
            lc_segments: list[LCDocument]  # 分割之后的langchain文档片段
    ):
        """存储文档片段到向量数据库，并完成状态更新"""
        # 1.循环遍历片段列表数据，将文档状态及片段状态设置成True
        for lc_segment in lc_segments:
            lc_segment.metadata["document_enabled"] = True
            lc_segment.metadata["segment_enabled"] = True

        # 2.调用向量数据库，每次存储10条数据，避免一次传递过多的数据--多线程
        # a.定义线程执行函数 参数包含当前flask应用对象,片段列表,片段ID列表
        def thread_func(
                flask_app: Flask,
                chunks: list[LCDocument],
                node_ids: list[UUID]
        ) -> None:
            ''' 线程函数 执行向量数据库与postgres数据存储 '''
            # 当前代码是在异步环境下执行 在celery服务下执行 需要能获取flask服务下的上下文(db：Flask SQLAlchemy对象)
            with flask_app.app_context():
                # 调用向量数据库服务 存储对应的数据
                self.vector_store_service.vector_store.add_documents(
                    documents=chunks,
                    ids=node_ids,  # 向量数据的ID 是自定义的
                )

                # 更新数据库中片段的状态以及完成时间
                with self.db.auto_commit():
                    self.db.session.query(Segment).filter(
                        Segment.node_id.in_(node_ids)
                    ).update({
                        "status": SegmentStatus.COMPLETED,  # 片段已完成
                        "completed_at": datetime.now(),  # 片段已完成
                        "enabled": True,  # 片段可用
                    })

        # b 创建线程池(最大数量5) 在线程池上下文中完成一下操作
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []  # 线程执行的Future对象列表

            # 每次存储10条数据，避免一次传递过多的数据改造为多线程版本
            for i in range(0, len(lc_segments), 10):  # 0-9 10-19 20-29
                segment_chunks = lc_segments[i:i + 10]
                # 从片段文档中取出元数据 node_id
                node_ids = [chunk.metadata["node_id"] for chunk in segment_chunks]
                # 以当前10个元素作为任务启动一个线程 生成一个Future任务 加入到列表中
                futures.append(
                    executor.submit(
                        thread_func,
                        flask_app=current_app._get_current_object(),
                        chunks=segment_chunks,
                        node_ids=node_ids,
                    )
                )

            # 等待每个Future执行完成
            for future in futures:
                future.result()

        # 6.更新文档的状态数据
        self.update(
            model_instance=document,
            status=DocumentStatus.COMPLETED,  # 文档已完成
            completed_at=datetime.now(),  # 文档已完成
            enabled=True,
        )

    ##############################################################################

    # 根据传递的文档id更新文档状态,同时修改weaviate向量数据库中的记录,
    # 同时修改关键词表中的关键词与片段ID
    def update_document_enabled_keyword_service(
            self,
            document_id: UUID
    ) -> None:
        """根据传递的文档id更新文档状态，同时修改weaviate向量数据库中的记录"""
        # 1.构建缓存锁  DocumentService.update_document_enabled方法
        #  在redis内创建了该缓存键,此处更新数据成功后,要删除该缓存键
        cache_key = LOCK_DOCUMENT_UPDATE_ENABLED.format(
            document_id=document_id
        )

        # 2.根据传递的document_id获取文档记录
        document = self.get(Document, document_id)
        if document is None:
            logging.exception(f"当前文档不存在，文档id：{document_id}")
            raise NotFoundException("当前文档不存在")

        # 3.查询归属于当前文档的所有片段的节点id
        # 查询 Segment.id, Segment.node_id, Segment.enabled 生成元祖
        # [(x,x,x),(x,x,x),(x,x,x),....]
        segments = self.db.session.query(Segment).with_entities(
            Segment.id,
            Segment.node_id,
            Segment.enabled,
        ).filter(
            Segment.document_id == document.id,  # 文档ID为检索条件
            Segment.status == SegmentStatus.COMPLETED,  # 只能处理已完成的片段
        ).all()
        # 从以上数据库查询结果中 提取出所有的segment.id
        segment_ids = [id for id, _, _ in segments]
        # 从以上数据库查询结果中 提取出所有的segment.node_id
        node_ids = [node_id for _, node_id, _ in segments]

        try:
            # 4.执行循环遍历所有node_ids并更新向量数据 元数据 enabled
            # 只读属性:vector_database_service.collection 获取指定数据集
            collection = self.vector_store_service.collection

            for node_id in node_ids:
                try:
                    # 循环修改向量数据中该文档下所有片段的启用状态
                    collection.data.update(
                        uuid=node_id,  # 以向量数据ID为修改条件
                        properties={
                            "document_enabled": document.enabled,
                            "segment_enabled": document.enabled,
                        }
                    )
                    # 同步更新该片段在数据中的启用状态
                    segment = self.db.session.query(Segment).filter(
                        Segment.node_id == node_id
                    ).one_or_none()
                    # 修改数据
                    self.update(
                        segment,
                        enabled=document.enabled,
                        disabled_at=None if document.enabled else datetime.now(),  # 禁用
                    )

                except Exception as e:
                    # 如果当前片段向量库操作发生异常 立即处理 不会影响到整体操作
                    # 标记该片段数据不可用 状态为ERROR
                    with self.db.auto_commit():
                        self.db.session.query(Segment).filter(
                            Segment.node_id == node_id
                        ).update({
                            "error": str(e),
                            "status": SegmentStatus.ERROR,
                            "stopped_at": datetime.now(),
                        })

            # 5 更新关键词表对应的数据 禁用(清除关键词表中所有片段信息) 启用(增加关键词表中所有片段信息)
            #   enabled为false表示从关键词表中删除数据，
            #   enabled为true表示在关键词表中新增数据
            if document.enabled is True:
                # 6.从禁用改为启用，需要新增关键词
                # 找到片段数据中 所有为启用的片段 再生成对应关键词表数据
                enable_segment_ids = self.db.session.query(Segment).with_entities(
                    Segment.id,
                ).filter(
                    Segment.document_id == document.id,  # 文档ID为检索条件
                    Segment.status == SegmentStatus.COMPLETED,  # 只能处理已完成的片段
                    Segment.enabled == True,
                ).all()  # 当前文档下 status:completed以及enabled为True的片段
                # [(id),(id),(id)] --> [id,id,id...]
                enable_segment_ids = [id for id, in enable_segment_ids]

                self.keyword_table_service.add_keyword_table_from_ids(
                    dataset_id=document.dataset_id,  # 知识库ID
                    segment_ids=enable_segment_ids,  # 要添加关键词的片段ID列表
                )
            else:
                # 7.从启用改为禁用，需要剔除关键词
                disabled_segment_ids = self.db.session.query(Segment).with_entities(
                    Segment.id,
                ).filter(
                    Segment.document_id == document.id,  # 文档ID为检索条件
                    Segment.status == SegmentStatus.COMPLETED,  # 只能处理已完成的片段
                    Segment.enabled == False,
                ).all()  # 当前文档下 status:completed以及enabled为False的片段
                # [(id),(id),(id)] --> [id,id,id...]
                disabled_segment_ids = [id for id, in disabled_segment_ids]

                self.keyword_table_service.delete_keyword_table_from_ids(
                    dataset_id=document.dataset_id,  # 知识库ID
                    segment_ids=disabled_segment_ids,  # 要添加关键词的片段ID列表
                )

        except Exception as e:
            # 5. 处理整个文档如果出错   记录日志并将状态修改回原来的状态
            logging.exception(
                f"修改向量数据库文档启用状态失败，"
                f"文档id：{document_id}，错误信息：{str(e)}"
            )
            origin_enabled = not document.enabled  # 原始状态必然和当前需要改成的状态相反
            self.update(
                document,
                enabled=origin_enabled,
                disabled_at=None if origin_enabled else datetime.now(),
            )

        finally:
            # 6.清空缓存键表示异步操作已经执行完成，无论失败还是成功都全部清除
            self.redis_client.delete(cache_key)

    # 根据传递的知识库id+文档id删除文档信息
    def delete_document_keyword_service(
            self,
            dataset_id: UUID,
            document_id: UUID
    ) -> None:
        """根据传递的知识库id+文档id删除文档信息"""
        # 1.查找该文档下的所有片段id列表
        segment_ids = self.db.session.query(Segment).with_entities(
            Segment.id,
        ).filter(
            Segment.document_id == document_id,
        ).all()
        # [(id),(id),(id),....] => [id,id,id]
        segment_ids = [id for id, in segment_ids]

        # 2.调用向量数据库删除其关联记录
        # 只读属性 collection 获取向量库中项目使用的数据集
        collection = self.vector_store_service.collection
        collection.data.delete_many(
            where=Filter.by_property("document_id").equal(document_id)  # 元数据过滤
        )

        # 3.删除数据库下该document关联的segment记录
        with self.db.auto_commit():
            self.db.session.query(Segment).filter(
                Segment.document_id == document_id,
            ).delete()

        # 4.删除片段id对应的关键词记录
        self.keyword_table_service.delete_keyword_table_from_ids(
            dataset_id=dataset_id,
            segment_ids=segment_ids,
        )

        #  将上述代码包装在 try except finally中关闭缓存锁

    # 根据传递的知识库id执行相应的删除操作
    def delete_dataset(self, dataset_id: UUID) -> None:
        """根据传递的知识库id执行相应的删除操作"""
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

            # 5.调用向量数据库删除知识库的关联记录
            self.vector_store_service.collection.data.delete_many(
                # 元数据作为搜索条件
                where=Filter.by_property("dataset_id").equal(
                    str(dataset_id)
                )
            )
        except Exception as e:
            logging.exception(
                f"异步删除知识库关联内容出错, dataset_id: {dataset_id}, 错误信息: {str(e)}"
            )
