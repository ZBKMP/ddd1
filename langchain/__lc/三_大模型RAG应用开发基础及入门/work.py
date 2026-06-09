import re
import uuid

import dotenv
from langchain_core.embeddings import Embeddings
from langchain.schema import Document
from langchain_pinecone import PineconeVectorStore
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

dotenv.load_dotenv()


#  使用 向量库实现记忆存储 按内容的相似性检索记忆内容
class VectorMemory:
    def __init__(
            self,
            embeddings: Embeddings = None,
            top_k: int = 3  # 从向量库检索数据的结果的条数
    ):
        self.embeddings = embeddings
        self.top_k = top_k
        # 初始化pinecone数据库
        self.db = PineconeVectorStore(
            embedding=embeddings,
            index_name="llmops5",  # pinecone中的库名 index
            namespace='dataset_memory',  # 每个库index下可以有多个namespace(类比SQL中的表)
        )

    def load_memory_variables(
            self,
            conversation_id: str,
            current_query: str
    ) -> list[BaseMessage]:
        """根据当前用户输入与会话ID，检索相关历史对话"""

        # 没有数据则返回空
        if not current_query or self.db is None :
            return []

        # 以用户提问从向量中检索文本相关的记忆内容 以会话ID作为额外过滤条件
        docs = self.db.similarity_search(
            current_query,
            k=self.top_k,
            filter={"conversation_id":{"$eq": conversation_id}},
        )
        if not docs:
            return []

        # 将page_content 转换为一轮对话 包含Human消息与AI消息
        messages = []
        # 格式化历史对话
        for doc in docs:
            content = doc.page_content
            match = re.search(r'Human:(.*?) AI:(.*)', content)
            if match:
                human = match.group(1).strip()  # 从当前一组内容中取出第一个元素内容
                ai = match.group(2).strip() # 从当前一组内容中取出第2个元素内容
                print("history-Human:", human)
                print("history-AI:", ai)
                messages.append(HumanMessage(human))
                messages.append(AIMessage(ai))

        print("messages:", messages)
        return messages

    # 保存记忆
    def save_context(self,
                     conversation_id: str,  # 会话ID  元数据存储
                     human_input: str,
                     ai_output: str,
                     ) -> None:
        """保存当前对话的人类输入和AI输出到向量库"""
        if not human_input or not ai_output:
            return
        # 构造文档内容
        content = f"Human:{human_input} AI:{ai_output}"
        doc = Document(
            page_content=content,
            metadata={"conversation_id": conversation_id}
        )
        # 添加到vectorstore
        self.db.add_documents(
            documents=[doc]
        )


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
memory = VectorMemory(
    embeddings=OpenAIEmbeddings(model="text-embedding-3-small")
)

# 4 编辑链
conversation_id = str(uuid.uuid4()) # 创建会话ID
print(conversation_id)
chain = (RunnablePassthrough.assign(
    chat_history=RunnableLambda(lambda x: memory.load_memory_variables(conversation_id, x["query"])),
) | prompt | (lambda x: print("prompt:", x) or x) | llm | StrOutputParser())

while True:
    query = input("Human:")

    if query.lower() == "q":
        break

    chain_input = {"query": query}

    result = chain.invoke(chain_input)
    print("AI:",result)

    # 保存记忆
    memory.save_context(conversation_id, query, result)
