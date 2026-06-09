import importlib
from datetime import datetime
from hashlib import sha3_256
from typing import Any


# 动态导入特定模块下的特定功能  1模块名(包名)  2导出内容
def dynamic_import(module_name:str,symbol_name:str)->Any:
    # 定位到需要的模块
    module = importlib.import_module(module_name)
    # 以属性的模式看待模块内的内容(类 变量 方法)
    return getattr(module,symbol_name)


# 装饰器 用于将工具输入规范Schema 转换为工具函数的属性
def add_attribute(attr_name:str,attr_value:Any):
    """装饰器函数，为特定的函数添加相应的属性，
                 第一个参数为属性名字，第二个参数为属性值"""
    def decorator(func):
        setattr(func,attr_name,attr_value)
        return func

    return decorator


# 计算文本内容的HASH值
def generate_text_hash(text: str) -> str:
    """根据传递的文本计算对应的哈希值"""
    # 1.将需要计算哈希值的内容加上None这个字符串，
    #   避免传递了空字符串导致计算出错
    text = str(text) + "None"
    # 2.使用sha3_256将数据转换成哈希值后返回
    return sha3_256(text.encode()).hexdigest()



# 将传入的datetime时间转换成时间戳
def datetime_to_timestamp(dt: datetime) -> int:
    """将传入的datetime时间转换成时间戳，如果数据不存在则返回0"""
    if dt is None:
        return 0
    return int(dt.timestamp())