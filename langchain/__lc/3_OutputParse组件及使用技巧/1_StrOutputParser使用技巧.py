from datetime import datetime
import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser # 字符串输出解析器

# output_parsers 输出解析器 将大模型生成的BaseMessage 转换成其他形式

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
# 定义字符串输出解析器 解析结果为str
str_output_parser = StrOutputParser()

# 执行大模型 AIMessage结果再传递给输出解析器  字符串输出解析器执行结果为 str
content = str_output_parser.invoke(chat_model.invoke(prompt.invoke({"query":"你好 你是谁?"})))
print(content,type(content))