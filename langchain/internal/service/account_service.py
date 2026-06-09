import base64
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from flask import request
from injector import inject

from pkg.password import hash_password, compare_password
from pkg.sqlalchemy import SQLAlchemy
from .jwt_service import JwtService
from .base_service import BaseService
from internal.model import Account, AccountOAuth
from internal.exception import FailException


@inject
@dataclass
class AccountService(BaseService):
    """账号服务"""
    db: SQLAlchemy
    jwt_service: JwtService

    # 根据id获取指定的账号模型实例
    def get_account(self, account_id: UUID) -> Account:
        """根据id获取指定的账号模型"""
        return self.get(Account, account_id)

    # 根据传递的 提供者名字+openid 从数据库查询第三方授权认证记录
    def get_account_oauth_by_provider_name_and_openid(
            self,
            provider: str,
            openid: str,
    ) -> AccountOAuth:
        """根据传递的提供者名字+openid获取第三方授权认证记录"""
        return self.db.session.query(
            AccountOAuth
        ).filter_by(
            provider=provider,
            openid=openid
        ).one_or_none()

    # 根据传递的邮箱查询账号信息
    def get_account_by_email(self, email: str) -> Account:
        """根据传递的邮箱查询账号信息"""
        return self.db.session.query(Account).filter(
            Account.email == email
        ).one_or_none()

    # 根据传递的键值对创建账号信息
    def create_account(self, **kwargs) -> Account:
        """根据传递的键值对创建账号信息"""
        return self.create(Account, **kwargs)

    # 更新当前账号密码信息
    def update_password(
            self,
            password: str,
            account: Account,
            old_password: str | None = None,
    ) -> Account:
        """更新当前账号密码信息；传入 old_password 时须先校验原密码"""
        if old_password is not None:
            if not account.is_password_set or not compare_password(
                    password=old_password,
                    password_hashed_base64=account.password,
                    salt_base64=account.password_salt,
            ):
                raise FailException("原密码错误，请核实后重试")

        # 1.生成密码随机盐值(字节串) ,又再生成字符串存于数据库
        salt = secrets.token_bytes(16)  # bytes
        base64_salt = base64.b64encode(salt).decode()  # str

        # 2.利用盐值和password进行加密(字节串) ,又再生成字符串存于数据库
        password_hashed = hash_password(password, salt)  # bytes
        base64_password_hashed = base64.b64encode(password_hashed).decode()  # str

        # 3.修改当前账号的密码信息 直接调用类中的update_account修改数据
        self.update_account(
            account=account,
            password=base64_password_hashed,
            password_salt=base64_salt,
        )

        return account

    # 根据传递的信息更新账号  密码  name  头像
    def update_account(
            self,
            account: Account,
            **kwargs
    ) -> Account:
        """根据传递的信息更新账号"""
        self.update(
            model_instance=account,
            **kwargs
        )
        return account

    # 根据传递的密码+邮箱登录特定的账号
    def password_login(
            self,
            email: str,
            password: str
    ) -> dict[str, Any]:  # 返回令牌与过期时间
        # 1.调用方法 根据传递的邮箱查询账号是否存在
        account = self.get_account_by_email(email)
        if not account:
            # 为配合前端操作 此处必须抛出 FailException
            raise FailException("账号不存在或者密码错误，请核实后重试")

        # 2.校验账号密码是否正确
        if not account.is_password_set or not compare_password(
                password=password,
                password_hashed_base64=account.password,
                salt_base64=account.password_salt
        ):
            # 为配合前端操作 此处必须抛出 FailException
            raise FailException("账号不存在或者密码错误，请核实后重试")

        # 3.email和密码验证成功  生成token以及过期时间
        # 过期时间为30天
        expire_at = int(
            (datetime.now() + timedelta(days=30)).timestamp()
        )
        # 载荷信息
        payload = {
            "sub": str(account.id),  # 账号ID
            "iss": "llmops",  # 令牌发放平台
            "exp": expire_at,  # 过期时间
        }
        # 生成token
        access_token = self.jwt_service.generate_token(payload)

        # 4.修改account表 更新登录记录
        self.update(
            model_instance=account,
            last_login_at=datetime.now(),
            last_login_ip=request.remote_addr,
        )

        # 5.返回结果
        return {
            "expire_at": expire_at,
            "access_token": access_token,
        }
