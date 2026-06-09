import os
from dataclasses import dataclass

import tiktoken
from injector import inject
from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_community.storage import RedisStore
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from redis import Redis


# 本地化文本嵌入模型服务
@inject
@dataclass
class EmbeddingsService:
    """文本嵌入模型服务"""
    # 私有属性 依赖注入
    # 嵌入模型
    _embeddings: Embeddings
    # redis缓存,相同的query进行向量生成时,会先从redis内获取数据
    _store: RedisStore
    # 带有缓存功能的嵌入模型
    _cache_backed_embeddings: CacheBackedEmbeddings

    def __init__(self,redis: Redis):
        # openai 嵌入模型
        self._embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )


        # 创建本地向量模型 基于HuggingFace
        # self._embeddings = HuggingFaceEmbeddings(
        #      # 模型类型
        #     model_name = "Alibaba-NLP/gte-multilingual-base",
        #     # 模型本地存储位置
        #     cache_folder = os.path.join("internal", "core", "embeddings"),
        #     # 模型参数 是否信任远程代码
        #     model_kwargs = {
        #         "trust_remote_code": True,
        #     }
        # )

        # 构建redis向量缓存
        self._store = RedisStore(client=redis)
        # 在app.http.module.ExtensionModule中 增加了redis_client的对象注入,
        # 因此执行该构造函数时会自动注入redis_client:Redis

        # 带缓存功能的向量模型
        self._cache_backed_embeddings = CacheBackedEmbeddings.from_bytes_store(
            underlying_embeddings=self._embeddings,
            document_embedding_cache=self._store,
            namespace="embeddings",
        )

    # 只读属性 获取redis缓存
    @property
    def store(self) -> RedisStore:
        return self._store

    # 只读属性 获取向量模型
    @property
    def embeddings(self) -> Embeddings:
        return self._embeddings

    # 只读属性 获取带缓存的向量模型
    @property
    def cache_backed_embeddings(self) -> CacheBackedEmbeddings:
        return self._cache_backed_embeddings

    # 类方法  计算token数量
    @classmethod
    def calculate_token_count(cls, query: str) -> int:
        """计算传入文本的token数 gpt-3.5 """
        # 编码器 获取token数量
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(encoding.encode(query))