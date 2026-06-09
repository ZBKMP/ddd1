import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from injector import inject
from langchain_core.tools import BaseTool
from sqlalchemy import desc

from internal.core.tools.api_tools.entities import OpenAPISchema
from internal.exception import (
    ValidationException,
    NotFoundException,
)
from internal.model import ApiToolProvider, ApiTool, Account
from internal.schema import (
    CreateApiToolReq,
    UpdateApiToolProviderReq,
)
from pkg.paginator import Paginator
from .base_service import BaseService
from pkg.sqlalchemy import SQLAlchemy
from internal.schema import GetApiToolProvidersWithPageReq
from ..core.tools.api_tools.providers import ApiProviderManager


@inject
@dataclass
# 编写了BaseService之后,继承于该类
class ApiToolService(BaseService):
    # 依赖注入
    db: SQLAlchemy

    # 类方法 解析openapi_schema字符串格式 如出错则抛出异常
    # 正确则返回OpenAPISchema对象(先返回Any)
    @classmethod
    def parse_openapi_schema(
            cls,
            openapi_schema_str: str
    ) -> Any:
        # 1 先判断传入参数是否为JSON
        try:
            data = json.loads(openapi_schema_str.strip())
            if not isinstance(data, dict):
                # 转不了dict 则必然不是JSON格式
                raise  # 抛出异常
        except Exception as e:
            raise ValidationException(
                "传递数据必须符合OPENAPI规范的JSON字符串"
            )

        # 2 再借助OpenAPISchema(BaseModel) 来验证openapi_schema数据格式是否正确
        #   并返回解析结果
        return OpenAPISchema(**data)

    # 根据传递的请求创建自定义API工具
    def create_api_tool_provider(
            self,
            req: CreateApiToolReq,
            account: Account, # 登录验证实现之后 需要关联当前账号
    ) -> None:
        """根据传递的请求创建自定义API工具"""
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个 账号ID account_id
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.使用parse_openapi_schema 检验并提取openapi_schema对应的数据
        openapi_schema = self.parse_openapi_schema(
            req.openapi_schema.data
        )

        # 2.查询当前登录的账号是否已经创建了同名的工具提供者，如果是则抛出错误
        api_tool_provider = self.db.session.query(
            ApiToolProvider
        ).filter_by(
            account_id=account_id,
            name=req.name.data,
        ).one_or_none()
        # 有则抛异常
        if api_tool_provider:
            raise ValidationException(
                f"该工具提供者名字{req.name.data}已存在"
            )

        # 基本的增删改查 可以写在Service父类中
        # 3.首先创建工具提供者，并获取工具提供者的id信息，然后在创建工具信息
        api_tool_provider = self.create(
            ApiToolProvider,
            account_id=account_id,
            name=req.name.data,
            icon=req.icon.data,
            description=openapi_schema.description,  # 描述信息
            openapi_schema=req.openapi_schema.data,  # json_str
            headers=req.headers.data
        )

        # 4.创建ApiTool并关联ApiToolProvider 每个openapi_schema.paths(dict) 有多个path
        for path, path_item in openapi_schema.paths.items():
            # 每个path 可能有 post 或 get 两个访问方式 每个访问方式就是一个工具
            for method, method_item in path_item.items():
                api_tool = self.create(
                    ApiTool,
                    account_id=account_id,
                    provider_id=api_tool_provider.id,
                    name=method_item.get("operationId"),  # 工具名称
                    description=method_item.get("description"),
                    url=f'{openapi_schema.server}{path}',  # 该工具的完整访问地址
                    method=method,
                    parameters=method_item.get("parameters", []),  # 参数列表
                )

    # 根据传递的Provider_id删除对应的工具提供者+工具信息
    def delete_api_tool_provider(
            self,
            provider_id: UUID,
            account: Account,
    ):
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个account_id
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.先查找数据，检测下provider_id对应的数据是否存在，权限是否正确
        api_tool_provider = self.get(ApiToolProvider, provider_id)

        # 账号错误 或 工具提供者不存在 抛出异常
        if (api_tool_provider is None
                or
                str(api_tool_provider.account_id) != account_id):
            raise NotFoundException("该工具提供者不存在")

        # 2.开启数据库的自动提交
        with self.db.auto_commit():
            # 3.先删除提供者对应的工具信息
            self.db.session.query(ApiTool).filter(
                ApiTool.provider_id == provider_id,
                ApiTool.account_id == account_id,
            ).delete()

            # 4.再删除服务提供者
            self.db.session.delete(api_tool_provider)

    # 根据provide_id以及请求参数 更新自定义API工具提供者信息
    def update_api_tool_provider(
            self,
            provider_id: UUID,
            req: UpdateApiToolProviderReq,
            account: Account,
    ):
        """根据传递的provider_id+req更新对应的API工具提供者信息"""
        # todo:等待授权认证模块完成进行切换调整 虚拟一个account_id
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.根据传递的provider_id查找API工具提供者信息并校验
        api_tool_provider = self.get(ApiToolProvider, provider_id)

        # ApiToolProvider不存在 或者 账号ID错误 则抛出异常
        if (api_tool_provider is None
                or
                str(api_tool_provider.account_id) != account_id):
            raise ValidationException("该工具提供者不存在")

        # 2.校验openapi_schema数据
        openapi_schema = self.parse_openapi_schema(
            req.openapi_schema.data
        )

        # 3.检测当前账号是否已经创建了与请求参数同名的工具提供者，如果是则抛出错误
        #  以账号id 提供者名称 提供者ID(不相等)为条件查询
        check_api_tool_provider = self.db.session.query(
            ApiToolProvider
        ).filter(
            ApiToolProvider.account_id == account_id,
            ApiToolProvider.name == req.name.data,
            ApiToolProvider.id != api_tool_provider.id,
        ).one_or_none()  # 结果必为一条或None 否则抛异常
        if check_api_tool_provider:
            raise ValidationException(
                f"该工具提供者名字{req.name.data}已存在"
            )

        # 4.开启数据库的自动提交
        with self.db.auto_commit():
            # 5.先删除该工具提供者下的所有工具
            self.db.session.query(ApiTool).filter(
                ApiTool.provider_id == api_tool_provider.id,
                ApiTool.account_id == account_id,
            ).delete()

        # 6 修改工具提供者信息
        self.update(api_tool_provider,
                    name=req.name.data,
                    icon=req.icon.data,
                    headers=req.headers.data,
                    description=openapi_schema.description,
                    openapi_schema=req.openapi_schema.data,
                    )

        # 7.再根据传入的openapi_schema重新创建工具 (和之前create过程中的步骤一致)
        # 继承与BaseService之后 不需要之前删除的自动提交上下文 代码前移
        for path, path_item in openapi_schema.paths.items():
            for method, method_item in path_item.items():
                api_tool = self.create(
                    ApiTool,
                    account_id=account_id,
                    provider_id=api_tool_provider.id,
                    name=method_item.get("operationId"),
                    description=method_item.get("description"),
                    url=f"{openapi_schema.server}{path}",
                    method=method,
                    parameters=method_item.get("parameters", []),
                )

    # 根据传递的provider_id 获取指定的API工具提供者信息
    def get_api_tool_provider(
            self,
            provider_id: UUID,
            account: Account,
    ):
        """根据传递的provider_id获取API工具提供者信息"""
        # todo:等待授权认证模块完成进行切换调整 先使用虚拟的account_id
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.根据provider_id 查询数据库获取对应的数据
        api_tool_provider = self.get(ApiToolProvider, provider_id)

        # 2.检验数据是否为空，并且判断该数据是否属于当前账号
        if (api_tool_provider is None
                or
                str(api_tool_provider.account_id) != account_id):
            raise NotFoundException("该工具提供者不存在")

        # 3 返回提供者对象
        return api_tool_provider

    # 根据传递的provider_id 与 tool_name 获取指定的API工具信息
    def get_api_tool(
            self,
            provider_id: str,
            tool_name: str,
            account: Account,
    ) -> ApiTool:
        """根据传递的provider_id+tool_name获取对应工具的参数详情信息"""
        # todo:等待授权认证模块完成进行切换调整 先使用虚拟的account_id
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # provide_id 以及 tool_name作为条件
        api_tool = self.db.session.query(ApiTool).filter_by(
            provider_id=provider_id,
            name=tool_name,
        ).one_or_none()
        #  检测用户账号
        if (api_tool is None
                or
                str(api_tool.account_id) != account_id):
            raise NotFoundException("该工具不存在")
        # 返回查询结果
        return api_tool

    #  自定义API工具及提供者信息数据分页查询  结果包含数据列表与分页数据 可以组合成元组
    def get_api_tools_providers_with_page(
            self,
            req: GetApiToolProvidersWithPageReq,
            account: Account,
    ) -> tuple[list[Any], Paginator]:
        # todo:等待授权认证模块完成进行切换调整 先虚拟一个account_id
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.构建分页查询器 Paginator (分页查询的列表 分页相关数据)
        paginator = Paginator(db=self.db, req=req)

        # 2.构建筛选器 增加account_id查询条件
        filters = [ApiToolProvider.account_id == account_id]  # 以当前用户的账号为条件是必须得
        # 如果由传search_word 以ApiToolProvider.name做模糊查询
        if req.search_word.data:
            # 模糊查询
            filters.append(ApiToolProvider.name.like(f"%{req.search_word.data}%"))
        # 创建查询对象
        select = self.db.session.query(ApiToolProvider).filter(*filters).order_by(desc("created_at"))
        # 执行分页查询
        api_tool_providers = paginator.paginate(select=select)

        # 3 返回查询列表结果 以及 分页数据
        return api_tool_providers, paginator

    ################################################################################

    # 编写方法:测试ApiProviderManager
    api_provider_manager: ApiProviderManager

    def get_api_base_tool(
            self,
            provider_id: str,  # 提供者id
            tool_name: str,  # 工具名称
    ) -> BaseTool:

        # 1 数据库查询 找到对应工具
        api_tool = self.get_api_tool(provider_id, tool_name)
        # 获取tool对应的Provider
        api_tool_provider = api_tool.provider

        # 导入ToolEntity
        from internal.core.tools.api_tools.entities import ToolEntity
        # 实例化ToolEntity,并以数据库查询结果填充属性值
        # 再使用api_provider_manager 得到BaseTool工具对象
        tool = self.api_provider_manager.get_tool(ToolEntity(
            id=provider_id,
            name=tool_name,
            url=api_tool.url,
            method=api_tool.method,
            description=api_tool.description,
            headers=api_tool_provider.headers,
            parameters=api_tool.parameters,
        ))
        return tool
