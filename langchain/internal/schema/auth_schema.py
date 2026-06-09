from flask_wtf import FlaskForm
from marshmallow import Schema, fields
from wtforms import StringField
from wtforms.validators import DataRequired, Length, regexp, Email

from pkg.password import password_pattern


# 账号密码登录请求参数验证类
class PasswordLoginReq(FlaskForm):
    """账号密码登录请求结构"""
    # 必填email
    email = StringField("email", validators=[
        DataRequired("登录邮箱不能为空"),
        Email("登录邮箱格式错误"),  #  底层需要email_validator模块支持
        Length(min=5, max=254, message="登录邮箱长度在5-254个字符"),
    ])

    # 必填密码
    password = StringField("password", validators=[
        DataRequired("账号密码不能为空"),
        regexp(
            regex=password_pattern,
            message="密码最少包含一个字母，一个数字，并且长度为8-16"
        )
    ])


# 忘记密码重置请求参数验证类
class ResetPasswordReq(FlaskForm):
    """忘记密码重置请求结构（须校验原密码）"""
    email = StringField("email", validators=[
        DataRequired("登录邮箱不能为空"),
        Email("登录邮箱格式错误"),
        Length(min=5, max=254, message="登录邮箱长度在5-254个字符"),
    ])
    old_password = StringField("old_password", validators=[
        DataRequired("原密码不能为空"),
    ])
    password = StringField("password", validators=[
        DataRequired("新密码不能为空"),
        regexp(
            regex=password_pattern,
            message="密码最少包含一个字母，一个数字，并且长度为8-16"
        ),
    ])


# 账号密码授权认证响应结构包装类
class PasswordLoginResp(Schema):
    # 账号密码授权认证响应结构包装类
    access_token = fields.String()  # 授权令牌
    expire_at = fields.Integer()  # 过期时间
