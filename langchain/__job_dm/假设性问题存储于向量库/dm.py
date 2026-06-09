import uuid, os, dotenv, time
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_weaviate import WeaviateVectorStore
from langchain.storage import InMemoryStore
from langchain.retrievers.multi_vector import MultiVectorRetriever
import weaviate

# 0. 环境加载
dotenv.load_dotenv()

# 1. 动态 Index 名字
INDEX_NAME = f"JokerRAG_{int(time.time())}"
ID_KEY = "parent_doc_id"
WEAVIATE_URL = "192.168.172.129"


# 2. 结构化定义
class HypotheticalQuestions(BaseModel):
    questions: List[str] = Field(description="生成的3个假设性问题")


# 3. 初始化 LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    model_kwargs={"response_format": {"type": "json_object"}}
).with_structured_output(HypotheticalQuestions)

prompt = ChatPromptTemplate.from_template("作为哥谭专家，为这段独白生成3个短问题用于档案检索。输出JSON。\n内容: {doc}")
chain = ({"doc": lambda x: x.page_content} | prompt | llm)

# 4. 原始数据
raw_docs = [
    Document(page_content="哥谭市需要一场彻底的混乱来醒悟，现在的秩序只是一个笑话。"),
    Document(page_content="即使站在那儿被嘲笑，也好过站在那儿被忽视。"),
    Document(page_content="我曾经认为我的生活是一场悲剧，但现在我意识到，它是一场喜剧。")
]

# 5. 连接与初始化
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
client = weaviate.connect_to_local(host=WEAVIATE_URL, port=8080)

try:
    vectorstore = WeaviateVectorStore(client=client, index_name=INDEX_NAME, text_key="text", embedding=embeddings)
    store = InMemoryStore()

    retriever = MultiVectorRetriever(vectorstore=vectorstore, docstore=store, id_key=ID_KEY)

    # 生成并打印 Q1, Q2, Q3
    print(f" 正在为 {len(raw_docs)} 段独白生成假设性问题...\n")
    doc_ids = [str(uuid.uuid4()) for _ in raw_docs]
    hypo_outputs = chain.batch(raw_docs)

    summary_docs = []
    for i, output in enumerate(hypo_outputs):
        parent_id = doc_ids[i]
        print(f"原文档: {raw_docs[i].page_content}")
        for j, q in enumerate(output.questions):
            print(f"   └── q{j + 1}: {q}")
            summary_docs.append(Document(page_content=q, metadata={ID_KEY: parent_id}))
        print("-" * 60)

    #  入库
    store.mset(list(zip(doc_ids, raw_docs)))
    vectorstore.add_documents(summary_docs)
    time.sleep(3)

    # 8. 提问与影子匹配打印
    query = "为什么说现在的社会秩序很可笑？"
    print(f"\n 提问: {query}")

    # 获取影子文档
    sub_docs = vectorstore.as_retriever(search_kwargs={'k': 3}).invoke(query)

    print(f" 向量库匹配到的最接近的问题 :")
    retrieved_ids = []
    for i, s_doc in enumerate(sub_docs):

        p_id_str = str(s_doc.metadata.get(ID_KEY))
        print(f"   {i + 1}. {s_doc.page_content} (parent_id: {p_id_str[:8]}...)")
        if p_id_str not in retrieved_ids:
            retrieved_ids.append(p_id_str)

    # 9. 还原本体
    print(f"\n 原始独白 (本体):")
    actual_docs = store.mget(retrieved_ids)

    found = False
    for doc in actual_docs:
        if doc:
            print(f" {doc.page_content}")
            found = True

finally:
    client.close()
