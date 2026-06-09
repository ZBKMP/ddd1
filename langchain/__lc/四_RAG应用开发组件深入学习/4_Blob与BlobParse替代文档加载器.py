# Blob与BlobParse替代文档加载器

from typing import Iterator
from langchain_community.document_loaders.parsers.txt import TextParser
from langchain_core.document_loaders import Blob
from langchain_core.document_loaders.base import BaseBlobParser
from langchain_core.documents import Document
from langchain_community.document_loaders.blob_loaders import FileSystemBlobLoader
from langchain_community.document_loaders.generic import GenericLoader


# 1  获取数据的逻辑已经有了 只需要定义解析过程即可
#    假设有需求:自定义解析器 用于将传入的文本二进制数据的每一行解析成Document对象
class CustomParser(BaseBlobParser):  # 必须继承于BaseBlobParser
    # 重写抽象方法 lazy_parse
    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        # blob:Blob 表示使用工具将文件内容加载成的二进制数据
        line_number = 0
        # 将blob转为缓冲字节流数据 会生成每行数据构成的生成器
        with blob.as_bytes_io() as f:
            for line in f:
                line_number += 1
                yield Document(
                    page_content=line,
                    metadata={"source": blob.source, "line_number": line_number},
                )


# 2 加载文件内容为二进制数据
blob = Blob.from_path("电商产品数据.txt") # txt md

# 3 测试使用 Blob+自定义的解析器 读取文本文件
# parser = CustomParser()
# docs = list(parser.lazy_parse(blob=blob))
#
# for doc in docs:
#     print(doc)

##################################################################

# 4 还可以直接从内存中加载临时数据
# blob = Blob(data='hello world1\r\nhello world2\r\nhello world3\r\n')
# parser = TextParser() # TextParser 文本解析器
# documents = parser.parse(blob)
# print(documents)

####################################################################

# 5 文件系统二进制加载器 加载指定文件夹下的特定文件 加载结果为Blob 可以进一步解析为Document
# 从当前目录下 加载所有数据 glob指定特定文件  txt/md
'''
loader = FileSystemBlobLoader(".",glob="*.md",show_progress=True)
parser = CustomParser()
for blob in loader.yield_blobs():# 遍历目录下所有适合文件读取成的Blob数据
    print("*"*50)
    docs = list(parser.lazy_parse(blob))
    for doc in docs:
        print(doc)
'''

####################################################################

# 6 Blob通用加载器 由BlobLoader与BlobParser组合而成,实现加载与解析两个步骤的合并
g_loader = GenericLoader.from_filesystem(
    path=".",
    glob="*.md",
    show_progress=True,
    #parser="default", # 默认解析器仅支持文本文件
    parser=CustomParser(), # 使用自定义的解析器 可以支持md文件
)

docs = g_loader.lazy_load()
for doc in docs:
    print(doc)
    print("-" * 50)