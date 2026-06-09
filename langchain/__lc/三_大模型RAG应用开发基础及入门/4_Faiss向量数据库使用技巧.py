# Faiss向量数据库的配置与使用
# pip install faiss-cpu==1.12.0
import dotenv
from jsonschema.exceptions import relevance
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

dotenv.load_dotenv()
# 1 构建嵌入模型
embedding = OpenAIEmbeddings(model='text-embedding-3-small')

# 2 构建需要存储的文本列表
poem = [
    "我养了一只猫，叫笨笨",
    "它的瞳孔是两枚新月",
    "总在黄昏时缓缓升起",
    "肉垫踩过散落的诗稿",
    "留下梅花状的空白",
    "它把呼噜声藏在毛毯褶皱里",
    "像台老旧的收音机",
    "调频着温暖的杂音",
    "当阳光斜照窗台",
    "笨笨就碎成一滩金箔",
    "唯有尾巴尖保持着清醒",
    "在梦与现实的边界",
    "画下流动的逗号",
    "我尝试用逗猫棒丈量时光",
    "它却用哈欠截断计数",
    "瓷碗里牛奶的涟漪",
    "荡开三百六十五个晨昏",
    "某天书架倒塌的巨响中",
    "笨笨叼着半页日记",
    "端坐如参禅的僧侣",
    "——原来它早已将我的生活",
    "悄悄排列成鱼骨形的密码",
]

# 3 以文本列表为数据源 存储到Faiss向量库
# db = FAISS.from_texts(
#     texts=poem,
#     embedding=embedding,
# )
# 查看生成的向量数据的ID 每存一条向量信息会生成一个UUID,查看向量库中id的个数
# print(db.index.ntotal)

# 4 使用向量库进行相似性搜索 提取相似相最高的前k条数据 默认4
# document_list =db.similarity_search(query="一只叫笨笨的猫",k=5)
# for document in document_list:
#     print(document)

# 5 FAISS 相似性搜索 得到相似性最高的前几条文档 并附带欧几里得距离值 距离越小越相似
# document_list = db.similarity_search_with_score(query="一只叫笨笨的猫",k=5)
# for doc,score  in document_list:
#     print(doc, score)

# 6 FAISS 代相似性得分的相似性搜索 ,除了文档内容外 还附带相似性得分 越接近1 越相似
# document_list = db.similarity_search_with_relevance_scores(query="一只叫笨笨的猫",k=5)
# for doc,score  in document_list:
#     print(doc, score)

# FAISS 缓存库  运行结束之后 数据就没有了

#################################################################################

# 1 保存文本数据page_content的同时还给每个向量数据增加额外数据 元数据 Metadata
#   文本列表的长度 要和 元数据列表的长度要一至
meta_data: list = [
    {"page": 1,"other":"message"}, {"page": 2}, {"page": 3}, {"page": 4}, {"page": 5},
    {"page": 6}, {"page": 7}, {"page": 8}, {"page": 9}, {"page": 10},
    {"page": 11}, {"page": 12}, {"page": 13}, {"page": 14}, {"page": 15},
    {"page": 16}, {"page": 17}, {"page": 18}, {"page": 19}, {"page": 20},
    {"page": 21}, {"page": 22},
]

# 2 FAISS数据的持久化 保存到本地文件
# db = FAISS.from_texts(
#     texts=poem,
#     metadatas=meta_data, # 为每个文档增加元数据
#     embedding=embedding,
# )
# db.save_local('./faiss_vector_store/') # 保存到本地文件
# 保存到本地之后  确保同样的数据仅保存一次  保存的代码只执行一次


# 3 从本地文件中加载已经持久化的向量数据
db = FAISS.load_local(
    folder_path='./faiss_vector_store/',  # 读取指定目录的向量数据
    embeddings=embedding,
    allow_dangerous_deserialization=True,
    relevance_score_fn=lambda distance: 1.0 / (1.0 + distance),  # 设置相似性得分算法
)
# 查看保存的数据量
print(db.index.ntotal)


# 执行相似性搜索  filter 同时以元数据作为过滤条件 进行过滤检索
document_list = db.similarity_search_with_relevance_scores(
    query="一只叫笨笨的猫",
    k=5,
    filter = lambda x:x["page"] >= 10 # FAISS库中元数据搜索的语法
)


for doc,score  in document_list:
    print(doc, score)


