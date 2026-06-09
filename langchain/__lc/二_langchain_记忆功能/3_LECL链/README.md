# 1.Runnable组件动态添加默认调用参数  
   bind函数用途与使用技巧:  
   在一个 Runnable 可运行队列中中调用另一个Runnable，并传递一些常量参数，
   但是这些参数不是前一个 Runnable 的输出的一部分，也不是用户输入的一部分，
   而是某个 Runnable 组件的一部分参数. 可以考虑使用 Runnable.bind() 来传递这些默认参数
   例如:
      1. 创建了一个 ChatOpenAI 的 LLM 大语言模型，利用这个 LLM 来构建两条链；
      2. 第 1 条链的 temperature 为 -0.7，即生成的内容确定性更强；第 2 条链的 
         temperature 为1.2，生成的内容会更随机，更有创意；
      3. 在构建时，即可通过 LLM.bind(temperature=0.7) 和 LLM.bind(temperature=1.2) 
         来为 LLM 设置不同的默认调用参数;
   bind()函数用于修改 Runnable 底层的默认调用参数，并在调用时会自动传递该参数，无需手动传
   递，像原始链一样正常调用即可。所以如果在构建 Runnable 链应用时就知道对应的参数，可以使用
   bind 函数来绑定参数（事先指定）

   bind函数使用方式:
   1.动态添加默认调用参数:
   在构建链应用时，初始化一个通用的 LLM 大语言模型，在构建链应用时才绑定上对应的停止词，可
   以让 LLM 在更多链上被使用，灵活性更强，而无需实例化多个 LLM

   2.解决多参RunnableLambda函数传参
   在 LangChain 中，如果要将一个函数变成 Runnable 组件，可以通过 RunnableLambda 函数进行包
   装。但是封装后，所有的 Runnable 组件的 invoke 函数，调用时，只能传递一个参数（类型不限制），
   如果原本的函数支持多个参数，并且是必填参数，就会出现报错


   bind函数运行流程解析:
   bind() 函数是在构建应用的时候添加上对应的默认调用参数，而在Runnable.bind() 函数的底层，
   本质上是往 Runnable 的 kwargs 属性添加对应的字段，并生成一个新的 Runnable，
   当 Runnable 组件执行调用时（invoke、ainvoke、stream、astream、batch、abatch等），
   会自动将 kwargs 字段里的所有参数合并并覆盖默认调用参数,从而完成动态添加默认调用参数的效果.
   
# 2.Runnable组件配置运行时链内部
   configurable_fields方法使用技巧:
   在构建链的时候配置对应的调用参数，也可能让链在执行调用的时候才去配置对应的
   运行时链内部（运行时修改链相应参数），包括运行时动态调整温度、停止词、传递自定义参数、
   甚至是运行时动态替换模型为另外一个.
   针对这类需求，在 LangChain 也提供了相应的解决方案：
     1. configurable_fields() ：和 bind() 方法接近，但是并不是在构建时传递对应的参数，而是在
        链运行时为链中的给定步骤指定参数，比 bind() 更灵活。
     2. configurable_alternatives() ：使用这个方法可以在链运行时，将链中的某一个部分替换成其
        他替换方案，例如：运行中更换提示模板、更换大语言模型等
   

   configurable_fields运行流程及解析:
   
# 3.Runnable组件动态替换运行时组件
  configurable_alternatives 方法与使用技巧:
  在 LLMOps 项目中，应用编排页面可以在调试的过程中替换大语言模型继续之前的对话进行调试，这就
  是需要运行时组件替换功能，例如在构建的链应用中，动态替换掉特定的模型、提示词等整个组件本
  身，而不是替换组件里的参数信息.
  在 LangChain 中，提供了一个叫 configurable_alternatives() 方法来实现这个功能，所有的
  Runnable 组件均支持这个函数.
  步骤：
    1. 为有可能替换的组件定义一个键，这样在链应用中就可以区分出来是哪一个组件；
    2. 接下来为当前的组件选项设置一个默认值，当没有传递任何配置信息时，使用的就是默认值，组件
       不会发生替换；
    3. 接下来创建所有替换组件的实例，并为备选方案添加上对应的 key 值，以便配置信息知道值和对应
       组件的关系；
    4. 调用链，并传递配置信息，执行对应的动态替换运行组件。


  configurable_alternatives 运行流程与解析:
   
# 4.Runnable组件重试与回退机制降低程序错误率
  runnable重试机制:
  在 LangChain 中，针对 Runnable 抛出的异常提供了重试机制—— with_retry() ，
  当 Runnable 组件出现异常时，支持针对特定的异常或所有异常，重试特定的次数，
  并且配置每次重试时间的时间进行指数增加.
  with_retry 函数的参数如下：
    1. retry_if_exception_type ：需要重试的异常，默认为所有异常，类型为元组。
    2. wait_exponential_jitter ：是否在重试之间添加抖动，默认为 True，即每次重试时间指数增加
                                （并随机再增加 1 秒内的时间）。
    3. stop_after_attempt ：重试的次数，默认为 3，即 3 次重试后没有正常结果就暂停 
  with_retry() 函数的运行原理非常简单，通过构建一个新的 Runnable，在执行调用类的函数时，循
  环特定次数，直到组件能正常执行结束即暂停，并且在每次循环的过程中，休眠特定的时间.  


  runnable回退机制:
  在某些场合中，对于 Runnable 组件的出错，并不想执行重试方案，而是执行特定的备份/回退方案，
  例如 OpenAI 的 LLM 大模型出现异常时，自动切换到 文心一言 的模型上，
  在 LangChain 中也提供了对应的回退机制—— with_fallback.
  with_fallback 函数的参数：
     1. fallbacks ：原始组件运行失败，进行回退/替换的 Runnable 组件列表，必填参数。
     2. exceptions_to_handle ：需要回退的异常，默认为所有异常，类型为元组。
     3. exception_key ：错误异常键，当指定错误信息后，Runnable 组件产生的错误异常作为输入的一
             部分传递给回退组件，且以指定的键名存储，默认为 None，表示异常不会传递给回退处理程序.
             但该参数一般使用较少

# 5.Runnable 组件生命周期监听器与使用场景
   Runnable 生命周期监听器:
   在 LangChain 中，除了在链执行时传递 config+callbacks 来对链进行监听，Runnable 还提供了一个
   简约的方法 with_listeners 来监听 开始 、 结束 、 出错 这 3 个常见的生命周期，并且
   with_listeners 提供的方法比 CallbackHandler 更简洁，更统一。   
   with_listeners 配置的 on_start 、 on_end 、 on_error 函数格式参数一模一样，如下：
      1. run_obj: Run ：运行时对象，内部涵盖了运行id、运行名称、开始时间、结束时间、运行类型、
                        额外数据、错误信息、输入字典、输出字典、标签等内容。
      2. config: RunnableConfig ：执行时传递的 config 配置信息，类型为字典。
   
   with_listeners 运行流程与解析:
   with_listeners() 在底层会将传递的 on_start 、 on_end 、 on_error 合并到 
   config 配置选项汇中的 callbacks 中，本质上就是使用 CallbackHandler 
   的逻辑来实现对应的监听

# 6.基于Runnable封装记忆链实现记忆自动管理
   Runnable 封装记忆组件思路:
   在 Runnable 链应用中，可以考虑将 memory 通过 config+configurable 的形式传递给链，在链的执
   行函数（invoke、stream 等）中可以通过第 2 个参数获取到对应的 memory 实例，从而获取到记忆历
   史，并且为链添加 on_end 函数，即可获取到整个链的输入与输出，在 on_end 生命周期中将对话信息
   存储到记忆系统中.  

   Runnable 其他细节功能探索:
   LCEL 表达式与 Runnable 其他细节功能：
      1. 官方文档：
     https://python.langchain.com/v0.2/docs/how_to/lcel_cheatsheet/
      2. 翻译文档：
     http://imooc-langchain.shortvar.com/docs/how_to/lcel_cheatsheet/  
   
# 7.开源智能体MetaGpt记忆模块