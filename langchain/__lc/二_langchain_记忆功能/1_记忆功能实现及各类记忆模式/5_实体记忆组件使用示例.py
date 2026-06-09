# langchain_实体记忆组件
import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.chains.conversation.base import ConversationChain # 在早期的langchain版本中 定义的Chain类
from langchain.memory import ConversationEntityMemory  # 实体记忆组件
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE  # 实体信息提取专用Template
from langchain_community.chat_models.baidu_qianfan_endpoint import QianfanChatEndpoint

dotenv.load_dotenv()

# 需要使用能力较强的Mmodel
llm = ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0)  # gpt-4o-mini


# 在早期的langchain版本中 定义的Chain类 ,将每个可运行组件作为参数传入
# 使用对话链 嵌入记忆组件
chain = ConversationChain(
    llm=llm,
    prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE, # 实体记忆组件专用提示模板 用户输入的key 为input
    memory=ConversationEntityMemory(llm=llm), # 传入大模型 用于从对话信息中提取以及描述实体
)


# print(chain.invoke({"input": "你好，我是小黑子。我最近正在学习LangChain。"}))
# print(chain.invoke({"input": "我最喜欢的编程语言是 Python。"}))
# print(chain.invoke({"input": "我住在广州"}))


while True:
    query = input("Human:")
    if query.lower() == "q":
        break

    result = chain.invoke({"input":query})

    print(result)


# 查询对话中的实体
entities = chain.memory.entity_store.store
print(entities)
