# 在链中构建错误处理来减轻故障出现的概率
from typing import Any

import dotenv
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1 构建工具 模拟异常的产生
@tool # 没有进行参数格式规范的描述
def complex_tool(int_arg:int,float_arg:float,dict_arg:dict) -> float:
    """这是一个复杂工具,包含一个整型,一个浮点型以及一个字典参数 进行复杂运算"""
    print(int_arg,float_arg,dict_arg)
    return int_arg + float_arg

# 2 创建LLM 绑定工具
llm = ChatOpenAI(model='gpt-3.5-turbo-16k',temperature=0).bind_tools([complex_tool])


# 用以下方式构建的链 在执行过程中 大模型无法生成完整的工具调用参数,则在执行到工具调用时 必然出错
'''
# 3 构建链 得到AI消息中的tool_calls中的第一个元素,再提取其中的args字段 传递给后续要调用的工具
chain = llm | (lambda ai_msg:ai_msg.tool_calls[0]["args"]) |complex_tool

# 4 调用链 模拟异常 需要三个参数 但输入中只描述了2个参数
result = chain.invoke("使用复杂工具,传入参数为 5 和 5.6")
print(result,type(result))
'''

# 5 优化链 增加异常处理
#   构建函数(Runnable组件) 实现在调用工具函数时增加异常处理
def tool_executor(tool_args:dict,config:RunnableConfig) -> Any:
    # 函数中执行工具调用 但增加异常处理
    try:
        return complex_tool.invoke(tool_args,config)
    except Exception as e:
        print(e)
        return f'在调用工具时使用了一下参数:{tool_args} 出现错误!'

# 6 修改链 增加异常处理过程
chain  = llm | (lambda ai_msg:ai_msg.tool_calls[0]["args"]) | RunnableLambda(tool_executor)
result = chain.invoke("使用复杂工具,传入参数为 5 和 5.6")
print(result,type(result))