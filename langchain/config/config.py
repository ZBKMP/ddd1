# 处理项目中 Flask对象读取.env内的配置项
import os
from typing import Any

from config.default_config import DEFAULT_CONFIG


# 定义方法 从.env文件读取配置信息
def _get_env(key:str)->Any:
    # 以key去env中获取数据,没有则使用默认值
    return os.getenv(key, DEFAULT_CONFIG.get(key))
# 针对bool配置做特殊处理 env配置默认所有数据都是str,要将 True/False 转为bool值
def _get_bool_env(key:str)->bool:
    value = _get_env(key)
    return value.lower() == 'true' if value is not None else False

class Config:
    def __init__(self):
        # 所有配置项内容都来源于.env文件
        self.DEBUG = _get_bool_env('DEBUG')
        self.WTF_CSRF_ENABLED = _get_bool_env('WTF_CSRF_ENABLED')

        # 加载prostgres sqlAlchemy配置
        self.SQLALCHEMY_DATABASE_URI = _get_env("SQLALCHEMY_DATABASE_URI")
        self.SQLALCHEMY_ENGINE_OPTIONS ={
            "pool_size": int(_get_env("SQLALCHEMY_POOL_SIZE")),
            "pool_recycle": int(_get_env("SQLALCHEMY_POOL_RECYCLE")),
        }
        self.SQLALCHEMY_ECHO = _get_bool_env("SQLALCHEMY_ECHO")

        # 读取redis配置信息 这些配置信息都会被Flask对象获取
        self.REDIS_HOST = _get_env("REDIS_HOST")
        self.REDIS_PORT = _get_env("REDIS_PORT")
        self.REDIS_USERNAME = _get_env("REDIS_USERNAME")
        self.REDIS_PASSWORD = _get_env("REDIS_PASSWORD")
        self.REDIS_DB = _get_env("REDIS_DB")
        self.REDIS_USE_SSL = _get_bool_env("REDIS_USE_SSL")

        # Celery配置 基于REDIS配置和celery自身配置  redis作为缓存
        # Flask对象会先加载这些配置信息
        redis_pwd = _get_env('REDIS_PASSWORD')
        # 只有当密码存在时才拼接 “:密码@”，否则直接拼接空字符串
        auth_part = f":{redis_pwd}@" if redis_pwd else ""

        self.CELERY = {
            "broker_url": f"redis://{auth_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{int(_get_env('CELERY_BROKER_DB'))}",
            "result_backend": f"redis://{auth_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{int(_get_env('CELERY_RESULT_BACKEND_DB'))}",
            "task_ignore_result": _get_bool_env("CELERY_TASK_IGNORE_RESULT"),
            "result_expires": int(_get_env("CELERY_RESULT_EXPIRES")),
            "broker_connection_retry_on_startup": _get_bool_env("CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP"),
        }

        # Weaviate向量数据库配置
        self.WEAVIATE_HTTP_HOST = _get_env("WEAVIATE_HTTP_HOST")
        self.WEAVIATE_HTTP_PORT = _get_env("WEAVIATE_HTTP_PORT")
        self.WEAVIATE_GRPC_HOST = _get_env("WEAVIATE_GRPC_HOST")
        self.WEAVIATE_GRPC_PORT = _get_env("WEAVIATE_GRPC_PORT")