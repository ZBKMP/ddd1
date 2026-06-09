from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


#  队列事件枚举类型 (参考AppHandler中的debug2,进行简单流式输出时,在队列中加入元素时的事件名称)
class QueueEvent(str, Enum):
    """队列事件枚举类型"""
    # 长期记忆召回事件
    LONG_TERM_MEMORY_RECALL = "long_term_memory_recall"
    # 智能体推理事件 大模型生成工具调用信息时则触发该事件
    AGENT_THOUGHT = "agent_thought"
    # 智能体消息事件 大模型生成文本内容时则触发该事件
    AGENT_MESSAGE = "agent_message"
    # 智能体动作  大模型执行工具调用时则触发该事件
    AGENT_ACTION = "agent_action"
    # 知识库检索事件
    DATASET_RETRIEVAL = "dataset_retrieval"
    # 智能体正常结束事件
    AGENT_END = "agent_end"
    # 智能体意外停止事件
    STOP = "stop"
    # 智能体错误事件
    ERROR = "error"
    # 智能体超时事件 智能体执行任务超过时间阈值时则触发该事件
    TIMEOUT = "timeout"
    # ping联通事件 执行耗时访问时 定期发起ping访问 保持前后端连接联通
    PING = "ping"


# 智能体队列事件模型 存储事件产生的数据信息 后期往队列中添加的为该模型对象
class AgentQueueEvent(BaseModel):
    """智能体队列事件模型"""
    # 1.事件对应的id,事件类型参考QueueEvent类,同一个事件中的多个片段内事件id是相同的.
    # 例如agent_message中采用流式输出,会有多条片段,但都标识为同一个事件
    id: UUID
    # 任务id,一次AI对话可看成是一个任务
    task_id: UUID
    # 事件类型
    event: QueueEvent

    # 2.事件的推理与观察
    # LLM推理内容,LLM生成的工具调用内容
    thought: str = ""
    # 观察内容 知识库、工具调用结果等非LLM生成的内容，用于让LLM观察
    observation: str = ""

    # 3.工具相关的字段
    # 调用工具的名字
    tool: str = ""
    # 工具的输入参数
    tool_input: dict = Field(default_factory=dict)

    # 4.消息相关的数据 (LLM的输入)
    # 推理使用的消息列表(流式输出时将消息转换为字典)
    message: list[dict] = Field(default_factory=dict)
    # 消息花费的token数
    message_token_count: int = 0
    # 单价
    message_unit_price: float = 0
    # 价格单位
    message_price_unit: float = 0

    # 5.答案相关的数据 (LLM的最终输出)
    # LLM生成的最终答案
    answer: str = ""
    # LLM生成答案的token数
    answer_token_count: int = 0
    # 单价
    answer_unit_price: float = 0
    # 价格单位
    answer_price_unit: float = 0

    # 6.Agent推理统计相关
    # 总token消耗数量
    total_token_count: int = 0
    # 总价格
    total_price: float = 0
    # 步骤推理耗时
    latency: float = 0
