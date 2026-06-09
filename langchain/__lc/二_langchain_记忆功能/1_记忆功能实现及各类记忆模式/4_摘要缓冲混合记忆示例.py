# langchain_摘要记忆组件 摘要缓冲混合记忆
# 长期记忆使用大模型生成摘要  近期历史保存原始记忆

import dotenv
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
# 增加百度千帆AI大模型测试
#     pip install qianfan==0.4.12.3
#     pip install transformers==4.57.0 (如果需要使用百度千帆生成摘要,则需要安装此版本 4.33.0)
from langchain_community.chat_models.baidu_qianfan_endpoint import QianfanChatEndpoint

# 摘要缓冲混合记忆 分析源码 查看该类必要属性,以及默认的摘要生成提示文本(父类SummarizerMixin)
from langchain.memory import (
    ConversationSummaryBufferMemory,
)
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter

dotenv.load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是具有AI功能的聊天机器人,请根据对应的上下文回答问题"),
    # MessagesPlaceholder("history"),  # 此占位符 需要的history是一个列表
    ("placeholder", "{history}"),  # 元祖可传可不传 声明类则必须没有也传[]
    ("human", "用户的问题是:{query}")
])

# 缓冲摘要记忆组件
summary_memory = ConversationSummaryBufferMemory(
    max_token_limit=500,
    llm=ChatOpenAI(model="gpt-3.5-turbo-16k"),  # 用于计算token以及生成摘要
    return_messages=True,
    input_key="query",
    # 可以更改底层的记忆存储模式  默认是内存存储
    chat_memory=FileChatMessageHistory('chat_history.txt')
    # prompt= ?,

)

# llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
# 改为百度千帆模型测试效果
llm = QianfanChatEndpoint(
    model="ernie-5.0-thinking-preview",
    timeout=100,
)

# 在链中使用记忆组件
chain = (RunnablePassthrough.assign(
    chat_history=RunnableLambda(lambda x: summary_memory.load_memory_variables(x)) | itemgetter("history"),
) | prompt | llm | StrOutputParser())

while True:
    query = input("Human:")

    if query.lower() == "q":
        break

    chain_input = {"query": query}

    result = chain.invoke(chain_input)
    print(result)

    # 保存记忆
    summary_memory.save_context(
        inputs=chain_input,  # 整个链的输入
        outputs={"ai": result},  # ai的输出结果  key要与memory中设置的output_key值相同
    )

    print("-------")
    # 显示历史记忆信息  获取对应的记忆信息
    print("history: ", summary_memory.load_memory_variables(chain_input))


# 要求 2 : 在缓冲摘要记忆组件中,自定义一个文本提示模板,尝试用中文重写提示模板文本内容
#          ,必须包含以下两个关键词占位符:"summary", "new_lines".


'''
运行成功后 改为百度千帆测试:
https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application
#控制台-系统管理-API key:
#https://console.bce.baidu.com/qianfan/ais/console/apiKey
#右上角个人信息-安全认证-Access Key
#https://console.bce.baidu.com/iam/#/iam/apikey/list

.env中增加以下配置
QIANFAN_API_KEY=your-qianfan-api-key
QIANFAN_ACCESS_KEY=your-qianfan-access-key
QIANFAN_SECRET_KEY=your-qianfan-secret-key
'''