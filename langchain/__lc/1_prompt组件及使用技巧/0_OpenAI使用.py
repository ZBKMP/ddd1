import os
import dotenv
from openai import OpenAI

'''
python版本 使用 3.11
安装 requirements.txt  下所有的依赖
pip install -r requirements.txt

1.1 安装openai模块
pip install openai==1.107.2

1.2 安装dotenv模块
pip install dotenv
在项目根目录创建.env文件设置openai 的 api_key

LLM 
'''


# 1 测试使用dotenv读取.env配置文件的内容
dotenv.load_dotenv()
print(os.getenv("OPENAI_API_KEY"))
print(os.getenv("OPENAI_BASE_URL"))

# 2 创建一个OpenAI大模型客户端 只要执行了dotenv.load_dotenv() 会自动取加载两个配置信息
client = OpenAI(
    #api_key=os.getenv("OPENAI_API_KEY"),
    #base_url=os.getenv("OPENAI_BASE_URL"),
)

# 3 使用客户端 向OpenAI服务器发起请求
query = "请介绍一下什么是LLM?" # 用户提问
completion = client.chat.completions.create(
    model="gpt-3.5-turbo-16k",
    messages=[
        # 系统消息 用于告知大模型需要扮演的角色,会对大模型内容生成产生影响
        {"role":"system","content":"你是一个AI助手,负责根据用户提供的提问生成回答"},
        # 用户消息 用户提供的内容 (提问或其他)
        {"role":"user","content":query},
    ]
)

# 4 从OpenAI服务器响应回的结果中提取AI生成的内容 AI消息
print(completion) # ChatCompletion类对象

# 5 从生成结果中提取AI回答的内容
content = completion.choices[0].message.content
print(content)


# 基于OpenAI实现聊天机器人,测试系统消息给予不同的身份描述,观察测试AI生成内容的区别

