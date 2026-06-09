# RAG多查询结果融合策略 使用RRF倒排序排名算法优化MultiQueryRetriever的逻辑
from typing import List

import dotenv
import weaviate
from langchain.retrievers import MultiQueryRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.load import dumps, loads
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()


# RRF算法函数 [ [doc,doc],[doc,doc],[doc,doc] ]
def rrf(results: List[List[Document]]):
    # 对传入的二层嵌套文档列表进行去重合并,并返回排名较高的数据
    # 1.定义一个变量存储每个文档的得分信息
    fused_result = {}

    # 2.循环两层获取每一个文档信息
    '''
    【
query：【docs】
query：【docs】
query：【docs】
query：【docs】
   】
    '''
    for docs in results:
        for rank, doc in enumerate(docs):
            # 3.dumps将对象转换为字符串
            doc_str = dumps(doc)
            # 4.判断该文档的字符串是否已经计算过得分
            if doc_str not in fused_result:
                fused_result[doc_str] = 0
            # 5.计算新得分
            fused_result[doc_str] += 1 / (60 + rank)
    # 6.执行排序操作,按得分的降序排序,获取相应的数据 使用降序
    reranked_results = [
        (loads(doc), score) for doc, score in sorted(fused_result.items(), key=lambda x: x[1], reverse=True)
    ]
    return reranked_results

###########################################################################################################

# 重写MultiQueryRetriever检索器
class RRFMultiQueryRetriever(MultiQueryRetriever):
    k: int = 4

    # 重写 retrieve_documents 方法 但返回值改为二维列表
    def retrieve_documents(
        self,
        queries: list[str],
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[list[Document]]:
        # 将原本的extend方法替换成append方法 则结果会变为二维列表
        documents = []
        for query in queries:
            docs = self.retriever.invoke(
                query,
                config={"callbacks": run_manager.get_child()},
            )
            documents.append(docs) # extends / append
        return documents


    # 重写方法 unique_union ,实现按RRF算法合并文档列表  参数为二维列表
    def  unique_union(self, documents: list[list[Document]]) -> list[Document]:
        # 对传入的二层嵌套文档列表进行去重合并,并返回排名较高的数据
        # 1.定义一个变量存储每个文档的得分信息
        fused_result = {}

        # 2.循环两层获取每一个文档信息
        for docs in documents:
            for rank, doc in enumerate(docs):
                # 3.dumps将对象转换为字符串
                doc_str = dumps(doc)
                # 4.判断该文档的字符串是否已经计算过得分
                if doc_str not in fused_result:
                    fused_result[doc_str] = 0
                # 5.计算新得分
                fused_result[doc_str] += 1 / (rank + 60)
        # 6.执行排序操作,按得分的降序排序,获取相应的数据 使用降序
        reranked_results = [
            # Document对象  RRF算法的得分
            (loads(doc), score) for doc, score in sorted(fused_result.items(), key=lambda x: x[1], reverse=True)
        ]

        # 7 返回文档列表 仅需要Document对象 不需要分数
        return [item[0] for item in reranked_results[:self.k]]


#####################################################################################

# 测试
client = weaviate.connect_to_local(
    host="192.168.172.129",
    port=8080,
)
db = WeaviateVectorStore(
    client=client,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    index_name='collection_project',  # 数据集名称
    text_key='text',  # 文本内容的key名
)
retriever = db.as_retriever(search_type="mmr")

m_retriever = RRFMultiQueryRetriever.from_llm(
# 中文环境下 建议重构中文版本的提示词
    prompt=ChatPromptTemplate.from_template(
        "你是一个AI语言模型助手。你的任务是根据给定的用户问题生成3个不同的版本，"
        "以便从向量数据库中检索相关文档。通过从多个角度生成用户问题，"
        "你的目标是帮助用户克服基于距离的相似性搜索的一些局限性。"
        "请用换行符分隔这些替代问题。原始问题：{question}"),
    retriever=retriever,  # 基本检索器
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.1),  # 生成问题的大模型
    include_original=True,  # 是否包含原始问题
)

results = m_retriever.invoke("关于配置接口的信息有哪些")
for doc in results:
    print(doc.page_content[:100],doc.metadata)
    print("-------")

client.close()


# 要求4 理解上述代码逻辑