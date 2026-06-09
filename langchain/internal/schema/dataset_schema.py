from flask_wtf import FlaskForm
from marshmallow import Schema, fields, pre_dump
from wtforms import StringField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, URL, Optional, AnyOf, NumberRange

from internal.entity.dataset_entity import RetrievalStrategy
from internal.lib import datetime_to_timestamp
from internal.model import Dataset, DatasetQuery
from pkg.paginator import PaginatorReq


# 创建知识库视图方法的request验证
class CreateDatasetReq(FlaskForm):
    """创建知识库请求"""
    # 知识库名称
    name = StringField("name", validators=[
        DataRequired("知识库名称不能为空"),
        Length(max=100, message="知识库名称长度不能超过100字符"),
    ])
    # 知识库图标 数据类型为URL
    icon = StringField("icon", validators=[
        DataRequired("知识库图标不能为空"),
        URL(message="知识库图标必须是图片URL地址"),
    ])
    # 知识库描述 可选值
    description = StringField(
        "description", default="", validators=[
            Optional(),
            Length(max=2000, message="知识库描述长度不能超过2000字符")
        ])


# 根据ID查询知识库结果的响应
class GetDatasetResp(Schema):
    """获取知识库详情响应结构"""
    id = fields.UUID(dump_default="")  # ID
    name = fields.String(dump_default="")  # 知识库名称
    icon = fields.String(dump_default="")  # 知识库图标
    description = fields.String(dump_default="")  # 描述信息
    document_count = fields.Integer(dump_default=0)  # 文档数量
    hit_count = fields.Integer(dump_default=0)  # 命中次数
    related_app_count = fields.Integer(dump_default=0)  # 关联的应用数量
    character_count = fields.Integer(dump_default=0)  # 字符数
    updated_at = fields.Integer(dump_default=0)
    created_at = fields.Integer(dump_default=0)

    # 预先将数据结果包装为字典 以便转换为JSON
    @pre_dump
    def process_data(self, data: Dataset, **kwargs):
        return {
            "id": data.id,
            "name": data.name,
            "icon": data.icon,
            "description": data.description,
            "document_count": data.document_count,
            "hit_count": data.hit_count,
            "related_app_count": data.related_app_count,
            "character_count": data.character_count,
            "updated_at": int(data.updated_at.timestamp()),
            "created_at": int(data.created_at.timestamp()),
        }


# 更新知识库视图方法的request验证
class UpdateDatasetReq(FlaskForm):
    """更新知识库请求"""
    name = StringField("name", validators=[
        DataRequired("知识库名称不能为空"),
        Length(max=100, message="知识库名称长度不能超过100字符"),
    ])
    icon = StringField("icon", validators=[
        DataRequired("知识库图标不能为空"),
        URL(message="知识库图标必须是图片URL地址"),
    ])
    description = StringField(
        "description", default="",
        validators=[
            Optional(),
            Length(max=2000, message="知识库描述长度不能超过2000字符")
        ]
    )


# 分页查询 请求验证 父类PaginatorReq中包含分页参数:
#                current_page page_size
class GetDatasetsWithPageReq(PaginatorReq):
    """获取知识库分页列表请求数据"""
    search_word = StringField(
        "search_word", default="",
        validators=[
            Optional(),
        ]
    )


# 分页查询结果封装
class GetDatasetsWithPageResp(Schema):
    """获取知识库分页列表响应数据"""
    id = fields.UUID(dump_default="")
    name = fields.String(dump_default="")
    icon = fields.String(dump_default="")
    description = fields.String(dump_default="")
    document_count = fields.Integer(dump_default=0)
    related_app_count = fields.Integer(dump_default=0)
    character_count = fields.Integer(dump_default=0)
    updated_at = fields.Integer(dump_default=0)
    created_at = fields.Integer(dump_default=0)

    # 预先将数据结果包装为字典 以便转换为JSON
    @pre_dump
    def process_data(self, data: Dataset, **kwargs):
        return {
            "id": data.id,
            "name": data.name,
            "icon": data.icon,
            "description": data.description,
            "document_count": data.document_count,
            "related_app_count": data.related_app_count,
            "character_count": data.character_count,
            "updated_at": int(data.updated_at.timestamp()),
            "created_at": int(data.created_at.timestamp()),
        }


# 知识库召回测试请求验证类
class HitReq(FlaskForm):
    """知识库召回测试请求"""
    # 查询语句
    query = StringField("query", validators=[
        DataRequired("查询语句不能为空"),
        Length(max=200, message="查询语句的最大长度不能超过200")
    ])

    # 检索策略
    retrieval_strategy = StringField("retrieval_strategy", validators=[
        DataRequired("检索策略不能为空"),
        AnyOf(
            values=[item.value for item in RetrievalStrategy],
            message="检索策略格式错误"
        )
    ])

    # 最大召回数量
    k = IntegerField("k", validators=[
        DataRequired("最大召回数量不能为空"),
        NumberRange(min=1, max=10, message="最大召回数量的范围在1-10")
    ])

    # 相似度得分阈值
    score = FloatField("score", validators=[
        NumberRange(min=0, max=0.99, message="最小匹配度范围在0-0.99")
    ])


# 获取知识库最近查询响应结构封装类
class GetDatasetQueriesResp(Schema):
    """获取知识库最近查询响应结构"""
    id = fields.UUID(dump_default="")  # query结果 id
    dataset_id = fields.UUID(dump_default="")  # dataset_id
    query = fields.String(dump_default="")  # query语句
    source = fields.String(dump_default="")  # 查询来源
    created_at = fields.Integer(dump_default=0)

    # 预先将数据结果包装为字典 以便转换为JSON
    @pre_dump
    def process_data(self, data: DatasetQuery, **kwargs):
        return {
            "id": data.id,
            "dataset_id": data.dataset_id,
            "query": data.query,
            "source": data.source,
            "created_at": datetime_to_timestamp(data.created_at),
        }
