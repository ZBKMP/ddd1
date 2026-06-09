# 内置的检索器与自定义检索器技巧
# langchain内置的检索器大部分都是面向国外的平台或web服务,大多数也是可运行组件
# 国内项目经常需要使用自定义检索器,去定义连接国内的网络数据资源,如百度,豆瓣等等

from typing import List

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

# 继承于检索器父类
class CustomRetriever(BaseRetriever):
    """自定义检索器"""
    # 模拟存储数据的文档列表 实际使用时可以先将爬取到的文档数据传入
    documents: list[Document]
    # k值参数 返回的记录条数
    k: int
    # pydantic.BaseModel

    # 重写抽象方法
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        """根据传入的query，获取相关联的文档列表"""
        matching_docs = []
        for doc in self.documents:
            # 到达K条数据则直接返回
            if len(matching_docs) >= self.k:
                return matching_docs
            # 如果要搜索的内容包含在某个文档的内容里 添加该文档到匹配的文档列表
            if query.lower() in doc.page_content.lower():
                matching_docs.append(doc)
        return matching_docs



# 测试自定义检索器
# 1.定义预设文档
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

# 2 创建检索器
retriever = CustomRetriever(documents=documents,k=4)

# 3 执行检索器
retriever_documents = retriever.invoke(input="我")
for doc in retriever_documents:
    print(doc.page_content,doc.metadata)
