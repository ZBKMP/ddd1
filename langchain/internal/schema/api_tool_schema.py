from flask_wtf import FlaskForm
from marshmallow import Schema, fields, pre_dump
from wtforms import StringField
from wtforms.validators import DataRequired, Length, URL, Optional

from internal.exception import ValidationException
from pkg.paginator import PaginatorReq
from .schema import ListField
from internal.model import ApiToolProvider, ApiTool


# ApiToolHandler.validate_openai_schema方法中用于验证
# OpenAPI请求中是否包含参数openapi_schema
class ValidateOpenApiSchemaReq(FlaskForm):
    # 参数 openapi_schema 必填
    openapi_schema = StringField(
        label="openapi_schema",
        validators=[
            DataRequired(message="openapi_schema参数不能为空"),
        ]
    )


# ApiToolHandler.create_api_tool方法中用于验证请求参数
class CreateApiToolReq(FlaskForm):
    # 参数 工具提供商名称 name
    name = StringField(
        label="name",
        validators=[
            DataRequired(message="工具提供者名字不能为空"),
            Length(min=1, max=30, message="工具提供者的名字长度在1-30"),
        ]
    )

    # 参数 工具图标 icon URL:校验内容是否符合URL连接格式
    icon = StringField(
        label="icon",
        validators=[
            DataRequired(message="工具提供者的图标不能为空"),
            URL(message="工具提供者的图标必须是URL链接"),
        ]
    )
    # 参数 工具描述 openapi_schema 在业务层之前已经实现对内容的验证
    openapi_schema = StringField(
        label="openapi_schema",
        validators=[
            DataRequired(message="openapi_schema字符串不能为空")
        ]
    )
    # 参数属性 工具请求头headers 列表数据
    # (使用自定义的FlaskForm下的列表数据类型,使用官方的比较麻烦)
    headers = ListField()

    # 编写方法自定义对headers属性进行更为详细的校验
    # 在FlaskForm内 只要方法名为'validate_参数属性名'就会去自动调用该方法去校验对应的参数属性是否正确
    # 抛出异常则表示验证错误 , 无异常则正确
    # form表示表单本身  field表示对应的参数 field.data才能拿到参数数据
    @classmethod
    def validate_headers(cls, form, field) :
        """校验headers请求的数据是否正确，涵盖列表校验，列表元素校验"""
        for header in field.data:
            # 验证列表里的每一个字典是否正确
            if not isinstance(header, dict):
                raise ValidationException("headers里的每一个元素都必须是字典")
            # 每个header只能包含 key  value 两个数据
            if set(header.keys()) != {"key","value"}:
                raise ValidationException("headers里的每一个元素都必须包含key/value两个属性，不允许有其他属性")




# 视图方法update_api_tool_provider 定义请求的数据结构
# 与create的请求数据结构相同
class UpdateApiToolProviderReq(FlaskForm):
    """更新API工具提供者请求参数验证"""
    # 请求参数 name
    name = StringField(
        "name",
        validators=[
            DataRequired(message="工具提供者名字不能为空"),
            Length(min=1, max=30, message="工具提供者的名字长度在1-30"),
        ]
    )
    # 请求参数icon
    icon = StringField(
        "icon",
        validators=[
            DataRequired(message="工具提供者的图标不能为空"),
            URL(message="工具提供者的图标必须是URL链接"),
        ]
    )
    # 请求参数 openapi_schema
    openapi_schema = StringField(
        "openapi_schema",
        validators=[
            DataRequired(message="openapi_schema字符串不能为空")
        ]
    )
    # 请求参数 headers
    headers = ListField("headers", default=[])

    @classmethod
    def validate_headers(cls, form, field):
        """校验headers请求的数据是否正确，涵盖列表校验，列表元素校验"""
        for header in field.data:
            if not isinstance(header, dict):
                raise ValidationException(
                    "headers里的每一个元素都必须是字典"
                )
            if set(header.keys()) != {"key", "value"}:
                raise ValidationException(
                    "headers里的每一个元素都必须包含key/value两个属性，不允许有其他属性"
                )

# 为视图方法ApiToolHandler.get_api_tool_provider定义响应的数据结构
# 实现将业务层返回的对象转换成字典
class GetApiToolProviderResp(Schema):
    """获取API工具提供者响应信息"""
    # 参照要转换的对象的类 定义属性
    id = fields.UUID()
    name = fields.String()
    icon = fields.String()
    openapi_schema = fields.String()
    headers = fields.List(fields.Dict, default=[])  # 数据类型为list[dict] 默认为[]
    created_at = fields.Integer(default=0)  # 数据值为时间戳  默认0

    # 定义方法实现 实现将类ApiToolProvider(db.Model)对象转化为字典 从而实现序列化为JSON
    @pre_dump
    def process_data(self, data:ApiToolProvider,**kwargs):
        return {
            "id":data.id,
            "name": data.name,
            "icon": data.icon,
            "openapi_schema": data.openapi_schema,
            "headers": data.headers,
            # 将时间类型转换为 int
            "created_at": int(data.created_at.timestamp()),
        }

# 为视图方法ApiToolHandler.get_api_tool定义响应的数据结构
class GetApiToolResp(Schema):
    """获取API工具参数详情响应"""
    id = fields.UUID()
    name = fields.String()
    description = fields.String()
    inputs = fields.List(fields.Dict, default=[]) # 参数列表
    provider = fields.Dict() # 对应的提供者信息

    # 定义方法实现 实现将类ApiTool(db.Model)对象转化为字典,以便转为JSON
    @pre_dump
    def process_data(self, data: ApiTool, **kwargs):
        # ApiTool的响应结果里还要包含对应的Provider信息
        provider = data.provider  # 给ApiTool增加只读属性
        return {
            "id": data.id,
            "name": data.name,
            "description": data.description,
            # 提取所有parameter参数信息(字典),每个parameter中排除掉其中的in字段
            "inputs": [
                {k: v for k, v in parameter.items() if k != "in"}
                for parameter in data.parameters
            ],
            # ApiTool的响应结果里还要包含对应的Provider信息
            "provider": {
                "id": provider.id,
                "name": provider.name,
                "icon": provider.icon,
                "description": provider.description,
                "headers": provider.headers,
            }
        }

# 视图方法ApiToolHandler.get_api_tools_providers_with_page定义请求的数据结构
# 继承于分页Req基类
class GetApiToolProvidersWithPageReq(PaginatorReq):
    # 参数属性 搜索关键字 Optional()表示此为可选参数
    search_word = StringField(
        "search_word",
        validators=[Optional()],# 参数可选
    )
    # 分页的相关参数属性 包含在父类PaginatorReq中, 实现通用性



# 视图方法ApiToolHandler.get_api_tools_providers_with_page定义响应的数据结构
class GetApiToolProvidersWithPageResp(Schema):
    # 参照要转换的对象的类 定义属性
    id = fields.UUID()
    name = fields.String()
    icon = fields.String()
    description = fields.String()
    tools = fields.List(fields.Dict, default=[]) #  工具列表
    headers = fields.List(fields.Dict, default=[])  # 数据类型为list[dict] 默认为[]
    created_at = fields.Integer(default=0)  # 数据值为时间戳  默认0

    # 定义方法将类ApiToolProvider(db.Model)对象转化为字典 以便转为JSON
    @pre_dump
    def process_data(self, data:ApiToolProvider,**kwargs):
        # 获取该提供商下所有工具列表 编写一个只读属性 获取该提供商下所有工具列表
        tools = data.tools

        return {
            "id": data.id,
            "name": data.name,
            "icon": data.icon,
            "description": data.description,
            "headers": data.headers,
            # 遍历提供商下的所有工具 每个工具都编辑成一个字典 组成字典列表
            "tools":[
                {
                    "id": tool.id,
                    "description": tool.description,
                    "name": tool.name,
                    # 读取parameters时,去掉其中每个字典的 in 字段
                    "inputs": [
                        {
                           k:v for k,v in parameter.items()  if k!='in'
                        }
                        for parameter in tool.parameters
                    ],
                }for tool in tools
            ],
            "created_at": int(data.created_at.timestamp()),
        }




