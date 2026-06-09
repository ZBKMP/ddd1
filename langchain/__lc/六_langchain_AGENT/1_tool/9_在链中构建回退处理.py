# 在链中构建回退fallback处理:
from typing import Any

import dotenv
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1 构建工具 模拟异常产生
@tool
def complex_tool(int_arg:int,float_arg:float,dict_arg:dict) -> float:
    """这是一个复杂工具,包含一个整型,一个浮点型以及一个字典参数 进行复杂运算"""
    print(int_arg,float_arg,dict_arg)
    return int_arg + float_arg

# 2 构建大模型
llm = ChatOpenAI(model="gpt-3.5-turbo-16k").bind_tools([complex_tool])
# 3 构建一个用于回退使用的更好的大模型
llm_better = ChatOpenAI(model="gpt-4o").bind_tools([complex_tool])

# 4 修改链 增加回退处理 出现异常会再调佣其他链
chain = llm | (lambda ai_msg:ai_msg.tool_calls[0]["args"]) | complex_tool
better_chain = llm_better | (lambda ai_msg:ai_msg.tool_calls[0]["args"]) | complex_tool
final_chain = chain.with_fallbacks(
    fallbacks=[better_chain],
)
# print(final_chain.invoke("使用复杂工具,传入参数为 5 和 3.4"))
print(chain.invoke("使用复杂工具,传入参数为 3.5 和 4 ,不要忘记了dict_arg参数 "))

# 但仍不稳定 很有可能还是会出错 无法生成第三个参数  如果是字符串参数 会自动生成

