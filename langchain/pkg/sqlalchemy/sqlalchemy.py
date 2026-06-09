from contextlib import contextmanager
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy

# 继承于SQLAlchemy核心类 增加事务提交的上下文函数
class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try :
            #yield之前的代码 代码上下文中执行的内容
            yield
            self.session.commit()
        except  Exception as e:
            self.session.rollback()
            raise e