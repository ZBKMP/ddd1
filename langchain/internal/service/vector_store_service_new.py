from dataclasses import dataclass

from flask_weaviate import FlaskWeaviate
from injector import inject
import weaviate
from langchain_openai import OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate import WeaviateClient
from weaviate.auth import AuthApiKey
from weaviate.collections import Collection
from.embeddings_service import EmbeddingsService

# 向量数据库的集合名字
COLLECTION_NAME = "Llmops_dataset"

# 知识库检索服务
@inject
@dataclass
class WeaviateVectorStoreService:
    """向量库检索服务"""
    weaviate_flask: FlaskWeaviate
    embeddings_service: EmbeddingsService

    # 通过FlaskWeaviate对象获取weaviate中的VectorStore
    @property
    def vector_store(self) -> WeaviateVectorStore:
        return WeaviateVectorStore(
            client= self.weaviate_flask.client,
            index_name= COLLECTION_NAME,
            text_key="text",
            embedding=self.embeddings_service.cache_backed_embeddings,
        )


    # 只读属性 获取向量库中项目对应的数据集
    @property
    def collection(self) -> Collection:
        return self.weaviate_flask.client.collections.get("Llmops_dataset")