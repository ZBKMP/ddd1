#  pip install langchain==0.3.27
#  pip install langchain-community==0.3.29
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

# PromptTemplate(文本提示模板)  ChatPromptTemplate(聊天提示模板) 简单实用案例

# 1 文本提示模板  默认使用f-string对文本内容进行格式化编排
#   文本中可以包含 {XXX} 表示的占位符,在使用该提示模板时,则必须以站位符的名称传入对应的数据
prompt = PromptTemplate.from_template("你是一个AI助手  \n\n 请讲一个关于{subject}的{content}")
#   提示模板对象使用invoke执行出结果,该结果才可以传递给后续的大模型
#   模版文本中包含的占位符变量,在invoke时就必须使用input(dict)传入
prompt_value = prompt.invoke(input={"subject": "程序员", "content": "冷笑话"})
#   提示模板执行结果返回类型为PromptValue
print(prompt_value, type(prompt_value))
print(prompt_value.to_string())  # 转为字符串
print(prompt_value.to_messages())  # 转为消息列表

print("*" * 50)

# 2 聊天提示模板 消息列表  默认支持f-string编辑占位符变量
#   身份只能是 ：'human', 'user', 'ai', 'assistant', or 'system'
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是{provider}开发的AI智能助手,请根据用户的提问回答问题"),
    ("user", "请讲一个关于{subject}的{content}"),
])
# 执行提示模板时 传入所有消息中的占位符变量值 得到PromptValue对象
prompt_value = chat_prompt.invoke(
    input={"provider": "OpenAI", "subject": "产品经理", "content": "打油诗"})
# 查看PromptValue对象结果
print(prompt_value, type(prompt_value))
# 调用PromptValue.to_string()
print(prompt_value.to_string())
# 调用PromptValue.to_messages() # 聊天提示模板 消息列表
print(prompt_value.to_messages())

print("*" * 50)

# 3 聊天提示模板中 使用类对象的方式去表示每个消息
chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("你是{provider}开发的AI智能助手,请根据用户的提问回答问题"),
    # SystemMessage("你是{provider}开发的AI智能助手,请根据用户的提问回答问题"), # XXXMessage 无法解析占位符

    # 以后实现记忆功能 还可以在消息列表中填入 历史聊天消息列表 (HumanMessage AIMessage HumanMessage AIMessage ......)
    # ("placeholder","{chat_history}"), # 在执行时允许不传该占位符
    # 历史消息列表使用类的方式来实现 参数就是占位符的名称
    MessagesPlaceholder("chat_history"),  # 在执行时必须传该占位符


    HumanMessagePromptTemplate.from_template("请讲一个关于{subject}的{content}"),
    # HumanMessage("请讲一个关于{subject}的{content}"),
])

# 执行提示模板时 传入所有消息中的占位符变量值 得到PromptValue对象
prompt_value = chat_prompt.invoke(
    input={
        "provider": "OpenAI",
        "subject": "产品经理",
        "content": "打油诗",

        # 传递历史消息列表占位符变量
        "chat_history": [
            ("human", "你好 你是谁？"),
            ("ai", "我是一个人工智能聊天机器人"),
            HumanMessage("请介绍一下什么是LLM"),
            AIMessage("LLM是大语言模型........")
        ]
    })
# 查看PromptValue对象结果
print(prompt_value, type(prompt_value))
# 调用PromptValue.to_string()
print(prompt_value.to_string())
# 调用PromptValue.to_messages() # 聊天提示模板 消息列表
print(prompt_value.to_messages())

print("*" * 50)

# 4 在执行提示模板之前 预选传入某些占位符的参数 partial
chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("你是{provider}开发的AI智能助手,请根据用户的提问回答问题"),
    HumanMessagePromptTemplate.from_template("请讲一个关于{subject}的{content}"),
]).partial(provider = 'BaiDuQianFan')

# 执行提示模板时 有设置过partial的占位符 可以不再传值
prompt_value = chat_prompt.invoke(
    input={
        "subject": "产品经理",
        "content": "打油诗",
    }
)
# 查看PromptValue对象结果
print(prompt_value, type(prompt_value))
# 调用PromptValue.to_string()
print(prompt_value.to_string())
# 调用PromptValue.to_messages() # 聊天提示模板 消息列表
print(prompt_value.to_messages())


# 总结两种提示模板的使用特点

# 编辑一套聊天提示模板 要求包含 系统消息,聊天历史,人类消息。使用partial预先传入占位符关键字
# 提示模板和消息列表中分别使用 元祖模式和类模式 主题可以是销售类型  知识问答类型 等


'''
面试题：
1、langchain 的6大组件是什么？
2、什么是提示词，它在与大模型交互中的作用是什么？
3、在langchain中写提示词，form_template与form_messages有什么区别，分别在什么场景下使用
'''