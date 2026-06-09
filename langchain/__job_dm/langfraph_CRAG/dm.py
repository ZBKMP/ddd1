
import os
import dotenv
from typing import TypedDict, Any, Literal
import weaviate
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from langgraph.graph import StateGraph
import cohere  # 导入 Cohere 官方库


dotenv.load_dotenv()  #读取 .env 配置文件
llm = ChatOpenAI(model='gpt-4o-mini')

co = cohere.Client(os.getenv("COHERE_API_KEY"))

# 连接 Weaviate 数据库
client = weaviate.connect_to_local(host="192.168.172.129", port=8080)
db = WeaviateVectorStore(
    client=client,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    index_name='Collection',
    text_key='text',
)
retriever = db.as_retriever(search_type="mmr")  # [mmr] ：找资料时保证多样性



# RAG 生成链的模板
template = """你是一个助理。使用以下上下文回答问题。不知道就说不知道。
问题: {query}
上下文: {context}
答案: """
rag_prompt = ChatPromptTemplate.from_template(template)
rag_chain = rag_prompt | llm.bind(temperature=0) | StrOutputParser()


# 文档评估逻辑 (强制要求 AI 只输出 yes 或 no)
class GradeDocument(BaseModel):
    binary_score: Literal["yes", "no"] = Field(description="文档与问题是否关联")


grade_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一名相关性评估员。给出一个是否相关得分：yes或no。"),
    ("human", "检索文档: \n\n{context}\n\n用户问题: {query}"),
])
grade_chain = grade_prompt | llm.with_structured_output(schema=GradeDocument)

# 问题重写逻辑 (如果资料不好，就把问题改得更适合搜索)
rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个问题重写器，用于优化网络搜索。"),
    ("human", "原始问题:\n\n{query}\n\n请提出一个改进后的搜索问题。")
])
rewrite_chain = rewrite_prompt | llm.bind(temperature=0) | StrOutputParser()

# 谷歌搜索工具
google_serper_tool = GoogleSerperRun(api_wrapper=GoogleSerperAPIWrapper())


# --- 4. 定义图状态

class GraphState(TypedDict):
    query: str  #  存储当前问题
    documents: list[Document]  #  存储文档资料夹
    is_web_search: Literal["yes", "no"]  # 是否需要上网
    answer: str  # [str] 存储最后的答案


# --- 5. 节点函数 具体的干活逻辑

def retriever_node(state: GraphState) -> Any:
    """【检索站】：去数据库搬书"""
    print("--- 步骤：从‘数据库’检索 ---")
    query = state["query"]  # [state] 指从记事本读取 query 这一页
    documents = retriever.invoke(input=query)  # [invoke] 技能：开始检索
    return {**state, "documents": documents}  # [**] 保留旧记录，只更新 documents


def grade_chain_node(state: GraphState) -> Any:
    """【审查站】：检查找回来的书行不行"""
    print("--- 步骤：评估文档相关性 ---")
    query = state["query"]
    documents = state["documents"]
    is_web_search = "no"  # 默认不需要上网
    filtered_docs = []

    for document in documents:  #
        res = grade_chain.invoke(input={"context": document.page_content, "query": query})
        grade_result = res.binary_score
        if grade_result.lower().strip() == "yes":  # 如果是 yes
            filtered_docs.append(document)  # 把合格的放进新盒子
        else:
            is_web_search = "yes"  # [=] 赋值：只要一份不行，就标记需要上网

    return {**state, "documents": filtered_docs, "is_web_search": is_web_search}


def rewrite_chain_node(state: GraphState) -> Any:
    """【翻译站】：重写搜索词"""
    print("--- 步骤：重写搜索关键词 ---")
    new_query = rewrite_chain.invoke(input={"query": state["query"]})
    return {**state, "query": new_query}


def web_search_node(state: GraphState) -> Any:
    """【外援站】：去谷歌搜资料"""
    print("--- 步骤：执行谷歌搜索 ---")
    query = state["query"]
    documents = state["documents"]
    search_result = google_serper_tool.invoke(input={"query": query})
    # [Document] ：把网页文字包装成标准的“书本格式”
    documents.append(Document(page_content=search_result))
    return {**state, "documents": documents}


def rerank_node(state: GraphState) -> Any:
    """【装修站】：Cohere 精炼重排"""
    print("--- 步骤：Cohere 语义重排精炼 ---")
    query = state["query"]
    documents = state["documents"]
    if not documents: return state

    # [doc.page_content] 动作：只提取书里的文字，给 Cohere 看
    doc_contents = [doc.page_content for doc in documents]
    response = co.rerank(
        model="rerank-multilingual-v3.0",
        query=query,
        documents=doc_contents,
        top_n=3  # 只要前三名
    )

    # 按照 Cohere 的推荐顺序重新排文档
    reranked_docs = [documents[hit.index] for hit in response.results]
    return {**state, "documents": reranked_docs}


def rag_chain_node(state: GraphState) -> Any:
    """【作家站】：写出最终答案"""
    print("--- 步骤：生成最终回答 ---")
    query = state["query"]
    documents = state["documents"]
    # [\n\n.join] ：把所有选出的文档粘在一起
    context = '\n\n'.join([doc.page_content for doc in documents])
    answer = rag_chain.invoke(input={"context": context, "query": query})
    return {**state, "answer": answer}


# --- 6.  (构建分流规则与连线) ---

def decide_to_route(state: GraphState) -> Literal["rewrite_chain_node", "rerank_node"]:
    """[分流器]：决定去搜索还是去重排"""
    if state["is_web_search"] == "yes":
        return "rewrite_chain_node"
    return "rerank_node"


# 实例化
agent_builder = StateGraph(state_schema=GraphState)

# [add_node] ：设立窗口
agent_builder.add_node("retriever_node", retriever_node)
agent_builder.add_node("grade_chain_node", grade_chain_node)
agent_builder.add_node("rewrite_chain_node", rewrite_chain_node)
agent_builder.add_node("web_search_node", web_search_node)
agent_builder.add_node("rerank_node", rerank_node)
agent_builder.add_node("rag_chain_node", rag_chain_node)

# [add_edge] ：连线
agent_builder.set_entry_point("retriever_node")  # 起点
agent_builder.add_edge("retriever_node", "grade_chain_node")  # 单行道

# [add_conditional_edges] ：建岔路口
agent_builder.add_conditional_edges("grade_chain_node", decide_to_route)

# 连线
agent_builder.add_edge("rewrite_chain_node", "web_search_node")
agent_builder.add_edge("web_search_node", "rerank_node")  # 搜完去重排
agent_builder.add_edge("rerank_node", "rag_chain_node")  # 重排完去生成
agent_builder.set_finish_point("rag_chain_node")  # 终点

# 编译并运行
agent = agent_builder.compile()

if __name__ == "__main__":
    # 模拟输入
    inputs = {"query": "蓝猫的饲养攻略"}
    result = agent.invoke(inputs)
    print("\n【最终答案】:\n", result["answer"])
    client.close()