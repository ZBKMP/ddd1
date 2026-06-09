# 要求 1  在flask的视图函数中 实现从请求中获取用户提问 编辑提示模板(使用各种拼接)
#        大模型生成内容 提取content 作为响应结果 以JSON方式响应到前端(requests测试)

'''
要求 2 
请实现一个智能家具控制机器人。该机器人必须输出json格式的控制指令(结合JsonOutputParser),
思考：在系统消息中如何编写提示词，以告知AI需要完成的任务
示例如下:
Human：请帮我打开厨房灯
Ai:{"target":"light","position":"kitchen","id":XXXXX,"url":"wwww.alltman.com"}
执行过程中 可以测试单次生成 和 批处理
# 要求 3
# 将上述所有AI执行流程 换成chain 来执行
'''

'''
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# --- 1. 定义输出结构 (Pydantic) ---
class SmartHomeCommand(BaseModel):
    target: str = Field(description="控制目标，如 light, air_conditioner, TV")
    position: str = Field(description="设备所在位置，如 kitchen, bedroom, living_room")
    id: int = Field(description="设备的唯一识别码，固定为 4 位整数")
    url: str = Field(description="控制接口的 URL 地址")

# --- 2. 初始化组件 ---
model = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0
)

parser = JsonOutputParser(pydantic_object=SmartHomeCommand)

# --- 3. 编写提示模板 ---
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能家居控制机器人。你的任务是将用户的自然语言转换为特定的 JSON 控制指令。\n{format_instructions}"),
    ("human", "{user_input}")
])

# --- 4. 组装 Chain (要求 3：全流程使用 Chain) ---
chain = prompt | model | parser

# --- 5. 执行测试 ---

# 单次生成
print("=== 单次生成测试 ===")
single_res = chain.invoke({
    "user_input": "请帮我打开厨房灯",
    "format_instructions": parser.get_format_instructions()
})
print(f"单次输出内容: {single_res}")
print(f"类型确认: {type(single_res)}") # 已经是 dict 类型

print("\n" + "*"*50 + "\n")

# 测试 B：批处理 (Batch)
print("=== 批处理测试 ===")
batch_inputs = [
    {"user_input": "把卧室空调调到26度", "format_instructions": parser.get_format_instructions()},
    {"user_input": "关掉客厅的电视机", "format_instructions": parser.get_format_instructions()}
]
batch_res = chain.batch(batch_inputs)

for i, res in enumerate(batch_res):
    print(f"任务 {i+1} 结果: {res}")
'''

'''
通过langchain回调功能Callbask 实现统计TTFT耗时。

import time
import dotenv
from typing import Any, Optional, Union
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler, StdOutCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.outputs import LLMResult, GenerationChunk, ChatGenerationChunk
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableConfig

# 加载 .env 环境变量（包含 API Key）
dotenv.load_dotenv()

class TTFTMetricsCallbackHandler(BaseCallbackHandler):

    def __init__(self):
        self.start_time = 0.0  # 请求开始时间
        self.ttft_time = 0.0  # 首字到达时间
        self.token_count = 0  # 累计生成的 Token 数量
        self.has_recorded_ttft = False  # 状态锁：确保只记录一次首字时间

    def on_chat_model_start(
            self, serialized: dict[str, Any], messages: list[list[BaseMessage]], **kwargs: Any
    ) -> Any:

        self.start_time = time.time()  # 记录起点
        self.has_recorded_ttft = False  # 重置状态锁
        self.token_count = 0  # 重置计数器
        print(f"\n[系统日志] >>> 模型开始推理...")

    def on_llm_new_token(
            self, token: str, chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None, **kwargs: Any
    ) -> Any:

        self.token_count += 1

        # 如果是第一个 Token，记录 TTFT
        if not self.has_recorded_ttft:
            # 当前时间减去开始时间即为 TTFT
            self.ttft_time = time.time() - self.start_time
            self.has_recorded_ttft = True
            print(f"\n[性能指标]  TTFT (首字响应时间): {self.ttft_time:.4f} 秒")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:

        end_time = time.time()
        total_duration = end_time - self.start_time

        # 计算 TPOT: (总时间 - 首字时间) / 剩下的 Token 数
        # 这反映了模型纯粹的“打字”速度，排除了首字网络延迟
        other_tokens_count = self.token_count - 1
        tpot = (total_duration - self.ttft_time) / other_tokens_count if other_tokens_count > 0 else 0

        print(f"\n[性能指标]  推理结束")
        print(f"      - 总耗时: {total_duration:.4f} 秒")
        print(f"      - Token 总数: {self.token_count}")
        print(f"      - TPOT (单字平均耗时): {tpot:.4f} 秒/Token")

# 1. 实例化模型，必须设置 streaming=True，否则无法触发 on_llm_new_token
chat_model = ChatOpenAI(
    model="gpt-3.5-turbo-16k",
    streaming=True,
    temperature=0.7
)

# 2. 准备提示词模板
prompt = ChatPromptTemplate.from_template("请用100字左右介绍一下 {query}")

# 3. 组合 LCEL 链
chain = (
        {"query": RunnablePassthrough()}
        | prompt
        | chat_model
        | StrOutputParser()
)


# 实例化我们的自定义回调
perf_handler = TTFTMetricsCallbackHandler()

print("开始测试流式输出与性能统计...\n")

# 使用 .stream 方法启动
chunks = chain.stream(
    input="量子力学",
    # 在 config 中挂载回调，StdOutCallbackHandler 是 LangChain 官方的控制台日志
    config=RunnableConfig(callbacks=[perf_handler])
)

# 打印 AI 的回复内容
print("AI 回复内容: ", end="")
for chunk in chunks:
    # flush=True 确保字符实时显示在屏幕上，不进缓冲区
    print(chunk, end="", flush=True)

print("\n\n测试完成。")
'''
'''
# 要求 1: 模拟真实RAG检索,重新编写retriever函数,判断用户输入中是否包含某个关键词(历史 人文 物理 化学 地理.....)
# 如果有则找到以关键词命名的文档文件(历史.txt,人文.txt,物理.txt...)读取文档内容作为检索结果

# 要求 2 : 还可以扩展为MySQL数据库查询,以知识库表中的 知识科目(subject)列为搜索条件,以关键词进行查询
# 或者是以知识内容列 进行模糊查询，内容包含关键词，注意多条结果要合并为一个文本

'''
'''
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "sx",
    "charset": "utf8mb4"
}

def custom_rag_retriever(input_data: dict) -> str:
    query = input_data.get("query", "")
    print(f"--- 程序启动 ---")


    subjects = ["zb", "zz", "zg", "物理", "化学"]
    found_subject = None
    for s in subjects:
        if s in query:
            found_subject = s
            break

    retrieved_contents = []

    try:
        import pymysql
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:

            sql = "SELECT name, age, score FROM stunew WHERE name = %s OR name LIKE %s"
            cursor.execute(sql, (found_subject, f"%{query}%"))

            results = cursor.fetchall()
            print(f"数据库查询到 {len(results)} 条结果")

            for row in results:
                # 将查询到的数据转为字符串描述
                content = f"学生姓名: {row[0]}, 年龄: {row[1]}, 分数: {row[2]}"
                retrieved_contents.append(content)

    except Exception as e:
        print(f"数据库查询异常: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

    if not retrieved_contents:
        return "未找到相关参考知识。"

    return "\n".join(retrieved_contents)


# 测试调用
if __name__ == "__main__":

    print(custom_rag_retriever({"query": "给我 zb 的资料"}))
    '''


