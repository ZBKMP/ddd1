# google_serper工具
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from internal.lib import add_attribute


class GoogleSerperArgsSchema(BaseModel):
    """谷歌SerperAPI搜索参数描述"""
    query: str = Field(description="需要检索查询的语句.")

# 定义方法 返回需要的工具对象 方法保持和工具名称同名
# 将上面的 Schema 类注入为下面方法(Callable)的属性
@add_attribute(attr_name="args_schema",attr_value=GoogleSerperArgsSchema)
def google_serper(**kwargs)->BaseTool:
    """谷歌搜索工具"""
    return GoogleSerperRun(
        name="google_serper",
        description="这是一个低成本的谷歌搜索API。当你需要搜索时事的时候，可以使用该工具，该工具的输入是一个查询语句",
        args_schema=GoogleSerperArgsSchema,
        api_wrapper=GoogleSerperAPIWrapper(),
    )