from dataclasses import dataclass

from flask_login import login_required, current_user
from injector import inject


from internal.schema import UploadFileReq, UploadImageReq, UploadFileResp
from internal.service import CosService
from pkg.response import validation_error_json, success_json


@inject
@dataclass
class UploadFileHandler:
    # 依赖注入
    cos_service: CosService

    # 视图方法 文件上传至腾讯云COS
    @login_required
    def upload_file(self):
        """上传文件/文档"""
        # 1.构建请求并校验
        req = UploadFileReq() # 自动识别是form还是JSON
        if not req.validate():
            return validation_error_json(req.errors)

        # 2.调用业务方法 上传文件并获取记录 返回UploadFile数据模型对象
        upload_file = self.cos_service.upload_file(
            current_user,
            req.file.data,  # FileStorage
        )

        # 3.响应结果
        resp = UploadFileResp()
        return success_json(data=resp.dump(upload_file))

    # 图片文件上传
    @login_required
    def upload_image(self):
        """上传图片"""
        # 1.构建请求并校验
        req = UploadImageReq()
        if not req.validate():
            return validation_error_json(req.errors)

        # 2.调用服务并上传文件 并同步保存至数据库
        upload_file = self.cos_service.upload_file(
            current_user,
            req.file.data,
            only_image=True,# 只允许上传图片文件

        )

        # 3.获取图片的实际URL地址(文件也可以获取URL路径)
        image_url = self.cos_service.get_file_url(upload_file.key)

        return success_json({"image_url": image_url})