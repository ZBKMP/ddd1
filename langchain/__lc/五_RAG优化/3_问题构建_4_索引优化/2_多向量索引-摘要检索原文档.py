# MultiVector实现多向量检索文档 摘要检索原文档

import uuid

import dotenv
from langchain.retrievers import MultiVectorRetriever
from langchain.storage import LocalFileStore
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

dotenv.load_dotenv()

# 1.创建加载器、文本分割器并处理文档
loader = UnstructuredFileLoader("电商产品数据.txt")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
docs = loader.load_and_split(text_splitter)

# 2 定义摘要生成链 Document生成摘要
summary_chain = (
        {"doc": lambda x: x.page_content}
        | ChatPromptTemplate.from_template("请总结一下文档的内容:\n\n{doc}")
        | ChatOpenAI(model="gpt-4o-mini", temperature=0)
        | StrOutputParser()
        | (lambda x: print("摘要:", x) or x)
)

# 3 批量生成摘要与唯一标识
summaries = summary_chain.batch(
    inputs=docs,  # 以文档列表作为batch的参数,每次执行链时就会传入一个Document
    config=RunnableConfig(
        configurable={"max_concurrency": 5}  # 设置最大并发数量
    )
)
# 同步生成唯一标识
doc_ids = [str(uuid.uuid4()) for _ in summaries]

# 4 根据摘要生成新的文档  同时将唯一标识作为元数据
summaries_docs = [
    Document(page_content=summary, metadata={"doc_id": doc_ids[index]})
    for index, summary in enumerate(summaries)
]

# 5.构建文档数据库(存切割后的原文档片段)与向量数据库(原文档片段生成的摘要)
byte_store = LocalFileStore("multy_vector") # 文档数据库
db = FAISS.from_documents(
    documents=summaries_docs,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
) # 创建向量库 并存储摘要文档

# 6 构建多向量检索器 实现在向量库中使用相似性检索摘要文档,但返回文档数据库中的原文档.
retriever = MultiVectorRetriever(
    vectorstore=db, # 向量库
    byte_store=byte_store, # 原文档存储库
    id_key="doc_id", # 摘要与原文档共用的唯一标识
)

# 7.将原文档存储到LocalFileStore中
# 此时向量数据库中已经有数据了,但文档数据库中还没有数据。
# 将标识ID与对应的原Doc文档合并成元祖列表,使用retriever.docstore.mset存储于文档数据库中
retriever.docstore.mset(list(zip(doc_ids, docs)))  # [(doc_id,doc),(doc_id,doc),(doc_id,doc)]

# 如果使用其他向量库 不能重复执行上述存储数据的过程
###########################################################################################################

# 8.执行检索  检索的是摘要 返回的是原文档
results= retriever.invoke("请推荐一些潮州的特产")
for doc in results:
    print(doc)