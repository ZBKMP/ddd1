# PromptTemplate文本提示模板+ PipelinePromptTemplate管道提示模板 实现提示模板的复用

from langchain_core.prompts import PromptTemplate, PipelinePromptTemplate

# 文本提示模板的整体架构 可以在每个占位符位置传入子文本模版
final_prompt = PromptTemplate.from_template("""
    以下是背景介绍:
    {instruction}\n
    在回答问题前可以参考以下示例:
    {example}\n
    接下来准备回答用户的问题:
    {start}\n    
""")


# 定义三个子模版(文本提示模板)
instruction_prompt = PromptTemplate.from_template("你正在模拟{person}")

example_prompt = PromptTemplate.from_template("""
    以下是一个聊天过程的示例:
    Q:{example_question}
    A:{example_answer}
""")

start_prompt = PromptTemplate.from_template("""
    你现在是一个真实的人,请回答用户的提问.
    用户的问题是:{query}
""")

# 定义占位符与子模板之间的对应关系
pipeline_prompts = [
    ("instruction",instruction_prompt),
    ("example",example_prompt),
    ("start",start_prompt)
]

# 使用管道提示模板将多个子模版组合到整体模板中
pipe_line_prompt = PipelinePromptTemplate(
    # 整体的架构模版
    final_prompt=final_prompt,
    # 架构模版中每个占位符与子模板的对应关系
    pipeline_prompts=pipeline_prompts
)

# 执行组合后的管道提示模版 所有子模板中包含的占位符参数 都需要传递
prompt_value = pipe_line_prompt.invoke({
    "person":"python_AI程序员",
    "example_question":"你最擅长的编程技术是什么?",
    "example_answer":"python mysql flask ...",
    "query":"python中如何实现基于AI大模型的编程设计?"
})

# 查看执行结果
print(prompt_value.to_string())