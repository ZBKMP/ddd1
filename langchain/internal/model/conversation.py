from sqlalchemy import (
    Column,
    UUID,
    String,
    Text,
    Integer,
    DateTime,
    Boolean,
    Numeric,  # 相比Float更加精确
    Float,
    text,
    PrimaryKeyConstraint, func, asc,
)
from sqlalchemy.dialects.postgresql import JSONB

from internal.extension.database_extension import db


# 会话模型
class Conversation(db.Model):
    """交流会话(包含多轮对话过程)模型"""
    __tablename__ = "conversation"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_conversation_id"),
        #Index("conversation_app_id_idx", "app_id"),
        #Index("conversation_app_created_by_idx", "created_by"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    # 关联应用id
    app_id = Column(UUID, nullable=False)
    # 会话名称
    name = Column(
        String(255), nullable=False, server_default=text("''::character varying"))
    # 会话摘要(长期记忆)
    summary = Column(Text, nullable=False, server_default=text("''::text"))
    # 是否置顶
    is_pinned = Column(Boolean, nullable=False, server_default=text("false"))
    # 是否删除(逻辑删除)
    is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    # 会话调用来源 参考internal.entity.conversation_entity.InvokeFrom
    invoke_from = Column(
        String(255), nullable=False, server_default=text("''::character varying"))
    # 会话创建者，会随着invoke_from的差异记录不同的信息，
    # 其中web_app和debugger会记录账号id、service_api会记录终端用户id
    created_by = Column(UUID,nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)')
    )
    created_at = Column(
        DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

    # 只读属性，用于判断该会话是否是第一次创建
    @property
    def is_new(self) -> bool:
        """只读属性，用于判断该会话是否是第一次创建"""
        # 统计该对话下的消息数量 如果大于1则表示已不是一个新会话
        message_count = db.session.query(func.count(Message.id)).filter(
            Message.conversation_id == self.id
        ).scalar()

        return False if message_count > 1 else True


# 消息模型
class Message(db.Model):
    """消息模型"""
    __tablename__ = "message"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_message_id"),
        #Index("message_conversation_id_idx", "conversation_id"),
        #Index("message_created_by_idx", "created_by"),
    )
    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    # 关联应用id
    app_id = Column(UUID, nullable=False)
    # 关联会话id
    conversation_id = Column(UUID, nullable=False)
    # 会话调用来源 参考internal.entity.conversation_entity.InvokeFrom
    # 调用来源，涵盖service_api、web_app、debugger等
    invoke_from = Column(
        String(255),nullable=False,server_default=text("''::character varying"))
    # 消息的创建来源，有可能是LLMOps的用户，也有可能是开放API的终端用户
    created_by = Column(UUID, nullable=False)

    # 用户提问的原始query
    query = Column(Text, nullable=False, server_default=text("''::text"))
    # 产生answer的消息列表
    message = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    # 消息列表的token总数
    message_token_count = Column(Integer, nullable=False, server_default=text("0"))
    # 消息的单价
    message_unit_price = Column(
        Numeric(10, 7),# 总位数  小数点数
        nullable=False,
        server_default=text("0.0")
    )
    # 消息的价格单位
    message_price_unit = Column(
        Numeric(10, 4), # 总位数  小数点数
        nullable=False,
        server_default=text("0.0")
    )

    # Agent生成的消息答案
    answer = Column(Text, nullable=False, server_default=text("''::text"))
    # 消息答案的token数
    answer_token_count = Column(Integer, nullable=False, server_default=text("0"))
    # token的单位价格
    answer_unit_price = Column(
        Numeric(10, 7),
        nullable=False,
        server_default=text("0.0"),
    )
    # token的价格单位
    answer_price_unit = Column(
        Numeric(10, 4),
        nullable=False,
        server_default=text("0.0"),
    )

    # 消息的总耗时
    latency = Column(Float, nullable=False, server_default=text("0.0"))
    # 软删除标记
    is_deleted = Column(Boolean, nullable=False, server_default=text("false"))

    # 消息的状态，涵盖正常、错误、停止
    #  参考internal.entity.conversation_entity.MessageStatus
    status = Column(
        String(255),
        nullable=False,
        server_default=text("''::character varying")
    )
    # 发生错误时记录的信息
    error = Column(Text, nullable=False, server_default=text("''::text"))
    # 消耗的总token数，计算步骤的消耗
    total_token_count = Column(Integer, nullable=False, server_default=text("0"))
    # 消耗的总价格，计算步骤的总消耗
    total_price = Column(
        Numeric(10, 7),
        nullable=False,
        server_default=text("0.0")
    )

    # 消息时间相关信息
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)')
    )

    # 只读属性，返回该消息对应的智能体推理过程列表
    @property
    def agent_thoughts(self) -> list["MessageAgentThought"]:
        """只读属性，返回该消息对应的智能体推理过程列表"""
        return db.session.query(MessageAgentThought).filter(
            MessageAgentThought.message_id == self.id,
        ).order_by(asc("position")).all()


# 消息智能体推理观察模型，用于记录Agent生成最终消息答案的推理步骤
class MessageAgentThought(db.Model):
    """消息智能体观察模型，用于记录Agent生成最终消息答案的推理步骤"""
    __tablename__ = "message_agent_thought"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_message_agent_thought_id"),
        #Index("message_agent_thought_app_id_idx", "app_id"),
        #Index("message_agent_thought_conversation_id_idx", "conversation_id"),
        #Index("message_agent_thought_message_id_idx", "message_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))

    # 关联的应用id
    app_id = Column(UUID, nullable=False)
    # 关联的会话id
    conversation_id = Column(UUID, nullable=False)
    # 关联的消息id
    message_id = Column(UUID, nullable=False)
    # 会话调用来源 参考internal.entity.conversation_entity.InvokeFrom
    # 调用来源，涵盖service_api、web_app、debugger等
    invoke_from = Column(
        String(255),
        nullable=False,
        server_default=text("''::character varying"),
    )
    # 消息的创建来源，有可能是LLMOps的用户，也有可能是开放API的终端用户
    created_by = Column(UUID, nullable=False)

    # 该步骤在消息中执行的位置 推理观察的位置
    position = Column(Integer, nullable=False, server_default=text("0"))

    # 推理与观察，分别记录LLM和非LLM产生的消息
    # 事件名称
    event = Column(
        String(255), nullable=False, server_default=text("''::character varying"))
    # 推理内容(存储LLM生成的内容)
    thought = Column(Text, nullable=False, server_default=text("''::text"))
    # 观察内容(存储知识库、工具等非LLM生成的内容，用于让LLM观察)
    observation = Column(Text, nullable=False, server_default=text("''::text"))

    # 工具相关，涵盖工具名称、输入，在调用工具时会生成
    # 调用工具名称
    tool = Column(Text, nullable=False, server_default=text("''::text"))
    # LLM调用工具的输入，如果没有则为空字典
    tool_input = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    # Agent推理观察步骤使用的消息列表(传递prompt消息内容)
    # 该步骤调用LLM使用的提示消息
    message = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    # 消息花费的token数
    message_token_count = Column(Integer, nullable=False, server_default=text("0"))
    # 单价，所有LLM的计算方式统一为CNY
    message_unit_price = Column(
        Numeric(10, 7),
        nullable=False,
        server_default=text("0.0")
    )
    # 价格单位，值为1000代表1000token对应的单价
    message_price_unit = Column(
        Numeric(10, 4),
        nullable=False,
        server_default=text("0"),
    )

    # LLM生成内容相关(生成内容)
    # LLM生成的答案内容，值和thought保持一致
    answer = Column(
        Text,
        nullable=False,
        server_default=text("''::text")
    )
    # LLM生成答案消耗token数
    answer_token_count = Column(
        Integer,
        nullable=False,
        server_default=text("0")
    )
    # 单价，所有LLM的计算方式统一为CNY
    answer_unit_price = Column(
        Numeric(10, 7),
        nullable=False,
        server_default=text("0.0")
    )
    # 价格单位，值为1000代表1000token对应的单价
    answer_price_unit = Column(
        Numeric(10, 4),
        nullable=False,
        server_default=text("0.0"),
    )

    # Agent推理观察统计相关
    # 总消耗token
    total_token_count = Column(Integer, nullable=False, server_default=text("0"))
    # 总消耗
    total_price = Column(
        Numeric(10, 7), nullable=False, server_default=text("0.0"))
    # 推理观察步骤耗时
    latency = Column(Float, nullable=False, server_default=text("0.0"))

    # 时间相关信息
    # 更新时间
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    # 创建时间
    created_at = Column(
        DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
