import sys
import types
import typing

# ==========================================
# 0. 强力内存补丁：修复损坏的 langchain_core
# ==========================================
try:
    import langchain_core.language_models as lm
    # 如果发现缺失核心组件，手动补齐
    if not hasattr(lm, "BaseLanguageModel") or not hasattr(lm, "LanguageModelInput"):
        from langchain_core.runnables import Runnable
        # 伪造 BaseLanguageModel (它本质上是一个 Runnable)
        if not hasattr(lm, "BaseLanguageModel"):
            lm.BaseLanguageModel = Runnable
        # 伪造 LanguageModelInput (本质上是 Any 类型)
        if not hasattr(lm, "LanguageModelInput"):
            lm.LanguageModelInput = typing.Any
        print("--- 已手动修复 langchain_core 组件缺失问题 ---")
except Exception as e:
    print(f"--- 补丁尝试失败: {e} ---")

# 1. 之前的分布式补丁
sys.modules["torch.distributed.rpc"] = types.ModuleType("rpc")
sys.modules["torch.distributed.rpc.api"] = types.ModuleType("api")

# ==========================================
# 2. 现在再开始导入（这时它们就能找到伪造的组件了）
# ==========================================
from langchain.retrievers import MultiQueryRetriever
# ... 剩下的导入保持不变
import sys
import os
import types
import dotenv
import weaviate



from typing import List
from langchain_weaviate import WeaviateVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings  # 避开 LanguageModelInput 报错
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.retrievers import MultiQueryRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.load import dumps, loads
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 加载环境变量
dotenv.load_dotenv()


# ==========================================
# 第一部分：RRF 核心算法实现
# ==========================================
class RRFMultiQueryRetriever(MultiQueryRetriever):
    k: int = 4  # 最终返回最相关的 4 条数据

    def retrieve_documents(
            self, queries: list[str], run_manager: CallbackManagerForRetrieverRun
    ) -> list[list[Document]]:
        """重写检索方法：为每个查询保留独立的文档列表（二维列表）"""
        documents = []
        for query in queries:
            docs = self.retriever.invoke(
                query, config={"callbacks": run_manager.get_child()}
            )
            documents.append(docs)
        return documents

    def unique_union(self, documents: list[list[Document]]) -> list[Document]:
        """重写合并方法：使用 RRF 算法进行排名融合"""
        fused_result = {}
        for docs in documents:
            for rank, doc in enumerate(docs):
                doc_str = dumps(doc)
                if doc_str not in fused_result:
                    fused_result[doc_str] = 0
                # RRF 公式：得分 = 1 / (60 + 排名)
                fused_result[doc_str] += 1 / (rank + 60)

        # 按得分降序排列
        reranked_results = [
            (loads(doc), score)
            for doc, score in sorted(fused_result.items(), key=lambda x: x[1], reverse=True)
        ]
        # 仅返回前 k 个 Document 对象
        return [item[0] for item in reranked_results[:self.k]]


# ==========================================
# 第二部分：本地化路径处理与模型加载
# ==========================================
# 动态定位当前脚本目录下的 text.md
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'text.md')

if not os.path.exists(file_path):
    print(f"错误：找不到文件 {file_path}")
    sys.exit()

# 使用 BGE-M3 模型 (确保入库和检索使用同一个模型)
model_name = 'BAAI/bge-m3'
embeddings = HuggingFaceEmbeddings(model_name=model_name)

# ==========================================
# 第三部分：连接与执行
# ==========================================
client = weaviate.connect_to_local(
    host=os.getenv("HOST"),
    port=int(os.getenv("PORT")),
    grpc_port=int(os.getenv("GRPC_PORT"))
)

try:
    # 定义基础检索器
    db = WeaviateVectorStore(
        client=client,
        embedding=embeddings,
        index_name='LocalTest',
        text_key='text'
    )
    base_retriever = db.as_retriever(search_type="mmr")

    # 定义 RRF 高级检索器
    m_retriever = RRFMultiQueryRetriever.from_llm(
        prompt=ChatPromptTemplate.from_template(
            "你是一个AI助手。请针对以下问题生成3个不同版本的搜索查询，"
            "用换行符分隔。原始问题：{question}"),
        retriever=base_retriever,
        llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.1),
        include_original=True,
    )

    # 执行查询
    query_str = "关于配置接口的信息有哪些"
    results = m_retriever.invoke(query_str)

    print(f"\n--- 查询结果 (基于 RRF 融合排名) ---")
    for i, doc in enumerate(results):
        print(f"[{i + 1}] 内容预览: {doc.page_content[:100]}...")
        print(f"    元数据: {doc.metadata}\n-------")

finally:
    client.close()