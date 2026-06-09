from enum import Enum

# 默认知识库描述格式化文本
DEFAULT_DATASET_DESCRIPTION_FORMATTER = "当你需要回答管理《{name}》问题的时候,可以引用该知识库。"


# 定义枚举 规定Document处理类型 自动与自定义
class ProcessType(str, Enum):
    AUTOMATIC = "automatic" # 使用项目中编辑好的默认规则
    CUSTOM = "custom"  # 用户传递自定义规则


# process rule 默认的文档处理规则
DEFAULT_PROCESS_RULE = {
    "mode": "automatic",  # mode 默认为自动
    "rule": {  # rule默认规则
        "pre_process_rules": [  # 预处理规则
            # 是否 移除多余的特殊字符
            {"id": "remove_extra_space", "enabled": True},
            # 移除URL与email地址
            {"id": "remove_url_and_email", "enabled": True},
        ],
        "segment": {  # 分段处理规则
            "separators": [  # 支持中文语言的分隔符列表
                "\n\n",
                "\n",
                "。|！|？",
                "\.\s|\!\s|\?\s",  # 英文标点符号后面通常需要加空格
                "；|;\s",
                "，|,\s",
                " ",
                ""
            ],
            "chunk_size": 500,  # 分割后片段大小
            "chunk_overlap": 50,  # 片段重叠区大小
        }
    }
}

# 文档状态类型枚举
class DocumentStatus(str, Enum):
    """文档状态类型枚举"""
    WAITING = "waiting"
    PARSING = "parsing"
    SPLITTING = "splitting"
    INDEXING = "indexing"
    COMPLETED = "completed"
    ERROR = "error"

# 片段状态类型枚举
class SegmentStatus(str, Enum):
    """片段状态类型枚举"""
    WAITING = "waiting"
    INDEXING = "indexing"  # 片段需要进行关键词提取
    COMPLETED = "completed"
    ERROR = "error"

# 检索策略类型枚举
class RetrievalStrategy(str, Enum):
    """检索策略类型枚举"""
    FULL_TEXT = "full_text"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


# 检索来源
class RetrievalSource(str, Enum):
    """检索来源"""
    HIT_TESTING = "hit_testing"
    APP = "app"
    DEBUGGER="debugger"

