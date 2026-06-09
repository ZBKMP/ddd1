from injector import inject
import weaviate
from langchain_openai import OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate import WeaviateClient
from weaviate.auth import AuthApiKey
from weaviate.collections import Collection
from.embeddings_service import EmbeddingsService


# 知识库检索服务
@inject
class WeaviateVectorStoreService:
    """向量库检索服务"""
    client : WeaviateClient
    vector_store : WeaviateVectorStore
    # 依赖注入
    embeddings_service : EmbeddingsService

    # ****代码修改****
    def __init__(self, embeddings_service: EmbeddingsService):
        # 定义了EmbeddingsService之后 从EmbeddingsService获取向量模型 injector会自动注入该类对象
        self.embeddings_service = embeddings_service

        # 建议使用 docker的本地化部署
        self.client = weaviate.connect_to_local(
            host="192.168.172.129",
            port=8080,
        )
        self.vector_store = WeaviateVectorStore(
            client=self.client,
            index_name="Llmops_dataset", #向量库数据集名称:Llmops_dataset
            text_key="text",
            # embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
            # 使用 embeddings_service 获取嵌入模型
            embedding = self.embeddings_service.cache_backed_embeddings
        )

    # 只读属性 获取向量库中项目对应的数据集
    @property
    def collection(self) -> Collection:
        return self.client.collections.get("Llmops_dataset")