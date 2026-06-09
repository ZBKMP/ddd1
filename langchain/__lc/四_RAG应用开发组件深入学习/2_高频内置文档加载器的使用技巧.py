# langchain内置文档加载器使用技巧 MarkDown Office URL File
# 需要连接外网 下载nltk工具包

# 1 MarkDown文档加载器
# pip install unstructured==0.10.30
# pip install markdown==3.9
'''
from langchain_community.document_loaders import UnstructuredMarkdownLoader
loader = UnstructuredMarkdownLoader(
    file_path='项目API文档.md',
    mode='single',# 整个文件加载为一个文档
)
doc = loader.load()
print(doc[0]) # 元数据 source
'''

# 2 Office / WPS
'''
Excel: pip install openpyxl pandas  msoffcrypto-tool
PPT: pip install python-magic python-pptx
Word: pip install python-docx
'''
from langchain_community.document_loaders import (
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)

# 2.1 xlsx
'''
loader = UnstructuredExcelLoader(
    file_path='员工考勤表.xlsx',
    mode='single', # single/elements
)
doc = loader.load()
print(doc[0])
'''

# 2.2 ppt 分页加载
'''
loader = UnstructuredPowerPointLoader(
    file_path='章节介绍.pptx',
    mode='elements',# single/elements
)
docs = loader.load()
for doc in docs:
    print(doc)
'''

# 2.3 word
'''
loader = UnstructuredWordDocumentLoader(
    file_path='喵喵.docx',
    mode='single',
)
docs = loader.load()
print(docs[0])
'''

# 3 URL
'''
from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader(
    web_path='https://movie.douban.com/',
)
docs = loader.load()
print(docs[0])
# metadata={'source': 'https://movie.douban.com/', 'title': '\n        豆瓣电影\n', 'description': '豆瓣电影提供最新的电影介绍及评论包括上映影片的影讯查询及购票服务。你可以记录想看、在看和看过的电影电视剧，顺便打分、写影评。根据你的口味，豆瓣电影会推荐好电影给你。', 'language': 'zh-CN'}
'''

# 4 通用文档加载器 适用于未知的文档文件类型
'''
from langchain_community.document_loaders import UnstructuredFileLoader
loader = UnstructuredFileLoader(
    file_path=['员工考勤表.xlsx','电商产品数据.txt'],
    mode='single',
)
docs = loader.load()
for doc in docs:
    print("-------------------------")
    print(doc)
'''

# 5 PDF文档加载器
'''
* 安装模块:支持加载pdf文件:
        pip install "pdfminer.six==20221105"
        pip install "unstructured==0.10.30"
        pip install pi_heif   
        pip install unstructured_inference
        pip install pdf2image
        pip install unstructured_pytesseract
'''
from langchain_community.document_loaders import UnstructuredPDFLoader

loader = UnstructuredPDFLoader(
    file_path='LLm大语言模型.pdf',
    mode='single',
)
docs = loader.load()
print(docs[0])
