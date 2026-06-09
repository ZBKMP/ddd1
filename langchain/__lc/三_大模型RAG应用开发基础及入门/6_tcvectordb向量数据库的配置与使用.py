# TCVectorDB向量数据库(腾讯云)的配置与使用
import os

import dotenv
from langchain_community.vectorstores import TencentVectorDB
from langchain_community.vectorstores.tencentvectordb import (
    ConnectionParams,
    MetaField,
    META_FIELD_TYPE_STRING,
    META_FIELD_TYPE_UINT64
)
from langchain_openai import OpenAIEmbeddings

dotenv.load_dotenv()
#  1 使用腾讯云内嵌的嵌入模型  不支持元数据
db = TencentVectorDB(
    embedding=None,
    connection_params=ConnectionParams(
        url=os.getenv("TC_VECTOR_DB_URL"),
        username=os.getenv("TC_VECTOR_DB_USERNAME"),
        key=os.getenv("TC_VECTOR_DB_KEY"),
        timeout=int(os.getenv("TC_VECTOR_DB_TIMEOUT")),
    ),
    database_name=os.getenv("TC_VECTOR_DB_DATABASE"),
    collection_name="dataset_1",  #集合名称
)

# 要添加的文本数据
poem = [
    "我养了一只猫，叫笨笨",
    "它的瞳孔是两枚新月",
    "总在黄昏时缓缓升起",
    "肉垫踩过散落的诗稿",
    "留下梅花状的空白",
]

# 添加数据的操作仅做一次
# ids = db.add_texts(
#     texts=poem,
# )
# 添加后会返回每个数据的ID 组成列表
# print(ids)

# result = db.similarity_search_with_score("笨笨")
# print(result)

print("*"*50)

# 2  使用自主选择的向量模型 以及添加元数据filter 需要重新建立 collection
db = TencentVectorDB(
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"), # 1536
    connection_params=ConnectionParams(
        url=os.getenv("TC_VECTOR_DB_URL"),
        username=os.getenv("TC_VECTOR_DB_USERNAME"),
        key=os.getenv("TC_VECTOR_DB_KEY"),
        timeout=int(os.getenv("TC_VECTOR_DB_TIMEOUT")),
    ),
    database_name=os.getenv("TC_VECTOR_DB_DATABASE"),
    collection_name="dataset_2",  #集合名称
    meta_fields=[
        MetaField(name="page",data_type=META_FIELD_TYPE_UINT64,description="每条文档的页码"),
    ]# 声明该数据集中包含的元数据
)
# 元数据
meta_datas: list = [
    {"page": 1},
    {"page": 2},
    {"page": 3},
    {"page": 4},
    {"page": 5},
]

# 添加文本内容以及元数据
# ids = db.add_texts(
#     texts=poem,
#     metadatas=meta_datas,
# )
# print(ids)

# 使用filter结合元数据编辑过滤条件
# https://cloud.tencent.com/document/product/1709/112947
# https://cloud.tencent.com/document/product/1709/95122
result = db.similarity_search_with_score(
    query="笨笨",
    expr =" page <= 3 "
)
print(result)

# 要求 2: 自行编辑文档数据于元数据 使用TCVectorDB向量库存储
# 检索数据:  db.similarity_search db.similarity_search_with_score db.similarity_search_with_relevance_scores
# 使用filter结合元数据作为过滤条件  大于 小于 大于等于 小于等于  不等于  in  not in   and/or

