# 1.LCEL表达式与Runnable可运行协议
   多组件invoke嵌套的缺点:
   a.嵌套式写法让程序的维护性与可读性降低.
   b.无法得知每一步的具体结果与执行进度,难以排查错误.
   c.嵌套式写法没法集成大量的组件,组件越来越多时,代码会变成"一次性"代码
   如果能将嵌套的代码改为平级的调用,就可以屏蔽嵌套带来的大量缺陷.

   手写一个Chain优化代码:
   prompt,model,outputParse组件都有一个共同的调用方法invoke,
   并且每一个组件的输出都是下一个组件的输入,这样可以将所有组件组装成一个列表,
   循环依次调用每个组件的invoke,并将当前组件的输出作为下一个组件的输入.

   Runnable简介与LCEL(LangChain Expression Language)表达式:
   为了尽可能简化创建自定义链,LangChain官方实现了一个Runnable协议,
   它适用于LangChain中大部分组件,并实现了大量的标准接口,涵盖:
   stream , invoke, batch,astream,ainvoke,abatch,astream_log.
   Runnable还重写了__or__和__ror方法(Python中|操作符的运算逻辑),
   从而使的Runnable组件可以通过 | 或 pipe()的方式将多个组件拼接成链,
   在 | 的左右两边只要有一个是Runnable组件,最终都可以组成Runnable可执行链.
   官方说明:
   https://python.langchain.com/docs/how_to/#langchain-expression-language-lcel
   Runnable接口:
   https://reference.langchain.com/python/langchain_core/runnables/

