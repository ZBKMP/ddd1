# app.py
import os

import dotenv
from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

app = Flask(__name__)

# 固定提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个AI机器人 负责回答用户的问题"),
    ("user", "用户的提问是:{query}")
])

# 初始化模型
dotenv.load_dotenv()
llm = ChatOpenAI(
    model="gpt-3.5-turbo"
)

# 构建链
chain = prompt | llm | StrOutputParser()


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' field"}), 400

    query = data["query"].strip()
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    try:
        answer = chain.invoke({"query": query})
        return jsonify({"content": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)