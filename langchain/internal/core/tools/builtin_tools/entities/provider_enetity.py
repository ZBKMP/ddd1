import os
from typing import Any

import yaml
from pydantic import BaseModel, Field
from internal.lib import dynamic_import

from .tool_entity import ToolEntity


class ProviderEntity(BaseModel):
    """服务提供商实体类，映射的数据是providers.yaml
                          里的每条记录 用于验证数据格式"""
    name: str  # 名字
    label: str  # 标签、展示给前端显示的
    description: str  # 描述
    icon: str  # 图标地址
    background: str  # 图标的颜色
    category: str  # 分类信息
    created_at: int = 0  # 提供商/工具创建时间戳


class Provider(BaseModel):
    """工具提供商类 包含 所有工具、描述、图标等多个信息"""
    # 1 必填属性
    name: str  # 工具提供商的名字
    position: int  # 工具提供商的顺序
    provider_entity: ProviderEntity  # 工具提供商实体

    # 2 该提供商旗下 所有工具信息映射字典
    # 工具实体(yaml配置信息)映射表
    tool_entity_map: dict[str, ToolEntity] = Field(default_factory=dict)
    # 工具函数(生成工具实例的函数)映射表
    tool_func_map: dict[str, Any] = Field(default_factory=dict)

    # 3 BaseModel的Config配置 保护命名空间
    class Config:
        protected_namespaces = ()

    # 4 初始化函数
    def __init__(self, **kwargs):
        """构造函数，完成对应服务提供商的初始化"""
        super().__init__(**kwargs)
        # 填充该提供商下所有工具信息映射字典 过程封装在函数中实现
        self._provider_init()

    # 5 填充该提供商下所有工具信息映射字典
    def _provider_init(self):
        """工具提供商初始化函数 填充tool_entity_map与tool_func_map
                                           获取该提供商下的工具信息"""
        # 1.获取当前类的路径，计算得到对self.name应服务提供商目录的地址路径
        # 当前文件路径
        current_path = os.path.abspath(__file__)
        # 当前目录路经
        entities_path = os.path.dirname(current_path)
        # 从entities_path所在包builtin_tools路径,定位到providers子包路径,
        builtin_tools_path = os.path.dirname(entities_path)
        # 再定位到name指向的服务提供商名字的子包路径
        provider_path = os.path.join(
            builtin_tools_path,
            "providers",
            self.name,
        )

        # 2.读取工具提供商子包目录下的positions.yaml数据工具排序位置配置信息,以获取旗下工具名称列表
        positions_yaml_path = os.path.join(
            provider_path,
            "positions.yaml",
        )
        with open(positions_yaml_path, "r", encoding="utf-8") as f:
            # 每个工具位置为 -开头 多个字符串组成列表
            positions_yaml_data = yaml.safe_load(f)

        # 3.循环读取工具排序位置配置信息,获取工具提供商的旗下的工具名称
        #   以每个工具名称为标记,读取工具信息,组装成工具实体并用动态导入获取工具函数,
        #   分别填充两个工具字典
        for tool_name in positions_yaml_data:
            # 4.获取工具对应的的yaml配置数据 如google_serper.yaml
            tool_yaml_path = os.path.join(
                provider_path,
                f'{tool_name}.yaml',
            )
            with open(tool_yaml_path, "r", encoding="utf-8") as f:
                tool_yaml_data = yaml.safe_load(f)

            # 5.将工具配置信息生成工具实体,并填充到tool_entity_map中
            self.tool_entity_map[tool_name] = ToolEntity(**tool_yaml_data)

            # 6.动态导入对应的工具并填充到tool_func_map中,注意导入的只是工具生成函数,
            #   后续获取后调用时要加(),已得到工具对象.
            # 借助internal.lib.dynamic_import 以python动态导入实现
            self.tool_func_map[tool_name] = dynamic_import(
                # 需要导入内容的模块
                module_name=f"internal.core.tools.builtin_tools.providers.{self.name}",
                # 需要导入的内容 (可以生成工具的函数)
                symbol_name=tool_name,
            )

    #################################################################################################
    # 其他辅助功能:
    # 根据工具的名字，来获取到该服务提供商下的指定工具生成方法
    def get_tool(self, tool_name: str) -> Any:
        """根据工具的名字，来获取到该服务提供商下的指定工具生成方法"""
        return self.tool_func_map.get(tool_name)

    # 根据工具的名字，来获取到该服务提供商下的指定工具的实体信息
    def get_tool_entity(self, tool_name: str) -> ToolEntity:
        """根据工具的名字，来获取到该服务提供商下的指定工具的实体信息"""
        return self.tool_entity_map.get(tool_name)

    # 获取该服务提供商下的所有工具实体/信息列表
    def get_tool_entities(self) -> list[ToolEntity]:
        """获取该服务提供商下的所有工具实体/信息列表"""
        return list(self.tool_entity_map.values())
