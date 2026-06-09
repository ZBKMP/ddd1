# 使用EnsembleRetriever 混合多种检索策略

import dotenv
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

dotenv.load_dotenv()

# 1.创建文档列表
documents = [
    Document(page_content="笨笨是一只很喜欢睡觉的猫咪", metadata={"page": 1}),
    Document(page_content="我喜欢在夜晚听音乐，这让我感到放松。", metadata={"page": 2}),
    Document(page_content="猫咪在窗台上打盹，看起来非常可爱。", metadata={"page": 3}),
    Document(page_content="学习新技能是每个人都应该追求的目标。", metadata={"page": 4}),
    Document(page_content="我最喜欢的食物是意大利面，尤其是番茄酱的那种。", metadata={"page": 5}),
    Document(page_content="昨晚我做了一个奇怪的梦，梦见自己在太空飞行。", metadata={"page": 6}),
    Document(page_content="我的手机突然关机了，让我有些焦虑。", metadata={"page": 7}),
    Document(page_content="阅读是我每天都会做的事情，我觉得很充实。", metadata={"page": 8}),
    Document(page_content="他们一起计划了一次周末的野餐，希望天气能好。", metadata={"page": 9}),
    Document(page_content="我的狗喜欢追逐球，看起来非常开心。", metadata={"page": 10}),
]

# 2 构建BM25关键词检索器
# pip install rand_bm25==0.2.2
# BM25Retriever.from_documents(documents) 直接将文档列表加载为Retriever对象
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 4

# 3 用同样的文档内容创建FAISS向量库
faiss_db = FAISS.from_documents(
    documents=documents,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small")
)
retriever = faiss_db.as_retriever(
    search_kwargs = {
        "k":4
    }
)

# 4 以多个不同类型检索器为参数 创建混合检索器
ensemble_retriever = EnsembleRetriever(
    retrievers = [bm25_retriever, retriever],
    weights = [0.5, 0.5], #  设置每个检索器的比例
)


# 5 执行检索
results = ensemble_retriever.invoke(
    input ="你养了哪些宠物"
)
for result in results:
    print(result)


# 要求 1  实现多种检索器: 1生成多个问题的RRF融合检索器,2少量提示模板检索器,3HyDE混合检索器
#        将多个检索器使用EnsembleRetriever混合多个检索器的结果 综合出最终结果





'''
面试题总结

1、除了RRF算法你们还了解其他的算法吗？常数为什么取60？你们做过调优吗？
2、你说了解到 查询转换阶段 6种策略，能分别说说吗？
3、什么是多查询重写策略？
4、什么是多结果融合策略？
5、什么是Stepback回退回答策略？
6、什么是doc-doc 对称检索？
7、什么是Hyde混合检索？
8、什么是混合检索器
'''