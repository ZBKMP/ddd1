import logging
from dataclasses import dataclass
from injector import inject
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .base_service import BaseService
from internal.entity.conversation_entity import (
    SUMMARIZER_TEMPLATE,
    CONVERSATION_NAME_TEMPLATE,
    ConversationInfo,
    SUGGESTED_QUESTIONS_TEMPLATE,
    SuggestedQuestions,
)


@inject
@dataclass
class ConversationService(BaseService):
    # 根据传递的人类消息、AI消息还有原摘要信息总结生成一段新的摘要
    @classmethod
    def summary(
            cls,
            human_message: str,
            ai_message: str,
            old_summary: str = "",
    ) -> str:
        """根据传递的人类消息、AI消息还有原摘要信息总结生成一段新的摘要"""
        # 1.创建prompt internal.entity.conversation_entity.SUMMARIZER_TEMPLATE
        prompt = ChatPromptTemplate.from_template(SUMMARIZER_TEMPLATE)

        # 2.构建大语言模型实例，并且将大语言模型的温度调低，降低幻觉的概率
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

        # 3.构建链应用
        summary_chain = prompt | llm | StrOutputParser()

        # 4.调用链并获取新摘要信息  参照提示模板,组织需要传入的占位符参数
        new_summary = summary_chain.invoke({
            "summary": old_summary,
            "new_lines": f"Human: {human_message}\nAI: {ai_message}",
        })

        return new_summary

    # 根据传递的query生成对应的会话名字，并且语言与用户的输入保持一致
    @classmethod
    def generate_conversation_name(cls, query: str) -> str:
        """根据传递的query生成对应的会话名字，并且语言与用户的输入保持一致"""
        # 1.创建prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", CONVERSATION_NAME_TEMPLATE),
            ("human", "{query}")
        ])

        # 2.构建大语言模型实例，并且将大语言模型的温度调低，降低幻觉的概率
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        # internal.entity.conversation_entity.ConversationInfo 规范大语言模型输出
        structured_llm = llm.with_structured_output(ConversationInfo)

        # 3.构建链应用
        chain = prompt | structured_llm

        # 4.提取并整理query,截取长度过长的部分,长度超过2000则仅截取开头结尾各300长度
        if len(query) > 2000:
            query = query[:300] + "...[TRUNCATED]..." + query[-300:]
        query = query.replace("\n", " ")

        # 5.调用链并获取会话信息
        conversation_info = chain.invoke({"query": query})
        print("conversation_info:", conversation_info)
        # 6.提取会话名称  生成结果中包含了subject属性,则提取成会话名称
        name = "新的会话"
        try:
            if conversation_info and hasattr(conversation_info, "subject"):
                name = conversation_info.subject
        except Exception as e:
            logging.exception(f"提取会话名称出错, conversation_info: {conversation_info}, 错误信息: {str(e)}")

        # 7.会话名称控制在75字以内
        if len(name) > 75:
            name = name[:75] + "..."

        return name

    # 根据传递的历史信息生成最多不超过3个的建议问题
    @classmethod
    def generate_suggested_questions(cls, histories: str) -> list[str]:
        """根据传递的历史信息生成最多不超过3个的建议问题"""
        # 1.创建prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", SUGGESTED_QUESTIONS_TEMPLATE),
            ("human", "{histories}")
        ])

        # 2.构建大语言模型实例，并且将大语言模型的温度调低，降低幻觉的概率
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        # internal.entity.conversation_entity.SuggestedQuestions 规范大语言模型输出
        structured_llm = llm.with_structured_output(SuggestedQuestions)

        # 3.构建链应用
        chain = prompt | structured_llm

        # 4.调用链并获取建议问题列表
        suggested_questions = chain.invoke({"histories": histories})

        # 5.提取建议问题列表
        questions = []
        try:
            if suggested_questions and hasattr(suggested_questions, "questions"):
                questions = suggested_questions.questions
        except Exception as e:
            logging.exception(f"生成建议问题出错, suggested_questions: {suggested_questions}, 错误信息: {str(e)}")

        # 6.限定生成的问题数量最多3个
        if len(questions) > 3:
            questions = questions[:3]

        return questions
