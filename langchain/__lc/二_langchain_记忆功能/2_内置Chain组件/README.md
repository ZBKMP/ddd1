# 1.langchain 内置chain组件的使用与解读
 Chain简介:
 Chain 通常用来描述一系列的操作或函数,这些操作或函数按照特定的顺序依次执行,
 前一个操作的输出会作为后一个操作的输入.这种模式也被称为管道(Pipeline)或链式调用(Chain Calling).
 LangChain中也有 Chain 的概念,用于在复杂场景下将LLM组件、提示词模板、向量存储、记忆、输出解析器
 等多个组件串联起来一起使用,在 LCEL 表达式出现之前,LangChain 就为Chain 设计了相应的接口,
 并且为不同场景设计封装了大量 Chain 组件. 
 在 LangChain 中存在两种类型的链:
   1. [推荐]使用 LCEL 构建的链(顺序可执行链)
   2. [遗产]通过 Chain类子类 构建的链,这些链不使用 LCEL,而是独立的类.
 0.1.0 版本之后Chain基类也继承了RunnableSerializable,同样也是一个可运行组件,
 在使用上了 LCEL 表达式构建的链一模一样,屏蔽了使用的差异.

 利用Chain类构件链应用:
 
 官网介绍内置的Chain组件:
 https://python.langchain.com/v0.1/docs/modules/chains/
 
 内置的chain:
   LECL Chain : LCEL文档填充链  
   遗产 Chain : 对话链

# 2 RunnableWithMessageHistory简化代码
   RunnableWithMessageHistory 使用示例:
   在前面的示例中,我们将历史消息显示地传递给链,在链外单独处理历史消息的记忆存储.
   LangChain还提供RunnableWithMessageHistory函数/包裹器,能让链自动处理这个过程(填充+存储).
   类构造函数接收的参数如下：
   a.runnable:需要包装的链或者可运行的组件。
   b.get_session_history:一个工厂函数,它返回给定会话ID的消息历史记录.
     链就可以通过加载不同对话的不同消息,来同时处理多个用户.
   c.input_messages_key:人类的输入键,指定输入的哪个部分应该在聊天历史中被跟踪和存储.
   d.output_messages_key:AI的输出键,指定要将哪个输出存储为历史记录.
   e.history_messages_key:历史消息键,用于指定以前的消息使用特定的变量在模板中格式化.
   使用RunnableWithMessageHistory包装链后,就可以像正常链一样调用了,还可以增加一
   个运行时配置来指定传递给工厂函数的session_id,确认从哪里获取存储的历史消息.

   

   RunnableWithMessageHistory 运行流程:
  