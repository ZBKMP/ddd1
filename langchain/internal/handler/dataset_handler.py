from dataclasses import dataclass
from uuid import UUID

from flask import request
from flask_login import login_required
from flask_login import current_user # 获取当前登录的Account信息

from injector import inject

from internal.core.file_extractor import FileExtractor
from internal.model import UploadFile
from internal.schema import (
    CreateDatasetReq,
    GetDatasetResp,
    UpdateDatasetReq,
    GetDatasetsWithPageReq,
    GetDatasetsWithPageResp,
    HitReq,
    GetDatasetQueriesResp,
)
from internal.service import (
    DatasetService,
    EmbeddingsService,
    JiebaService, WeaviateVectorStoreService,
)
from pkg.paginator import PageModel
from pkg.response import (
    validation_error_json,
    success_message,
    success_json,
)


# 知识库handler处理器
@inject
@dataclass
class DatasetHandler:
    # 依赖注入
    dataset_service: DatasetService
    embeddings_service: EmbeddingsService
    jieba_service: JiebaService
    file_extractor: FileExtractor
    vector_store_service: WeaviateVectorStoreService

    # 新增知识库
    @login_required
    def create_dataset(self):
        # 1.提取请求并校验
        req = CreateDatasetReq()
        if not req.validate():
            return validation_error_json(req.errors)

        # 2 调用service 实现数据添加
        self.dataset_service.create_dataset(
            req,
            account=current_user,
        )

        # 3.返回成功调用提示
        return success_message("创建知识库成功")

    # 根据知识库ID获取知识库详情
    @login_required
    def get_dataset(self, dataset_id: UUID):
        """根据传递的知识库id获取详情"""
        # 完成授权认证模块后 增加account参数 current_user方法获取
        dataset = self.dataset_service.get_dataset(
            dataset_id,
            account = current_user,
        )
        # 将查询结果Dataset对象转换为dict 并响应结果
        resp = GetDatasetResp()
        return success_json(resp.dump(dataset))

    # 更新知识库
    @login_required
    def update_dataset(self, dataset_id: UUID):
        """根据传递的知识库id+信息更新知识库"""
        # 1.提取请求并校验
        req = UpdateDatasetReq()
        if not req.validate():
            return validation_error_json(req.errors)

        # 2.调用服务创建知识库
        # 完成授权认证模块后 增加account参数 current_user方法获取
        self.dataset_service.update_dataset(
            dataset_id,
            req,
            account=current_user,
        )
        # 3.返回成功调用提示
        return success_message("更新知识库成功")

    # 分页查询知识库
    @login_required
    def get_datasets_with_page(self):
        """获取知识库分页+搜索列表数据"""
        # 1.提取query数据并校验 get请求中的params需要作为参数传入
        req = GetDatasetsWithPageReq(request.args)
        if not req.validate():
            return validation_error_json(req.errors)
        # 2.调用服务获取分页数据
        # 完成授权认证模块后 增加account参数 current_user方法获取
        datasets, paginator = self.dataset_service.get_datasets_with_page(
            req,
            account = current_user,
        )
        # 3.构建响应 会返回多行结果
        resp = GetDatasetsWithPageResp(many=True)
        return success_json(
            PageModel(list=resp.dump(datasets), paginator=paginator)
        )

    #############################################################################

    #  测试向量查询方法
    def embeddings_query(self):
        query = request.args.get("query")

        # 测试 1 使用EmbeddingsService 生成向量数据
        # vectors = self.embeddings_service.embeddings.embed_query(query)
        # 测试带缓存功能的嵌入模型
        # vectors = self.embeddings_service.cache_backed_embeddings.embed_query(query)
        # return success_json({"vectors": vectors})

        # 测试 2 使用JiebaService 生成关键词
        # key_words = self.jieba_service.extract_keywords(query)
        # return success_json({"key_words": key_words})

        # 测试 3 使用FileExtractor 加载腾讯云COS文档
        # 先从本地数据库查询出文件信息记录  query为数据库中UploadFile的id
        from internal.extension import db
        upload_file = db.session.query(UploadFile).get(query)
        content = self.file_extractor.load(
            upload_file,
            return_text=False,
            is_unstructured=False,
        )
        for doc in content:
            print(doc)
        return success_json({
            "type": str(type(content))
        })

    # 测试从向量库检索数据 命中 击中
    def hit_test(self, dataset_id: UUID):
        # 元数据过滤条件
        from weaviate.classes.query import Filter
        # 检索问题
        query = request.form.get("query")
        # 构建检索器
        retriever = self.vector_store_service.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 10,
                # 元数据过滤条件
                "filters": Filter.all_of([  # and 所有条件都要满足
                    Filter.by_property("document_enabled").equal(True),
                    Filter.by_property("segment_enabled").equal(True),
                    Filter.any_of([  # or 多个条件中 起码满足一个即可
                        Filter.by_property("dataset_id").equal('ce95d190-1a86-4000-8bc6-8d65b6a215ff'),
                        Filter.by_property("dataset_id").equal('c4e81332-ca4a-4354-a0cd-cecf837b8ea7'),
                    ])
                ]),
            },
        )

        # 执行检索
        document_list = retriever.invoke(input=query)
        # 响应结果
        return success_json(data={
            "docs": [
                {
                    "page_content": doc.page_content,
                    "metadata": doc.metadata,
                }
                for doc in document_list
            ]
        })

    # 根据传递的知识库id+检索参数执行召回测试
    @login_required
    def hit(self, dataset_id: UUID):
        """根据传递的知识库id+检索参数执行召回测试"""
        # 1.提取数据并校验
        req = HitReq()
        if not req.validate():
            return validation_error_json(req.errors)

        # 2.调用服务执行检索策略 返回符合接口需求的list[dict]
        hit_result = self.dataset_service.hit(
            dataset_id,
            req,
            account=current_user,
        )

        return success_json(hit_result)

    # 根据传递的知识库id获取最近的10条查询记录
    @login_required
    def get_dataset_queries(self, dataset_id: UUID):
        """根据传递的知识库id获取最近的10条查询记录"""
        # 调用业务方法执行查询
        dataset_queries = self.dataset_service.get_dataset_queries(
            dataset_id,
            account=current_user,
        )
        # 封装查询结果 多行结果
        resp = GetDatasetQueriesResp(many=True)
        # 相应JSON结果
        return success_json(resp.dump(dataset_queries))

    # 根据传递的知识库id删除知识库
    @login_required
    def delete_dataset(self, dataset_id: UUID):
        """根据传递的知识库id删除知识库"""
        self.dataset_service.delete_dataset(
            dataset_id,
            account=current_user,
        )
        return success_message("删除知识库成功")
