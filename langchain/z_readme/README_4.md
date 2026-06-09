#    插件广场(内置工具) 与 自定义插件

# 1 插件广场(内置工具) 与 自定义插件 功能模块分析
 UI设计稿 https://js.design/f/I_B1Is?p=H6nW02nJkv&mode=design
 
# 2 YAML+工厂函数实现插件化配置思路
  2.1 工厂函数与Python动态导入
    * 项目中大模型需要绑定的工具是不确定的,根据用户的需要灵活变动需要绑定的工具,可使用工厂函数
      灵活创建需要的工具对象.
    * 工厂函数:定义函数用于创建对象,由输入的参数来决定创建什么对象
          由工厂模式实现(factory_method_demo.py)
    * 基于工厂函数概念,项目中要获取某个工具,期望实现的模式为:
 ```
  google_serper = get_provider_plugin("google", "google_serper")
  print(google_serper().invoke("2024年北京半程马拉松前3名成绩是多少?"))
 ```
  传入提供商名称与工具名称即可获取对应工具. 该方法可能的实现过程假设为:

 ```
                           工具提供商           工具名称
  def get_provider_plugin(provider_name: str, plugin_name: str) -> BaseTool:
    provider_plugin_map = {
        "google": {
            "google_serper": GoogleSerperRun(...),
            "google_news": GoogleSerperNews(...),
        },
        "gaode": {
            "gaode_ip": GaodeIp(...),
            "gaode_weather": GaodeWeather(...),
        },
        ... ...
    }
    return provider_plugin_map[provider_name][plugin_name]
 ```

  上述代码过于笨拙,所有工具需要事先创建好加入字典中,不利于后期扩展.
  可以使用python中的'动态导入'优化上述逻辑,根据配置(YAML)自动化加载工具字典.

  2.3动态导入:在运行时加载模块或包,而不是在程序启动时就静态导入.
          Python中可以用标准库提供的importlib模块来实现动态导入
          (importlib_demo.py)
  
  2.4 工厂模式与动态导入的结合的两种方式:
     a.提供一个特定格式的配置文件(YAML),在工厂函数内部先读取这个配置文件,找到所有工具的路径,
       然后循环遍历进行动态导入所有工具,从而完成工具映射.这样新增工具时只需要修改配置
       文件并在特定的位置存放模块即可.(推荐使用)
     b.提供一个特定的路径,在工厂函数内部先遍历该路径,并默认该路径下所有的*.py文件都是
       工具,将遍历的所有文件进行动态导入,从而完成工具映射.这样新增工具时,只需要在特定
       路径下新增,即可被工厂函数识别.

  2.5 根据图片:YAML+工厂函数实现添加插件流程.png,分析实现流程.
     * 内置工具的包结构为:
     在internal/core/tools/builtin_tools下
     - categories   #工具类型信息
     - entities     #实体包(类型实体 提供商实体 工具实体)
     - providers
       - google
         - _asset    #提供商图标目录
         - google_serper.py    #具体工具实现代码
         - google_serper.yaml  #工具配置信息(名称 label 描述 参数 )
         - positions.yaml      #提供商下所有工具位置排列配置
       - dalle      #其他提供商目录
         - ... ...
       - gaode
         - ... ...
       - ... ... 
       - builtin_provider_manager.py  内置工具管理类 (工厂函数类)
       - providers.yaml  所有提供商信息配置文件
     
     * 加载思路:
     工具管理类中的'工厂函数'加载 '所有提供商信息配置文件' 获取所有提供商信息,
     再加载每个提供商下的工具信息,从而拼接出每个工具的包路径,配合'动态加载',
     创建出工具信息字典,即可根据传入的提供商名称和工具名称获取具体工具信息。
   
  
# 3 工厂函数实现动态配置内置插件  
  3.1 internal/core下建立tools/builtin_tools包，其中包含所有内置工具的代码
     * 包下建立providers包,包含各个服务提供商的工具类代码,以及provides.yaml
       配置文件,包含所有提供商的配置信息.
     * provides.yaml配置文件中包含多个内置服务提供商(数组),每个配置以 - 开头,
       对应每个服务提供商也建立一个对应包.
     * 内置服务提供商 : google  gaode  dalle time wikipedia ... ...

  3.2 每个服务提供商包下包含以下的工具信息文件:
      _asset:图标目录
      __init__.py:初始化文件用于便捷导出.
      positions.yaml:工具排序位置配置文件 描述该提供商提供的工具以及工具排列顺序.
      {tool_name}.py:具体的工具文件,包含生成工具对象的函数,函数名与工具同名,
                     函数要便捷导出.
      {tool_name}.yaml:工具对应的描述信息配置文件,包含name,label,description,
                       params(使用工具要提供的参数).

  3.3 按3.2的目录结构在google服务提供商目录下创建google_serper工具
     * google_serper.py中编写函数:google_serper(**kwargs)->BaseTool,
       返回工具对象实例.对于需要有参数输入的工具,必须定义参数Schema.
     * 编写工具配置文件 google_serper.yaml.     

  3.4 使用工厂函数读取提供商及工具的yaml配置信息  
     * providers包下创建builtin_provider_manager.py,编写工厂方法类:
       BuiltinProviderManager,便捷导出.
     * BuiltinProviderManager中定义字典provider_map与读取配置的工厂函数:
       _get_provider_map,初始化时即执行该函数,以读取提供商与工具.
     * builtin_tool下创建包entities,包含描述各类型数据实体的BaseModel,便捷导出:
       1.ProviderEntity: 服务提供商实体类,内容对应providers.yaml
         配置文件中的每个配置项.(provider_entity.py)
       2.Provider: 服务提供商类,其中包含ProviderEntity以及所有工具、描述、图标
         等多个信息(核心代码).
       3.ToolEntity: 工具实体类,内容对应每个配置文件中的每个配置项.
        (tool_entity.py)
     * internal下建立lib/helper.py,提供动态导入的工具函数dynamic_import,
       便捷导出.
     * Provider类中,初始化过程最后通过调用dynamic_import实现动态获取每个
       builtin_tool的工具生成函数.
     * BuiltinProviderManager中再定义多个辅助函数:get_xxx,获取提供商或工具信息.
     * 在AppHandler.ping方法中测试 调用BuiltinProviderManager对象方法以获取
       需要的工具:
      GET : http://127.0.0.1:5000/ping

  3.5 带可配置参数的工具配置及获取逻辑
      部分工具在执行时还需要传入对应可配置参数,例如delle,可以设定图片分辨率,
      数量,质量,风格等参数
     * 在builtin_tool/entities/tool_entity.py下增加工具调用时的参数实体
       ToolParam,以验证数据格式.
     * 更新ToolEntity代码, 其中的params列表元素要限定类型为ToolParam
       ,以及定义类型枚举ToolParamType 
     * 更新tool_name.yaml,为params增加可配置参数描述,修改后可能需要重启才生效
        (完善dalle的配置参数,进行测试)
     * 再在AppHandler.ping方法中测试,通过BuiltinProviderManager
       获取Provide对象,再获取ToolEntity并输出,可看到tool_name.yaml配置的
       参数信息:
       GET : http://127.0.0.1:5000/ping

# 4 基于上述逻辑增加其他服务提供商及内置工具
  4.1 服务提供商 time
     providers.yaml增加相关配置
     providers包下增加time包,按照google包的格式添加工具内容
     工具:current_time

  4.2 服务提供商 duckduckgo
     providers.yaml增加相关配置
     providers包下增加duckduckgo包,按照google包的格式添加工具内容
     工具:duckduckgo_search

  4.3 服务提供商 delle
     providers.yaml增加相关配置 包含参数配置 
     providers包下增加delle包,按照google包的格式添加工具内容  
     工具:dalle3

  4.4 服务提供商 gaode
     providers.yaml增加相关配置
     providers包下增加gaode包,按照google包的格式添加工具内容 
     工具:gaode_weather

  4.5 服务提供商 wikipedia
     wikipedia.yaml增加相关配置
     providers包下增加wikipedia包,按照google包的格式添加工具内容
     安装包 : pip install wikipedia
     工具:wikipedia_search 

  4.6 在AppHandler.ping方法中测试 测试查看所有ProviderEntity,
      再获取每个工具 测试调用每个工具      

# 5 内置工具:插件广场API接口分析  项目API文档 - 2.2 2.3 
  5.1 内置工具API接口实现 获取所有内置插件(提供商,工具)列表信息  编写视图类与配置路由,以及业务服务层  
      * handler下新建builtin_tool_handler.py文件,编写视图类
        BuiltinToolHandler,包含内置工具API接口的视图函数:
        get_builtin_tools 获取所有provider信息及内置工具信息,绑定路由
        get_provider_tool 根据提供商信息及工具名称获取指定工具,绑定路由
      * 视图方法功能的具体实现由业务服务层实现,service下新建
        builtin_tool_service.py,编写BuiltinToolService类,实现业务服务过程:
        get_builtin_tools
        get_provider_tool

  5.2 BuiltinToolService.get_builtin_tools代码实现
      * 在BuiltinToolService.get_builtin_tools中,获取内置工具列表时,
        除了工具实体,还要提取工具的inputs,代表工具的输入信息,要将有输入规范
        Schema的工具，将输入规范Schema转换为工具生成函数的属性,从而能提取出inputs.
      * 在lib包下的help.py中定义add_attribute装饰器,以将工具输入Schema转换为
        工具生成函数的属性:args_schema.
        带有输入Schema的工具:dalle3,duckduckgo_search,gaode_weather,
                           google_serper,wikipedia,
        不需要输入Schema的工具:current_time
      * BuiltinToolService.get_builtin_tools实现加载provider信息及内置
        工具信息,以及包含每个工具中的inputs输入信息.
  
  5.3 BuiltinToolService.get_provider_tool代码实现 
      * 代码流程参考5.2的实现过程.
      * 观察接口文档可查,BuiltinToolHandler的get_provider_tool响应结果时,
        create_at字段要放在最外层.

  5.4 BuiltinToolHandler类中实现get_builtin_tools与get_builtin_tool方法代码
      * get_builtin_tools方法调用BuiltinToolService的get_builtin_tools方法,
        输出对应的JSON结果
      * get_provider_tool方法调用BuiltinToolService的get_provider_tool方法,
        输出对应的JSON结果
      * 为BuiltinToolHandler 的两个视图方法配置路由 并使用postman测试访问:
      GET : http://127.0.0.1:5000/builtin-tools
      GET : http://127.0.0.1:5000/builtin-tools/:provider_name/tools/:tool_name
      :provider_name 表示路径参数


# 6 内置工具:插件广场分类与图标API接口   项目API文档 - 2.1 2.4
  6.1  提供商图标文件响应接口
       * 先检查providers.yaml中每个工具的icon配置文件名与每个asset目录下的文件名
         是否相同,避免后期出错.
       * 在BuiltinToolService编写业务层方法get_provide_icon 获取图标字节流及
         文件类型信息.
       * BuiltinToolHandler视图方法get_provider_icon调用业务层方法:
         get_provide_icon,响应结果为字节流文件.
       * 配置路由,postman测试get_provider_icon查看响应的图片
       GET : http://127.0.0.1:5000/builtin-tools/:provider_name/icon

  6.2  提供商分类信息响应接口
       * 先在builtin_tools下增加categories包,包下增加分类信息yaml配置文件,
         以及对应各种类型的图标目录,图标都是svg类型.
       * 新增文件builtin_tools.entities.builtin_entity.py,编写
         CategoryEntity实体类,便捷导出.
       * 新增文件builtin_tools.categories.builtin_category_manager.py,
         编写BuiltinCategoryManager工具类,实现管理读取分类信息,便捷导出.
       * BuiltinToolHandler.get_categories中调用
         BuiltinToolService.get_categories响应出所有分类信息.
       * BuiltinToolService新增方法:get_categories,
         其中调用BuiltinCategoryManager.get_category_map获取所有分类信息.
       * 为BuiltinToolHandler.get_categories配置路由,
         postman测试get_categories,查看响应结果:
       GET : http://127.0.0.1:5000/builtin-tools/categories

-----------------------------------------------------------------------------------------------------------------------

# 7 自定义工具: OpenAPI规范解读与API插件设计思路
  7.1  OpenAPI规范介绍 
       对于企业现有的 API(其他第三方服务API)，想要接入到 LLMOps 项目中(作为项目内的用户自定义工具来使用)，
       一般来说，有两种策略：
       1.创建一个内置插件,在内置插件中,使用 requests 包对特定的 API 接口发起请求，
     工具的参数就是API 请求的参数,这种实现方法设计起来非常简单,使用requests包发起
     特定的请求即可，但是一个接口就要新增一个 Python 文件、一个 Yaml 描述文件,
     并且每次新增都需要重新启动项目，非常繁琐.例如我们已经实现过的高德天气查询工具,
     如果类似的其他工具都要以类似模式定义,工作量非常大.
       2.使用一种规范用来描述API接口，然后程序根据这个规范来提取数据，涵盖了:请求地址、
     请求参数、请求方法等信息，从而向特定的API接口发起请求，这种方式对比内置插件会更
     灵活，通过一个程序实现对任意的 API 接口实现请求，只需要传递不同的规范描述即可。
     这些API接口的访问信息存储于数据库. 
     (推荐使用)
         openAPI规范文档:https://spec.openapis.org/oas/latest.html 
         翻译文档:https://openapi.apifox.cn/  
       3.基于OpenAPI规范的JSON接口描述示例:
```
{
    // openapi版本 
  "openapi": "3.1.0",   
    // 接口信息,包含:标题 描述 版本
  "info": {            
    "title": "获取天气预报数据",
    "description": "检索某个位置当前的天气预报",
    "version": "v1.0.0"
  },
    // 接口所有可以访问的URL地址
  "servers": [  
    {
      "url": "https://weather.example.com"
    }
  ],
    // 服务下可以访问的所有路由
  "paths": {
       // 名为 /location 路由的具体信息 
    "/location": {
       // 该路由下GET请求方式访问描述
      "get": {
        "description": "获取特定位置的天气预报信息",
        "operationId": "GetCurrentWeather",
            //参数列表 
        "parameters": [
          {
             // 参数名
            "name": "location",
             // 参数位置 query表示?后的查询字符串
            "in": "query",
             // 参数描述
            "description": "需要获取天气预报的城市名",
             // 是否必填
            "required": true,
             // 参数规范 如:参数数据类型
            "schema": {
              "type": "string"
            }
          }
        ],
          // 是否过时抛弃
        "deprecated": false
      }
    }
  },
  "components": {
    "schemas": {}
  }
}
```
          
  8.2 基于OpenAPI规范的API插件(工具)
      1.对于企业现有接口，接口请求方式无非是 Get、Post、Delete、Put、Options 等.
    附加的数据无非是Header、Query、Body、Cookie 中,对于API接口我们可以使用OpenAPI
    规范来进行描述,符合OpenAPI规范的JSON,我们可以轻易使用程序读取其请求接口地址、
    请求方法、请求参数及详情、路径的描述,从而发起特定的请求。
      基于这个思想，我们可以来构建一个APITools,该工具传入OpenAPI规范的数据,从而创建
    一个请求工具,该请求工具会根据传递的配置构建一个函数,接收特定的参数,并向特定的API
    接口发起请求。
      这个思想就是LLMOps中创建自定义API工具的思路,因为对于企业现有的API,我们往往更
    希望通过手动在页面配置的方式进行热集成,而不是在后端代码中添加一个工具,然后重新运行
    项目。
      所以本质上就是创建一个'类/函数',该'类/函数'接收OpenAPI Schema数据,并返回一个
    自定义工具,该自定义工具被调用时会向OpenAPI Schema数据里描述的接口发起请求,并且
    该自定义工具参数就是OpenAPI Schema描述的参数.
      2.思路已经有了,核心部分就是如何设计一套程序,将OpenAPI-Schema转换成
    LangChain-BaseTool,在这部分存在几个需要解决的问题:
    1.一个OpenAPI-Schema描述中存在多个paths，其中一个path代表一个API或者一个工具，
      如何将一个OpenAPI-Schema转换成多个provider+tool的工具包.
    2.OpenAPI-Schema描述的信息是JSON(字典)，如何将其转换成LangChain-Tool中的
      name(String)、description(String)、args_schema(BaseModel类)等信息,
      对于args_schema类,pydantic包是否提供了从json->BaseModel类的便捷性方法.
    3.OpenAPI-Schema描述的信息是JSON(字典),如何将servers+paths描述信息绑定到
      requests上,从而实现不同工具发起不同的请求并携带不同的参数.
    4.对于LLMOps项目来说,这是一个多用户的系统,如何设计一套存储方案,可以存储多个用户
      的多个OpenAPI-Schema规范信息,并相互进行隔离.

# 9 自定义工具:使用简化OpenAPI规范描述API工具 项目API文档-项目OpenAPI-Schema规范
  9.1 项目OpenAPI-Schema规范 
      在LLMOps项目中,如果使用完整的OpenAPI-Schema规范来描述API工具会显得特别繁琐,
      所以我们对OpenAPI-Schema规范进行相应的简化+调整,做出如下约定:
     1.所有的外部API请求类型只有GET/POST,并没有DELETE/PUT等方法,一个路径下可以拥有
       多个方法，例如同时拥有GET/POST,在项目中使用OperationId进行唯一标识判断(工具名称).
     2.基础的API地址有且只有一个,被添加到server中,该规范是LLMOps项目自行约定的,
       并不是标准OpenAPI规范.
     3.接口的数据可以作为参数被附加到Header/Query/Cookie/Path/RequestBody
       这5个位置.
     4.所有的参数都使用parameters进行记录,'in'参数的类型支持:
        path/query/header/cookie/request_body
       分别代表:请求路径、查询query、header请求头、cookie、
               RequestBody(只有POST才有).
     5.type类型支持str(字符串)、float(浮点型)、int(整形)、bool(布尔值)
       共计 4 种基础类型,注意下该规范并不是OpenAPI内置的定义,
       而是我们为了简化描述方案而约定的.
     6.required字段表示是否可选可不选,默认情况下都是true,代表是必填的。
  
  9.2  项目中使用的,简化后的OpenAPI规范的JSON接口描述示例:
```
{
  "description": "查询ip所在地、天气预报、路线规划等高德工具包",
  "server": "https://weather.example.com",
  "paths": {
    "/weather": {
      "get": {
        "description": "获取特定位置的天气预报信息",
        "operationId": "GetCurrentWeather",
        "parameters": [
          {
            "name": "location",
            "in": "query",
            "description": "需要获取天气预报的城市名",
            "required": true,
            "type": "str"
          },
          {
            ....
          }
        ]
      },
      "post":{
        
      }
    },
    "/ip": {
      "get": {
        "description": "根据传递的ip地址获取所在地",
        "operationId": "GetIpLocation",
        "parameters": [
          {
            "name": "ip",
            "in": "query",
            "description": "需要查询地址的标准ip，例如201.142.15.5",
            "required": true,
            "type": "str"
          }
        ]
      }
    }
  }
}  
```

# 10 自定义工具:个人空间插件模块API分析 项目API文档-2.5 2.6 2.7 2.8 2.9 2.10 2.11 2.12 

# 11 自定义工具:API插件数据库表设计与ORM实现
  11.1 internal/model下新增api_tool.py文件,增加模型类:
       ApiToolProvider,AppTool,便捷导出.
  11.2 在server/http.py中导入新增的模型类,执行数据迁移操作,
       注意提前为postgres安装uuid,在postgres内执行:
        create extension "uuid-ossp"
        SELECT uuid_generate_v4()  

# 12 自定义工具: OpenAPI结构数据验证接口实现与测试 项目接口文档 - 2.12
  12.1 OpenAPI结构数据验证接口
       * handler下新增文件api_tool_handler.py编写类ApiToolHandler,自定义工具
         API接口处理器,便捷导出.
         类中新增视图方法:validate_openapi_schema用于验证传入的openai_schema
         字符串的格式.
       * schema包新增api_tool_schema.py文件,为视图方法validate_openapi_schema
         编写请求参数验证类:ValidateOpenApiSchemaReq(FlaskForm),验证参数合法性,
         便捷导出.
       * 在service包下新增文件api_tool_service.py,定义业务服务类ApiToolService,
         定义类方法parse_openapi_schema,用于解析openapi_schema字符串格式,
         解析错误抛出异常。
         先初步判断传入的openapi_schema是否为基本的JSON格式,否则抛出自定义异常,
         后续对openapi_schema字符串格式的完整验证,由类OpenAPISchema(BaseModel)
         完成.
       * 在core/tools包下新建 api_tools包,再新建entities子包,新建文件
         openapi_schema.py.
         创建实体类OpenAPISchema(BaseModel),属性包含server,description,paths 
         表示OpenAPI规范的数据结构,基于Pydantic对该类中的每个属性进行校验.
         重点验证paths属性,便捷导出(核心代码).
       * 上述过程中需要在openapi_schema.py中定义两个枚举类: 
         ParameterType 与 ParameterIn,便捷导出.
       * ApiToolService中方法parse_openapi_schema中,借助OpenAPISchema来验证
         openapi_schema数据格式是否正确,并返回解析结果.
       * 视图函数ApiToolHandler.validate_openapi_schema调用
         ApiToolService.parse_openapi_schema方法,
         完成penAPI结构数据验证接口业务流程.配置路由,postman测试访问.
        POST : http://127.0.0.1:5000/api-tools/validate_openapi_schema
        { 
          "openapi_schema": "{\"description\":\"这是一个查询对应英文单词字典的工具\",\"server\":\"https://dict.youdao.com\",\"paths\":{\"/suggest\":{\"get\":{\"description\":\"根据传递的单词查询其字典信息\",\"operationId\":\"YoudaoSuggest\",\"parameters\":[{\"name\":\"q\",\"in\":\"query\",\"description\":\"要检索查询的单词，例如love/computer\",\"required\":true,\"type\":\"str\"},{\"name\":\"doctype\",\"in\":\"query\",\"description\":\"返回的数据类型，支持json和xml两种格式，默认情况下json数据\",\"required\":false,\"type\":\"str\"}]}}}}"
        }
        错误测试案例1:
        { 
          "openapi_schema": "{\"description\":\"这是一个查询对应英文单词字典的工具\",\"server\":\"https://dict.youdao.com\",\"paths\":\"123123\"}"
        }
        错误测试案例2:
        { 
          "openapi_schema": "{\"description\":\"这是一个查询对应英文单词字典的工具\",\"server\":\"https://dict.youdao.com\",\"paths\":{}}"
        }
         openapi_schema参数实际的JSON结构(如果作为参数需要将双引号加上转译字符):
```
上述正确测试案例的数据 等同于以下JSON字符串
{
  "description": "这是一个查询对应英文单词字典的工具",
  "server": "https://dict.youdao.com",
  
  "paths": {
  
    "/suggest": {
    
      "get": {
        "description": "根据传递的单词查询其字典信息",
        "operationId": "YoudaoSuggest",
        "parameters": [
          {
            "name": "q",
            "in": "query",
            "description": "要检索查询的单词，例如love/computer",
            "required": true,
            "type": "str"
          },
          {
            "name": "doctype",
            "in": "query",
            "description": "返回的数据类型，支持json和xml两种格式，默认情况下json数据",
            "required": false,
            "type": "str"  
          }
        ]
      }
    }    
  }
}
```    

# 13 自定义工具: 创建自定义API插件接口的设计与实现 项目API文档 - 2.7 
  13.1 创建自定义API插件接口的设计与实现 
     * ApiToolHandler新增视图方法 create_api_tool_provider,用于实现创建自定义
       API工具接口.
     * internal.schema.api_tool_schema.py中为视图函数create_api_tool_provider
       创建请求参数验证类:CreateApiToolReq(FlaskForm),便捷导出.
     * CreateApiToolReq中的headers参数 使用自定义的ListField,替代wtforms中官方
       的ListField,internal.schema包下新建schema.py,编写自定义的ListField,
       便捷导出.
     * CreateApiToolReq(FlaskForm)中编写自定义的验证方法,对headers参数单独定义
       方法进行格式校验.
     * internal.service.api_tool_service.py中ApiToolService类中新增业务方法
       create_api_tool_provider,根据传递的请求创建自定义API工具.
     * ApiToolHandler.create_api_tool_provider中调用
       ApiToolService.create_api_tool_provider,完成 创建自定义API插件 业务流程,
       为视图方法新增路由配置 postman测试.
       POST : http://127.0.0.1:5000/api-tools
{
    "name":"有道翻译工具包",
    "icon":"https://llmops-1328730224.cos.ap-guangzhou.myqcloud.com/2026/01/14/fa85547f-b9f9-4583-9ef6-ed837c9ee308.png", 
    "openapi_schema": "{\"description\":\"这是一个查询对应英文单词字典的工具\",\"server\":\"https://dict.youdao.com\",\"paths\":{\"/suggest\":{\"get\":{\"description\":\"根据传递的单词查询其字典信息\",\"operationId\":\"YoudaoSuggest\",\"parameters\":[{\"name\":\"q\",\"in\":\"query\",\"description\":\"要检索查询的单词，例如love/computer\",\"required\":true,\"type\":\"str\"},{\"name\":\"doctype\",\"in\":\"query\",\"description\":\"返回的数据类型，支持json和xml两种格式，默认情况下json数据\",\"required\":false,\"type\":\"str\"}]}}}}",
    "headers":[{"key":"Authorization","value":"token_123123"},{"key":"xxxx","value":"xxxx"}]
} 

# 14 自定义工具: 获取指定的API工具提供者信息  项目API文档 - 2.10
  14.1  获取指定的API工具提供者信息
      * ApiToolHandler新增视图方法 get_api_tool_provider
      * ApiToolService 新增业务方法 get_api_tool_provider
      * 视图方法调用业务方法实现数据查询 返回ApiToolProvider对象
        
  14.2  marshmallow 将对象序列化为dict(JSON字符串)
      * 安装marshmallow模块:pip install marshmallow.实现对象的序列化与反序列化
        用于将python对象直接序列化成JSON 以响应给前端
      * internal.schema.api_tool_schema.py中为视图方法get_api_tool_provider
        新增响应结果封装类:GetApiToolProviderResp(marshmallow.Schema),便捷导出.
      * 视图方法中使用ApiToolHandler.get_api_tool_provider该Schema类将
        ApiToolProvider序列化为JSON.配置路由,postman测试访问.
       GET : http://127.0.0.1:5000/api-tools/:provider_id
       

# 15  自定义工具: 获取指定的API工具信息  项目API文档 - 2.11
  15.1  获取指定的API工具信息
      * ApiToolHandler 新增视图方法 get_api_tool,
        ApiToolService 新增业务方法 get_api_tool,
        视图方法调用业务方法实现数据查询,返回ApiTool对象.
      * 查询ApiTool的结果中还要包含ApiToolProvider对象,在model/api_tool.py
        中为ApiTool类增加只读属性,返回对应的ApiToolProvider对象
      * 在schema/api_tool_schema.py中为视图方法ApiToolHandler.get_api_tool
        定义响应数据结构封装类:GetApiToolResponse(marshmallow.Schema)
        视图方法get_api_tool中使用该Schema类将ApiTool序列化为JSON
      * 为视图方法ApiToolHandler.get_api_tool_provider编辑路由 postman测试访问
       GET : http://127.0.0.1:5000/api-tools/:provider_id/tools/:tool_name
        
  
# 16 自定义工具: 删除自定义API工具提供者+工具  项目API文档 - 2.8
  16.1  删除自定义API工具提供者+工具
      * ApiToolHandler 新增视图方法 delete_api_tool_provider. 
      * ApiToolService 新增业务方法 delete_api_tool_provider.
      * 视图方法调用业务方法实现数据删除.
      * 为视图方法ApiToolHandler.delete_api_tool_provider,
        配置路由 postman测试访问
      POST : http://127.0.0.1:5000/api-tools/:provider_id/delete
  
# 17 自定义工具: 自定义API工具数据分页接口实现  项目API文档 - 2.5
  17.1  自定义API工具数据分页接口
      * ApiToolHandler 新增视图方法 get_api_tools_providers_with_page
      * ApiToolService 新增业务方法 get_api_tools_providers_with_page
        视图方法调用业务方法实现数据查询
      * 在schema/api_tool_schema.py中为视图方法get_api_tools_providers_with_page
        定义请求的参数验证类:GetApiToolProvidersWithPageReq(PaginatorReq) 
        其中分页相关的参数包含在pkg/paginator.py中的PaginatorReq父类中
      * 实现业务方法 get_api_tools_providers_with_page过程,
        为实现分页设计分页器:pkg/paginator.py中新增Paginator分页器类 
        在查询过程中实现分页查询
      * 定义响应的数据结构:GetApiToolProvidersWithPageResp(marshmallow.Schema)
        过程中需要为 ApiToolProvider 提供只读属性tools:读取旗下所有的工具组成列表
        视图方法ApiToolHandler.get_api_tools_providers_with_page中使用该
        Schema类将序列化为JSON
      * 为视图函数ApiToolHandler.get_api_tools_providers_with_page配置路由 
        postman测试:
      GET : http://127.0.0.1:5000/api-tools

# 18 自定义工具:修改自定义API插件接口的设计与实现  项目API文档 - 2.9
  18.1  修改自定义API插件接口
      * ApiToolHandler 新增视图方法 update_api_tool_provider
      * ApiToolService 新增业务方法 update_api_tool_provider
      * 视图方法调用业务方法实现数据修改
      * 在schema/api_tool_schema.py中为视图方法ApiToolHandler.update_api_tool_provider
        定义请求的参数验证类:UpdateApiToolProviderReq(FlaskForm),便捷导出
      * 为视图函数ApiToolHandler.update_api_tool_provider,
        配置路由 postman测试
     POST : http://127.0.0.1:5000/api-tools/:provider_id
{
    "name":"有道翻译工具包_1",
    "icon":"https://llmops-1328730224.cos.ap-guangzhou.myqcloud.com/2026/01/14/fa85547f-b9f9-4583-9ef6-ed837c9ee308.png", 
    "openapi_schema": "{\"description\":\"这是一个查询对应英文单词字典的工具\",\"server\":\"https://dict.youdao.com\",\"paths\":{\"/suggest\":{\"get\":{\"description\":\"根据传递的单词查询其字典信息\",\"operationId\":\"YoudaoSuggest_1\",\"parameters\":[{\"name\":\"q\",\"in\":\"query\",\"description\":\"要检索查询的单词，例如love/computer\",\"required\":true,\"type\":\"str\"},{\"name\":\"doctype\",\"in\":\"query\",\"description\":\"返回的数据类型，支持json和xml两种格式，默认情况下json数据\",\"required\":false,\"type\":\"str\"}]}}}}",
    "headers":[{"key":"Authorization","value":"12345678"}]
}   


# 19 分离Service服务中的基础增删改查
  19.1 在service包下新增文件BaseService.py,定义BaseService类 
       封装基础的增删改查代码
       
  19.2 修改 api_tool_service.py 中 ApiToolService类代码,继承自BaseService类
       使用封装的增删改查函数替代原本的增删改查代码
  
  19.3 重新测试ApiTooHandler下的视图方法
   
  

# 20 单元测试中实现数据回滚的技巧与实现
  20.1 在测试包中增加对自定义API工具数据增删改查的测试代码,且能够实现在完成多组测试之后,
       将数据还原到测试之前的初始状态.
  
  20.2 修改测试包中的conftest.py,重新配置测试客户端环境

  20.3 在测试包中的test_api_tool_handle.py中 新增 增删改查 的测试方法
  
# 21 API工具管理器实现动态创建工具 
  21.1 实现:由数据库中存储的工具配置信息,生成langchain下的BaseTool工具对象.
       新建包core/tools/api_tools/providers.
       包下新建文件api_provider_manager.py.
       新建类:ApiProviderManager(BaseModel),便捷导出.

  21.2 ApiProviderManager类中实现方法:
       get_tool(self, tool_entity: ToolEntity) -> BaseTool,
       根据传递的ToolEntity配置返回自定义API工具(langchain中的BaseTool).

  21.3 新增core/tools/api_tools/entities/tool_entity.py,
       编写类ToolEntity(API工具实体信息类),包含创建BaseTool工具所需的配置信息,
       作为模板生成BaseTool工具对象,便捷导出.
       
  21.4 ApiProviderManager.get_tool中使用StructuredTool.from_function,
       依据ToolEntity创建BaseTool

  21.5 ApiProviderManager类中实现辅助方法:
         _create_model_from_parameters(list[dict])生成工具的参数规范
       ApiProviderManager类中实现辅助方法:
         _create_tool_func_from_tool_entity(ToolEntity)生成工具的执行函数
      
  21.6 在api_tool_service.py中导入ApiProviderManager类,在ApiToolService
       类中将其依赖注入为属性,
       ApiToolService类中增加方法:api_tool_invoke,测试该Manager类生成工具,
       并调用该工具.
       AppHandler.ping测试调用 api_tool_invoke方法 查看工具调用结果.
       GET : http://127.0.0.1:5000/ping
         
# 23 前端页面
  导入前端代码(step4_5) 启动前端服务 测试与后端接口联动