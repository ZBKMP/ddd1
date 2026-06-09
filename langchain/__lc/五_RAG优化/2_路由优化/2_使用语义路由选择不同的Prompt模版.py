# 使用语义路由选择不同的Prompt模版
import dotenv
from langchain.utils.math import cosine_similarity
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

dotenv.load_dotenv()

# 1.定义两份不同的prompt模板(物理模板、数学模板)
physics_template = """你是一位非常聪明的物理教程。
你擅长以简洁易懂的方式回答物理问题。
当你不知道问题的答案时，你会坦率承认自己不知道。

这是一个问题：
{query}"""

math_template = """你是一位非常优秀的数学家。你擅长回答数学问题。
你之所以如此优秀，是因为你能将复杂的问题分解成多个小步骤。
并且回答这些小步骤，然后将它们整合在一起回来更广泛的问题。

这是一个问题：
{query}"""

# 2 使用嵌入模型 将原问题与两个提示模板进行相似性比对
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
prompts = [physics_template,math_template]
prompt_vectors = embeddings.embed_documents(prompts)


# 3 定义方法 将用户传入的内容 与 prompt_vectors向量值进行比对 找到合适的提示模板
def prompt_router(ipt:dict) -> ChatPromptTemplate:
    # 将用户输入的问题 也生成对应的向量值
    query_vector = embeddings.embed_query(ipt["query"])

    # 使用langchain的cosine_similarity 计算query向量值与prompt_vectors向量列表的相似性
    # 比较两个向量列表之间的相似度 会得到一个二维数组 numpy.ndarray
    similarity = cosine_similarity(
        X = [query_vector],
        Y = prompt_vectors
    )[0] # 计算query向量值与prompt_vectors向量列表的相似性 从结果中提取元素0即可

    # 从similarity.argmax() 中找到相似度最高元素的索引 在对应找到prompt文本
    most_similar_prompt = prompts[similarity.argmax()]

    # 使用找到的文本创建提示模板
    return ChatPromptTemplate.from_template(most_similar_prompt)


# 将上述函数编辑到链中 测试提示模板的路由选择效果
chain = (
    {"query":RunnablePassthrough()}
    | RunnableLambda(prompt_router)
    | (lambda x : print("prompt:",x) or x )
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)

result = chain.invoke("请介绍一下余弦计算公式?")
print(result)
print("---------------------------------------------------")
result = chain.invoke("请介绍一下牛顿第一定律?")
print(result)

# 要求 3 提供一组提示模板分别可用于回答 : 历史 地理 物理 化学...... 问题
#     根据用户的提问 由大模型自动选择合适的提示模板进行内容回答.

