# 大模型 流式输出  invoke必须等到所有结果都生成才会显示, stream会跟随token的生成 随时输出
import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

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

# 使用steam方法实现流式输出    生成/迭代 BaseMessageChunk(片段)
prompt_value = prompt.invoke({"query": "介绍一下在基于LLM进行Agent开发常用框架有哪些"})
chunks = chat_model.stream(prompt_value)
for chunk in chunks:
    # print(chunk)

    # 在控制台显示流式输出文本的效果
    print(chunk.content,end="",flush=True)

# 当前流式输出仅实现与Python控制台
# flask中要实现流式输出需要专门的代码设计
