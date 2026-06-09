import logging
from dataclasses import dataclass
from uuid import UUID

from injector import inject
from sqlalchemy import desc

from internal.entity.dataset_entity import DEFAULT_DATASET_DESCRIPTION_FORMATTER
from internal.exception import ValidationException, NotFoundException, FailException
from internal.model import Dataset, Segment, DatasetQuery, AppDatasetJoin, Account
from internal.schema import CreateDatasetReq, UpdateDatasetReq, GetDatasetsWithPageReq, HitReq
from .retrieval_service import RetrievalService
from .base_service import BaseService
from pkg.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy
from internal.lib import datetime_to_timestamp
from internal.task.dataset_task import delete_dataset


@inject
@dataclass
class DatasetService(BaseService):
    """知识库业务服务类 继承于BaseService 包含基本增删改查功能"""
    # 依赖注入
    db: SQLAlchemy
    retrieval_service: RetrievalService

    # 创建知识库业务流程
    def create_dataset(
            self,
            req: CreateDatasetReq,
            account: Account,
    ) -> Dataset:
        """根据传递的请求信息创建知识库"""
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个 账号ID account_id
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.检测该账号下是否存在同名知识库
        dataset = self.db.session.query(Dataset).filter_by(
            account_id=account_id,
            name=req.name.data,
        ).one_or_none()
        if dataset:
            raise ValidationException(f"该知识库{req.name.data}已存在")

        # 2.检测是否传递了描述信息，如果没有传递需要补充上
        if req.description.data is None or req.description.data.strip() == "":
            req.description.data = DEFAULT_DATASET_DESCRIPTION_FORMATTER.format(name=req.name.data)

        # 3.实现数据创建
        return self.create(
            Dataset,
            account_id=account_id,  # 账号ID
            name=req.name.data,  # 知识库名称
            icon=req.icon.data,  # 图标
            description=req.description.data,  # 描述
        )

    # 根据ID查询知识库详情
    def get_dataset(
            self,
            dataset_id: UUID,
            account: Account,
    ) -> Dataset:
        """根据传递的知识库id获取知识库记录"""
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个 账号ID account_id
        # 完成授权认证模块后去掉,从Account参数内容获取
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")

        return dataset

    # 根据ID修改指定知识库信息
    def update_dataset(
            self,
            dataset_id: UUID,
            req: UpdateDatasetReq,
            account: Account,
    ) -> Dataset:
        """根据传递的知识库id+数据更新知识库"""
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个 账号ID account_id
        # 完成授权认证模块后去掉,从Account参数内容获取
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.检测知识库是否存在并校验
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")

        # 2.检测修改后的知识库名称是否出现重名
        check_dataset = self.db.session.query(Dataset).filter(
            Dataset.account_id == account_id,
            Dataset.name == req.name.data,
            Dataset.id != dataset_id,  # 当前知识库除外 是否有同名
        ).one_or_none()
        if check_dataset:
            raise ValidationException(
                f"该知识库名称{req.name.data}已存在，请修改"
            )

        # 3.校验描述信息是否为空，如果为空则人为设置成默认的知识库描述信息
        if (req.description.data is None
                or req.description.data.strip() == ""):
            req.description.data = DEFAULT_DATASET_DESCRIPTION_FORMATTER.format(
                name=req.name.data
            )

        # 4.更新数据
        self.update(
            dataset,
            name=req.name.data,
            icon=req.icon.data,
            description=req.description.data,
        )

        return dataset

    # 分页查询知识库信息
    def get_datasets_with_page(
            self,
            req: GetDatasetsWithPageReq,
            account: Account  # 完成授权认证模块后 增加account参数
    ) -> tuple[list[Dataset], Paginator]:
        """根据传递的信息获取知识库列表分页数据"""
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个 账号ID account_id
        # 完成授权认证模块后去掉,从Account参数内容获取
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.构建分页查询器
        paginator = Paginator(db=self.db, req=req)

        # 2.构建筛选器  按照search_word对name进行模糊查询
        #  账号ID为查询的第一个必要条件
        filters = [Dataset.account_id == account_id]
        if req.search_word.data:
            filters.append(
                Dataset.name.like(f"%{req.search_word.data}%")
            )

        # 3.执行分页并获取数据
        datasets = paginator.paginate(
            self.db.session.query(Dataset)
            .filter(*filters)
            .order_by(desc("created_at"))
        )

        return datasets, paginator

    # 根据传递的知识库id+请求执行召回测试
    def hit(
            self,
            dataset_id: UUID,
            req: HitReq,
            account: Account,
    ) -> list[dict]:
        # todo:等待授权认证模块完成进行切换调整 虚拟账号ID
        # 完成授权认证模块后去掉,从Account参数内容获取
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.检测知识库是否存在并校验
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")

        # 2.调用检索服务执行检索 得到LangChain中的Document文档列表
        lc_documents = self.retrieval_service.search_in_datasets(
            dataset_ids=[dataset_id],
            account_id=account_id,
            **req.data,  # 从请求中解构其他参数
        )
        # 将文档列表结果转换为文档字典,key为元数据中的片段ID,值为文档
        lc_document_dict = {
            str(lc_document.metadata["segment_id"]): lc_document
            for lc_document in lc_documents
        }

        # 3.根据检索到的数据查询对应的数据库内Segment片段信息
        segments = self.db.session.query(Segment).filter(
            Segment.id.in_(
                [str(lc_document.metadata["segment_id"])
                 for lc_document in lc_documents]
            )
        ).all()
        # 将查询结果列表转换为字典
        segment_dict = {
            str(segment.id): segment for segment in segments
        }

        # 4.排序片段数据:根据lc_documents顺序重新排列segment顺序
        sorted_segments = [
            segment_dict[str(lc_document.metadata["segment_id"])]
            for lc_document in lc_documents
            if str(lc_document.metadata["segment_id"]) in segment_dict
        ]

        # 5.组装响应数据
        hit_result = []  # 封装检索结果的列表
        # 遍历排序之后的sorted_segments 每个元素添加到响应结果hit_result中
        for segment in sorted_segments:
            # 只读属性 获取关联的document实体
            document = segment.document
            # 只读属性 返回文档对应的腾讯云COS上传文件
            upload_file = document.upload_file
            # 组装数据 加入结果列表
            hit_result.append({
                "id": segment.id,
                "document": {  # document相关数据
                    "id": document.id,
                    "name": document.name,
                    "extension": upload_file.extension,
                    "mime_type": upload_file.mime_type,
                },
                "dataset_id": segment.dataset_id,
                # 相似性得分
                "score": lc_document_dict[str(segment.id)].metadata["score"],
                "position": segment.position,
                "content": segment.content,
                "keywords": segment.keywords,
                "character_count": segment.character_count,
                "token_count": segment.token_count,
                "hit_count": segment.hit_count,
                "enabled": segment.enabled,
                "status": segment.status,
                "error": segment.error,
                # 时间戳数据
                "disabled_at": datetime_to_timestamp(segment.disabled_at),
                "updated_at": datetime_to_timestamp(segment.updated_at),
                "created_at": datetime_to_timestamp(segment.created_at),
            })

        return hit_result

    # 根据传递的知识库id获取最近的10条查询记录
    def get_dataset_queries(
            self,
            dataset_id: UUID,
            account: Account,
    ) -> list[DatasetQuery]:
        """根据传递的知识库id获取最近的10条查询记录"""
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个 账号ID account_id
        # 完成授权认证模块后去掉,从Account参数内容获取
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.获取知识库并校验权限
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")

        # 2.调用知识库查询模型查找最近的10条记录
        dataset_queries = self.db.session.query(
            DatasetQuery
        ).filter(
            DatasetQuery.dataset_id == dataset_id,
        ).order_by(
            desc("created_at")
        ).limit(10).all()

        # 返回查询结果
        return dataset_queries

    # 根据传递的知识库id删除知识库信息
    def delete_dataset(
            self,
            dataset_id: UUID,
            account: Account,
    ) -> None:
        """根据传递的知识库id删除知识库信息，涵盖知识库底下的所有
                            文档、片段、关键词，以及向量数据库里存储的数据"""
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个 账号ID account_id
        # 完成授权认证模块后去掉,从Account参数内容获取
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.获取知识库并校验权限
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")

        try:
            # 2.删除知识库基础记录以及知识库和应用关联的记录
            self.delete(dataset)

            with self.db.auto_commit():  # 手动调用 自动提交上下文
                self.db.session.query(AppDatasetJoin).filter(
                    AppDatasetJoin.dataset_id == dataset_id,
                ).delete()

            # 3.调用异步任务执行后续的耗时操作
            delete_dataset.delay(dataset_id)

        except Exception as e:
            logging.exception(
                f"删除知识库失败, dataset_id: {dataset_id}, 错误信息: {str(e)}"
            )
            raise FailException("删除知识库失败，请稍后重试")
