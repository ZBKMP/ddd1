# pip install langchain-openai
import dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 基于langchain使用OpenAI大模型

# 提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system","你是OpenAI智能助手,请根据用户提问回答问题"),
    ("user","用户的提问是:{query}"),
])


# 加载配置文件
dotenv.load_dotenv()
# 基于Langchain创建大模型
chat_model = ChatOpenAI(
    model="gpt-3.5-turbo-16k",
)

# 先执行提示模板 生成PromptValue
prompt_value = prompt.invoke({"query": "你好 你是谁?"})
# 将PromptValue作为参数 传递给大模型 由大模型生成内容 返回结果必然是AIMessage
ai_message = chat_model.invoke(input=prompt_value) # 参数可以是PromptValue,str,List[BaseMessage]
print(ai_message,type(ai_message)) # AIMessage
print(ai_message.content)# AIMessage中表示大模型生成的文本内容的属性



