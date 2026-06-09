# BaseDocumentTransformer组件:字符分割器基础使用技巧
# pip install  langchain-text-splitters==0.3.11

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import CharacterTextSplitter  # 文本分割器

# 1 加载文档
loader = UnstructuredMarkdownLoader(
    file_path="项目API资料.md",
)
docs = loader.load()

# 2 构建文本分割器
splitter = CharacterTextSplitter(
    separator="\n\n",  # 切割文件时使用的分割符
    chunk_size=500,  # 先按照分割符进行分割,在将分割的结果合并,合并长度不能超过该size
    chunk_overlap=50,  # 分割结果的每个片段 前后重叠的长度,以尽量保持文档内容的完整性
    add_start_index=True,  # 在分割出的每个Document中保留该切块的起点索引,作为一个元数据
)

# 3 实现文档分割
chunks = splitter.split_documents(documents=docs)
for chunk in chunks:
    #print(chunk)
    print(f'chunk_size:{len(chunk.page_content)},metadata:{chunk.metadata}')
    print("*"*50)


'''
使用 characterTextsplitter 进行分割时，虽然传递了 chunk_size 为500，但是仍然没法确保分割出
  来的文档一直保持在这个范围内，这是因为在底层 characterTextsplitter 是先按照分割符号拆分整个文档，
  然后循环遍历拆分得到的列表，将每个列表逐个相加，直到最接近 chunk_size 窗口大小时则完成一个 
  Document 的组装。
  但是如果基于分割符号得到的文本，本身长度已经超过了chunk_size，则会直接进行警告，并且将对应的文本
  单独变成一个块。

  核心方法：split_text
'''
