from dataclasses import dataclass

from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, trim_messages, get_buffer_string
from sqlalchemy import desc

from internal.entity.conversation_entity import MessageStatus
from internal.extension.database_extension import db  # 数据库db
from internal.model import Conversation, Message


@dataclass
# 基于token计数的缓冲记忆组件
class TokenBufferMemory:
    """基于token计数的缓冲记忆组件"""
    conversation: Conversation  # 会话模型实体
    model_instance: BaseLanguageModel  # LLM大语言模型 用于计算token长度

    # 根据传递的 token限制+消息条数限制 从数据库中获取指定会话模型的历史消息列表
    def get_history_prompt_messages(
            self,
            max_token_limit: int = 2000,
            message_limit: int = 10,
    ) -> list[AnyMessage]: # 返回任意类型的消息列表
        """根据传递的token限制+消息条数限制获取指定会话模型的历史消息列表"""
        # 1.判断会话模型实体是否存在，如果不存在则直接返回空列表
        if self.conversation is None:
            return []

        # 2.查询该会话的消息列表，并且使用时间进行倒序，同时匹配答案不为空、
        #   匹配会话id、没有被删除、状态是正常或停止
        messages = db.session.query(Message).filter(
            Message.conversation_id == self.conversation.id,
            Message.answer != "",
            Message.is_deleted == False,
            # Message.status == MessageStatus.NORMAL,
            # 后期增加搜索范围 STOP , TIMEOUT
            Message.status.in_([
                MessageStatus.STOP,
                MessageStatus.NORMAL,
                MessageStatus.TIMEOUT,
            ]),
        ).order_by(desc("created_at")).limit(message_limit).all()
        # 反转顺序
        messages = list(reversed(messages))

        # 3.将messages转换成LangChain消息列表
        prompt_messages = []  # LangChain消息列表
        for message in messages:
            prompt_messages.extend([
                HumanMessage(content=message.query), # query-Human
                AIMessage(content=message.answer),  # answer-AI
            ])

        # 4.调用LangChain集成的trim_messages函数剪切消息列表
        return trim_messages(
            messages=prompt_messages, # 消息列表
            max_tokens=max_token_limit, # token阈值
            token_counter=self.model_instance, # token计算函数
            strategy="last", # 裁剪策略 尽量保存近期消息
            start_on="human",
            end_on="ai",
        )

    # 根据传递的数据获取指定会话历史消息提示文本(短期记忆的文本形式，用于文本生成模型)
    def get_history_prompt_text(
            self,
            human_prefix: str = "Human",
            ai_prefix: str = "AI",
            max_token_limit: int = 2000,
            message_limit: int = 10,
    ) -> str:
        """根据传递的数据获取指定会话历史消息提示文本(短期记忆的文本形式，用于文本生成模型)"""
        # 1.根据传递的信息获取历史消息列表
        messages = self.get_history_prompt_messages(max_token_limit, message_limit)

        # 2.调用LangChain集成的get_buffer_string()函数将消息列表转换成文本
        return get_buffer_string(messages, human_prefix, ai_prefix)

