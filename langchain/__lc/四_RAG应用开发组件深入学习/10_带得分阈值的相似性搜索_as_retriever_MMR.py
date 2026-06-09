# VectorStore组件深入学习与检索方法
# 带得分阈值的相似性搜索 / as_retriever / MMR

# A 带得分阈值的相似性搜索
import dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

dotenv.load_dotenv()
# 1 文本嵌入模型
embedding = OpenAIEmbeddings(model="text-embedding-3-small")
# 2 document列表
documents = [
    Document(page_content="笨笨是一只很喜欢睡觉的猫咪", metadata={"page": 1}),
    Document(page_content="我喜欢在夜晚听音乐，这让我感到放松。", metadata={"page": 2}),
    Document(page_content="猫咪在窗台上打盹，看起来非常可爱。", metadata={"page": 3}),
    Document(page_content="学习新技能是每个人都应该追求的目标。", metadata={"page": 4}),
    Document(page_content="我最喜欢的食物是意大利面，尤其是番茄酱的那种。", metadata={"page": 5}),
    Document(page_content="昨晚我做了一个奇怪的梦，梦见自己在太空飞行。", metadata={"page": 6}),
    Document(page_content="我的手机突然关机了，让我有些焦虑。", metadata={"page": 7}),
    Document(page_content="阅读是我每天都会做的事情，我觉得很充实。", metadata={"page": 8}),
    Document(page_content="他们一起计划了一次周末的野餐，希望天气能好。", metadata={"page": 9}),
    Document(page_content="我的狗喜欢追逐球，看起来非常开心。", metadata={"page": 10}),
]
# 3 存入FAISS数据库
db = FAISS.from_documents(documents, embedding)
# 4 不带阈值的搜索 结果包含相似度很低的数据 比如有负数的
result = db.similarity_search_with_relevance_scores("我养了一只猫，叫笨笨")
print(result)
print("-" * 10)
# 5 在进行 with_relevance_scores 相似性检索时 设置得分阈值
result = db.similarity_search_with_relevance_scores(
    query="我养了一只猫，叫笨笨",
    score_threshold=0.4 , # 低于该分数的文档不检索
)
print(result)

print("-" * 10)

# b 检索器的使用

import dotenv
import weaviate
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

# 1 构建加载器与分割器
loader = UnstructuredMarkdownLoader("项目API文档.md")
text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", "。|！|？", "\.\s|\!\s|\?\s", "；|;\s", "，|,\s", " ", "", ],
    is_separator_regex=True,
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
)
# 2 加载文档并分割 得到document列表
documents = loader.load()
chunks = text_splitter.split_documents(documents)

# 3 添加数据至向量库
client = weaviate.connect_to_local(
    host="192.168.172.129",
    port=8080,
)
db = WeaviateVectorStore(
    client=client,
    embedding=embedding,
    index_name='collection_project',  # 数据集名称
    text_key='text',  # 文本内容的key名
)
# ids = db.add_documents(chunks)
# print(ids)

# 召回测试

# 5 使用检索器实现 带阈值的相似性检索
from weaviate.classes.query import Filter
filters = Filter.by_property("start_index").greater_or_equal(4000)
retriever = db.as_retriever(
    search_type="similarity_score_threshold", # similarity  mmr  similarity_score_threshold
    # k 得分阈值 元数据过滤filters ......
    search_kwargs={
        "k": 4,
        "score_threshold": 0.6,
        "filters":filters,
    }
)
# 可运行组件 invoke方法
docs = retriever.invoke(input="关于配置接口的信息有哪些")
for doc in docs:
    print(doc.page_content[:100],doc.metadata)


print("*" * 50)

#  C MMR检索策略
# db.max_marginal_relevance_search()
retriever = db.as_retriever(
    search_type='mmr',
    search_kwargs={
        "k":4,
        "fetch_k":20,
    }
)
results = retriever.invoke(input="关于配置接口的信息有哪些")
for result in results:
    print(result.page_content[:100])
    print("----------")


# 要求 1 :  测试基于不同的向量库 生成检索器 各个测试三种检索策略 以及 各自使用filter的策略