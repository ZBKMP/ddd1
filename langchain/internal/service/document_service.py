import logging
import time
from dataclasses import dataclass
import random
from datetime import datetime
from uuid import UUID

from injector import inject
from redis import Redis
from sqlalchemy import desc, asc, func

from pkg.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from internal.entity.dataset_entity import ProcessType, SegmentStatus, DocumentStatus
from internal.model import Document, Dataset, UploadFile, ProcessRule, Segment, Account
from internal.entity.upload_file_entity import ALLOWED_DOCUMENT_EXTENSION
from internal.exception import ForbiddenException, NotFoundException, FailException

from internal.task.document_task import (
    build_documents,
    update_document_enabled,
    delete_document,
)
from internal.entity.cache_entity import LOCK_DOCUMENT_UPDATE_ENABLED, LOCK_EXPIRE_TIME
from internal.lib import datetime_to_timestamp
from internal.schema import GetDocumentsWithPageReq


@inject
@dataclass
class DocumentService(BaseService):
    # 依赖注入
    db: SQLAlchemy
    redis_client: Redis

    # 根据传入的参数创建文档实体列表, 并调用异步任务
    def create_documents(
            self,
            dataset_id: UUID,
            upload_file_ids: list[UUID],  # 文件ID列表
            process_type: str = ProcessType.AUTOMATIC,  # 处理规则类型
            rule: dict = None,  # 规则内容
            account:Account = None,
    ) -> tuple[list[Document], str]:  # 返回Document实体列表与处理批次str
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个 账号ID account_id
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id=str(account.id)

        # 1 检测知识库权限
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise ForbiddenException(
                "当前用户无该知识库操作权限,或该知识库不存在!"
            )

        # 2 提取文件 并校验文件权限与文件扩展
        upload_files = self.db.session.query(UploadFile).filter(
            UploadFile.account_id == account_id,  # 账号条件
            UploadFile.id.in_(upload_file_ids),  # 文件ID列表条件
        ).all()

        # 只保留允许上传的文件类型
        upload_files = [
            upload_file for upload_file in upload_files
            if upload_file.extension.lower() in ALLOWED_DOCUMENT_EXTENSION
        ]

        # 提取之后如果列表中没有数据了 则抛出异常
        if len(upload_files) == 0:
            # 出现异常 记录日志
            logging.warning(
                f"上传的文档列表未解析到合法文件 "
                f"account_id:{account_id} dataset_id:{dataset_id} "
                f"upload_file_id:{upload_file_ids}"
            )
            # 抛出自定义异常
            raise ForbiddenException(
                "上传的文档列表未解析到合法文件,请重新上传"
            )

        # 3 创建批次与处理规则并记录到数据库中
        # 生成批次信息(当前时间再拼接一个随机数)
        batch = time.strftime("%Y%m%d%H%M%S") + str(random.randint(100000, 999999))

        # 数据库添加处理规则数据
        process_rule = self.create(
            ProcessRule,
            account_id=account_id,
            dataset_id=dataset_id,
            mode=process_type,
            rule=rule,  # 处理规则
        )

        # 4 调用方法:获取当前知识库的最新文档位置 （最后一个文档的position数字再+1）
        position = self.get_latest_document_position(dataset_id)

        # 5 循环遍历所有合法的上传文件列表  并记录到数据库 生成Document
        documents = []
        for upload_file in upload_files:
            position += 1  # 后一个文档的position数字再+1
            document = self.create(
                Document,
                account_id=account_id,
                dataset_id=dataset_id,
                upload_file_id=upload_file.id,  # 文件ID
                process_rule_id=process_rule.id,  # 刚添加成功的处理规则的ID
                batch=batch,
                name=upload_file.name,
                position=position,
            )
            documents.append(document)

        # 6.完成异步任务函数后 调用异步任务 完成后续操作:
        #  文档切割 生成索引(关键词) 存储片段到数据库与向量库
        build_documents.delay(
            [document.id for document in documents]
        )

        # 7. 返回结果 文档列表+处理批次组合成的元祖
        return documents, batch

    # 获取指定知识库的最新文档位置
    def get_latest_document_position(
            self,
            dataset_id: UUID
    ):
        # 根据position倒序排列 查出第一个数据
        document = self.db.session.query(Document).filter(
            Document.dataset_id == dataset_id,
        ).order_by(desc("position")).first()
        # 有数据则最新位置为该文档的position数据 否则为0
        return document.position if document else 0

    # 根据dataset_id与batch批处理标识获取文档状态
    def get_documents_status(
            self,
            dataset_id: UUID,
            batch: str,
            account: Account,
    ) -> list[dict]:
        """根据传递的知识库id+处理批次获取文档列表的状态"""
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个 账号ID account_id
        # 完成授权认证模块后去掉,从Account参数内容获取
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.检测知识库权限
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise ForbiddenException("当前用户无该知识库权限或知识库不存在")

        # 2.根据 知识库ID 以及批次信息 查询文档Document列表
        documents = self.db.session.query(Document).filter(
            Document.dataset_id == dataset_id,  # 知识库ID
            Document.batch == batch,  # 批次信息
        ).order_by(asc("position")).all()
        if documents is None or len(documents) == 0:
            raise NotFoundException("该处理批次未发现文档，请核实后重试")

        # 3.循环遍历文档列表提取文档的状态信息
        documents_status = []  # 最终结果列表
        for document in documents:
            # 4.查询每个文档的总片段数
            segment_count = document.segment_count
            # 5.查询每个文档的已构建完成的片段数
            completed_segment_count = self.db.session.query(
                func.count(Segment.id)
            ).filter(
                Segment.document_id == document.id,
                Segment.status == SegmentStatus.COMPLETED,
                Segment.enabled == True,
            ).scalar()
            # 6 提取原文件信息
            upload_file = document.upload_file
            # 7 组合状态信息字典 添加至列表
            documents_status.append({
                "completed_segment_count": completed_segment_count,
                "error": document.error,
                "extension": upload_file.extension,
                "id": document.id,
                "mime_type": upload_file.mime_type,
                "name": document.name,
                "position": document.position,
                "segment_count": segment_count,
                "size": upload_file.size,
                "status": document.status,
                # 各个时间数据值  由datatime都转换为时间戳或0
                "stopped_at": datetime_to_timestamp(document.stopped_at),
                "created_at": datetime_to_timestamp(document.created_at),
                "completed_at": datetime_to_timestamp(document.completed_at),
                "parsing_completed_at": datetime_to_timestamp(document.parsing_completed_at),
                "processing_started_at": datetime_to_timestamp(document.processing_started_at),
                "splitting_completed_at": datetime_to_timestamp(document.splitting_completed_at),
            })
        return documents_status

    # 根据传递的知识库id+文档id获取文档记录信息
    def get_document(
            self,
            dataset_id: UUID,
            document_id: UUID,
            account: Account,
    ) -> Document:
        """根据传递的知识库id+文档id获取文档记录信息"""
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个 账号ID account_id
        # 完成授权认证模块后去掉,从Account参数内容获取
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 查询对应的文档记录
        document = self.get(Document, document_id)
        # 文档不存在 抛出异常
        if document is None:
            raise NotFoundException("该文档不存在，请核实后重试")
        # 知识库ID或账号ID不匹配
        if (
                document.dataset_id != dataset_id
                or
                str(document.account_id) != account_id  # 虚拟账号为str
        ):
            raise ForbiddenException("当前用户获取该文档，请核实后重试")

        # 返回查询结果
        return document

    # 根据传递的知识库id+文档id，更新文档信息
    def update_document(
            self,
            dataset_id: UUID,
            document_id: UUID,
            account: Account,
            **kwargs,
    ) -> Document:
        """根据传递的知识库id+文档id，更新文档信息"""
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个 账号ID account_id
        # 完成授权认证模块后去掉,从Account参数内容获取
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        document = self.get(Document, document_id)
        if document is None:
            raise NotFoundException("该文档不存在，请核实后重试")
        if (document.dataset_id != dataset_id
                or
                str(document.account_id) != account_id):
            raise ForbiddenException("当前用户无权限修改该文档，请核实后重试")

        return self.update(document, **kwargs)

    # 根据传递的知识库id+请求数据获取文档分页列表数据
    def get_documents_with_page(
            self,
            dataset_id: UUID,
            req: GetDocumentsWithPageReq,
            account: Account,
    ) -> tuple[list[Document], Paginator]:
        """根据传递的知识库id+请求数据获取文档分页列表数据"""
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个 账号ID account_id
        # 完成授权认证模块后去掉,从Account参数内容获取
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.获取知识库并校验权限
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在，或无权限")

        # 2.构建分页查询器
        paginator = Paginator(db=self.db, req=req)

        # 3.构建筛选器
        # 查询条件
        filters = [
            Document.account_id == account_id,
            Document.dataset_id == dataset_id,
        ]
        # 使用搜索关键字对文档名称进行模糊查询
        if req.search_word.data:
            filters.append(
                Document.name.like(f"%{req.search_word.data}%")
            )

        # 4.执行分页并获取数据
        documents = paginator.paginate(
            self.db.session.query(Document)
            .filter(*filters)
            .order_by(desc("created_at"))
        )
        # 返回数据结果以及分页数据
        return documents, paginator

    # 根据传递的知识库id+文档id，更新文档的启用状态，同时会异步更新weaviate向量数据库中的数据
    def update_document_enabled(
            self,
            dataset_id: UUID,
            document_id: UUID,
            enabled: bool,  # 目标状态
            account: Account,
    ) -> Document:
        """根据传递的知识库id+文档id，更新文档的启用状态，
                    同时会异步更新weaviate向量数据库中的数据"""
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个 账号ID account_id
        # 完成授权认证模块后去掉,从Account参数内容获取
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.获取文档并校验权限
        document = self.get(Document, document_id)
        if document is None:
            raise NotFoundException("该文档不存在，请核实后重试")
        if (document.dataset_id != dataset_id
                or
                str(document.account_id) != account_id):
            raise ForbiddenException(
                "当前用户无权限修改该知识库下的文档，请核实后重试"
            )

        # 2.判断文档是否处于可以修改的状态，只有构建完成才可以修改enabled
        if document.status != DocumentStatus.COMPLETED:
            raise ForbiddenException(
                "当前文档处于不可修改状态，请稍后重试"
            )

        # 3.判断修改的启用状态是否正确，需与当前的状态相反
        if document.enabled == enabled:
            raise FailException(
                f"文档状态修改错误，当前已是{'启用' if enabled else '禁用'}状态"
            )

        # 4.获取更新文档启用状态的redis缓存键,用于在修改时上锁
        cache_key = LOCK_DOCUMENT_UPDATE_ENABLED.format(
            document_id=document_id,
        )
        catch_value = self.redis_client.get(cache_key)
        # 并检测是否上锁 如果该key存在,表示当前文档正在修改中
        if catch_value is not None:
            raise FailException("当前文档正在修改启用状态，请稍后再次尝试")

        # 5.数据库中修改文档的启用状态并设置缓存锁，缓存时间为600s
        self.update(
            model_instance=document,
            enabled=enabled,  # 更新状态
            disabled_at=None if enabled else datetime.now(),  # 禁用
        )
        # 在后续耗时操作之前 先给当前文档数据加锁  所有操作执行完毕 要删除该redis锁
        self.redis_client.setex(cache_key, LOCK_EXPIRE_TIME, 1)

        # 6.启用异步任务完成后续操作(更新向量库,更新关键词表)
        update_document_enabled.delay(document.id)

        # 返回修改后的Document实体数据
        return document

    # 根据传递的知识库id+文档id删除文档信息
    def delete_document(
            self,
            dataset_id: UUID,
            document_id: UUID,
            account: Account,
    ) -> Document:
        """根据传递的知识库id+文档id删除文档信息，涵盖：文档片段删除、关键词表更新、weaviate向量数据库记录删除"""
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个 账号ID account_id
        # 完成授权认证模块后去掉,从Account参数内容获取
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.获取文档并校验权限
        document = self.get(Document, document_id)
        if document is None:
            raise NotFoundException("该文档不存在，请核实后重试")
        if (document.dataset_id != dataset_id
                or
                str(document.account_id) != account_id):
            raise ForbiddenException("当前用户无权限删除该知识库下的文档，请核实后重试")

        # 2.判断文档是否处于可删除状态，只有构建完成/出错的时候才可以删除，其他情况需要等待构建完成
        if document.status not in [DocumentStatus.COMPLETED,DocumentStatus.ERROR]:
            raise FailException("当前文档处于不可删除状态，请稍后重试")

        # 3.删除数据库中的文档基础信息, 项目中没有设计外键,必须靠程序逻辑维护主外键关系
        self.delete(document)

        # 增加逻辑 开启缓存锁

        # 4.调用异步任务执行后续操作,包括:关键词表更新、片段数据删除、weaviate记录删除等
        delete_document.delay(dataset_id, document_id)

        return document