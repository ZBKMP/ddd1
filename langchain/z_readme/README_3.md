# 1. API接口文档 
   1.1按照API接口文档需求 在app_handler.py的AppHandler类中增加debug方法，并配置对应路由

# 2. 实现带记忆功能与RAG检索功能的聊天机器人
   2.1在debug方法中实现带记忆功能的聊天机器人 ，并实现记忆持久化，存储于storage目录

   2.2在debug方法中实现带记忆功能的聊天机器人 基于Runnable封装记忆链 实现记忆自动管理

   2.3在debug方法中实现带RAG检索的聊天机器人
      在service下新增文件 vector_store_service.py 
      新增WeaviateVectorStoreService类,增加@inject装饰器
      类中包含属性client与vectorstore,初始化函数中创建出client与vectorstore
      在app_handler.py中的AppHandler类中增加属性weaviate_service
      利用该属性以及在2.2带记忆功能聊天机器人基础上实现带RAG检索的聊天机器人

---------------------------------------------------------------------------------------


# 3. 前端环境搭建
   3.1 安装 Node.js / npm, 会自动配置环境变量
       官网: https://nodejs.org/en
       控制台执行 node -v 查看当前nodejs版本
       控制台执行 npm  -v 查看当前npm版本
       可以通过node指令直接执行js代码或js文件
       
   3.2 设置镜像加速下载
       控制台执行 npm config list 查看当前npm配置信息
       腾讯云镜像地址: http://mirrors.cloud.tencent.com/npm/
       执行镜像地址设置:
          控制台执行: npm config set registry http://mirrors.cloud.tencent.com/npm/
       检查镜像设置结果: npm config get registry
   
   3.3 依赖管理工具 -- Yarn  https://yarnpkg.com
       安装 : npm install -g yarn 
       查看版本 : yarn -v
       查看配置 : yarn config list
       设置yarn镜像源 : yarn config set registry http://mirrors.cloud.tencent.com/npm/
       yarn常用指令: https://classic.yarnpkg.com/en/docs/usage 

   3.4 yarn下载依赖包测试
       初始化操作: 建立前端项目目录(llmops_ui),建立测试目录(node_demo),进入目录控制台执行: 
                 yarn init ( 所有输入均跳过 生成package.json管理包依赖)
       使用 yarn下载vue : 进入测试目录控制台执行:
                 yarn add vue (安装后查看package.json,而且生成了yarn.lock文件)
       使用 yarn安装下载好的模块:进入测试目录控制台执行:
                 yarn / yarn install (根据package.json与yarn.lock文件安装下载好的模块)


# 4.前端项目搭建
   4.1 框架选型: VUE(组合式)  https://cn.vuejs.org/
   
   4.2 创建VUE项目: 进入前端项目目录llmops_ui,控制台执行: yarn create vue
       创建项目名称: llmops_ui
       VUE选项选择 : TypeScript, Router（单页面应用开发）, Pinia（状态管理）,
                    Vitest（单元测试）, ESLint（错误预防）, Prettier（代码格式化）,
                    选择包含示例代码.
       项目初始化完成，可执行以下命令：
          cd llmops_ui
          yarn      # 安装所需的依赖
          yarn format
          yarn dev  # 启动开发服务器 http://localhost:5173/  
       在发布到生产环境时执行:
          npm方式指令:npm run build
          yarn方式指令:yarn build

       配置yarn的全局安装路径和缓存路径(目录要提前创建):
          yarn config set global-folder "D:\nodejs\env\nodejs\yarn_cache"
          yarn config set cache-folder "D:\nodejs\env\nodejs\yarn_global"
       为目录D:\nodejs\env\nodejs\yarn_global文件增加访问权限:
          右键点击 D:\nodejs\env\nodejs\yarn_global 文件夹
          属性 → 安全 → 编辑 → 当前用户 → 勾选"完全控制" → 应用   
       查看配置结果:yarn config list 

   4.3 项目目录分析
       根据项目需要 在生成的VUE项目中补齐需要的其他目录 (主要在src目录下)
       assets  components config hooks router service stores utils views
   
# 5.安装webStorm前端开发工具
   5.1 webstorm官网 :https://www.jetbrains.com/webstorm/
       使用webstorm打开之前使用nodejs+yarn创建的Vue项目
       使用之前的破解工具中的webstorm包进行破解
       修改项目中格式美化配置文件 .prettierrc.json 
       
       {
        "$schema": "https://json.schemastore.org/prettierrc",
        "semi": false,
        "tabWidth": 2,
        "singleQuote": true,
        "printWidth": 100,
        "trailingComma": "all"
       }  

   5.2 代码质量检查配置
       在settings-Languages&Frameworks-javascript-code quality tools-ELint中
       修改配置 Manual ESLint configuration: 
            ESLint Package : D:\python_workspace\codes\llmops_ui\llmops_ui\node_modules\eslint
            Configuration File :D:\python_workspace\codes\llmops_ui\llmops_ui\eslint.config.ts
            勾选 Run-eslint  apply  确认
       测试:在src/views 下建立Vue Component : index 会发现报错,不符合ESlint代码规范
  
   5.3 代码美化配置
       在settings-Languages&Frameworks-javascript-Prettier中
       修改配置 Manual Prettier configuration: 
       Prettier package:D:\python_workspace\codes\llmops_ui\llmops_ui\node_modules\prettier
       勾选 Run on Reformat Code Action 
       勾选 Run on save 
       apply 确认
       测试: 修改App.vue代码 修改代码格式 保存之后会自动规范代码格式
   
   5.4 其他配置 
      关闭插件 Full Line Code Completion
      在settings-Tool-Action and Save中,勾选Reformat code/Optimize imports
      在settings-Languages&Frameworks-TypeScript-Vue中 勾选Auto
   
   5.5 scripts指令脚本 
      项目根目录下的package.json文件中,scripts中包含可执行脚本
      "dev": "vite"  启动项目服务 ,Local:   http://localhost:5173/
      服务支持热启动 尝试修改App.vue或view目录下的两个vue组件可见页面会自动更新
   
# 6 ArcoDesign 与 TailwindCSS 简化UI界面开发
   6.1 安装ArcoDesignUI组件库
      官网:https://arco.design
      webstorm终端执行 : yarn add --dev @arco-design/web-vue
      package.json中可查看到安装好的arcoDesign版本
  
   6.2 在项目中导入 ArcoDesign
      修改src/main.ts,增加导入ArcoDesign代码
      测试 在src/views/AboutView.vue中尝试使用AcroDesign组件如:a-button
  
   6.3 TailwindCSS安装与使用
      官网: https://tailwindcss.com/
      webstorm终端执行:  建议安装v3版本
          安装: npm install -D tailwindcss@^3 postcss autoprefixer 
          配置文件生成: npx tailwindcss init -p 
          最终在项目根目录生成两个JS文件
      使用官方推荐的tailwind.config.js配置修改其代码：
          https://v3.tailwindcss.com/docs/guides/vite#vue
          该文件配置哪些文件中的css代码会被tailwind解析
      还需要在assets/styles/main.css中添加对TailwindCSS样式的导入：
          @tailwind base;
          @tailwind components;
          @tailwind utilities;
      再在在src/main.ts中导入src/assets/styles/main.css,
      因修改了根目录下的文件,还需重启服务.
      测试:修改根目录下的index页面 增加tailwindcss样式代码,观察变化
          修改src/views目录下的AboutView.vue 增加tailwindcss样式代码,观察变化 
      ChatGPT/Dify等网站设计就是使用了TailwindCSS

# 7 VueRouter
   7.1 概念 以及 默认代码中的路由实现过程
     在src/App.vue中 使用了RouterLinker 与 RouterView标签
     RouterLinker中的to属性 指向 src/router/index.ts中的路由配置,
     当前代码中包含两个路由配置,分别指向views目录下的两个Vue组件.
     当页面点击RouterLinker时则可以实现RouterView的内容切换,默认显示path='/'的vue组件
     因在src/main.ts中加载了路由配置,则使得上述路由操作生效.

   7.2 页面嵌套布局
     在src/views/下创建layouts目录，其中添加DefaultLayout/BlankLayout两个Vue组件.
     在src/views/下创建space/apps目录,其中添加 ListView Vue组件.
     在src/views/下创建auth目录,其中添加LoginView Vue组件.
     在src/router/index.ts中导入上述layouts目录所有Layouts布局文件,
     重写src/router/index.ts中的routes:[]配置内容,实现页面嵌套布局,
     在一个路由配置中增加children配置,内容会显示在父组件的router-view内.
     浏览器访问:
       http://localhost:5173/   会重定向到/home
       http://localhost:5173/space/apps
       http://localhost:5173/auth/login
       也可以在App.vue内增加对应路由的RouterLink连接
     观察页面内容变化
   
   7.3 路由守卫功能
     更新src/router/index.ts代码,为router增加路由守卫beforeEach.
     可以在访问任何路径时查看到控制台日志输出:
           to:object
           from:object   
     可见beforeEach会影响到所有路径访问.
   
   7.4 基于路由守卫功能 模拟登录检查 
     除了登录页面，所有业务功能的访问都需要先经过登录.
     在src/utils下新增auth.ts文件,编写方法模拟登录判断,
     在src/router/index.ts导入该登录判断方法,并在beforeEach中加入判断,
     再次访问所有路径会发现,除了登录页面都需要先进行登录.

# 8 pinia实现多页面共享数据状态
   8.1 pinia概念
     可看成是Vue的临时内存数据库。其中存储的数据可以被Vue的所有组件/页面访问,并同步更新
   
   8.2 安装及配置
     官网: https://pinia.vuejs.org/zh/
     安装 : yarn add pinia
     修改src/main.ts在项目中导入并加载pinia

   8.3 pinia三大要素
     1.数据：或者说是状态，是 Pinia 存储的数据结构。
     2.计算属性：或者说是 getter，是基于数据计算后得到的结果，只读属性。
     3.函数：或者说是动作，用于处理数据，涵盖数据的增、删、改等操作。
     
   8.4 pinia数据操作
     src/stores/counter.ts包含一个数据状态存储定义的示例
     在src/views下建立目录pages,增加 HomeView Vue组件
     修改src/router/index.ts,在DefaultLayout的children路由配置中增加子路由HomeView配置
     在HomeView组件中导入 src/stores/counter.ts内的useCounterStore数据存储类并创建对象
     在HomeView组件中增加对userCounterStore数据存储对象的使用.
     访问 http://localhost:5173/home 测试效果,点击按钮数字增加.但只是临时存储,页面刷新则还原.
     
   8.5 pinia数据共享操作
     修改src/views/space/apps/ListView.vue,导入useCounterStore数据存储类并创建对象,
     再在src/views/space/apps/ListView.vue中增加数值显示代码 和 返回/home的RouterLinker连接,
     同时在HomeView中也增加跳转至ListView.vue的RouterLinker连接
     访问 http://localhost:5173/home 测试效果 在HomeView对数据进行修改,在ListView可观察数据的变化

   8.6 pinia实现对复杂数据的存储与操作
     在src/stores 下新建account.ts,其中再定义一个新的数据存储 useAccountStore,并提供操作对象与方法
     修改src/views/pages/HomeView.vue,增加对useAccountStore的导入与操作
     访问 http://localhost:5173/home 测试效果

# 9.前端结构请求Fetch方法封装
   9.1 Fetch使用
     MDN fetch介绍：https://developer.mozilla.org/zh-CN/docs/Web/API/Fetch_API
     src/utils 下新建request.ts文件 封装fetch_AJAX使用逻辑,
     后端服务路径前缀,以及后端响应状态包含在src/config/index.ts内
   
   9.2 在前端项目使用fetch访问后端接口
     src/views/space/apps 下新建DetailView.vue,设计组件并通过按钮点击访问后台路径
     src/router/index.ts 中增加DetailView.vue的路由配置
     访问 http://localhost:5173/space/apps/35e5e56c-4961-4306-95cd-12ca08e13d14 测试效果 
     出现跨域问题 解决之后可以访问

# 10 前后端跨域问题解决
   10.1 两种解决方案:
     跨域资源共享  /  Node.js中间件代理
     
   10.2 基于第一种策略的解决方案(建议使用)
     安装: pip install flask-cors
     在后端代码 internal/server/http.py中 使用CORS包装Flask对象

   10.3 基于第二种策略的解决方案
     使用node.js增加中间代理服务器 

# 11 与后端接口对接
   src/views/space/apps下新增DetailView_2代码,完成页面设计,包含聊天窗口,以及聊天功能实现
      
   增加src/models目录,复制代码app.ts,base.ts,包含响应数据结构设计
   
   增加src/service目录,复制代码app.ts ,包含后端接口访问方法 debugApp
      
   访问 http://localhost:5173/space/apps/35e5e56c-4961-4306-95cd-12ca08e13d14 测试效果 