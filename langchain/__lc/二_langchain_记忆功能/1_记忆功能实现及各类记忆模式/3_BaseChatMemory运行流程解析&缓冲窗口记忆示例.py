# langchain BaseChatMemory运行流程解析

import dotenv
import openai
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

# 记忆组件抽象父类 非Runnable
from langchain_core.memory import BaseMemory
# 继承于BaseMemory,但仍为抽象父类
from langchain.memory.chat_memory import BaseChatMemory

from langchain.memory import ConversationBufferMemory,ConversationBufferWindowMemory,ConversationTokenBufferMemory
from langchain_core.runnables import RunnablePassthrough, RunnableLambda # 将函数包装为可运行组件
from operator import itemgetter

# 创建模型:
dotenv.load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

# 创建提示词 要包含消息列表存储聊天记录
#MessagesPlaceholder要求必须传递一个消息列表,没有也得传[]
#使用 ("placeholder","{chat_history}") 没有可以不传
prompt = ChatPromptTemplate.from_messages([
    ("system","你是OpenAI的聊天机器人,请结合传入的聊天历史来回答问题"),
    # MessagesPlaceholder("chat_history"),
    ("placeholder","{chat_history}"),
    ("human","用户的问题是:{query}"),
])

# 缓冲窗口记忆组件
window_memory = ConversationBufferWindowMemory(
    k=3,# 保存的记忆轮数
    return_messages=True,# 读取记忆返回结果是否为消息列表,否则就是文本
    input_key="query", # 在用户输入的input字典中 哪个key表示用户提问
    output_key="ai", # 保存在记忆中AI消息内容key
    # 可以更改底层的记忆存储模式  默认是内存存储
    chat_memory=FileChatMessageHistory('chat_history.txt')
)
# 缓冲令牌记忆组件 通过限制token长度来保留一定长度的记忆内容
token_memory = ConversationTokenBufferMemory(
    max_token_limit=1000, # 限制记忆内容的token长度
    llm = ChatOpenAI(model="gpt-3.5-turbo-16k"), # 该模型仅用于计算token长度
    return_messages=True,
    input_key="query",
    output_key="ai",
    # 可以更改底层的记忆存储模式  默认是内存存储
    chat_memory=FileChatMessageHistory('chat_history.txt')
)

# 创建链 : 每次执行大模型之前需要把之前的历史记录填入到提示模板
# 从记忆组件中读取记忆的方法都是load_memory_variables
# 其中参数为整个链的输入(字典) 返回字典: {"history":记忆内容(str/messages)}

# chain =RunnablePassthrough.assign(
#     chat_history = lambda x: window_memory.load_memory_variables(x).get("history"),
# ) |prompt | llm |StrOutputParser()

# 和上述写法效果相同
chain =RunnablePassthrough.assign(
    chat_history = RunnableLambda(lambda x: window_memory.load_memory_variables(x)) | itemgetter("history") ,
) |prompt | llm |StrOutputParser()

while True:
    query = input("Human:")

    if query.lower() == "q":
        break

    chain_input = {"query": query}

    result = chain.invoke(chain_input)
    print(result)

    # 保存记忆
    window_memory.save_context(
        inputs=chain_input, # 整个链的输入
        outputs={"ai":result}, # ai的输出结果  key要与memory中设置的output_key值相同
    )

# 要求1 : 尝试 使用RunnableParallel 改写上述代码