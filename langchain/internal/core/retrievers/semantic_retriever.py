from uuid import UUID

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document as LCDocument

from langchain_core.retrievers import BaseRetriever
from langchain_weaviate import WeaviateVectorStore
from pydantic import Field
from weaviate.collections.classes.filters import Filter


# 自定义相似性检索器/向量检索器
class SemanticRetriever(BaseRetriever):
    """相似性检索器/向量检索器"""
    # 属性(BaseRetriever也继承于BaseModel)
    # dataset ID列表 检索仅能在限定的知识库列表中检索
    dataset_ids: list[UUID]
    # WeaviateVectorStore向量库
    vector_store: WeaviateVectorStore
    # 检索器其他搜索参数 k/score_threshold/filters,可以不传,使用默认值
    search_kwargs: dict = Field(default_factory=dict)

    #  重写方法  _get_relevant_documents
    def _get_relevant_documents(
            self,
            query: str,
            *,
            run_manager: CallbackManagerForRetrieverRun
    ) -> list[LCDocument]:
        """根据传递的query执行相似性检索"""
        # 1.提取最大搜索条件k，默认值为4
        k = self.search_kwargs.pop("k")

        # 2.执行相似性检索并获取得分信息 返回结果:list[tuple[Document, float]]
        search_result= self.vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=k,
            **{
                # 元数据过滤 所有条件必须都满足
                "filters":Filter.all_of([
                    # 在指定的dataset_id列表之内
                    Filter.by_property("dataset_id").contains_any(
                        [str(dataset_id) for  dataset_id in self.dataset_ids]
                    ),
                    # document状态必须为可用
                    Filter.by_property("document_enabled").equal(True),
                    # 片段状态必须为可用
                    Filter.by_property("segment_enabled").equal(True),
                ])
            },
            # 如果传递了自定义的search_kwargs包含搜索条件则会覆盖默认的filter搜索条件,
            # 没有则使用默认的
            **self.search_kwargs
        )

        # 如果没有结果 返回空列表
        if search_result is None or len(search_result) == 0:
            return []

        # # 有结果(list[tuple[Document, float]]),则拆解为文档元祖和分数元祖
        # lc_documents,scores = zip(*search_result)
        # # 3.执行循环将得分添加到文档的元数据中
        # for lc_document ,score in zip(lc_documents,scores):
        #     lc_document.metadata["score"] = score

        lc_documents = []
        for lc_document,score in search_result:
            lc_document.metadata['score'] = score
            lc_documents.append(lc_document)


        # 4.返回文档列表
        return lc_documents

