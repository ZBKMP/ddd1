# 1 LLMOps项目记忆与流式响应模块功能解析
  UI设计稿 https://js.design/f/I_B1Is?p=H6nW02nJkv&mode=design

# 2 流式事件与块响应接口设计流程拆解

# 3 应用调试接口该流式事件输出的初体验
  3.1 pkg/response/response.py中定义函数compact_generate_response
      用于统一合并处理块输出以及流式事件输出,便捷导出.

  3.2 修改handler/app_handler.py下AppHandlr类,新增方法debug2,
      结合队列,图,子线程,Flask流式输出,实现在Flask接口中实现大模型流式输出效果.
      将原本debug函数的路由配置,指向debug2函数,
      前端代码更新后(step6) 前端页面测试访问：
      POST : http://localhost:5173/space/apps/b71255e3-f922-4c00-bb3f-7b6cf25f9ac3
     {
      "query":"你好 你是谁?" 
     }

  

# 4 长记忆摘要服务实现与Prompt编写 （自行完成）
  4.1 internal/service下新建文件conversation_service.py,新建类ConversationService,便捷导出.
  
  4.2 类中定义类方法summary,根据传递的人类消息、AI消息还有原摘要信息总结生成一段新的摘要
      摘要生成模版定义在:internal.entity.conversation_entity.SUMMARIZER_TEMPLATE
  
  4.3 修改AppHandler中ping函数,测试summary摘要生成服务方法,POSTMAN测试多轮摘要生成结果
     GET : http://127.0.0.1:5000/ping

# 5 Agent会话名称自动生成设计与实现  模拟流行的AI对话网页,每次会话会自动生成名称 （自行完成）
  5.1 internal/service/conversation_service.py下,类ConversationService中新建方法
      generate_conversation_name,根据传递的query生成对应的会话名字，并且语言与用户的输入保持一致
      名称生成模版定义在:internal.entity.conversation_entity.CONVERSATION_NAME_TEMPLATE
      
  5.2 在生成会话名称时定义internal.entity.conversation_entity.ConversationInfo(BaseModel)实体 
      用于在生成会话名称时 规范LLM输出.

  5.3 修改AppHandler中ping函数,测试generate_conversation_name会话名称生成服务方法,
      POSTMAN测试会话名称生成结果.
      GET : http://127.0.0.1:5000/ping

# 6 Agent问答建议服务实现与Prompt编写 （自行完成）
  6.1 internal/service/conversation_service.py下,类ConversationService中新建方法
      generate_suggested_questions,根据根据传递的历史信息(摘要)生成最多不超过3个的建议问题
      建议问题生成模版定义在:
        internal.entity.conversation_entity.SUGGESTED_QUESTIONS_TEMPLATE 

  6.2 在生成建议问题时定义internal.entity.conversation_entity.SuggestedQuestions实体 
      用于在生成建议问题时 规范LLM输出结构.
 
  6.3 修改AppHandler中ping函数,测试generate_suggested_questions建议问题生成服务方法,
      POSTMAN测试建议问题生成结果.
      GET : http://127.0.0.1:5000/ping

# 7 记忆与应用调试模块API文档分析 项目API文档 - 应用模块  会话交流模块

# * 8 记忆与消息会话数据库表设计及ORM设计 基于关系型数据库的记忆存储
  8.1 internal/model下新建文件conversation.py,
      新增模型类:Conversation,Message,MessageAgentThought  
  
  8.2 internal/server/http.py中,
      增加模块导入internal.model.Conversation,Message,MessageAgentThought
      以便在进行数据迁移时能生成对应的数据表,
      执行数据迁移.
  
  8.3 internal.entity.conversation_entity中创建枚举类InvokeFrom,表示会话调用来源
      internal.entity.conversation_entity中创建枚举类MessageStatus,表示消息状态
  
# * 9 基于会话模型的记忆组件设计与实现
  9.1 internal/core下新建包memory(记忆组件),新建文件token_buffer_memory.py.
      文件中编写类TokenBufferMemory,实现(token长度限制的短期记忆组件),便捷导出.
       
       system_message : ,,,,,,,,,,,,,...{summary}....{context 4} 
       placeholder :  list[HM AI ....] 
       human: {query}
       placehoder : list[TM] 
      

      大语言模型的上下文长度=预设的提示词长度+
                          短期记忆长度+
                          长期记忆长度+
                          原始提问长度+
                          工具调用/知识库检索结果长度+
                          大模型剩余可以生成的长度 
      大模型输入输出的总token数是有限的,需要合理设计各个部分的长度组合.


  
# 10 基于工具调用的Agent图结构设计与实现     AI执行者
  10.1 internal/core下新建包agent/agents,新建文件base_agent.py.
       新建类BaseAgent,作为后续其他各类Agent组件的抽象父类,便捷导出.
  
  10.2 internal/core下新建包agent/entities,新建文件agent_entity.py.
       新建类AgentConfig,作为Agent组件的配置信息类
       新建类AgentState,作为自定义的图状态数据
  
  10.3 internal/core/agent/agents下新建文件function_call_agent.py,
       新建类FunctionCallAgent,作为工具调用智能体,便捷导出.
  
  10.4 internal/handler/app_handler.py中,修改AppHandler类,
       修改AppHandler中ping函数,调用FunctionCallAgent执行图应用输出结果,
       PostMan测试访问,LangSmith中观察运行流程.
       GET : http://127.0.0.1:5000/ping        

# 11 使用队列管理器优化Agent流式事件输出
  11.1 internal/core/agent/entities下新建queue_entity.py文件,
       新增 队列事件枚举类QueueEvent 定义多种事件类型
       新增 智能体队列事件模型AgentQueueEvent 存储事件产生的数据信息
  
  11.2 internal/core/agent/agents下新建agent_queue_manager.py文件
       新增 智能体队列管理类AgentQueueManager 智能体队列管理器,便捷导出.
   

# 12 为工具调用智能体添加队列管理器  实现流式输出
  12.1 修改internal/core/agent/agents/base_agent.py中的BaseAgent类
       将原代码改为调用AgentQueueManager 智能体队列管理器实现
  
  12.1 修改internal/core/agent/agents/function_call_agent.py中的FunctionCallAgent类
       将原代码改为调用AgentQueueManager 智能体队列管理器实现 
  
  12.3 修改handler/app_handler.py下AppHandlr类,新增方法debug3,
       测试基于AgentQueueManager实现流式输出,将原本debug函数的路由配置,指向debug3函数,
       POSTMAN测试访问.
      POST: http://127.0.0.1:5000/apps/:app_id/debug
      {
    "query":"截止到今天 马拉松世界纪录是多少?"
      }  


      修改前端代码(step6):views/space/apps/DetailView.vue:
      // todo: 3.暂时只处理agent_message事件，其他事件类型等接口开发完毕后添加
      if (event === 'agent_message') {
        let chunk_content = data?.answer
        messages.value[lastIndex].content = message.content + chunk_content
      }
      再测试: http://localhost:5173/space/apps/b71255e3-f922-4c00-bb3f-7b6cf25f9ac3
       
        
      前端页面更新后(step6) 测试知识库操作界面 增删改查知识库与文档