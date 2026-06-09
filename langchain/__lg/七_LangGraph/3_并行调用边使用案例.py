

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.constants import END
from langgraph.graph.message import StateGraph, MessagesState

# 并行调用边使用案例:
# 1 构建图 可以直接使用MessagesState作为状态信息类(该状态类中仅包含一个属性messages)
graph_builder = StateGraph(MessagesState)

# 2 模拟LLM节点
def chatbot(state: MessagesState, config: RunnableConfig) -> Any:
    return {
        "messages":[AIMessage(content="你好 我是OpenAI机器人")]
    }

# 3 两个并行节点
def parallel1(state: MessagesState, config: RunnableConfig) -> Any:
    return {
        "messages": [HumanMessage(content="这是并行节点1")]
    }
def parallel2(state: MessagesState, config: RunnableConfig) -> Any:
    return {
        "messages": [HumanMessage(content="这是并行节点2")]
    }


#4 绘制图应用
#4.1 添加节点
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("parallel1", parallel1)
graph_builder.add_node("parallel2", parallel2)

#4.2 绘制边
graph_builder.set_entry_point("chatbot")
#并行边
graph_builder.add_edge("chatbot", "parallel1")
graph_builder.add_edge("chatbot", "parallel2")
# 并行节点 都连接到结束节点 (节点是否连接到结束,不影响该节点是否被执行)
#graph_builder.set_finish_point("parallel1")
graph_builder.add_edge("parallel2", END)

# 4.3编译
graph = graph_builder.compile()


# 5执行测试
result  = graph.invoke({
    "messages":[HumanMessage(content="测试开始")]
})

for message in result["messages"]:
    print(message)
