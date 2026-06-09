# 自定义文档分割器
# 实现一个根据传递的分隔符实现对文档进行片段划分，并且将分割出来的文档片段提取出N个关键词的分割器

# 安装分词包： pip install jieba==0.42.1
from typing import List
import jieba.analyse # 分词 提取关键词
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import TextSplitter

# 自定义文档分割器
class CustomTextSplitter(TextSplitter):

    def __init__(self,seperator:str,top_k:int=10,**kwargs):
        super().__init__(**kwargs)
        self.seperator = seperator # 分割符
        self.top_k = top_k # 从分割结果中提取关键词的上限

    # 重写方法  将原文本内容 切割成多个片段
    def split_text(self, text: str) -> list[str]:
        texts = text.split(self.seperator)
        text_keywords= []
        for text in texts:
            # 从text中提取出top_k个关键词
            keywords=jieba.analyse.extract_tags(
                sentence = text,
                topK = self.top_k,
            )
            text_keywords.append(keywords)
        return [ ",".join(keywords) for keywords in text_keywords]


# 加载文档 测试关键词提取
loader = UnstructuredFileLoader("科幻短篇.txt")
docs = loader.load()
splitter = CustomTextSplitter(seperator="\n\n",top_k=10)
docs = splitter.split_documents(docs)
for doc in docs:
    print(doc)




# 要求 1: 使用不同的文档加载器 将内容生成为Document(一个文件只能生成一个文档)
# 调用VectorStore的 add_documents方法存入向量库,在一个库中存入多篇文档生成的向量数据
# 再使用包含RAG检索的链测试文档相似性检索的效果

# 要求 2 ：实现一个chat-to-pdf 的功能
# 在指定的文件夹下面放入PDF，用户能够向AI询问PDF相关的内容
# 先实现PDF文档加载 切割 向量存储
# 再实现AI生成时先从指定向量库中检索知识

'''
面试题
1、你们项目中既然用到了文档加载器，你了解那些加载器？
2、你们在做知识库的时候使用到了分片是怎么做的？
3、你讲到知识库的分词，这是怎么做的？
'''