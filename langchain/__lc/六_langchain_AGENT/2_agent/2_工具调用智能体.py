# 工具调用智能体  AgentExecutor

import dotenv
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.tools import GoogleSerperRun
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


# 1 定义工具与工具列表
class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")
class DallEArgsSchema(BaseModel):
    query: str = Field(description="输入应该是生成图像的文本提示(prompt)")
# google搜索
google_serper_tool = GoogleSerperRun(
    name="google_serper_tool",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，可以调用该工具。"
        "该工具的输入是搜索查询语句。"
    ),
    api_wrapper=GoogleSerperAPIWrapper(),
    args_schema=GoogleSerperArgsSchema,
)
# 文生图片
dalle = OpenAIDALLEImageGenerationTool(
    name="openai_dalle",
    api_wrapper=DallEAPIWrapper(model="dall-e-3"),
    args_schema=DallEArgsSchema,
)
tools = [google_serper_tool, dalle]

# 2 定义工具调用agent提示词模板  可以方便的设置中文模板
# 在 create_tool_calling_agent 源码中可查看到提示模板的写法
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是由OpenAI开发的聊天机器人，善于帮助用户解决问题。"),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"), #agent_scratchpad智能体草稿
])

# 3 创建大语言模型
llm = ChatOpenAI(model="gpt-4o-mini")

# 4 创建agent 工具智能体
agent = create_tool_calling_agent(
    prompt=prompt,
    llm=llm,
    tools=tools,  # 工具列表
)
# 5 创建agent执行者
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,  # 工具列表
    verbose=True,  # 提供丰富调用信息
    handle_parsing_errors=True,
)

# 6 链执行 如果提问内容不包含工具调用 结果也不会出异常
#print(agent_executor.invoke({"input": "你好 你是谁"}))
#print(agent_executor.invoke({"input": "生成一张老爷爷爬山的图片"}))
print(agent_executor.invoke({"input": "马拉松世界记录是多少?以及为此生成一张图片"}))
