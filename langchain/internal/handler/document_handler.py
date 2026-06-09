from dataclasses import dataclass
from uuid import UUID

from flask import request
from flask_login import login_required, current_user
from injector import inject

from internal.schema.document_schema import (
    CreateDocumentsReq,
    CreateDocumentsResp,
    UpdateDocumentEnabledReq,
    GetDocumentResp, UpdateDocumentNameReq, GetDocumentsWithPageReq, GetDocumentsWithPageResp,
)
from internal.service import DocumentService
from pkg.paginator import PageModel
from pkg.response import validation_error_json, success_json, success_message


@inject
@dataclass
class DocumentHandler:
    """文档处理器"""
    # 依赖注入
    document_service: DocumentService

    @login_required
    def create_documents(self, dataset_id: UUID):
        """知识库新增/上传文档列表"""
        # 1 获取请求参数并校验
        req = CreateDocumentsReq()
        if not req.validate():
            return validation_error_json(req.errors)

        # 2 调用服务并创建文档，返回文档实体列表+处理批次组成的元祖
        documents, batch = self.document_service.create_documents(
            dataset_id=dataset_id,
            **req.data,
            account=current_user,
        )

        # 3.生成响应结构并返回
        resp = CreateDocumentsResp()
        # 将service返回的结果组合成元祖,再转换成响应结果对象
        return success_json(data=resp.dump((documents, batch)))

    # 根据传递的知识库id+批处理标识获取文档的状态
    @login_required
    def get_documents_status(self, dataset_id: UUID, batch: str):
        """根据传递的知识库id+批处理标识获取文档的状态"""
        # 调用业务服务层完成处理过程 返回文档状态字典列表
        documents_status = self.document_service.get_documents_status(
            dataset_id=dataset_id,
            batch=batch,
            account=current_user,
        )
        # 响应结果
        return success_json(data=documents_status)

    # 1
    # 根据传递的知识库id+文档id获取文档详情信息
    @login_required
    def get_document(self, dataset_id: UUID, document_id: UUID):
        """根据传递的知识库id+文档id获取文档详情信息"""

        # 返回Document模型类对象
        # 完成授权认证模块后 增加account参数 current_user方法获取
        document = self.document_service.get_document(
            dataset_id,
            document_id,
            account=current_user,
        )
        # 包装响应结果类型
        resp = GetDocumentResp()
        # Document模型类对象转换为字典,再响应结果
        return success_json(resp.dump(document))

    # 2
    # 根据传递的知识库id+文档id更新对应文档的名称信息
    @login_required
    def update_document_name(self, dataset_id: UUID, document_id: UUID):
        """根据传递的知识库id+文档id更新对应文档的名称信息"""
        # 1.提取请求并校验数据
        req = UpdateDocumentNameReq()
        if not req.validate():
            return validation_error_json(req.errors)

        # 2.调用服务更新文档的名称信息
        # 完成授权认证模块后 增加account参数 current_user方法获取
        self.document_service.update_document(
            dataset_id,
            document_id,
            name=req.name.data,
            account=current_user,
        )

        return success_message("更新文档名称成功")

    # 3
    # 根据传递的知识库id获取文档分页列表数据
    @login_required
    def get_documents_with_page(self, dataset_id: UUID):
        """根据传递的知识库id获取文档分页列表数据"""
        # 1.提取请求数据并校验 get请求中的params需要作为参数传入
        req = GetDocumentsWithPageReq(request.args)
        if not req.validate():
            return validation_error_json(req.errors)

        # 2.调用服务获取分页列表数据以及分页数据
        # 完成授权认证模块后 增加account参数 current_user方法获取
        documents, paginator = self.document_service.get_documents_with_page(
            dataset_id,
            req,
            account=current_user,
        )

        # 3.构建响应结构并映射 结果会有多条数据
        resp = GetDocumentsWithPageResp(many=True)
        # 结果封装为 PageModel
        return success_json(
            PageModel(list=resp.dump(documents), paginator=paginator)
        )

    # 根据传递的知识库id+文档id更新指定文档的启用状态
    @login_required
    def update_document_enabled(
            self,
            dataset_id: UUID,
            document_id: UUID
    ):
        """根据传递的知识库id+文档id更新指定文档的启用状态"""
        # 1.提取请求并校验
        req = UpdateDocumentEnabledReq()
        if not req.validate():
            return validation_error_json(req.errors)

        # 2.调用服务更新指定文档的状态
        self.document_service.update_document_enabled(
            dataset_id=dataset_id,
            document_id=document_id,
            enabled=req.enabled.data,
            account=current_user,
        )

        # 3.响应成功
        return success_message(msg="更改文档启用状态成功")

    # 根据传递的知识库id+文档id删除指定的文档信息
    @login_required
    def delete_document(self, dataset_id: UUID, document_id: UUID):
        """根据传递的知识库id+文档id删除指定的文档信息"""

        self.document_service.delete_document(
            dataset_id,
            document_id,
            account=current_user,
        )

        return success_message("删除文档成功")
