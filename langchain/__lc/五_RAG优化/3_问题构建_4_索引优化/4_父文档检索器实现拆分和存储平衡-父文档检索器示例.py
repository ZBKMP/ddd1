# 父文档检索器实现拆分和存储平衡 逻辑上和之前的案例2、3类似,使用ParentDocumentRetriever
# 父文档检索器示例
import os
import dotenv
import weaviate
from langchain.retrievers import ParentDocumentRetriever #继承于多向量检索器
from langchain.storage import LocalFileStore
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()
# 1.创建加载器与文档列表，并加载文档,加载多个数据文档
#    建议使用Loader列表实现加载多个文档
loaders = [
    UnstructuredFileLoader("电商产品数据.txt"),
    UnstructuredFileLoader("项目API文档.md"),
]
docs = []
for loader in loaders:
    docs.extend(loader.load())

# 2.创建文本分割器 递归字符文本分割器 用于将父文档分割为小块
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=200,
)

# 3.创建weaviate向量库据库与文档数据库
# 需要将doc_id(uuid)存储于向量库,Weaviate会将其认为是UUID类型,需要自己创建数据集,强制将其看成str
# REST endpoint 表示某个Cluster的服务地址
cluster_url = 'jwfhblxsry0agg3aybxg.c0.asia-southeast1.gcp.weaviate.cloud'
# API_KEY  针对某个Cluster的服务APIkey
api_key = os.getenv("WEAVIATE_API_KEY", "")
# 创建 weaviate客户端
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=cluster_url,
    auth_credentials=AuthApiKey(api_key=api_key),
    skip_init_checks=True,  # 跳过初始化检查
)
db = WeaviateVectorStore(
    client=client,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    index_name='Collection_doc',  # 数据集名称 此案例中需要先创建该数据集
    text_key='text',  # 文本内容的key名
)
# 本地文档数据库 存储原父文档
byte_store = LocalFileStore("parent_document")

# 4 构建ParentDocumentRetriever : 在存储片段内容时 会生成doc_id 关联原文档
retriever = ParentDocumentRetriever(
    vectorstore=db,
    byte_store=byte_store,
    child_splitter=text_splitter,
)

# 5 通过父文档检索器添加文档  只执行一次  id会自动生成可以不填
# retriever.add_documents(docs)

# 6.检索并返回内容
result = retriever.invoke("介绍一下LLMOPS项目中如何进行应用配置")
for result in result:
    print(result.page_content)
    print(result.metadata)
    print("----------------------")

print("*"*50)

result = retriever.invoke("介绍一下潮汕有哪些特产")
for result in result:
    print(result.page_content)
    print(result.metadata)
    print("----------------------")

client.close()