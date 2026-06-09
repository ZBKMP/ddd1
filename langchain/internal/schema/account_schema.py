from flask_wtf import FlaskForm
from marshmallow import Schema, fields, pre_dump
from wtforms import StringField
from wtforms.validators import DataRequired, regexp, Length, URL

from internal.lib import datetime_to_timestamp
from internal.model import Account
from pkg.password import password_pattern


# 获取当前登录账号信息响应封装类
class GetCurrentUserResp(Schema):
    """获取当前登录账号信息响应"""
    id = fields.UUID(dump_default="")  # 账号ID
    name = fields.String(dump_default="")  # 账号名称
    email = fields.String(dump_default="")  # email
    avatar = fields.String(dump_default="")  # 头像
    last_login_at = fields.Integer(dump_default=0)  # 最后登录时间
    last_login_ip = fields.String(dump_default="")  # 最后登录ID
    created_at = fields.Integer(dump_default=0)

    # 数据对象先转为字典 以便后期转为JSON
    @pre_dump
    def process_data(self, data: Account, **kwargs):
        return {
            "id": data.id,
            "name": data.name,
            "email": data.email,
            "avatar": data.avatar,
            "last_login_at": datetime_to_timestamp(data.last_login_at),
            "last_login_ip": data.last_login_ip,
            "created_at": datetime_to_timestamp(data.created_at),
        }


# 更新账号密码请求参数验证类
class UpdatePasswordReq(FlaskForm):
    """更新账号密码请求"""
    old_password = StringField("old_password", validators=[
        DataRequired("原密码不能为空"),
    ])
    password = StringField("password", validators=[
        DataRequired("新密码不能为空"),
        regexp(
            regex=password_pattern,
            message="密码最少包含一个字母、一个数字，并且长度是8-16"
        ),
    ])

# 更新账号名称请求参数验证类
class UpdateNameReq(FlaskForm):
    """更新账号名称请求"""
    # 必须传递新名称name
    name = StringField("name", validators=[
        DataRequired("账号名字不能为空"),
        # 参数值格式验证
        Length(min=3, max=30, message="账号名称长度在3-30位"),
    ])

# 更新账号头像请求参数验证类
class UpdateAvatarReq(FlaskForm):
    """更新账号头像请求"""
    avatar = StringField("avatar", validators=[
        DataRequired("账号头像不能为空"),
        URL("账号头像必须是URL图片地址"),
    ])