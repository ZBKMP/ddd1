# Runnable组件动态添加默认调用参数 解决多参RunnableLambda函数传参问题
import random
from typing import Any
from langchain_core.runnables import RunnableLambda


# 定义函数 使用RunnableLambda包装为可运行组件
# 1 函数仅包含一个参数 如果需要多个包装成字典
def method_add(in_put:dict[str:Any])->int:
    # 假设传入的字典包含 key : num1  num2
    num1 : int = in_put["num1"]
    num2 : int = in_put["num2"]
    return num1 + num2
runnable = RunnableLambda(method_add)
# 包装后也称为了可运行组件  有invoke方法
result = runnable.invoke({"num1": 1, "num2": 2})
print(result)

# 2 如果函数包含多个参数:使用invoke调用时只能传递第一个参数,其他参数只能在创建Runnable对象时通过bind去传递
#   不建议这样定义函数去包装为RunnableLambda 建议使用第一种方式
def get_weather(location: str, unit: str) -> str:
    """根据传入的位置+温度单位获取对应的天气信息"""
    print("location:", location)
    print("unit:", unit)
    return f"{location}天气为{random.randint(24, 40)}{unit}"
runnable = RunnableLambda(get_weather).bind(unit="摄氏度")
result = runnable.invoke(input="长沙")
print(result)
# 按照参数为字典的模式 重新定义 get_weather 符合Runnable组件仅有一个参数的规则
