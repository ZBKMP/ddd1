# 本案例应在app_handler内实现 先以单独py文件实现

import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import  StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.base import RunnableSequence
# 使用langchain的管道操作符 '|' 链接多个可运行组件(遵循了可运行协议)

#1 构建提示词
prompt = ChatPromptTemplate.from_template("用户的问题是:{query}")

#2 构建llm
dotenv.load_dotenv()
chat_model = ChatOpenAI(model="gpt-3.5-turbo-16k")

#3 创建一个输出解析器
parser = StrOutputParser()

#4 使用LCEL(langchain 表达式语言) 实现链式编程
# 每个组件的输出作为下一个组件的输入,最开始的输入传递给第一个组件,最后一个组件的输出则是整个链的输出
# 每个可运行组件(RunnableSerializable) 都重写了方法 __or__ / __ror__ 从而改写了操作符 '|'-->管道操作符
chain = prompt | chat_model | parser
print(type(chain)) # 通过管道操作符合并的结果 最终都是Runnable组件
result  = chain.invoke(input={"query":"请介绍一下什么是LLM?"})
print(result) # 最后为str输出解析器 结果为字符串


# 在 | 的左右两边 起码有一个是Runnable组件
# R|R->R   Oth|R->R   R|Oth->R

'''
面试题：
1、langchain 的6大组件是什么？
2、什么是提示词，它在与大模型交互中的作用是什么？
3、在langchain中写提示词，form_template与form_messages有什么区别，分别在什么场景下使用
4、你们项目中格式解析器都用什么？如何保证输出的一定是JSON
'''

# 要求 1  在flask的视图函数中 实现从请求中获取用户提问 编辑提示模板(使用各种拼接)
#        大模型生成内容 提取content 作为响应结果 以JSON方式响应到前端(requests测试)

"""
要求 2 
请实现一个智能家具控制机器人。该机器人必须输出json格式的控制指令(结合JsonOutputParser),
思考：在系统消息中如何编写提示词，以告知AI需要完成的任务
示例如下:
Human：请帮我打开厨房灯
Ai:{"target":"light","position":"kitchen","id":XXXXX,"url":"wwww.alltman.com"}


执行过程中 可以测试单次生成 和 批处理
"""

# 要求 3
# 将上述所有AI执行流程 换成chain 来执行



