from typing import Any

import dotenv
from langchain_core.messages import ToolCall, AIMessage, ToolMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


# 在链中构建携带错误信息的重试处理:
# 1 工具函数
@tool
def complex_tool(int_arg:int,float_arg:float,dict_arg:dict) -> float:
    """这是一个复杂工具,包含一个整型,一个浮点型以及一个字典参数 进行复杂运算"""
    print(int_arg,float_arg,dict_arg)
    return int_arg + float_arg

# 2 自定义异常 包含两个属性:AI消息(工具调用信息) 与 调用工具时抛出的原始异常对象
class CustomToolException(Exception):
    def __init__(self, ai_msg:AIMessage,exception:Exception) -> None:
        self.ai_msg = ai_msg
        self.exception = exception

# 3 定义工具执行者函数 在执行时需要捕获异常 包装自定义异常
n = 0
def tool_executor(ai_msg:AIMessage,config:RunnableConfig) ->Any:
    global n
    n += 1
    print(f"这是第{n}次执行工具")
    try :
        return complex_tool.invoke(ai_msg.tool_calls[0]["args"],config)
    except Exception as e :
        print(e)
        # 将原本的异常包装为自定义异常,加上AI消息
        raise CustomToolException(ai_msg,e)

# 4 提示模板 (不仅支持原始链,还要支持回退链)
prompt = ChatPromptTemplate.from_messages([
    ("system","你是一个AI助手,能够根据用户的提问回答问题,如果需要使用工具,则可以调用工具,如果有历史信息也需要参考."),
    ("human","{query}"),
    ("placeholder","{last_output}"),# 用于在回退执行时填入历史信息,可以传也可以不传
    # 在第一次执行失败之后,编辑一段消息列表
    # 包含上次的错误信息，以及新增一条人类消息告知大模型上次错误的原因，以及接下来的建议
])

# 5 定义Runnable函数组装历史消息 将异常信息 融入到后续提示词中{last_output}的消息列表内
def exception_handler(ipt:dict,config:RunnableConfig) -> dict :
    """
    该组件的输入结构:
    {
    "query":"?",
    "exception":CustomToolException()
    }
    该组件的输出要求
    {
    "query":"query?",
    "exception":CustomToolException(),
    "last_output":list[BaseMessage],
    }
    """
    # 1 先从ipt中提取exception值
    exception = ipt.get("exception")
    # 2 组装消息列表 组装过程中 要告知LLM上次执行出错 不要再犯同样的错误
    messages = [
        exception.ai_msg,# AI消息
        ToolMessage( # Tool调用消息(失败的调用结果)
            tool_call_id = exception.ai_msg.tool_calls[0]["id"],
            content = str(exception.exception),# 异常的描述信息
        ),
        #再增加一条Human消息 告知LLM不要犯同样的错误
        HumanMessage(content="最后一次工具调用引发了异常，请尝试使用更正的参数再次调用该工具，请不要重复犯错,不要忘记了dict_arg参数 "),
    ]

    ipt["last_output"] = messages
    return  ipt

# 6 创建大模型
llm = ChatOpenAI(model="gpt-3.5-turbo-16k",temperature=0).bind_tools([complex_tool])
# 7 创建 chain
chain = prompt | llm | RunnableLambda(tool_executor)
final_chain = chain.with_fallbacks(
    exception_key="exception",
    fallbacks=[RunnableLambda(exception_handler)| (lambda x:print("fix_messages:",x) or x)|chain]
)

result = final_chain.invoke({"query":"使用复杂工具,传入参数为 5 和 3.4,不要忘记了dict_arg参数 "})
print(result)

# exception_key: 当默认链在执行过程中产生了异常之后,会将异常信息以exception_key的值
#                作为key合并到初始的input输入之内({"query":xxxxx,"exception":e})
#                传给下一个备份链

# 要求 4  理解上述案例
'''
面试题
1、什么是function_call？有什么方式创建函数工具？
2、function_call里面的函数调用时AI去调用还是人类去调用的？
3、不支持Function_call的大模型如何进行函数调用？
4、如何使用function_call实现JSON输出？
5、Langchain 实现 Function_call总共分几步？
6、什么是函数调用，有什么方式创建函数工具
7、大模型在函数调用的时候，出错了怎么办？
8、什么是React智能体？
9、ReACT的主要缺陷？
10、什么是多模态，有了解过吗？
'''