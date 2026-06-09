# 装饰器 : 使用函数闭包对传入的函数进行包装 返回包装之后的结果
#         注意处理原函数的参数与返回值
from tokenize import endpats


# 定义装饰器 将原函数作为参数传入,返回装饰之后的函数结果
# 1 简单案例 无参 无返回
def decorator_func(func):
    def wrapper():
        print("new code before......")
        # 调用原函数
        func()
        print("new code after......")
    return wrapper
# 原函数 + 装饰器
@decorator_func
def func_1():
    print('func_1...........')
# 执行原函数 实际是被装饰之后的结果
func_1()

print("*"*50)

# 完整案例 有参有返回
def decorator_func_2(func):
    # *args **kwargs 可以确保能接受任何形式的参数传递
    def wrapper(*args, **kwargs):
        print("new code before......")
        print('*args:',args)
        print('**kwargs:',kwargs)
        return_value= func(*args, **kwargs)
        print("new code after......")
        # wrapper应该发返回原函数返回的结果
        return return_value
    return wrapper

# 再函数执行完毕之后 计算函数执行的耗时
import time
def decorator_func_3(func):
    def wrapper(*args, **kwargs):
        print("decorator code 3 before......")
        begin = time.time() # 当前时间距离1970-1-1 0：0：0 的秒数
        return_value= func(*args, **kwargs)
        end = time.time()
        times = end - begin
        print(f"decorator code 3 after......函数耗时:{times}")
        return return_value
    return wrapper

# 在一个函数上可以声明多个装饰器  栈(先进后出 后进先出)
@decorator_func_2
@decorator_func_3
def func_2(a,b):
    return a+b
# 调用原方法
result = func_2(1, b=2)
print(result)


# 小案例:方法传入参数以及包含返回值 ，添加装饰器展示所有参数并返回结果 调用原方法展示结果
# 小案例:展示执行耗时的装饰器，在方法调用前展示当前时间,调用后展示当前时间，再最后展示方法执行消耗的时间
# 可以在一个函数上 先后注册多个装饰器

'''
import datetime
import time
print(datetime.datetime.now())
print(time.time())
sum = 0
for i in range(100001):
    sum += i
print(sum)
print(datetime.datetime.now())
print(time.time())
'''