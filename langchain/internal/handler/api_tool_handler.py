from dataclasses import dataclass
from uuid import UUID

from flask import request
from flask_login import login_required, current_user
from injector import inject
from internal.schema import (
    ValidateOpenApiSchemaReq,
    CreateApiToolReq, UpdateApiToolProviderReq, GetApiToolProviderResp,
)
from internal.schema.api_tool_schema import (
    GetApiToolProvidersWithPageReq,
    GetApiToolProvidersWithPageResp,
    GetApiToolResp,
)
from internal.service import ApiToolService
from pkg.paginator import PageModel
from pkg.response import validation_error_json, success_message, success_json


@inject
@dataclass
class ApiToolHandler:
    '''自定义工具API接口处理器'''
    api_tool_service: ApiToolService

    # 用于验证请求中openapi_schema参数格式是否正确
    @login_required
    def validate_openapi_schema(self):
        ''' 用于验证请求中openapi_schema参数格式是否正确 '''
        # 1 从请求中提取参数 基础验证该参数必填
        req = ValidateOpenApiSchemaReq()
        if not req.validate():
            return validation_error_json(req.errors)

        # 2 调用服务并解析传递的openapi_schema数据 验证失败会抛出异常
        openapi_schema_str = req.openapi_schema.data
        open_api_schema = self.api_tool_service.parse_openapi_schema(
            openapi_schema_str
        )

        # 3 正常执行 没有异常
        return success_message(msg="openapi_schema验证成功")

    # 创建自定义API工具接口 填充到数据库
    @login_required
    def create_api_tool_provider(self):
        # 1 提取前端参数 并进行校验
        req = CreateApiToolReq()
        if not req.validate():
            return validation_error_json(req.errors)

        # 2 执行数据库添加操作  调用业务层完成
        self.api_tool_service.create_api_tool_provider(
            req,
            account=current_user,# 增加登录验证之后 需要向业务层传递Account信息
        )

        # 3 响应结果
        return success_message("创建自定义API插件成功")

    # 根据传递的Provider_id删除对应的工具提供者+工具信息
    @login_required
    def delete_api_tool_provider(self, provider_id: UUID):
        # 调用service业务层代码 实现数据删除
        # 如果删除失败 则会抛出异常
        self.api_tool_service.delete_api_tool_provider(
            provider_id,
            account=current_user,
        )
        # 返回结果
        return success_message("删除自定义API插件成功")

    # 更新自定义API工具提供者信息
    @login_required
    def update_api_tool_provider(self, provider_id: UUID):
        """更新自定义API工具提供者信息"""
        # 1 提取前端参数 并进行校验
        req = UpdateApiToolProviderReq()
        if not req.validate():
            return validation_error_json(req.errors)
        # 2 调用业务层代码完成修改业务操作 过程出错会抛出异常
        self.api_tool_service.update_api_tool_provider(
            provider_id,
            req,
            account=current_user,
        )
        # 3 返回响应结果
        return success_message("更新自定义API插件成功")

    # 根据传递的provider_id 获取指定的API工具提供者信息
    @login_required
    def get_api_tool_provider(self, provider_id: UUID):
        # 调用service业务层代码 实现数据查询
        api_tool_provider = self.api_tool_service.get_api_tool_provider(
            provider_id,
            account=current_user,
        )

        # 对象-->dict
        # 使用Schema对象将 查询结果ApiToolProvider对象转换为dict,再返回响应结果
        resp = GetApiToolProviderResp()
        return success_json(data=resp.dump(api_tool_provider))

    # 根据传递的provider_id 与 tool_name 获取指定的API工具信息
    @login_required
    def get_api_tool(self, provider_id: UUID, tool_name: str):
        # 调用service业务层代码 实现数据查询
        # 完成授权认证模块后 增加account参数 current_user方法获取
        api_tool = self.api_tool_service.get_api_tool(
            provider_id,
            tool_name,
            account=current_user,
        )
        # 使用Schema对象将 查询结果ApiTool对象转换为dict,再返回响应结果
        resp = GetApiToolResp()
        return success_json(resp.dump(api_tool))

    #  自定义API工具及提供者信息数据分页查询
    @login_required
    def get_api_tools_providers_with_page(self):
        # 从请求提取数据 该视图函数会以GET配置路由,要将url中的query字符串传入
        # FlaskForm默认只能接收form表单/JSON数据 (POST)
        req = GetApiToolProvidersWithPageReq(request.args)  # 支持get模式下 ?后的参数
        if not req.validate():
            return validation_error_json(req.errors)

        # 调用业务层实现分页查询
        api_too_providers, paginator = self.api_tool_service.get_api_tools_providers_with_page(
            req,
            account=current_user,
        )

        # 将上述两个数据合并成一个对象 并将其中的ApiToolProvider list 转为字典
        resp = GetApiToolProvidersWithPageResp(many=True)  # 可以处理列表

        page_model = PageModel(
            list=resp.dump(api_too_providers),  # 响应结果 list[ApiToolProvider] --> list[字典]
            paginator=paginator,  # Paginator中仅包含4个int属性 是可以直接转换为字典的
        )

        return success_json(data=page_model)
