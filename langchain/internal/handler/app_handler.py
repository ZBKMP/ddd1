import json
import uuid
from dataclasses import dataclass
from queue import Queue
from threading import Thread
from typing import Literal, Generator

from flask import Flask, request, jsonify
from injector import inject
from langchain_community.chat_models import QianfanChatEndpoint
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.constants import END
from langgraph.graph import MessagesState, StateGraph

from internal.core.agent.agents import AgentQueueManager
from internal.core.agent.agents import FunctionCallAgent
from internal.core.agent.entities.agent_entity import AgentConfig
from internal.core.graph import agent
from internal.core.tools.builtin_tools.providers import (
    BuiltinProviderManager
)
from internal.core.tools.builtin_tools.providers.google import google_serper
from internal.entity.conversation_entity import InvokeFrom
from internal.exception import ValidationException
from internal.schema import DebugReq
from internal.service import (
    AppService,
    ApiToolService,
    ConversationService,
)
from internal.task.demo_task import demo_task
from pkg.response import (
    Response,
    HttpCode,
    fail_message,
    success_json,
    success_message, validation_error_json,
)
from pkg.response.response import compact_generate_response


@inject
@dataclass
class AppHandler:
    '''App 模块下的视图函数类'''

    # 依赖注入 业务层对象
    app_service: AppService
    builtin_provider_manager: BuiltinProviderManager
    api_tool_service: ApiToolService
    conversation_service: ConversationService

    def ping(self):
        '''图方法 测试Flask访问'''
        print(1/0)
        return {"ping": "pong"}

        # 1.1  测试 BuiltinProviderManager 获取某个提供商下的指定工具
        # google_serper_func = self.builtin_provider_manager.get_tool(
        #     provider_name='google',
        #     tool_name='google_serper',
        # )
        # # 得到的只是函数 需要执行才能获取工具对象
        # google_serper = google_serper_func()
        # # 测试调用工具
        # result = google_serper.invoke("至今截止的马拉松世界记录是多少")
        # # 响应结果
        # return success_json({
        #     "content": result,
        # })

        # 1.2 测试获取工具的param信息
        # tool = self.builtin_provider_manager.get_tool(
        #     "dalle",
        #     "dalle3"
        # )()
        # tool_entity = self.builtin_provider_manager.get_provider(
        #     "dalle"
        # ).get_tool_entity("dalle3")
        # return success_json({
        #     "content": tool.invoke({"query": "生成老爷爷的图片"}),
        #     "tool_entity": tool_entity.model_dump()
        # })

        # 1.3 测试查看所有ProviderEntity
        # provider_entities = self.builtin_provider_manager.get_provider_entities()
        # provider_entities = [
        #     entity.model_dump() for entity in provider_entities
        #    ]
        # return success_json({
        #     "content": provider_entities,
        # })

        # 1.4 测试其他工具
        # time_tool = self.builtin_provider_manager.get_tool(
        #     "time", "current_time")()
        # time_result = time_tool.invoke(input={})

        # duck_tool = self.builtin_provider_manager.get_tool(
        #     "duckduckgo", "duckduckgo_search")()
        # duck_result = duck_tool.invoke(
        #     input={"query": "至今为止的马拉松世界记录"}
        # )

        # gaode_tool = self.builtin_provider_manager.get_tool(
        #     "gaode", "gaode_weather")()
        # gaode_result = gaode_tool.invoke(input={"city": "长沙"})

        # wiki_tool = self.builtin_provider_manager.get_tool(
        #     "wikipedia", "wikipedia_search")()
        # wiki_result = wiki_tool.invoke(input={"query": "哥德巴赫猜想"})

        # dalle_tool = self.builtin_provider_manager.get_tool(
        #     "dalle", "dalle3")()
        # dalle_result = dalle_tool.invoke(
        #     input={"query": "生成老爷爷的图片"}
        # )

        # return success_json({
        #     "time": time_result,
        #     # "duck_result": duck_result,
        #     # "gaode_result": gaode_result,
        #     # "wiki_result": wiki_result,
        #     # "dalle_result": dalle_result
        #
        # })

        # 1.5 测试ApiToolManager 加载自定义工具
        # tool = self.api_tool_service.get_api_base_tool(
        #     provider_id="88b58768-8ed3-4050-bc28-5cbcd12ddf7f",
        #     tool_name="YoudaoSuggest_2"
        # )
        # result = tool.invoke({"q": "hello", "doctype": "json"})
        # return success_json({"tool_result": result})

        # 1.6 测试调用 Celery异步任务
        # demo_task.delay(uuid.uuid4())
        # return success_message("执行了一个异步任务")

        # 1.7 测试 ConversationService.summary 生成摘要
        # summary = self.conversation_service.summary(
        #     human_message="请介绍什么是LLM",
        #     ai_message="""
        #                    大语言模型（Large Language Model, LLM） 是一种基于深度学习的自然语言处理模型，
        #                    它通过在大规模文本数据上进行训练，学会了理解、生成和处理人类语言
        #                     """,
        #     old_summary="""
        #                     人类介绍自己是小黑子，喜欢唱跳、rap和篮球，并询问AI的身份和喜好。AI自我介绍为DeepSeek-V3，
        #                     强调自己的“爱好”是学习新知识、解答问题和与人交流，尽管没有真实情感，但擅长聊天和讨论各种话题，
        #                     包括唱跳、rap和篮球。AI表示随时准备帮助小黑子
        #                     """
        # )
        # return success_json({"summary": summary})

        # 1.8 测试 ConversationService.generate_conversation_name 生成会话名称
        # conversation_name = self.conversation_service.generate_conversation_name(
        #     query="请介绍什么是LLM"
        # )
        # return success_json({"conversation_name": conversation_name})

        # 1.9 测试 ConversationService.generate_suggested_questions 生成建议问题
        # suggested_questions = self.conversation_service.generate_suggested_questions(
        #     histories="""
        #             人类介绍自己是小黑子，喜欢唱跳、rap和篮球，并询问AI的身份和喜好。AI自我介绍为DeepSeek-V3，
        #             强调自己的“爱好”是学习新知识、解答问题和与人交流，尽管没有真实情感，但擅长聊天和讨论各种话题，
        #             包括唱跳、rap和篮球。AI表示随时准备帮助小黑子
        #             """
        # )
        # return success_json({"suggested_questions": suggested_questions})

    def debug(self, app_id: uuid.UUID):
        '''在flask平台下 测试langchain ai应用'''
        # query = request.json.get("query") # json - dict

        # 所有对请求中参数的验证 交给FlaskForm去完成
        req = DebugReq()
        if not req.validate():
            # 1
            # 如果DebugReq验证错误 返回错误结果到前端
            # return req.errors

            # 2
            # 使用包装的Response对象来表示接口响应的结果
            # response = Response(
            #     code=HttpCode.FAIL,
            #     message="请求参数出现错误!",
            #     data= req.errors
            # )
            # 使用 jsonify 将对象转换为字典 再输出为JSON
            # return jsonify(response)

            # 3
            # 使用包装好的响应方法 替代上述代码
            # return fail_message(msg="请求参数出现错误!")

            # 4 将各种类型的错误 包装为指定的异常 在抛出
            raise ValidationException(data=req.errors)

        # 验证成功 则从DebugReq中提取参数值
        query = req.query.data
        # langchain实现
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "你是OpenAi 开发的机器人， 请回答用户的问题："),
                ("human", "{query}")
            ]
        )
        llm = ChatOpenAI(model='gpt-3.5-turbo-16k')
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"query": query})

        # 1
        # return {"content":result}

        # 2
        # 使用包装的Response对象来表示接口响应的结果
        # response = Response(
        #     code=HttpCode.SUCCESS,
        #     message="响应成功",
        #     data={"content":result}
        # )
        # return jsonify(response)

        # 3
        # 使用包装好的响应方法 替代上述代码
        # return success_json(data = {"content":result})

        # 使用Agent测试
        result = agent.invoke({"query": query})
        return success_json(data={"content": result.get("answer")})

    # 要求1 改写debug  在其中调用一个图应用 图应用可以写在 core/graph/my_graph.py中
    #                 在此处应用出 "图应用" 执行结果输出到浏览器

    ####################################################################################

    # 调用业务层 实现数据库增删改查的接口
    # 1 调用业务层 实现添加一个数据
    def create_app(self):
        # 模拟添加 省略了从request获取参数

        # 调用业务层 实现在app表中新增一行数据
        app = self.app_service.create_app()

        # 响应结果
        return success_message(f'数据创建成功 id:{app.id}')

    def get_app(self, id: uuid.UUID):  # 增加路径参数
        app = self.app_service.get_app(id)
        return success_message(f"应用成功获取 name为{app.name}")

    def update_app(self, id: uuid.UUID):  # 增加路径参数
        app = self.app_service.update_app(id)
        return success_message(f"应用成功修改 name为{app.name}")

    def delete_app(self, id: uuid.UUID):  # 增加路径参数
        app = self.app_service.delete_app(id)
        return success_message(f"应用成功删除 name为{app.name}")

    ##########################################################################
    #  debug2 测试流式输出 在函数过程中创建一个图应用
    def debug2(self, app_id: uuid.UUID):
        # 1 请求处理
        req = DebugReq()
        if not req.validate():
            return validation_error_json(req.errors)
        query = req.query.data

        # 2 创建队列 在多个线程之间共享数据
        q = Queue()

        # 3 创建Graph图程序 并最终执行图应用 在执行大模型节点与工具调用节点时 会向队列添加元素
        def graph_app() -> None:
            # 3.1 工具列表
            tools = [
                self.builtin_provider_manager.get_tool(
                    "google",
                    "google_serper")(),
                self.builtin_provider_manager.get_tool(
                    "gaode",
                    "gaode_weather")(),
                self.builtin_provider_manager.get_tool(
                    "dalle",
                    "dalle3")(),
            ]

            # 3.2 LLM节点  会向队列添加元素
            def chatbot(state: MessagesState) -> MessagesState:
                # 3.2.1 创建大语言模型并绑定工具
                chat_model = ChatOpenAI(
                    model="gpt-3.5-turbo-16k",
                    temperature=0.7).bind_tools(tools)

                print("tools_bind:",tools)
                print("chat_model:",chat_model)

                # 3.2.2 调用stream流式输出,并判断生成结果为文本还是工具调用信息
                is_tool_call = False  # 标记:是否为工具调用
                is_first_chunk = True  # 标记:是否为第一个块
                gathered = None  # 定义变量,合并多个chunk块
                id = str(uuid.uuid4())  # 生成一个UUID 作为队列中当前节点的事件编号

                # 以状态中的消息列表作为输入,执行stream方法实现流式输出,遍历输出结果的每个片段
                for chunk in chat_model.stream(input=state["messages"]):
                    print("chunk", chunk)
                    # 3.2.3 检测是否为非工具,且为执行结果的第一个块,某些LLM第一个块无内容要抛弃
                    if is_first_chunk and not chunk.tool_calls and chunk.content.strip() == "":
                        continue

                    # 3.2.4 叠加相应的区块 (ai消息最终需要合并成完整消息  作为大模型节点的返回结果)
                    if is_first_chunk:
                        # 将第一个片段先赋值给 gathered
                        gathered = chunk
                        is_first_chunk = False
                    else:
                        gathered += chunk
                    # gathered 将所有片段又合并成一个完整的AI消息

                    # 3.2.5 将每个片段对应信息加入到队列,作为流式输出的内容,要判断每个片段是工具调用还是文本生成
                    if chunk.tool_calls or is_tool_call:
                        # chunk中包含tool_calls属性则表示当前是工具调用信息,将标记is_tool_call改为true
                        is_tool_call = True
                        # 往队列中加入元素,值为字典,结构为 id: event: data:
                        q.put(item={
                            "id": id,  # 用于标记当前大模型的一次操作 一次操作下会生成多个chunk
                            "event": "agent_thought",  # agent_thought 表示该事件为工具调用
                            "data": json.dumps(chunk.tool_calls)  # 片段中的工具调用消息
                        })
                    else:
                        # 文本输出
                        q.put(item={
                            "id": id,
                            "event": "agent_message",  # agent_message 表示该事件为内容生成
                            "data": chunk.content
                        })

                # 返回状态中需要的消息列表 合并成一条完整的消息
                print("gathered ai_msg:", gathered)
                return {
                    "messages": [gathered],
                }

            # 3.3 工具调用节点 会向队列添加元素
            def tool_executor(state: MessagesState) -> MessagesState:
                # 3.3.1提取状态中最后一条消息中的tool_calls
                tool_calls = state["messages"][-1].tool_calls
                # 3.3.2将工具列表转换为字典
                tools_dict = {
                    tool.name: tool for tool in tools
                }
                # 3.3.3执行工具并得到对应结果
                messages = []
                for tool_call in tool_calls:
                    # 循环遍历 tool_calls ,执行需要的每个工具
                    tool = tools_dict[tool_call["name"]]
                    tool_result = tool.invoke(tool_call["args"])
                    # 执行完一次工具调用 则在消息列表中增加一条工具调用消息
                    messages.append(ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=json.dumps(tool_result),
                        name=tool_call["name"],
                    ))

                    # 每个工具都生成唯一的事件ID
                    id = str(uuid.uuid4())
                    # 每执行完一次工具调用 也将工具调用结果加入到队列中
                    q.put(item={
                        "id": id,
                        "event": "agent_action",  # 事件类型
                        "data": json.dumps(tool_result)  # 工具调用结果是完整的 不会生成chunk
                    })

                # 返回消息列表 包含所有的工具调用消息 合并到之前的消息列表
                return {
                    "messages": messages,
                }

            # 3.4 定义路由函数 确定下一个步骤
            def route(state: MessagesState) -> Literal["tool_executor", "__end__"]:
                ai_message = state["messages"][-1]
                if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
                    return "tool_executor"
                return END

            # 3.5 创建状态图
            graph_builder = StateGraph(MessagesState)
            # 3.6 添加节点
            graph_builder.add_node("chatbot", chatbot)
            graph_builder.add_node("tool_executor", tool_executor)
            # 3.7 添加边
            graph_builder.set_entry_point("chatbot")
            graph_builder.add_conditional_edges("chatbot", route)
            graph_builder.add_edge("tool_executor", "chatbot")
            # 3.8 编译图
            graph = graph_builder.compile()
            # 3.9 调用图 生成结果
            result = graph.invoke({"messages": [("human", query)]})
            print("最终结果:", result)
            q.put(None)  # 标记 向队列发送一个None,以表示队列结束

        # 4 定义一个生成器 作为流式事件输出响应内容 从队列中不停提取内容 作为flask流式响应
        def stream_event_response() -> Generator:
            # 4.1 循环遍历队列中的数据,并使用yield做为生成器的输出
            while True:
                item = q.get()
                print("item", item)
                if item is None:
                    break

                # 4.2 使用yield返回对应的数据 严格按照以下格式输出!
                yield f"event: {item.get('event')}\ndata: {json.dumps(item)} \n\n"
                q.task_done()  # 通知队列完成了单次任务

        # 5 创建子线程执行图程序 过程中不断向队列添加元素,
        t = Thread(target=graph_app)
        t.start()

        # 6 主线程中 以生成器作为参数,返回流式输出响应的FlaskResponse
        # compact_generate_response执行生成器的过程中,不断访问队列中添加的事件,则持续进行流式响应输出
        return compact_generate_response(response=stream_event_response())

    # debug3 测试agent模块下的 BaseAgent FunctionAllAgent 实现流式输出
    def debug3(self, app_id: uuid.UUID):
        # 1 请求处理
        req = DebugReq()
        if not req.validate():
            return validation_error_json(req.errors)
        query = req.query.data

        # 2 构建智能体
        # 2.1定义工具列表
        tools = [
            self.builtin_provider_manager.get_tool(
                "google", "google_serper")(),
            self.builtin_provider_manager.get_tool(
                "gaode", "gaode_weather")(),
            self.builtin_provider_manager.get_tool(
                "dalle", "dalle3")(),
        ]
        # 2.2 配置对象
        agent_config = AgentConfig(
            llm=ChatOpenAI(model="gpt-4o-mini"),
            preset_prompt="你是由OpenAI开发的聊天机器人，可以帮助用户回答问题，必须调用工具帮助用户解答，如果问题需要多个工具回答，请一次性调用所有工具，不要分步调用",
            enable_long_term_memory=True,
            tools=tools,
        )
        # 2.3 队列管理器
        agent_queue_manager = AgentQueueManager(
            user_id=uuid.uuid4(),  # 用户ID
            task_id=uuid.uuid4(),  # 任务ID
            invoke_from=InvokeFrom.DEBUGGER,  # 会话来源
        )
        # 2.4 创建智能体对象
        function_call_agent = FunctionCallAgent(
            agent_config=agent_config,
            agent_queue_manager=agent_queue_manager,
        )

        # 定义流式响应输出生成器函数
        def stream_event_response() -> Generator:
            """流式事件输出响应"""
            #  遍历 agent.run执行返回的生成器 ,暂时不传递短期记忆,暂时先模拟一个长期记忆
            #  run方法内部已经使用子线程去执行.
            #  run方法内部包含了agent_queue_manager.listen(),启动队列监听
            for agent_queue_event in function_call_agent.run(
                    query=query,
                    # 虚假的模拟数据
                    history=[
                        HumanMessage("什么是LLM?"),
                        AIMessage("LLM指的是人工智能大语言模型,可以根据人类提问回答问题.")
                    ],
                    # 虚假的模拟数据
                    long_term_memory="人类说自己叫小黑子,问AI你是谁.AI回答自己是AI智能机器人"
            ):
                #  agent_queue_event --> data(dict)
                data = {
                    "id": str(agent_queue_event.id),  # 事件ID
                    "task_id": str(agent_queue_event.task_id), # 会话ID
                    "event": agent_queue_event.event.value,  # 事件类型
                    "thought": agent_queue_event.thought,  # 推理过程 工具调用信息
                    "message": agent_queue_event.message, # LLM输入的消息列表list[dict]
                    "observation": agent_queue_event.observation, # 工具生成结果
                    "tool": agent_queue_event.tool,  # 工具名称
                    "tool_input": agent_queue_event.tool_input, # 工具调用采纳数
                    "answer": agent_queue_event.answer, # LLM回答的文本结果
                    "latency": agent_queue_event.latency # 耗时
                }
                # 按固定格式 进行流式事件响应yield输出 从而实现生成器
                yield f"event: {data['event']}\ndata: {json.dumps(data)}\n\n"

        #  compact_generate_response执行生成器的过程中,
        #  不断访问队列中添加的事件, 则持续进行流式响应输出
        return compact_generate_response(stream_event_response())


