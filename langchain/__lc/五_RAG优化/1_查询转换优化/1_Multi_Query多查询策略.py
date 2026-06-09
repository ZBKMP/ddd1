# 优化策略: 多查询重写策略提升检索准确性 MultiQueryRetriever
# 根据主问题 生成相关子问题 子问题通常更细节 帮助大语言模型深入理解主问题 检索更准确 以提供正确答案

import dotenv
import weaviate
from langchain.retrievers import MultiQueryRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()

# 1 构建向量库--基础检索器
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
retriever = db.as_retriever(search_type="mmr")

# 2.创建多查询检索器 MultiQueryRetriever 根据用户的提问从不同的侧面生成3个问题
#   MultiQueryRetriever内部包含了一个用于生成3个问题的英文的提示模板
m_retriever = MultiQueryRetriever.from_llm(
    # 中文环境下 建议重构中文版本的提示词
    prompt=ChatPromptTemplate.from_template(
        "你是一个AI语言模型助手。你的任务是根据给定的用户问题生成3个不同的版本，"
        "以便从向量数据库中检索相关文档。通过从多个角度生成用户问题，"
        "你的目标是帮助用户克服基于距离的相似性搜索的一些局限性。"
        "请用换行符分隔这些替代问题。原始问题：{question}"),
    retriever=retriever,  # 基本检索器
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.1),  # 生成问题的大模型
    include_original=True,  # 是否包含原始问题
)

# 3 执行检索
results = m_retriever.invoke(input="关于配置接口的信息有哪些")
for doc in results:
    print(doc.page_content[: 100],doc.metadata)


client.close()
# 可以在langsmith平台中查看到 由一个问题生成出的3个不同版本的问题
# 每个问题都会在向量库中进行检索,多条检索结果会进行合并去重,最终提取K条记录