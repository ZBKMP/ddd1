# gpt-4o多模态输入调用工具:

import json
import os
from typing import Type, Any

import dotenv
import requests
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from pydantic import Field, BaseModel
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


# 1 定义工具
# 天气预报查询工具参数规范
class GaodeWeatherArgsSchema(BaseModel):
    city: str = Field(description="需要查询天气预报的目标城市,例如:长沙")


# 天气预报查询工具
class GaodeWeatherTool(BaseTool):
    """根据传入的城市名称查询天气"""
    name: str = "gaode_weather_tool"
    description: str = "可以根据城市名称查询对应天气预报的工具"
    args_schema: Type[BaseModel] = GaodeWeatherArgsSchema

    def _run(self, *args: Any, **kwargs: Any) -> str:
        """根据传入的城市名称运行调用api获取城市对应的天气预报信息"""
        try:
            # 1 获取GAODE API KEY
            gaode_api_key = os.getenv("GAODE_API_KEY")
            if not gaode_api_key:
                return f"未配置高德开放平台"
            # 2 从参数中获取城市名称
            city = kwargs.get("city")
            print(city)
            # 3 根据城市名称获取adcode
            gaode_domain = "https://restapi.amap.com/v3"
            session = requests.Session()
            city_response = session.request(
                method="GET",
                url=f'{gaode_domain}/config/district?key={gaode_api_key}&keywords={city}&subdistrict=0',
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            city_response.raise_for_status()  # 如果访问异常则抛出
            # 参考返回结果参数说明 解析JSON
            city_data = city_response.json()
            # print(city_data)
            if city_data["info"] == 'OK':  # 解析adcode
                adcode = city_data["districts"][0]["adcode"]
                # 4 根据adcode获取天气信息
                weather_response = session.request(
                    method="GET",
                    url=f'{gaode_domain}/weather/weatherInfo?key={gaode_api_key}&city={adcode}&extensions=all&output=json',
                    headers={"Content-Type": "application/json; charset=utf-8"},
                )
                weather_response.raise_for_status()
                weather_data = weather_response.json()
                # print(weather_data)
                if weather_data["info"] == 'OK':  # 解析weather
                    # 5 返回最后的字符串结果
                    return json.dumps(weather_data, ensure_ascii=False)
            return f"获取{city}天气预报信息失败"
        except Exception as e:
            print(e)
            return f"获取{kwargs.get('city')}天气预报信息失败"


# 创建工具
gaode_weather_tool = GaodeWeatherTool()

# 多媒体(图片,音频,视频)输入
# 2 在消息列表中 以字典列表为结构传入多模态信息 例如包含图片连接
# 2.1.构建能接受媒体文件URL的prompt
# 基础prompt 支持多模态输入 以图片URL连接传入图片信息
url_prompt = ChatPromptTemplate.from_messages(
    [
        # 人类消息内容原本为字符串,改为字典列表,以传递多模态消息(OpenAI传递多模态消息也是这样的格式)
        # 根据文本提示词 LLM会根据该链接去生成其对应的城市名称
        ("human", [
            {"type": "text", "text": "请获取以下网络图片所在城市的天气预报。"},
            {"type": "image_url", "image_url": "{image_url}"},
        ])
    ]
)

# 2.2 构建大模型 并绑定工具
llm = ChatOpenAI(model="gpt-3.5-turbo-16k").bind_tools(
    tools=[gaode_weather_tool],
    tool_choice="gaode_weather_tool"  # tool_choice 指向tool的name属性
)

# 2.3 创建 天气信息总结prompt
# 将工具生成结果填入占位符 用于让LLM根据天气工具生成的结果 再生成友好输出信息
weather_prompt = ChatPromptTemplate.from_template(
    """请整理下传递的城市的天气预报信息，并以用户友好的方式输出。
    <weather>
    {weather}
    </weather>
    """
)

# 4.将天气信息字典作为输入(原理为RunnableParallel),传入到天气信息总结prompt,再由llm生成新内容
chain = {
            "weather": (
                    {"image_url": RunnablePassthrough()}
                    | url_prompt
                    | llm
                    | (lambda ai_msg: ai_msg.tool_calls[0]["args"])  # 从AI_MESSAGE结果提取工具调用信息
                    | GaodeWeatherTool()
                    # | (lambda x: print(f"Weather result: {x}") or x)  # 调试输出
            )
        } | weather_prompt | llm | StrOutputParser()

print(chain.invoke("https://imooc-langchain.shortvar.com/guangzhou.jpg"))
# gpt-4o执行媒体文件输入生成耗时比较长
