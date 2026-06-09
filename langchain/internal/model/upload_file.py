from sqlalchemy import (
    Column,
    UUID,
    String,
    Integer,
    DateTime,
    PrimaryKeyConstraint,
    text,
)

from internal.extension.database_extension import db


class UploadFile(db.Model):
    """上传文件模型"""
    __tablename__ = "upload_file"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_upload_file_id"),
    )
    # 主键
    id = Column(UUID, nullable=False, server_default=text('uuid_generate_v4()'))
    # 登录账号ID
    account_id = Column(UUID, nullable=False)
    # 原文件名
    name = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # 云端位置
    key = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # 文件大小
    size = Column(Integer, nullable=False, server_default=text('0'))
    # 扩展名
    extension = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # 文件类型
    mime_type = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # 文件hash值 用于进行文件内容比对
    hash = Column(String(255), nullable=False, server_default=text("''::character varying"))

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
