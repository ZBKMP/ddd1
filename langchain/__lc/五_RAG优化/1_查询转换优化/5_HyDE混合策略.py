# 混合策略实现doc-doc对称检索 HyDE混合策略 局限性与失败案例

from typing import List
import dotenv
import weaviate
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()

# 1 自定义HyDE混合策略检索器
class HyDERetriever(BaseRetriever):
    retriever: BaseRetriever
    llm: BaseLanguageModel

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        # 编辑一个链 通过现有问题生成一篇文章 以文章作为检索条件去检索文档
        prompt = ChatPromptTemplate.from_template(
            "请根据提问写一篇相关文章来回答这个问题。\n"
            "问题: {question}\n"
            "文章: "
        )
        chain = (
                {"question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
                | (lambda x: print("生成的文章:", x) or x)
                | self.retriever
        )
        return chain.invoke(query)


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
# 创建回退问题检索器
hyde_retriever = HyDERetriever(
    retriever=retriever,
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),
)
result = hyde_retriever.invoke("关于配置接口的信息有哪些")
for doc in result:
    print(doc.page_content[:100],doc.metadata)
    print("-"*50)

client.close()


