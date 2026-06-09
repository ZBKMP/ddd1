# 1.两个Runnable核心类的讲解与使用
   RunnableParallel并行运行工具:
   Langchain中支持运行多个Runnable的类,用于操作Runnable的输出,
   以匹配序列中下一个Runnable的输入,起到并行运行Runnable,并格式化输出结构的作用.
   
   RunnablePassthrough传递数据工具:
   这个类透传上游参数输入,可以获取上游的数据,并保持不变或新增额外的键.
   通常与RunnableParallel一起使用,将数据分配给映射中的新键.
   
   官方文档:
   https://python.langchain.com/docs/how_to/parallel/
   官方API:
   https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.base.RunnableParallel.html#langchain_core.runnables.base.RunnableParallel
   https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.passthrough.RunnablePassthrough.html
   https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.base.RunnableLambda.html
   RunnableLambda converts a python callable into a Runnable.