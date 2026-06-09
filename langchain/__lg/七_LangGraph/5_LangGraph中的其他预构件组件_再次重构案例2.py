import json
from typing import TypedDict, Annotated, Any, Literal
import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode,tools_condition # 内置的工具执行节点 以及工具调用条件判断函数

# 使用图结构实现工具调用 判断 循环
dotenv.load_dotenv()

# A.创建图所需要准备的材料
# 1.定义工具与工具列表
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

# 2. 创建大语言模型 并绑定工具
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)

# 3. 定义图状态
# MessagesState 和上述代码本质是一样的

# 4. 定义LLM节点函数
def chatbot(state: MessagesState,config:RunnableConfig) :
    print("LLM_NODE_INPUT:", state, "\n\n")
    ai_message = llm_with_tools.invoke(state["messages"])
    return {
        "messages": [ai_message],
    }

# 5. 定义工具调用节点函数
'''
def tool_executor(state: MessagesState, config: RunnableConfig = None) -> Any:
    print("TOOL_NODE_INPUT:", state, "\n\n")
    # 此时消息列表中的最后一条消息必然是AI消息,而且一定包含工具调用信息
    tool_calls = state["messages"][-1].tool_calls
    # 将工具列表转换为工具字典
    tools_dict = {
       tool.name:tool for tool in tools
    }
    # 循环调用工具列表 将工具执行结果封装到消息列表
    tool_messages = []
    for tool_call in tool_calls:
        tool = tools_dict[tool_call["name"]] # 通过名字获取工具
        result = tool.invoke(tool_call["args"]) # 执行工具
        # 工具调用结果封装为ToolMessage
        tool_messages.append(ToolMessage(
            tool_call_id = tool_call["id"],
            content = result,
            name = tool_call["name"],
        ))
    return {
        "messages": tool_messages, #所有工具调用结果列表合并到原消息列表
    }
'''
# langgraph中已近预制了一个通用的工具调用节点 ToolNode

#6. 条件边需要的路由函数,用于决定后续节点是什么,返回值用Literal[str,str,....]表示
#   结果只能是工具节点tool_executor_node 或 结束节点END
'''
def route(
        state: MessagesState,
        config: RunnableConfig,
)->Literal["tool_executor","__end__"]:
    print("conditional_route_INPUT:", state, "\n\n")

    # 以state作为输入,经过判断之后,结果必然是Literal中多个选项中的某一个
    # 此时最后一条消息必然是AI消息 判断消息中是否包含tool_calls
    ai_message = state["messages"][-1]
    if hasattr(ai_message, "tool_calls") and ai_message.tool_calls:
        print("execute_tool")
        return "tool_executor"
    else:
        print("execute_content")
        return END
'''
#使用tools_condition替代自定义的工具调用路由函数 要求工具调用节点必须命名为 tools
##################################################################

# B.使用上面创建的材料 构建图应用
# 1. 图构建者
graph_builder = StateGraph(state_schema=MessagesState)

# 2. 添加节点
graph_builder.add_node("chatbot",chatbot)
# 使用ToolNode替代自定义的工具执行节点
graph_builder.add_node("tools",ToolNode(tools=tools))

# 3.添加边
# 开始--LLM
graph_builder.set_entry_point("chatbot")
# LLM之后是一个条件边 可以到工具调用节点 也可以到 结束节点
graph_builder.add_conditional_edges(
    source="chatbot",
    path = tools_condition, # 路由函数 以判断接下来去哪一个节点
)
# 工具调用节点之后可以再连到LLM节点 从而实现循环效果
graph_builder.add_edge("tools", "chatbot")

# LLM--结束(上述的条件边已经包含这条边)


# 4. 将图编辑为可运行组件
graph = graph_builder.compile()
# 5. 调佣图架构应用 得到最终状态
result = graph.invoke({
    "messages":[("human","至今为止马拉松世界记录是多少,并以此生成一张图片")]
})
# 6. 在最终结果状态中检查是否有toll_call函数调用参数
for message in result["messages"]:
    print(message)

















