# langchain中的内置工具
# DuckDuckGO搜索引擎工具：
# pip install -U duckduckgo-search=8.1.1
# pip install -U ddgs=9.11.1

from langchain_community.tools import DuckDuckGoSearchRun,DuckDuckGoSearchResults
from langchain_core.utils.function_calling import convert_to_openai_tool

# 创建工具对象(langchain内置工具)
search_tool = DuckDuckGoSearchRun(
# 描述原为英文 可以重新编辑该工具的描述
    description='DuckDuckGo 搜索工具的封装接口。适用于需要回答实时事件相关问题的场景。输入内容应为搜索查询语句。'
)

# 单独使用工具
result = search_tool.invoke(input="至今为止马拉松世界记录是多少?") # 将输入的内容传递给DDG需要的query参数
# result = search_tool.invoke(input={"query":"至今为止马拉松世界记录是多少?"})
print(result)

# 查看工具信息
print("工具名称:",search_tool.name)
print("工具描述:",search_tool.description)
print("工具需要的参数:",search_tool.args)
print("工具的参数规范:",search_tool.args_schema)
print("工具是否直接返回结果:",search_tool.return_direct) # False表示工具执行结果不是最终结果,需要再传给大模型

# DuckDuckGoSearchResults 类似DuckDuckGoSearchRun ,但会携带给更多信息(如结果来源的网址)