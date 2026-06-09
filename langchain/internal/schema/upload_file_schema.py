from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileSize, FileAllowed
from marshmallow import Schema, fields, pre_dump
from wtforms import FileField
from internal.entity.upload_file_entity import ALLOWED_DOCUMENT_EXTENSION, ALLOWED_IMAGE_EXTENSION
from internal.model import UploadFile


# 上传文件请求参数验证类
class UploadFileReq(FlaskForm):
    """上传文件请求"""
    # 验证请求上传的文件信息 类型为'文件'
    file = FileField(
        label="file",
        validators=[
            # 文件必填
            FileRequired(message="文件内容不能问为空"),
            # 文件大小
            FileSize(max_size=15*1024*1024, message="上传文件不能超过15M"),
            # 允许上传的文件类型  ALLOWED_DOCUMENT_EXTENSION列表 描述允许的文件后缀名
            FileAllowed(
                upload_set=ALLOWED_DOCUMENT_EXTENSION,
                message=f"仅允许上传{'/'.join(ALLOWED_DOCUMENT_EXTENSION)}文件",
            )
        ]
    )

# 上传文件接口响应结果封装类
class UploadFileResp(Schema):
    """上传文件接口响应接口"""
    id = fields.UUID(dump_default="")  # id
    account_id = fields.UUID(dump_default="")  # 当前账号
    name = fields.String(dump_default="")  # 原文件名
    key = fields.String(dump_default="")  # COS云端路径
    size = fields.Integer(dump_default=0)  # 大小
    extension = fields.String(dump_default="")  # 扩展名
    mime_type = fields.String(dump_default="")  # mime类型
    created_at = fields.Integer(dump_default=0)  # 创建时间

    # 预先将UploadFile(db.Model)对象转换为字典 以便最终转为JSON
    @pre_dump
    def process_data(self,data:UploadFile,**kwargs):
        return {
            "id": data.id,
            "account_id": data.account_id,
            "name": data.name,
            "key": data.key,
            "size": data.size,
            "extension": data.extension,
            "mime_type": data.mime_type,
            # 将Datetime对象转换为int
            "created_at": int(data.created_at.timestamp()),
        }

# 上传图片请求参数验证类
class UploadImageReq(FlaskForm):
    """上传图片请求结构体"""
    file = FileField(
        "file",
        validators=[
            FileRequired("上传图片不能为空"),
            FileSize(max_size=15 * 1024 * 1024,
                     message="上传图片最大不能超过15MB"),
            FileAllowed(ALLOWED_IMAGE_EXTENSION,
        message=f"仅允许上传{'/'.join(ALLOWED_IMAGE_EXTENSION)}文件")
        ]
    )