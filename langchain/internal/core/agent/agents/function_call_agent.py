import json
import time
import uuid
from threading import Thread
from typing import Generator

from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, RemoveMessage, messages_to_dict, \
    ToolMessage
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.prebuilt import tools_condition

from internal.exception import FailException
from .base_agent import BaseAgent
from internal.core.agent.entities.agent_entity import AgentState, AGENT_SYSTEM_PROMPT_TEMPLATE, \
    DATASET_RETRIEVAL_TOOL_NAME
from internal.core.agent.entities.queue_entity import AgentQueueEvent, QueueEvent


# 基于函数/工具调用的智能体 继承抽象父类
class FunctionCallAgent(BaseAgent):
    """基于函数/工具调用的智能体"""

    # 继承于父类 则会包含两个属性 ：
    # agent_config: AgentConfig
    # agent_queue_manager: AgentQueueManager

    # 重写父类抽象方法
    def run(
            self,
            query: str,  # 用户提问原始问题
            history: list[AnyMessage] = None,  # 短期记忆
            long_term_memory: str = "",  # 长期记忆
    ) -> Generator[AgentQueueEvent, None, None]:
        """运行智能体应用，并使用yield关键字返回对应的数据"""
        # 1 预处理传递的数据 如果没有传递短期记忆消息列表参数,则短期记忆为空列表
        if history is None:
            history = []

        # 2.调用函数构建智能体
        agent = self._build_graph()

        # 3 子线程执行智能体invoke
        thread = Thread(
            target= agent.invoke,
            args = (
                {
                    "messages":[HumanMessage(content=query)],
                    "history": history,
                    "long_term_memory": long_term_memory,
                },
            )
        )
        thread.start()

        # 4 主线程中增加调用队列管理器 监听数据 并返回生成器
        #    主线程与子线程并行执行 子线程执行智能体调用不断向队列增加元素,
        #    主线程则启动循环不停处理队列内的元素.
        yield from self.agent_queue_manager.listen()  #此处返回的 AgentQueueEvent


    # 构建LangGraph图结构编译程序 返回编译好的图应用
    def _build_graph(self) -> CompiledStateGraph:
        """构建LangGraph图结构编译程序"""
        # 1.图的构建者
        graph_builder = StateGraph(AgentState)

        # 2 构建节点
        graph_builder.add_node(
            "long_term_memory_recall", self._long_term_memory_recall_node
        )
        graph_builder.add_node("llm", self._llm_node)
        graph_builder.add_node("tools", self._tools_node)

        # 3 绘制边
        graph_builder.set_entry_point("long_term_memory_recall")
        graph_builder.add_edge("long_term_memory_recall", "llm")
        graph_builder.add_conditional_edges("llm", tools_condition)
        graph_builder.add_edge("tools", "llm")

        # 4 编译智能体
        agent = graph_builder.compile()
        # 5 返回编译好的智能体
        return agent

    # 记忆召回节点(在LLM之前)
    def _long_term_memory_recall_node(self, state: AgentState) -> AgentState:
        # 1.根据传递的智能体配置判断是否需要召回长期记忆
        long_term_memory = ""
        if self.agent_config.enable_long_term_memory:
            long_term_memory = state["long_term_memory"]
            # 向队列中推送长期记忆召回事件 流式输出
            self.agent_queue_manager.publish(AgentQueueEvent(
                id=uuid.uuid4(),
                task_id=self.agent_queue_manager.task_id,
                event=QueueEvent.LONG_TERM_MEMORY_RECALL,
                observation=long_term_memory,  # 表示这是用于给LLM参考的记忆数据
            ))

        # 2.构建预设消息列表，并将preset_prompt+long_term_memory填充到系统消息中
        preset_messages = [
            SystemMessage(content=AGENT_SYSTEM_PROMPT_TEMPLATE.format(
                preset_prompt=self.agent_config.preset_prompt,
                long_term_memory=long_term_memory,
            ))
        ]

        # 3.将短期历史消息添加到消息列表中
        history = state["history"]
        if isinstance(history, list) and len(history) > 0:
            # 4.校验历史消息是不是复数形式，也就是[人类消息, AI消息, 人类消息, AI消息, ...]
            if len(history) % 2 != 0:
                raise FailException("智能体历史消息列表格式错误")
            # 5.在预设的消息列表中 连接上短期历史记忆
            preset_messages.extend(history)

        # 6.拼接当前用户的提问信息 执行图应用时,传入的图状态中,消息列表仅包含一个人类提问消息
        human_message = state["messages"][-1]
        # 将包含用户提问的人类消息 拼接到preset_messages的最后一个 : SY History(HU AI HU AI ....) HU(query)
        preset_messages.append(HumanMessage(human_message.content))

        # 7.处理预设消息，将预设消息添加到用户消息前，先去删除用户的原始消息，然后补充一个新的代替
        return {
            "messages": [RemoveMessage(id=human_message.id), *preset_messages]
        }

    # 大模型节点
    def _llm_node(self, state: AgentState) -> AgentState:
        """大语言模型节点"""
        # 1.从智能体配置中提取大语言模型
        llm = self.agent_config.llm

        # 2.检测大语言模型实例是否有bind_tools方法，如果没有则不绑定，
        #   如果有还需要检测tools是否为空，不为空则绑定
        if (hasattr(llm, "bind_tools")
                and
                callable(getattr(llm, "bind_tools"))
                and
                len(self.agent_config.tools) > 0):
            llm = llm.bind_tools(self.agent_config.tools)
            print("tools_list:",self.agent_config.tools)

        # 3.流式调用LLM输出对应内容
        # 生成事件ID
        event_id = uuid.uuid4()
        # 开启时间统计
        start_at = time.perf_counter()
        gathered = None  # 合并多个chunk
        is_first_chunk = True  # 是否为第一个chunk
        generation_type = ""  # 生成类型 工具调用  文本生成

        # 流式输出 需要再合并多个chunk 作为节点最终返回结果
        for chunk in llm.stream(state["messages"]):
            # 检测是否为非工具,且为执行结果的第一个块,某些LLM第一个块无内容要抛弃
            if is_first_chunk and not chunk.tool_calls and chunk.content.strip() == "":
                print("~~~~~~~~~~~first_empty_chunk~~~~~~~~~~~:", chunk.content, '-----', chunk.tool_calls)
                continue

            # 合并片段
            if is_first_chunk:
                print("~~~~~~~~~~~first_chunk~~~~~~~~~~~:", chunk.content, '-----', chunk.tool_calls)
                gathered = chunk
                is_first_chunk = False
            else:
                gathered += chunk

            # 4  检测生成类型是工具调用还是文本生成 仅针对第一个有效片段
            if not generation_type:
                if chunk.tool_calls:
                    generation_type = "thought"  # 工具调用
                else:
                    generation_type = "message"  # 文本生成

            # 5 如果生成的是文本消息则提交队列 :智能体文本消息事件
            if generation_type == "message":
                self.agent_queue_manager.publish(AgentQueueEvent(
                    # 事件ID
                    id=event_id,
                    # 任务ID
                    task_id=self.agent_queue_manager.task_id,
                    # 事件类型
                    event=QueueEvent.AGENT_MESSAGE,
                    # LLM生成推理内容为消息内容
                    thought=chunk.content,
                    # 前置消息 消息对象[AnyMessage]转换为字典 使用langchain中自带的函数
                    message=messages_to_dict(state["messages"]),
                    # LLM生成的答案
                    answer=chunk.content,
                    # 统计耗时 再次调用time.perf_counter(),并减去初次调用的结果,得到耗时
                    latency=(time.perf_counter() - start_at),
                ))

        # 6.遍历流式输出结束后, 如果类型为推理则添加智能体推理事件
        #  大模型生成工具调用信息,不需要再每个片段中加入队列,
        #  在所有工具参数生成完毕之后,执行一次推送队列
        if generation_type == "thought":
            # 往队列添加事件
            self.agent_queue_manager.publish(AgentQueueEvent(
                # 事件ID
                id=event_id,
                # 任务ID
                task_id=self.agent_queue_manager.task_id,
                # 事件名称
                event=QueueEvent.AGENT_THOUGHT,
                # 前置消息(每个消息转换为字典)
                message=messages_to_dict(state["messages"]),
                # 统计耗时
                latency=(time.perf_counter() - start_at),
            ))
            # 如果类型是thought表示大模型生成了工具调用信息,还要继续调用工具节点.
        elif generation_type == "message":
             # 7.遍历流式输出结束后,如果类型为message,则表示已经拿到了最终答案，则停止监听
             self.agent_queue_manager.stop_listen()

        # 大模型节点返回状态
        print("llm_result:",generation_type, gathered)
        return {
            "messages": [gathered]
        }

    # 工具调用节点
    def _tools_node(self,state: AgentState) -> AgentState:
        # 1.将工具列表转换成字典，便于调用指定的工具
        tools_dict = {
            tool.name: tool
            for tool in self.agent_config.tools
        }

        # 2.提取消息中的工具调用参数 此时最后一条消息必为工具调用消息
        tool_calls = state["messages"][-1].tool_calls

        # 3.循环执行工具组装工具消息
        messages = []  # 消息列表 存储生成的多个ToolMessage
        for tool_call in tool_calls:
            # 4 创建智能体工具调用事件id并记录开始时间
            event_id = uuid.uuid4()
            start_at = time.perf_counter()

            # 5.获取工具并调用工具
            tool = tools_dict[tool_call["name"]]
            tool_result = tool.invoke(tool_call["args"])

            # 6.将工具消息添加到消息列表中
            messages.append(ToolMessage(
                tool_call_id=tool_call["id"],
                content=json.dumps(tool_result),
                name=tool_call["name"],
            ))

            # 7.判断执行工具的名字，提交不同事件，
            #    涵盖智能体动作以及知识库检索
            event = (
                QueueEvent.AGENT_ACTION
                if tool_call["name"] != DATASET_RETRIEVAL_TOOL_NAME
                else QueueEvent.DATASET_RETRIEVAL
             )

            # 往队列添加事件
            self.agent_queue_manager.publish(AgentQueueEvent(
                # 事件ID
                id=event_id,
                # 任务ID
                task_id=self.agent_queue_manager.task_id,
                # 事件名称
                event=event,
                # 大模型观察内容为工具调用结果
                observation=json.dumps(tool_result),
                # 工具名称
                tool=tool_call["name"],
                # 工具调用名称
                tool_input=tool_call["args"],
                # 统计耗时
                latency=(time.perf_counter() - start_at),
            ))


        # 最终返回状态结果
        return {
            "messages": messages
        }

