# LangGraph子图架构实现AI工作流 :
# 根据输入信息,通过子图分别实现输出 抖音直播带货文案 和 小红书推广文案

from typing import TypedDict, Any, Annotated

import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# 1 创建模型
dotenv.load_dotenv()
llm = ChatOpenAI(model='gpt-4o-mini')

# 2 定义工具
# google搜索 工具
class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")
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


# 3 设计父图状态 如果不设置每个属性的归纳函数,则再一个节点生成该节点内容之后,会将并行的其他节点需要的内容覆盖为None
#   该归纳函数逻辑:判断该属性有没有生成内容 有则替覆盖来的None,如果没有生成内容则不覆盖。
def overwrite_str(left:str|None,right:str|None)->str:
    # 实现 如何将right 覆盖 left
    if right is not None and right.strip() :
        return right # 图就会将right值覆盖left
    else:
        return left

# 设计父图状态 包含原始输入,每个子节点分别生成的文本结果,都需要使用归纳函数
class AgentState(TypedDict):
    query: Annotated[str,overwrite_str]   # 用户原始提问
    live_content: Annotated[str,overwrite_str]  # 抖音直播带货文案结果
    xhs_content: Annotated[str,overwrite_str]   # 小红书推广文章结果

# 4 设计子图状态 都继承于父图
# 4.1 抖音子图 过程中会执行工具调用 所以还需要增加消息列表
class LiveAgentState(TypedDict):
    query: Annotated[str, overwrite_str]
    live_content: Annotated[str, overwrite_str]
    xhs_content: Annotated[str, overwrite_str]
    # 该子图需要的 消息列表
    messages: Annotated[list[BaseMessage],add_messages]
# 4.2 小红书子图 过程进需要大模型生成结果即可
class XhsAgentState(AgentState):
    pass


# 5 创建子图节点
#################################################################################################
# 5.1 创建直播带货子图  ( 优化之前工具调用智能体,在大模型节点增加了提示模板 )
live_graph_builder= StateGraph(state_schema=LiveAgentState)
# 直播带货子图的大模型节点
def live_chat_bot(
        state:LiveAgentState,  # 第二轮执行该节点时 状态query:xxxx , messages:[ai_msg,tool_msg]
        config:RunnableConfig
)->dict[str,Any]:
   # 编辑该节点是 需要牢记该节点是会被调用两次的!
   # 1 生成包含工具调的AI消息
   # 2 将工具调用结果再次传入该节点 生成最终内容

   # 在直播带货的大模型节点内 增加提示模板 用于指导大模型生成直播带货文案
   prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "你是一个拥有10年经验的直播文案专家，请根据用户提供的产品整理一篇直播带货脚本文案，如果在你的知识库内找不到关于该产品的信息，可以使用搜索工具。"
        ),
        ("human", "{query}"),  # 人类输入
        # 再循环再次调用大模型时,状态的消息列表中会有工具调用结果,将消息列表存入到chat_history内以告知大模型已经调用了工具
        ("placeholder", "{chat_history}"),
   ])
   # 有了提示模板 则必须以chain的形式执行LLM
   chain = prompt | llm.bind_tools([google_serper_tool])
   # 执行chain
   ai_msg = chain.invoke(
       input={
           "query": state["query"],# 状态中提取出用户初始提问
           "chat_history": state["messages"],#第二次执行大模型时需要将第一轮产生的AI_msg,和Tool_msg合并到提示模板 则能最终生成内容
       },
   )

   # 编辑返回结果
   return {
       # 针对第一轮 会产生工具调用消息，需要将该工具调用消息合并到状态中的messages
       "messages":[ai_msg],
       # 第二轮执行时,该节点会生成最后的文案结果
       "live_content":ai_msg.content
   }

live_graph_builder.add_node("live_chat_bot", live_chat_bot)
# 直播带货子图的工具调用节点
live_graph_builder.add_node("tools", ToolNode([google_serper_tool]))
# 绘制直播带货子图的边
live_graph_builder.set_entry_point("live_chat_bot")
live_graph_builder.add_conditional_edges(
    source="live_chat_bot",
    path=tools_condition,
)
live_graph_builder.add_edge("tools", "live_chat_bot")
# 编译子图 编译的结果可以直接作为一个节点加入到父图
live_agent = live_graph_builder.compile()
# 要求 3 ：理解上述代码 实现优化后的工具调用智能体(llm前增加了提示模板)
##############################################################

##############################################################
#5.2 创建小红书文案子图
def xhs_chat_bot(state:XhsAgentState,config:RunnableConfig)->Any:
    # 与之前案例不同,之前直接传递状态中的消息列表让LLM生成结果,
    # 而本例中需要通过提示词编辑系统消息,让LLM生成小红书文案
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "你是一个小红书文案大师，请根据用户传递的商品名，生成一篇关于该商品的小红书笔记文案，注意风格活泼，多使用emoji表情。"),
        ("human", "{query}"),
        # 此智能体中 不需要调用工具 直接由LLM生成文案 因此不会包含工具调用的历史消息,也不会形成循环回路
    ])
    # 编辑链
    chain = prompt | llm | StrOutputParser()
    # 返回结果
    return{
        "xhs_content":chain.invoke({"query":state["query"]})
    }
xhs_graph_builder= StateGraph(state_schema=XhsAgentState)
xhs_graph_builder.add_node("xhs_chat_bot", xhs_chat_bot)
xhs_graph_builder.set_entry_point("xhs_chat_bot")
xhs_graph_builder.set_finish_point("xhs_chat_bot")
#编译子图
xhs_agent = xhs_graph_builder.compile()
##############################################################

# 6 编辑父图
agent_graph_builder = StateGraph(state_schema=AgentState)
# 以两个子图agent作为父图的节点
agent_graph_builder.add_node("live_agent", live_agent) # 直播带货子图节点
agent_graph_builder.add_node("xhs_agent", xhs_agent)  # 小红书子图节点


# 先设置一个空节点 再从空节点链到两个并行节点
def parallel_start_node(state:AgentState, config:RunnableConfig)->Any:
    return state
# 先设置一个空节点 两个并行节点先连到空节点
def parallel_end_node(state:AgentState, config:RunnableConfig)->Any:
    return state

# 开始到两个子图的并行运行
agent_graph_builder.set_entry_point("live_agent")
agent_graph_builder.set_entry_point("xhs_agent")
# 两个并行子图到结束
agent_graph_builder.set_finish_point("live_agent")
agent_graph_builder.set_finish_point("xhs_agent")

# 编译图
agent = agent_graph_builder.compile()
result = agent.invoke({"query":"潮汕牛肉丸"})
print(result)

# 总结:
# 1 包含多个子节点(子图)并行运行时归纳函数的写法
# 2 调用工具时 大模型节点中包含链 也包含提示模板后 工具调用的写法
# 3 父图中包含子图时的处理流程

# 要求 1  理解上述代码 参照直播带货子图 修改小红书子图 再其中增加工具调用(网络搜索/知识库检索等)
#          再增加其他平台处理的子图