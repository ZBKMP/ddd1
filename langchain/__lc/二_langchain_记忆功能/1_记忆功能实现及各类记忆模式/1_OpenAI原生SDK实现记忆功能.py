# openAi原生API 记忆功能实现
from typing import Any
import openai
import dotenv
from openai import OpenAI


class ConversationSummaryBufferMemory:
    """摘要缓冲混合记忆类"""
    # 需要实现的属性及功能:
    # 1.max_token属性 用于判断是否需要生成新的摘要
    # 2.summary属性 用户存储摘要信息
    # 3.chat_histories属性(列表) 用于存储历史对话
    # 4.get_num_tokens方法 用于计算传入文本的token值
    # 5.save_content方法 用于存储新的交流对话
    # 6.get_buffer_string方法 用于将历史对话转换为str
    # 7.load_memory_variables方法 用于加载记忆变量信息
    # 8.summary_text方法 用于将旧的摘要和传入的对话生成新摘要

    # 初始化函数  摘要信息 历史信息 token最大长度
    def __init__(self,
                 summary: str = '',
                 char_histories: list = None,
                 max_tokens: int = 300):
        self.summary = summary
        self.char_histories = [] if char_histories is None else char_histories
        self.max_tokens = max_tokens

        self._client = OpenAI()  # 类中使用独立的OpenAI客户端以生成摘要

    # 4.get_num_tokens用于计算传入文本的token值
    @classmethod  # 不需要使用任何属性 设计成classmethod
    def get_num_tokens(cls, query: str) -> int:
        return len(query)  # 暂时用len函数,以后会使用模型的专用计算方法

    # 5.save_content用于存储新的交流对话
    def save_context(self, human_query: str, ai_content: str) -> None:
        # 对话信息记录到历史信息列表 包含 human 与 ai 信息
        self.char_histories.append({"human": human_query, "ai": ai_content})
        # 需要将历史信息转换为文本
        buffer_str = self.get_buffer_string()
        # 计算token数量
        tokens = self.get_num_tokens(buffer_str)
        # 超过长度 需要截取
        if tokens > self.max_tokens:
            # 取出第0条信息
            first_chat = self.char_histories[0]
            print("新摘要生成中...")
            # 转成摘要
            self.summary = self.summary_text(
                self.summary,
                f'Human:{first_chat["human"]}\nAI:{first_chat["ai"]}'
            )
            print("新摘要:", self.summary)
            # 转成后删除第0个信息
            del self.char_histories[0]
        # 完整逻辑是要求在去掉第0个消息转为摘要之后,还要继续判断是否依然超过长度,继而循环处理

    # 6.get_buffer_string用于将历史消息(列表)转换为str
    def get_buffer_string(self) -> str:
        buffer_str: str = ''
        for chat in self.char_histories:
            buffer_str += f'Human:{chat["human"]}\nAI:{chat["ai"]}\n\n'
        return buffer_str.strip()

    # 7.load_memory_variables用于加载记忆变量信息 转为dict 便于加到prompt中
    def load_memory_variables(self) -> dict[str, Any]:
        buffer_str = self.get_buffer_string()
        return {
            "chat_history": f'摘要:{self.summary}\n\n 历史信息:{buffer_str}\n',
        }

    # 8.summary_text用于将旧的摘要和传入的对话生成新摘要
    def summary_text(self, origin_summary: str, new_line: str) -> str:
        prompt = f'''
   你是一个强大的聊天机器人,请根据用户提供的谈话内容生成摘要,并将其添加到先前提供的摘要中,返回一个新的摘要,
   除了摘要内容,其他内容都不要返回,不要将example中的数据当成实际数据,它只是一个举例。如果用户的对话信息里
   有一些关键的信息,例如姓名,爱好,性别等重要事件,都要包含在摘要中,摘要要尽可能还原用户的对话记录
   <example>
   当前摘要:人类会问人工智能对人工智能的看法,人工智能认为人工智能是一股向善的力量
   
   新的对话:
   Human:为什么你认为人工智能是一股向善的力量?
   AI:因为人工智能会帮助人类充分发挥潜力。
    
   新摘要:人类会问人工智能对人工智能的看法,人工智能认为人工智能是一股向善的力量,因为它将帮助人类  
         充分发挥潜力
   </example>

   ========================以下是实际需要处理的数据================================   

   当前摘要: {origin_summary}   
  
   新的对话: 
   {new_line}
   
   请帮用户以上述信息生成新摘要:
'''
        # 将prompt发送至大模型 以生成新的摘要
        completion = self._client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content


##########################################################################################

'''
# 未进行记忆处理,哪怕是多次对话,AI也无法获取之前对话中出现的信息
# 创建openai访问模型
dotenv.load_dotenv()
client = openai.OpenAI()
# 创建一个死循环用于人机对话
while True:
    # 获取人类输入
    query = input("Human:")
    # 判断输入是否为q 是则退出
    if query == "q":
        break
    # 向openai的接口发起请求,获取AI生成内容
    response = client.chat.completions.create(
        model='gpt-3.5-turbo-16k',
        messages=[
            {"role": "user", "content": query}
        ],
        stream=True,
    )
    # 循环读取流式响应的内容
    print("AI: ", flush=True, end="")
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content is None:
            break
        print(content, flush=True, end="")
    print("")
'''
##########################################################################################


# OpenAI 摘要缓冲混合记忆实现
# 1 创建openai访问模型
dotenv.load_dotenv()
client = openai.OpenAI()
# 创建memory对象
memory = ConversationSummaryBufferMemory("", [], 300)

# 2 创建一个死循环用于人机对话
while True:
    # 3 获取人类输入
    query = input("Human: ")
    # 4 判断输入是否为q 是则退出
    if query == "q":
        break

    # 创建prompt,将记忆变量加载为dict,在prompt中填入chat_history key值
    memory_variables = memory.load_memory_variables()
    answer_prompt = (
        "你是一个强大的聊天机器人,请根据对应的上下文和用户解决问题\n\n"
        f"{memory_variables.get('chat_history')}\n\n"
        f"用户的提问是:{query}"
    )
    print("prompt:",answer_prompt)

    # 5 向openai的接口发起请求,获取AI生成内容
    response = client.chat.completions.create(
        model='gpt-4-turbo',
        messages=[
            {"role": "user", "content": answer_prompt}
        ],
        stream=True,  # 流式模式输出结果
    )
    # 直接使用query作为消息传入 LLM不会拥有任何记忆功能
    # 改为使用Prompt提示词,并将历史记忆插入提示词中,让LLM具有记忆能力

    # 6 循环读取流式响应的内容
    print("AI: ", flush=True, end="")
    ai_content = ""  # 将每一块AI生成的内容拼接
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content is None:
            break
        ai_content += content
        print(content, flush=True, end="")
    print("")

    # 保存交流对话 包含用户提问 以及AI响应
    memory.save_context(query, ai_content)
