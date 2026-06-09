# SerperAPI谷歌搜索工具

import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from pydantic import BaseModel, Field

dotenv.load_dotenv()


# 定义谷歌Serper工具的参数规范
class GoogleSerperToolArgsSchema(BaseModel):
    query: str = Field(description="执行google搜索时传入的搜索关键词")
# 创建工具
google_serper_tool = GoogleSerperRun(
    name="google_serper_tool",
    description=(
        "一个低成本的谷歌搜索API,"
        "当你需要回答有关时事的问题时,可以调用该工具."
        "该工具的输入是搜索查询语句"
    ),
    api_wrapper=GoogleSerperAPIWrapper(),  # 内部已经包含了参数规范描述
    args_schema=GoogleSerperToolArgsSchema,
)

# 使用工具
print("工具名称:", google_serper_tool.name)
print("工具描述:", google_serper_tool.description)
print("工具需要的参数:", google_serper_tool.args)
print("工具的参数规范:", google_serper_tool.args_schema)

# 使用时可以简化 仅传递要搜索的字符串即可
# result = google_serper_tool.invoke("至今为止马拉松世界记录是多少?")
# print(result)

result = google_serper_tool.invoke({"query": "至今为止马拉松世界记录是多少?"})
print(result)
