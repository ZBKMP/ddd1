from dataclasses import dataclass
from typing import Optional

from flask import Request
from injector import inject

from internal.exception import UnauthorizedException
from internal.model import Account
from internal.service import JwtService, AccountService


@inject
@dataclass
class Middleware:
    """应用中间件，编写方法request_loader与unauthorized_handler"""
    # 依赖注入
    jwt_service : JwtService
    account_service : AccountService

    # 定义方法request_loader,返回Account(UserMixIn)模型类对象或者是None,
    # 该方法会在创建Flask_APP对象时与LoginManager进行绑定.
    # 每次进行登录检查时 会调用该方法 如果返回None 则表示没有登录
    def request_loader(
            self,
            request: Request
    ) -> Optional[Account]:
        """登录管理器的请求加载器"""
        # 1.单独为llmops路由蓝图创建请求加载器,该路由下的业务功能需要进行登录判断
        #   登录判断的逻辑为检查请求头中的Authorization,是否包含格式正确的Token字符串
        #   Authorization标准格式: Bearer access_token
        if request.blueprint == "llmops":
            # 2.提取请求头headers中的Authorization信息,如果没有则表示当前访问是未登录的访问
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise UnauthorizedException(
                    "该接口需要授权才能访问，请登录后尝试"
                )

            # 3.Authorization信息中没有空格分隔符,则验证失败.
            if " " not in auth_header:
                raise UnauthorizedException(
                    "该接口需要授权才能访问，验证格式失败"
                )

            # 4.分割授权信息,必须符合 Bearer access_token 格式
            auth_schema, access_token = auth_header.split(" ",maxsplit=1)
            if auth_schema.lower() != "bearer":
                raise UnauthorizedException(
                    "该接口需要授权才能访问，验证格式失败"
                )

            # 5.解析access_token信息得到用户信息并返回
            '''
            后期实现登录后 生成的载荷信息结构:
            payload = {
            "sub": str(account.id),  # 账号ID
            "iss": "llmops",  # 令牌签发主体
            "exp": expire_at,  # 过期时间
            }
            '''
            payload = self.jwt_service.parse_token(access_token)
            account_id = payload.get("sub")
            return self.account_service.get_account(account_id)
        else:
            return None