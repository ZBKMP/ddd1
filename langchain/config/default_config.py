# 应用默认配置项选值
DEFAULT_CONFIG = {
    "DEBUG": "True",  # DEBUG
    "WTF_CSRF_ENABLED": "False",  # WTF_CSRF

    # SQLAlchemy 默认配置值
    "SQLALCHEMY_DATABASE_URI": "",
    "SQLALCHEMY_POOL_SIZE": 30,
    "SQLALCHEMY_POOL_RECYCLE": 3600,
    # 作用于从env加载配置信息的默认值,所以这里要写成字符串
    "SQLALCHEMY_ECHO": "True",

    # redis 配置默认值
    "REDIS_HOST": "127.0.0.1",
    "REDIS_PORT": "6379",
    "REDIS_USERNAME": "",
    "REDIS_PASSWORD": "",
    "REDIS_DB": 0,
    "REDIS_USE_SSL": "False",

    # Celery默认配置
    "CELERY_BROKER_DB": 1,
    "CELERY_RESULT_BACKEND_DB": 1,
    "CELERY_TASK_IGNORE_RESULT": "False",
    "CELERY_RESULT_EXPIRES": 3600,
    "CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP": "True",

    "WEAVIATE_HTTP_HOST": "192.168.172.129",
    "WEAVIATE_HTTP_PORT": 8080,
    "WEAVIATE_GRPC_HOST": "192.168.172.129",
    "WEAVIATE_GRPC_PORT": 50051,

}
