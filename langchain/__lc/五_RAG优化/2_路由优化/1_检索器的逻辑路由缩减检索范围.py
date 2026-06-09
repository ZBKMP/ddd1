# 检索器的逻辑路由缩减检索范围 函数回调规范化输出 基于逻辑和语义的路由分发
# 有针对多个门类知识的向量库,根据用户的提问,分析该从哪个向量库中检索文档
# 让大模型能够生成一个存在的知识库名称

from typing import Literal  # 可选值
import dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

dotenv.load_dotenv()

# 1 让大模型根据用户的提问生成一个答案 ,答案要求必须在某几个选项中任选其一
#   with_structured_output(BaseModel类)用于设置大模型的输出结构 (本质是利用 大模型工具调用 来实现规范输出)
class StoreNameModel(BaseModel):
    store_name : Literal["python_doc","javascript_doc","java_doc"] = Field(
        description="请根据用户的提问,选择哪个最相关的知识库去检索文档来回答用户的问题"
    )
# 限定了大模型生成的内容为Pydantic.BaseModel对象,必须包含store_name字段,而且值只能是"python_doc","js_doc","java_doc"其中之一
llm = ChatOpenAI(model="gpt-4o-mini").with_structured_output(StoreNameModel)
# 测试大模型的格式化输出 输出结果为json  store_name 必须在几个可选值中任选其一
# query =" 请问如何在程序中实现遍历一个字典,再将字典转换为列表或元祖 "
# result = llm.invoke(input=query)
# print(result)
# query =" 请问如何在前端开发中实现,点击页面按钮Button,弹出alert对话框 "
# result = llm.invoke(input=query)
# print(result)
# query =" 请问在程序代码中 String类对象 有哪些方法可以使用 "
# result = llm.invoke(input=query)
# print(result)

query =" 你好 你是谁? "
result = llm.invoke(input=query)
print(result)

# 根据大模型生成出的向量库名称 去找指定的向量库 再检索文档
vector_store_name = result.store_name
print(vector_store_name)



# 要求 2 使用with_structured_output实现 :
#       要求大模型按照特定的结构输出内容: 大模型在生成内容 即回答结果answer 还包含对于结果的解释explain

