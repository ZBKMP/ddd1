import os.path
from typing import Any

import yaml
from injector import inject, singleton
from pydantic import BaseModel, Field

from internal.core.tools.builtin_tools.entities import ProviderEntity
from internal.core.tools.builtin_tools.entities.provider_enetity import Provider


# 工具提供商工厂类 基于BaseModel
@inject
@singleton  # 单例模式 整个项目
class BuiltinProviderManager(BaseModel):
    '''服务提供商工厂类'''

    # 工具提供商字典
    # 1 值类型先写成Any
    # provider_map: dict[str, Any] = {}
    # 2 值类型改为Provider
    provider_map: dict[str, Provider] = Field(default_factory=dict)

    def __init__(self, **kwargs) -> None:
        '''构造函数 初始化provider_map'''
        super().__init__(**kwargs)
        # 将加载工具信息的过程包装成一个内部函数
        self._get_provider_map()

    def _get_provider_map(self):
        '''读取yaml配置文件  加载工具提供商字典'''
        # 1.检测provider_tool_map是否为None 若不为None表示已经加载过了
        if self.provider_map:  # 加载一次即可
            return

        # 2.获取当前py文件所在的目录路径 获取同目录下的providers.yaml文件路径
        # 获取当前文件的绝对路径
        current_path = os.path.abspath(__file__)
        # 获取当前文件所在目录的路径 providers
        providers_path = os.path.dirname(current_path)
        # 获取providers目录中 providers.yaml的绝对路径
        providers_yaml_path = os.path.join(providers_path, 'providers.yaml')

        # 3 读取providers.yaml的数据
        # (yaml配置文件读取后的结果为字典 或者是 字典组成的列表)
        with open(providers_yaml_path, 'r', encoding='utf-8') as f:
            providers_yaml_data = yaml.safe_load(f)

        # 4 循环遍历providers.yaml中的每个配置,读取为字典,再映射到字典
        #   provider_tool_map
        #   使用enumerate函数遍历providers_yaml_data列表,同时生成索引
        for idx, provider_data in enumerate(providers_yaml_data):
            # 读取的的每个字典要包装为entities包下的ProviderEntity(BaseModel),以验证数据格式
            provider_entity = ProviderEntity(**provider_data)

            # 根据循环的数据创建每个Provider对象 加入到provider_map映射之内
            self.provider_map[provider_entity.name] = Provider(
                name=provider_entity.name,
                position=idx + 1,
                provider_entity=provider_entity,
            )  # 创建对象的过程中 先填充好基本信息 还需要继续填充旗下的工具信息

    #################### 其他功能函数 ###################################
    # 根据传递的名字来获取工具提供商
    def get_provider(self, provider_name: str) -> Provider:
        '''根据传递的名字来获取服务提供商'''
        return self.provider_map.get(provider_name)

    # 获取所有工具提供商列表
    def get_providers(self) -> list[Provider]:
        '''获取所有服务提供商列表'''
        return list(self.provider_map.values())


    # 获取所有工具提供商配置信息实体列表
    def get_provider_entities(self) -> list[ProviderEntity]:
        '''获取所有服务提供商配置实体列表'''
        return [provider.provider_entity
                for provider in self.provider_map.values()]

    # 通过 工具提供商+工具名字 获取指定工具
    def get_tool(self,provider_name: str,tool_name) -> Any:
        provider = self.get_provider(provider_name)
        if provider is None:
            return None
        return provider.get_tool(tool_name)
