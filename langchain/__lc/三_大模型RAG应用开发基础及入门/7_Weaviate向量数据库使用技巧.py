# Weaviate向量数据库 使用
# pip install  weaviate-client==4.16.10
# pip install  langchain-weaviate==0.0.5


import os
import dotenv
import weaviate
from langchain_openai import OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey
from weaviate.classes.query import Filter

# 1 创建大模型
dotenv.load_dotenv()
embedding = OpenAIEmbeddings(model="text-embedding-3-small")

# 2.1 Weaviate远程云端连接
# REST endpoint 表示某个Cluster的服务地址
cluster_url = 'jwfhblxsry0agg3aybxg.c0.asia-southeast1.gcp.weaviate.cloud'
# API_KEY  针对某个Cluster的服务APIkey
api_key = os.getenv("WEAVIATE_API_KEY", "")
# 创建 weaviate客户端
# client = weaviate.connect_to_weaviate_cloud(
#     cluster_url=cluster_url,
#     auth_credentials=AuthApiKey(api_key=api_key),
#     skip_init_checks=True,  # 跳过初始化检查
# )

# 2.2 Weaviate在Linux的docker下部署
client = weaviate.connect_to_local(
    host="192.168.172.129",
    port=8080,
)


# 3 通过客户端连接到向量库
db = WeaviateVectorStore(
    client=client,
    embedding=embedding,
    index_name='collection_1',  # 数据集名称
    text_key='text',  # 文本内容的key名
)

# 4 新增数据
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
# 新增返回ID列表
# ids = db.add_texts(
#     texts=poem,
#     metadatas=meta_datas,
# )
# print(ids)



# 5 相似检索
# 元数据过滤
# filters = Filter.by_property("page").less_or_equal(3)

# filter_1 = Filter.by_property("page").less_or_equal(2)
# filter_2 = Filter.by_property("page").greater_or_equal(4)
# filters = Filter.any_of([filter_1, filter_2]) # or / and

#
# result = db.similarity_search_with_score(
#     query="笨笨",
#     k=3,
#     filters = filters
# )
# print(result)




# 6 删除一条向量数据
# ids = ["d8b3b76e-cc05-44ca-87e3-c7ef148c7c03"]
# db.delete(
#     ids=ids,
# )


# 7 从向量库对象中获取检索器 是一个可运行组件
retriever = db.as_retriever()
result = retriever.invoke(input="笨笨") # input == query
print(result)

# 关闭链接
client.close()

# 要求 3 : 自行编辑文档数据于元数据 使用weaviate向量库存储
# 检索数据:  db.similarity_search db.similarity_search_with_score db.similarity_search_with_relevance_scores
# 使用filter结合元数据作为过滤条件  大于 小于 大于等于 小于等于  不等于  in  not in   and/or
