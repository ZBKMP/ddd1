from operator import itemgetter

import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough


# 结合RunnableParallel模拟在链中使用RAG检索

# 模拟RAG检索 编写一个从知识库检索出知识内容的函数
# 往往以用户的原始提问去知识库检索出文档
def retriever(query: str) -> str:
    print("通过用户的提问 从知识库检索文档")
    return "我叫小黑子 是一名牛B的AI开发工程师"  # 模拟这是从知识库检索出的知识信息


query = "你好 你是谁?"

# 在提示模板中 要能包含从知识库检索出的文档内容 合并传递给大模型
# context 上下文
prompt = ChatPromptTemplate.from_template("""
   你是一个AI助手机器人,请根据用户的问题进行回答,如果不知道怎么回答可以用以下的上下文内容做参考:
   <context>
   {context}
   </context>
   回答问题尽量简洁明了.
    
   用户的问题是:{query} 
""")

# 创建大模型
dotenv.load_dotenv()
chat_model = ChatOpenAI(model='gpt-4o-mini')

# 1 编辑链 将query传递给retriever,同时还要将query传递给prompt,retriever的执行结果也要传递给prompt
'''
chain = prompt | chat_model | StrOutputParser()
result = chain.invoke(
    input={
        "context": retriever(query),
        "query": query
    }
)
print(result)
'''
# 同一个输入数据 在链中被传递多次 维护麻烦 使用RunnableParallel优化上述代码

# 2 使用RunnableParallel优化链 将一个输入的query 转换成 context+query 再传给prompt
# RunnableParallel在执行时会执行每个key对应的函数 以得到结果

'''
runnable_parallel = RunnableParallel(
    steps__={
        "context": lambda x:retriever(x["query"]),
        "query": lambda x:x["query"], # RunnableParallel中使用lambda表达式定义函数,参数就是整个链的输入
    }
)
chain = runnable_parallel | prompt | chat_model | StrOutputParser()

result = chain.invoke(
    input={
        "query": query
    }
)
print(result)
'''

# 3 RunnableParallel + RunnablePassthrough优化链的执行
#  用法1 : RunnablePassthrough():直接获取chain中 input输入的参数
'''
runnable_parallel = RunnableParallel(
    steps__={
        "context": retriever, # 等同于 lambda x:retriever(x)
        "query": RunnablePassthrough() # 直接获取str类型的input
    }
)
chain = runnable_parallel | prompt | chat_model | StrOutputParser()
# 使用了RunnablePassthrough()之后 执行时可以仅传递query字符串
result = chain.invoke(
    input=query
)
print(result)
'''

# 4 RunnableParallel的本质就是一个字典,直接使用字典替代RunnableParallel对象
# 管道操作符 会将字典自动包装为RunnableParallel
'''
chain = {
            "context": lambda x: retriever(x["query"]),
            "query": itemgetter("query")  # 等价为 lambda x: x["query"],
        } | prompt | chat_model | StrOutputParser()
result = chain.invoke(
    input={
        "query": query
    }
)
print(result)
'''

# 5 用法2 : RunnablePassthrough.assign:
#  得到一个可运行组件,在原有的输入字典中增加其他key,以满足Prompt的需要
runnable_passthrough = RunnablePassthrough.assign(
    # 只需要包含新增的key lambda表达式参数可以获取整个链的输入
    context = lambda x : retriever(x["query"]),
)
chain = runnable_passthrough | prompt | chat_model | StrOutputParser()
result = chain.invoke(
    input={
        "query": query
    }
)
print(result)

# query:  物理问题:  什么是黑洞
#         化学问题:  水的化学分子式是什么
#         历史问题:  .........

# 要求 1: 模拟真实RAG检索,重新编写retriever函数,判断用户输入中是否包含某个关键词(历史 人文 物理 化学 地理.....)
# 如果有则找到以关键词命名的文档文件(历史.txt,人文.txt,物理.txt...)读取文档内容作为检索结果

# 要求 2 : 还可以扩展为MySQL数据库查询,以知识库表中的 知识科目(subject)列为搜索条件,以关键词进行查询
# 或者是以知识内容列 进行模糊查询，内容包含关键词，注意多条结果要合并为一个文本
