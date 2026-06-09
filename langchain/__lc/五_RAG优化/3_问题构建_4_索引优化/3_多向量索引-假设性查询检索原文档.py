# 多向量索引-假设性查询检索原文档
'''
假设性査询检索
是利用 LLM 对切块后的文档生成多个 假设性标题，在向量数据库中存储 假设性标题 文档块，
使用检索到的数据查找 原始文档.
'''
from typing import List

import dotenv
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from scipy.signal import qspline1d

dotenv.load_dotenv()

#1 假设性问题生成链
# 要求大模型根据一个文档片段 生成3个假设性问题
class HypotheticalQuestions(BaseModel):
    questions :  List[str] = Field(
        min_length=3,
        max_length=3,
        description="假设性问题列表,类型为字符串列表"
    )

# 提示模板 由切片后的文档 生成3个假设性问题 用户的输入在向量库中检索出的是3个假设性问题
prompt = ChatPromptTemplate.from_template(
    "依据原文档生成3个假设性的问题.这些问题可以用于回答以下文档内容:\n\n{doc}"
)

# 规范大模型输出
llm = ChatOpenAI(model="gpt-4o-mini",temperature=0).with_structured_output(HypotheticalQuestions)

# 定义链
chain = (
    {"doc":lambda  x: x.page_content}
    | prompt
    | llm
)

# 测试假设性问题生成
questions = chain.invoke(
    Document(page_content="你是一个乐于助人的AI助理，可以针对一个输入问题生成多个相关的子问题")
)
print(questions)

#要求 1 : 对比案例 在切割出文档列表之后 以批处理的方式将文档列表生成出BaseModel对象,其中包含list[str]属性,
#              同时给每个文档的假设性列表也生成对应唯一标识 doc_id
#              假设性问题存储于向量库(存3个/合并成一个),同一个文档的三个假设性问题使用同一个唯一标识 doc_id作为元数据
'''
                      q1
            doc       q2      metadata : doc_id
                      q3


                      query
'''