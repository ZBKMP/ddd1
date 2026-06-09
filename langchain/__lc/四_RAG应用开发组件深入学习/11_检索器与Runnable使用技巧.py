# 检索器组件深入学习与使用技巧
# 检索器:返回与query相关文档列表的Runnable组件-->向量数据库.as_retriever方法
# 并在invoke时动态更改db.as_retriever所需的参数：search_type/search_kwargs

import dotenv
import weaviate
from langchain_core.runnables import ConfigurableField, RunnableConfig
from langchain_openai import OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()
# 1 构建向量库
client = weaviate.connect_to_local(
    host="192.168.172.129",
    port=8080,
)
db = WeaviateVectorStore(
    client=client,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    index_name='collection_project',  # 数据集名称
    text_key='text',  # 文本内容的key名
)

# 2 构建检索器,配置运行时参数
retriever = db.as_retriever(
    search_kwargs = {"k":4}
).configurable_fields(
    search_type = ConfigurableField(id="retriever_search_type"),
    search_kwargs = ConfigurableField(id="retriever_search_kwargs"),
)

# 3 测试执行 invoke传入参数 更改配置
results = retriever.invoke(
    input="关于配置接口的信息有哪些",
    config =  RunnableConfig(
        configurable={
            "retriever_search_type": "mmr",
            "retriever_search_kwargs": {
                "k": 4,
                "fetch_k":20,
            }
        }
    )
)
for doc in results:
    print(doc.page_content[:100],doc.metadata)



# 要求 2 : 基于要求 1 将检索器需要的参数 使用configurable_fields动态配置

# 要求 3 : 在一个向量库下定义多个不同策略的检索器 使用configurable_alternative实现在 组件/链 中动态切换检索器