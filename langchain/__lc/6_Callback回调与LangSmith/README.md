# 1.利用回调功能调试链应用-让过程更透明
  CallBack功能介绍:
  CallBack是langchain提供的回调机制,允许在LLM应用程序的各个阶段使用hook函数(钩子),
  如果把应用程序看成一个个的处理逻辑,从开始到结束,hook函数就是在事件传送到终点前截获并监控事件的传输.
  CallBack对于记录日志、监控、流式传输等任务非常有用,是记录整个流程的运行情况的一个组件,
  在每个关键的节点记录相应的信息,以便跟踪整个应用的运行情况.
  CallBack模块具体实现包含两大功能:callbackHandler 和 CallbackManager

  实现自定义回调:
  
# 2.LangSmith
  https://smith.langchain.com/
  注册 登录 首次进入会有一个默认应用
  选择创建新应用,选择OpenAI Agent模式 获取API_KEY 
  按提示进行.env配置 在配置中针对当前API_KEY设置自定义项目名称
  LANGSMITH_TRACING=true
  LANGSMITH_ENDPOINT=https://api.smith.langchain.com
  LANGSMITH_API_KEY=your-langsmith-api-key
  LANGSMITH_PROJECT=llmops_project


  运行LLM访问后,可在project界面看到项目运行信息
  点击RUN COUNT 查看每条信息详情
  点击详情还可以将此次交互添加到数据库中,可在数据库界面查看
  
  langsmith提供playground 进行LLM调试 会记录到playground项目中

  prompt界面 创建prompt 并在playground中测试
  prompt_hub仓库: https://smith.langchain.com/hub


  使用langchain可以直接使用langsmith 不需要进行额外的模块安装以及配置
  如果不使用langchain框架也想使用langsmith,参考官方文档:
  https://docs.langchain.com/langsmith/observability-quickstart