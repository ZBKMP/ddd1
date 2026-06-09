# pip install injector==0.22.0 # 轻量级依赖注入框架

# 使用该装饰器可以省略类的初始化函数
from dataclasses import dataclass
# 通过装饰器@inject和Injector实例,轻松实现依赖注入,不需要显式创建依赖对象
from injector import Injector, inject


@dataclass # 根据你定义的属性 自动生成init函数 非类属性而是实例属性
class A:
    name:str = 'hello'
    # def __init__(self):
    #     self.name = 'hello'
# a1 = A(name='hello')
# a2 = A(name='world')
# print(a1.name)
# print(a2.name)

@inject #依赖注入 : 在使用Injector创建该类对象时,会自动填入该类需要的其他对象属性
@dataclass
class B:
    a:A
    # def __init__(self,a:A):
    #     self.a = a

# 传统方式: B中有一个A类作为属性 则必须传入一个A类对象才可创建出B类对象
# a = A()
# b = B(a=a)

# 使用 Injector + inject 创建B类对象
injector = Injector()
b = injector.get(B)
print(b.a.name)

