from dataclasses import dataclass
from typing import Callable, Type, Optional

import requests
from injector import inject
from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field, create_model

from internal.core.tools.api_tools.entities import ToolEntity, ParameterIn, ParameterTypeMap


@inject
@dataclass
class ApiProviderManager(BaseModel):
    ''' API工具管理器 能根据传递的工具配置信息 生成Langchain工具 BaseTool'''

    def get_tool(
            self,
            tool_entity: ToolEntity  # 数据来源于数据库
    ) -> BaseTool:
        """根据传递的ToolEntity配置获取自定义API工具"""
        # 使用 StructuredTool.from_function 生成BaseTool
        return StructuredTool.from_function(
            # * 该工具需要的函数
            func=self._create_tool_func_from_tool_entity(tool_entity),
            # 工具名称
            name=f'{tool_entity.id}_{tool_entity.name}',
            # 描述
            description=tool_entity.description,
            # * 工具参数规范
            args_schema=self._create_model_from_parameters(tool_entity.parameters),
        )

    # 根据ToolEntity创建工具需要的函数
    @classmethod
    def _create_tool_func_from_tool_entity(
            cls ,
            tool_entity: ToolEntity
    ) -> Callable:
        # 创建函数 函数过程为读取ToolEntity内的信息 实现一个requests的HTPP访问
        # my_tool.invoke({"q":"xxxx","doctype":"xxxx","other":"xxxx"})
        def tool_func(**kwargs) -> str:
            # 1.定义字典,存储以path/query/header/cookie/request_body
            #   方式传递到远程服务的参数值,
            #   向API接口发起请求时 可能使用上述任意一种形式去传递参数
            parameters = {
                ParameterIn.PATH: {}, #所有路径参数存储于这个字典
                ParameterIn.HEADER: {},  # headers
                ParameterIn.QUERY: {},  # query  ?
                ParameterIn.COOKIE: {},  # cookie
                ParameterIn.REQUEST_BODY: {}  # request_body
            }

            # 2.将 tool_entity.parameters中的参数规范字典信息List[dict],
            #   转换为字典结构{参数名:参数信息dict}
            #   以便用于判断调用函数时传递的参数是否都是合法参数.
            #   每个参数信息dict包含: name,in,description,required,type
            parameter_map= {
                parameter_dict.get("name"):parameter_dict
                for parameter_dict in tool_entity.parameters
            }

            #  3.循环遍历调用该工具函数时传递的实际参数kwargs并校验
            for key, value in kwargs.items():
                # 4.如果调用该工具时传递的某个参数 不在parameter_map内
                #   则抛弃该参数.因为大模型在生成函数调用信息时,有可能产生多余的参数.
                parameter_dict = parameter_map.get(key)
                # 不再参数规范定义的范围之内的参数则跳过
                if parameter_dict is None:
                    continue

                # 5.根据每个参数字典的in字段,将每个kwargs中的参数
                #   存储到合适的位置上，默认在query ? 上
                #  每组位置也是字典 参数名为key 参数值为value
                parameters[
                    parameter_dict.get("in",ParameterIn.QUERY)
                ][key] = value
            # 上述步骤实现了 将**kwargs 填充到了parameters,用于作为发起requests请求时传递的参数

            # 6.构建request请求并返回采集的内容
            #   将tool_entity.headers中的参数信息List[dict]转换为字典结构:
            #   {参数名:参数信息dict.get[value]}
            #   作为发起request请求时传递的headers数据
            header_map = {
                header.get("key"):header.get("value")
                for header in tool_entity.headers
            }

            # 发起requests HTTP访问 将参数填入到正确的位置 以及传递headers
            return requests.request(
                # 请求提交的方式
                method=tool_entity.method,
                # 假设有路径参数 路径的写法: http:127.0.0.1:5000/some_path/{arg1}/other_path/{arg2}
                url = tool_entity.url.format(**parameters[ParameterIn.PATH]), # URL 可能包含路径参数
                # 如果有 ？ 之后的参数 GET
                params= parameters[ParameterIn.QUERY],
                # POST BODY JSON
                json = parameters[ParameterIn.REQUEST_BODY],
                # headers的内容 可能来源于parameters 也可能来源于 header_map
                headers={
                    **header_map,
                    **parameters[ParameterIn.HEADER],
                },
                # 编辑cookie参数
                cookies=parameters[ParameterIn.COOKIE],
            ).text # 只需要去requests响应结果中的文本内容

        # 返回定义的函数
        return tool_func

    # 根据ToolEntity创建工具需要的参数规范BaseModel类
    @classmethod
    def _create_model_from_parameters(
            cls,
            parameters: list[dict]
    ) -> Type[BaseModel]:
        """根据传递的parameters参数创建BaseModel子类"""
        fields = {}  # 要生成的BaseModel类的属性字典
        for parameter in parameters:
            # 通过ToolEntity中的parameters中的每个parameter 生成对应的BaseModel 的 field
            # 属性名
            filed_name = parameter.get("name")
            # 属性类型
            filed_type = ParameterTypeMap.get(
                parameter.get("type",str),
            )
            # 参数是否必填
            filed_required = parameter.get("required",True)
            # 参数描述
            field_description = parameter.get("description","")
            # 把每个属性信息加入到fields字典中
            fields[filed_name] = (
                # 参数必填则直接使用该类型 否则包装为允许None
                filed_type if filed_required else Optional[filed_type],
                # 创建Filed对象
                Field(description=field_description),
            )

        # pydantic提供create_model函数以创建BaseModel子类(类,非对象)
        # 参数: 类名 类中的属性
        return create_model('DynamicModel', **fields)