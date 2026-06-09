from langchain_community.tools.wikipedia.tool import WikipediaQueryInput, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import BaseTool

from internal.lib import add_attribute


# 将工具输入参数Schema装饰成工具的属性 以便后期加载工具时获取Schema
# 观察WikipediaQueryRun源码 可看到args_schema为WikipediaQueryInput 输入参数为query
@add_attribute(attr_name="args_schema",attr_value=WikipediaQueryInput)
def wikipedia_search(**kwargs) -> BaseTool:
    """返回维基百科搜索工具"""
    api_wrapper = WikipediaAPIWrapper()
    tool = WikipediaQueryRun(api_wrapper=api_wrapper)
    return tool


if __name__ == "__main__":
    api_wrapper = WikipediaAPIWrapper()
    tool = WikipediaQueryRun(api_wrapper=api_wrapper)
    wiki_result = tool.invoke(input={"query": "哥德巴赫猜想"})
    print(wiki_result)