import redis
from flask import Flask
from redis import Connection, SSLConnection

# 创建redis客户端
# 在其他任务中可能会需要使用redis_client,所以需要将其在app.http.module.py中
# 将该对象与Redis类绑定,以便依赖注入
redis_client = redis.Redis()


# 定义函数将redis与Flask进行绑定
def init_app(app: Flask):
    # 1.检测不同的场景使用不同的连接方式  普通模式与SSL模式
    connection_class = Connection
    if app.config.get("REDIS_USE_SSL", False):
        connection_class = SSLConnection

    # 2.创建redis连接池 配置信息来源于app.config
    redis_client.connection_pool = redis.ConnectionPool(
        **{
            "host": app.config.get("REDIS_HOST", "localhost"),
            "port": app.config.get("REDIS_PORT", 6379),
            "username": app.config.get("REDIS_USERNAME", None),
            "password": app.config.get("REDIS_PASSWORD", None),
            "db": app.config.get("REDIS_DB", 0),
            "encoding": "utf-8",
            "encoding_errors": "strict",  # 编码错误处理方式 严格
            "decode_responses": False # 是否进行编码转换
        },
        connection_class=connection_class,
    )

    # 3 将redis客户端与Flask对象绑定
    app.extensions["redis"] = redis_client