import json
import os
from typing import Any, Type
import requests
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from internal.lib import add_attribute


# 天气预报查询工具参数规范 必须包含城市名称
class GaodeWeatherArgsSchema(BaseModel):
    city: str = Field(description="需要查询天气预报的目标城市,例如:长沙")

# 天气预报查询工具 继承于BaseTool
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
            print("city:",city)
            # 3 根据城市名称获取adcode
            gaode_domain = "https://restapi.amap.com/v3"
            session = requests.Session()
            city_response = session.request(
                method="GET",
                url=f'{gaode_domain}/config/district?key={gaode_api_key}&keywords={city}&subdistrict=0',
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            city_response.raise_for_status()  # 如果访问异常则抛出
            # 参考返回结果参数说明 解析JSON 返回字典
            city_data = city_response.json()
            print("city_data:",city_data)
            if city_data["info"] == 'OK':  # 解析出adcode
                adcode = city_data["districts"][0]["adcode"]
                # 4 再根据adcode获取天气信息
                weather_response = session.request(
                    method="GET",
                    url=f'{gaode_domain}/weather/weatherInfo?key={gaode_api_key}&city={adcode}&extensions=all&output=json',
                    headers={"Content-Type": "application/json; charset=utf-8"},
                )
                weather_response.raise_for_status()
                weather_data = weather_response.json()# 返回字典
                print("weather_data:",weather_data)
                if weather_data["info"] == 'OK':  # 解析weather
                    # 5 返回最后的JSON字符串结果
                    return json.dumps(weather_data, ensure_ascii=False)
            return f"获取{city}天气预报信息失败"
        except Exception as e:
            print(e)
            return f"获取{kwargs.get('city')}天气预报信息失败"

# 定义方法返回gaode_weather工具
# 将上面的 Schema 类注入为下面方法(Callable)的属性
@add_attribute(attr_name="args_schema",attr_value=GaodeWeatherArgsSchema)
def gaode_weather(**kwargs) -> BaseTool:
    """获取高德天气预报查询工具"""
    return GaodeWeatherTool()