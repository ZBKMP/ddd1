# 对接自定义向量数据库

import uuid
from typing import List, Optional, Any, Iterable, Type
import dotenv
import numpy as np
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore, VST
from langchain_openai import OpenAIEmbeddings



class MemoryVectorStore(VectorStore):
    # 简易模拟向量库 使用字典存储向量数据内容
    store: dict = {}  # id为key  整体数据为值

    # 设置嵌入模型属性
    def __init__(self, embedding: Embeddings):
        self._embedding = embedding

    # 重写方法 add_texts
    def add_texts(
            self,
            texts: Iterable[str],
            metadatas: Optional[list[dict]] = None,
            *,
            ids: Optional[list[str]] = None,  # 可选 可以自定义id列表
            **kwargs: Any,
    ) -> list[str]:  # 返回uuID列表
        # 1 检测元数据的数据格式
        if metadatas is not None and len(metadatas) != len(texts):
            raise ValueError("metadatas and texts must have same length")

        # 2 将每个文本数据转换为向量数据
        vectors = self._embedding.embed_documents(texts=texts)

        # 3 给每个向量数据匹配对应的id
        ids = [str(uuid.uuid4()) for _ in texts]

        # 4 将id,text,metadata 包装成最终结果
        for index, text in enumerate(texts):
            data = {
                "id": ids[index],
                "text": text,
                "metadata": metadatas[index] if metadatas is not None else {},
                # 同步读取每条text对应的元数据,如果没有传递元数据则给与{}
                "vector": vectors[index],  # 添加当前text对应的向量值
            }
            # 以每个id为key
            self.store[ids[index]] = data
        return ids

    # 重写 from_texts 执行该方法会返回一个本类向量库对象
    @classmethod
    def from_texts(
            cls: type["MemoryVectorStore"],
            texts: list[str],
            embedding: Embeddings,
            metadatas: Optional[list[dict]] = None,
            *,
            ids: Optional[list[str]] = None,
            **kwargs: Any,
    ) -> "MemoryVectorStore":
        # 创建本类对象
        memory_vector_store = cls(embedding=embedding)
        # 直接调用 add_texts 方法完成数据添加
        memory_vector_store.add_texts(
            texts=texts,
            metadatas=metadatas,
            **kwargs,
        )
        return memory_vector_store


    # 重写  similarity_search 实现相似性检索
    def similarity_search(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> list[Document]: #返回结果必须是Document列表
       # 1  使用向量模型将输入转为向量
       query_vector = self._embedding.embed_query(text=query)


       # 2 循环store中的每一个向量数据 和 query进行欧几里得距离计算
       result = []
       for id,data in self.store.items():
           # 计算 输入问题的向量值与 store中存储的每个向量值进行 欧几里得距离计算
           distance = self._euclidean_distance(query_vector, data["vector"])
           # 保存原data数据并再加上每个data于query之间的距离
           result.append({
               **data,
               "distance": distance,
           })

       # 3 排序
       # 根据每个数据中的distance进行排序  key:通过lambda表达式设置排序策略
       sorted_result = sorted(result, key=lambda x: x["distance"])
       # 仅提取前K条数据
       sorted_result = sorted_result[:k]


       # 4 将每个字典包装为Document对象
       return [Document(
           page_content=data["text"],
           metadata={**data["metadata"],"distance":data["distance"]}, # 在原有元数据的基础上 增加一个新的距离元数据
       ) for data in sorted_result  ]


    @classmethod
    def _euclidean_distance(cls, vec1: list, vec2: list) -> float:
        """计算两个向量的欧几里得距离"""
        return np.linalg.norm(np.array(vec1) - np.array(vec2))



#############################################################################################
# 1 创建模型
dotenv.load_dotenv()
embedding = OpenAIEmbeddings(model="text-embedding-3-small")

# 2 编辑数据
# 数据
poem = [
    "我养了一只猫，叫笨笨",
    "它的瞳孔是两枚新月",
    "总在黄昏时缓缓升起",
    "肉垫踩过散落的诗稿",
    "留下梅花状的空白",
]
# 元数据
meta_datas: list = [
    {"page": 1},
    {"page": 2},
    {"page": 3},
    {"page": 4},
    {"page": 5},
]

# 3 构建数据库
db = MemoryVectorStore(embedding=embedding)
# 4 数据添加
ids = db.add_texts(poem, meta_datas)
print(ids)
# 5 执行检索
print(db.similarity_search("我养了一只猫，叫笨笨"))


# 要求 4 理解上述代码

"""
面试题:
1、你们项目中的向量数据库是怎么做的？
2、你们的向量数据库选择的匹配方式是什么
3、你们项目中使用的是那种向量模型？
4、什么是向量？
5、如果需要切换向量模型我们需要怎么做？
6、什么是向量模型？
"""
