# 1 LLMOPS 模块知识库功能模块解析
UI设计稿 https://js.design/f/I_B1Is?p=H6nW02nJkv&mode=design
 
# 2 知识库模块流程图拆解

# 3 文件上传模块数据库表设计与API接口文档分析  项目API文档 - 3.1 3.2
  3.1 文件实体模型类定义,用于描述上传文件的描述信息,文件上传至腾讯云COS,
      但在本地Postgresql数据库中同步保存数据. 
      * 在model包下新建upload_file.py,其中定义类UploadFile(db.Model)
      * 便捷导出该实体模型类,在server/http.py中导入该实体模型类,进行数据迁移,
        生成数据表.
      

  3.2 将文件/图片 上传到腾讯云COS  COS环境搭建
      * 腾讯云: https://cloud.tencent.com/  账号必须实名认证
      * 腾讯云控制台 :https://console.cloud.tencent.com/?Is=sdk-topnav 
                    搜索“对象存储”
      * 腾讯云对象存储COS : https://console.cloud.tencent.com/cos  
                    在"资源包管理" 可查看到 "免费额度资源包"
      * 存储桶列表-创建存储桶-公有读私有写-创建
        存储桶概览-域名信息: 
              https://llmops-1328730224.cos.ap-guangzhou.myqcloud.com 
              https://llmops2-1328730224.cos.ap-guangzhou.myqcloud.com
              https://llmops3-1328730224.cos.ap-guangzhou.myqcloud.com  
                      
      * 用户-访问管理-API秘钥管理-新建秘钥-配置于.env：
                  SecretId:your-cos-secret-id
                  SecretKey:your-cos-secret-key
      * 存储桶使用: 对象存储-常用工具-SDK下载-Python
      (https://cloud.tencent.com/document/product/436/12269?from=console_document_search)
                  查看主要步骤:初始化 -- 上传对象 -- 下载对象
                  模块安装 : pip install -U cos-python-sdk-v5 
                  
  3.3 文件/图片上传代码实现  项目API文档-上传文件至腾讯云COS
      设计要求: 文件上传至腾讯云COS 并对应将文件信息存储在数据库中

   3.3.1 handler与schema类定义     
      * handler包下新建文件upload_file.py,创建视图类UploadFileHandler,
        作为文件上传处理器,便捷导出.
      * 视图包含方法upload_file与upload_image,并配置路由.
      * 在schema包下新建 upload_file_schema.py为UploadFileHandler的
        视图方法定义请求验证与响应包装:
        UploadFileReq(FlaskForm), UploadFileResp(Schema),
        UploadImageReq(FlaskForm),便捷导出.
      * 新建包internal.entity 定义文件upload_file_entity.py,其中声明允许上传
        的文件类型列表:ALLOWED_DOCUMENT_EXTENSION.

   3.3.2 Service业务服务层类定义
      * service包下新建cos_service.py,新建CosService类,新增方法:
        upload_file/download_file
        对接腾讯云COS对象存储,实现文件上传/下载业务逻辑,便捷导出.
      * service包下新建upload_file_service.py,新建类:
        UploadFileService(BaseService),
        实现方法create_upload_file,完成文件数据的数据库录入,便捷导出
      * CosService.upload_file在文件上传业务最后调用
        UploadFileService.create_upload_file,
        在上传同时完成数据库添加,返回添加成功的db.Model对象.

   3.3.3 组装handler代码
      * UploadFileHandler.upload_file使用UploadFileReq验证请求,
        调用CosService.upload_file,
        响应结果封装为UploadFileResp,使用POSTMAN测试文件上传.
      * UploadFileHandler.upload_image使用UploadFileReq验证请求,
        调用CosService.upload_file,
        UploadFileService新增业务方法get_file_url,获取图片的实际URL地址,
        视图方法仅需要图片路径作为响应结果,使用POSTMAN测试文件上传
      POST : http://127.0.0.1:5000/upload-files/file
      POST : http://127.0.0.1:5000/upload-files/image
      form_data表单上传文件 参数名file

# 4 LLMOPS继承日志记录器实现错误记录
   4.1 设计需求:在项目中增加日志记录功能

   4.2 日志功能实现
      * extension包下增加文件 logging_extension.py,编写函数init_app,
        为Flask_app对象增加日志功能.
      * 修改server.http.py文件 为Http(Flask)类注册日志功能,在其
        _register_error_handle
        函数中增加日志输出,当访问后台接口出现异常时就会进行日志记录.
      * 项目任何位置需要记录日志 只需导入logging包 使用logging.X函数输出
        各个级别日志信息.
      * 进行错误的HTTP访问测试 可在storage/log目录下查看到app.log内的日志信息,
        跨天后可看到app.log会备份为以日期为名称的log文件中.
   
# 5.知识库,文档,片段 模块API文档分析及表结构  项目API文档 - 4.1-4.7  4.8-4.14  4.15-4.20

# 6.Flask集成Redis实现缓存与消息代理
   6.1 Redis环境搭建 
      * Windows或Docker下安装Redis,.evn中新增redis配置.
      * config/config.py下Config类中增加Redis配置信息读取代码
      * config/default_config.py中增加Redis配置的默认值
      * 安装python redis依赖 pip install redis 

   6.2 创建Redis扩展
      * extension包下新建文件redis_extension.py,创建Redis连接对象,便捷导出.
         增加方法init_app(Flask),创建连接池,并关联Flask的app对象.
      * 修改server/http.py中Http(Flask)类,调用redis_extension.init_app
         方法实现Flask_app对象与redis关联,
      * app.http.module.py中 增加对redis_extension中redis_client对象的绑定.
    

# 7.FLask集成Celery处理异步任务
   7.1 celery依赖安装 : pip install celery eventlet
   
   7.2 创建Celery扩展 创建Celery执行环境
      * extension包下新建文件celery_extension.py,创建,
        增加方法init_app(Flask).
      * .env中增加Celery配置,config/config.py下Config类中增加
         Celery配置信息读取代码
      * config/default_config.py中增加Celery配置的默认值
      * 修改server/http.py中Http(Flask)类,调用init_app方法实现
        Flask_app对象与Celery关联.
      * 修改app/http/app.py,其中声明一个celery全局变量,以便后续在终端
        执行celery指令.  
   
   7.3 使用Celery   异步任务框架     (asyncio  async def await)
      * 在internal下新建包task(包含项目中所有的耗时操作),
        包中新增文件demo_task.py,创建测试task
      * 修改AppHandler类测试函数ping 调用demo_task.py异步任务demo_task,
      * 终端执行操作启动Celery服务 : 
celery -A app.http.app.celery worker --loglevel INFO --pool solo  --logfile storage/log/celery.log
celery -A app.http.app.celery worker --loglevel INFO --pool solo  --concurrency 10 

      * POSTMAN测试访问AppHandler.ping,在storage/log/celery.log
        下查看异步任务输出结果(只能在日志文件中查看到),
        可在redis下查看到对应的celery数据
        GET: http://127.0.0.1:5000/ping
      * 后续如需要执行异步任务,可在task包下创建对应的异步任务函数,
        使用函数.delay(args)方式执行异步任务,
        后续如修改了任何异步任务的定义 需要重启Celery服务
   
# 8 知识库三大层级及扩展表ORM模型 实现
   8.1 实体模型类创建
      * 在model包下新建文件dataset.py,其中定义知识库,文档,片段,
         KeywordTable,ProcessRule,DatasetQuery实体模型类.
         便捷导出该实体模型类,在server/http.py中导入该实体模型类.
      * 修改model包下app.py,增加实体模型类AppDatasetJoin,表示 
         应用知识库关联表模型.
         便捷导出该实体模型类,在server/http.py中导入该实体模型类.
      * 进行数据迁移,生成数据表.

# 9 知识库增改查4个API接口 设计与实现 项目API文档 - 4.2 4.5 4.3 4.1
   9.1 创建知识库功能实现
      * handler包下新建dataset_handler.py,定义类DataSetHandler,
        作为知识库模块的视图函数类.
      * DataSetHandler下新增视图方法:
        create_dataset,get_dataset,update_dataset,
        get_datasets_with_page,
        便捷导出该视图函数类,并为其中方法配置路由.
      * 在schema包下新建 dataset_schema.py为DataSetHandler的视图方法定义
        请求验证与响应规范:
         CreateDatasetReq,GetDatasetResp,UpdateDatasetReq,
         GetDatasetsWithPageReq,GetDatasetsWithPageResp.
      * 在service包下新建 dataset_service.py,定义类DatasetService,
        增加方法create_dataset,实现添加知识库的业务逻辑.
      * 在entity包下新建dataset_entity.py,定义创建知识库时所需的默认的
        知识库描述信息.
      * DataSetHandler.create_dataset视图方法,通过CreateDatasetReq验证请求,
        调用DatasetService.create_dataset,输出JSON结果,POSTMAN测试访问. 
        POST: http://127.0.0.1:5000/datasets
        测试参数1 :
        {
         "name":"llmops_dataset_1",
         "icon":"https://llmops-1328730224.cos.ap-guangzhou.myqcloud.com/2026/01/30/55a6a2cb-bbe2-44ac-904e-328b14fc7044.png",
         "description":"llmops测试知识库_1"
        }
        测试参数2 :
         {
         "name":"llmops_dataset_2",
         "icon":"https://llmops-1328730224.cos.ap-guangzhou.myqcloud.com/2026/01/30/9959c670-83e7-4cf9-86eb-c30b144382a4.png"
        }

  9.2 根据知识库ID获取指定知识库信息
      * 基于9.1步骤 已经搭建好代码框架,继续完成视图函数get_dataset,
        使用GetDatasetResp作为响应结果
      * 定义类DatasetService下增加业务方法 get_dataset 实现数据库查询
      * POSTMAN测试访问 
       GET :http://127.0.0.1:5000/datasets/:dataset_id
      
  9.3 根据知识库ID更新指定知识库信息
      * 基于9.1步骤 已经搭建好代码框架,继续完成视图函数update_dataset,
         使用UpdateDatasetReq作为请求数据验证
      * 定义类DatasetService下增加业务方法 update_dataset 实现数据库修改
      * POSTMAN测试访问  
       POST :http://127.0.0.1:5000/datasets/:dataset_id
        {
         "name":"llmops_dataset_1",
         "icon":"https://llmops-1328730224.cos.ap-guangzhou.myqcloud.com/2026/01/30/55a6a2cb-bbe2-44ac-904e-328b14fc7044.png",
         "description":"当你需要回答管理 llmops_dataset_1 时 可以使用该知识库"
        }

    
  9.4 分页查询知识库信息
      * 基于9.1步骤 已经搭建好代码框架,继续完成视图函数get_datasets_with_page,
         使用GetDatasetsWithPageReq作为请求数据验证,
         使用GetDatasetsWithPageResp作为响应结果
      * 定义类DatasetService下增加业务方法 get_datasets_with_page 
        实现数据库分页
      * POSTMAN测试访问 
       GET: http://127.0.0.1:5000/datasets
          
    
# 10 weaviate向量数据库的配置与安装
  10.1 linux_docker 本地安装weaviate向量数据库 
  
  10.2 修改vector_store_service.WeaviateVectorStoreService,
       测试使用本地向量库

# 11 本地Embeddings模型部署与使用
  11.1 创建本地Embeddings模型业务层
      * service包下新建embeddings_service.py,编写EmbeddingsService类,便捷导出,
        基于HuggingFaceEmbeddings实现本地化的文本嵌入模型,提供文本嵌入业务服务,
        过程中还可以结合redis 实现 CacheBackedEmbeddings,
        以RedisStore作为数据缓存.
      * 使用本地部署的嵌入模型 下载的文件存储于 internal/core/embeddings
      * DatasetHandler中引入EmbeddingsService,增加视图测试方法embeddings_query,
         测试:从请求中获取query参数,调用EmbeddingsService,
             以将query参数转换为向量数据列表,
         为视图方法编辑路由,POSTMAN测试访问.
       GET: http://127.0.0.1:5000/datasets/embeddings
       增加params参数:query
      * 第一次启动执行成功之后,会远程下载向量模型.在.env中增加配置
       TRANSFORMERS_OFFLINE=1,则后续不会再进行远程下载.

  11.2 部署了本地的Embeddings模型之后,在WeaviateVectorStoreService中
       基于EmbeddingsService来获取Embeddings模型.

# 12 jieba分词服务设计与关键词抽取
  12.1 jieba 分词器 用于分词 提取文本中的关键词
      * 模块安装 pip install jieba 
      * service包下新建jieba_service.py,创建类JiebaService,
        作为Jieba业务服务类,便捷导出. 
      * entity包下新建jieba_entity.py,文件中增加集合STOPWORD_SET,
        表示jieba停止词集合.
      * JiebaService类新增业务方法(类方法)extract_keywords,
        用于实现对文本内容提取关键词.
  12.2 测试使用 JiebaService  
      * 在DatasetHandler中引入JiebaService,修改视图方法embeddings_query 
         测试:从请求中获取query参数,调用JiebaService,
             从query中提取出关键词,POSTMAN测试
       GET: http://127.0.0.1:5000/datasets/embeddings 
       增加params参数:query

# 13 通用文件加载器实现cos文件加载
  13.1 以数据库存储的文件ID去加载远程文件,使用加载器得到文档列表或文本
      * core下新建包file_extractor,新增文件file_extractor.py,
        新建类FileExtractor,用于提取远程文件成文档或字符串,类中借助CosService,
        实现从腾讯云COS读取远程文件,便捷导出.
      * 类中新增方法 load ,根据UploadFile数据库记录 加载对应远程文档,
        结果为文档列表或文本字符串
      * 安装模块:支持加载docx文件: 
        pip install python-docx 
        pip install docx2txt  
        pip install unstructured
      * 安装模块:支持加载pdf文件:
        pip install "pdfminer.six==20221105"
        pip install "unstructured==0.10.30"
        pip install pi_heif   
        pip install unstructured_inference
        pip install pdf2image
        pip install unstructured_pytesseract
  13.2 测试使用 FileExtractor  
      * 在DatasetHandler中引入FileExtractor,修改视图方法embeddings_query.
      * 测试:从请求中获取query参数(UploadFile.id),调用FileExtractor,
            从腾讯云COS加载文件,并返回文档列表.
        POSTMAN测试,需要从云端下载文件,并通过文档加载器加载,耗时较长.
        GET: http://127.0.0.1:5000/datasets/embeddings 
        增加params参数:query(UploadFile.id)
  
# 14  新增Document文档API接口同步任务 设计与实现  项目接口文档-4.9
  14.1 知识库新增文档实体列表功能实现:将腾讯云中的文件加载为知识库下的文档Document
       从UploadFile表中获取多个文件ID,将其转换为Document实体记录,
       并发起异步任务进行文件下载与后期处理. 
      * handler包下新增document_handler.py,新增DocumentHandler视图方法类,
        便捷导出.定义方法create_documents,用于知识库新增/上传文档列表.
      * schema包下新增document_schema.py文件,定义create_documents视图方法所需
        请求验证类与响应包装类 CreateDocumentsReq/CreateDocumentsResp,便捷导出.
        CreateDocumentsReq中先仅定义所需要的属性,后续任务中完成复杂的属性验证过程.
      * internal.entity.dataset_entity.py下声明ProcessType枚举,
        规定CreateDocumentsReq中process_type只能是自动或自定义.
      * internal.schema.schema.py下声明DictField以替代wtforms下的DictField,
        作为CreateDocumentsReq中rule属性的类型.
      * service包下新增 document_service.py文件,新增类DocumentService,便捷导出
         新增方法 create_documents 实现创建Document实体列表的业务流程,
         方法中的核心流程：“调用异步任务 完成后续操作” 在后续步骤实现。 
      * DocumentHandler.create_documents视图方法通过CreateDocumentsReq
        验证请求数据,调用DocumentService.create_documents方法实现业务过程,
        结果封装为CreateDocumentsResp,
      * 为DocumentHandler.create_documents 配置路由 ,完成后续任务15再进行测试
      POST: http://127.0.0.1:5000/datasets/:dataset_id/documents 

# 15  知识库文档分段规则校验逻辑 实现
  15.1 完整14步骤中中还未完成的部分 实现对CreateDocumentsReq中复杂参数格式验证函数
      * internal.entity.dataset_entity.py下声明DEFAULT_PROCESS_RULE,
        表示默认的处理规则字典. 
      * 修改CreateDocumentsReq代码,新增函数validate_upload_file_dis,
        完成类中属性upload_file_ids的校验过程
      * 修改CreateDocumentsReq代码,新增函数validate_rule,
         完成类中属性rule的校验过程
      (核心代码:CreateDocumentsReq.validate_rule 验证文档处理规则参数合法性)
      * PostMan测试DocumentHandler.create_documents的路由,
        检验Document文档实体数据的创建
      POST: http://127.0.0.1:5000/datasets/:dataset_id/documents
     测试参数1:
     {
      "upload_file_ids":["a1e78bc7-e423-43af-935e-4a05cecb2730","f6abfbc8-eff4-4b16-8fe4-394dc94912ba"],
      "process_type":"automatic"
     } 
     测试参数2:
     {
      "upload_file_ids":["a1e78bc7-e423-43af-935e-4a05cecb2730","f6abfbc8-eff4-4b16-8fe4-394dc94912ba"],
      "process_type":"custom",
      "rule":{"pre_process_rules":[{"id":"remove_extra_space","enabled":false},{"id":"remove_url_and_email","enabled":false}],"segment":{"separators":["\n\n","\n"," ",""],"chunk_size":1000,"chunk_overlap":50}}
     }
     !!!注意:数据尚不完整 测试成功之后删除document表与process_rule表数据

# 16 耗时操作 加载与分割文档(生成片段列表)异步任务 设计与实现
  16.1  实现文档分割异步任务
      * task包下新建文件document_task.py 用于包含文档操作的相关异步任务
         定义异步任务方法build_documents,调用IndexingService.build_documents
        (document_ids),以实现根据传递的文档id列表构建知识库文档.
      * service包下新建indexing_service.py文件,构建类IndexingService,便捷导出
         新增业务方法build_documents(document_ids),用于构建知识库文档业务过程.
         (核心业务方法)
      * IndexingService.build_documents过程中需要调用的功能方法:
          1 _parsing:文档加载功能函数 返回langchain_Document文档列表
          2 _clean_extra_text: 类方法 去除文本中多余的空格
          3 _splitting:文档分割功能函数 返回分割处理后的langchain_Document
                       文档列表
          4._indexing:构建关键词索引
          5._complete_thread: 完成最后的向量存储与数据更新
      * IndexingService.build_documents过程中需要调用的其他组件:
          1 定义internal.entity.dataset_entity.DocumentStatus/SegmentStatus枚举
          2 service包下新建process_rule_service.py文件,构建类ProcessRuleService,
            便捷导出.
            新增业务方法:
             get_text_splitter_by_process_rule,根据process_rule获取递归文本分割器
             clean_text_by_process_rule,实现根据处理规则 清除多余的字符窜
          3 修改lib包下help.py文件,新增方法generate_text_hash,用于生成文本信息的hash值
      * IndexingService.build_documents完成的步骤:
          1 根据传递的文档id列表获取所有文档
          2 执行循环遍历所有文档完成对每个文档的构建
          3 更新当前状态为解析中，并记录开始处理的时间
          4 执行文档加载步骤，并更新文档的状态与时间
          5 执行文档分割步骤，并更新文档状态与时间，涵盖了片段的信息
      * IndexingService.build_documents当前尚未完成的步骤:
          6 执行文档索引构建，涵盖关键词提取、向量，并更新数据状态
          7 存储操作，涵盖文档状态更新，以及向量数据库的存储
      * 在步骤14 : 
         DocumentService.create_documents中补充未完成的异步任务调用-步骤6
      
# 17 耗时操作 文档索引与存储异步任务 设计与实现
  17.1 继续16步骤,完成IndexingService.build_documents未完成的步骤
      * 新增IndexingService.build_documents需要调用的功能方法
         _indexing:根据传递的信息构建索引
         _completed:存储文档片段到向量数据库，并完成状态更新(直接使用步骤18.1多线程方案实现)
      * IndexingService.build_documents需要调用的其他组件:
        service包下新建文件keyword_table_service.py,
        新建业务服务类KeywordTableService,便捷导出.
        类中新增方法get_keyword_table_from_dataset_id,
        依据知识库ID获取对应关键词表信息.
  17.2 测试步骤14 15 16 17 实现新增文档并将文档内容分割处理后存入向量库
      * 启动项目,启动celery异步服务,postman测试DocumentHandler.create_documents
  celery -A app.http.app.celery worker --loglevel INFO --pool solo  --concurrency 10  
      * 再次测试:PostMan测试DocumentHandler.create_documents的路由,
                检验Document文档实体数据的创建
        POST: http://127.0.0.1:5000/datasets/:dataset_id/documents   

# 18 Thread多线程使用与文档存储代码优化
  18.1 使用多线程优化indexing_service.py中IndexingService代码
      * 优化_completed方法逻辑,将循环存储向量库的过程改为使用多线程实现
      * 再次测试:PostMan测试DocumentHandler.create_documents,
                检验Document文档实体数据的创建
        POST: http://127.0.0.1:5000/datasets/:dataset_id/documents 

  整体执行流程
  document_handler->document_service->document_task->indexing_service->(OtherService......)


  18.2 数据存储至向量库之后,尝试进行数据检索操作,演示召回测试效果
      * handler/dataset_handler.py下,DatasetHandler类中新增函数hit_test,
        测试从向量库检索数据,为函数配置路由,POSTMAN测试访问.
        POST :http://127.0.0.1:5000/datasets/:dataset_id/hit

# 19 批处理获取文档状态 接口设计与实现  项目接口文档-4.10
  19.1 根据传递的知识库id+批处理标识获取文档的状态,前端会轮巡实时访问该接口
      * handler/document_handler.py下,DocumentHandler类中新增方法:
        get_documents_status
       获取文档的状态,过程中调用DocumentService业务服务类完成处理过程,配置路由
      * service/document_service.py下,DocumentService类中新增方法
        get_documents_status:
       完成根据dataset_id与batch批处理标识获取文档状态的业务过程
      * 完成DocumentService.get_documents_status需要的其他组件
        lib/help.py中新建函数:datetime_to_timestamp
        将传入的datetime时间转换成时间戳,如果数据不存在则返回0.
      * PostMan测试DocumentHandler.get_documents_status视图函数,查看结果
     GET : http://127.0.0.1:5000/datasets/:dataset_id/documents/batch/:batch
  
# 20 文档模块基础CURD 接口设计与实现   项目API文档 - 4.8 4.11 4.13
  20.1 获取指定文档的基础信息  4.13
      * handler/document_handler.py下,DocumentHandler类中新增方法: 
        get_document
       根据传递的知识库id+文档id获取文档详情信息,
       过程中调用DocumentService.get_document,配置路由.
      * schema/document_schema.py下,新增类:GetDocumentResp,
       描述获取文档基础信息响应结构作为DocumentHandler.get_document
        方法响应结果封装类.
      * service/document_service.py下,DocumentService类中新增方法:
        get_document
       完成根据传递的知识库id+文档id获取文档详情信息的业务过程.
      * POSTMAN测试访问
     GET : http://127.0.0.1:5000/datasets/:dataset_id/documents/:document_id
  
  20.2 更新指定文档基础名称 4.11
      * handler/document_handler.py下,DocumentHandler类中新增方法:
        update_document_name
        根据传递的知识库id+文档id更新对应文档的名称信息,过程中调用
        DocumentService.update_document,配置路由.
      * schema/document_schema.py下,新增类UpdateDocumentNameReq,
        更新文档名称信息请求验证类
      * service/document_service.py下,DocumentService类中新增方法:
         update_document
        完成根据传递的知识库id+文档id，更新文档信息的业务过程  
      * POSTMAN测试访问
     POST : http://127.0.0.1:5000/datasets/:dataset_id/documents/:document_id/name
     {
    "name":"项目API文档"
     }

  20.3 获取指定知识库的文档列表 4.8
      * handler/document_handler.py下,DocumentHandler类中新增方法:
        get_documents_with_page
       根据传递的知识库id获取文档分页列表数据,过程中调用
        DocumentService.get_documents_with_page,配置路由.
      * schema/document_schema.py下,新增类GetDocumentsWithPageReq,
         获取文档分页列表请求验证类
      * schema/document_schema.py下,新增类GetDocumentsWithPageResp,
         获取文档分页列表响应结构封装类
      * service/document_service.py下,DocumentService类中新增方法:
         get_documents_with_page
       完成根据传递的知识库id+请求数据获取文档分页列表数据的业务过程 
      * POSTMAN测试访问
     GET : http://127.0.0.1:5000/datasets/:dataset_id/documents
  


# 21 耗时操作 缓存锁与修改文档启用状态 接口设计与实现  项目API文档 - 4.12
  21.1 该接口主要用于更改指定文档的启用状态(开启/关闭),文档只有在completed
       完成状态下才可以做相应的更新调整,否则抛出异常,同时还需要异步更新weaviate
       向量数据库中的数据.
       在执行对某文档的异步更新的过程中,执行的是耗时操作,下一次执行对该文档该异步任务
       之前,必须等待本次操作完成,借助redis缓存锁完成此业务要求.
      * handler/document_handler.py下,DocumentHandler类中新增方法:
        update_document_enabled
       根据传递的知识库id+文档id，更新文档的启用状态，过程中调用
       DocumentService.update_document_enabled,配置路由.
      * schema/document_schema.py下,新增类UpdateDocumentEnabledReq,
       作为更新文档启用状态请求验证类.
      * service/document_service.py下,DocumentService类中新增方法:
        update_document_enabled,
        完成根据传递的知识库id+文档id,更新文档的启用状态,
        函数最后会异步更新weaviate向量数据库中的数据的业务过程.
      * DocumentService.update_document_enabled业务方法需要的其他组件
       1 internal/entity下新建文件cache_entity.py,其中定义关于缓存锁所需要的
         相关常量:
         LOCK_DOCUMENT_UPDATE_ENABLED : redis中的key名
         LOCK_EXPIRE_TIME : 缓存所的过期时间
       2 过程中除了修改数据库数据,还要执行对应的更新weaviate向量数据库中的数据,
         在internal/task下修改document_task.py,新增异步方法:
         update_document_enabled,完成更新weaviate向量库.
       3.修改vector_database_service.WeaviateVectorStoreService,
         增加只读属性collection,获取向量库中项目对应的数据集.
       4.update_document_enabled异步方法执行过程中需要再调用IndexingService
          中的业务方法:
         update_document_enabled,实现根据传递的文档id更新文档状态,
         同时修改weaviate向量数据库中的记录.
         weaviate向量库操作中,通过collection修改集合内的数据,参考文档:
         https://docs.weaviate.io/weaviate/manage-objects/update
       5.修改文档启用状态时,还需要同步更新key_world表中的关键词数据,在后续步骤23中实现.
      * 重启celery异步服务，重启项目,postman测试,可观察到在异步任务执行过程中产生了
        redis缓存锁,执行完毕之后锁消失,查看向量库数据,enabled状态发生变化
     POST : http://127.0.0.1:5000/datasets/:dataset_id/documents/:document_id/enabled
      {
       "enabled":true
      }

# 22 耗时操作 缓存锁与删除文档接口的设计与实现 项目API文档 - 4.14
  22.1 根据传递的信息删除文档信息,并删除其所有片段,同时删除向量数据库中对应的片段文档.
       该操作为耗时操作,以异步方式执行,同时也需要在删除时加上缓存锁.
      * handler/document_handler.py下,DocumentHandler类中新增方法:
        delete_document根据传递的知识库id+文档id，更新文档的启用状态，
        过程中调用DocumentService.delete_document,配置路由
      * service/document_service.py下,DocumentService类中新增方法:
        delete_document完成 根据传递的知识库id+文档id删除文档信息,
         同时会异步删除weaviate向量数据库中的数据的业务过程 
      * DocumentService.delete_document业务方法需要的其他组件
         1 过程中除了删除数据库数据,还要执行对应的删除weaviate向量数据库中的数据,
           在internal/task下修改document_task.py,新增异步方法delete_document,
           完成删除weaviate向量库对应数据,以及数据库中关键词表数据的更新.
         2 异步方法document_task.delete_document过程中再调用
            IndexingService.delete_document,
           实现根据传递的知识库id+文档id删除文档信息,同步删除weaviate数据.
           删除collection内的数据参考文档:
         https://docs.weaviate.io/weaviate/manage-objects/delete
         3 过程最后同步删除文档对应的片段信息,以及更新关键词表中的对应数据.
      * 后续步骤23 优化代码结构 将删除关键词表的代码部分单独抽取成服务
      * 重启celery异步服务，重启项目,postman测试,可观察到在异步任务执行过程中产生了
         redis缓存锁,执行完毕之后锁消失,查看向量库数据,enabled状态发生变化
      POST ： http://127.0.0.1:5000/datasets/:dataset_id/documents/:document_id/delete

# 23 混合检索器设计思路 与 关键词表服务抽取 
   23.1 将IndexingService.delete_document操作中删除关键词表的操作抽离成单独的
        服务方法
      * service/keyword_table_service.py中,修改KeywordTableService,新增方法:
        delete_keyword_table_from_ids,根据传递的知识库id+片段id列表删除对应
        关键词表中多余的数据.
      * service/indexing_service.py中,修改IndexingService.delete_document
        方法将原本删除keyword_table数据的操作更改为调用:
         KeywordTableService.delete_keyword_table_from_ids,
         以实现删除关键词表中的片段ID和关键词.
      * 重启celery异步服务,重启项目,postman测试DocumentHandler.delete_document
     POST ： http://127.0.0.1:5000/datasets/:dataset_id/documents/:document_id/delete

   23.2 在IndexingService.update_document_enabled操作中新增关键词表的操作抽离成
        单独的服务方法
      * service/keyword_table_service.py中,修改KeywordTableService,新增方法:
        add_keyword_table_from_ids,根据传递的知识库id+片段id列表，
        在关键词表中添加关键词与片段ID.
      * service/indexing_service.py中,
        修改IndexingService.update_document_enabled方法
        在更新document的enabled状态之后,要连带的新增或删除关键词表数据,
        过程调用KeywordTableService中的
        delete_keyword_table_from_ids或add_keyword_table_from_ids方法实现.
      * 重启celery异步服务,重启项目,postman测试
         DocumentHandler.update_document_enabled
      POST : http://127.0.0.1:5000/datasets/:dataset_id/documents/:document_id/enabled
      {
       "enabled":true
      }

      SELECT LENGTH(keyword_table::text) FROM keyword_table;

# 24 RAG片段模块接口设计与实现 项目API文档 - 4.15 4.19 4.20
   24.1 获取指定文档的片段列表 (独立完成)
      * handler包下新建segment_handler.py,创建类SegmentHandler,便捷导出
      * 新增方法 get_segments_with_page 获取指定知识库文档的片段列表信息,配置路由.
      * schema包下新建segment_schema.py,为get_segments_with_page视图函数创建:
         请求验证类:GetSegmentsWithPageReq
         响应结果封装类:GetSegmentsWithPageResp
         便捷导出.
      * service包下新建文件segment_service.py,创建类SegmentService,便捷导出.
      * SegmentService类中新建方法:get_segments_with_page,
        实现获取指定知识库文档的片段列表信息的业务流程,
        SegmentHandler.get_segments_with_page调用该业务方法完成处理.
      * 启动服务 POSTMAN测试 SegmentHandler.get_segments_with_page
     GET : http://127.0.0.1:5000/datasets/:dataset_id/documents/:document_id/segments
       

   24.2 查询文档片段信息 (独立完成)
      * SegmentHandler 新增方法 get_segment 获取指定的文档片段信息详情,配置路由
      * 修改schema/segment_schema.py,为get_segment视图函数创建 响应结果封装类:
         GetSegmentResp,便捷导出  
      * SegmentService类中新建方法get_segment,实现根据传递的信息获取片段详情信息
        的业务流程,SegmentHandler中视图函数调用该业务方法完成处理
      * 启动服务 POSTMAN测试 SegmentHandler.get_segment 
     GET : http://127.0.0.1:5000/datasets/:dataset_id/documents/:document_id/segments/:segment_id


   24.3 更新文档片段的启用状态 4.19
      * SegmentHandler 新增方法 update_segment_enabled 
        根据传递的信息更新指定的文档片段启用状态,配置路由.
      * 修改schema/segment_schema.py,为update_segment_enabled视图函数创建
        请求验证类:UpdateSegmentEnabledReq,便捷导出.
      * SegmentService类中新建方法update_segment_enabled,实现根据传递的信息
        更新文档片段的启用状态信息的业务流程,SegmentHandler中视图函数调用该业务
        方法完成处理. 
      * 启动服务 POSTMAN测试 SegmentHandler.update_segment_enabled
      POST : http://127.0.0.1:5000/datasets/:dataset_id/documents/:document_id/segments/:segment_id/enabled
      {
        "enabled":true
      }


# 25 知识库新增片段API接口的设计与实现 项目API文档 - 4.16
   25.1  新增文档片段信息
      * SegmentHandler 新增方法 create_segment 根据传递的信息创建知识库文档片段,
        配置路由
      * 修改schema/segment_schema.py,为create_segment视图函数创建请求验证类:
         CreateSegmentReq,便捷导出 
      * SegmentService类中新建方法create_segment,实现根据传递的信息新增文档片段
        信息的业务流程,SegmentHandler视图函数create_segment调用该业务方法完成处理
      * 启动服务 POSTMAN测试 SegmentHandler.create_segment
      POST : http://127.0.0.1:5000/datasets/:dataset_id/documents/:document_id/segments
      测试案例1:
      {
      "content":"测试用片段信息1 这是测试用片段信息 包含与原文档相关的内容 包含与知识库相关的内容 "
      }
      测试案例2:
      {
       "content":"测试用片段信息2 其中包含了自定义的关键字信息 不需要程序生成 ",
       "keywords":["测试","关键字","程序"]
      }
   
# * 26 基于知识库的LangChain检索器实现
   26.1 构建基于LangChain的相似性检索器
      * internal/core包下新建包retrievers,新建文件semantic_retriever.py
      * semantic_retriever.py下新建类SemanticRetriever,自定义的相似性检索器,
        便捷导出.

   26.2 构建基于LangChain的全文检索器
      * retrievers包下新建文件full_text_retriever.py
      * full_text_retriever.py下新建类FullTextRetriever,
        完成自定义的全文性检索器,便捷导出           
       

# * 27 召回测试与查询API接口设计与实现 项目API文档 - 4.6 4.7
   27.1 使用指定的知识库进行召回测试,检测不同的query在(数据库/知识库)中的检索效果
      * 修改internal/handler/dataset_handler.py下的DatasetHandler类,
        修改方法hit,去掉之前做测试的代码,重新定义hit视图函数,根据传递的
        知识库id+检索参数执行召回测试.
      * 修改internal/schema/dataset_schema.py,为hit视图函数创建请求验证类: 
        HitReq,便捷导出.
      * 修改internal/entity/dataset_entity.py,增加检索策略类型枚举定义
        RetrievalStrategy.
      * internal/service/dataset_service.py下DatasetService类中新建方法hit,
         实现根据传递的知识库id+请求执行召回测试的业务流程,
         DatasetHandler中视图函数hit调用该业务方法完成处理.
      * internal/service下新建retriever_service.py,新增业务服务类:
        RetrieverService,便捷导出.
      * RetrieverService中新增方法search_in_datasets,实现根据传递的
        query+知识库列表执行检索,并返回检索的文档+得分数据的业务流程,
        DatasetService.hit方法调用该方法实现过程
      * 启动服务 POSTMAN测试 DatasetHandler.hit 请求数据示例:
      POST :http://127.0.0.1:5000/datasets/:dataset_id/hit
          (注意该路由中对应的函数由hit_test改为hit)
{
    "retrieval_strategy":"semantic",
    "k":4,
    "query":"配置",
    "score":0.5
}


   27.2 获取指定知识库最近的查询列表,返回最近的10条记录 (独立完成)
      * 修改internal/handler/dataset_handler.py下的DatasetHandler类,
        新增方法:get_dataset_queries,
        根据传递的知识库id获取最近的10条查询记录,配置路由
      * 修改internal/schema/dataset_schema.py,为get_dataset_queries
        视图函数创建相应结果封装类:
        GetDatasetQueriesResp,便捷导出.
      * internal/service/dataset_service.py下DatasetService类中新建方法:
         get_dataset_queries,实现根据传递的知识库id获取最近的10条查询记录的
         业务流程.
        DatasetHandler.get_dataset_queries调用该业务方法完成处理. 
      * 启动服务 POSTMAN测试 DatasetHandler.get_dataset_queries
      GET : http://127.0.0.1:5000/datasets/:dataset_id/queries

# 28  删除片段与知识库API接口设计与实现  项目API文档 - 4.4 4.17
   28.1  耗时操作 删除指定的知识库 删除知识库之后会将关联的应用配置,文档,片段,查询记录也
        一并删除.  4.4
      * 修改internal/handler/dataset_handler.py下的DatasetHandler类,
        新增方法:delete_dataset
        根据传递的知识库id删除知识库,配置路由
      * internal/service/dataset_service.py下DatasetService类中新建方法:
        delete_dataset,
        实现根据传递的知识库id删除知识库信息的业务流程,
        DatasetHandler中视图函数delete_dataset调用该业务方法完成处理. 
      * DatasetService.delete_dataset执行过程中会需要执行异步耗时任务,
        在internal/task下新建文件dataset_task.py,
        其中定义异步任务delete_dataset.
      * 异步任务delete_dataset的执行过程依赖IndexingService.delete_dataset
        业务方法实现.在IndexingService下新增该业务方法.
      * 重启celery异步服务，重启项目,postman测试DatasetHandler.delete_dataset
      POST : http://127.0.0.1:5000/datasets/:dataset_id/delete

   28.2 删除对应的文档片段信息 同步删除向量库中的数据  (独立完成)  4.17
      * 修改internal/handler/segment_handler.py下的SegmentHandler类,
        新增方法delete_segment.
        根据传递的信息删除指定的文档片段信息,配置路由
      * internal/service/segment_service.py下SegmentService类中新建方法:
        delete_segment,
        实现根据传递的信息删除指定的文档片段信息的业务流程,
        SegmentHandler中视图函数delete_segment调用该业务方法完成处理.
      * 启动服务 POSTMAN测试 SegmentHandler.delete_segment
      POST : http://127.0.0.1:5000/datasets/:dataset_id/documents/:document_id/segments/:segment_id/delete
   
# 29 RAG模块修改片段接口实现  项目API文档 - 4.18
   29.1  修改指定的文档片段信息
      * 修改internal/handler/segment_handler.py下的SegmentHandler类,
        新增方法update_segment,根据传递的信息更新文档片段信息,配置路由.
      * 修改internal/schema/dataset_schema.py,为update_segment视图函数
        创建相应请求验证类: 
        UpdateSegmentReq,便捷导出.
      * internal/service/segment_service.py下SegmentService类中新建方法:
        update_segment,
        实现根据传递的信息更新指定的文档片段信息的业务流程,
        SegmentHandler中视图函数update_segment调用该业务方法完成处理.
      * 启动服务 POSTMAN测试 SegmentHandler.update_segment
      POST : http://127.0.0.1:5000/datasets/:dataset_id/documents/:document_id/segments/:segment_id
      测试案例1:
      {
      "content":"这是修改后的片段信息,与文档内容,知识库名称相关联"
      }
      测试案例2:
      {
      "content":"修改后的片段信息,属于某个知识库下的某个文档,支持相似度查询",
      "keywords":["片段","知识库","文档","相似度"]
      }