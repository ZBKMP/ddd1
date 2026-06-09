from abc import ABC, abstractmethod
from typing import Generator

from langchain_core.messages import AnyMessage

from .agent_queue_manager import AgentQueueManager
from internal.core.agent.entities.agent_entity import AgentConfig
from internal.core.agent.entities.queue_entity import AgentQueueEvent


# LLMOps项目基础Agent  抽象类(父类 自身不能实例化)
class BaseAgent(ABC):
    """LLMOps项目基础Agent"""
    # agent相关配置信息
    agent_config: AgentConfig
    # 新增 : 智能体队列管理器
    agent_queue_manager: AgentQueueManager


    def __init__(
            self,
            agent_config: AgentConfig,
            agent_queue_manager: AgentQueueManager,
    ):
        """构造函数，初始化智能体图结构程序"""
        self.agent_config = agent_config
        self.agent_queue_manager = agent_queue_manager # 智能体队列管理器


    # 抽象类中可以包含抽象方法 子类必须重写父类中的抽象方法
    # 智能体的运行方法
    @abstractmethod
    def run(
            self,
            query: str,  # 用户提问原始问题
            history: list[AnyMessage] = None,  # 短期记忆
            long_term_memory: str = "",  # 长期记忆
    ) -> Generator[AgentQueueEvent, None, None]:
        # 新增 : 返回生成器 实现流式输出,yield返回类型为AgentQueueEvent
        """智能体运行函数，传递原始提问query、长短期记忆，并调用智能体生成相应内容"""
        raise NotImplementedError("Agent智能体的run函数未实现")

'''
    Generator[YieldType, SendType, ReturnType]
    YieldType: 生成器每次 yield 返回的数据类型
    SendType: 通过 generator.send(value) 发送给生成器的数据类型
    ReturnType: 生成器结束时 return 返回的值类型（Python 3.3+）

    Generator[AgentQueueEvent, None, None]含义：
    AgentQueueEvent：生成器每次 yield 返回的是 AgentQueueEvent 类型的对象
    第一个 None：不能通过 .send() 方法向生成器发送数据
    第二个 None：生成器结束时没有返回值（或者返回 None）
'''