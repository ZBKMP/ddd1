配置 pip 镜像
python.exe -m pip install --upgrade pip
pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple

# 1.创建项目目录结构/Inject依赖注入/dataclass
  1.1 依据文档要求建立项目结构 
      注意在settings->project->structure中更改test目录模式为Tests,该目录不参与编译
  1.2 依赖注入/dataclass 案例

# 2.创建Flask的视图函数类 AppHandler

2.1 在internal/handler包下创建app_handler.py,编写视图函数类AppHandler类,
2.2 先编写一个最简单的视图方法 (def ping) 测试flask项目的启动  
2.3 编辑__init__.py暴露AppHandler类 被导入时路径中可以省去文件名

# 3.创建Flask路由管理工具类Router

3.1 在internal/router包下创建router.py
    编写Router类,导入AppHandler类,该类中视图方法的路由配置由该类实现
    在类中编写方法register_route方法传入app:Flask作为参数
    类中添加属性 app_handler = AppHandler(),
    由@injext实现依赖注入app_handler,
    并通过@dataclass省略__init__初始化函数
3.2 方法内创建蓝图，由bp.add_url_rule设置app_handler.ping视图方法的路由
3.3 将蓝图与Flask对象绑定
3.4 编辑 router.__init__.py 暴露Router类

# 4.创建Flask应用类 Http,继承自Flask

4.1 在internal/server目录下创建http.py
    编写Http类(继承于Flask),初始化函数传入Router类对象
    *args  **kwargs 用于向父类传递参数
    例如Flask的第一个参数__name__
   
    class Http(Flask):
    """Http服务引擎"""
      def __init__(self,
                 *args,
                 router:Router,
                 **kwargs):
        # 1. 调用父类构造函数初始化
        super().__init__(*args,**kwargs)
        # 2. 关联路由配置
        router.register_router(self)

4.2 server.__init__.py中暴露出Http类  

# 5. 创建项目启动文件 app.py

5.1 在app/Http目录下编写app.py文件(项目启动文件) 
   app.py中创建Http(Flask)对象,以Router对象作为参数传入
  
   # 创建inject对象,用以创建Router对象
   injector = Injector()
   # 创建flask应用,传入__name__与Router等多个作为参数
   app = Http(__name__,
           router=injector.get(Router)
         )  

5.2 编写main执行过程,启动Flask,测试访问路由路径
5.3 可以将app以FlaskServer模式配置运行,可更改DEBUG模式,
    运行选择->script模式-->app.py
5.4 建议在终端启动 : py -m app.http.app   


# 6.查看项目依赖包,并写入文件
6.1 freeze指令
生成当前环境的所有包
pip freeze > requirements.txt
或者只生成项目直接依赖（需要 pip 21.2+）
pip freeze --exclude-editable > requirements.txt

6.2 依据 requirements.txt 安装模块
pip install -r requirements.txt

# 7.postman / apipost
7.1.安装 注册 登录
7.2.创建workspaces 创建项目->文件夹->新请求
7.3在Environment下创建环境,测试新建环境与全局环境下的变量使用
7.4测试请求参数(get/post),测试路由参数,均需要后台支持

# 8.Postgres数据库
下载地址:https://postgresql.org/download
8.1 安装Postgres 启动pgAdmin4

8.2 ubuntu / docker 安装并连接postgresql

8.3 postgresql执行：create extension "uuid-ossp"; 安装uuid扩展

create extension "uuid-ossp";
SELECT uuid_generate_v4();
   
  