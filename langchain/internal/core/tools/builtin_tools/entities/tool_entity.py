from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field

# 3 实现带可配置参数的工具配置及获取逻辑 : 工具可配置参数类型枚举类
class ToolParamType(str, Enum):
    """工具可配置参数类型枚举类"""
    STRING = "string" # 文本框/单选按钮 文字
    NUMBER = "number" # 文本框/单选按钮 数字
    BOOLEAN = "boolean" # 复选框 勾选
    SELECT = "select" #下拉菜单类型数据


# 2 实现带 可配置参数 的工具配置及获取逻辑 : 工具可配置参数类型实体类
class  ToolParam(BaseModel):
    """工具可配置参数类型实体类"""
    name: str  # 参数的实际名字
    label: str  # 参数的前端展示标签
    type: ToolParamType  # 参数的类型,定义一个枚举限定类型范围(下拉菜单,文本框,单选按钮... ...)
    required: bool = False  # 是否必填
    default: Optional[Any] = None  # 默认值
    min: Optional[float] = None  # 最小值
    max: Optional[float] = None  # 最大值
    # 下拉菜单选项列表 默认值不要使用[] 要使用Field
    options: list[dict[str, Any]] = Field(default_factory=list)



# 1 工具实体类
class ToolEntity(BaseModel):
    """工具实体类，存储的信息映射的是工具名.yaml里的数据"""
    name: str  # 工具名字
    label: str  # 工具标签
    description: str  # 工具描述
    # 1.1 工具可配置参数 先定义为空列表 默认工具没有可配置参数
    # params:list=[]

    # 1.2 实现带可配置参数的工具配置及获取逻辑 :
    # 工具的可配置参数信息也需要进行类型验证,默认值不要使用[],要使用Field
    params: list[ToolParam] = Field(default_factory=list)

