import re
from dataclasses import dataclass
from typing import Callable

from injector import inject
from langchain_text_splitters import TextSplitter, RecursiveCharacterTextSplitter

from internal.model import ProcessRule


# 处理规则服务类
@inject
@dataclass
class ProcessRuleService:
    """处理规则服务"""

    # 根据处理规则 获取文档分割器(递归)
    @classmethod
    def get_text_splitter_by_process_rule(
            cls,
            # 处理规则
            process_rule: ProcessRule,
            # 计算token长度的函数(参数为str,返回值为int) 默认使用len函数
            length_function: Callable[[str], int] = len,
            # 其他额外参数
            **kwargs,
    ) -> TextSplitter:  # 返回文本分割器
        """根据传递的处理规则+长度计算函数，获取相应的文本分割器"""
        # 返回递归文本分割器  从处理规则中获取分割器需要的参数
        return RecursiveCharacterTextSplitter(
            chunk_size=process_rule.rule["segment"]["chunk_size"],  # 片段长度
            chunk_overlap=process_rule.rule["segment"]["chunk_overlap"],  # 重叠区域长度
            separators=process_rule.rule["segment"]["separators"],  # 分割父列表
            is_separator_regex=True,  # 分割符是否支持正则表达式
            length_function=length_function,  # 计算token长度的函数
            **kwargs,
        )

    # 根据处理规则 清除多余的字符串 (包含:空格 EMAIL URL)
    @classmethod
    def clean_text_by_process_rule(
            cls,
            text: str,  # document.page_content
            process_rule: ProcessRule  # 处理规则对象
    ) -> str:
        """根据传递的处理规则清除多余的字符串"""
        # 1.循环遍历所有预处理规则 按要求处理文本内容
        for pre_process_rule in process_rule.rule["pre_process_rules"]:
            # 2.遍历处理规则,如果规则id为remove_extra_space,且值为True,则删除多余空格
            if (pre_process_rule["id"] == "remove_extra_space"
                    and
                    pre_process_rule["enabled"] is True):
                # 如果出现连续的多个换行 换成两个换行
                pattern = r'\n{3,}'
                text = re.sub(pattern, "\n\n", text)
                # 特殊空格如果出现2次或以上 换成一个空格' '
                pattern = r'[\t\f\r\x20\u00a0\u1680\u180e\u2000-\u200a\u202f\u205f\u3000]{2,}'
                text = re.sub(pattern, " ", text)

            # 3.遍历处理规则,如果规则id为remove_url_and_email,且值为True,则删除多余的URL链接及邮箱
            if (pre_process_rule["id"] == "remove_url_and_email"
                    and
                    pre_process_rule["enabled"] is True):
                # 去掉邮箱
                pattern = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
                text = re.sub(pattern, '', text)
                # 去掉URL
                pattern = r'https?://[^\s]+'
                text = re.sub(pattern, '', text)

        # 返回处理之后的结果
        return text