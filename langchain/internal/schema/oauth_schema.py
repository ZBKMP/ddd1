from flask_wtf import FlaskForm
from marshmallow import Schema, fields
from wtforms import StringField
from wtforms.validators import DataRequired


# 第三方授权认证请求验证类
class AuthorizeReq(FlaskForm):
    """第三方授权认证请求体"""
    code = StringField(
        "code",
        validators=[DataRequired("code代码不能为空")]
    )

# 第三方授权认证响应结构封装类
class AuthorizeResp(Schema):
    """第三方授权认证响应结构"""
    access_token = fields.String()  # 授权令牌
    expire_at = fields.Integer()  # 过期时间