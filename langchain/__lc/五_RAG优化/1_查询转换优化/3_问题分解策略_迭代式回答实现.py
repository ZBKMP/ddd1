# 问题分解策略提升复杂问题检索正确率 迭代式回答实现
from operator import itemgetter

import dotenv
import weaviate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()
# 1 构建一个链 将一个原始问题分解为三个步骤的问题
# 1.1 定义分解子问题的prompt
decomposition_prompt = ChatPromptTemplate.from_template(
    "你是一个乐于助人的AI助理，可以针对一个输入问题生成多个相关的子问题。\n"
    "目标是将输入问题分解成一组可以独立回答的子问题或者子任务。\n"
    "生成与以下问题相关的多个搜索查询：{question}\n"
    "并使用换行符进行分割，输出(3个子问题/子查询):"
)
# 1.2 构建问题生成链
decomposition_chain =( {
    "question":RunnablePassthrough()
} | decomposition_prompt
  | ChatOpenAI(model="gpt-4o-mini",temperature=0.0)
  | StrOutputParser()
  | (lambda x : x.strip().split("\n"))
)

# 1.3 测试问题生成链
# query = "关于配置接口的信息有哪些"
# step_questions =decomposition_chain.invoke(input="关于配置接口的信息有哪些")
# print(step_questions)

#########################################################################

# 2 通过多个步骤问题进行检索
# 2.1 构建向量库检索器
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

# 文档检索结果必然是list[Document],必须编写一个方法将list[Document]转换为文本
def combine_document(documents: list[Document]) -> str:
    # 将每个Document中的page_content合并成一个字符串
    return "\n\n".join([doc.page_content for doc in documents])

# 2.2 使用问题分解链构建3个步骤子问题
query = "关于配置接口的信息有哪些"
step_questions = decomposition_chain.invoke(input=query)

# 2.3 定义每次进行步骤问答所使用的提示模板
prompt = ChatPromptTemplate.from_template(
    """这是这次你需要回答的问题:
    ----
    {question}
    ----

    这是所有可用的之前的背景问题和答案:
    ----
    {qa_pairs}
    ----

    这是与本次问题相关的额外背景信息:
    ---
    {context}
    ---"""
)

# 2.4 定义每次执行时需要的链
step_chain = (
    {
        "question":itemgetter("question"), # 获取原始问题
        "qa_pairs":itemgetter("qa_pairs"), # 获取上几轮的问题与回答记录
        "context":itemgetter("question") | retriever | combine_document, # 原始问题去进行知识库检索
    }
    | prompt
    | ChatOpenAI(model="gpt-3.5-turbo-16k")
    | StrOutputParser()
)

# 3 循环遍历step_questions 每个问题都执行一次step_chain
qa_pairs = "" # 用于累加每次的问题和回答
for step in step_questions:
    result = step_chain.invoke(input={
        "question":step,
        "qa_pairs":qa_pairs,
    })
    qa_pairs += '\n--------\n' + f'question:{step} \n answer:{result}'.strip()

#最后一次循环的输出 即是问题的最终答案
print(qa_pairs)



client.close()

