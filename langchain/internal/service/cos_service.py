import hashlib
import os
import uuid
from dataclasses import dataclass
from datetime import datetime

from injector import inject
from qcloud_cos import CosS3Client, CosConfig
from werkzeug.datastructures import FileStorage

from internal.entity.upload_file_entity import (
    ALLOWED_IMAGE_EXTENSION,
    ALLOWED_DOCUMENT_EXTENSION,
)
from internal.exception import FailException
from internal.model import UploadFile, Account
from .upload_file_service import UploadFileService


@inject
@dataclass
class CosService:
    # 依赖注入
    upload_file_service: UploadFileService

    # 业务方法:上传文件到腾讯云cos对象存储,文件数据保存至数据库,上传后返回文件的信息
    def upload_file(
            self,
            account: Account,
            file: FileStorage,  # 表单上传的文件数据
            only_image: bool = False,  # 上传内容是否是图片

    ) -> UploadFile:
        """上传文件到腾讯云cos对象存储，上传后返回文件的信息"""
        # todo:等待授权认证模块完成进行切换调整 虚拟一个账号ID
        # account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        account_id = str(account.id)

        # 1.提取文件扩展名并检测是否可以上传
        filename = file.filename  # 原始文件名
        # 截取扩展名  rsplit:右边（末尾）开始分割
        # maxsplit: 参数指定最大分割次数
        # 如果上传的文件没有后缀名 则直接赋予 ""
        extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
        if extension.lower() not in ALLOWED_IMAGE_EXTENSION + ALLOWED_DOCUMENT_EXTENSION:
            # 允许图片或文档文件
            raise FailException(f"该.{extension}扩展的文件不允许上传")
        elif only_image and extension.lower() not in ALLOWED_IMAGE_EXTENSION:
            # 如果只上传图片
            raise FailException(
                f"该.{extension}扩展的文件不支持上传，请上传正确的图片"
            )

        # 2 获取腾讯云COS 客户端+存储桶名字
        client = self._get_client()
        bucket = self._get_bucket()

        # 3.生成一个随机的名字
        random_filename = str(uuid.uuid4()) + "." + extension
        now = datetime.now()
        # 存储于COS的完整路径
        upload_filename = f'{now.year}/{now.month}/{now.day:02d}/{random_filename}'

        # 4 读取请求传递的文件内容 流
        file_content = file.stream.read()

        # 5 将数据上传至COS
        try:
            client.put_object(
                Bucket=bucket,
                Body=file_content,
                Key=upload_filename,
            )
        except Exception as e:
            raise FailException("文件上传失败,请稍后重试")

        # 6.创建upload_file记录 调用UploadFileService.create_upload_file
        upload_file = self.upload_file_service.create_upload_file(
            account_id=account_id,
            name=filename, # 原文件名
            key=upload_filename, # COS端的文件路径
            size=len(file_content), # 文件大小
            extension=extension, # 扩展名
            mime_type=file.mimetype, # mime类型
            hash=hashlib.sha256(file_content).hexdigest(), # 文件内容HASH值
        )
        # 返回UploadFile数据模型对象
        return upload_file



    # 读取配置文件 加载成腾讯云COS客户端对象
    @classmethod
    def _get_client(cls) -> CosS3Client:
        """获取腾讯云cos对象存储客户端"""
        conf = CosConfig(  # 读env文件
            Region=os.getenv("COS_REGION"),  # 地区信息
            SecretId=os.getenv("COS_SECRET_ID"),  # 秘钥ID
            SecretKey=os.getenv("COS_SECRET_KEY"),  # 秘钥key
            Token=None,
            Scheme=os.getenv("COS_SCHEME", "https"),  # 协议类型 http+ssl
        )
        return CosS3Client(conf)

    # 读取COS_BUCKET存储桶名称 配置信息
    @classmethod
    def _get_bucket(cls) -> str:
        """获取存储桶的名字"""
        return os.getenv("COS_BUCKET")

    # 获取腾讯云文件的URL地址(图片上传之后响应结果只需要URL)
    @classmethod
    def get_file_url(cls, key: str) -> str:
        """根据传递的cos云端key获取图片的实际URL地址"""
        # 如果配置了自定义的COS域名
        cos_domain = os.getenv("COS_DOMAIN")

        # 未配置自定义的COS域名 则使用腾讯云提供的文件域名
        if not cos_domain:
            bucket = os.getenv("COS_BUCKET")
            scheme = os.getenv("COS_SCHEME")
            region = os.getenv("COS_REGION")
            cos_domain = f"{scheme}://{bucket}.cos.{region}.myqcloud.com"
        # 返回完整URL路径
        return f"{cos_domain}/{key}"

    # 业务方法:下载cos云端的文件到本地的指定路径
    def download_file(self, key: str,target_file_path:str) :
        """下载cos云端的文件到本地的指定路径"""
        client = self._get_client()
        bucket = self._get_bucket()
        # 使用client下载文件
        client.download_file(
            Bucket=bucket,
            Key=key,
            DestFilePath=target_file_path,
        )