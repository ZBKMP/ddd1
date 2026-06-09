# dalle3工具
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from internal.lib import add_attribute


# dalle3工具参数格式规范
class Dalle3ArgsSchema(BaseModel):
    query: str = Field(description="输入应该是生成图像的文本提示(prompt)")

# 定义方法返回delle3工具
# 将上面的 Schema 类注入为下面方法(Callable)的属性
@add_attribute(attr_name="args_schema",attr_value=Dalle3ArgsSchema)
def dalle3(**kwargs) -> BaseTool:
    """返回dalle3绘图的LangChain工具"""
    return OpenAIDALLEImageGenerationTool(
        # model 选择图片生成模型 dall-e-3
        api_wrapper=DallEAPIWrapper(model="dall-e-3", **kwargs),
        args_schema=Dalle3ArgsSchema,
    )