
import os
from dataclasses import dataclass
from typing import Any

import jwt
from injector import inject

from internal.exception import UnauthorizedException


@inject
@dataclass
# JWT业务服务类
class JwtService:
    """jwt服务"""

    # 根据传递的载荷信息生成token信息
    @classmethod
    def generate_token(cls, payload: dict[str, Any]) -> str:
        """根据传递的载荷信息生成token信息"""
        secret_key = os.getenv("JWT_SECRET_KEY")
        return jwt.encode(payload, secret_key, algorithm="HS256")

    # 解析传入的token信息得到载荷
    @classmethod
    def parse_token(cls, token: str) -> dict[str, Any]:
        """解析传入的token信息得到载荷"""
        secret_key = os.getenv("JWT_SECRET_KEY")
        # 将JWT异常转为自定义异常
        try:
            return jwt.decode(token, secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:  # 令牌超时
            raise UnauthorizedException("授权认证凭证已过期请重新登陆")
        except jwt.InvalidTokenError: # 内容篡改
            raise UnauthorizedException("解析token出错，请重新登陆")
        except Exception as e:
            raise UnauthorizedException(str(e))
