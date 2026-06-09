# 图结构断点实现Agent与人进行交互 在执行工具调用节点之前可以先由用户进行判断再执行
import json
from typing import TypedDict, Annotated, Any, Literal
import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.messages import ToolMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.graph.message import add_messages

dotenv.load_dotenv()
# 1 定义工具与工具列表
class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")
class DallEArgsSchema(BaseModel):
    query: str = Field(description="输入应该是生成图像的文本提示(prompt)")
# google搜索
google_serper_tool = GoogleSerperRun(
    name="google_serper_tool",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，可以调用该工具。"
        "该工具的输入是搜索查询语句。"
    ),
    api_wrapper=GoogleSerperAPIWrapper(),
    args_schema=GoogleSerperArgsSchema,
)
# 文生图片
dalle = OpenAIDALLEImageGenerationTool(
    name="openai_dalle",
    api_wrapper=DallEAPIWrapper(model="dall-e-3"),
    args_schema=DallEArgsSchema,
)
tools = [google_serper_tool, dalle]

# 2 创建大语言模型 并绑定工具
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)

# 3 定义图状态
# MessageState

# 4 定义LLM节点 使用MessagesState替代自定义State
def chatbot(state: MessagesState, config: RunnableConfig = None) -> Any:
    """聊天机器人节点"""
    ai_message = llm_with_tools.invoke(state["messages"])
    return {"messages": ai_message}

# 5 工具调用节点
# 6 路由判断函数

# 7 构建图应用
graph_builder = StateGraph(state_schema=MessagesState)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools))

graph_builder.set_entry_point("chatbot")
graph_builder.add_conditional_edges(
    source="chatbot",
    path=tools_condition,  # tools __end__
)
graph_builder.add_edge("tools", "chatbot") # 循环

# 8 在编译图过程中增加记忆功能
graph = graph_builder.compile(
    # 增加checkpointer
    checkpointer=MemorySaver(),
    # 在指定位置设置断点 遇到断点图应用会直接中断
    interrupt_after=["tools"], # 在工具执行节点之后 设置断点
)

# 9 测试 检查点--断点 效果
config = RunnableConfig(configurable={"thread_id":1})
result = graph.invoke(
    input={"messages":[HumanMessage(content="至今为止马拉松世界记录是多少?")]},
    config=config,
)
# 可以观察到 执行工具调用节点之前  图应用就会中断
for message in result["messages"]:
    print(message,type(message))

print("*******************************************************")

# 10 在恢复执行之前 读取图应用中记忆的内容(图状态) 内存读取
grahp_state = graph.get_state(config).values
print(grahp_state)


# 11 更新当前加载回的记忆状态 修改其中最后一条ToolMessage
messages = grahp_state["messages"] #提取状态中的消息列表
tool_message = ToolMessage(
    id = messages[-1].id, # 覆盖相同ID的ToolMessage
    tool_call_id = messages[-2].tool_calls[0]["id"], # 从倒数第二条消息(AI消息)获取tool_call_id
    name = messages[-2].tool_calls[0]["name"], # 从倒数第二条消息(AI消息)获取 name
    content ="截止2025年上半年,马拉松世界记录为 小黑子 02:01:01" # 篡改原有的工具调用结果
)

# 12 更新读取的记忆状态      更改状态中的messages字段,该状态设置了add_message归纳函数,遇到相同的消息ID,覆盖原有的消息
graph.update_state(config=config,values={"messages": [tool_message]})


# 13 重新启动终端的图应用
final_result = graph.invoke(input=None,config=config)
for message in final_result["messages"]:
    print(message)


# 要求2 : 使用预构件(工具调用节点,工具调用判断函数,MessageState)编辑一个能调用工具的智能体图应用.
#         在结束节点之前 增加一个断点，再重启之前，清洗每个消息内容中是否包含不雅字符(例如 : TMD 王八蛋)
#         有则替换成 *****


'''
面试题：
1、请总结langchain 跟langgraph 的区别？
2、通过langchain实现一个聊天机器人总共分几步？
3、什么时检查点？有什么作用
4、langgraph 3要素是什么？
5、什么是 HIL？
6、如何调试图程序？
7、在集群运行过程中如何保证能够在多机器上运行？
'''
