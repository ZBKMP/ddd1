# 大模型 批处理
import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

'''
prompts = []

for p in prompts:
    pv = p.invoke({})
    ai_msg= chat_model.invoke(pv)
    
使用批处理替代循环代码
'''

# 加载配置文件
dotenv.load_dotenv()
# 提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system","你是OpenAI智能助手,请根据用户提问回答问题"),
    ("user","用户的提问是:{query}"),
])
# 创建大模型 会自动读取dotenv内的配置信息
chat_model = ChatOpenAI(
    model="gpt-3.5-turbo-16k",# gpt-4o-mini
)

# 创建PromptValue列表
prompt_value1 = prompt.invoke({"query":"讲一个关于程序员的冷笑话"})
prompt_value2 = prompt.invoke({"query":"讲一个关于产品经理的的打油诗"})
prompt_value3 = prompt.invoke({"query":"什么是LLM大模型"})
prompt_value_list = [prompt_value1, prompt_value2, prompt_value3]

# 使用大模型的批处理 多次生成内容
ai_messages = chat_model.batch(prompt_value_list)
print(type(ai_messages)) #List<AIMessage>
for ai_msg in ai_messages:
    #print(ai_msg)
    print(ai_msg.content)