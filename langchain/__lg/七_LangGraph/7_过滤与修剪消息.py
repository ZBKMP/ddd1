# 过滤与修剪消息:

import dotenv
from langchain_core.messages import HumanMessage, AIMessage, trim_messages, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from torch.backends.opt_einsum import strategy

# 1 模型创建
dotenv.load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

# 2 模拟对话过程中产生的消息列表
messages = [
    SystemMessage(content='你是OpenAI开发的机器人助手,用于回答用户的问题.'),
    HumanMessage(content="你好，我叫小黑子，我喜欢唱跳RAP篮球，你喜欢什么呢？"),
    AIMessage([
        {"type": "text",
         "text": "你好，小黑子！我对很多话题感兴趣，比如探索新知识和帮助解决问题。你最喜欢唱跳RAP还是篮球呢？"},
        {
            "type": "text",
            "text": "你好，小黑子！我喜欢探讨各种话题和帮助解答问题。你对唱跳RAP和篮球的兴趣很广泛，有没有特别喜欢的运动方式或运动员呢？"
        },
    ]),
    HumanMessage(content="如果我想学习关于天体物理方面的知识，你能给我一些建议么？"),
    AIMessage(
        content="当然可以！你可以从基础的天文学和物理学入手，然后逐步深入到更具体的天体物理领域。阅读相关的书籍，如《宇宙的结构》或《引力的秘密》，也可以关注一些优秀的天体物理学讲座和课程。你对哪个方面最感兴趣？"
    ),
]

# 3 使用trim_messages函数对消息列表进行过滤与裁剪
result_messages = trim_messages(
    messages=messages,  # 消息列表
    max_tokens=200,  # 裁剪之后的长度
    token_counter=llm,  # 使用大模型计算token长度
    strategy="first",  # 裁剪策略 从头或从尾开始
    allow_partial=False,  # 是否允许将一条消息裁剪成两半
    text_splitter=RecursiveCharacterTextSplitter().split_text  # 分割符
)

# 4 测试截取结果
for message in result_messages:
    print(message)
