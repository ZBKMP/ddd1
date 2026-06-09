"""
要求 2
请实现一个智能家具控制机器人。该机器人必须输出json格式的控制指令(结合JsonOutputParser),
思考：在系统消息中如何编写提示词，以告知AI需要完成的任务
示例如下:
Human：请帮我打开厨房灯
Ai:{"target":"light","position":"kitchen","id":XXXXX,"url":"wwww.alltman.com"}


执行过程中 可以测试单次生成 和 批处理
"""

import os
import random
from typing import Optional

import dotenv
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# 定义输出结构（用于指导 LLM 和 JSON 解析）
class FurnitureControl(BaseModel):
    target: str = Field(description="设备类型，例如 'light', 'air_conditioner', 'curtain'")
    position: str = Field(description="设备所在位置，例如 'kitchen', 'living_room', 'bedroom'")
    id: str = Field(description="设备唯一标识，可以随机生成或从指令推断")
    url: str = Field(description="控制端点 URL，固定为 'wwww.alltman.com'")

# 初始化 JSON 输出解析器
parser = JsonOutputParser(pydantic_object=FurnitureControl)

# 构建提示模板（包含格式要求）
prompt = PromptTemplate(
    template="你是一个智能家具控制机器人。根据用户的指令，提取出目标设备类型（target）、位置（position）。\n"
             "你需要生成一个随机的 5 位数字作为设备 ID（id）。url 字段固定为 'wwww.alltman.com'。\n"
             "请严格按照以下 JSON 格式输出，不要包含任何其他文本：\n{format_instructions}\n"
             "用户指令：{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# 初始化 LLM（使用 OpenAI，请设置环境变量 OPENAI_API_KEY）
dotenv.load_dotenv()
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 构建处理链
chain = prompt | llm | parser

def control_robot(user_input: str) -> dict:
    """
    处理用户输入并返回 JSON 控制指令。
    无记忆功能，每次调用独立。
    """
    try:
        result = chain.invoke({"query": user_input})

        # 确保 id 字段存在且为字符串，url 固定
        result["url"] = "wwww.alltman.com"
        if "id" not in result or not result["id"]:
            result["id"] = str(random.randint(10000, 99999))

        return result
    except Exception as e:
        # 错误时返回一个默认 JSON
        return {
            "target": "unknown",
            "position": "unknown",
            "id": str(random.randint(10000, 99999)),
            "url": "wwww.alltman.com",
            "error": str(e)
        }

# 示例交互（单轮多次调用，无记忆）
if __name__ == "__main__":
    # 测试示例
    test_queries = [
        "请帮我打开厨房灯",
        "关闭卧室空调",
        "把客厅窗帘拉上"
    ]
    for q in test_queries:
        print(f"Human: {q}")
        resp = control_robot(q)
        print(f"AI: {resp}\n")