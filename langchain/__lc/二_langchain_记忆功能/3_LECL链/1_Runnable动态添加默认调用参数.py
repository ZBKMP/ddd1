# Runnable组件 bind函数 动态添加默认调用参数
import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()
# 1 构建提示词
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个OpenAI机器人,请根据用户的提问回答问题:"),
    ("human", "{query}")
])

# 2 创建大模型 设置其他参数
# temperature  温度 可以控制大模型在生成内容时的创造能力
# openAI 模型调用时的参数:https://platform.openai.com/docs/api-reference/chat/create
# 其中model_kwargs表示各种大模型自己独有的参数属性,使用bind函数来设置这些参数
chat_model = ChatOpenAI(
    model='gpt-4o-mini',
    #temperature=1.0,
)
# 使用 bind设置stop参数 只能在invoke执行之前设置
chat_model = chat_model.bind(temperature=0.0,stop=".")
chain = prompt | chat_model | StrOutputParser()


# 测试stop参数的效果
result = chain.invoke({"query":"请介绍一下什么是LLM"})
print(result)
