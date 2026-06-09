import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from flask import request
from injector import inject

from internal.exception import NotFoundException
from internal.model import Account, AccountOAuth
from internal.service import AccountService, JwtService
from internal.service.base_service import BaseService
from pkg.oauth import GithubOAuth
from pkg.oauth.oauth import OAuth
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class OAuthService(BaseService):
    # 依赖注入
    db: SQLAlchemy
    account_service: AccountService
    jwt_service: JwtService

    # 类方法 获取LLMOps集成的所有第三方授权认证方式对象
    @classmethod
    def get_all_oauth(cls) -> dict[str, OAuth]:
        # 1.实例化集成的第三方授权认证OAuth

        # 创建github第三放登录对象GithubOAuth
        github = GithubOAuth(
            # 客户端id 例如env配置的:GITHUB_CLIENT_ID
            client_id=os.getenv("GITHUB_CLIENT_ID"),
            # 客户端秘钥 例如env配置的:GITHUB_CLIENT_SECRET
            client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
            # 授权成功后跳转的前端项目地址 重定向uri
            #      例如env配置的:GITHUB_REDIRECT_URI
            redirect_uri=os.getenv("GITHUB_REDIRECT_URI"),
        )

        # 后续可以增加其他第三方登录工具有对象

        # 2.构建字典并返回,当前仅包含github服务,
        #   后续可以再增加其他第三方服务
        return {
            "github": github,
            # ....
        }

    # 根据传递的服务提供商名字获取授权服务
    @classmethod
    def get_oauth_by_provider_name(
            cls,
            provider_name: str
    ) -> OAuth:
        all_oauth = cls.get_all_oauth()
        oauth = all_oauth.get(provider_name)

        if oauth is None:
            raise NotFoundException(
                f"该授权方式[{provider_name}]不存在"
            )
        return oauth

    # 第三方OAuth授权认证登录，返回授权凭证Token以及过期时间
    def oauth_login(
            self,
            provider_name: str,
            code: str
    ) -> dict[str, Any]:
        """第三方OAuth授权认证登录，返回授权凭证Token以及过期时间"""
        # 1.根据传递的provider_name获取第三方oauth对象
        oauth = self.get_oauth_by_provider_name(provider_name)

        # 2.根据code从第三方登录服务中获取access_token
        oauth_access_token = oauth.get_access_token(code)

        # 3 根据上一步骤中获取到的access_token再提取第三方平台上的user_info信息
        oauth_user_info = oauth.get_user_info(oauth_access_token)
        print({
            "id": oauth_user_info.id,
            "name": oauth_user_info.name,
            "email": oauth_user_info.email,
        })

        # 4.调用account_service中的方法,根据provider_name+openid
        #   从数据库查询第三方授权认证记录
        account_oauth = self.account_service.get_account_oauth_by_provider_name_and_openid(
            provider=provider_name,
            openid=oauth_user_info.id
        )
        if not account_oauth:
            # 5.查不到授权记录 则该授权认证方式是第一次登录，
            # 先调用account_service.get_account_by_email 查询账号是否存在
            account = self.account_service.get_account_by_email(
                email=oauth_user_info.email
            )
            if not account:
                # 6.如果账号不存在，调用account_service.create_account，
                #   使用同token中提取的用户信息和邮箱地址注册新账号
                account = self.account_service.create_account(
                    email=oauth_user_info.email,
                    name=oauth_user_info.name,
                )
            # 7.第一次使用该授权方式登录,添加授权认证记录
            account_oauth = self.create(
                AccountOAuth,
                account_id=account.id,
                provider=provider_name,
                openid=oauth_user_info.id,
                encrypted_token=oauth_access_token,
            )
        else:
            # 8.能查到记录,则从授权认证记录中查找账号信息
            account = self.account_service.get_account(
                account_oauth.account_id
            )

        # 9.更新账号信息，涵盖最后一次登录时间，以及ip地址
        self.update(
            model_instance=account,
            last_login_at=datetime.now(),
            last_login_ip=request.remote_addr,  # 从flask的request获取请求来源的IP地址
        )
        # 同步更新account_oauth数据中的加密Token信息
        self.update(
            model_instance=account_oauth,
            encrypted_token=oauth_access_token,
        )



        # 10 生成LLMOPS后端接口授权凭证Token信息
        # 过期时间 30天
        expire_at = int(
            (datetime.now() + timedelta(days=30)).timestamp()
        )
        # 载荷信息:用户信息
        payload = {
            "sub": str(account.id),  # 账号ID
            "iss": "llmops",  # 令牌签发主体
            "exp": expire_at,  # 过期时间
        }
        # 依据载荷生成后端接口授权凭证Token信息,后续访问后端时,
        # 遇到需要登录检查的接口,需要在请求中包含该token
        access_token = self.jwt_service.generate_token(payload)

        return {
            "expire_at": expire_at,  # 过期时间
            "access_token": access_token,  # 登录成功token
        }
