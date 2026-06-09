# 内置工具 业务服务层
import mimetypes
import os
from dataclasses import dataclass
from typing import Any

from flask import current_app
from injector import inject
from langchain_core.utils.function_calling import tool_example_to_messages
from pydantic import BaseModel

from internal.core.tools.builtin_tools.categories import BuiltinCategoryManager
from internal.core.tools.builtin_tools.providers import BuiltinProviderManager
from internal.exception import NotFoundException


@inject
@dataclass
class BuiltinToolService():
    '''内置工具 业务服务层'''
    builtin_provider_manager: BuiltinProviderManager
    builtin_category_manager: BuiltinCategoryManager

    # 1  获取内置工具列表  包含所用提供商 以及 旗下所有工具信息
    def get_builtin_tools(self) -> list[dict[str, Any]]:
        '''获取所有内置插件(提供商,工具)列表信息'''
        # 1 获取所有的Provider对象列表
        providers = self.builtin_provider_manager.get_providers()
        # 最终响应结果数据(data)需要包装为一个字典列表
        provider_dict_list = []

        # 2 遍历所有提供商 并提取工具信息
        for provider in providers:
            # 3 获取Provider对象内的ProviderEntity供应商实体信息
            provider_entity = provider.provider_entity
            # 4 根据接口定义需求 组织响应结果字典结构 每个供应商实体转为一个dict
            provider_dict = {
                # provider_entity为Pydantic的BaseModel类型,
                # 通过model_dump转为字典,再拆包,
                # 过程中排除icon字段(接口文档中不包含该字段)
                **provider_entity.model_dump(exclude={"icon"}),
                # 增加tools字段,类型为列表 用于包含该provide下的所有工具信息
                "tools": []
            }
            # 5 遍历该提供商下的所有工具实体
            for tool_entity in provider.get_tool_entities():
                # 6 构建工具实体信息字典
                tool_dict = {
                    **tool_entity.model_dump(),
                    # inputs为工具的输入Schema 通过BuiltinProviderManager可以拿到工具函数,
                    # 但拿不到Schema,需要使用add_attribute装饰器,将其作为工具生成函数的属性(args_schema)
                    # 函数也是对象(Callable),也可以有属性
                    "inputs": []
                }
                # 7 在provider中通过tool_name获取 工具生成函数
                tool_func = provider.get_tool(tool_entity.name)
                # 8 检测工具生成函数中是否有args_schema属性,而且属性为BaseModel类型
                if (hasattr(tool_func, "args_schema")
                        and
                        issubclass(tool_func.args_schema, BaseModel)):
                    inputs = []  # 空的参数字典列表
                    # 按照接口定义的要求,从新增的args_schema属性中提取参数描述信息,
                    # args_schema为BaseModel类.
                    # model_fields:得到BaseModel类中定义的属性名与属性组成的字典,
                    # 其中: key:属性名  value:属性对象.
                    for filed_name, filed_info in tool_func.args_schema.model_fields.items():
                        inputs.append({
                            "name": filed_name,  # BaseModel的某个属性名
                            "description": filed_info.description or "",  # BaseModel的某个属性的描述
                            "required": filed_info.is_required(),  # BaseModel的某个属性是否必填
                            "type": filed_info.annotation.__name__,  # 属性的类型名称  str  int .....
                        })
                    # 9 所有参数的描述填入到tool_dict中
                    tool_dict["inputs"] = inputs
                # 10 每个工具信息填充到 provider字典中的 tools列表中
                provider_dict["tools"].append(tool_dict)
            # 11 每个provide字典加入到provider_dict_list
            provider_dict_list.append(provider_dict)
        # 12 返回最终的 提供商及工具 字典列表
        return provider_dict_list

    # 2 获取单个工具信息
    def get_provider_tool(
            self,
            provider_name: str,
            tool_name: str
    ) -> dict[str, Any]:
        """根据传递的provider_name与tool_name 获取指定工具信息"""
        # 1 获取指定的提供商信息对象
        provider = self.builtin_provider_manager.get_provider(
            provider_name=provider_name
        )
        if provider is None:
            # 找不到对应的提供商 抛出自定义异常
            raise NotFoundException(f'该提供者{provider_name}不存在')

        # 2. 获取该提供商下对应名称的工具实体信息
        tool_entity = provider.get_tool_entity(tool_name=tool_name)
        if tool_entity is None:
            # 找不到对应工具 抛出自定义异常
            raise NotFoundException(f'该工具{tool_name}不存在')

        # 3 按接口要求 组装响应信息 包含提供商实体 和 工具生成函数
        provider_entity = provider.provider_entity  # 提供商实体
        tool_func = provider.get_tool(tool_name=tool_name)

        # 组装返回字典结果
        builtin_tool = {
            "provider": {  # 提供商信息 不需要图标以及创建时间
                **provider_entity.model_dump(
                    exclude={"icon", "created_at"}
                )
            },
            **tool_entity.model_dump(),  # 工具实体拆包为字典
            # 来自提供商的创建时间 应接口要求放在最外层
            "create_at": provider_entity.created_at,
            # 工具的输入参数列表
            "inputs": []
        }
        # 4 与上一个函数相同 根据工具生成方法的属性
        #    获取其输入schema信息 组成inputs列表
        if (hasattr(tool_func, "args_schema")
                and
                issubclass(tool_func.args_schema, BaseModel)):
            inputs = []  # 空的参数字典列表
            # 按照接口定义的要求,从新增的args_schema属性中提取参数描述信息,
            # args_schema为BaseModel类.
            # model_fields:得到BaseModel类中定义的属性名与属性组成的字典,
            # 其中: key:属性名  value:属性对象.
            for filed_name, filed_info in tool_func.args_schema.model_fields.items():
                inputs.append({
                    "name": filed_name,  # BaseModel的某个属性名
                    "description": filed_info.description or "",  # BaseModel的某个属性的描述
                    "required": filed_info.is_required(),  # BaseModel的某个属性是否必填
                    "type": filed_info.annotation.__name__,  # 属性的类型名称  str  int .....
                })
            # 所有参数的描述填入到tool_dict中
            builtin_tool["inputs"] = inputs

        return builtin_tool

    # 3 根据provider_name获取对应ICON图标流信息,返回 流 与 类型str
    def get_provider_icon(
            self,
            provider_name: str
    ) -> tuple[bytes, str]:
        # 1 获取对应的Provider对象
        provider = self.builtin_provider_manager.get_provider(
            provider_name=provider_name
        )
        if provider is None:
            raise NotFoundException(f'该提供者{provider_name}不存在')

        # 2 定位该Provider的icon文件路径
        # 项目根路径 + internal/core/tools/builtin_tools/providers/provider_name/_asset/icon文件名
        # 项目根路径: current_app 当前运行的app文件
        root_path = os.path.dirname(
            os.path.dirname(current_app.root_path)
        )
        # 拼接上中间的包路径,得到provider所在路径:
        provider_path = os.path.join(
            root_path,
            "internal", "core", "tools", "builtin_tools", "providers",
            provider_name,
        )
        # 定位到该提供商图标的路径
        icon_path = os.path.join(
            provider_path,
            '_asset',
            provider.provider_entity.icon
        )
        # 检测icon路径是否存在
        if not os.path.exists(icon_path):
            raise NotFoundException(f'该工具提供者_asset下未提供图标')

        # 3 mimetypes.guess_type方法读取icon的类型,该方法返回元祖
        mimetype, _ = mimetypes.guess_type(icon_path)
        # 如果提取失败 给一个默认类型
        mimetype = mimetype or 'application/octet-stream'

        # 4 获取文件的字节流
        with open(icon_path, 'rb') as f:
            byte_data = f.read()

        # 5 返回 流 与 类型
        return byte_data, mimetype

    # 4 获取所有的内置工具分类信息 包含category name  icon
    def get_categories(self):
        # 调用 manager工具类 获取类型信息映射
        category_map = self.builtin_category_manager.get_category_map()
        return [
            {
                "category":category["entity"].category,
                "name":category["entity"].name,
                "icon":category["icon"],
            } for category in category_map.values()
        ]