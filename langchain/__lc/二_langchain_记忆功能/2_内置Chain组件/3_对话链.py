import dotenv
from langchain.chains.conversation.base import ConversationChain
from langchain_openai import ChatOpenAI

# 1 构建链组件
dotenv.load_dotenv()
llm = ChatOpenAI(model="gpt-3.5-turbo-16k")

# 2  对话链 链中默认已包含提示词(key:history/query),包含记忆组件
# 和LCEL 不同，Chain 类封装的链绝大部分都是以实例化 Chain 类的方式来实现的。
chain = ConversationChain(
    llm=llm,
    # memory= ?  # 可以更改底层的记忆组件,默认是 ConversationBufferMemory
    # prompt= ?, # 可以更改底层的文本提示模板 ,默认包含一个,可以改为中文的提示模板,但必须包含两个占位符:history input
)


# 3  循环执行链 无需手写保存记忆的代码 chain中已经实现了
while True:
    query= input("Human:")

    if query.lower() == "q":
        break

    chain_input = {"input": query}

    result = chain.invoke(chain_input)
    print(result) # 结果为字典 包含 input  history  response  （JsonOutputParser）


#  要求3  :  按照上述说明 自定义ConversationChain中的记忆组件(实现文件存储)
#           以及 提示模板


'''
面试题:
你们大模型中的记忆是怎么做的？ 
请回答记忆的多种策略，以及使用的场景？
'''

