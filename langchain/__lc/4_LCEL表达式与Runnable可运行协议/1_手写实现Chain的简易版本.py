from typing import Any

import dotenv
from humanfriendly.terminal import output
from langchain_core.runnables import RunnableSerializable
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import  StrOutputParser
from langchain_core.prompts import ChatPromptTemplate



#1 定义提示模板
prompt = ChatPromptTemplate.from_template("用户的问题是:{query}")

#2 创建模型
dotenv.load_dotenv()
chat_model = ChatOpenAI(model="gpt-3.5-turbo-16k")

#3 定义output解析器
parser = StrOutputParser()

# 模拟LCEL链编程的效果 组装一个可运行组件列表 ,执行列表完成链应用的执行
# 模拟langchain的LCEL 能够按顺序执行item_list的每个组件
# 每个组件的输出作为下一个组件的输入,最开始的输入传递给第一个组件,最后一个组件的输出则是整个链的输出
runnable_list = [prompt,chat_model,parser]

# 类中定义一个方法 参数为langchain的组件列表,执行过程为每个元素依次调用,最后一个组件的结果为最终结果
# 提示模板 大模型 输出解析器 都属于 RunnableSerializable 类的子类(都属于可运行组件,都实现了Runnable协议),都有invoke方法
class MyChain:
    def __init__(self,chain:list[RunnableSerializable]):
        self.chain = chain

    # 执行整个链 参数即为最开始的输入，该方法的返回值即最后组件的输出结果
    def invoke(self,in_put : Any)->Any:

        out_put = None # 接受每个组件输出的结果
        for runnable in  self.chain:
            print(f"runnable: {type(runnable)} input:{in_put}")
            out_put = runnable.invoke(in_put)
            print(f"output:{out_put}   type:{type(out_put)}")
            # 每个组件的输出 就是下一个的输入
            in_put = out_put
        # 执行完最后一个组件 output就是整个链的输出
        return out_put

# 使用自定义的Chain执行工具  执行一个可运行组件列表
chain = MyChain(runnable_list)
result = chain.invoke(in_put={"query":"你好 你是谁?"}) # 调用方法的参数 为第一个组件需要的参数
print(result)

