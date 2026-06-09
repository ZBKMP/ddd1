#类属性及方法
class Myclass :
    #该属性是类属性，该类下所有对象公用这一个类属性,类属性可以直接通过类名去访问
    x  = 100
    # self.x 都是实例属性 实例就是对象
    def __init__(self,a,b):
        self.a = a
        self.b = b
    def func(self):
        pass
    # 使用classmethod装饰器 得到类方法
    # 使用类名直接调用 类方法中不能使用实例属性 可以使用类属性
    @classmethod
    def class_method(cls):
        print(f'class me....{cls.x}')
      #静态方法 使用类名直接访问 不能使用任何属性
    @staticmethod
    def static_method():
        print(f'static me....')
myc1 = Myclass(10,20)
print(myc1.a,myc1.b)
myc2 = Myclass(100,200)
print(myc2.a,myc2.b)
#访问类属性
Myclass.x = 300
print(myc1.x,myc2.x)
print(Myclass.x)

#__dict__类属性 能获取垓类下/对象所有的属性 组成一个字典
print(myc1.__dict__)#--对象看不到类属性
print(Myclass.__dict__)#--类看不到数值

#调用类方法
Myclass.class_method()
#调用静态方法
Myclass.static_method()


