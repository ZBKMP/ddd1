# langchain ChatMessageHistory组件使用

import dotenv
import openai
from langchain_experimental.graph_transformers.llm import system_prompt
from langchain_openai import ChatOpenAI
from openai import OpenAI

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

# 1 测试使用内存存储聊天记录
chat_history = InMemoryChatMessageHistory()
# 模拟添加聊天消息
chat_history.add_user_message("你好 你是谁?")
chat_history.add_ai_message("你好 我是OpenAI聊天机器人")
# 对象本身就能获取聊天记录 文本形式  重写了 __str__方法
print(chat_history)
# 消息列表形式
print(chat_history.messages)

print("*" * 50)

# 2 使用OpenAI原生代码 配合ChatMessageHistory 实现记忆功能
# 如果使用FileChatMessageHistory 需要传入文件名
chat_history = FileChatMessageHistory("chat_history.txt")

dotenv.load_dotenv()  # 加载配置信息
client = OpenAI()

while True:
    # 输入用户问题
    query = input("Human:")
    if query.lower() == "exit":
        break

    # 在系统消息中 定义包含记忆内容的关键字占位符 占位符对应的数据就是ChatMessageHistory对象
    system_prompt = f"""
        你是一个OpenAI的聊天机器人,可以根据相应的上下文回复用户的问题,上下文里包含的是你与人类聊天的历史记录消息列表.\n\n
        <context>
        {chat_history}
        </context>
    """
    # 直接输出ChatMessageHistory对象就能获取文本形式的聊天留

    # 发起聊天请求
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
    )

    # 从completion中获取AI响应
    content = completion.choices[0].message.content
    print("AI:",content)

    # 一轮对话结束之后需要保存当前对话信息
    chat_history.add_user_message(query)
    chat_history.add_ai_message(content)


#要求 : 基于langchain LCEL 改写上述代码 使用ChatMessageHistory保存或提取聊天记录