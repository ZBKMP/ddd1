# 语义文档分割器与其他内容分割器
# pip install  langchain_experimental==0.3.4
import dotenv
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_experimental.text_splitter import SemanticChunker  # 语义相似分割器
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter, HTMLHeaderTextSplitter

dotenv.load_dotenv()

# 1 语义文档分割器:
'''
loader = UnstructuredFileLoader(file_path="科幻短篇.txt")
docs = loader.load()
# 创建分割器
splitter = SemanticChunker(
    embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),# 使用嵌入模型进行语义分析
    number_of_chunks=10, # 设置需要分割的结果数量
    add_start_index=True,
    sentence_split_regex=r"(?<=[。？！.?!])"  # 句子切割正则 以中英文的点,问号,感叹号作为分隔符
)
# 查看分割结果
chunks = splitter.split_documents(docs)
for chunk in chunks:
    print(chunk.page_content)
    print("--------------------------------------")
'''

# 2 HTML文档分割器
html_string = """
<!DOCTYPE html>
<html>
<body>
    <div>
        <h1>标题1</h1>
        <p>关于标题1的一些介绍文本。</p>
        <div>
            <h2>子标题1</h2>
            <p>关于子标题1的一些介绍文本。</p>
                <h3>子子标题1</h3>
                <p>关于子子标题1的一些文本。</p>
                <h3>子子标题2</h3>
                <p>关于子子标题2的一些文本。</p>
        </div>
        <div>
            <h2>子标题2</h2>
            <p>关于子标题2的一些文本。</p>
        </div>
        
        
    </div>
</body>
</html>
"""

'''
# 标识要分割的标签以及标题
headers_to_split_on = [
    ("h1","一级标题"),
    ("h2","二级标题"),
    ("h3","三级标题")
]
# 创建HTML标签文本分割器
splitter = HTMLHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
)
chunks = splitter.split_text(html_string)
for chunk in chunks:
    print(chunk.page_content)
    print("------------------------------------")
'''

# 3  JSON 文档分割器  (深度优先方式切割)
import json
import requests
from langchain_text_splitters import RecursiveJsonSplitter # 递归JSON分割器
url = "https://api.smith.langchain.com/openapi.json"
json_data = requests.get(url).json() #响应结果为JSON对象或这是JSON对象组成的列表,程序中会读取为字典或这是字典列表
print(len(json.dumps(json_data)))

# JSON文档分割器
splitter = RecursiveJsonSplitter(
    max_chunk_size=30000
)
# 分割出来的结果还是JSON(dict) 需要转换为Document
json_chunks = splitter.split_json(json_data)
document_chunks = splitter.create_documents(json_chunks)

total = 0
for chunk in document_chunks:
    print(f"{len(chunk.page_content)} , {chunk.metadata}")
    total  += len(chunk.page_content)
print(total)
