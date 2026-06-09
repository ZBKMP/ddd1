# 1.OpenAI配置
openai快速入门文档:
https://platform.openai.com/docs/quickstart?desktop-os=windows&language=python

1.1 安装openai模块
pip install --upgrade openai

1.2 安装dotenv模块
pip install dotenv
在项目根目录创建.env文件设置openai 的 api_key

1.3 在app/http/app.py中,添加加载env文件代码

    # 加载env全局配置文件
    dotenv.load_dotenv()

# 2.创建openAI聊天接口

2.1 在internal\handler\app_handler\AppHandler下创建新的视图方法

    def completion(self):
        # 1.提取从接口中获取的输入 POST
        query = request.json.get("query")
        # 2.构建OpenAI客户端,并发起请求
        client = OpenAI(
              # 从env读取配置信息
              api_key=os.getenv("OPENAI_API_KEY"),
              base_url=os.getenv("OPENAI_BASE_URL"),
        )
        # 3.得到请求响应,然后将OpenAI的响应传递给前端
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "你是一个AI助手，负责根据用户提供的提示生成回答"},
                {"role": "user", "content": query}
            ]
        )
        # 4.提取响应内容
        content = completion.choices[0].message.content
        # 5.返回至前端
        return content

2.2 在internal\router\Router为该视图方法进行路由配置

    bp.add_url_rule("/app/completion",methods=["POST"],view_func=self.app_handler.completion)

2.3 使用postman对该接口进行测试,参数以Body\raw\JSON模式封装

    {
     "query":"你好,你是谁?"
    }

2.4 使用dotenv自动加载配置信息
    
    import dotenv
    dotenv.load_dotenv()
    client = OpenAI() #无需再填入配置信息,自动加载


# 3.校验API接口输入请求 wtforms
wtf文档:
https://flask-wtf.readthedocs.io/en/1.2.x/
https://wtforms.readthedocs.io/en/3.2.x/

3.1 安装 flask-wtf 模块
pip install -U Flask-WTF

3.2 在internal\schema 下创建文件app_schema.py
编写CompletionReq类,对基础聊天的query请求参数进行验证

    class CompletionReq(FlaskForm):
      """基础聊天请求验证"""
      # 必填，长度最大为2000
      query = StringField('query',validators=[
         DataRequired(message='用户提问是必填的'),
         Length(min=1,max=2000,message='用户的提问最大程度为2000字')
      ])

在schema.__init__.py中暴露CompletionReq类

3.3 解决在使用WTF模块下引发CSRF验证问题:
在config下增加config文件,编写Config类,后续flask要加载该配置类
暂时关闭 WTF的CSRF验证: self.config["WTF_CSRF_ENABLED"]=False
或者将该配置信息先写在全局配置文件中,使用os.getenv去加载

    class Config:
    def __init__(self):
        # 暂时关闭 WTF的CSRF保护
        # self.WTF_CSRF_ENABLED = False
        # 使用os.getenv去加载 env配置文件中的配置
        self.WTF_CSRF_ENABLED = _get_bool_env("WTF_CSRF_ENABLED")

在config.__init__.py中暴露Config类       

3.4 修改internal\server\http下Http类
增加参数 config:Config,Flask使用该参数进行配置

    def __init__(self,
                 *args,
                 config:Config, # 参数2
                 router:Router, # 参数1
                 **kwargs):
        # 1. 调用父类构造函数初始化
        super().__init__(*args,**kwargs)
        # 2. 关联路由配置
        router.register_router(self)
        # 3. 初始化应用配置
        self.config.from_object(config)

3.5 修改app\app内的Flask启动代码,创建Http类对象时增加参数
   
    app = Http(__name__,
           config=Config(), # 参数 2
           router=injector.get(Router) # 参数 1
           )

3.6 使用postman测试,如前端未传递query参数则会看到错误信息

# 4.统一响应接口设计与实现  规范JSON结构输出

4.1 HTTP响应状态码都是200,为了告知前端业务相应状态,需要定义业务响应状态码.
    在pkg包中新建response包,新建文件http_code.py,新建枚举类HttpCode,编辑各种状态码的值:
   
    #每个枚举值既是枚举成员，也是字符串
    class HttpCode(str, Enum):
       """ http基础业务状态码 """
       SUCCESS ="success", #成功状态
       FAIL = "fail", #失败状态
       NOT_FOUND = "not_found", #未找到
       UNAUTHORIZED = "unauthorized", #未授权
       FORBIDDEN = "forbidden", # 无权限
       VALIDATION_ERROR = "validation_error", # 数据验证错误      


4.2 在pkg.response包下再新建response.py文件,编写自定义Response类,设计响应基础格式.
    所有响应状态码都是200,但通过不同的业务状态码表示各种访问结果类型:
  
    @dataclass #装饰器 自动生成init函数
    class Response(object):
      """基础HTTP接口响应格式"""
      # 响应状态码 默认success
      code:HttpCode = HttpCode.SUCCESS
      # 响应文本消息
      message:str = ""
      # 业务响应数据 默认为{} 但使用filed的默认工厂函数产生空字典
      data:Any= field(default_factory=dict)

4.3 视图方法返回的结果必须为JSON格式,还需要将自定义的Response类对象转换为JSON格式输出.
    在response.py文件内再定义一系列响应函数,将自定义Response转为FlaskJSONResponse   
    包含两组响应模式分别为:
       响应结果有仅data数据没有message的模式
       和响应结果没有data数据仅有message的模式
       既有  又有
    函数中利用Flask的jsonify方法将自定义Response转换为Flask的Response对象，
    
4.4 在pkg.response.__init__py将上述所有定义的类与函数暴露出去

4.5修改internal\handler\app_handler\AppHandler类
   所有视图函数通过上一步骤定义的两组函数的调用结果，作为响应返回值。
   
# 5.异常错误状态统一设计与实现 将错误信息与步骤4的业务状态码关联

5.1 在exception包下创建exception.py文件,
    定义基础异常类CustomException，继承自Exception类:

     class CustomException(Exception):
     """基础自定义异常信息类"""
      code: HttpCode = HttpCode.FAIL
      message: str
      data: Any = field(default_factory=dict) #默认为{}

      def __init__(self,message:str=None,data:Any=None):
        super().__init__()
        self.message = message
        self.data = data

5.2 再按照HttpCode中定义的错误类型,分别定义对应的异常子类
    在__init__.py中导出所有的异常类定义

5.3 在internal\handler\app_handler\AppHandler类中编写测试代码
    在视图方法中手动抛出异常,使用postman测试访问,异常会以HTML形式展示,
    
    这样会将异常信息直接暴露给用户,需要将出异常的显示改换为JSON形式传递到前端,
    再由前端去处理错误信息显示.
     
    def ping(self):
        #return {"ping": "pong"}
        # 3异常测试
        # raise FailException("数据未找到")
        raise ValueError("value error")

5.4 将HTML形式展示的异常信息转也为统一响应接口,也要变为JSON响应
    在server\http.py的Http类中，针对flask对象增加异常配置
    
    5.4.1 Http类的初始方法增加以下代码:

    # 4. 异常错误状态统一设计与实现:注册绑定异常处理
    # 项目中所有异常，统一由一个函数处理
    self.register_error_handler(Exception,self._register_error_handle)
    
    5.4.2 增加自定义的异常处理函数,将异常输出转换为统一响应接口：

    # 自定义异常处理函数
    def _register_error_handle(self,error:Exception):
        # 简单输出
        # print("exception:",error)
        # return error.message

        # 转换为统一响应接口
        # 1.异常如果是我们定义的自定义异常,提取code和message信息
        if isinstance(error,CustomException):
            return json(Response(
                code=error.code,
                message=error.message,
                data=error.data if error.data else {},
            ))

        # 2.不是我们定义的自定义异常,提取信息,设置为FAIL状态码
        if self.debug or os.environ.get('FLASK_ENV')=='development':
            # 开发/调试模式下直接抛出异常,运行转态配置与env文件中
            raise error
        else:
            # 运行模式下才输出至前端
            return json(Response(code=HttpCode.FAIL, message=str(error), data={}))
        # 可以将app以FlaskServer模式配置运行,可更改DEBUG模式,
        # 选择 script模式-->app.py   


# 3,4,5 步骤改造后 completion方法代码

    def completion(self):
       """ 聊天接口 """
       # 1.提取从接口中获取的输入 POST
       # 进行数据验证
       req = CompletionReq()
       # 验证失败则直接响应错误提示文本
       if not req.validate():
          # 返回错误信息
          # return req.errors
          # 增加响应函数定义后 使用响应函数返回结果
          return validate_error_json(req.errors)
       #从CompletionReq获取请求中的query参数数据
       query = req.query.data
       # 2.构建OpenAI客户端,并发起请求
       # 加载所有配置信息 后期移植到config中
       # dotenv.load_dotenv()
       print(os.getenv("OPENAI_API_KEY"))
       print(os.getenv("OPENAI_BASE_URL"))
       client = OpenAI()
       # 3.得到请求响应,然后将OpenAI的响应传递给前端
       completion = client.chat.completions.create(
           model="gpt-3.5-turbo-16k",
           messages=[
                 {"role": "system", "content": "你是一个AI助手，负责根据用户提供的提示生成回答"},
                 {"role": "user", "content": query}
             ]
         )
       # 提取响应内容
       content = completion.choices[0].message.content
       # 返回至前端
       # return content
       # 增加响应函数定义后 使用响应函数返回结果
       return success_json({"content": content})


# 6.PyTest配置字与API测试用例编写  单元测试 程序员自己完成的测试

6.1 安装测试模块 pip install pytest==8.4.2

6.2 在测试包test下建立相关包及测试文件与测试类
    文件路径要保持与被测试包路径对应,以_test结尾或以test_开头,
    类名以Test开头,类不包含__init__方法,测试函数以test_开头
    例如:
    internal_test\handler_test\test_app_handler.py
    test_app_handler.py内编写测试类: TestAppHandler
    编写测试方法:

       # 简单测试
       def test_example(self):
           print('test_example')
           assert 1 == 1  # 断言测试

   注意:一般选择在命令行运行测试方法

6.3 命令行执行:pytest测试所有测试文件中的测试方法
    # 直接运行文件夹内符合规则的所有用例
    pytest folder_name
    # 执行某个 Python 文件中的用例
    pytest test_file.py
    # 执行某个 Python 文件内的某个函数
    pytest test_file.py::test_func
    # 执行某个 Python 文件内某个测试类的某个方法
    pytest test_file.py::TestClass::test_method
    # 运行测试时显示标准输出(stdout)，允许测试中的 print() 语句直接输出到终端
    pytest -s
    # 运行测试时显示详细的信息，包括每个测试用例的名称及结果(通过/失败/跳过等)，-v 代表 verbose
    pytest -v    
   
    工程根目录下增加 pytest.ini文件

    执行测试: pytest test_app_handler.py::TestAppHandler::test_example
    注意: 要进入到测试文件所在的目录下执行!!!    

6.4 使用@pytest.fixture 测试 项目中的视图函数(接口) app_handler\AppHandle 
    使用fixture为测试提供预设数据和设置测试环境
    在test目录下编写conftest.py文件 配置flask_app测试模式,获取测试client对象:

    import pytest
    # 导入app对象以供测试
    from app.http.app import app 
    @pytest.fixture
    def client():
        # 开启测试模式
        app.config['TESTING'] = True
        # 获取测试client对象
        with app.test_client() as client:
             yield client

    在具体的测试类中(test_app_handler),测试方法增加client作为参数
    以client发起请求 进行对视图方法的测试:

    # 测试app_handle 传入测试对象client
    # 会从@pytest.fixture 自动导入client
    def test_completion(self, client):
        print('test_completion')
        # 发起post请求

        # 正确访问测试
        resp = client.post("/app/completion",json={"query":"你好请介绍LLM的发展历史?"})
        assert resp.status_code == 200 #断言
        assert resp.json.get("code") == HttpCode.SUCCESS
        print("response:",resp.json)
    
6.5 在测试方法上增加装饰器@pytest.mark.parametrize,传递多个参数,简化测试案例
    
    # 批量传入多组测试用例 每组参数使用字典封装 ,多组参数封装为列表/元祖
    @pytest.mark.parametrize("params",({"query":"你好你是谁?"},{"query":None}))
    def test_completion2(self,params,client):
        print("test_completion2_information")
        print(params)

        # POST请求
        resp = client.post('/apps/completion', json={"query": params['query']})
        # HTTP响应状态码必须是200
        assert resp.status_code == 200
        # 根据不同的参数 做出不同的断言
        if params['query'] is None or len(params['query']) > 2000:
           assert resp.json.get("code") == HttpCode.VALIDATION_ERROR
        else:
           assert resp.json.get("code") == HttpCode.SUCCESS
        # 输出原本的响应结果
        print("response:", resp.json)

6.7 在项目根目录下配置pytest.ini文件 修改 '.pytest_cache' 目录生成位置,
    要在源码文件架内查看.

# 7 flask_sqlalchemy

7.1 模块安装
pip install flask_sqlalchemy
pip install flask_migrate
pip install psycopg2 #postgres数据库连接驱动 

7.2 flask_postgres配置,在env文件中增加数据库连接配置项

    #数据库连接配置
    SQLALCHEMY_DATABASE_URI=postgresql://postgres:postgres@127.0.0.1:5432/llmops_project2
    SQLALCHEMY_POOL_SIZE=30
    SQLALCHEMY_POOL_RECYCLE=3600
    SQLALCHEMY_ECHO=true

7.3 在config\config.py中Config类中读取数据库配置
在原本app.http.app.py中加载env的代码dotenv.load_dotenv()
转移到Config类的init方法中,项目运行初始化时即加载env文件

    class Config:
    def __init__(self):
        # 加载env全局配置文件
        dotenv.load_dotenv()
        # 暂时关闭 WTF的CSRF保护
        # self.WTF_CSRF_ENABLED = False
        # 使用os.getenv去加载 env配置文件中的配置
        self.WTF_CSRF_ENABLED = _get_bool_env("WTF_CSRF_ENABLED")
        # 数据库配置
        self.SQLALCHEMY_DATABASE_URI =_get_env("SQLALCHEMY_DATABASE_URI")
        self.SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": int(_get_env("SQLALCHEMY_POOL_SIZE")),
            "pool_recycle": int(_get_env("SQLALCHEMY_POOL_RECYCLE")),
        }
        self.SQLALCHEMY_ECHO = _get_bool_env("SQLALCHEMY_ECHO")

7.4 flask extension 扩展代码
    在internal\extension下新建database_extension.py文件
    在文件中创建数据库连接:

    from flask_sqlalchemy import SQLAlchemy
    # 创建数据库连接
    db = SQLAlchemy()

7.5 修改server\http.py中Http类,给init方法增加参数:db 

    class Http(Flask):
    """Http服务引擎"""
    def __init__(self,
                 *args,
                 config:Config, # 参数2
                 db:SQLAlchemy, # 参数3
                 router:Router, # 参数1
                 **kwargs):
        # 1. 调用父类构造函数初始化
        super().__init__(*args,**kwargs)
        # 2. 关联路由配置
        router.register_router(self)
        # 3. 初始化应用配置
        self.config.from_object(config)
        # 4. 异常错误状态统一设计与实现:注册绑定异常处理
        # 项目中所有异常，统一由一个函数处理
        self.register_error_handler(Exception,self._register_error_handle)
        # 5. 关联数据库
        db.init_app(self)
        

7.6 修改app\http中app.py文件,初始化Flask时增加参数:db

    # 创建inject对象,用以创建Router对象
    injector = Injector()
    # 创建flask应用,传入__name__与Router等多个对象作为参数
    app = Http(__name__,
           config=Config(), # 参数 2
           db=db, # 参数 3
           router=injector.get(Router) # 参数 1
    )


7.7 优化上述代码,使用injector.Module 实现使用injector获取一个已创建的对象:db
    在app.http包下新建文件module.py,并修改app.http.app代码:
    
    * module.py:
    class ExtensionModule(Module):
       def configure(self, binder: Binder) -> None:
            # 绑定SQLAlchemy类与db对象
            binder.bind(SQLAlchemy, to=db)
    injector = Injector(modules=[ExtensionModule])

    * app.http.app:
    from .module import injector
    # 加载env全局配置文件
    dotenv.load_dotenv()

    # 创建flask应用,传入__name__与Router等多个对象作为参数
    app = Http(__name__,
           router=injector.get(Router),  # 参数 1 injector 创建路由对象
           config=Config(),  # 参数 2 配置
           db=injector.get(SQLAlchemy),  # 参数 3 injector 获取db对象
           migrate=migrate,  # 参数 4
           )

   
# 8 ORM模型创建 执行增删改查

8.1 在internal\model下创建文件app.py,文件中增加App(db.Model)类定义
    在__init__.py中暴露出App模型类

8.2 在internal\service下创建文件appservice.py,
     编写AppService类,包含项目中的数据库CRUD操作:
     编写方法create_app(创建App类型对象)
     编写方法get_app(根据ID查询单个App对象)
     编写方法update_app(根据ID修改APP对象)
     编写方法delete_app(根据ID删除APP对象)
    在__init__.py中暴露出AppService业务类

8.3 在AppHandler中测试AppService提供的业务方法
    在AppHandler中增加AppService属性引用,编写视图方法调用AppService的CRUD方法,
    为视图方法编写route路由,并通过POSTMan测试

8.4 数据表创建:此时还未生成数据表,在该文件中导入所有需要进行数据迁移的模型类


8.5 修改 model : App 代码
    之前的default其实是通过代码层面上去设置默认值，也就是在使用App实例时，如果没有设置默认值，
    代码层面会填充对应的默认值，但是在数据库层面时没有设置默认值的
    通过程序设置默认值灵活性更强，并且因为程序的默认值不依赖于特定的数据库的函数或特性，具备跨数据库兼容性，
    而且可以通过简单地修改代码代码来更改默认值的生成逻辑，而无需更改数据库本身。
    但是在开发中，缺点也非常明显，开发中数据表里存在数据，通过迁移新增表字段的时候，数据库会新增新增的字段
    记录没有默认值而创建字段失败。
    所以在开发阶段&设计表时，可以考虑同时设置程序默认值和服务器默认值，或者单独设置服务器默认值，
    未设置默认值的字段不添加强约束非空，在开发完成进行部署后，才修改成强约束状态    

    class App(db.Model):
    """AI应用基础模型类"""
    __tablename__ = "app"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_app_id"),
        Index("idx_app_account_id", "account_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    account_id = Column(UUID)
    name = Column(String(255), nullable=False, server_default=text("''::character varying"))
    icon = Column(String(255), nullable=False, server_default=text("''::character varying"))
    description = Column(Text, nullable=False, server_default=text("''::text"))
    status = Column(String(255), nullable=False, server_default=text("''::character varying"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"),
        server_onupdate=text("CURRENT_TIMESTAMP(0)"),
    )
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(0)"))


    为postgres安装uuid,在postgres内执行:
    create extension "uuid-ossp"
    SELECT uuid_generate_v4()    


# 9.重写SQLAlchemy核心类实现事务提交

9.1 在pkg下新建包sqlalchemy,再新建文件sqlalchemy.py,
    编写自定义SqlAlchemy类继承于原本的SqlAlchemy类,实现事务提交
    
9.2 修改 internal\extension\database_extension.py 为导入自定义的SQLAlchemy

9.3 修改 internal\server\http.py\Http类 为导入自定义的SQLAlchemy

9.4 修改 internal\service\appservice.py 为导入自定义的SQLAlchemy,并使用向下文方式改写增删改操作

# 10.flask_migrate 数据迁移

10.1 模块安装 pip install flask-migrate

10.2 在初始化db时初始化migrate
     在internal\extension 下增加migrate_extension文件,进行migrate初始化
    
     from flask_migrate import Migrate
     migrate = Migrate() 
    
10.3 修改internal\server\http\Http 增加初始化参数migrate
     将migrate与app关联:
        
     def __init__(self,
                 *args,
                 config:Config, # 参数2
                 db:SQLAlchemy, # 参数3
                 migrate:Migrate, # 参数4
                 router:Router, # 参数1
                 **kwargs):
        ... ...
   
        # 6. 初始化数据表
        '''
        # 后期进行数据迁移时 可以先注释掉该段代码 由数据迁移进行建表
        with self.app_context():
            print("创建表")
            # 导入App Model 确保会创建该表
            _ = App()
            db.create_all()
        '''
        # 7. 关联migrate  设置迁移文件目录
        migrate.init_app(self, db, directory="internal/migration") 
     
10.4 修改app\http\app文件,在初始化app应用对象时传入migrate对象

     app = Http(__name__,
           config=Config(), # 参数 2
           db=db, # 参数 3
           migrate=migrate, # 参数 4
           router=injector.get(Router) # 参数 1
           )

10.5 在终端使用migrate命令进行数据迁移操作:

### 查看当前项目的路由

flask --app app.http.app routes

### 初始化migrate环境 会创建migrate迁移目录 该命令仅需执行一次

flask --app app.http.app db init

### 创建迁移文件

当前数据库已创建有表,将Http类中的初始化数据表操作注释掉,并删除现有表,测试由数据迁移建表
flask --app app.http.app db migrate -m 'db init'  (-m 注释)
生成文件在version目录下 会在数据库生成迁移记录表

### 执行迁移文件

命令执行后会执行迁移文件代码,并生成相应数据表
flask --app app.http.app db upgrade

flask --app app.http.app db upgrade version_no

### 回退执行迁移文件

命令执行后会执行迁移文件代码,回退到上一版本
flask --app app.http.app db downgrade
回退到最初版本
flask --app app.http.app db downgrade base
回退到指定版本
flask --app app.http.app db downgrade version_no

### 对表进行修建

修改表设计后重新执行 migrate迁移指令,生成新的迁移文件
再执行upgrade 执行新的迁移文件,可观察到数据表结构的更新
  
   
  
  


  
  
  

  