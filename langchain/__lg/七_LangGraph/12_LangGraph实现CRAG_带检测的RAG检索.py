# LangGraph实现CRAG 带检测的RAG检索
from typing import TypedDict, Any, Literal

import dotenv
import weaviate
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from langgraph.graph import StateGraph
from weaviate.auth import AuthApiKey

# 1.图应用需要的材料
# 1.1 LLM大模型
dotenv.load_dotenv()
llm = ChatOpenAI(model='gpt-3.5-turbo-1106')

# 1.2 基于weaviate向量库实现检索器
client = weaviate.connect_to_local(
    host="192.168.58.129",
    port=8080,
)
db = WeaviateVectorStore(
    client=client,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    index_name='Collection_project',  # 数据集名称
    text_key='text',  # 文本内容的key名
)
retriever = db.as_retriever(search_type="mmr")

# 1.3 RAG增强生成最终结果链
template = """
你是一个问答任务的助理。使用以下检索到的上下文来回答问题。如果不知道就说不知道，不要胡编乱造，并保持答案简洁。
问题: {query}
上下文: {context}
答案: 
"""
prompt = ChatPromptTemplate.from_template(template)
# 执行链时使用bind,动态的将温度设置为0 使其回答更为确定 结果转换为str
rag_chain = prompt | llm.bind(temperature=0) | StrOutputParser()


# 1.4 构建检索评估链 结合原问题 检索到的每条文档 判断文档是否可用
# 必须规范大模型输出结果为  yes/no
class GradeDocument(BaseModel):
    """文档评分Pydantic模型"""
    relevant: Literal["yes", "no"] = Field(description="文档与问题是否关联，请回答yes或者no")


# 文档评估链
system = """你是一名评估检索到的文档与用户问题相关性的评估员。
如果文档包含与问题相关的关键字或语义，请将其评级为相关。
给出一个是否相关得分为yes或者no，以表明文档是否与问题相关。"""

system = """你是一名评估检索到的文档与用户问题相关性的评估员。你的任务是根据提供的文档内容，判断该文档是否与用户问题相关。
如果相关，输出一个标准的 JSON 对象，其中键必须是 "relevant"，值必须是 "yes"；如果不相关，则值是 "no"。
**注意：请只输出 JSON 对象，不要输出任何其他解释、评论或格式，例如：{{"relevant": "yes"}}。**"""
grade_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "检索文档: \n\n{context}\n\n用户问题: {query}"),
])
# 定义链
grade_chain = grade_prompt | llm.with_structured_output(
    schema=GradeDocument,
    method="json_mode"
).bind(temperature=0) | (lambda x:(print("grade_output:",x)) or x)

# 1.5 网络搜索问题重写链
rewrite_prompt = ChatPromptTemplate.from_messages([
    (
        "system", "你是一个将输入问题转换为优化的更好版本的问题重写器，并用于网络搜索。请查看输入并尝试推理潜在的语义意图或含义。"
    ),
    ("human", "这里是初始化问题:\n\n{query}\n\n请尝试提出一个改进问题。")
])
rewrite_chain = rewrite_prompt | llm.bind(temperature=0) | StrOutputParser()


# 1.6 网络搜索工具 googleSerper
class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


google_serper_tool = GoogleSerperRun(
    name="google_serper_tool",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，可以调用该工具。"
        "该工具的输入是搜索查询语句。"
    ),
    api_wrapper=GoogleSerperAPIWrapper(),
    args_schema=GoogleSerperArgsSchema,
)


# 1.7 要求 2 cohere 精炼 (将之前检索到的文档列表包装为自定义检索器,再传递给Cohere)


# 2 根据上述材料构建图应用需要的节点函数
# 2.1 定义图状态
class GraphState(TypedDict):
    """图结构应用的数据状态"""
    query: str  # 原始用户输入
    documents: list[Document]  # 文档列表
    is_web_search: Literal["yes", "no"]  # 是否需要进行网络搜索新文档
    answer: str  # 图应用最终生成的文本内容


# 该状态可以不设置归纳函数,该应用使用状态时仅需要对已有属性进行覆盖更新即可

# 2.2 检索节点 根据用户输入 从知识库检索出文档列表
def retriever_node(state: GraphState) -> Any:
    """检索节点 根据原始问题搜索向量数据库"""
    print("---检索节点---")
    # 提取原始问题
    query = state["query"]
    # 使用原始问题进行检索
    documents = retriever.invoke(input=query)
    print("搜索出的文档:")
    for document in documents:
        print("--------------------")
        print(document.page_content[:100])
        print("--------------------")

    # 没有归纳函数 覆盖原有内容中的documents
    return {
        **state,  # 其他状态属性保持不变
        "documents": documents,
    }


# 2.3 llm生成节点
def format_docs(docs: list[Document]) -> str:
    return '\n\n'.join([doc.page_content for doc in docs])


def rag_chain_node(state: GraphState) -> Any:
    """LLM生成节点,根据原始问题+上下文内容调用LLM生成内容"""
    print("---LLM生成节点---")
    # 获取原始问题
    query = state["query"]
    # 获取文档列表
    documents = state["documents"]
    # 合并列表成文本
    context = format_docs(documents)
    # 得到最后结果
    answer = rag_chain.invoke(input={"context": context, "query": query})
    return {
        **state,
        "answer": answer,
    }


# 2.4 质量评估节点 (对文档列表中的每一个文档进行质量评估,结果为no则删除该文档,节点返回yes,否则返回no)
def grade_chain_node(state: GraphState) -> Any:
    """文档与原始问题关联性评估节点"""
    print("---文档与原始问题关联性评估节点---")
    # 从状态中获取原始提问
    query = state["query"]
    # 从状态中获取文档列表
    documents = state["documents"]
    # 假设不需要网络检索
    is_web_search = "no"
    # 遍历每个文档 调用评估链 进行评估
    filtered_docs = []  # 经过筛选后的文档列表
    for document in documents:
        grade_document: GradeDocument = grade_chain.invoke(
            input={"context": document.page_content, "query": query}
        )
        print({"context": document.page_content, "query": query})
        print("grade_document:",grade_document)
        grade_result = grade_document.relevant
        print("文档评估结果:", grade_result)
        if grade_result.lower().strip() == "yes":  # 该文档评估通过
            filtered_docs.append(document)
        else:  # 该文档不合格 更改 is_web_search 需要进行网络检索
            is_web_search = "yes"
    # 返回结果
    return {
        **state,
        "documents": filtered_docs,
        "is_web_search": is_web_search,
    }


# 2.5 条件边判断路由函数
def decide_to_generate_or_transform_query(
        state: GraphState
) -> Literal["rewrite_chain_node", "rag_chain_node"]:
    """决定是去生成节点 还是去 重写问题节点"""
    print("---选择边的路由函数---")
    # 获取是否需要网络检索
    is_web_search = state["is_web_search"]
    if is_web_search.lower().strip() == "yes":
        print("--- 执行web搜索 重新生成问题 ---")
        return "rewrite_chain_node"
    else:
        print("--- 执行LLM生成节点---")
        return "rag_chain_node"


# 2.6 问题重写节点  根据原始问题 生成新问题
def rewrite_chain_node(state: GraphState) -> Any:
    """重写原始问题节点"""
    print("---重写原始问题节点---")
    # 获取原始问题
    query = state["query"]
    # 执行重写链生成新问题
    new_query = rewrite_chain.invoke(input={"query": query})
    print("重写问题:", new_query)
    # 返回结果
    return {
        **state,
        "query": new_query,
    }


# 2.7 网络检索节点 使用新问题进行网络检索 根据检索结果生成新文档,加入到文档列表
def web_search_node(state: GraphState) -> Any:
    """网络搜索节点"""
    print("---网络搜索节点---")
    # 获取提问
    query = state["query"]
    # 获取文档列表
    documents = state["documents"]
    # 进行网络检索 将文本结果包装为Document 补充到文档列表中
    search_result = google_serper_tool.invoke(input={"query": query})
    print("网络搜索结果:", search_result)
    documents.append(Document(page_content=search_result))
    # 返回结果
    return {
        **state,
        "documents": documents,
    }


# 3 构建图应用
agent_builder = StateGraph(state_schema=GraphState)

# 增加节点
agent_builder.add_node("retriever_node", retriever_node)
agent_builder.add_node("rag_chain_node", rag_chain_node)
agent_builder.add_node("grade_chain_node", grade_chain_node)
agent_builder.add_node("rewrite_chain_node", rewrite_chain_node)
agent_builder.add_node("web_search_node", web_search_node)

# 绘制边
# 开始
agent_builder.set_entry_point("retriever_node")
agent_builder.add_edge("retriever_node", "grade_chain_node")
agent_builder.add_conditional_edges(
    source="grade_chain_node",
    path=decide_to_generate_or_transform_query,
)  # 条件边会练到 大模型生成节点 或 问题重构节点
agent_builder.add_edge("rewrite_chain_node", "web_search_node")
agent_builder.add_edge("web_search_node", "rag_chain_node")
# 结束
agent_builder.set_finish_point("rag_chain_node")

# 编译图
agent = agent_builder.compile()

# 4 测试
result = agent.invoke({"query": "LLMOPS平台接口如何开发"})
print(result)

client.close()

# 要求 2 按照飞书文档要求 在评估正确 到LLM节点之间 增加一个文档精炼节点 cohere对文档进行重排


# 要求 3 以图应用的方式实现 基于MYSQL实现记忆功能
''' 表：
  id  conversation_id  消息类型(Human,AI) 消息内容content
'''
#  开始 ---> 记忆加载节点(读取数据库 加载为消息列表 存入到状态,考虑:通过对话轮数实现长期记忆生成摘要(做一条系统消息)，短期记忆保持原样) -- > 大模型节点 (每次将用户提问 与 ai回答记录到数据库 每条消息都是单独记录)-->结束
#  循环执行图 测试记忆功能 每次执行产生一个随机的ConversationID
