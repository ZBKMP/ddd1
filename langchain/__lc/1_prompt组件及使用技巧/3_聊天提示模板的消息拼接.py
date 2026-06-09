#  ChatPromptTemplate(基于消息列表) 的消息拼接
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

# 实现多个ChatPromptTemplate消息列表的合并

# 创建多组消息列表
system_chat_prompt = ChatPromptTemplate.from_messages([
    ("system","你是一个{provider}开发的聊天机器人........")
])
history_chat_prompt = ChatPromptTemplate.from_messages([
    ("placeholder","{chat_history}")
])
human_chat_prompt = ChatPromptTemplate.from_messages([
    ("human","用户的问题是:{query}")
])



# + 合并多个消息列表
chat_prompt = system_chat_prompt + history_chat_prompt + human_chat_prompt

prompt_value=chat_prompt.invoke({
    "provider":"DeepSeek",
    "query":"请描述一下什么是人工智能",
    "chat_history":[
        HumanMessage("您好你是谁"),
        AIMessage("我是AI助手"),
    ],
})
print(prompt_value.to_string())