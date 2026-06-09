from injector import inject
from dataclasses import dataclass
from flask import Flask, Blueprint

from internal.handler import (
    AppHandler,
    BuiltinToolHandler,
    ApiToolHandler,
    UploadFileHandler,
    DatasetHandler,
    DocumentHandler,
    SegmentHandler,
    OAuthHandler, AccountHandler, AuthHandler,
)
from internal.schema import GetCurrentUserResp


# 路由类 增加inject装饰器,可由Inject创建Router对象 ,以便注入给需要Router的类


@inject
@dataclass
class Router:
    # 将handler中的handler类作为属性导入
    app_handler: AppHandler
    builtin_tool_handler: BuiltinToolHandler
    api_tool_handler: ApiToolHandler
    upload_file_handler: UploadFileHandler
    dataset_handler: DatasetHandler
    document_handler: DocumentHandler
    segment_handler: SegmentHandler
    oauth_handler: OAuthHandler
    account_handler: AccountHandler
    auth_handler: AuthHandler

    def register_route(self, app: Flask):
        """注册路由 以Flask对象为参数"""
        # 1.创建蓝图 该蓝图用于表示所用从web网页传递来的请求
        bp = Blueprint('llmops', __name__, url_prefix='')

        # 2.为项目中所有视图函数编辑路由
        # 2.1 为AppHandler中的ping方法配置路由
        bp.add_url_rule(
            rule="/ping",
            methods=["GET"],
            view_func=self.app_handler.ping
        )

        # 2.2 AppHandler debug方法
        bp.add_url_rule(
            rule="/apps/<uuid:app_id>/debug",
            methods=["POST"],
            view_func=self.app_handler.debug3
        )

        # 2.3  增加路由 测试create_app业务方法
        bp.add_url_rule(
            rule="/apps",
            methods=["post"],
            view_func=self.app_handler.create_app
        )

        # 2.4 增加路由 测试get_app业务方法 增加路径参数
        bp.add_url_rule("/apps/<uuid:id>", methods=["GET"],
                        view_func=self.app_handler.get_app)
        # 2.5 增加路由 测试update_app业务方法 增加路径参数
        bp.add_url_rule("/apps/<uuid:id>", methods=["POST"],
                        view_func=self.app_handler.update_app)
        # 2.6 增加路由 测试delete_app业务方法 增加路径参数
        bp.add_url_rule("/apps/<uuid:id>/delete", methods=["POST"],
                        view_func=self.app_handler.delete_app)

        # 2.7 增加 builtin_tool_handler.get_builtin_tools
        #     获取所有provider信息及内置工具信息
        bp.add_url_rule("/builtin-tools",
                        methods=["GET"],
                        view_func=self.builtin_tool_handler.get_builtin_tools)
        # 2.8 增加 builtin_tool_handler.get_provider_tool 根据提供商信息及工具名称获取指定工具
        bp.add_url_rule("/builtin-tools/<string:provider_name>/tools/<string:tool_name>",
                        methods=["GET"],
                        view_func=self.builtin_tool_handler.get_provider_tool)

        # 2.9 增加builtin_tool_handler.get_provider_icon 获取供应商图标ICON 所有分类信息
        bp.add_url_rule("/builtin-tools/<string:provider_name>/icon",
                        methods=["GET"],
                        view_func=self.builtin_tool_handler.get_provider_icon)

        # 2.10 增加builtin_tool_handler.get_categories 获取所有分类信息
        bp.add_url_rule("/builtin-tools/categories",
                        methods=["GET"],
                        view_func=self.builtin_tool_handler.get_categories)

        # 2.11 增加 ApiToolHandler validate_openai_schema 用于验证请求中openapi_schema参数格式是否正确
        bp.add_url_rule('/api-tools/validate_openapi_schema', methods=["POST"],
                        view_func=self.api_tool_handler.validate_openapi_schema)

        # 2.12 增加ApiToolHandler  create_api_tool 用于新增api_tool信息到数据库
        bp.add_url_rule('/api-tools', methods=["POST"],
                        view_func=self.api_tool_handler.create_api_tool_provider)

        # 2.13 增加ApiToolHandler  get_api_tool_provider 用于查询api_tool_provider信息
        bp.add_url_rule('/api-tools/<uuid:provider_id>', methods=["GET"],
                        view_func=self.api_tool_handler.get_api_tool_provider)

        # 2.14 增加ApiToolHandler  get_api_tool 用于查询api_tool信息
        bp.add_url_rule('/api-tools/<uuid:provider_id>/tools/<string:tool_name>', methods=["GET"],
                        view_func=self.api_tool_handler.get_api_tool)

        # 2.15 增加ApiToolHandler  delete_api_tool_provider 用于删除api_tool_provide及其工具信息
        bp.add_url_rule('/api-tools/<uuid:provider_id>/delete', methods=["POST"],
                        view_func=self.api_tool_handler.delete_api_tool_provider)

        # 2.16 增加ApiToolHandler  get_api_tools_providers_with_page 自定义API工具数据分页查询
        bp.add_url_rule('/api-tools', methods=["GET"],
                        view_func=self.api_tool_handler.get_api_tools_providers_with_page)

        # 2.17 增加ApiToolHandler update_api_tool_provider 用于修改api_tool_provide信息
        bp.add_url_rule('/api-tools/<uuid:provider_id>', methods=["POST"],
                        view_func=self.api_tool_handler.update_api_tool_provider)

        # 2.18 增加 UploadFileHandler upload_file 用于上传文件至腾讯云COS
        bp.add_url_rule('/upload-files/file', methods=["POST"],
                        view_func=self.upload_file_handler.upload_file)

        # 2.19 增加 UploadFileHandler upload_image 用于上传图片至腾讯云COS
        bp.add_url_rule('/upload-files/image', methods=["POST"],
                        view_func=self.upload_file_handler.upload_image)

        # 2.20 增加 DatasetHandler 中 增删改查方法配置路由
        bp.add_url_rule('/datasets', methods=["GET"],
                        view_func=self.dataset_handler.get_datasets_with_page)
        bp.add_url_rule('/datasets', methods=["POST"],
                        view_func=self.dataset_handler.create_dataset)
        bp.add_url_rule('/datasets/<uuid:dataset_id>', methods=["GET"],
                        view_func=self.dataset_handler.get_dataset)
        bp.add_url_rule('/datasets/<uuid:dataset_id>', methods=["POST"],
                        view_func=self.dataset_handler.update_dataset)

        # 2.21 增加 DatasetHandler 中embeddings_query 方法配置路由
        bp.add_url_rule('/datasets/embeddings', methods=["GET"],
                        view_func=self.dataset_handler.embeddings_query)

        # 2.22 增加 DocumentHandler 中create_documents 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/documents', methods=["POST"],
                        view_func=self.document_handler.create_documents)

        # 2.23 增加 DatasetHandler 中hit方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/hit', methods=["POST"],
                        view_func=self.dataset_handler.hit)  # hit_test --> hit

        # 2.24 增加 DocumentHandler 中 get_documents_status 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/documents/batch/<string:batch>',
                        methods=["GET"],
                        view_func=self.document_handler.get_documents_status)

        # 2.25 增加 DocumentHandler 中 get_document 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/documents/<uuid:document_id>',
                        methods=["GET"],
                        view_func=self.document_handler.get_document)

        # 2.26 增加 DocumentHandler 中 update_document_name 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/name',
                        methods=["POST"],
                        view_func=self.document_handler.update_document_name)

        # 2.27 增加 DocumentHandler 中 get_documents_with_page 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/documents',
                        methods=["GET"],
                        view_func=self.document_handler.get_documents_with_page)

        # 2.28 增加 DocumentHandler 中 update_document_enabled 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/enabled',
                        methods=["POST"],
                        view_func=self.document_handler.update_document_enabled)

        # 2.29 增加 DocumentHandler 中 delete_document 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/delete',
                        methods=["POST"],
                        view_func=self.document_handler.delete_document)

        # 2.30 增加 SegmentHandler 中 get_segments_with_page 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments',
                        methods=["GET"],
                        view_func=self.segment_handler.get_segments_with_page)

        # 2.31 增加 SegmentHandler 中 get_segment 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments/<uuid:segment_id>',
                        methods=["GET"],
                        view_func=self.segment_handler.get_segment)

        # 2.32 增加 SegmentHandler 中 update_segment_enabled 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments/<uuid:segment_id>/enabled',
                        methods=["POST"],
                        view_func=self.segment_handler.update_segment_enabled)

        # 2.33 增加 SegmentHandler 中 create_segment 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments',
                        methods=["POST"],
                        view_func=self.segment_handler.create_segment)

        # 2.34 增加 DatasetHandler 中 get_dataset_queries 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/queries',
                        methods=["GET"],
                        view_func=self.dataset_handler.get_dataset_queries)

        # 2.35 增加 DatasetHandler 中 delete_dataset 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/delete',
                        methods=["POST"],
                        view_func=self.dataset_handler.delete_dataset)

        # 2.36 增加 SegmentHandler 中 delete_segment 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments/<uuid:segment_id>/delete',
                        methods=["POST"],
                        view_func=self.segment_handler.delete_segment)

        # 2.37 增加 SegmentHandler 中 update_segment 方法配置路由
        bp.add_url_rule('/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments/<uuid:segment_id>',
                        methods=["POST"],
                        view_func=self.segment_handler.update_segment)

        # 2.38 增加 OAuthHandler 中 provider 方法配置路由
        bp.add_url_rule('/oauth/<string:provider_name>',
                        methods=["GET"],
                        view_func=self.oauth_handler.provider)

        # 2.39 增加 OAuthHandler 中 authorize 方法配置路由
        bp.add_url_rule('/oauth/authorize/<string:provider_name>',
                        methods=["GET","POST"],
                        view_func=self.oauth_handler.authorize)

        # 2.40 增加 AccountHandler 中 get_current_user 方法配置路由
        bp.add_url_rule('/account',
                        methods=["GET"],
                        view_func=self.account_handler.get_current_user)

        # 2.41 增加 AccountHandler 中 update_password 方法配置路由
        bp.add_url_rule('/account/password',
                        methods=["POST"],
                        view_func=self.account_handler.update_password)

        # 2.42 增加 AccountHandler 中 update_name 方法配置路由
        bp.add_url_rule('/account/name',
                        methods=["POST"],
                        view_func=self.account_handler.update_name)

        # 2.43 增加 AccountHandler 中 update_avatar 方法配置路由
        bp.add_url_rule('/account/avatar',
                        methods=["POST"],
                        view_func=self.account_handler.update_avatar)

        # 2.44 增加 AuthHandler 中 password_login 方法配置路由
        bp.add_url_rule('/auth/password-login',
                        methods=["POST"],
                        view_func=self.auth_handler.password_login)

        # 2.44.1 增加 AuthHandler 中 reset_password 方法配置路由
        bp.add_url_rule('/auth/reset-password',
                        methods=["POST"],
                        view_func=self.auth_handler.reset_password)

        # 2.45 增加 AuthHandler 中 logout 方法配置路由
        bp.add_url_rule('/auth/logout',
                        methods=["POST"],
                        view_func=self.auth_handler.logout)

        # 3 将bp与app对象进行绑定
        app.register_blueprint(bp)
