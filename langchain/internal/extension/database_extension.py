#from flask_sqlalchemy import SQLAlchemy
from pkg.sqlalchemy import SQLAlchemy # 改用自定义的带有自动提交上下文的SQLAlchemy
# 创建数据库连接
db = SQLAlchemy()

