# 不使用langchain内置的这些记忆组件 配合MySQL实现记忆存储类 只读取近期的N条对话 之前的都生成摘要
# 提供方法  加载记忆(返回消息列表/字符串) 存储记忆(参数 人类提问 和 AI生成)

'''
CREATE TABLE  chat_messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    conversation_id VARCHAR(255) NOT NULL,
    human_input TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ;
'''

import traceback
import uuid

import dotenv
import pymysql
from typing import List, Tuple
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI  # 需要安装 langchain-openai

dotenv.load_dotenv()

# 数据库连接对象
class DBUtil:
    def __init__(self):
        self.__conn = None
        self.__cursor = None

    def get_conn(self):
        self.__conn = pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            database="mydb",
            port=3306,
            charset='utf8mb4',
        )
        self.__cursor = self.__conn.cursor()
        return self.__conn, self.__cursor

    def close_conn(self):
        if self.__conn is not None and self.__cursor is not None:
            self.__cursor.close()
            self.__conn.close()


# 数据库记忆类
class SimpleMemoryStore:
    def __init__(self, llm=None):
        self.__dbutil = DBUtil()
        self.k = 3  # 保留最近k轮对话
        # 如果未提供 LLM，则使用默认的 ChatOpenAI（需设置 OPENAI_API_KEY 环境变量）
        if llm is None:
            self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        else:
            self.llm = llm

    def store(self, conversation_id, human_input, ai_response) -> None:
        """存储一条对话记录"""
        conn, cursor = self.__dbutil.get_conn()
        try:
            sql = """
                  INSERT INTO chat_messages (conversation_id, human_input, ai_response)
                  VALUES (%s, %s, %s) \
                  """
            cursor.execute(sql, (conversation_id, human_input, ai_response))
            conn.commit()
        except Exception as e:
            print(e)
            traceback.print_exc()
            conn.rollback()
        finally:
            self.__dbutil.close_conn()

    def _generate_summary(self, old_messages: List[Tuple[str, str]]) -> str:
        """
        使用大模型根据旧聊天记录生成摘要
        old_messages: list of (human_input, ai_response)
        """
        if not old_messages:
            return ""
        # 构建聊天历史文本，格式：Human:xxx, AI:xxx ; Human:xxx, AI:xxx ; ......
        chat_history_parts = []
        for human, ai in old_messages:
            chat_history_parts.append(f"Human: {human}, AI: {ai}")
        chat_history = " ; ".join(chat_history_parts)

        prompt_template = "请根据提供的聊天对话信息生成一段摘要信息,总结该段聊天信息核心思想内容，以下是聊天信息文本:{chat_history}"
        prompt = prompt_template.format(chat_history=chat_history)

        # 调用大模型生成摘要
        response = self.llm.invoke(prompt)
        summary = response.content
        return summary.strip()

    def load(self, conversation_id) -> List[BaseMessage]:
        """
        加载记忆：返回消息列表（List[BaseMessage]）
        如果存在k轮以外的历史，则生成摘要并作为 SystemMessage 放在列表开头
        然后接上最近k轮对话转换的 HumanMessage 和 AIMessage
        """
        conn, cursor = self.__dbutil.get_conn()
        try:
            sql = """
                  SELECT human_input, ai_response, created_at
                  FROM chat_messages
                  WHERE conversation_id = %s
                  ORDER BY created_at ASC \
                  """
            cursor.execute(sql, (conversation_id,))
            rows = cursor.fetchall()  # each row: (human_input, ai_response, created_at)

            total = len(rows)
            if total == 0:
                return []

            # 分离历史（用于生成摘要）和近期对话
            if total <= self.k:
                recent_rows = rows
                old_rows = []
            else:
                recent_rows = rows[-self.k:]
                old_rows = rows[:-self.k]

            # 生成摘要（如果有旧消息）
            summary = ""
            if old_rows:
                old_pairs = [(row[0], row[1]) for row in old_rows]
                summary = self._generate_summary(old_pairs)

            # 构建消息列表
            messages: List[BaseMessage] = []
            if summary:
                # 生成的摘要放在消息列表的开头 作为系统消息
                messages.append(SystemMessage(content=summary))

            for row in recent_rows:
                human_text, ai_text, _ = row
                messages.append(HumanMessage(content=human_text))
                messages.append(AIMessage(content=ai_text))

            return messages

        except Exception as e:
            print(e)
            traceback.print_exc()
            return []
        finally:
            self.__dbutil.close_conn()


#  测试使用

# 1 大模型
llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
# 2 创建提示词
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是具有AI功能的聊天机器人,请根据对应的上下文回答问题"),
    # MessagesPlaceholder("chat_history"),  # 此占位符 需要的chat_history是一个列表
    ("placeholder", "{chat_history}"),  # 元祖可传可不传 声明类则必须没有也传[]
    ("human", "用户的问题是:{query}")
])

# 3 记忆对象
memory = SimpleMemoryStore(
    llm=llm,
)

# 4 编辑链
chain = (RunnablePassthrough.assign(
    chat_history=RunnableLambda(lambda x: memory.load(conversation_id)),
) | prompt | (lambda x:print("prompt:",x) or x) | llm | StrOutputParser())

# 5 执行对话过程
conversation_id = str(uuid.uuid4()) # 创建会话ID
while True:
    query = input("Human:")

    if query.lower() == "q":
        break

    chain_input = {"query": query}

    result = chain.invoke(chain_input)
    print(result)

    # 保存记忆
    memory.store(conversation_id, query, result)
