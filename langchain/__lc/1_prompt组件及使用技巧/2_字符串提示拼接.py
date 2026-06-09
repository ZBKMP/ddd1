from langchain_core.prompts import PromptTemplate

# 文本提示模板 与 字符串的拼接
# PromptTemplate 重写了 __add__ 方法可以合并另一个文本提示模板或字符串

prompt = PromptTemplate.from_template("请讲一个关于{subject}的冷笑话.")
# 基于现有的文本提示模板 拼接新的后续内容 例如字符串
prompt = prompt + "\n 请使用{language}语言来生成内容"
# 还可以再拼接另一个文本提示模版
other_prompt = PromptTemplate.from_template("\n 一次生成{n}个")
prompt = prompt + other_prompt
# 还可以使用默认传占位符
prompt = prompt.partial(n="3")



# 加法合并的结果仍然为文本提示模板 要包含所有的占位符
prompt_value = prompt.invoke(
    input={
        "subject": "工程师",
        "language": "english",
    }
)

print(prompt_value.to_string())
