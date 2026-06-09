# gpt-4o接入DALL.E工具实现文生图:

import dotenv
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1 dalle 可以通过文本生成图片工具（结果为URL）
dalle = OpenAIDALLEImageGenerationTool(
    name="openai-dalle",
    # api包装器,模型指向dall-e-2/dall-e-3
    api_wrapper=DallEAPIWrapper(model="dall-e-3")
)
# 该工具需要的参数为query 例如:长沙橘子洲头的风景，青翠的橘子树，宁静的湘江水，远处现代城市的高楼大厦与蓝天白云相映成趣
result = dalle.invoke({"query": "生成一张登山的图片"})
print(result)


# 2 将图片生成工具绑定到大模型
llm = ChatOpenAI(model="gpt-4o-mini")
llm.bind_tools(tools=[dalle],tool_choice="openai-dalle")
chain = (
    llm | (lambda x: print(f"ai_message: {x}") or x)  | (lambda msg: msg.tool_calls[0]['args']) | dalle
)
# 3 执行链 结果为图片连接
result_url = chain.invoke("生成一张打野猪的图片")
print(result_url)


# 要求 1  : 大模型绑定多个工具(谷歌搜索,天气查询,图片生成),实现在用户提问之后 除了回答问题,还能依据回答结果生成一张图片



