from flask_wtf import FlaskForm
from marshmallow import Schema, fields, pre_dump
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, AnyOf, ValidationError, Length, Optional

from internal.entity.dataset_entity import ProcessType, DEFAULT_PROCESS_RULE
from pkg.paginator import PaginatorReq
from .schema import (
    ListField,
    DictField,
)
from internal.model import Document
from internal.lib import datetime_to_timestamp


# 新增文档实体列表请求验证
class CreateDocumentsReq(FlaskForm):
    """创建文档请求"""
    # Upload文件ID列表 自定义ListField字段，用于存储列表型数据
    upload_file_ids = ListField("upload_file_ids", validators=[
        DataRequired("文件id列表不能为空"),
    ])

    # 处理类型
    process_type = StringField(
        "process_type",
        validators=[
            DataRequired("文件处理类型不能为空"),
            # 只支持 自动与自定义 两种规则 internal.entity.dataset_entity.ProcessType
            AnyOf(
                values=[ProcessType.AUTOMATIC, ProcessType.CUSTOM],
                message="处理类型格式错误"
            )
        ]
    )

    # 规则  自定义的 DictField 以替代wtforms下的DictField
    rule = DictField(
        label="rule"
    )

    #########################################################################
    # 后续新增方法 对参数rule进行校验
    def validate_rule(self, field: DictField) -> None:
        """校验上传处理规则"""
        # 1.校验处理模式，如果为自动，则为文档处理规则rule赋值为默认值
        if self.process_type.data == ProcessType.AUTOMATIC:
            # internal.entity.dataset_entity.DEFAULT_PROCESS_RULE
            field.data = DEFAULT_PROCESS_RULE["rule"]
        else:
            # 2.检测自定义处理类型下是否传递了rule 没有则抛出异常
            if not isinstance(field.data, dict) or len(field.data) == 0:
                raise ValidationError("自定义处理模式下，rule不能为空")

            # 3.校验预处理规则列表:pre_process_rules,非空且必须是列表
            if ("pre_process_rules" not in field.data
                    or
                    not isinstance(field.data["pre_process_rules"], list)):
                raise ValidationError("pre_process_rules必须为列表")

            # 4.校验预处理规则列表:pre_process_rules,检测其中的每一个配置
            unique_pre_process_rule_dict = {}  # 将预处理规则列表转换为字典
            for pre_process_rule in field.data["pre_process_rules"]:
                # 5.校验预处理规则中的id字段,非空,只允许是两个值中的一个
                if ("id" not in pre_process_rule
                        or
                        pre_process_rule["id"] not in
                        ["remove_extra_space", "remove_url_and_email"]):
                    raise ValidationError("预处理id格式错误")

                # 6 .校验预处理规则中的enabled字段,非空,且必须是布尔值
                if ("enabled" not in pre_process_rule
                        or
                        not isinstance(pre_process_rule["enabled"], bool)):
                    raise ValidationError("预处理enabled格式错误")

                # 7.将数据添加到字典中,key为pre_process_rule的id字段,
                #   值为 pre_process_rule 中的id字段值与enabled字段值,
                #   使用字典的目的是过滤掉重复的id,并在每个pre_process_rule中去掉多余的字段
                unique_pre_process_rule_dict[pre_process_rule["id"]] = {
                    "id": pre_process_rule["id"],
                    "enabled": pre_process_rule["enabled"],
                }

            # 8.判断pre_process_rules是否传递了两个处理规则 预处理规则长度必须为2
            if len(unique_pre_process_rule_dict) != 2:
                raise ValidationError("预处理规则格式错误，请重试尝试")

            # 9.将处理后的预处理规则字典转换回列表,并覆盖原数据
            field.data["pre_process_rules"] = list(
                unique_pre_process_rule_dict.values()
            )

            # 10.校验分段处理规则字段:segment,非空类型为字典
            if ("segment" not in field.data
                    or
                    not isinstance(field.data["segment"], dict)):
                raise ValidationError("分段设置不能为空且为字典")

            # 11. 校验segment中的分隔符字段:separators,非空,必须为列表,子元素为字符串
            if ("separators" not in field.data["segment"]
                    or
                    not isinstance(field.data["segment"]["separators"], list)):
                raise ValidationError("分隔符列表不能为空且为列表")
            # 分隔符列表的每个元素都必须是字符串
            for separator in field.data["segment"]["separators"]:
                if not isinstance(separator, str):
                    raise ValidationError("分隔符列表元素类型错误")
            if len(field.data["segment"]["separators"]) == 0:
                raise ValidationError("分隔符列表不能为空列表")

            # 12 校验segment中的分块大小:chunk_size,非空,必须为数字,范围100-1000
            if ("chunk_size" not in field.data["segment"]
                    or
                    not isinstance(field.data["segment"]["chunk_size"], int)):
                raise ValidationError("分割块大小不能为空且为整数")
            if (field.data["segment"]["chunk_size"] < 100
                    or
                    field.data["segment"]["chunk_size"] > 1000):
                raise ValidationError("分割块大小在100-1000")

            # 13.校验segment中的块重叠大小chunk_overlap,非空,必须为数字,
            if ("chunk_overlap" not in field.data["segment"]
                    or
                    not isinstance(field.data["segment"]["chunk_overlap"], int)):
                raise ValidationError("块重叠大小不能为空且为整数")
            #    范围0-chunk_size*0.5
            if not (
                    0 <= field.data["segment"]["chunk_overlap"] <= field.data["segment"]["chunk_size"] * 0.5
            ):
                raise ValidationError(
                    f"块重叠大小在0-{int(field.data['segment']['chunk_size'] * 0.5)}"
                )

            # 14.更新并剔除可能包含的多余数据,作为检测后的rule属性值
            field.data = {
                "pre_process_rules": field.data["pre_process_rules"],
                "segment": {
                    "separators": field.data["segment"]["separators"],
                    "chunk_size": field.data["segment"]["chunk_size"],
                    "chunk_overlap": field.data["segment"]["chunk_overlap"],
                }
            }

    #########################################################################


# 新增文档实体列表响应结构
class CreateDocumentsResp(Schema):
    """创建文档列表响应结构"""
    # 文档实体列表 --> 字典列表
    documents = fields.List(fields.Dict, dump_default=[])
    # 处理批次
    batch = fields.String(dump_default="")

    # 将 data: tuple[list[Document], str] 元祖类型结果转换为字典
    # 以便后续转换为JSON
    @pre_dump
    def process_data(self, data: tuple[list[Document], str], **kwargs):
        return {
            # 遍历文档实体列表 元祖的第一个元素
            "documents": [
                {
                    "id": document.id,
                    "name": document.name,
                    "status": document.status,
                    "created_at": int(document.created_at.timestamp())
                }
                for document in data[0]
            ],
            # 处理批次在元祖的第二个元素
            "batch": data[1]
        }

# 获取文档基础信息响应结构类
class GetDocumentResp(Schema):
    """获取文档基础信息响应结构"""
    id = fields.UUID(dump_default="")  # id
    dataset_id = fields.UUID(dump_default="")  # 知识库ID
    name = fields.String(dump_default="")  # 名称
    segment_count = fields.Integer(dump_default=0)  # 片段数量
    character_count = fields.Integer(dump_default=0)  # 字符总数
    hit_count = fields.Integer(dump_default=0)  # 命中次数
    position = fields.Integer(dump_default=0)  # 位置
    enabled = fields.Bool(dump_default=False)  # 是否可用
    disabled_at = fields.Integer(dump_default=0)  # 禁用时间
    status = fields.String(dump_default="")  # 状态
    error = fields.String(dump_default="")  # 错误信息
    updated_at = fields.Integer(dump_default=0)
    created_at = fields.Integer(dump_default=0)

    # 将数据转换成字典 以便后期转换为JSON
    @pre_dump
    def process_data(self, data: Document, **kwargs):
        return {
            "id": data.id,
            "dataset_id": data.dataset_id,
            "name": data.name,
            "segment_count": data.segment_count,  # Document实体只读属性
            "character_count": data.character_count,
            "hit_count": data.hit_count,  # Document实体只读属性
            "position": data.position,
            "enabled": data.enabled,
            "disabled_at": datetime_to_timestamp(data.disabled_at),
            "status": data.status,
            "error": data.error,
            "updated_at": datetime_to_timestamp(data.updated_at),
            "created_at": datetime_to_timestamp(data.created_at),
        }

# 获取文档分页列表请求验证类
class GetDocumentsWithPageReq(PaginatorReq):
    """获取文档分页列表请求"""
    # 搜索关键词
    search_word = StringField("search_word", default="", validators=[
        Optional() #可选参数
    ])
    # 分页参数继承自PaginatorReq


# 获取文档分页列表响应结构封装类
class GetDocumentsWithPageResp(Schema):
    """获取文档分页列表响应结构"""
    id = fields.UUID(dump_default="")
    name = fields.String(dump_default="")
    character_count = fields.Integer(dump_default=0)
    hit_count = fields.Integer(dump_default=0)
    position = fields.Integer(dump_default=0)
    enabled = fields.Bool(dump_default=False)
    disabled_at = fields.Integer(dump_default=0)
    status = fields.String(dump_default="")
    error = fields.String(dump_default="")
    updated_at = fields.Integer(dump_default=0)
    created_at = fields.Integer(dump_default=0)

    # 将数据转换成字典 以便后期转换为JSON
    @pre_dump
    def process_data(self, data: Document, **kwargs):
        return {
            "id": data.id,
            "name": data.name,
            "character_count": data.character_count,
            "hit_count": data.hit_count,
            "position": data.position,
            "enabled": data.enabled,
            "disabled_at": datetime_to_timestamp(data.disabled_at),
            "status": data.status,
            "error": data.error,
            "updated_at": datetime_to_timestamp(data.updated_at),
            "created_at": datetime_to_timestamp(data.created_at),
        }





# 更新文档名称信息请求验证类
class UpdateDocumentNameReq(FlaskForm):
    """更新文档名称信息请求"""
    name = StringField("name", validators=[
        DataRequired("文档名称不能为空"),
        Length(max=100, message="文档的名称长度不能超过100")
    ])






# 更新文档启用状态请求验证类
class UpdateDocumentEnabledReq(FlaskForm):
    """更新文档启用状态请求"""
    # 参数:是否可用 bool类型
    enabled = BooleanField("enabled")

    # 数据验证方法
    def validate_enabled(self, field: BooleanField) -> None:
        """校验文档启用状态enabled"""
        if not isinstance(field.data, bool):
            raise ValidationError("enabled状态不能为空且必须为布尔值")




