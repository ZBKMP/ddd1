import math
from dataclasses import dataclass
from typing import Any

from flask_wtf import FlaskForm
from sqlalchemy import Select
from wtforms import IntegerField
from wtforms.validators import Optional, NumberRange

from pkg.sqlalchemy import SQLAlchemy


# 包含分页请求参数的通用Req基类 继承于FlaskForm
class PaginatorReq(FlaskForm):
    """分页请求基础类，涵盖当前页数、每页条数，如果接口请求需要携带分页信息，可直接继承该类"""
    # 当前页码
    current_page = IntegerField(
        label="current_page",
        default=1,
        validators=[
            Optional(),
            NumberRange(min=1, max=9999, message='页码必须在1-9999之间'),  # 数字范围在1-9999之间
        ]
    )

    # 每页行数
    page_size = IntegerField(
        label="page_size",
        default=20,
        validators=[
            Optional(),
            NumberRange(min=1, max=50, message='每页行数必须在1-50之间'),
        ]
    )


# 通用分页查询工具
@dataclass
class Paginator:
    """分页器
    1执行paginate方法可以得到分页查询列表结果
    2执行之后对象中就包含所有需要的分页其他数据
    """
    total_page: int = 0  # 总页数
    total_record: int = 0  # 总条数
    current_page: int = 1  # 当前页数
    page_size: int = 20  # 每页条数

    def __init__(self, db: SQLAlchemy, req: PaginatorReq = None):
        # 有传递req 则给当前页码和每页行数复制
        if req is not None:
            self.current_page = req.current_page.data
            self.page_size = req.page_size.data
        self.db = db  # db属性仅在__ini__内声明,对象序列化(转JSON)时会排除该属性

    def paginate(self, select: Select) -> list[Any]:
        """
           对传入的查询工具对象进行分页查询处理
           self.db.session.query(XXXX).filter_by()
        """

        # 1.调用db.paginate进行数据分页
        p = self.db.paginate(
            select=select,  # 先传入默认的查询要求
            page=self.current_page,  # 当前页面
            per_page=self.page_size,  # 每页行数
            error_out=False,  # 当前页数如果超出范围是否会抛出404错误
        )

        # 2 计算总页数 总行数
        self.total_record = p.total
        self.total_page = math.ceil(p.total / self.page_size)  # 向上取整

        # 3 返回分页查询的列表结果
        return p.items


# 定义数据模型类 包装分页查询结果列表 以及 分页器对象
# 用于视图函数对结果进行JSON序列化
@dataclass
class PageModel:
    list: list[Any]
    paginator: Paginator
