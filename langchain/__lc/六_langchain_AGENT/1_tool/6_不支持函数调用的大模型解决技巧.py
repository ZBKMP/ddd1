#  不支持函数调用的大模型解决技巧

import json
import os
from typing import Any, Type, TypedDict, Dict, Optional
import dotenv
import requests
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableConfig, RunnableLambda
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool, render_text_description, render_text_description_and_args
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

dotenv.load_dotenv()


# 1 创建工具
class GaodeWeatherToolArgsSchema(BaseModel):
    city: str = Field(description="需要进行天气查询的目标位置,例如:长沙,岳麓区")

class GaodeWeatherTool(BaseTool):
    """根据传入的位置信息获取对应天气数据"""
    name: str = "gaode_weather_tool"
    description: str = "根据传入的位置信息获取对应天气数据"
    args_schema: Type[BaseModel] = GaodeWeatherToolArgsSchema

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        # 1 先获取api_key
        gaode_api_key = os.getenv("GAODE_API_KEY")
        if not gaode_api_key:
            return "未配置高德开放平台的API密钥"

        # 2 从传入的参数中获取位置名称
        city = kwargs.get("city")

        # 3 根据city在高德平台中获取对应的adcode
        gaode_domain = "https://restapi.amap.com/v3"
        # 需要访问两次高德后端接口 建立一个HTTP session会话
        session = requests.Session()
        city_response = session.request(
            method="GET",
            url=f"{gaode_domain}/config/district?key={gaode_api_key}&keywords={city}&subdistrict=0",
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        # 如果响应的结果码不是200 则抛出异常
        city_response.raise_for_status()
        # 从requests.Response对象中提取JSON结果(dict)
        city_data = city_response.json()
        # print(city_data)
        # print(city_data["districts"][0]["adcode"])
        # 判断city_data中是否包含正确响应的结果
        if (city_data["info"] == "OK"
                and
                int(city_data["count"]) > 0):
            adcode = city_data["districts"][0]["adcode"]
            # 再使用天气查询路径获取天气信息数据
            weather_response = session.request(
                method="GET",
                url=f"{gaode_domain}/weather/weatherInfo?key={gaode_api_key}&city={adcode}&extensions=all",
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            # 如果响应的结果码不是200 则抛出异常
            weather_response.raise_for_status()
            # 结果转换为字典
            weather_data = weather_response.json()
            if (weather_data["info"] == "OK"
                    and
                    int(weather_data["infocode"]) == 10000):
                return json.dumps(weather_data, ensure_ascii=False)
        return f"获取{city}的天气信息失败"

gaode_weather_tool = GaodeWeatherTool()

class GoogleSerperToolArgsSchema(BaseModel):
    query: str = Field(description="执行google搜索时传入的搜索关键词")

google_serper_tool = GoogleSerperRun(
    name="google_serper_tool",
    description=(
        "一个低成本的谷歌搜索API,"
        "当你需要回答有关时事的问题时,可以调用该工具."
        "该工具的输入是搜索查询语句"
    ),
    api_wrapper=GoogleSerperAPIWrapper(),
    args_schema=GoogleSerperToolArgsSchema,
)

# 将上述两个工具组成字典与列表
tool_dict = {
    gaode_weather_tool.name: gaode_weather_tool,
    google_serper_tool.name: google_serper_tool,
}
tool_list = [gaode_weather_tool, google_serper_tool]

# 2 模拟不支持工具调用的大模型(不准使用bind_tools方法) 来实现工具调用
#  生成所有工具的描述信息文本
tool_descriptions = render_text_description_and_args(tool_list)
# print(tool_descriptions)

# 3 构建工具调用提示模板
system = """你是一个由OPENAI开发的聊天机器人,可以访问以下工具:
以下是每个工具的名称和描述:
{tool_descriptions}

根据用户输入,返回要使用的工具名称和参数输入,
将你的响应作为具有'name'和'arguments'键的JSON块返回
其中'name'表示函数名称,'arguments'是一个字典,key为参数名,值对应从用户输入中解析的参数值
"""
prompt = ChatPromptTemplate.from_messages([
    ('system',system),
    ('human',"{query}")
]).partial(tool_descriptions=tool_descriptions) # 预先传入工具列表描述信息

# 4 构建大模型
llm = ChatOpenAI(model='gpt-4o-mini')

# 5 测试工具调用
chain = prompt | llm
ai_message = chain.invoke({"query": "长沙最近的天气情况怎么样?"})
print(ai_message)
# {\n  "name": "gaode_weather_tool",\n  "arguments": {\n    "city": "长沙"\n  }\n}

# ai_message = chain.invoke({"query": "请告诉我长沙最近的天气情况,以及至今为止马拉松世界记录是多少?"})
# print(ai_message)
# ai_message = chain.invoke({"query": "你好 你是谁?"})
# print(ai_message)

# 根据不同的问题 测试结果可能生成了工具调用信息,也有生成不了,
# 也有可能生成了工具调用的格式,但没有对应的工具,可能只能生成一次工具调用

print("*"*50)

# 6 将工具调用信息进行解析 调用工具 再将结果传回大模型
#   再原本链的最后.增加一个组件用于执行工具(一定会执行一个工具)
# TypeDict 定义一个字典的格式规范 必须包含定义的key
class TookExecutorDict(TypedDict):
    name:str
    arguments:dict[str, Any]
# 工具执行者
def tool_executor(
        tool_executor_dict: TookExecutorDict,  # input输入
        config:Optional[RunnableConfig] = None, # config配置
) -> str:
    # 获取工具 传入参数 得到工具调用结果
    name = tool_executor_dict["name"]
    arguments = tool_executor_dict["arguments"]
    tool = tool_dict.get(name)
    result = tool.invoke(arguments,config)
    return json.dumps(result, ensure_ascii=False)

# 7 更新链 将大模型输出结果(json_str--dict)传递给工具执行者
chain = prompt | llm | JsonOutputParser() | RunnableLambda(tool_executor)  | llm | StrOutputParser()
result = chain.invoke({"query": "请告诉我长沙最近的天气情况"})
print(result)

# 要求 3 完善上述链 再第二次传递给llm之前 将原始问题以及工具调用结果 传递给一个提示模板再传递给llm