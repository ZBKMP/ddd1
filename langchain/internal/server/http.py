# 自定义Flask类,创建该Flask对象后,在init函数中完成所有对该Flask对象的设置
import logging

from flask import Flask
from flask import Response as FlaskResponse
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_weaviate import FlaskWeaviate

from internal.extension import logging_extension, redis_extension, celery_extension
from internal.middleware import Middleware
# from flask_sqlalchemy import SQLAlchemy
from pkg.sqlalchemy import SQLAlchemy

from pkg.response import HttpCode
from pkg.response.response import to_json, Response
from config import Config
from internal.exception import CustomException
from internal.router import Router

# 关联所有的db.Model数据库实体类
from internal.model import (
    App,
    ApiToolProvider,
    ApiTool,
    UploadFile,
    AppDatasetJoin,
    Dataset,
    Document,
    Segment,
    KeywordTable,
    ProcessRule,
    DatasetQuery,
    Conversation,
    Message,
    MessageAgentThought,
    Account,
    AccountOAuth,
)


class Http(Flask):
    """Http服务引擎 Flask类"""

    def __init__(
            self,
            *args,
            router: Router,  # 参数1  路由配置工具类对象
            config: Config,  # 参数2  Flask配置对象
            db: SQLAlchemy,  # 参数3  SQLAlchemy数据库操作对象
            migrate: Migrate,  # 参数4 数据迁移对象
            login_manager: LoginManager, # 参数5 登录管理器
            middleware: Middleware,  # 参数6 登录检查中间件
            weaviate_flask:FlaskWeaviate, # 参数7 运维 优化 配置 weaviate
            **kwargs
    ):
        # 1 调用父类对象实现构造函数初始化
        super().__init__(*args, **kwargs)

        # 2 关联上路由配置 将自身对象作为参数传入
        router.register_route(self)

        # 3 处理项目中所有的配置信息读取
        # self.config["WTF_CSRF_ENABLED"]=False
        # flask相关配置也要写在 .env内 ,通过专门的配置工具类去读取
        self.config.from_object(config)  # 对象中的属性则成为flask配置

        # 4 给flask对象增加异常处理配置 出现异常后 转为JSON模式的响应输出
        self.register_error_handler(
            code_or_exception=Exception,  # 设置可以处理的异常类型 所有异常(包括自定义异常和系统异常)
            f=self._error_handle
            # 自定义异常处理函数,原本函数返回的Response是基于HTML响应,需要改为JSON响应(ResponseHeader)
        )

        # 5 将SQLAlchemy对象与Flask对象进行关联,让SQLAlchemy对象可以读到配置信息
        db.init_app(self)
        # 6 将Migrate对象与FLask,SQLAlchemy对象关联 指定数据迁移文件目录
        migrate.init_app(self, db, directory='migrations')

        # 7 日志处理 调用loging_extension中的 init_app 方法
        logging_extension.init_app(self)

        # 8 redis客户端与flask对象的关联绑定
        redis_extension.init_app(self)

        # 9关联celery
        celery_extension.init_app(self)

        # 10 CORS处理
        CORS(self, resources={
            r"/*": {
                "origins": ["*"],
                "supports_credentials": True,
                # "methods":["GET","POST"],
                # "allow_headers":["Content-Type"],
            }
        })

        # 12 关联LoginManager
        login_manager.init_app(self)

        # 13 login_manager关联Middleware
        # 某个handler处理器如要进行登录验证时,就会自动使用该中间件的request_loader进行验证
        # 函数定义: request_loader(self, request: Request) -> Optional[Account]
        login_manager.request_loader(middleware.request_loader)

        # 14 weaviate关联flask
        weaviate_flask.init_app(self)

    # 自定义的异常处理函数,在运营阶段所有异常都以JSON格式输出,开发阶段系统异常要以HTML形式输出,以便开发者观察错误信息
    def _error_handle(self, error: Exception) -> FlaskResponse:
        # 日志记录 记录错误信息
        logging.error(
            "An error has occurred : %s ",  # 日志输出的消息文本 可以包含多个 %s 占位符
            error,  # 填充上述多个 %s 占位符的变量
            exc_info=True,
        )

        # 判断异常类型是否为自定义异常
        if isinstance(error, CustomException):
            # 自定义异常则以JSON格式输出
            return to_json(Response(
                code=error.code,
                message=error.message,
                data=error.data if error.data else {},
            ))

        # 系统异常 判断当前是开发模式还是运营模式
        if self.debug:
            raise error
        else:
            return to_json(Response(
                code=HttpCode.FAIL,
                message=str(error),
                data={},
            ))
