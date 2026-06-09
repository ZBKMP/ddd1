# OpenAI Embedding接口使用实践测试 接入嵌入模型

import dotenv
import numpy as np
from langchain_openai import OpenAIEmbeddings
from numpy.linalg import norm

# 向量数据生成 以及向量相似度计算

# 1 使用嵌入模型
dotenv.load_dotenv()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # 维度 1536


# 2 将文本内容转为向量数据
# 2.1 将单个文本内容生成一个向量数据 -->list[float]
query_vector = embeddings.embed_query("你好 我是小黑子 我喜欢唱跳RAP篮球 你是谁?")
print(query_vector)
print(len(query_vector))

print("*"*50)

# 2.2 将一组文本列表生成一组向量值 -->list[list[float]]
document_vectors = embeddings.embed_documents([
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