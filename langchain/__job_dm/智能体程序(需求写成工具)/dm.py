import os, dotenv, uuid
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent


dotenv.load_dotenv()


# 定义工具

@tool
def get_weather(city: str) -> str:
    """查询指定城市当前的实时天气。当用户询问温度、天气状况时使用。"""
    # 模拟数据
    return f"{city}目前晴天，气温 20°C，非常适合户外活动。"


@tool
def internet_search(query: str) -> str:
    """当用户询问实时新闻、当前发生的事件或大模型知识库之外的信息时，使用此工具。"""
    return f"【搜索结果】：关于 '{query}'，哥谭日报报道称小丑最近在筹备一场大型喜剧秀。"


class ImageArgs(BaseModel):
    prompt: str = Field(description="描述图片的中文提示词，例如 '霓虹灯下的赛博朋克城市'")


@tool("generate_image", args_schema=ImageArgs)
def generate_image(prompt: str) -> str:
    """生成图片的工具。用户要求画画、出图时使用。请注意：调用前需将用户需求翻译为中文。"""
    image_id = uuid.uuid4().hex[:8]
    return f"图片生成成功！ID: {image_id}，存储路径: /images/{image_id}.png。提示词内容: {prompt}"


@tool
def joker_knowledge_base(query: str) -> str:
    """查询小丑（Joker）内部档案库的工具。当用户问及小丑的语录、哲学、独白时使用。"""
    # 这里模拟你之前的向量库检索结果
    return "档案库记录：'我曾以为我的生活是一场悲剧，现在我发现它是一场喜剧。'"


# 配置 (LLM)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 放入工具箱
tools = [get_weather, internet_search, generate_image, joker_knowledge_base]

# -编写提示模板
# 这是智能体的“思考流程说明书”
prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个名为“影子”的全能助手。
    你可以使用各种工具来回答用户。如果用户的问题需要查询，请务必使用工具。

    你的思考方式：
    1. 思考 (Thought)：分析用户想要什么。
    2. 行动 (Action)：选择合适的工具并准备参数。
    3. 观察 (Observation)：查看工具返回的信息。
    4. 最终总结：根据搜集的信息，用友好的语气回答用户。"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# (Agent)
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 测试 -
if __name__ == "__main__":
    print("--- 智能体已就绪 ---")

    # 场景 A：
    print("\n[测试任务 1: 城市服务]")
    agent_executor.invoke({"input": "哥谭市天气如何？顺便告诉我哥谭市最近的新闻", "chat_history": []})

    # 场景 B：
    print("\n[测试任务 2: 画图]")
    agent_executor.invoke({"input": "帮我画一张哥谭市雨夜的艺术图。", "chat_history": []})