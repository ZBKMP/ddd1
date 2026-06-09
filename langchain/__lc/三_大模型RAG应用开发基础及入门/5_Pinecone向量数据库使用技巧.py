# Pinecone向量数(云端)据库的配置与使用
# pip install pinecone==7.0.1
# pip install langchain_pinecone==0.2.13
# 需要模块 readline 报错后点击连接安装

import dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

dotenv.load_dotenv()
# 嵌入模型
embeddings = OpenAIEmbeddings(model='text-embedding-3-small')
# 加入向量库的数据
poem = [
    "我养了一只猫，叫笨笨",
    "它的瞳孔是两枚新月",
    "总在黄昏时缓缓升起",
    "肉垫踩过散落的诗稿",
    "留下梅花状的空白",
]
# 元数据列表 仅包含page一项元数据
meta_datas: list = [
    {"page": 1},
    {"page": 2, "account_id": 1},  # 设置多个元数据 以便条件测试
    {"page": 3},
    {"page": 4},
    {"page": 5},
]
# 创建向量库
db = PineconeVectorStore(
    embedding=embeddings,
    index_name="llmops5",  # pinecone中的库名 index
    namespace='dataset_cat',  # 每个库index下可以有多个namespace(类比SQL中的表)
)

# 添加数据
# db.add_texts(
#     texts=poem,
#     metadatas=meta_datas,
#     namespace='dataset_cat',
# )
# 数据保存仅执行一次 否则会包含重复信息


# 执行相似性搜索 返回list[Document]
query = "我养了一只猫，叫笨笨"
# 越接近1相似度越高
result = db.similarity_search_with_score(
    query=query,
    namespace='dataset_cat',  # 确定从哪个namespace去进行检索哦
    # filter={"page": {"$lte": 3}},  # 参考pinecone--docs
    filter={"$or":[{"page":1},{"account_id":1}]}, # and/or  如果是eq可以简写,直接用字典表示条件的值
)

print(result)

# 要求 1  : 自行编辑文档数据于元数据 使用pinecone/faiss向量库存储
# 检索数据:  db.similarity_search db.similarity_search_with_score db.similarity_search_with_relevance_scores
# 使用filter结合元数据作为过滤条件  大于 小于 大于等于 小于等于  不等于  in  not in   and/or


'''
使用向量数据库实现长期记忆功能。
实现流程如下:
1、将用户的问题，向量化
2、通过向量化匹配数据库里面跟本次对话最相似的对话。
3、将匹配到的对话，加入到聊天对话中
4、对话结束 将AI 对话和人类对话存储到向量数据库中


conversation_id 作为元数据  human_input, ai_response合并成一个文本生成向量 : Human:xxx, AI:xxx 
以当前用户提问 在向量库中检索出与该提问语义近似的聊天记录 
'''


