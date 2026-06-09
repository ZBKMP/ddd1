# 创建一个最基本的图架构聊天机器人,仅包含三个节点:  START开始节点-->LLM节点-->END结束节点
# pip install langgraph==0.6.8

from typing import TypedDict, Annotated, Any
import dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
#                           状态图       消息图                      开始节点 结束节点
from langgraph.graph import StateGraph, MessageGraph,MessagesState, START, END
from langgraph.graph.message import add_messages  # langgraph内置归纳函数(将节点输出的消息列表合并到输入的消息列表中)

# 1 先定义图需要的材料 创建LLM
dotenv.load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")


# 2 定义图状态  # TypedDict / Pydantic_BaseModel
class State(TypedDict):
    # 消息列表(即是输入 也是输出,LLM新产生的AI消息合并到输入的消息列表则是输出)
    messages:Annotated[list[BaseMessage],add_messages]
    # 如果没有设置归纳函数add_message 则节点返回的状态数据会直接覆盖原有状态数据
    info : str

# 3 创建图构建者
graph_builder = StateGraph(
    state_schema=State,
)

# 4 构建图节点 (节点的方式为函数,参数为状态 返回也是状态)
def chatbot(state:State,config:RunnableConfig)->dict[str, Any]:
    # 从状态中消息列表作为输入,让大模型进行内容生成,AI消息再合并到状态中
    messages = state["messages"]
    ai_message = llm.invoke(messages)

    # 返回结果也按照state的结构去定义
    return {
        "messages": [ai_message],
        "info": "经过节点之后对这个状态数据进行更新",
    }
graph_builder.add_node("chatbot", chatbot)
# 开始/结束 节点不需要定义

# 5 绘制边
# 开始节点--->大模型节点
graph_builder.add_edge(START,"chatbot")
# 大模型节点-->结束节点
graph_builder.add_edge("chatbot",END)

# 6 生成图应用
graph = graph_builder.compile()

# 7 执行图 输入为状态
ipt_state = {
    "messages":[SystemMessage("你是一个AI助手,负责回答用户的问题."),HumanMessage("你好 你是谁?")],
    "info":"这是测试用的字符串",
}
result =  graph.invoke(ipt_state)
print(result)