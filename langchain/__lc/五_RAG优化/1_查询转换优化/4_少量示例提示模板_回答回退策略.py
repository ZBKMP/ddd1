# step_back 回答回退策略扩大检索范围
from typing import List

# 少量示例提示模板
import dotenv
import weaviate
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()
# A 少量示例提示模板
# 1.构建示例模板与示例的内容
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{question}"),
        ("ai", "{answer}")
    ]
)
# 2.编辑示例列表
examples = [
    {"question": "请帮我计算2+2等于多少", "answer": "4"},
    {"question": "请帮我计算10+20等于多少", "answer": "30"},
    {"question": "请帮我计算2*2等于多少", "answer": "4"},
]
# 3.构建少量示例提示模板
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples
)
# print(few_shot_prompt.format())

# 4.将生成的少量示例提示模板 融合到提问提示模板中
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个可以执行数学计算的AI助手,必须按以下的少量示例进行回答:"),
        few_shot_prompt,
        ("human", "{question}")
    ]
)
# print(prompt.format(question="请计算23*34的结果是多少"))

# 5 在链中使用上述模板
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | StrOutputParser()
result = chain.invoke({"question": "请计算23*34的结果是多少"})
print(result)

print("*" * 50)


# B step_back 回答回退策略 把原本小范围的问题,回退到范围更大更容易回答的问题
class StepBackRetriever(BaseRetriever):
    retriever: BaseRetriever
    llm: BaseLanguageModel

    # 重写方法
    def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        # 利用少量示例提示模板 将原本的问题生成回退问题
        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{question}"),
                ("ai", "{answer}")
            ]
        )
        examples = [
            {"question": "博睿智启上有关于AI应用开发的课程吗？", "answer": "博睿智启上有哪些课程？"},
            {"question": "博小睿出生在哪个国家？", "answer": "博小睿的个人经历是怎样的？"},
            {"question": "司机可以开快车吗？", "answer": "司机可以做什么？"},
        ]
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples,
        )
        # 最终的提示模板
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一个AI助手,你的任务是生成回退问题，将问题改述为更一般或者前置问题,这样更易于回答."),
                few_shot_prompt,
                ("human", "{question}")
            ]
        )
        # 构建回退问题生成链
        chain = (
            {"question":RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
            | (lambda x:print("回退问题:",x) or x)
            | self.retriever
        )

        return chain.invoke(input= query)


#####################################################################################

# 测试
client = weaviate.connect_to_local(
    host="192.168.172.129",
    port=8080,
)
db = WeaviateVectorStore(
    client=client,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    index_name='collection_project',  # 数据集名称
    text_key='text',  # 文本内容的key名
)
retriever = db.as_retriever(search_type="mmr")
# 创建回退问题检索器
back_retriever = StepBackRetriever(
    retriever=retriever,
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),
)
result = back_retriever.invoke("关于配置接口的信息有哪些")
for doc in result:
    print(doc.page_content[:100],doc.metadata)
    print("-"*50)

client.close()

