from dataclasses import dataclass
from injector import inject
import jieba.analyse
from jieba.analyse import default_tfidf

from internal.entity.jieba_entity import STOPWORD_SET


# jieba分词服务
@inject
@dataclass
class JiebaService:
    """jieba分词服务"""

    def __init__(self):
        """构造函数，扩展jieba的停用词 在停止词列表中的关键词，
                                   不会被统计 结果中去掉语气词等无意义的词"""
        default_tfidf.stop_words = STOPWORD_SET

    # 业务方法 从文本中提取出指定最大数量的关键词
    @classmethod
    def extract_keywords(
            cls,
            text: str,
            max_keyword_pre_chunk: int = 10
    ) -> list[str]:
        """根据输入的文本，提取对应文本的关键词列表"""
        return jieba.analyse.extract_tags(
            sentence=text,
            topK=max_keyword_pre_chunk,
        )
