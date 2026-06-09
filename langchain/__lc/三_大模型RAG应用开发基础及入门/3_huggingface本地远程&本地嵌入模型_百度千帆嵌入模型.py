# HuggingFace嵌入模型 需要翻墙
# pip install  langchain-huggingface==0.3.1
# pip install  sentence-transformers==5.1.0


# 模型较大 提前安装加载
import dotenv
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpointEmbeddings
from langchain_community.embeddings.baidu_qianfan_endpoint import QianfanEmbeddingsEndpoint

# 1 huggingface接入本次嵌入模型 会将模型下载到本地目录内
'''
embeddings = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2",
    cache_folder = "./embeddings/",
)
query_vector = embeddings.embed_query("你好 我是小黑子 我喜欢唱跳RAP篮球")
print(query_vector)
print(len(query_vector))
'''

# 2 huggingface 接入远程向量模型 在env配置中增加HUGGINGFACEHUB_API_TOKEN配置
'''
embeddings = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2",
)
query_vector = embeddings.embed_query("你好 我是小黑子 我喜欢唱跳RAP篮球")
print(query_vector)
print(len(query_vector))
'''

# 3 千帆嵌入模型
embeddings = QianfanEmbeddingsEndpoint(model="Qwen3-Embedding-0.6B")
query_vector = embeddings.embed_query("你好 我是小黑子 我喜欢唱跳RAP篮球")
print(query_vector)
print(len(query_vector))