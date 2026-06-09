from uuid import UUID
from celery import shared_task


@shared_task
def delete_dataset(dataset_id: UUID) -> None:
    """根据传递的知识库id删除特定的知识库信息"""
    from internal.service import IndexingService
    # 使用injector 注入indexing_service对象
    from app.http.module import injector
    indexing_service = injector.get(IndexingService)
    indexing_service.delete_dataset(dataset_id)
