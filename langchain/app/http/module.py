from flask_login import LoginManager
from flask_migrate import Migrate
from flask_weaviate import FlaskWeaviate
from redis import Redis

# from flask_sqlalchemy import SQLAlchemy
from pkg.sqlalchemy import SQLAlchemy

from internal.extension import (
    db,
    migrate,
    redis_client, login_manager, weaviate,
)
from injector import Module, Binder, Injector




# 将已经创建好的对象(例如db)与其对应的类进行绑定,以便使用injector导入
class  ExtensionModule(Module):
    def configure(self, binder: Binder):
        # 将db对象 与 SQLAlchemy类进行绑定
        binder.bind(SQLAlchemy, to=db)
        # 将migrate对象 与 Migrate类进行绑定
        binder.bind(Migrate, to=migrate)
        # 将redis_client对象与 Redis类绑定
        binder.bind(Redis, to=redis_client)
        # 绑定 LoginManager 与 loginManager 对象
        binder.bind(LoginManager, to=login_manager)
        # 绑定 weaviate 与 FlaskWeaviate
        binder.bind(FlaskWeaviate,to=weaviate)

# 创建injector工具
injector = Injector(modules=[ExtensionModule])