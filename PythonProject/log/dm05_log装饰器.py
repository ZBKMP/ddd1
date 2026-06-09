# 使用装饰器对函数进行包装:通过日志模式输出函数的参数及返回值  以及异常信息
import logging
import traceback

# 先进行日志配置
logging.basicConfig(
    # 配置多个日志输出目标
    handlers=[
        # 输出到控制台
        logging.StreamHandler(),
        logging.FileHandler(filename='demo05_log_decorator.log', mode='a+', encoding='utf-8'),
    ],
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s -%(lineno)d - %(thread)d -%(filename)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
# 创建日志工具
logger = logging.getLogger("demo05_log_decorator")
# 定义装饰器
def log_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            # 日志输出原函数的参数
            logger.info(f'func_name:{func.__name__} *args: {args} , **kwargs: {kwargs}')
            # 原函数没有处理异常 而是再通过raise抛出异常 这样才能被装饰器捕获该异常
            return_value = func(*args, **kwargs)
            logger.info(f'func_name:{func.__name__} return_value: {return_value}')
            return return_value
        except Exception as e:
            logger.error(f'func_name:{func.__name__} error: {e}')
            #traceback.print_exc()
    return wrapper



# 使用装饰器包装原函数
@log_decorator
def func_div(num1, num2):
    try:
        result = num1 / num2
        return result
    except Exception as e:
        # 内部不处理 抛出异常 交给装饰器去处理
        raise e

# 直接调用原函数
result = func_div(100, 2)
print(result)
result = func_div(100,num2=0)
print(result)
