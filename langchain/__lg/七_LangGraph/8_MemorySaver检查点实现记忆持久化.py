

import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver, PersistentDict
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# MemorySaver检查点实现记忆持久化

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

# 2 创建大语言模型
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 3 创建检查点/记忆点
check_pointer = MemorySaver()

# 4 基于ReACT智能体使用检查点
agent = create_react_agent(
    model=model,
    tools=tools,
    # 在ReAct智能体中设置检查点
    # 创建智能体时设置检查点,后续使用该智能体时,必须要传入检查点线程ID(标识当前的使用者,每个使用者使用不同的ID)
    # 因为检查点存储的不是整个图结构应用程序的节点状态,而存储的是特定线程的数据状态
    # (LangGraph在设计时考虑到一个应用被多个线程异步访问的情况)
    checkpointer=check_pointer,
)

# 5 测试基于检查点实现的 图记忆功能
while True:
    ipt = input("Human:")
    if ipt =='exit':
        break
    result = agent.invoke(
        input={"messages":[HumanMessage(content=ipt)]},
        # 在执行图应用时,每次都通过config传递相同的配置项 thread_id ,该配置项的值每次都一样,则能自动保存提取之前的记忆
        config=RunnableConfig(configurable={"thread_id":1})
    )
    for message in result["messages"]:
        print(message)
    print("---------------------------------------------")

