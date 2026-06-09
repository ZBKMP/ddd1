# 本案例应在app_handler内实现 先以单独py文件实现
# 记忆组件的持久化与第三方集成

from operator import itemgetter
import dotenv
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

#1 加载配置对象
dotenv.load_dotenv()

#2 编辑提示模板
prompt = ChatPromptTemplate.from_messages(
    [("system", "你是OpenAi 开发的机器人， 请回答用户的问题， 现在的时间是"),
     MessagesPlaceholder("history"),
     ("human", "{query}")]
)

#3 缓冲窗口记忆组件 设置文件存储记忆组件(默认是InMemoryChatMessageHistory)
#记忆组件本身没有持久化能力,使用文件或Redis或Postgres等MessageHistory组件则能实现持久化
memory = ConversationBufferWindowMemory(
    k = 3,
    input_key="query",
    output_key="output",
    return_messages=True,
    #记忆存储使用本地文件存储
    chat_memory=FileChatMessageHistory("store_memory_history.txt")
)

#4 使用缓冲窗口记忆组件构建llm应用,每次记忆信息会存储于本地文件,则每次对话可以从本地文件获取历史记录
llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
parser = StrOutputParser()

#5 结合记忆组件 编辑链应用
runnable = RunnablePassthrough.assign(
    history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
)
chain =runnable | prompt | llm | parser

#6 执行链
query = input("query:")
content = chain.invoke({"query":query})

#7 保存历史信息至记忆组件
memory.save_context({"query":query},{"output":content})

print(content)