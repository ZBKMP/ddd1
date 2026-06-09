# current_time 获取当前时间的工具
from datetime import datetime
from typing import Any
from langchain_core.tools import BaseTool

# 获取当前时间的自定义工具 继承自BaseTool
class CurrentTimeTool(BaseTool):
    '''一个获取当前时间的工具'''
    name:str = 'current_time'
    description:str = '一个获取当前时间的工具'

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        '''获取当前系统的时间 并进行格式化后返回'''
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')

# 获取工具对象的方法
def current_time(**kwargs) -> BaseTool:
    """返回获取当前时间的Langchain工具"""
    return CurrentTimeTool()