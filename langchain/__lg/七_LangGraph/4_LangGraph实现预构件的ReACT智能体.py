import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent  # langgraph预构件

# LangGraph实现预构件的ReACT智能体:

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

# 2. 创建大语言模型
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 3. 使用langgraph中的预构建智能体 该智能体以图的模式实现 状态中包含消息列表 messages
agent = create_react_agent(
    model=model,
    tools=tools,
)

# 4 执行ReAct智能体
result = agent.invoke({
    "messages":[HumanMessage(content="至今为止的100米世界纪录是多少?以此为内容生成一张图片")]
})
for message in result["messages"]:
    print(message)