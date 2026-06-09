import dotenv
from typing import Any
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, MessagesState, START

dotenv.load_dotenv()


# 1. 定义工具
class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


google_serper_tool = GoogleSerperRun(
    name="google_serper_tool",
    description="查询时事问题的工具。",
    api_wrapper=GoogleSerperAPIWrapper(),
    args_schema=GoogleSerperArgsSchema,
)
tools = [google_serper_tool]

# 2. 模型绑定
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)


# 3. 定义节点函数
def chatbot(state: MessagesState, config: RunnableConfig = None) -> Any:
    """智能体决策节点"""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def content_cleaner(state: MessagesState) -> Any:
    """内容清洗节点：如果发现不雅词汇则替换"""

    return {"messages": []}


# 4. 构建图
graph_builder = StateGraph(state_schema=MessagesState)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools))
graph_builder.add_node("cleaner", content_cleaner)  # 增加清洗节点
graph_builder.add_edge(START, "chatbot")

# 路由：chatbot 决定去 tools 还是去 cleaner
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
    {
        "tools": "tools",
        "__end__": "cleaner"  # 替代默认结束，先去清洗
    }
)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("cleaner", END)

# 5. 编译图：设置断点

graph = graph_builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["cleaner"]
)

# 6. 测试运行：第一阶段（运行至断点）
config = RunnableConfig(configurable={"thread_id": "clean_demo"})
input_data = {"messages": [HumanMessage(content="TMD，帮我查查马拉松世界纪录")]}

print("--- 启动图应用（运行中...） ---")
# 第一次运行
graph.invoke(input_data, config=config)

# 7. 模拟清洗
print("\n--- 检测到断点：正在执行内容脱敏清洗 ---")

# 获取当前状态
current_state = graph.get_state(config)
messages = current_state.values["messages"]

dirty_words = ["TMD", "王八蛋", "卧槽"]
updates = []

for msg in messages:
    content = msg.content
    if isinstance(content, str):
        new_content = content
        for word in dirty_words:
            if word in new_content:
                new_content = new_content.replace(word, "*****")


        if new_content != content:
            # 创建一个同 ID 的新对象来触发 add_messages 的更新逻辑
            updated_msg = msg.__class__(content=new_content, id=msg.id)
            updates.append(updated_msg)

if updates:
    print(f"清洗成功，修改了 {len(updates)} 条消息。")
    graph.update_state(config, {"messages": updates})
else:
    print("未发现不雅字符。")

# 8. 重新启动：从断点恢复执行
print("\n--- 恢复执行 ---")
final_result = graph.invoke(None, config=config)

# 查看最终结果
print("\n--- 最终消息列表展示 ---")
for message in final_result["messages"]:
    print(f"[{type(message).__name__}]: {message.content}")