from uuid import UUID
from celery import shared_task


# 异步任务 根据传递的文档id列表构建知识库文档
@shared_task
def build_documents(document_ids: list[UUID]) -> None:
    """根据传递的文档id列表，构建文档"""
    # 需要哪个业务类 临时导入
    from internal.service.indexing_service import IndexingService
    # 使用injector 注入indexing_service对象
    from app.http.module import injector
    indexing_service = injector.get(IndexingService)
    # 调用 indexing_service 完成异步任务
    indexing_service.build_documents(document_ids)


# 异步任务  根据传递的文档id修改文档的enabled状态
@shared_task
def update_document_enabled(document_id: UUID) -> None:
    """根据传递的文档id修改文档的enabled状态"""
    from internal.service.indexing_service import IndexingService
    # 使用injector 注入indexing_service对象
    from app.http.module import injector
    indexing_service = injector.get(IndexingService)
    # 调用 indexing_service 完成异步任务
    indexing_service.update_document_enabled_keyword_service(document_id)


# 异步任务  根据传递的文档id+知识库id清除文档记录
@shared_task
def delete_document(dataset_id: UUID, document_id: UUID) -> None:
    """根据传递的文档id+知识库id清除文档记录"""
    from internal.service.indexing_service import IndexingService
    # 使用injector 注入indexing_service对象
    from app.http.module import injector
    indexing_service = injector.get(IndexingService)
    # 调用 indexing_service 完成异步任务
    indexing_service.delete_document_keyword_service(dataset_id, document_id)