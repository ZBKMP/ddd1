# 自查询检索器实现动态元数据过滤 带有条件的问题 数据需要包含元数据 以作为查询条件
# pip install  lark==1.3.1
import dotenv
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers import SelfQueryRetriever
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_weaviate import WeaviateVectorStore  # 测试Weaviate使用自查询检索器
from langchain_community.vectorstores import Weaviate

dotenv.load_dotenv()
# 1.构建文档(包含多种元数据)列表并上传到数据库
documents = [
    Document(
        page_content="肖申克的救赎",
        metadata={"year": 1994, "rating": 9.7, "director": "弗兰克·德拉邦特"},
    ),
    Document(
        page_content="霸王别姬",
        metadata={"year": 1993, "rating": 9.6, "director": "陈凯歌"},
    ),
    Document(
        page_content="阿甘正传",
        metadata={"year": 1994, "rating": 9.5, "director": "罗伯特·泽米吉斯"},
    ),
    Document(
        page_content="泰坦尼克号",
        metadata={"year": 1997, "rating": 9.5, "director": "詹姆斯·卡梅隆"},
    ),
    Document(
        page_content="千与千寻",
        metadata={"year": 2001, "rating": 9.4, "director": "宫崎骏"},
    ),
    Document(
        page_content="星际穿越",
        metadata={"year": 2014, "rating": 9.4, "director": "克里斯托弗·诺兰"},
    ),
    Document(
        page_content="忠犬八公的故事",
        metadata={"year": 2009, "rating": 9.4, "director": "莱塞·霍尔斯道姆"},
    ),
    Document(
        page_content="三傻大闹宝莱坞",
        metadata={"year": 2009, "rating": 9.2, "director": "拉库马·希拉尼"},
    ),
    Document(
        page_content="疯狂动物城",
        metadata={"year": 2016, "rating": 9.2, "director": "拜伦·霍华德"},
    ),
    Document(
        page_content="无间道",
        metadata={"year": 2002, "rating": 9.3, "director": "刘伟强"},
    ),
]
db = PineconeVectorStore(
    index_name="llmops5",
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    namespace="dataset_movie",
    text_key="text"
)
retriever = db.as_retriever() # 基础检索器
# 数据存储仅执行一次
# ids = db.add_documents(documents, namespace='dataset_movie')
# print(ids)

# 2 声明元数据信息列表
metadata_field_info = [
    AttributeInfo(name="year", description="电影的年份", type="integer"),
    AttributeInfo(name="rating", description="电影的评分", type="float"),
    AttributeInfo(name="director", description="电影的导演", type="string"),
]

# 3 创建 SelfQueryRetriever 对象 实现将query提取出对应的filter条件
self_query_retriever = SelfQueryRetriever.from_llm(
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),
    vectorstore=db,
    document_contents="电影信息内容",  # 描述知识库的内容
    enable_limit=True,  # 是否允许控制K值
    metadata_field_info=metadata_field_info,#元数据描述信息列标
    # Pinecone方法中都需传递参数namespace表示指定的数据集
    search_kwargs={"namespace": "dataset_movie"},
)

#  4 测试结果
result = retriever.invoke("请查询2000年以后评分高于9.3的电影信息")
print(result)
print("----------------------------------------------------")
result = self_query_retriever.invoke("请查询2000年以后评分高于9.3的电影信息")
print(result)

# 要求 5: 切换不同的向量库 测试自查询检索结果  是否都能生成正确的filter条件