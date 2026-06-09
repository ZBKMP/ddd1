# 创建自定义工具
from typing import Type, Any
from langchain_core.tools import tool, StructuredTool, BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


# 工具的参数规范
class AddToolArgsSchema(BaseModel):
    a: int = Field(description="加法工具的第一个参数")
    b: int = Field(description="加法工具的第二个参数")


# 1  @tool装饰器 将函数包装为Langchain的工具对象
@tool(
    name_or_callable="add_tool",
    # description="" 函数开头写了三引号注释 等同于写了描述
    args_schema=AddToolArgsSchema,
    return_direct=False,
)
def add_tool(a: int, b: int) -> int:
    """将传递的两个数据进行加法计算,返回结果"""
    return a + b


# 测试执行该工具
result = add_tool.invoke(input={"a": 10, "b": 20})
print(result)
# 查看工具信息
print("工具名称:", add_tool.name)
print("工具描述:", add_tool.description)
print("工具需要的参数:", add_tool.args)
print("工具的参数规范:", add_tool.args_schema)
print("工具是否直接返回结果:", add_tool.return_direct)

print("*" * 50)


# 2 StructuredTool类方法 比@tool提供了更多配置项,如同时支持同步与异步
class MultipleToolArgsSchema(BaseModel):
    a: int = Field(description="乘法工具的第一个参数")
    b: int = Field(description="乘法工具的第二个参数")


def multiple_func(a: int, b: int) -> int:  # 同步版本
    return a * b


async def a_multiple_func(a, b) -> int:  # 异步版本
    return await a * b


multiple_tool = StructuredTool.from_function(
    func=multiple_func,  # 同步方法
    coroutine=a_multiple_func,  # 异步方法
    name="multiple_tool",
    description="计算两个数字的乘法,返回相乘的结果",
    args_schema=MultipleToolArgsSchema,
    return_direct=False,
)

# 测试执行
result = multiple_tool.invoke(input={"a": 10, "b": 20})
print(result)
print("工具名称:", multiple_tool.name)
print("工具描述:", multiple_tool.description)
print("工具需要的参数:", multiple_tool.args)
print("工具的参数规范:", multiple_tool.args_schema)
print("工具是否直接返回结果:", multiple_tool.return_direct)

print("*" * 50)


# 3 继承与BaseTool父类,创建自定义工具(BaseTool实际也是一个BaseModel子类)
class SubToolArgsSchema(BaseModel):
    a: int = Field(description="除法工具的第一个参数")
    b: int = Field(description="除法工具的第二个参数")


class SubTool(BaseTool):
    name: str = "sub_tool"
    description: str = "这是一个进行除法计算的工具,传入两个数字,返回相除的结果"
    args_schema: Type[BaseModel] = SubToolArgsSchema  # 参数规范
    return_direct = False

    # 只需要重写 _run方法
    def _run(self, *args: Any, **kwargs: Any) -> Any:
        # 根据args_schema 判断出必然有的参数
        return kwargs["a"] / kwargs["b"]


sub_tool = SubTool()
result = sub_tool.invoke(input={"a": 10, "b": 20})
print(result)

print("工具名称:", sub_tool.name)
print("工具描述:", sub_tool.description)
print("工具需要的参数:", sub_tool.args)
print("工具的参数规范:", sub_tool.args_schema)
print("工具是否直接返回结果:", sub_tool.return_direct)
