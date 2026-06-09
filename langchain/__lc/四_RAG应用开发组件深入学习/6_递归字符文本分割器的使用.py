# BaseDocumentTransformer组件:
# 递归字符文本分割器  (中文场景下的递归分割)  衍生代码分割器

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# A 递归字符文本分割器 默认分隔符列表 ["\n\n","\n"," ",""] (设计思路为面向英文文档的编写习惯)
# 先按第一个分隔符分割,过大则再用后续的分隔符.如果过小会合并

# 加载文档
loader = UnstructuredMarkdownLoader("项目API文档.md")
docs = loader.load()

# 创建递归字符文本分割器

# 适用于中文的分隔符列表,包含了正则表达式的内容,分割器需要设置对应的参数
separators = [
    "\n\n", # 两次换行
    "\n",  # 一次换行
    "。|！|？", # 正则 中文句号 感叹号 问号
    "\.\s|\!\s|\?\s",  #正则 英文标点符号后面通常需要加空格
    "；|;\s", # 正则 中英文的分段
    "，|,\s", # 正则 中英文逗号
    " ",
    ""
]
splitter = RecursiveCharacterTextSplitter(
    #separators= ["\n\n", "\n", " ", ""], # 默认的分割符列表 契合英文文档的书写习惯,以空格去分割内容
    separators= separators, # 使用适合中文语义的分割符列表
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
    is_separator_regex=True,# 在分割符中是否支持正则表达式
)
#  测试递归分割效果
chunks = splitter.split_documents(documents=docs)
for chunk in chunks:
    print(f'chunk_size:{len(chunk.page_content)},metadata:{chunk.metadata}')
print(f'total_size:{len(chunks)}')

print("*"*50)
######################################################################################

# B 衍生--代码分割器
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
# 加载文档
loader = UnstructuredFileLoader("demo.py")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=300,
    chunk_overlap=50,
    add_start_index=True,
)
# 文档分割
chunks = splitter.split_documents(documents=docs)
for chunk in chunks:
    print(f'chunk_size:{len(chunk.page_content)},metadata:{chunk.metadata}')
print(f'total_size:{len(chunks)}')
# 查看各类编程语言的分割符列表
separators = RecursiveCharacterTextSplitter.get_separators_for_language(
    language=Language.JAVA,
)
print(separators)
