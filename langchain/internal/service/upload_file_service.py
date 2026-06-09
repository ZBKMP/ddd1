from dataclasses import dataclass

from injector import inject

from internal.model import UploadFile
from internal.service.base_service import BaseService
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class UploadFileService(BaseService):
    ''' 上传文件数据 数据库增删改查操作业务层 '''

    # 依赖注入
    db: SQLAlchemy

    # 继承自BaseService 完成文件数据的数据库添加操作
    def create_upload_file(self,**kwargs)->UploadFile:
        return self.create(UploadFile, **kwargs)