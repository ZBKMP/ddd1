# Runnable组件配置运行时链状态 configurable_fields方法使用技巧

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import ConfigurableField, RunnableConfig, Runnable
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# 构建提示词
dotenv.load_dotenv()

# 在invoke时 临时动态的去更改 可运行组件的参数
# 1 创建大模型时先要设置可通过invoke-config动态配置的参数
chat_model = ChatOpenAI(model="gpt-3.5-turbo-16k").configurable_fields(
    # 声明有哪些参数 可以在invoke时动态更改
    temperature=ConfigurableField(
        id='llm_temperature',  # 在invoke中更改该参数时使用的名称
        name="temperature的动态配置名",
        description="可以通过该参数在invoke时动态更改大模型的temperature参数",
    )
)

# 4 除了LLM ,提示模板也可以设置可变参数
prompt = PromptTemplate.from_template("请生成一个小于{x}的随机x正整数").configurable_fields(
    # 新增一个可配置参数 映射template参数
    template = ConfigurableField(
        id = "prompt_template"
    )
)

# 2 创建链
chain = prompt | chat_model | StrOutputParser()

# 3 循环调用 执行时动态更改LLM参数值
# for i in range(0, 3):
#     result = chain.invoke(
#         input={"x": 100},
#         config=RunnableConfig(configurable={
#             "llm_temperature":0.1
#         })
#     )
#     print(result)


# 5 测试更改提示模板的template属性 链中所有可运行组件配置过的可变参数都可以配置
result  = chain.invoke(
    input={"subject":"医生"},
    config=RunnableConfig(configurable={
        "prompt_template":"请讲一个关于{subject}的冷笑话?",
        "llm_temperature":1.5,
    })
)
print(result)

# 要求 1: 重构之前拼接提示模板的案例 通过设置运行时参数实现 由用户选择 动态切换提示模板:政治问题 历史问题 数学问题 物理问题.......
#        不同学科问题 回答时的温度也要不一样