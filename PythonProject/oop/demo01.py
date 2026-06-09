#一切皆对象 属性,方法

#定义类 Person 属性 id name sex age 方法 show_info
class Person: #建议首字母大写
    def __init__(self,id, name, age,sex,salary:float,score:dict):
        print('Person init called')
        self.id = id
        self.name = name
        # 默认情况下 所有属性都是公有public(公开)的，在类的外部可以直接被访问/操作
        # 属性名 以_开头,认为该属性是受保护的protected(受保护）的，不建议在类的外部直接使用

        self._age = age
        self.sex = sex
        self.__salary = salary
        self.score = score
        #面向对象的编程: 封装 继承 多态

    #针对受保护的/私有属性 提供公有的访问方法
    def set_salary(self,salary):
        self.__salary = salary
    def get_salary(self):
        return self.__salary




    #定义方法 描述该类对象具有的功能
    #每个方法都要使用self作为第一个参数
    #类中方法可以使用类中定义的属性
    def show_info(self):
        self.study()
        self.work()
        return f"id:{self.id} name:{self.name} age:{self._age} sex:{self.sex} salary:{self.__salary} "
    def study(self):
        print('person study')
    def work(self):
        print('person work')

#2通过类创建对象 类名() 实际上就是调用的 类中定义的__init__方法
person = Person(1,'zb',18,'man',9999,{'语文':77})
#通过类创建的对象 会拥有 类中定义的属性以及方法
print(person.name)
person._age += 10
print(person._age)
print(person.id)
print(person.sex)
# print(person.get__salary) #类的外部不能操作类的内部的私有属性

print(person.score)
person_info = person.show_info()
print(person_info,type(person_info))

#使用公开的访问方法去操作私有/受保护的属性
person.set_salary(2000)
print(person.get_salary())
'''
self的含义是什么？
一个类可以创建多个对象,多个对象在内存中如何存储:
每个对象的属性 是分开存储的
多个同类对象之间 方法在内存中只有一份

方法如何知道是那个对象调用的自己？
方法中self就代表当前调用自己的对象是谁
每次对象中的方法时，都会提示传入self参数,x.方法(),x就会作为self传递到方法内
'''

person2 = Person(2,'zk',22,'woman',6666,{'化学':80})

print(person.show_info())
print(person2.show_info())
