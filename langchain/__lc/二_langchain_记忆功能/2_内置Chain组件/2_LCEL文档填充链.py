# langchian LCEL文档填充链  模拟RAG的效果 在生成内容前注入文档 让大模型参考文档内容去生成

import dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
# langchain的RAG概念中的文档对象 以后从知识库提取出的内容都会包装为该类对象
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 1 构建链组件
dotenv.load_dotenv()
llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个强大的AI机器人,可以通过用户提供的上下文来回复问题\n\n<context>{context}</context>"),
    ("human", "{query}"),
])

# 2 创建文档列表 模拟从某个知识库中提取出多条知识文档
documents = [
    Document(page_content="小明喜欢绿色,但不喜欢黄色"),
    Document(page_content="小王喜欢粉色,也有一点喜欢红色"),
    Document(page_content="小泽喜欢蓝色,但更喜欢青色"),
]

# 3 创建文档填充对话链
chain = create_stuff_documents_chain(
    prompt=prompt,
    llm=llm,
)

# 4 可以传入文档列表组合到提示词内
result = chain.invoke(input={
    "context": documents,
    "query": "请帮我统计一下大家都喜欢什么颜色",
})
print(result)
