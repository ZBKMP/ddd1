import copy
from dataclasses import dataclass
from uuid import UUID

from injector import inject
from redis import Redis

from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from internal.entity.cache_entity import LOCK_KEYWORD_TABLE_UPDATE_KEYWORD_TABLE, LOCK_EXPIRE_TIME
from internal.model import KeywordTable, Segment


# 知识库关键词表业务服务类
@inject
@dataclass
class KeywordTableService(BaseService):
    """知识库关键词表服务"""
    db: SQLAlchemy
    redis_client: Redis

    # 依据知识库ID获取对应关键词表
    def get_keyword_table_from_dataset_id(
            self,
            dataset_id: UUID
    ) -> KeywordTable:
        # 关键词表数据库查询
        keyword_table = self.db.session.query(KeywordTable).filter(
            KeywordTable.dataset_id == dataset_id,
        ).one_or_none()
        # 如果没有数据 表示还未记录任何知识库文档信息,则创建一个空字典
        if keyword_table is None:
            keyword_table = self.create(
                KeywordTable,
                dataset_id=dataset_id,
                keyword_table={}
            )
        # 返回查询结果或新建结果
        return keyword_table

    # 根据传递的知识库id+片段id列表，在关键词表中添加关键词
    def add_keyword_table_from_ids(
            self,
            dataset_id: UUID,
            segment_ids: list[UUID],  # 某文档下可以使用的片段列表
    ) -> None:
        """根据传递的知识库id+片段id列表，在关键词表中添加关键词"""
        # 1.将片段中的关键词信息同步更新到关键词表中,
        # 该操作需要针对当前 知识库id 进行上锁,避免在并发的情况下拿到错误的数据
        cache_key = LOCK_KEYWORD_TABLE_UPDATE_KEYWORD_TABLE.format(
            dataset_id=dataset_id
        )

        # 使用上下文方式 创建缓存锁
        with self.redis_client.lock(cache_key, timeout=LOCK_EXPIRE_TIME) as lock:
            # 2.从数据库中获取当前知识库的关键词表模型类对象
            keyword_table_record = self.get_keyword_table_from_dataset_id(
                dataset_id
            )

            # 去掉关键词表模型对象中关键词表字段内重复的片段ID (list->set) 生成一个新字典
            keyword_table = {
                field: set(value)
                for field, value in keyword_table_record.keyword_table.items()
            }

            # 3.根据segment_ids查找片段的关键词信息
            # 只查询Segment.id与Segment.keywords结果生成元祖
            segments = self.db.session.query(Segment).with_entities(
                Segment.id,
                Segment.keywords,  # 关键词列表
            ).filter(
                Segment.id.in_(segment_ids),
            ).all()

            # 4.循环将新关键词添加到原关键词表中
            for id, keywords in segments:  # 遍历每个片段
                for keyword in keywords:  # 遍历片段的每个关键词
                    # 如果该关键词不在原关键词表内 则为其创建一个新集合
                    if keyword not in keyword_table:
                        keyword_table[keyword] = set()
                    # 将片段ID加入到这个关键词对应的集合中
                    keyword_table[keyword].add(str(id))

            # 5.更新关键词表数据
            self.update(
                model_instance=keyword_table_record,
                keyword_table={
                    field: list(value)
                    for field, value in keyword_table.items()
                }
            )

    # 根据传递的知识库id+片段id列表删除对应关键词表中多余的片段ID数据
    def delete_keyword_table_from_ids(
            self,
            dataset_id: UUID,
            segment_ids: list[UUID]
    ) -> None:
        # 1.删除知识库关键词表里多余的片段ID数据，该操作需要上锁，
        #   避免在并发的情况下拿到错误的数据
        cache_key = LOCK_KEYWORD_TABLE_UPDATE_KEYWORD_TABLE.format(
            dataset_id=dataset_id
        )

        # redis的lock上下文,开启时会生成redis数据,执行完毕后自动删除redis数据
        with self.redis_client.lock(cache_key, timeout=LOCK_EXPIRE_TIME):
            # 2.从数据库中获取当前知识库的关键词表模型类对象
            keyword_table_record = self.get_keyword_table_from_dataset_id(
                dataset_id
            )
            # keyword_table字段为JSONB类型,实质为字典,使用copy深度复制一个副本
            keyword_table = copy.deepcopy(keyword_table_record.keyword_table)

            # 3.将片段id列表转换成集合
            # 将segment_ids 原为UUID列表 转换为字符串列表
            segment_ids_to_disable = set(
                [str(segment_id) for segment_id in segment_ids]
            )
            # 要删除的关键词集合
            keywords_to_delete = set()  # 空集合

            # 4.循环遍历所有关键词执行判断与更新
            for keyword, segment_ids in keyword_table.items():
                segment_ids = set(segment_ids)  # segment_ids列表转为集合
                # intersection判断是否存在交集
                # 存在则表示关键词表里存在这些片段ID的数据
                if segment_ids_to_disable.intersection(segment_ids):
                    # 执行删除操作,关键词表数据更新为ids_set
                    # 减去segment_ids_to_delete
                    keyword_table[keyword] = list(
                        # difference:前一个集合减去后一个集合 剩下的内容 (本质就是前一个减去两者之间的交集)
                        segment_ids.difference(segment_ids_to_disable)
                    )
                    '''   
                    kw               disabled
                ( A B C D )   -    ( G B C S ) = AD
    
                    '''
                    # 删除之后如果该关键词表变为空列表,则将其添加到
                    # keywords_to_delete列表中
                    if not keyword_table[keyword]:
                        keywords_to_delete.add(keyword)

            # 5 检测空关键词数据并删除
            for keyword in keywords_to_delete:
                # 删除字典内的某个key
                del keyword_table[keyword]

            # 6.将数据更新到关键词表中
            self.update(
                model_instance=keyword_table_record,
                keyword_table=keyword_table
            )
