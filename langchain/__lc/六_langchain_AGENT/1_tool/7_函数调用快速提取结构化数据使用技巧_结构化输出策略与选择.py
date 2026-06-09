# 函数调用快速提取结构化数据使用技巧
import dotenv
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 结构化输出策略与选择:
# 1 规范输出结构
# with_structured_output 底层会根据该类创建一个虚假函数,并强制调用该函数
# 类名为函数名 属性为函数参数 该类的首行注释说明会成为该函数的说明
# LLM会以该函数的调用结构从而生成规范化的输出
class QAExtra(BaseModel):
    """一个问答键值对工具,传递对应的假设性问题与答案"""
    question: str = Field(description="假设性问题")
    answer: str = Field(description="假设性问题的答案")

# 2 构建架构化输出LLM  LLM要支持工具调用及结构化输出
llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
# LLM绑定上结构化输出信息 即能实现结构化输出
structured_llm = llm.with_structured_output(schema=QAExtra)

# 3 提示词 其中系统消息要告知LLM该如何去使用结构化输出
prompt = ChatPromptTemplate.from_messages([
    # ("system", "请从用户传递的问题中提取假设性的问题+答案"),
    ("system", "请从以户传递的问题以及你的回答组合成问题+答案"),
    ("human", "{query}")
])

# 4 创建链 并执行 结果为QAExtra类型对象
chain = {"query": RunnablePassthrough()} | prompt | structured_llm
result = chain.invoke("请简短介绍一下你自己")
print(result,type(result))


print("*"*50)

# 5 with_structured_output的底层会优先使用函数调用,
# 如果LLM支持json模式,还可以再函数内多传递一个参数: method="json_mode",则按json格式去提取
# 同时在提示词中需要增加json描述 否则会抛异常
prompt = ChatPromptTemplate.from_messages([
    # ("system", "请从用户传递的问题中提取假设性的问题+答案"),
    ("system", "请从以户传递的问题以及你的回答组合成问题+答案,响应结果为包含question与answer两个属性的JSON格式"),
    ("human", "{query}")
])
# 6 创建模型
llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
# 7 更改调用模式为JSON结构
structured_llm = llm.with_structured_output(method="json_mode")
chain = {"query": RunnablePassthrough()} | prompt | structured_llm
result = chain.invoke("请简短介绍一下你自己")
print(result,type(result))

# 运用结构化输出,将用户的问题分解为:提问与回答
result = chain.invoke("我是小黑子 我喜欢唱跳RAP篮球")
print(result,type(result))
result = chain.invoke("你好")
print(result,type(result))
# 如果未能正常提取,尝试调整提示词,以及调低温度
# 支持JSON模式的LLM较少,而且会干扰prompt,建议使用普通函数模式

