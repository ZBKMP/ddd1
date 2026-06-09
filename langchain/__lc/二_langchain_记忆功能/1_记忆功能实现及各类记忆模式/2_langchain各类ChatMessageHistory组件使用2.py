# langchain ChatMessageHistory组件使用

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


'''
langchain中常用的ChatMessageHistory类:
1 抽象父类 BaseChatMessageHistory 实现存储历史聊天记录的基类
2 内存临时存储子类 InMemoryChatMessageHistory 实现将聊天信息临时存储于内存
3 postgres数据库聊天信息存储类 PostgresChatMessageHistory
4 文件聊天信息存储类 FileChatMessageHistory
'''
# 1 BaseChatMessageHistory 基类 与 内存存储类
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
# 2 langchain_community Postgres 存储相关类
# from langchain_community.chat_message_histories import PostgresChatMessageHistory
# 建议从 langchain-postgres 导入: pip install langchain-postgres
# from langchain_postgres import PostgresChatMessageHistory
# 3 langchain_community 文件存储相关类
from langchain_community.chat_message_histories import FileChatMessageHistory



chat_history = FileChatMessageHistory('chat_history.txt')

dotenv.load_dotenv()  # 加载配置信息
chat_model = ChatOpenAI(
    model='gpt-3.5-turbo-16k'
)
history_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个OpenAI的聊天机器人,根据用户的提问回答问题,回答时请参考以下的历史消息记录"),
    ("placeholder","{chat_history}"), # 消息列表
    ("human","用户的问题是:{query}")
])
chain = history_prompt | chat_model | StrOutputParser()

while True:
    query = input("Human:")
    if query == "exit":
        break
    content = chain.invoke({
        "query": query,
        "chat_history": chat_history.messages,
    })
    print(content)
    # 执行完一轮对话之后 将聊天记录存储于ChatMessageHistory对象
    chat_history.add_user_message(query)
    chat_history.add_ai_message(content)



