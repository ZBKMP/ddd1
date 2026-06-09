# JsonOutputParser使用技巧

import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# 要求大模型按照特定的JSON结构输出内容: 大模型在生成内容 即回答结果answer 还包含对于结果的解释explain

# 利用Pydantic的BaseModel规范输出的JSON数据结构
class ResultFormatter(BaseModel):
    # 属性的描述会作为相关信息传递给大模型,影响其内容的生成
    answer: str = Field(description="表示回答用户问题的答案")
    explain: str = Field(description="表示对于问题答案的解释")
# 创建JSONOutput输出解析器 要以一个Pydantic BaseModel类作为参数 规划输出格式
output_parser = JsonOutputParser(pydantic_object=ResultFormatter)

# 加载配置文件
dotenv.load_dotenv()
# 创建大模型 会自动读取dotenv内的配置信息
chat_model = ChatOpenAI(
    model="gpt-3.5-turbo-16k",  # gpt-4o-mini
)
# 在提示模板中在系统消息中,告知大模型将来生成内容的格式
prompt = ChatPromptTemplate.from_messages([
    ("system","你是OpenAI智能助手,请按以下格式介绍来回答问题:{format_instructions}"),
    ("user","用户的提问是:{query}"),
]).partial(format_instructions=output_parser.get_format_instructions())
# 由JsonOutputParser来负责提供关于JSON格式的描述文本

# 测试大模型生成的结果 查看是否为JSON格式(dict)  “{"key":"value"}”=》dict
result = output_parser.invoke(chat_model.invoke(prompt.invoke({"query":"请讲一个关于程序员的冷笑话"})))
print(result)
result = output_parser.invoke(chat_model.invoke(prompt.invoke({"query":"你好 你是谁?"})))
print(result)




