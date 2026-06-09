# ReACT智能体运行流程与实现
import dotenv
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from pydantic import BaseModel, Field
from langchain_core.tools import render_text_description_and_args
from langchain_openai import ChatOpenAI
from langchain import hub

# 创建一个带有谷歌实时搜索的ReACT架构Agent
dotenv.load_dotenv()


# 1.定义工具与工具列表
class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


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
tools = [google_serper_tool]

# 2. langchain官方针对ReACT智能体写的Prompt
template = '''Answer the following questions as best you can. You have access to the following tools:

            {tools}

            Use the following format:

            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of [{tool_names}]
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question

            Begin!

            Question: {input}
            Thought:{agent_scratchpad}'''
prompt = PromptTemplate.from_template(template)

# 3.创建大语言模型与智能体
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# agent的本质是一个单chain应用 只能执行一次 要基于agent_executor才能实现循环操作
agent = create_react_agent(
    llm=llm,
    prompt=prompt,
    tools=tools,
    tools_renderer=render_text_description_and_args,
)

# 4 创建智能体执行工具
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # 提供丰富调用信息 查看执行步骤信息
    handle_parsing_errors=True
)

print(agent_executor.invoke({"input": "马拉松的最新世界记录是多少?"}))
print("*" * 50)
print(agent_executor.invoke({"input": "你好 你是?"}))

# ReAct智能体会执行推理,推理出需要调用的工具,再进行工具调用,结果再传递给大语言模型
# ReAct智能体 执行过程中必须调用工具,所问问题找不到合适工具,也会强制去调用工具,经过多次错误重试后会停止
