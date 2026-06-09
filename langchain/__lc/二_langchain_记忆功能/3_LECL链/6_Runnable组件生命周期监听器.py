import time

from langchain_core.runnables import RunnableConfig
from langchain_core.runnables import RunnableLambda
from langchain_core.tracers import Run


# Runnable组件生命周期监听器 with_listener
# 让可运行组件或chain在某个生命周期节点(start end error) 触发相应的操作
#    Run:当前组件对象, RunnableConfig:整个链执行时的配置信息
def on_start(run_obj: Run, config: RunnableConfig) -> None:
    print("on_start")
    print("run_obj:", run_obj) # on_start 可以看到当前是哪一个运行组件 而且可以看到该组件的输入
    print("config:", config)

def on_end(run_obj: Run, config: RunnableConfig) -> None:
    print("on_end")
    print("run_obj:", run_obj) # on_end 可以看到当前是哪一个运行组件 而且可以看到该组件的输入以及输出

def on_error(run_obj: Run, config: RunnableConfig) -> None:
    print("on_error")
    print("run_obj:", run_obj) # on_error 可以看到当前是哪一个运行组件 而且可以看到该组件的输入以及错误信息


# 给可运行组件 配置监听器 执行到该组件时,会自动调用对应的 on_Xxx 方法
runnable_lambda_1 = RunnableLambda(lambda x: 4 / x).with_listeners(
    on_start=on_start,
    on_end=on_end,
    on_error=on_error,
)
runnable_lambda_2 = RunnableLambda(lambda x: time.sleep(x)).with_listeners(
    on_start=on_start,
    on_end=on_end,
    on_error=on_error,
)

chain = runnable_lambda_1 | runnable_lambda_2

chain.invoke(
    input=2,
    config=RunnableConfig(configurable={
        "name": "jack"
    })
)


print("finish........")