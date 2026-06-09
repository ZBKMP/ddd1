from operator import itemgetter
from typing import Any

import dotenv
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
from langchain_core.memory import BaseMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableConfig
from langchain_core.tracers import Run
from langchain_openai import ChatOpenAI

# 基于Runnable封装记忆链实现记忆自动管理 :
# 1.可以通过配置 在运行时去选择不同的记忆组件
# 2.在对话完成之后实现自动保存记忆(生命周期监听函数)

dotenv.load_dotenv()
# 1 创建提示词
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是具有AI功能的聊天机器人,请结合传入的历史消息记录来回答问题."),
    ("placeholder", "{chat_history}"),
    ("human", "用户的问题是:{query}")
])
# 2 创建模型:
chat_model = ChatOpenAI(model="gpt-3.5-turbo-16k")

# 3 定义函数 参数为链的输入以及配置,返回带有记忆内容的字典,将该函数填入到链中RunnablePassthrough.assign 会将链的input以及Config都传给他
def _load_memory_variables(in_put:dict[str,Any],config:RunnableConfig) -> dict[str,Any]:
    # 1 从config 中提取配置信息
    configurable = config.get("configurable",{})
    # 2 从configurable中提取memory配置 得到记忆组件
    memory = configurable.get("memory",None)
    # 3 判断是否正确获取到了记忆组件对象
    if memory is not None and isinstance(memory,BaseMemory):
        # 从记忆组件中提取记忆内容
        return memory.load_memory_variables(in_put)
    # 4 如果没有正常获取记忆组件 则返回一个空记忆
    return {"history":[]}

# 4 编辑链 在原有记忆功能链基础上改为 新增一个函数,函数获取链的输入以及配置,并将该函数包装为RunnableLambda 填入链中
chain = RunnablePassthrough.assign(
    #                 获取链的输入:  lambda input,config:{"history":buffer}
    chat_history = RunnableLambda(_load_memory_variables) | itemgetter("history"),
) |  prompt | chat_model | StrOutputParser()

# 5 再为链增加生命监听函数  on_end 在执行链操作的末尾 自动保存记忆
def _on_end(run_obj: Run, config: RunnableConfig) -> None:
    # 1 从config中获取配置信息
    configurable = config.get("configurable",{})
    # 2 再从配置信息中获取memory配置
    memory = configurable.get("memory",None)
    # 3 判断是记忆组件对象 才进行记忆保存
    if memory is not None and isinstance(memory,BaseMemory):
        # 从Run参数中获取链的输入以及输出
        memory.save_context(
            inputs=run_obj.inputs,
            outputs=run_obj.outputs,
        )
chain = chain.with_listeners(
    on_end = _on_end
)

############################################################################################

# 5 执行链
# 预先定义好了多种可选择的记忆组件
#   记忆组件 配合生命周期函数使用时,output_key必须设置为output,或者不设置默认为output
summary_memory = ConversationSummaryBufferMemory(
    max_token_limit=500,
    return_messages=True,
    input_key="query",
    output_key="output",
    llm=ChatOpenAI(model="gpt-3.5-turbo-16k"),
)
window_memory = ConversationBufferWindowMemory(
    k=3,
    return_messages=True,
    input_key="query",
    output_key="output",
)

while True:
    query = input("Human")

    if query.lower() == "exit":
        break

    in_put ={"query":query}

    #在执行链的过程中需要增加运行时可配置参数 memory 表示当下需要选择的记忆组件
    result = chain.invoke(
        input=in_put,
        config = RunnableConfig(configurable={
            "memory":window_memory
        })
    )

    print(result)

    # 一次对话结束之后 不需要执行保存 在chain的定义中就完成记忆保存过程


# 要求 3 : 理解这个案例


# 要求 4 : 不使用langchain内置的这些记忆组件 配合MySQL实现记忆存储类 只读取近期的N条对话 之前的都生成摘要
# 提供方法  加载记忆(返回消息列表/字符串) 存储记忆(参数 id  对话ID(uuid) 人类提问 和 AI生成 保存时间)