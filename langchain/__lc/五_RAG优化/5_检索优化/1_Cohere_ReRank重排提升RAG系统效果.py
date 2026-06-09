# ReRank重排序  Cohere重排序:
# pip install langchain-cohere==0.4.6
# pip install httpx-sse==0.4.1
import dotenv
import weaviate
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from langchain_openai import OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
dotenv.load_dotenv()

# 1.创建向量数据库与重排组件
embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

client = weaviate.connect_to_local(
    host="192.168.172.129",
    port=8080,
)

db = WeaviateVectorStore(
    client=client,
    embedding=embedding,
    index_name='collection_project_1',  # 数据集名称
    text_key='text',  # 文本内容的key名
)


# test_docs = [
#     Document(page_content="LLMOps 配置核心：环境变量管理。必须确保 OPENAI_API_KEY 和 API_BASE 在生产环境中通过加密方式注入，避免硬编码。"),
#     Document(page_content="模型参数配置：在 LLMOps 流程中，Temperature 和 Top_P 的设置直接影响生成质量。通常 RAG 场景建议 Temperature 设为 0。"),
#     Document(page_content="计算资源配置：Agent 运行环境需要配置合适的显存（VRAM）和内存。对于本地部署的 BGE-M3 模型，建议预留至少 2GB 内存。"),
#     Document(page_content="提示词工程配置：LLMOps 平台通常支持 Prompt 的版本管理。配置中应包含 Prompt ID，以便在 A/B 测试中快速切换。"),
#     Document(page_content="监控与指标配置：应为 LLMOps 系统配置 Prometheus 或类似工具，监控 Token 消耗速度、响应延迟（Latency）以及请求成功率。"),
#     Document(page_content="网络代理配置：在受限网络环境下运行 Agent，需配置 HTTP_PROXY 环境变量，并确保 SSL 证书校验路径正确。"),
#     Document(page_content="数据库连接配置：向量数据库（如 Weaviate）的连接 URL 和端口（8080/50051）必须在 config 文件中明确定义，并配置连接池。"),
#     Document(page_content="安全审计配置：LLMOps 需要配置内容审查过滤器（Content Moderation），防止敏感信息泄露或有害内容输出。")
# ]
#
#
# db.add_documents(test_docs)
# print(f"成功入库 {len(test_docs)} 条 LLMOps 相关配置数据！")
base_retriever = db.as_retriever(search_type='mmr')

# 2 rerank模型  v1:rerank-multilingual-v3.0
rerank = CohereRerank(model="rerank-v3.5")  # v2

# 3  构建压缩检索器 配置重排序rerank模型实现 文档列表的去重以及顺序重排
compress_retriever = ContextualCompressionRetriever(
    base_retriever=base_retriever,  #基础检索器
    base_compressor=rerank,  # 重排序模型
)

# 4 测试重排压缩效果
results = base_retriever.invoke("关于LLMOPS中的应为配置的信息有哪些")
for result  in results:
    print(result)
    print("-----------------")
print("*"*50)
results = compress_retriever.invoke("关于LLMOPS中的应为配置的信息有哪些")
for result  in results:
    print(result)
    print("-----------------")


client.close()


# 要求 2 实现chat-to-sql 功能
#       用户根据数据库的建表语句，使用大模型将用户的问题转换成sql 并且执行大模型生成的sql
#       将建表的语句描述在提示模板内




'''
面试题
那你了解路由的优化策略吗？
那你了解问题构建的优化策略吗？
那你了解索引构建的优化策略吗？
那你了解检索器的优化策略吗？
'''