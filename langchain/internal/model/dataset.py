
from sqlalchemy import (
    Column,
    UUID,
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    PrimaryKeyConstraint,
    text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from internal.extension.database_extension import db
from .upload_file import UploadFile
from .app import AppDatasetJoin

# 知识库
class Dataset(db.Model):
    """知识库表"""
    __tablename__ = "dataset"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_dataset_id"),
    )
    # 主键
    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    # 账号ID
    account_id = Column(UUID, nullable=False)
    # 名称
    name = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # 图片
    icon = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # 描述
    description = Column(Text, nullable=False, server_default=text("''::text"))

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
    )

    # 只读属性 关联知识库对应的文档对象列表
    @property
    def document_count(self) -> int:
        """只读属性，获取知识库下的文档数"""
        return (
            db.session.
            query(func.count(Document.id)).
            filter(Document.dataset_id == self.id).
            scalar()  # 返回单行结果的第一列
        )

    # 只读属性 计算知识库的命中次数
    @property
    def hit_count(self) -> int:
        """只读属性，获取该知识库下所有片段的命中次数"""
        # coalesce 如果第一个结果为None 则选择0返回，否则返回结果
        return (
            db.session.
            query(func.coalesce(func.sum(Segment.hit_count), 0)).
            filter(Segment.dataset_id == self.id).
            scalar()
        )

    # 只读属性 计算该知识库关联的应用数量
    @property
    def related_app_count(self) -> int:
        """只读属性，获取该知识库关联的应用数"""
        return (
            db.session.
            query(func.count(AppDatasetJoin.id)).
            filter(AppDatasetJoin.dataset_id == self.id).
            scalar()
        )

    # 只读属性 计算该知识库下的字符总数
    @property
    def character_count(self) -> int:
        """只读属性，获取该知识库下的字符总数"""
        return (
            db.session.
            query(func.coalesce(func.sum(Document.character_count), 0)).
            filter(Document.dataset_id == self.id).
            scalar()
        )
        #  func.coalesce 如果该列结果为None 默认为0

# 文档 后续使用时 一定要注意区分langchain中的Document类(LCDocument) 与数据库model中的Document类
class Document(db.Model):
    """文档表模型"""
    __tablename__ = "document"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_document_id"),
    )

    # ID
    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    # 账号ID
    account_id = Column(UUID, nullable=False)
    # 知识库ID
    dataset_id = Column(UUID, nullable=False)
    # 上传文件ID
    upload_file_id = Column(UUID, nullable=False)
    # 处理规则ID
    process_rule_id = Column(UUID, nullable=False)
    # 批次
    batch = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # 名称
    name = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # 位置
    position = Column(Integer, nullable=False, server_default=text("1"))
    # 字数
    character_count = Column(Integer, nullable=False, server_default=text("0"))
    # token数
    token_count = Column(Integer, nullable=False, server_default=text("0"))
    # 处理开始时间
    processing_started_at = Column(DateTime, nullable=True)
    # 解析完成时间
    parsing_completed_at = Column(DateTime, nullable=True)
    # 分割完成时间
    splitting_completed_at = Column(DateTime, nullable=True)
    # 索引构建完成时间
    indexing_completed_at = Column(DateTime, nullable=True)
    # 完成时间
    completed_at = Column(DateTime, nullable=True)
    # 解析停止时间
    stopped_at = Column(DateTime, nullable=True)
    # 解析停止的错误信息
    error = Column(Text, nullable=False, server_default=text("''::text"))
    # 是否可用
    enabled = Column(Boolean, nullable=False, server_default=text("false"))
    # 禁用时间
    disabled_at = Column(DateTime, nullable=True)
    # 状态 默认为等待中
    status = Column(String(255), nullable=False, server_default=text("'waiting'::character varying"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

    # 只读属性 返回文档对应的腾讯云COS上传文件 upload_file_id
    # "UploadFile" 向前引用 避免循环导入
    @property
    def upload_file(self)->"UploadFile":
        return db.session.query(UploadFile).filter(
            UploadFile.id == self.upload_file_id
        ).one_or_none()

    # 只读属性 获取文档处理规则
    @property
    def process_rule(self)->"ProcessRule":
        return db.session.query(ProcessRule).filter(
            ProcessRule.id == self.process_rule_id
        ).one_or_none()

    # 只读属性 文档的片段数量
    @property
    def segment_count(self) -> int:
        return db.session.query(func.count(Segment.id)).filter(
            Segment.document_id == self.id,
        ).scalar()
    # 只读属性 文档下所有片段的命中次数总和
    @property
    def hit_count(self) -> int:
        return db.session.query(func.coalesce(func.sum(Segment.hit_count), 0)).filter(
            Segment.document_id == self.id,
        ).scalar()

# 片段
class Segment(db.Model):
    """片段表模型"""
    __tablename__ = "segment"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_segment_id"),
    )

    # ID
    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    # 账号ID
    account_id = Column(UUID, nullable=False)
    # 知识库ID
    dataset_id = Column(UUID, nullable=False)
    # 文档ID
    document_id = Column(UUID, nullable=False)
    # 向量库中的节点ID
    node_id = Column(UUID, nullable=False)
    # 位置
    position = Column(Integer, nullable=False, server_default=text("1"))
    # 内容
    content = Column(Text, nullable=False, server_default=text("''::text"))
    # 文本长度
    character_count = Column(Integer, nullable=False, server_default=text("0"))
    # token长度
    token_count = Column(Integer, nullable=False, server_default=text("0"))
    # 关键词列表 JSONB类型
    keywords = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    # 内容生成的HASH值
    hash = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # 命中次数
    hit_count = Column(Integer, nullable=False, server_default=text("0"))
    # 是否可用
    enabled = Column(Boolean, nullable=False, server_default=text("false"))
    # 禁用时间
    disabled_at = Column(DateTime, nullable=True)
    # 处理开始时间
    processing_started_at = Column(DateTime, nullable=True)
    # 索引构建完成时间
    indexing_completed_at = Column(DateTime, nullable=True)
    # 解析完成时间
    completed_at = Column(DateTime, nullable=True)
    # 解析错误停止时间
    stopped_at = Column(DateTime, nullable=True)
    # 解析错误信息
    error = Column(Text, nullable=False, server_default=text("''::text"))
    # 状态
    status = Column(String(255), nullable=False, server_default=text("'waiting'::character varying"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

    # 只读属性 获取关联的document实体
    @property
    def document(self)->"Document":
        return db.session.query(Document).get(self.document_id)
# 关键词
class KeywordTable(db.Model):
    """关键词表模型"""
    __tablename__ = "keyword_table"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_keyword_table_id"),
    )

    # ID
    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    # 知识库ID
    dataset_id = Column(UUID, nullable=False)
    # 关键词 与 片段ID 的映射关系 JSONB类型
    '''
{
  "2024": [
    "68a6df4a-d102-4a25-80ed-16d11fe23a9d"
  ],
  "4o": [
    "9e4ea176-e4d9-4bee-92dd-7acf69fa7376"
  ],
  "GPT": [
    "9e4ea176-e4d9-4bee-92dd-7acf69fa7376",
    "68a6df4a-d102-4a25-80ed-16d11fe23a9d",
    "663fca2a-f986-471a-84a9-6606b2b25ed2",
    "551e2389-62d8-4be9-afef-e91fb28fb07b"
  ]
}
    '''
    keyword_table = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

# 知识库查询历史
class DatasetQuery(db.Model):
    """知识库查询表模型"""
    __tablename__ = "dataset_query"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_dataset_query_id"),
    )
    # ID
    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    # 知识库表
    dataset_id = Column(UUID, nullable=False)
    # 查询语句
    query = Column(Text, nullable=False, server_default=text("''::text"))
    # 数据来源
    source = Column(String(255), nullable=False, server_default=text("'HitTesting'::character varying"))
    # 产生查询的APPID
    source_app_id = Column(UUID, nullable=True)
    # 执行查询的账号ID
    created_by = Column(UUID, nullable=True)

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))


# 处理规则
class ProcessRule(db.Model):
    """文档处理规则表模型"""
    __tablename__ = "process_rule"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_process_rule_id"),
    )
    # ID
    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    # 账号ID
    account_id = Column(UUID, nullable=False)
    # 知识库ID
    dataset_id = Column(UUID, nullable=False)
    # 模式 默认值为自动 可选自定义
    mode = Column(String(255), nullable=False, server_default=text("'automic'::character varying"))
    # 处理规则 类型JSONB
    '''
{
  "segment": {
    "chunk_size": 500,
    "separators": [
      "\n\n",
      "\n",
      "。|！|？",
      "\\.\\s|\\!\\s|\\?\\s",
      "；|;\\s",
      "，|,\\s",
      " ",
      ""
    ],
    "chunk_overlap": 50
  },
  "pre_process_rules": [
    {
      "id": "remove_extra_space",
      "enabled": true
    },
    {
      "id": "remove_url_and_email",
      "enabled": true
    }
  ]
}
    '''
    rule = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
