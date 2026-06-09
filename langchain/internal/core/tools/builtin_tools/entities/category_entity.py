from pydantic import BaseModel, field_validator

from internal.exception import FailException


# 内置工具分类信息实体
class CategoryEntity(BaseModel):
    """分类实体"""
    category: str  # 分类唯一标识 必填
    name: str  # 分类名称 必填
    icon: str  # 分类图标名称 必填   *.svg

    # 装饰器 验证 icon属性内容 文件必须是svg类型
    @field_validator("icon")
    def check_icon_extension(cls, value: str):
        """校验icon的扩展名是不是.svg，如果不是则抛出错误"""
        if not value.endswith(".svg"):
            raise FailException("该分类的icon图标并不是.svg格式")
        return value