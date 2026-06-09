# 构建第一个LangChainRAG应用 外挂知识库的带记忆功能的聊天机器人示例
from langchain_core.memory import BaseMemory
from operator import itemgetter
from typing import Any
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableConfig
from langchain_core.tracers import Run
from langchain_openai import ChatOpenAI
import weaviate
from langchain_openai import OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey
from weaviate.classes.query import Filter
import dotenv
# 基于Runnable封装记忆链实现记忆自动管理 :
# 1.可以通过配置 在运行时去选择不同的记忆组件
# 2.在对话完成之后自动实现保存记忆(生命周期监听函数)

dotenv.load_dotenv()
# 1 创建提示词
prompt_template = """
  你是具有AI功能的聊天机器人,如果遇到你不能回答的问题请参考以下上下文提供的知识内容来回答:
  <context>
  {context}
  </context>.\n\n
  在回答问题时还可以合传入的历史消息记录来回答.
"""
prompt = ChatPromptTemplate.from_messages([
    ("system", prompt_template),
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

################################################################################################
# 7 编辑知识库检索相关代码
# 7.1 搭建向量库
client = weaviate.connect_to_local(
    host="192.168.172.129",
    port=8080,
)
db = WeaviateVectorStore(
    client=client,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    index_name='collection_1',  # 数据集名称
    text_key='text',  # 文本内容的key名
)
# 7.2 创建检索器
retriever = db.as_retriever()

# 7.3 定义功能函数 实现将list[Document]合并为文本
def combine_document(docs:list[Document]) -> str:
    return "\n\n".join([doc.page_content for doc in docs])

################################################################################################

# 4 编辑链 在原有记忆功能链基础上改为 新增一个函数,函数获取链的输入以及配置,并将该函数包装为RunnableLambda 填入链中
chain = RunnablePassthrough.assign(
    context = itemgetter("query") | retriever | combine_document,
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

# 6 执行链
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











