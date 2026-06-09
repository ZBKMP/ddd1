from openai import BaseModel
from pydantic import Field


class ToolEntity(BaseModel):
    """API工具实体信息，记录了创建LangChain的BaseTool工具所需的配置信息"""
    # 对照 API文档中的请求响应格式 数据库Model设计 编辑属性
    id: str = Field(default="", description="API工具提供者对应的id")
    name: str = Field(default="", description="API工具的名称")
    description: str = Field(default="", description="API工具的描述信息")
    url: str = Field(default="", description="API工具发起请求的URL地址")
    method: str = Field(default="get", description="API工具发起请求的方法")
    parameters: list[dict] = Field(default_factory=list, description="API工具的参数规范列表信息")
    headers: list[dict] = Field(default_factory=list, description="API工具的请求头数据信息")

