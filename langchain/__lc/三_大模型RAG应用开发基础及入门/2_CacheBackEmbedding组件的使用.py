# CacheBackEmbedding组件的使用  缓存嵌入结果
# 将生成过的向量值存入本地缓存
import dotenv
import numpy as np
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_openai import OpenAIEmbeddings
from numpy.linalg import norm


# 向量数据生成 以及向量相似度计算

# 1.1 生成向量模型(嵌入模型)
dotenv.load_dotenv()
embeddings = OpenAIEmbeddings(model='text-embedding-3-small')

# 1.2 引入缓存 将生成过的向量数据保存在缓存中 下次再要生成相同内容 则直接从缓存中获取
embeddings_with_cache = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings=embeddings,
    document_embedding_cache=LocalFileStore("./cache/"),
    namespace=embeddings.model,# 使用模型名称作为命名空间,以区分不同的缓存空间
    query_embedding_cache=True,# 开启向量数据的缓存存储
)


# 2 将文本内容转为向量数据
# 2.1 将单个文本内容生成一个向量数据 -->list[float]
query_vector = embeddings_with_cache.embed_query("你好 我是小黑子 我喜欢唱跳RAP篮球 你是谁?")
print(query_vector)
print(len(query_vector))

print("*"*50)

# 2.2 将一组文本列表生成一组向量值 -->list[list[float]]
document_vectors = embeddings_with_cache.embed_documents([
    "小黑子 喜欢唱跳RAP篮球",
    "喜欢唱跳RAP篮球的有小黑子",
    "hello world 2026",
])
for document_vector in document_vectors:
    print(document_vector,len(document_vector))


print("*"*50)

# 通过余弦角度计算向量之间相似度的算法 得到一个相似度数据,数据越接近1,表示两个向量数据数据越相似
def cosine_similarity(vector1:list[float], vector2:list[float]) -> float:
    """计算传入两个向量的余弦相似度"""
    # 1.计算两个向量的点积
    dot_product = np.dot(vector1, vector2)
    # 2.计算向量的长度
    vec1_norm = norm(vector1)
    vec2_norm = norm(vector2)
    # 3.计算余弦相似度
    return dot_product / (vec1_norm * vec2_norm)

# 使用余弦相似度算法 计算提问与文档之间的相似度
for document_vector in document_vectors:
    result = cosine_similarity(query_vector, document_vector)
    print(result)