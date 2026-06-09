from enum import Enum

from pydantic import BaseModel, Field, field_validator

from internal.exception import ValidationException


# OpenAPI规范的数据结构
class OpenAPISchema(BaseModel):
    """OpenAPI规范的数据结构"""

    # 工具提供者的服务基础地址
    # validate_default=True 默认值也会参与校验
    server: str = Field(
        default="",
        validate_default=True,
        description="工具提供者的服务基础地址"
    )
    # 工具提供者的描述信息
    description: str = Field(
        default="",
        validate_default=True,
        description="工具提供者的描述信息"
    )
    # 工具提供者的路径参数字典
    paths: dict[str, dict] = Field(
        default_factory=dict,
        validate_default=True,
        description="工具提供者的路径参数字典"
    )

    # 对每个属性再进行深度的详细验证
    # mode="before" 对象在创建之前 即对构造函数传入的参数进行验证
    @field_validator("server", mode="before")
    def validate_server(cls, server: str) -> str:
        """校验server数据"""
        # server为空则抛出自定义异常
        if server is None or server == "":
            raise ValidationException("server不能为空且为字符串")
        return server

    @field_validator("description", mode="before")
    def validate_description(cls, description: str) -> str:
        """校验description信息"""
        # description为空则抛出自定义异常
        if description is None or description == "":
            raise ValidationException("description不能为空且为字符串")
        return description

    # 重要方法
    @field_validator("paths", mode="before")
    def validate_paths(
            cls, paths: dict[str, dict]
    ) -> dict[str, dict]:
        """校验paths字段信息，包含请求方式、描述、operationId唯一标识，parameters参数校验"""
        # 1.paths不能为空且类型为字典
        if not paths or not isinstance(paths, dict):
            raise ValidationException(
                "openapi_schema中的paths不能为空且必须为字典"
            )

        # 2.提取paths里的每一个元素,而且元素内的每个get/post都要再拆分成单独元素,组合成接口信息列表

        #  允许的请求提交方式 仅包含post/get
        methods = ['get', 'post']
        # 定义接口信息列表 存储所有提取出的接口调用信息
        interfaces = []
        # 遍历paths字典的每个key与value:
        # key为路径,value为该路径的请求描述(也是一个嵌套的字典)
        for path, path_item in paths.items():
            # 遍历所有可能的访问方式
            for method in methods:  # get  post
                # 3.如果每个path_item字典包含字段'get'或'post',
                #   将该path_item下的每个访问方式都提取成一个可访问接口(字典)
                if method in path_item:
                    interfaces.append({
                        # 接口完整路径
                        "path": path,
                        # 访问方式
                        "method": method,
                        # 特定method下的接口详情
                        # 包含description operationId parameters
                        "operation": path_item[method]
                    })
        # 没有提取出任何有效的接口信息
        if not interfaces:
            raise ValidationException("未能加载到任何合法接口请求路径")

        # 4.遍历接口信息列表,提取出所有接口并校验信息:
        #   description,operationId,parameters

        # 用于检测operationId的唯一性 记录产生过的operationId
        operation_ids = []
        # 定义空字典 容纳最终校验解析出的所有接口调用信息
        extra_paths = {}

        # 遍历接口信息列表
        for interface in interfaces:
            # 5.校验description/operationId/parameters字段是否有值 且符合期望类型
            if not isinstance(
                    interface["operation"].get("description"), str
            ):
                raise ValidationException("description不能为空且为字符串")

            if not isinstance(
                    interface["operation"].get("operationId"), str
            ):
                raise ValidationException("operationId不能为空且为字符串")

            if not isinstance(
                    interface["operation"].get("parameters", []), list
            ):
                raise ValidationException("parameters必须是列表或者为空")

            # 6.检测operationId是否是唯一的
            #   每个operationId都与之前加入的operationId进行重复判断
            #   在当前id被加入到operation_ids之前,如果就已经存在于operation_ids之内
            #   则表示已有operation_id的重复数据
            if interface["operation"]["operationId"] in operation_ids:
                raise ValidationException(
                    f"operationId必须唯一，{interface['operation']['operationId']}出现重复"
                )
            operation_ids.append(interface["operation"]["operationId"])

            # 7.校验parameters参数格式是否正确
            # 从接口详情中获取该接口所有参数列表 没有则默认为[]
            for parameter in interface["operation"].get("parameters", []):
                # 8.校验每个参数的name/in/description/required/type参数是否存在,并且类型正确
                if not isinstance(parameter.get("name"), str):
                    raise ValidationException(
                        "parameter.name参数必须为字符串且不为空"
                    )

                if not isinstance(parameter.get("description"), str):
                    raise ValidationException(
                        "parameter.description参数必须为字符串且不为空"
                    )

                if not isinstance(parameter.get("required"), bool):
                    raise ValidationException(
                        "parameter.required参数必须为布尔值且不为空"
                    )

                # 使用ParameterIn枚举来验证 in 参数是否正确
                if (
                        not isinstance(parameter.get("in"), str)
                        or
                        parameter.get("in") not in ParameterIn.__members__.values()  # 获取枚举中所有的选项
                ):
                    raise ValidationException(
                        f"parameter.in参数必须为字符串且不为空,而且必须在以下选项之内"
                        f"{'/'.join([item.value for item in ParameterIn])}"
                    )

                # 使用ParameterType枚举来验证 type 参数是否正确
                if (
                        not isinstance(parameter.get("type"), str)
                        or
                        parameter.get("type") not in ParameterType.__members__.values()  # 获取枚举中所有的选项
                ):
                    raise ValidationException(
                        f"parameter.type参数必须为字符串且不为空,而且必须在以下选项之内"
                        f"{'/'.join([item.value for item in ParameterType])}"
                    )

            # 9 对接口列表中的每个结构验证成功之后 将接口列表再转回字典模式extra_paths 作为返回值
            # 将整个interfaces列表数据再转换为字典,key为每个interface的路径path,值为字典
            # 内嵌的字典:key为请求方式,值为从operation中提取出的接口详情描述
            #          (description,operationId,parameters)再组合成的字典
            extra_paths[interface["path"]] = {
                interface["method"]: {
                    "description": interface["operation"]["description"],
                    "operationId": interface["operation"]["operationId"],
                    # 从operation提取parameters参数列表,每个参数重新包装为字典 再加入列表
                    # 这样操作的目的是从用户传递的schema结构中仅提取出需要的部分,抛弃其他部分
                    "parameters": [
                        {
                            "name": parameter.get("name"),
                            "in": parameter.get("in"),
                            "description": parameter.get("description"),
                            "required": parameter.get("required"),
                            "type": parameter.get("type"),
                        }
                        for parameter in interface["operation"].get("parameters", [])
                    ],
                }
            }

        # 最后返回paths经过验证以及过滤之后的字典
        return extra_paths


# 参数位置枚举类
class ParameterIn(str, Enum):
    """参数支持存放的位置"""
    PATH = "path"  # 路径参数
    QUERY = "query"  # get请求下 ？ 之后的参数
    HEADER = "header"  # 请求头
    COOKIE = "cookie"  # cookie
    REQUEST_BODY = "request_body"  # post请求 请求体(from json)


# 参数类型枚举
# 验证Parameter需要的枚举类
# 参数类型枚举 内容描述类型的字符串
class ParameterType(str, Enum):
    """参数支持的类型"""
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"


# ParameterType 中每个枚举与实际类型的映射字典
ParameterTypeMap = {
    ParameterType.STR: str,
    ParameterType.INT: int,
    ParameterType.FLOAT: float,
    ParameterType.BOOL: bool,
}
