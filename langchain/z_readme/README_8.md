# 运维 优化 配置

# 开发场合下日志写入冲突问题优化解决 
  在运行阶段Flask与Celery都会去修改日志文件,每到凌晨去更改日志文件名时可能会产生冲突.
  使用支持多线程的日志处理器去替代默认的日志处理器:
  1.模块安装 :pip install concurrent-log-handler
  2.更新logging_extension.py,根据不同的环境设置logging根处理器的日志级别.
  3.在service层修改日志输出代码(例如indexing_service.py),使用f-string效率较低改为format
  
# Weaviate向量数据库插件化集成与警告修复
  在使用Weaviate向量库时经常会出现client未关闭的警告,因此要为每次请求创建一个Weaviate连接,
  每次请求结束时释放该连接.
  1.模块安装 : pip install  flask-weaviate

  2.env中增加本地Weaviate配置  host: 192.168.58.129
    # Weaviate向量数据库配置
    WEAVIATE_HTTP_HOST=localhost
    WEAVIATE_HTTP_PORT=8080
    WEAVIATE_GRPC_HOST=localhost
    WEAVIATE_GRPC_PORT=50051

  3.config.py中Config类增加Weaviate配置读取
    # Weaviate向量数据库配置
    self.WEAVIATE_HTTP_HOST = _get_env("WEAVIATE_HTTP_HOST")
    self.WEAVIATE_HTTP_PORT = _get_env("WEAVIATE_HTTP_PORT")
    self.WEAVIATE_GRPC_HOST = _get_env("WEAVIATE_GRPC_HOST")
    self.WEAVIATE_GRPC_PORT = _get_env("WEAVIATE_GRPC_PORT")
    # self.WEAVIATE_API_KEY = _get_env("WEAVIATE_API_KEY")
    
  4.default_config.py中默认配置字典内增加Weaviate默认配置
    # Weaviate向量数据库配置
    "WEAVIATE_HTTP_HOST": "localhost",
    "WEAVIATE_HTTP_PORT": 8080,
    "WEAVIATE_GRPC_HOST": "localhost",
    "WEAVIATE_GRPC_PORT": 50051,
    # "WEAVIATE_API_KEY": "",
    

  5.增加Weaviate扩展: weaviate_extension.py
    app/http/module.py中注入该扩展对象 __init__.py中便捷导出

  6.修改Http类 增加weaviate:FlaskWeaviate参数,
    init中初始化:weaviate.init_app(self)

  7.修改app.http.module.py 
    injector增加weaviate对象与FlaskWeaviate类的绑定

  8.app.py中创建Flask对象时增加weaviate参数

  9.修改vector_store_service


# postgres数据库索引设计与添加
  1.修改model/account.py:
    Index("account_email_idx", "email")
        
    AccountOAuth:
    Index("account_oauth_account_id_idx", "account_id"),
    Index("account_oauth_openid_provider_idx", "openid", "provider"),
  
  2.执行数据迁移


# postgres多表查询优化


# 优化存储推理过程逻辑避免获取空数据


# 区分LLMOps运行环境并配置Celery猴子补丁
 1.模块安装 : pip install gevent 

 2.在app.http.app.py的开头部分增加相关判断,配置猴子补丁:

 ```
  # if os.environ.get("FlASK_DEBUG") == '0' or os.environ.get("FLASK_ENV") == "production":
  #     from gevent import monkey
  #     monkey.patch_all()
  #     import grpc.experimental.gevent
  #     grpc.experimental.gevent.init_gevent()
```

 3.celery -A app.http.app.celery worker --loglevel INFO --pool gevent  --concurrency 10  
   生产环境中 将solo改为gevent
 

# pip-tools Python依赖管理终极方案
 1.模块安装: pip install pip-tools
 

# Model模型onupdate配置与项目Bug维护
 1.更改模型的onupdate_at列配置:
    使用Python函数填充update字段
    onupdate=datetime.now,
 
 2.开发过程中要记录产生的Bug,以及解决过程
 
# 完善项目基础requirements.txt配置
 1.在完整版项目代码中创建Python解析器,安装在项目根目录下新建的.venv目录下.
   终端下安装 : pip install pip-tools

 2.项目代码根目录下新建文件:requirements.in,其中编辑运行环境下主依赖内容.
   终端下执行 : pip-compile .\requirements.in
   会根据主依赖内容生成完整的依赖内容,并写入文件requirements.txt,过程耗时较长.

 3.终端执行:pip-sync .\requirements.txt 完成所有依赖安装

 4.项目根目录下再新建文件:requirements_dev.in,表示测试环境下的依赖内容
   再执行命令 : pip-compile .\requirements_dev.in 完成测试环境下所有依赖安装
              pip-sync .\requirements_dev.txt 完成所有依赖安装
   如果需要回到运行环境下的依赖状态 则可以再执行:pip-sync .\requirements.txt

#################################################################################################


# 项目redis容器化配置部署与持久化
  1.项目docker目录下,docker-compose.yaml文件中增加redis服务的配置

  2.修改.env文件中关于redis配置内容,增加密码配置
    修改config.py文件中关于celery配置内容,增加redis密码配置

  3.在linux的docker环境下构建docker-compose服务:docker compose up -d
    这样会创建并启动docker-compose.yaml内配置的所有镜像及服务


# 项目Postgres数据库容器化配置部署与持久化
  1.项目docker目录下,docker-compose.yaml文件中增加Postgres数据库服务的配置

  2.仅启动postgres_docker: docker compose up llmops-db -d --build  

# Weaviate向量数据库容器化配置与持久化
  1.项目docker目录下,docker-compose.yaml文件中增加Weaviate向量数据库服务的配置

  2.仅启动Weaviate_docker: docker compose up llmops-weaviate -d 

# Gunicorn服务器与命令使用技巧

# 编写API与Celery服务执行脚本
  1.在项目代码根目录下创建文件夹docker,其中编写脚本文件entrypoint.sh,
    后期作为项目docker容器的启动脚本
  
# unstructured依赖于nltk数据下载
  1.如果出现nltk模型报错,进入完整代码根目录下的api目录,再执行以下命令(翻墙):
    python -m nltk.downloader punkt punkt_tab averaged_perceptron_tagger averaged_perceptron_tagger_eng -d ./internal/core/unstructured/nltk_data
  
  2.下载完成后 删除多余的压缩包 *.zip
  
# 同步于异步Weaviate对Gevent的影响
  1.修改requirements.in 增加配置:
    pywin32>=226; platform_system == "Windows"  # concurrent-log-handler的子依赖，在windows环境下需要
    transformers
    pandas

  2.IndexService中_completed方法改为同步写法

  3.app.http.app 中不再需要gevent补丁 
  
  4.修改项目代码目录下docker/entrypoint.sh文件中的celery工作模式配置
    以及gunicorn工作模式

# 编写FlaskAPI服务Dockerfile容器配置
  1.项目代码根目录下新建文件Dockerfile

  2.项目docker目录下,docker-compose.yaml文件中增加llmops-api服务的配置

  3.仅启动llmops-api: docker compose up llmops-api -d --build

# 编写Celery服务Docker容器配置
  1.项目docker目录下,docker-compose.yaml文件中增加llmops-celery服务的配置  
  
  2.仅启动llmops-api: docker compose up llmops-celery -d --build
  
  3.查看Celery日志: docker logs llmops-celery
  

# nginx反向代理服务器配置与部署
  1.docker目录下新建nginx目录,新增nginx.conf等配置文件
  
  2.项目docker目录下,docker-compose.yaml文件中增加llmops-nginx服务的配置
  
  3.重构整体项目: docker compose up  -d --build
    
  4.修改github中 oauth项目配置:
    Homepage URL : http//192.168.xxx.xxx (去掉最后的端口号)
    Authorization callback URL: 按上面的配置类似,去掉端口号
    
  5.按步骤4的配置,修改docker配置中llmops_api与llmops_celery的相关配置
  


# 完整项目访问地址 https://brtc-ai.alltman.com/auth/login



# docker下 发布完整项目：
  1. 复制项目源码至linux下 包含 API docker ui 三个目录
  2. liunx下进入ui目录 执行docker指令:sudo docker build -t llmops-ui:0.0.0.0 .
     耗时5-6分钟,执行docker images 可看到新建的docker镜像:llmops-ui:0.0.0.0    
  3. 测试启动llmops-ui:sudo docker run -d -p 3000:3000 --name llmops-ui llmops-ui:0.0.0.0
     浏览器访问成功后 删除容器 删除镜像 后期用docker compose打包发布启动
  4. 修改docker目录下的docker-compose.yaml:
     llmops-api - environment :
        SERVICE_IP:192.168.142.128
        SERVICE_API_PREFIX: https://192.168.142.128/api
        
        COS_SECRET_ID: your-cos-secret-id
        COS_SECRET_KEY: your-cos-secret-key
        COS_REGION: ap-guangzhou
        COS_SCHEME: https
        COS_BUCKET: llmops-1328730224
        COS_DUMAIN: 
     
        GITHUB_CLIENT_ID: your-github-client-id
        GITHUB_CLIENT_SECRET: your-github-client-secret
        GITHUB_REDIRECT_URI: http://192.168.142.128/auth/authorize/github

        LANGCHAIN_TRACING_V2: 'true'
        LANGCHAIN_ENDPOINT: https://api.smith.langchain.com
        LANGCHAIN_API_KEY: your-langsmith-api-key
        LANGCHAIN_PROJECT: LLMOpsDev
   
        OPENAI_API_KEY: your-openai-api-key
        OPENAI_API_BASE: https://api.ephone.chat/v1
   
        GAODE_API_KEY: your-gaode-api-key
    
        SERPER_API_KEY: your-serper-api-key

     llmops-celery - environment :
        SERVICE_IP: 192.168.142.128
        SERVICE_API_PREFIX: https://192.168.142.128/api
    
        COS_SECRET_ID: your-cos-secret-id
        COS_SECRET_KEY: your-cos-secret-key
        COS_REGION: ap-guangzhou
        COS_SCHEME: https
        COS_BUCKET: llmops-1328730224
        COS_DUMAIN: 
  
        GITHUB_CLIENT_ID: your-github-client-id
        GITHUB_CLIENT_SECRET: your-github-client-secret
        GITHUB_REDIRECT_URI: http://192.168.142.128/auth/authorize/github

        LANGCHAIN_TRACING_V2: 'true'
        LANGCHAIN_ENDPOINT: https://api.smith.langchain.com
        LANGCHAIN_API_KEY: your-langsmith-api-key
        LANGCHAIN_PROJECT: LLMOpsDev
   
        OPENAI_API_KEY: your-openai-api-key
        OPENAI_API_BASE: https://api.ephone.chat/v1
 
        GAODE_API_KEY: your-gaode-api-key
    
        SERPER_API_KEY: your-serper-api-key

  5.进入docker目录 启动docker-compose 
    sudo docker compose up -d
  
  6.修改GITHUB上的 URL配置：
    Homepage URL : http://192.168.142.128
    callback URL : http://192.168.142.128/auth/.....