# callback回调

import time
from typing import Any, Optional, Union
from uuid import UUID
import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler, StdOutCallbackHandler, FileCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.outputs import LLMResult, GenerationChunk, ChatGenerationChunk
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableConfig


# 自定义CallbackHandler  实现对大模型执行过程的监控
class MyLLMCallbackHandler(BaseCallbackHandler):
    start_at: float = 0.0

    # 重写方法 当执行到大模型开始时 会自动调用该方法
    def on_chat_model_start(
            self,
            serialized: dict[str, Any],
            messages: list[list[BaseMessage]],
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            tags: Optional[list[str]] = None,
            metadata: Optional[dict[str, Any]] = None,
            **kwargs: Any,
    ) -> Any:
        print("Chat model start")
        # 将当前时间记录到start_at中
        self.start_at = time.time()

        # 模型序列化配置信息
        print("serialized:", serialized)
        # 传递给模型的消息列表
        print("messages:", messages)

    # 当大模型产生了一个新Token会触发的方法(使用流式输出才可观察到)
    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        print("LLM new token")
        print("token:", token)
        print("chunk:", chunk)



    # 当大模型执行结束 会自动调用的方法
    def on_llm_end(
            self,
            response: LLMResult,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            **kwargs: Any,
    ) -> Any:
        print("Chat model end")
        end_at = time.time()
        print("response:", response)
        print("消耗的时间:", end_at - self.start_at)


# 1 构建提示词
prompt = ChatPromptTemplate.from_template("用户的问题是:{query}")

# 2 构建llm
dotenv.load_dotenv()
chat_model = ChatOpenAI(model="gpt-3.5-turbo-16k")

# 3 创建一个输出解析器
parser = StrOutputParser()

# 4 编辑一个可运行链
chain = {
            "query": RunnablePassthrough()
        } | prompt | chat_model | parser

# 5 执行链
# result = chain.invoke(
#     input="请介绍什么是LLM?",
#     # 在执行链的过程中 可以增加配置参数 其中可以配置callbacks回调 监控链的执行
#     config=RunnableConfig(
#         # StdOutCallbackHandler Langchain自带的回调处理器,没有监控到大模型
#         # 还可以增加自定义的CallbackHandler,查看大模型节点的输入输出,
#         callbacks=[StdOutCallbackHandler(),MyLLMCallbackHandler()],
#     )
# )
# 6 查看结果
# print(result)


# 如果需要查看到 on_llm_new_token 触发的结果 必须使用流式输出
chunks = chain.stream( # chain也可以使用流式输出函数
    input="请介绍什么是LLM?",
    # 在执行链的过程中 可以增加配置参数 其中可以配置callbacks回调 监控链的执行
    config=RunnableConfig(
        # StdOutCallbackHandler Langchain自带的回调处理器,没有监控到大模型
        # 还可以增加自定义的CallbackHandler,查看大模型节点的输入输出,
        callbacks=[StdOutCallbackHandler(),MyLLMCallbackHandler()],
    )
)
# 链中最后配置了 字符串输出解析器 片段也为str
for chunk in chunks:
    print(chunk,end="", flush=True)

'''
面试题：
1、在你们项目中，你们常用的runnable可运行组件有哪些？
2、你们项目中使用什么来监控大模型的运行状态？
3、什么是TFTT？
4、如何降低 TFTT 对 agent 的影响？
'''


"""
请通过langchain回调功能Callbask 实现统计TTFT耗时。

PS什么是TTFT？

AI 的 “首字响应”（行业标准术语为 TTFT，Time To First Token），指从用户发出指令
（如 “帮我打开厨房灯”）到 AI 输出第一个有效 Token（结构化结果的首个字符 / 字段）的耗时，
是衡量实时交互体验的核心性能指标。
"""

