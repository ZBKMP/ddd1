# langchain自定义文档加载器
# 假设有一个这样的需求，加载对应的文本信息，其中每行数据都作为一个 Document 组件

from typing import Iterator, AsyncIterator
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document


class MyTextFileLoader(BaseLoader):
    # 设置属性 file_path
    def __init__(self, file_path):
        self.file_path = file_path

    # 重写 lazy_load 方法
    def lazy_load(self) -> Iterator[Document]:
        # 实现自定义的加载逻辑 将文本文件的每行内容 转为一个Document对象
        with open(self.file_path, 'r', encoding='utf-8') as f:
            line_number = 0
            for line in f:
                line_number += 1
                # 将每行内容 生成一个Document  yield返回
                yield Document(
                    page_content=line,
                    metadata={"source": self.file_path, "line_number": line_number},
                )

    # 重写 异步版本
    async def alazy_load(self) -> AsyncIterator[Document]:
        import aiofiles  # 异步文件操作 pip install aiofiles
        async with aiofiles.open(self.file_path, encoding="utf-8") as f:
            line_number = 0
            async for line in f:
                line_number += 1
                yield Document(
                    page_content=line,
                    metadata={"score": self.file_path, "line_number": line_number}
                )


# 测试调用
loader = MyTextFileLoader("科幻短篇.txt")
docs = loader.load()
for doc in docs:
    print(doc)
