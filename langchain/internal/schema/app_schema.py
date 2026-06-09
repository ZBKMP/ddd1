# app 模块下 视图函数请求验证
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length


# FlaskForm 对请求中的参数进行验证 以及可以获取请求参数
# 支持 post表单form ,post JSON传参
class DebugReq(FlaskForm):
    # 必须有参数query str 最大长度2000
    query = StringField(
        label='query',  # 请求中的参数名
        validators=[
            DataRequired(message="用户提问是必填的"),  # 请求中必须包含该参数
            Length(min=1, max=2000,message="用户的提问长度不可超过2000")
        ]
    )
