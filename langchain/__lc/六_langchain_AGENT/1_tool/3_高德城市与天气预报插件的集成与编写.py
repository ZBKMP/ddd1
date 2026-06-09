# 高德城市与天气预报插件的集成与编写

# 需要使用的接口地址：
# 1 行政区域查询API服务接口地址 parameters表示需要传递的参数
# https://restapi.amap.com/v3/config/district?parameters

# 2 天气查询API服务接口地址 parameters表示需要传递的参数
# https://restapi.amap.com/v3/weather/weatherInfo?parameters

import json
import os
from typing import Any, Type
import dotenv
import requests
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

dotenv.load_dotenv()

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
        city_data = city_response.json() # dict list[dict]  str list[str]
        # 从结果中提出adcode数据
        if city_data["info"]=="OK"  and  int(city_data["count"]) >0:
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
                return json.dumps(weather_data,ensure_ascii=False)

        return f"获取{city}的天气信息失败"


gaode_weather_tool = GaodeWeatherTool()
result = gaode_weather_tool.invoke({"city": "changsha"})
print(result)
