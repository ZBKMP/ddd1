#继承 子类继承父类 则子类自动拥有父类中定义的属性/方法 实现代码复用
# 1 继承的基本概念
#学生Student id name sex age score  / show_info study
#Teacher id name sex age subject  / show_info Teacher

class Person(object):
   def __init__(self, name, age,sex,id):
    print('Person 的init方法')
    self.id = id
    self.name = name
    self.age = age
    self.sex = sex
   def show_info(self):
       return f'id:{self.id} name:{self.name} age:{self.age} sex:{self.sex}'

#子类继承于父类 会自动拥有父类中定义的成员
class Student(Person):
    # 子类的init方法 需要调用父类的初始化方法
    def __init__(self, name, age,sex,id,score):
        #name, age,sex,id向父类的init方法传递
        super().__init__(name, age,sex,id)
        self.score = score #score属性是子类自己定义

    def study(self):
        print(f'student study score:{self.score}')

student = Student('ZB',22,'man',0,88)
print(student.show_info())
student.study()

print('*'*100)
#继承是可以延续的 子类可以在继承子类
#本科学生:id name age sex score major/show_info study
class benke(Student):
    def __init__(self,id,name,age,sex,score,major):
        print('本科的init方法')
        super().__init__(id,name,age,sex,score,)
        self.major = major
    def ex(self):
        print(f'benke ex major:{self.major}')
#子类会拥有其上所有的父类的成员
benke = benke(1,'ZB',18,'man',88.5,'tumu')
print(benke.show_info())
benke.study()
benke.ex()

#所有类最终都继承于 object 类
print('*'*100)

# 单继承/多继承
#单继承:一个类只能由一个父类,一个父类可以有N个子类-->树型
#多继承:一个类可以继承于多个父类,一个父类可以有n个子类-->网状

#__mro__ 查看该类的继承顺序
#isinstance 操作符 判断对象是否某种类型bool
print(isinstance(benke,Student))

#多态  代码相同但运行结果不同
#方法重写Override:父类于子类都有相同功能,但子类于父类，子类于其他子类在实现功能的过程不一样
class Animal:
    def eat(self,food:str):
        print(f'Animal eat {food}')

class Dog(Animal):
    def eat(self,food:str):
        print(f'Dog eat {food}')

class Cat(Animal):
    def eat(self,food:str):
        print(f'Cat eat {food}')

a = Animal()
a.eat('food')

a = Dog()
a.eat('🍗')

a = Cat()
a.eat('🐟')

print('*'*100)

#所有类最终都继承object
class Human(object):
    def __init__(self,name,sex,age):
        self.name = name
        self.sex =sex
        self.age = age
        #重写__str__ 以实现输出对象时 按照自定义的逻辑生成字符串
    def __str__(self):
        return f'name:{self.name} sex:{self.sex} age:{self.age}'
           #重写__eq__ 实现两个对象是否相等:同类型 且属性值相同就判断相同
    def __eq__(self,other):
         #如果other为空 或者不是Human类型 直接判断为false
         if other is None or not isinstance(other, Human):
            return False
         return self.name==other.name and self.sex==other.sex and self.age==other.age


human = Human('ZZ','man',23)
print(Human)
other = Human('ZZ','man',23)
print(other == human ) #受对象中__eq__ 方法的影响
print(other is human ) #比较的是地址
print('*'*100)


# 定义职员 Employee类 (属性：id,name,sex,salary) 方法:_show_info_
#创建列表,包含多个对象，统计年龄 工资的总和(自定义)
#按年龄高低给列表排序(sorted lambda)
#筛选所有男性职员新列表(filter)
#提取所有员工工资信息组成新列表(map)
#提取出所有员工的工资信息
class Employee:
    def __init__(self,id:int,name:str,sex:str,age:int,salary:float):
        self.id = id
        self.name = name
        self.sex = sex
        self.age = age
        self.salary = salary

    def show_info(self):
        return f'id：{self.id} name：{self.name} sex：{self.sex} age：{self.age} salary：{self.salary} '

emp_list=[
Employee(0,'ZB','man',20,10000),
Employee(1,'ZD','man',22,12000),
Employee(2,'ZX','woman',22,9000)
]
age_sum = sum(emp.age for emp in emp_list)#年龄总和
print(age_sum)
salary_sum =sum(emp.salary for emp in emp_list)#工资总和
print(salary_sum)
#筛选出所有男性职员
man_emp_list = list(filter(lambda x:x.sex=='man',emp_list))
for x in man_emp_list:
  print(x.show_info())
