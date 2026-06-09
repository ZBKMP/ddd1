import os, requests
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage
load_dotenv()

# 定义图的状态
class State(TypedDict):
    # 使用 add_messages 确保对话历史能够增量更新，支持多轮工具调用
    messages: Annotated[list[BaseMessage], add_messages]




#  高德天气
@tool
def get_weather(city: str):
    """查询指定城市当前的实时天气。当用户询问气温、天气状况时使用。"""
    api_key = os.getenv("GAODE_API_KEY", "")
    url = f"https://restapi.amap.com/v3/weather/weatherInfo?city={city}&key={api_key}"
    try:
        res = requests.get(url).json()
        if res["status"] == "1" and res["lives"]:
            info = res["lives"][0]
            return f"{city}天气：{info['weather']}，气温：{info['temperature']}°C。"
    except:
        return "天气服务连接失败。"


#  谷歌搜索
@tool
def google_search(query: str):
    """搜索实时新闻、事件或知识库之外的信息。"""
    # 注入你的 SERPER_API_KEY
    os.environ["SERPER_API_KEY"] = "b49b1806c633b15830811ab1cc167fe8dfbe7b22"
    search = GoogleSerperAPIWrapper()
    return search.run(query)


#  DALL-E 3 绘图
# 配置 参数
dalle_wrapper = DallEAPIWrapper(model="dall-e-3", size="1024x1024", quality="standard")
image_gen_tool = OpenAIDALLEImageGenerationTool(api_wrapper=dalle_wrapper)

# 聚合
tools = [get_weather, google_search, image_gen_tool]
tool_node = ToolNode(tools)



# 绑定工具到大模型
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2).bind_tools(tools)


def agent_node(state: State):
    sys_msg = SystemMessage(content="""你是一个全能助手。
    你的执行逻辑必须遵循：
    - 必须【先调用】get_weather 获取真实天气，严禁自行猜测或使用缓存知识。
    - 只有在收到 get_weather 的 ToolMessage 后，才能进行后续的搜索或绘图。
    - 必须确保高德天气和谷歌搜索的结果都出现在你的最终回复中。""")
    messages = [sys_msg] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


# 构建Graph

workflow = StateGraph(State)

# 节点
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

# 连线
workflow.add_edge(START, "agent")

# 边
workflow.add_conditional_edges(
    "agent",
    tools_condition,
)

# 执行完后，回到 agent 节点进行总结
workflow.add_edge("tools", "agent")

app = workflow.compile()

# 执行测试
if __name__ == "__main__":
    print("开始执行")

    # 模拟一个涉及搜索和绘图的组合任务
    test_input = {
        "messages": [("human", "请使用高德天气搜索长沙市明天的天气，然后再使用谷歌搜索长沙市的特色美食，"
                               "最后依据查到的天气和搜到的美食，生成一张带有长沙特色地标的美食图。")]
    }

    #观察执行过程
    for event in app.stream(test_input, stream_mode="values"):
        event["messages"][-1].pretty_print()