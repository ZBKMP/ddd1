#使用chain类构件链应用

#早期chain基类(抽象类) 也属于Runnable组件 可以并入LCEL链
from langchain.chains.base import Chain

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain

#1 构建链组件 LLM prompt
dotenv.load_dotenv()
prompt = ChatPromptTemplate.from_template("请讲一个关于{subject}的冷笑话")
llm = ChatOpenAI(model="gpt-3.5-turbo-16k")

#2 使用LLMChain构建链应用  内置一个StrOutputParser
chain = LLMChain(
    prompt=prompt,
    llm=llm,
)

#3 调用该链应用
print(chain.invoke({"subject": "工程师"}))
print("*"*50)
print(chain.apply([{"subject":"程序员"}]))
print("*"*50)
print(chain.generate([{"subject":"程序员"}]))
print("*"*50)
print(chain.predict(subject="程序员"))
print("*"*50)
print(chain.run("程序员"))
print("*"*50)
#重写了__call__魔术方法 可以直接当成函数调用
print(chain("程序员"))



