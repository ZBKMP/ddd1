from dataclasses import dataclass
from uuid import UUID
from injector import inject
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document as LCDocument
from sqlalchemy import update

from internal.entity.dataset_entity import RetrievalStrategy, RetrievalSource
from internal.exception import NotFoundException
from internal.model import Dataset, DatasetQuery, Segment
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from .jieba_service import JiebaService
from .vector_store_service import WeaviateVectorStoreService


@inject
@dataclass
class RetrievalService(BaseService):
    """检索服务"""
    # 依赖注入
    db: SQLAlchemy
    jieba_service: JiebaService
    vector_database_service: WeaviateVectorStoreService

    #  根据传递的query+知识库列表执行检索，并返回检索的LangChain_Document列表
    #  元数据内包含得分信息,如果检索策略为全文检索，则得分为0
    def search_in_datasets(
            self,
            dataset_ids: list[UUID],
            account_id: str,
            query: str,
            # 检索策略为full_text/semantic/hybrid 默认semantic
            retrieval_strategy: str = RetrievalStrategy.SEMANTIC,
            k: int = 4,
            score: float = 0,
            retrival_source: str = RetrievalSource.HIT_TESTING,  # 检索需求来源
    ) -> list[LCDocument]:
        """根据传递的query+知识库列表执行检索，并返回检索的文档+得分数据
                                       （如果检索策略为全文检索，则得分为0）"""
        # todo:等待授权认证模块完成进行切换调整 虚拟账号ID
        # 完成授权认证模块后去掉,从Account参数内容获取
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        # 1.提取知识库列表并校验权限
        datasets = self.db.session.query(Dataset).filter(
            Dataset.id.in_(dataset_ids),
            Dataset.account_id == account_id,
        ).all()
        if datasets is None or len(datasets) == 0:
            raise NotFoundException("当前无知识库可执行检索")

        # 更新dataset_ids 从查询结果中提取出所有的知识库ID 组成列表
        # 不能直接使用dataset_ids参数,可能其中包含不存在的知识库ID,
        # 或当前账号没有权限
        dataset_ids = [dataset.id for dataset in datasets]

        # 2.构建不同种类的检索器 局部导入 避免出现循环依赖
        from internal.core.retrievers import (
            SemanticRetriever, FullTextRetriever
        )
        # 自定义相似性检索器
        semantic_retriever = SemanticRetriever(
            dataset_ids=dataset_ids,
            vector_store=self.vector_database_service.vector_store,
            search_kwargs={
                "k": k,
                "score_threshold": score,  # 得分阈值
            }
        )
        # 自定义全文检索器
        ful_text_retriever = FullTextRetriever(
            db=self.db,
            dataset_ids=dataset_ids,
            jieba_service=self.jieba_service,
            search_kwargs={
                "k": k
            },
        )
        # 混合检索器
        hybrid_retriever = EnsembleRetriever(
            retrievers=[semantic_retriever, ful_text_retriever],  # 混合的检索器列表
            weights=[0.5, 0.5]
        )

        # 3.根据不同的检索策略执行检索
        if retrieval_strategy == RetrievalStrategy.SEMANTIC:
            lc_documents = semantic_retriever.invoke(input=query)
        elif retrieval_strategy == RetrievalStrategy.FULL_TEXT:
            lc_documents = ful_text_retriever.invoke(input=query)
        else:
            lc_documents = hybrid_retriever.invoke(input=query)

        ######################################################################################
        # 4.添加知识库查询记录
        # （只存储唯一记录，也就是一个知识库如果检索出了多篇文档，也只存储一条）
        unique_dataset_ids = list(set(
            str(lc_document.metadata["dataset_id"]) for lc_document in lc_documents)
        )
        for dataset_id in unique_dataset_ids:
            self.create(
                DatasetQuery,
                dataset_id=dataset_id,
                query=query,
                source=retrival_source,
                source_app_id=None,
                created_by=account_id,
            )

        # 5.批量更新片段的命中次数，召回次数
        with self.db.auto_commit():
            # 构建一个多行的修改操作
            statement = (
                update(Segment)
                # 条件
                .where(
                    Segment.id.in_(
                        [lc_document.metadata["segment_id"] for lc_document in lc_documents]
                    ),
                )
                # 修改的内容
                .values(hit_count=Segment.hit_count + 1)
            )
            #update  segment set hit_count = hit_count + 1 where id in []
            self.db.session.execute(statement)
        ######################################################################################

        # 返回langchain文档列表
        return lc_documents
