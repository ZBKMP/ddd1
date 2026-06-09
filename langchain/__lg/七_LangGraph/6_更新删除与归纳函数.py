#更新删除消息message 与 归纳函数:
from typing import Any

import dotenv

from langchain_core.messages import RemoveMessage, AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph

# 0 模型创建
dotenv.load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

# 1 创建llm_node节点函数
def chatbot(state: MessagesState, config: RunnableConfig) -> Any:
    """聊天机器人节点"""
    return {"messages": [llm.invoke(state["messages"])]}

# 2.1 创建节点函数 实现对某条消息执行删除操作
def delete_messages(state: MessagesState, config: RunnableConfig) -> Any:
    # 删除一条HumanMessage (假设输入消息列表为 System Human)
    human_message = state["messages"][1]
    # 确定被删除的消息的ID add_messages函数会执行该消息的删除
    return {"messages": [RemoveMessage(id=human_message.id)]}

# 2.2 创建节点函数 实现对某条消息执行修改操作
def update_messages(state: MessagesState, config: RunnableConfig) -> Any:
    # 修改一条消息的内容 (假设输入消息列表 最后一条消息必然是AI消息)
    ai_msg = state["messages"][-1]
    # 创建一条消息,该消息的ID和之前的AI消息相同,归纳函数add_messages会替换掉消息列表中同ID的消息
    ai_msg = AIMessage(content='***更新之后的AI消息内容***', id=ai_msg.id)
    return {
        "messages": [ai_msg],
    }


# 3 编辑图
graph_builder = StateGraph(state_schema=MessagesState)
graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("delete_messages",delete_messages)
graph_builder.add_node("update_messages",update_messages)
graph_builder.set_entry_point("chatbot")
graph_builder.add_edge("chatbot","delete_messages")
graph_builder.add_edge("delete_messages","update_messages")
graph_builder.set_finish_point("update_messages")

# 4  测试运行
result = graph_builder.compile().invoke({
    "messages":[("system","你是一个AI助手"),HumanMessage('你好 你是谁?')]
})
for message in result["messages"]:
    print(message)


# 要求1 : 使用预构件(工具调用节点,工具调用判断函数,MessageState)编辑一个能调用工具的智能体图应用.
#         在结束节点之前 增加一个内容清洗节点，循环判断每个消息内容中是否包含不雅字符(例如 : TMD 王八蛋)
#         有则替换成 *****


