from collections import Counter
from uuid import UUID

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.retrievers import BaseRetriever
from pydantic import Field
from langchain_core.documents import Document as LCDocument
from rich import segment

from internal.model import KeywordTable, Segment
from internal.service import JiebaService
from pkg.sqlalchemy import SQLAlchemy


class FullTextRetriever(BaseRetriever):
    """全文检索器"""
    db: SQLAlchemy
    # dataset id列表
    dataset_ids: list[UUID]
    # 分词服务
    jieba_service: JiebaService
    # 搜索关键词 包含K值
    search_kwargs: dict = Field(default_factory=dict)

    #  重写方法  _get_relevant_documents
    def _get_relevant_documents(
            self,
            query: str,
            *,
            run_manager: CallbackManagerForRetrieverRun,
    ) -> list[LCDocument]:
        """根据传递的query执行关键词检索获取LangChain文档列表"""
        # 1.从查询query中提取关键词列表
        query_keywords = self.jieba_service.extract_keywords(
            text=query,
            max_keyword_pre_chunk=10
        )

        # 2.1 查找指定知识库的关键词表列表数据 仅查询一个列 结果为元祖
        keyword_table_datas = self.db.session.query(
            KeywordTable,
        ).with_entities(
            KeywordTable.keyword_table,
        ).filter(
            KeywordTable.dataset_id.in_(self.dataset_ids),
        ).all()
        # 2.2 从结果元祖中提取唯一元素再组成列表, 每个关键词表数据都为字典(JSONB)
        # [({}),({}),({}),.....]-->[{kw:[sids]},{},{}]
        keyword_tables = [
            keyword_table for keyword_table, in keyword_table_datas
        ]

        # 3.遍历所有的知识库关键词表，找到匹配query关键词的segment_id列表
        all_segment_ids = []
        for keyword_table in keyword_tables:
            # 4.遍历每一个关键词表的每一项
            for keyword, segment_ids in keyword_table.items():
                # 5.如果数据存在于query_keywords内,则提取关键词对应的片段id列表
                if keyword in query_keywords:
                    all_segment_ids.extend(segment_ids)

        # 4.此时all_segment_ids中可能会包含重复的片段ID
        #  统计segment_id出现的频率,使用collections.Counter进行快速统计
        #  格式为[(segment_id, freq), (segment_id, freq), ...]
        id_counter = Counter(all_segment_ids)
        print("id_counter:", id_counter)

        # 5.仅提取前K条数据
        # 从search_kwargs提取参数k ,默认值为4
        k = self.search_kwargs.get("k", 4)
        print("k:", k)
        # 获取频率最高的前k条数据 结果结构为元祖列表 会按照频率的数量降序排序
        top_k_sg_ids = id_counter.most_common(k)
        print("top_k_sg_ids:", top_k_sg_ids)
        # [('e221c9f2-70b1-4319-9c95-ed63e421ff54', 3), ('12e008eb-65e2-4b52-a395-7a7e50987267', 3), ('bcd074da-0dfe-4a1c-aa6b-ab4d2404068c', 1),....]

        # 8.根据得到的id列表检索数据库得到片段列表信息
        segments = self.db.session.query(
            Segment,
        ).filter(
            Segment.id.in_([sid for sid, _ in top_k_sg_ids]),
        ).all()
        print("segments:", len(segments))
        # 将查询结果列表 转为字典 key为每个片段ID,值为片段本身
        segments_dict = {
            str(segment.id): segment for segment in segments
        }
        # 此时查询出的结果和 top_k_sg_ids 顺序很可能不一致
        print("segments_dict:", segments_dict.keys())

        # 9.根据频率进行排序 将segments调整为top_k_sg_ids一致
        sorted_segments = [
            segments_dict[str(id)]
            for id, freq in top_k_sg_ids if id in segments_dict
        ]
        print("sorted_segments:", len(sorted_segments))

        # 10.构建LangChain文档列表
        lc_documents = [
            LCDocument(
                page_content=segment.content,
                metadata={  # 元数据格式和相似性检索结果相同
                    "account_id": str(segment.account_id),
                    "dataset_id": str(segment.dataset_id),
                    "document_id": str(segment.document_id),
                    "segment_id": str(segment.id),
                    "node_id": str(segment.node_id),
                    "document_enabled": True,
                    "segment_enabled": True,
                    "score": 0,  # 全文检索得分永远为0
                }
            )
            for segment in sorted_segments
        ]

        # 返回LangChain文档列表
        return lc_documents