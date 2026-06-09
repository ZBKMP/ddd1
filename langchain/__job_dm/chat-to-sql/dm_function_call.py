import os, dotenv
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

dotenv.load_dotenv()


# 1. 定义一个“模拟数据库”函数
@tool
def get_user_spending(user_name: str, year: int) -> str:
    """查询指定用户在特定年份的总消费金额。"""

    mock_data = {
        "二狗": {2025: "50,000 rmb", 2026: "80,000 rmb"},
        "三胖": {2025: "500,000,000 美元", 2026: "600,000,000 美元"}
    }
    res = mock_data.get(user_name, {}).get(year, "查无数据")
    return f"用户 {user_name} 在 {year} 年的消费是：{res}"


# 2. 初始化模型
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# 把函数放进工具箱
tools = [get_user_spending]
llm_with_tools = llm.bind_tools(tools)

# 3. 模拟对话
query = "帮我看看三胖 2026 年花了多少钱？"
print(f"用户提问: {query}")

# 模型分析意图
ai_msg = llm_with_tools.invoke(query)

# 检查模型是否发出了函数调用申请
if ai_msg.tool_calls:
    print(" 需要调用 get_user_spending 函数")
    for tool_call in ai_msg.tool_calls:
        # 获取模型提取的参数
        print(f" 提取参数: {tool_call['args']}")

        # 执行模拟查询
        result = get_user_spending.invoke(tool_call["args"])

        #数据喂回模型
        final_answer = llm.invoke(f"用户问：{query}\n工具返回结果：{result}\n请用亲切的语气回答。")
        print(f"\n 最终回答: {final_answer.content}")