# 内置工具API接口
import io

from flask import send_file
from injector import inject
from dataclasses import dataclass

from internal.service import BuiltinToolService
from pkg.response import success_json


@inject
@dataclass
class BuiltinToolHandler(object):
    '''内置工具处理器'''
    builtin_tool_service: BuiltinToolService

    # 1 获取所有provider信息及内置工具信息
    def  get_builtin_tools(self):
        '''获取所有内置插件(提供商,工具)列表信息'''
        # 调用业务层实现数据获取 数据必须是字典列表
        builtin_providers_tools = self.builtin_tool_service.get_builtin_tools()
        return success_json(data=builtin_providers_tools)

    # 2 根据提供商名称及工具名称获取指定工具信息
    def get_provider_tool(self, provider_name: str, tool_name: str):
        '''获取某个工具的详细信息'''
        # 调用业务层实现数据获取 数据必须是字典
        builtin_tool = self.builtin_tool_service.get_provider_tool(
            provider_name=provider_name,
            tool_name=tool_name
        )
        return success_json(data=builtin_tool)

    # 3 根据提供商名称获取ICON图标流文件信息
    def get_provider_icon(self, provider_name: str):
        # 调用业务层方法 结果为字节流与文件类型
        icon, mimetype = self.builtin_tool_service.get_provider_icon(
            provider_name=provider_name,
        )

        # flask.send_file 直接响应字节流转成的文件
        return send_file(io.BytesIO(icon), mimetype=mimetype)

    # 4 获取所有提供商的分类信息
    def get_categories(self):
        # 调用业务层方法
        categories = self.builtin_tool_service.get_categories()
        # 返回字典列表 转JSON
        return success_json(data=categories)