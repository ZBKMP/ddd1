# JSON Agent
import dotenv
from langchain import hub
from langchain.agents import create_xml_agent, AgentExecutor, create_json_chat_agent
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

# 2.定义工具调用agent提示词模板  关键信息基于JSON格式编写 模版内容来源于langsmith的hub
# https://smith.langchain.com/hub/hwchase17/react-chat-json?organizationId=bcb6432e-aa36-46ed-ade0-21a4f3fcf12d&tab=0
prompt = hub.pull("hwchase17/react-chat-json")
print(prompt.messages)

# XMLAgent
# https://smith.langchain.com/hub/hwchase17/xml-agent-convo?organizationId=bcb6432e-aa36-46ed-ade0-21a4f3fcf12d
# prompt = hub.pull("hwchase17/xml-agent-convo")
# create_xml_agent

# 3.创建大语言模型
llm = ChatOpenAI(model="gpt-4o-mini")

# 4.创建agent与agent执行者
agent = create_json_chat_agent(
    prompt=prompt,
    llm=llm,
    tools=tools,
)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
)

# 5 执行链 调用过程与结果均为JSON格式
print(agent_executor.invoke({"input": "马拉松的世界记录是多少？"}))


'''
总结前两章的知识要点
第一次课
1、langchain 的6大组件是什么？
2、什么是提示词，它在与大模型交互中的作用是什么？
3、在langchain中写提示词，form_template与form_messages有什么区别，分别在什么场景下使用
4、你们项目中格式解析器都用什么？如何保证输出的一定是JSON

第二次课
1、在你们项目中，你们常用的runnable可运行组件有哪些？
2、你们项目中使用什么来监控大模型的运行状态？
3、什么是TTFT(TTFT，Time To First Token)？
4、如何降低 TTFT 对agent 的影响？
'''