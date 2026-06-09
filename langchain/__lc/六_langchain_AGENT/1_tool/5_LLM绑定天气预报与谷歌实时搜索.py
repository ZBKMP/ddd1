# bind() 与 bind_tools():
# LLM 绑定天气预报与谷歌实时搜索:

import json
import os
from typing import Any, Type
import dotenv
import requests
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper

dotenv.load_dotenv()


# 1 准备所有需要的工具
# 高德天气工具参数规范
class GaodeWeatherToolArgsSchema(BaseModel):
    city: str = Field(description="需要进行天气查询的目标位置,例如:长沙,岳麓区")


#  定义高德天气预报工具
class GaodeWeatherTool(BaseTool):
    name: str = "gaode_weather_tool"
    description: str = "根据传入的位置信息获取对应天气数据"
    args_schema: Type[BaseModel] = GaodeWeatherToolArgsSchema

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        # 高德服务的根路径
        gaode_domain = "https://restapi.amap.com/v3"

        # 1 先获取高德APIkey
        gaode_api_key = os.getenv("GAODE_API_KEY")
        if not gaode_api_key:
            return "未配置高德开放平台的API密钥"

        # 2 从传入的参数 使用requests 获取adcode
        city = kwargs.get("city")
        # 有两次http访问 开始session
        session = requests.Session()
        city_response = session.request(
            method="GET",
            url=f'{gaode_domain}/config/district?key={gaode_api_key}&keywords={city}&subdistrict=0',
        )
        # 如果响应状态码不是200 抛出异常
        city_response.raise_for_status()
        # 从response中提取JSON响应结果
        city_data = city_response.json()  # dict list[dict]  str list[str]
        # 从结果中提出adcode数据
        if city_data["info"] == "OK" and int(city_data["count"]) > 0:
            # 判断按地址名称能正确的获取到数据 才从中提取adcode
            adcode = city_data["districts"][0]["adcode"]

            # 3 根据获取的adcode 再次查询天气信息
            weather_response = session.request(
                method="GET",
                url=f'{gaode_domain}/weather/weatherInfo?key={gaode_api_key}&city={adcode}&extensions=all',
            )
            # 如果响应的结果码不是200 则抛出异常
            weather_response.raise_for_status()
            # 结果转换为字典
            weather_data = weather_response.json()
            if weather_data["info"] == "OK" and int(weather_data["count"]) > 0:
                return json.dumps(weather_data, ensure_ascii=False)

        return f"获取{city}的天气信息失败"


gaode_weather_tool = GaodeWeatherTool()


# 定义谷歌Serper工具的参数规范
class GoogleSerperToolArgsSchema(BaseModel):
    query: str = Field(description="执行google搜索时传入的搜索关键词")


# 创建工具
google_serper_tool = GoogleSerperRun(
    name="google_serper_tool",
    description=(
        "一个低成本的谷歌搜索API,"
        "当你需要回答有关时事的问题时,可以调用该工具."
        "该工具的输入是搜索查询语句"
    ),
    api_wrapper=GoogleSerperAPIWrapper(),  # 内部已经包含了参数规范描述
    args_schema=GoogleSerperToolArgsSchema,
)

# 2 将所有工具组合成字典与列表
tool_dict = {
    gaode_weather_tool.name: gaode_weather_tool,
    google_serper_tool.name: google_serper_tool,
}
tool_list = [gaode_weather_tool, google_serper_tool]

# 3 创建prompt
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "你是由OpenAI开发的聊天机器人，可以帮助用户回答问题，必要时刻请调用工具帮助用户解答，如果问题需要多个工具回答，请一次性调用所有工具，不要分步调用"),
    ("human", "{query}"),
])

# 4 创建LLM (支持工具调用的大模型)
llm = ChatOpenAI(model='gpt-4o-mini')
# 5 大模型绑定工具
llm = llm.bind_tools(tools=tool_list)
# 6 编辑链测试工具调用  直接访问AIMessage
chain = {"query": RunnablePassthrough()} | prompt | llm
# 7 调用链
# ai_message = chain.invoke("请告诉我长沙最近的天气情况?")
# print(ai_message)
# {'name': 'gaode_weather_tool', 'args': {'city': '长沙'}, 'id': 'call_2gXIGkrkKv2AQITVQppTKLVO', 'type': 'tool_call'}

# query = "请告诉我长沙最近的天气情况,以及至今为止马拉松世界记录是多少?"
# ai_message = chain.invoke(query)
# print(ai_message)
#  {'name': 'gaode_weather_tool', 'args': {'city': '长沙'}, 'id': 'call_ztTth3ncHi8NzmFHxkdShPAy', 'type': 'tool_call'}, {'name': 'google_serper_tool', 'args': {'query': 'current marathon world record'}, 'id': 'call_leGWmYy5ZvJ5oSo66RnFrJW0', 'type': 'tool_call'}

# query = "你好 你是谁?"
# ai_message = chain.invoke(query)
# print(ai_message) # content 和 tool_calls 只能2选1


query = "请告诉我长沙最近的天气情况,以及至今为止马拉松世界记录是多少?"
ai_message = chain.invoke(query)
# 8 通过 有无tool_calls 以及 tool_calls的长度 来判断llm是调用函数还是正常输出
tool_calls = ai_message.tool_calls
if tool_calls is not None and len(tool_calls) > 0:

    # 如果有工具还要通过循环方式访问工具调用信息列表
    # 由工具调用结果 需要封装为ToolMessage 加入到消息列表 再传递给大模型 才最终得到结果.
    # 8.1 获取原有的消息列表
    messages = prompt.invoke(query).to_messages()  # System  Human
    messages.append(ai_message)  # AI
    # 8.2 接着将工具调佣信息中 每个tool_call包装为一个ToolMessage 加入到消息列表
    for tool_call in tool_calls: # ToolMessage ...
        # 获取工具 参数  id
        tool = tool_dict[tool_call["name"]]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]
        # 调用工具 获取工具执行结果 结果通过json.dumps转换为JSON字符串
        tool_result = json.dumps(tool.invoke(tool_args))
        # 包装成一个ToolMessage
        tool_message = ToolMessage(
            content=tool_result,
            tool_call_id=tool_id,
        )
        # 加入到消息列表
        messages.append(tool_message)

    # print(messages)
    # 将最终的消息列表再次传递给大模型 以得到最终结果
    final_result = llm.invoke(messages) # 大模型可以使用消息列表作为参数
    print(final_result) # 试用大模型再生成结果时 也有可能再次调用其他工具
else:
    print(ai_message.content)

# 上述代码已具备Agent雏形
# 要求1  编写一个智能体程序,大模型可以处理天气请求,网络搜索,图片生成,知识库检索(写成工具) 注意每个工具的描述以及提示模板的写法

# 要求2  将昨天的chat-to-sql 功能通过 function_call实现
