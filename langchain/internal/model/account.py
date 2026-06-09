from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import (
    Column,
    UUID,
    String,
    DateTime,
    text,
    PrimaryKeyConstraint,
    Index,
)

from internal.extension.database_extension import db


# 账号模型  后续要继承于UserMixin配合Flask框架实现登录判断
class Account(db.Model, UserMixin):
    """账号模型"""
    __tablename__ = "account"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_account_id"),
        # 运维 优化 配置 : postgres数据库索引设计与添加
        Index("account_email_idx", "email"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    name = Column(String(255), nullable=False, server_default=text("''::character varying"))
    email = Column(String(255), nullable=False, server_default=text("''::character varying"))
    avatar = Column(String(255), nullable=False, server_default=text("''::character varying"))
    password = Column(String(255), nullable=True, server_default=text("''::character varying"))
    password_salt = Column(String(255), nullable=True, server_default=text("''::character varying"))
    last_login_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(0)"))
    last_login_ip = Column(String(255), nullable=False, server_default=text("''::character varying"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"),
        server_onupdate=text("CURRENT_TIMESTAMP(0)"),
    )
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(0)"))

    # 只读属性，获取当前账号的密码是否设置 首次使用第三方登录后 会生成账号信息 此时没有密码
    @property
    def is_password_set(self) -> bool:
        """只读属性，获取当前账号的密码是否设置"""
        return self.password is not None and self.password != ""


class AccountOAuth(db.Model):
    """账号与第三方授权认证记录表"""
    __tablename__ = "account_oauth"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_account_oauth_id"),
        # 运维 优化 配置 : postgres数据库索引设计与添加
        Index("account_oauth_account_id_idx", "account_id"),
        Index("account_oauth_openid_provider_idx", "openid", "provider"),
    )
    # id
    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    # 账号ID
    account_id = Column(UUID, nullable=False)
    # 提供商名称  GITHUB
    provider = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # 开放ID(第三方平台上的用户ID)
    openid = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # 加密秘钥(第三方提供的TOKEN令牌)
    encrypted_token = Column(String(255), nullable=False, server_default=text("''::character varying"))

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"),
        server_onupdate=text("CURRENT_TIMESTAMP(0)"),
    )
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(0)"))
