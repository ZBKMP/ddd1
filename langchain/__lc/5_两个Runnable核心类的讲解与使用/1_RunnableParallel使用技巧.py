import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel

# RunnableParallel 并行运行多个链----dict  对比批处理

# 定义提示模板
joke_prompt = ChatPromptTemplate.from_template("请讲一个关于{subject}的冷笑话")
poem_prompt = ChatPromptTemplate.from_template("请写一篇关于{subject}的打油诗")

# 创建大模型
dotenv.load_dotenv()
chat_model = ChatOpenAI(model='gpt-4o-mini')

# 输出解析器
parser = StrOutputParser()

# 构建两个链
joke_chain = joke_prompt | chat_model | parser
poem_chain = poem_prompt | chat_model | parser

# 使用RunnableParallel 并行执行多个链  参数为字典
#  1 steps__ 传参
# parallel = RunnableParallel(
#     steps__={
#         "joke": joke_chain,
#         "poem": poem_chain,
#     }
# )

# 2 kwargs传参
parallel = RunnableParallel(
   joke = joke_chain,
   poem = poem_chain,
)
# 执行 结果为字典
result = parallel.invoke(input={"subject":"大夫"})
print(result)