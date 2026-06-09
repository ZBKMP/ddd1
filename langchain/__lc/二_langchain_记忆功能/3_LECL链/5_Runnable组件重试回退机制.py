import dotenv
from langchain_community.chat_models.baidu_qianfan_endpoint import QianfanChatEndpoint
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

# 1 Runnable组件重试机制
# 定义函数测试Runnable组件的重试效果
counter = -1 # 全局变量
def func(x):
    global counter
    print("counter:",counter)
    counter += 1
    print(x/counter)
# 包装成 RunnableLambda 测试重试机制
# stop_after_attempt 如果重试N次之后 就不再重试
runnable = RunnableLambda(func=func).with_retry(stop_after_attempt=3)
result = runnable.invoke(10)
print(result)

# 2 Runnable组件回退机制
# 当该组件在使用过程中出现异常 则可以选择回退列表中的备选方案,直到有一个方案可以解决异常则停止,
#     没有一个可解决则仍然抛出异常
dotenv.load_dotenv()
prompt = ChatPromptTemplate.from_template("{query}")
# exception_key 产生的异常也会作为一个新的输入key传递到备选的方案新组件中
chat_model = ChatOpenAI(model="gpt-3.5-turbo-18k").with_fallbacks(
    # 为当前组件提供多个回退用的备选方案
    fallbacks=[ChatOpenAI(model="gpt-3.5-turbo-20k"),QianfanChatEndpoint(model="ernie-5.0-thinking-preview",timeout=100)]
)
# 创建链
chain = prompt | chat_model |( lambda x: (print(x),x)[1] ) | StrOutputParser()
# 执行
result = chain.invoke(input={"query":"你好你是谁?"})
print(result)


'''
exception_key 产生的异常也会作为一个新的输入key传递到备选的方案新组件中
input= {
    "query":"xxxxx",
    "ex":Exception()
}
chain.with_fallbacks(fallbacks=[chainA,chainB],exception_key='ex')
'''
