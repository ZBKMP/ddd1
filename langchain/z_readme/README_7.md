# 1 授权认证与API鉴权功能解析
UI设计稿 https://js.design/f/I_B1Is?p=H6nW02nJkv&mode=design

# 2 LLMOPS授权认证模块API文档分析  (授权认证模块 账号设置模块)

# 3 账号与授权认证数据库表与ORM实现 
  3.1 internal/model下新建文件account.py,新建模型类Account,AccountOAuth,
      便捷导出,internal/server/http.py中导入模型类,进行数据迁移操作
  
# 4 集成JWT与哈希加密完成前置工作
  4.1 模块安装 pip install PyJWT
      env配置文件中增加JWT秘钥配置 JWT_SECRET_KEY=vG8q3wN5pX9jT7sL2mK4rF6cB1zD0hY3P.
   
  4.2 internal/service下新建文件jwt_service.py,新增业务服务类JwtService,便捷导出,
      类中包含 令牌生成 以及 令牌解析 两个业务方法.
  
  4.3 pkg下新建包password,包下新建文件password.py,
      文件中定义对密码进行格式校验的正则表达式password_pattern,
      文件中定义方法validate_password 校验传入的密码是否符合相应的匹配规则
      文件中定义方法hash_password 将传入的密码+盐值进行哈希加密
      文件中定义方法compare_password 根据传递的密码+盐值校验比对是否一致
      所有内容便捷导出.
  
# 5 Flask-Login扩展的集成与中间件编写 实现将登录判断功能与Flask框架深度绑定 
   5.1 模块安装 pip install flask-login,将internal/model/account.py中的Account实体类
       继承于UserMixin.
   
   5.2 internal/extension下新建文件login_extension.py,创建flask_login.LoginManager对象,
       便捷导出,并在app.http.module.ExtensionModule中绑定.

   5.3 修改internal/server/http.py中Http类,初始化方法增加参数login_manager:LoginManager,
       并实现该参数与Flask对象的关联.
       修改app/http/app.py代码,在创建Flask对象时增加参数login_manager:LoginManager的传递.
       启动app,测试Flask对象是否能创建成功.

   5.4 internal/middleware下新建文件middleware.py,
       创建类MiddleWare,应用中间件类,
       定义方法 : request_loader(self, request: Request) -> Optional[Account]
       表示登录管理器的请求加载器,方法先返回None.

   5.5 internal/service下新建account_service.py文件,新建AccountService业务服务类,便捷导出.
       类中新增方法get_account,通过账户ID数据库中查询账户信息. 
   
   5.6 flask.LoginManager 与 MiddleWare.request_loader方法绑定后的登录逻辑分析:
       Flask应用在识别到某个handler处理器需要登录验证时, 会先调用中间件中的request_loader方法,
       通过该方法返回当前登录的账号信息,所以request_loader可以返回Account类对象或抛出异常.

   5.7 MiddleWare.request_loader方法实现过程：
       先为internal.router.router.Router类中的蓝图llmops实现登录判断逻辑，
       过程中通过分割请求头中的Authorization,得到jwt令牌,使用JwtService解析令牌,
       解析令牌后，得到其中sub字段(账号ID),再通过AccountService加载账户信息,
       过程中若没有找到请求头Authorization,或者格式不正确(必须符合Bearer access_token),
       则抛出未授权异常.
       
   5.8 修改internal/server/http.py中Http类,初始化方法增加参数middleware:Middleware,
       并实现该参数与LoginManager对象的关联.
       修改app/http/app.py代码,在创建Flask对象时增加参数middleware:Middleware的传递.
       启动app,测试FLask对象是否能创建成功.

   5.9 测试登录验证效果,修改internal/handler/dataset_handler.py中DatasetHandler的视图等方法,
       例如在get_datasets_with_page方法上增加装饰器:@login_required,再次访问该handler时会进行
       登录验证,未登录状态下禁止访问

# 6 对接GitHub OAuth实现github快捷登录
   6.0 GITHUB登录流程分析:
    GITHUB登录-->后端向GITHUB发起第三方登录请求-->GITHUB回复code至前端项目-->前端会将code传递到后端-->
    后端接收到code后再向GITHUB发起请求-->GITHUB响应结果中会包含TOKEN-->后端接收到TOKEN后再向GITHUB发起请求获得用户信息-->
    根据用户信息得到或创建账号信息,完成登录.

   6.1 GitHub配置OAuth,支持作为第三方登录平台
       * github账号:QQ邮箱登录,需要安装手机应用(1Password,Authy,MicrosoftAuthenticator)
         做二次验证
       * github登陆后-->个人信息-->settings-->developer settings-->OAuth Apps-->
         New OAuth Apps--完成APP注册-->进入APP界面-->Generate a new client secret-->
         Homepage URL : http://localhost:5173
         Authorization callback URL:http://localhost:5173/auth/authorize/github
         生成:
           ClientID : your-github-client-id 
           Client secrets : 699c8c0a1290c7c8cd5c7da3f1fa415740d81a9a 
       * 将github oauth ClientID及ClientSecrets配置在env文件中
         以及在env中增加GITHUB_REDIRECT_URI配置

   6.2 pkg下新建包oauth,包含所有第三方登录验证的用户信息类文件,pkg/oauth下新建文件oauth.py,
       定义类OAuthUserInfo,表示OAuth用户基础信息，只记录id/name/email,便捷导出
       定义抽象类OAuth,表示第三方OAuth授权认证基础类,便捷导出.
   
   6.3 pkg/oauth下新建文件github_oauth.py,定义类OAuth的子类:GithubOAuth(OAuth),
       表示Github的第三方授权认证类,便捷导出.
       
# 7 OAuth模块API接口设计与实现 项目API文档 6.1  6.2
   7.1 获取指定第三方授权服务的重定向地址接口:用于获取指定第三方授权服务的重定向地址,
       如github,google等.
     * internal/handler下新建文件oauth_handler.py,新建类OAuthHandler,
       作为第三方授权认证处理Handler,便捷导出.
     * internal/service下新建文件oauth_service.py,新建类OAuthService,
       作为第三方授权认证业务服务类,便捷导出.
     * OAuthHandler增加视图方法 provider,根据传递的提供商名字获取授权认证重定向地址,
       OAuthHandler.provider方法内调用OAuthService.get_oauth_by_provider_name
       方法完整具体业务流程.
     * 为OAuthHandler.provider视图函数绑定路由，POSTMAN测试.
     GET : http://127.0.0.1:5000/oauth/:provider_name


响应结果示例:
{
  "code": "success",
  "data": {
    "redirect_url": "https://github.com/login/oauth/authorize?client_id=your-github-client-id&redirect_uri=http%3A%2F%2Flocalhost%3A5173%2Fauth%2Fauthorize%2Fgithub&scope=user%3Aemail"
  },
  "message": ""
}
       其中的URL地址为GITHUB对应的授权登录URL,(必须先登录GITHUB)进入后点击授权Authorize,则会跳转到
       GITHUB_REDIRECT_URI指定的前端项目地址,结果示例:
       http://localhost:5173/auth/authorize/github?code=0efe2c3c868b43b23010
       从中可以获取服务提供商名称github,并携带了code验证码,后续会再传递给后端接口,
       后端会再以该code向github发起新请求以获取当前github登录用户的TOKEN令牌,
       从而再获取该用户信息及邮箱地址.

  7.2 指定第三方授权服务的授权地址接口:
      用于第三方授权服务确认后的回调地址,GITHUB授权登录后,会回调LLMOPS平台,并携带相关的code标识,
      以在后端继续向GITHUB获取对应用户的TOKEN授权凭证.
    * OAuthHandler内新增视图方法authorize,根据传递的提供商名字+code获取第三方授权信息
    * internal/schema下新建文件oauth_schema.py,为视图方法authorize新增请求验证类:AuthorizeReq,
      响应结果封装类:AuthorizeResp,便捷导出
    * OAuthService类中新增业务方法oauth_login,实现第三方OAuth授权认证登录,返回授权凭证以及过期时间.
      过程中调用：
      AccountService.get_account_oauth_by_provider_name_and_openid,
      AccountService.get_account_by_email,
      AccountService.create_account,
      AccountService.get_account,  
      完成OAuth授权账号的相关数据库操作.
    * OAuthHandler.authorize视图方法调用业务方法oauth_login,完成第三方OAuth授权登录过程.
      为视图方法OAuthHandler.authorize设置路由,POSTMan测试,code参数使用上一个视图函数
      OAuthHandler.provider测试响应结果中的code数据.
    * 首次测试后可看到在account_oauth表中增加了一行授权信息,授权给github账号的登录权限
    * 测试成功后复制token值,再重新测试访问视图方法get_datasets_with_page,
      POSTMAN中选择Authorization-->AuthType:Bearer Token-->填入Token值
      点击发送即可正常访问,填入了Token值即处于已登录状态.
    POST : http://127.0.0.1:5000/oauth/authorize/:provider_name
    {
    "code":"5c71c52eb0d29da87340"
    }

# 8 账号设置模块API接口的设计与实现 项目API文档 - 7.1 7.2 7.3 7.4
  8.1 获取当前登录账号信息
     * internal/handler下新增文件account_handler.py,定义视图类AccountHandler,便捷导出
     * 视图类AccountHandler中新增方法get_current_user,用于获取当前登录账号信息。
       该视图方法增加装饰器@login_required,访问时请求头Authorization中必须包含token
       表示当前登录用户信息
     * internal/schema下新增文件account_schema.py文件,为AccountHandler.get_current_user
       视图方法编写响应结果封装类GetCurrentUserResp.
     * 视图方法中使用flask_login模块中的current_user获取用户信息,为视图方法配置路由 
       POSTMAN访问,必须传递Authorization请求头。
       GET : http://127.0.0.1:5000/account
        

  8.2 更新当前登录账号密码
     * 视图类AccountHandler中新增方法update_password,用于更新当前登录账号密码。
       该视图方法增加装饰器@login_required,访问时请求头Authorization中必须包含token
       表示当前登录用户信息
     * 修改internal/schema/account_schema.py文件,为AccountHandler.update_password
       视图方法编写请求参数验证类UpdatePasswordReq.
     * 修改internal/service/account_service.py文件下的AccountService类,增加业务服务方法
       update_password与业务方法update_account.
     * AccountHandler.update_password视图方法中使用flask_login模块中的current_user
       获取用户信息,连同请求中传递的新密码作为参数调用业务方法AccountService.update_password,
       完成密码修改业务流程
     * 为视图方法配置路由,POSTMAN访问,必须传递Authorization请求头。newpassword123
     POST : http://127.0.0.1:5000/account/password
     {
      "password":"newpassword123"
     }

  
  8.3 更新当前登录账号名称 (独立完成)
    * 视图类AccountHandler中新增方法update_name,用于更新当前登录账号名称。
       该视图方法增加装饰器@login_required,访问时请求头Authorization中必须包含token表示当前登录用户信息
    * 修改internal/schema/account_schema.py文件,为AccountHandler.update_name
       视图方法编写请求参数验证类UpdateNameReq.
    * AccountHandler.update_name视图方法中使用flask_login模块中的current_user获取用户信息,
       连同请求中传递的新name作为参数调用业务方法AccountService.update_account,完成name修改业务流程
    * 为视图方法配置路由,POSTMAN访问,必须传递Authorization请求头
     POST : http://127.0.0.1:5000/account/name
     {
    "name":"newuser123"
     }

  8.4 更新当前登录账号头像 (独立完成)
    * 视图类AccountHandler中新增方法update_avatar,用于更新当前登录账号头像。
       该视图方法增加装饰器@login_required,访问时请求头Authorization中必须包含token
       表示当前登录用户信息  
    * 修改internal/schema/account_schema.py文件,为AccountHandler.update_avatar
       视图方法编写请求参数验证类UpdateAvatarReq.
    * AccountHandler.update_avatar视图方法中使用flask_login模块中的current_user获取用户信息,
       连同请求中传递的新头像URL作为参数调用业务方法AccountService.update_account,
       完成头像修改业务流程
    * 为视图方法配置路由,POSTMAN访问,必须传递Authorization请求头
    POST : http://127.0.0.1:5000/account/avatar
    {
    "avatar":"https://llmops-1328730224.cos.ap-guangzhou.myqcloud.com/2026/01/30/9959c670-83e7-4cf9-86eb-c30b144382a4.png"
    }


# 9 账号密码登录与退出登录接口设计与实现 项目API文档 - 6.3 6.4
  9.1 使用账号密码登录LLMOPS平台
     * 模块安装 pip install email_validator 用于在请求schema类中验证电子邮件格式
     * internal/handler下新增文件auth_handler.py,定义视图类AuthHandler,便捷导出.
     * 视图类AccountHandler中新增方法password_login,用于实现账号密码登录。
     * internal/schema下新增文件auth_schema.py文件,为AccountHandler.password_login
       视图方法编写请求参数验证类PasswordLoginReq,响应结果封装类PasswordLoginResp,便捷导出
     * 修改internal/service/account_service.py文件下的AccountService类,
       增加业务服务方法password_login,根据传递的密码+邮箱登录特定的账号,
       AuthHandler.password_login调用该业务方法实现登录流程.
     * 为视图方法配置路由,POSTMAN访问    
     POST : http://127.0.0.1:5000/auth/password-login
     {
    "email":"810165727@qq.com",
    "password":"newpassword123"
     }

  9.2 退出当前登录的账号信息
     * 视图类AuthHandler中新增方法logout,退出登录，用于提示前端清除授权凭证。
       方法中可调用flask_login模块中的logout_user()方法实现退出登录流程.
       该视图方法增加装饰器@login_required,访问时请求头Authorization中必须包含token表示当前登录用户信息
     * 为视图方法配置路由,POSTMAN访问 
     POST : http://127.0.0.1:5000/auth/logout

 


# 10 项目服务历史Todo事项完善与优化
  10.1 打开pycharm界面左侧TODO菜单,观察之前在业务流程中未处理的账号ToDo任务

  10.2 处理步骤：
     * ApiToolHandler 每个视图函数增加@login_required装饰器
     * ApiToolService 带有todo标识的业务方法,内部去掉虚拟的账号ID,方法增加参数account:Account,账号ID从参数中获取.
                      调用该业务方法的视图方法中,增加Account对象传入,数据来源由flask_login模块的current_user方法获取
     * 修改api_tool_provider表与api_tool表数据,以及其他包含account_id的数据表,改为当前account表内正确的账户ID
     * postman 测试路由 '/api-tools' 测试在有无token的环境下的访问结果
     
     * 在修改其他服务 以及 handler代码 由postman测试 , 
       如果需要使用测试模块中的单元测试,在client测试环境中也需要增加access_token参数
  
# 11 更新前端项目代码 包含用户授权登录模块页面 完成登录之后 会在浏览器的localstorage保存Token令牌
     知识库下文档详情(片段信息及相关操作)的页面内容,也在本次更新之后实现

     将更新后的前端代码覆盖 内部包含对登录状态的检查
     http://localhost:5173/auth/login

     https://brtc-ai.alltman.com/auth/login