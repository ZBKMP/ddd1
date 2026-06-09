from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import dotenv
dotenv.load_dotenv()
# 定义表结构
MY_SCHEMA = """
表名: workers
字段: 
- id (员工编号)
- name (员工姓名)
- department (部门: '开发部', '市场部', '人事部')
- salary (薪资)
- join_date (入职日期)
"""
#固定输出
sql_template = """你是一个 SQL 生成专家。请根据下方的 Schema 将问题转为 SQL。
只输出 SQL 语句，不要任何解释。
[Schema]
{schema}

[question]
{question}

SQL:"""
prompt = PromptTemplate.from_template(sql_template)

#模型
llm = ChatOpenAI(model='gpt-4o-mini',
                 temperature=0,)
#连一起
chain = prompt|llm|StrOutputParser()

#提问
question = '帮我查下开发部的员工有哪些'

#执行
sql_output = chain.invoke({'schema': MY_SCHEMA, 'question': question})

clean_sql = sql_output.replace("```sql", "").replace("```", "").strip()
print(f" {clean_sql}")