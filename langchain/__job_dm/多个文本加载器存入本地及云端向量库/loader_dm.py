import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, UnstructuredExcelLoader
from langchain_weaviate.vectorstores import WeaviateVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
import weaviate
from weaviate.auth import AuthApiKey

# 1. 初始化配置
load_dotenv()
print("正在初始化 Embedding 模型...")
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

# 2. 文档加载阶段
all_documents = []
base_path = "/__job_dm/"

# --- 加载 TXT ---
txt_path = os.path.join(base_path, "test.txt")
if os.path.exists(txt_path):
    all_documents.extend(TextLoader(txt_path, encoding="utf-8").load())
    print(f" 已加载 TXT: {txt_path}")

# --- 加载 Excel---
xlsx_path = os.path.join(base_path, "text.xlsx")
if os.path.exists(xlsx_path):
    try:
        #  Excel 加载器
        loader_xlsx = UnstructuredExcelLoader(xlsx_path, mode="elements")
        all_documents.extend(loader_xlsx.load())
        print(f" 已加载 Excel: {xlsx_path}")
    except Exception as e:
        print(f" Excel 加载失败: {e}")

# 3. 连接并存入 Weaviate
if not all_documents:
    print("错误：未发现任何可加载的文档，请检查路径。")
else:
    print(f"正在连接 Weaviate 并存入 {len(all_documents)} 个文档...")
    client = weaviate.connect_to_wcs(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY"))
    )

    try:
        # 将多个文档一次性存入向量库
        vectorstore = WeaviateVectorStore.from_documents(
            documents=all_documents,
            embedding=embeddings,
            client=client,
            index_name="Lab_Knowledge_Base",
            text_key="text"
        )
        print(" 数据同步成功！请前往控制台查看。")

        # 4. 相似性检索测试
        query = "请根据文档内容回答相关问题"
        results = vectorstore.similarity_search(query, k=2)

        print("\n--- 检索结果 ---")
        for doc in results:
            source = doc.metadata.get('source', '未知')
            print(f"【来源: {source}】 内容: {doc.page_content[:100]}...")

    finally:
        client.close()
        print("Weaviate 连接已关闭。")