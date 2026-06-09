# 启动Flask应用
import os

import dotenv
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_weaviate import FlaskWeaviate

from internal.middleware import Middleware
# from flask_sqlalchemy import SQLAlchemy
from pkg.sqlalchemy import SQLAlchemy

from internal.extension import db
from injector import Injector
from config import Config
from internal.router import Router
from internal.server import Http
from .module import injector  # 绑定了modules的injector对象

# 加载.evn文件
dotenv.load_dotenv()

# 配置猴子补丁
if os.environ.get("DEBUG") == 'False' or os.environ.get("FLASK_ENV") == "production":
    from gevent import monkey
    monkey.patch_all()
    import grpc.experimental.gevent
    grpc.experimental.gevent.init_gevent()

# 创建Flask对象
app = Http(__name__,
           router=injector.get(Router),  # 参数1  创建路由对象
           config=Config(),  # 参数2 配置信息
           db=injector.get(SQLAlchemy),  # 参数3  数据库操作对象(要将SQLAlchemy类与db对象绑定)
           migrate=injector.get(Migrate),  # 参数4  数据库迁移对象
           login_manager=injector.get(LoginManager),  # 参数5 登录管理器
           middleware=injector.get(Middleware),  # 参数6 injector创建Middleware对象
           weaviate_flask = injector.get(FlaskWeaviate) # 参数7 运维 优化 配置  FlaskWeaviate
           )

# 为了能在终端执行Celery指令 需要从app扩展中获取Celery对象
celery = app.extensions['celery']

# 运行启动
if __name__ == '__main__':
    print(app.url_map)
    app.run()
