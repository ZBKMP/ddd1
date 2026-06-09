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
    interrupt_before=["tools"], # 在工具执行节点之前 设置断点
)

# 9 测试 检查点--断点 效果
config = RunnableConfig(configurable={"thread_id":1})
result = graph.invoke(
    input={"messages":[HumanMessage(content="至今为止马拉松世界记录是多少?")]},
    config=config,
)
# 可以观察到 执行工具调用节点之前  图应用就会中断
for message in result["messages"]:
    print(message)

print("*******************************************************")

# 10 中断后还可以唤醒图应用,加载之前保存的状态信息,重新执行图应用
#    在恢复之前,增加用户输入流程,只有在用户同意的前提下 执行后续工具调用.
# 判断当前状态消息中是否包含工具调用参数消息
if hasattr(result["messages"][-1], "tool_calls") and result["messages"][-1].tool_calls :
   tool_calls = result["messages"][-1].tool_calls
   print("即将调用以下工具:",tool_calls)
   human_input = input("是否可以继续执行工具调用:")
   if human_input.lower().strip() == "yes":
       # 继续执行之前中断的图应用
       # 重启之前在断点处结束的图应用 可以基于之前保存的状态继续执行而不需要重头开始
       # 如果没传递input,但传递了包含thread_id的config,则会读取之前存储的状态在断点处继续执行
       final_result = graph.invoke(None,config)
       for message in final_result["messages"]:
           print(message)
   else:
       print("应用结束")

