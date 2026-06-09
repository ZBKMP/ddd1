# Document组件与文档加载器的使用  TextLoader 的使用 加载Txt文件数据

from langchain_community.document_loaders import TextLoader

# 1 构建Text文档加载器
loader = TextLoader(
    file_path='电商产品数据.txt',
    encoding='utf-8',
)

# 2 执行加载  结果为 list[Document]
docs = loader.load()

# 3 单个文件 列表中仅有一个元素
print(docs[0])

# metadata={'source': '电商产品数据.txt'} 会自动包含一个元数据 文件名