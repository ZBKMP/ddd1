#自定义模块

PI = 3.14159

def func_add(a,b):
    return a+b
def func_sub(a,b):
    return a-b
def func_mul(a,b):
    return a*b
def func_div(a,b):
    return a/b

class MyClass(object):
    def say_hello(self):
        print("hello")

# 所有该py文件内要去执行的代码必须先经过判断
if __name__ == '__main__':
    print('execute code..........')
