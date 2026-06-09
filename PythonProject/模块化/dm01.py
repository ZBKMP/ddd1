#导入模块 : 从其他PY文件中导入内容 在本程序中去使用
import my_mod
# 导入模块后 使用模块内的内容
print(my_mod.PI)
print(my_mod.func_add(10,20))
my_class = my_mod.MyClass()
my_class.say_hello()

#对模块名的简化
import my_mod as md
print(md.PI)
print(md.func_add(10,20))
my_class = md.MyClass()
my_class.say_hello()

#从模块内导入部分内容
#from my_mod import PI,MyClass
from my_mod import *
print(PI)
my_class = MyClass()
my_class.say_hello()
