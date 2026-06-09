import os
from typing import Any

import yaml
from injector import inject, singleton
from pydantic import BaseModel, Field
from internal.core.tools.builtin_tools.entities import CategoryEntity
from internal.exception import NotFoundException


@inject
@singleton
class BuiltinCategoryManager(BaseModel):
    """内置的工具分类管理器"""
    # 读取所有分类信息 并存储于字典 便于后期读取数据
    category_map: dict[str, Any] = Field(default_factory=dict)

    # 初始化函数
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._get_category_map()

    # 读取类型配置信息文件 填充到category_map
    def _get_category_map(self):
        # 1.检测数据是否已经处理 其中已有数据则跳过
        if self.category_map:
            return

        # 2.获取categories.yaml数据路径并加载
        # 获取当前文件绝对路径
        current_path = os.path.abspath(__file__)
        # 获取文件当前目录  categories
        categories_path = os.path.dirname(current_path)
        # 获取categories.yaml的路径
        categories_yaml_path = os.path.join(
            categories_path,
            "categories.yaml",
        )
        # 加载yaml文件内容 字典列表
        with open(categories_yaml_path, "r", encoding="utf-8") as f:
            categories_yaml_data = yaml.safe_load(f)

        # 3 循环遍历字典列表 每个配置都生成一个Category实体
        for category_dict in categories_yaml_data:
            # 4  依据字典创建实体类对象
            category_entity = CategoryEntity(**category_dict)

            # 5 获取每个分类下的icon路径 检测icon是否存在
            icon_path = os.path.join(
                categories_path,
                "icons",
                category_entity.icon,
            )
            if not os.path.exists(icon_path):
                raise NotFoundException(
                    f"该分类{category_entity.category}的icon未提供"
                )

            # 6.读取对应的icon文件内容  svg文件内容本质为文本,可以用文字去表示
            with open(icon_path, "r", encoding="utf-8") as f:
                icon = f.read()

            # 7.将数据映射到字典中
            #   key为category的name,value为CategoryEntity对象与文件内容
            #     svg文件内容本质为文本,可以用字符串去表示
            self.category_map[category_entity.category] = {
                "entity": category_entity,
                "icon": icon,
            }


    # 获取分类映射信息
    def get_category_map(self) -> dict[str, Any]:
        """获取分类映射信息"""
        return self.category_map
