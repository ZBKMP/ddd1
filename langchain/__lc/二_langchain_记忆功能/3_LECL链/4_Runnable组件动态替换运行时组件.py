# Runnable组件动态替换运行时组件 configurable_alternatives方法与使用技巧

import dotenv
from langchain_community.chat_models.baidu_qianfan_endpoint import (
    QianfanChatEndpoint
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import ConfigurableField, RunnableConfig
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1 配置大模型组件在运行时可以选的做个备选组件
chat_model = ChatOpenAI(model="gpt-3.5-turbo-16k").configurable_alternatives(
    # 为当前组件准备多个同类的备选组件 配置名称必须使用which
    which=ConfigurableField(
        id="invoke_chat_model"
    ),
    # 以下就是配置多个备选
    gpt_4=ChatOpenAI(model="gpt-4o-mini"),
    qianfan=QianfanChatEndpoint(model="ernie-5.0-thinking-preview",timeout=100),
    # 针对默认值也可设置一个名称
    default_key="gpt-3.5"
)

# 2 提示模板 配置在运行时可选的多个备选组件
# 创建提示词 实现在运行过程 能切换不同的组件
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是{provider}开发的聊天机器人,请根据用户的提问回答问题"),
    ("user", "请讲一个关于{subject}的{content}"),
]).configurable_alternatives(
    which=ConfigurableField(
        id="invoke_chat_prompt"
    ),
    default_key="chat_prompt_default",
    prompt=PromptTemplate.from_template("""
        用户的提问是:{query}
    """)
)

# 3 构建链                     在此处输出上一个节点的输出 并再传递给下一个节点
chain = chat_prompt | chat_model | (lambda x: print("AI_MSG:",x) or x) | StrOutputParser()

# 3.1 执行时更改可运行组件
# result = chain.invoke(
#     input={"provider": "baidu", "subject": "程序员", "content": "冷笑话"},
#     config=RunnableConfig(configurable={
#         "invoke_chat_model": "qianfan"
#     })
# )
# print(result)


# 3.2 执行时更改可运行组件
result = chain.invoke(
    input = {"query":"你好 你是谁?"},
    config=RunnableConfig(configurable={
        "invoke_chat_prompt":"prompt"
    })
)
print(result)


# chain.with_config(config=RunnableConfig(configurable={}))
# 所有在运行时可配置的参数也可以通过with_config在invoke之前先行做配置

# 要求2 : 基于上一个要求 再更改过程: 不同方向的提问选择不同的Prompt对象,
#         不同问题选择不同的大模型 : 历史政治问题选择使用QianfanChatEndpoint,
#                                物理数学问题使用gpt-4o-mini