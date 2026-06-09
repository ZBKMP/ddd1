# 以list/dict 实现简单学生管理系统
# 学生信息字典 包含:名字nae 年龄age 成绩score
# 代码整体面向对象 类的模式来封装
# 数据要能保存到csv文件
# 1.程序启动时读取文件内容 加载到stu_list内
# 2.增删改查的操作 依然基于stu_list 去是实现
# 3. 在增删改查结束之后将当前stu_list再重写到文件内
import csv
import sys

#csv文件操作工具
class Csv:
    @classmethod
    def load_data_form_csv(cls):
        stu_list = []
        with open('data.csv', mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stu = Student(**row) #将字典拆包作为参数传递
                stu_list.append(stu)
        return stu_list

    #保存数据到csv文件，第一行包含列名
    @classmethod
    def save_data_to_csv(cls,stu_list:list):
        with open('data.csv', mode='w',newline='',encoding='utf-8') as f:
            writer = csv.DictWriter(f,fieldnames=['name','age','score'])
            writer.writeheader()
            # 此时stu_list中包含的都是Student对象,将stu_list改造成包含字典的列表
            stu_list =[stu.__dict__ for stu in stu_list]
            #写入到csv文件
            writer.writerows(stu_list)






# 定义全局变量 stu_list 用于存储所有的学生信息
stu_list = []


# 定义学生类
class Student:
    def __init__(self, name, age, score):
        self.name = name
        self.age = age
        self.score = score

    def __str__(self):
        return f'name: {self.name} age: {self.age} score: {self.score}'


# 学生管理工具类
class StuManager:
    # 属性 学生列表
    def __init__(self):
        #程序执行立即加载文件内的数据
        self.stu_list = Csv.load_data_form_csv()


    def add_xs(self):
        stu_name = input('请输入学生姓名:')
        stu_age = int(input('请输入学生年龄:'))
        stu_score = float(input('请输入学生成绩:'))
        # 将输入的三个数据 封装成对象
        student = Student(stu_name, stu_age, stu_score)
        # 对象加入到列表中
        self.stu_list.append(student)
        Csv.save_data_to_csv(self.stu_list)
        print('数据添加成功')

    def show_xs(self):
        # 展示所有学生信息
        print("所有学生信息如下:")
        for stu in self.stu_list:
            print(stu)

    def del_xs(self):
        # 前提在列表中 name是唯一的 以name作为搜索条件 找到对应数据 从列表中删除
        stu_name = input('输入要删除学生的姓名')
        stu_pbj = None
        # 以name为条件 搜索dict
        for stu in self.stu_list:
            if stu.name == stu_name:
                stu_obj = stu
                break
        if stu_obj is None:
            print('没有找到该学员')
            return
            # 从列表中删除该字典
        self.stu_list.remove(stu_obj)
        print('数据已删除')
        Csv.save_data_to_csv(self.stu_list)


    def update_xs(self):
        # 前提在列表中 name是唯一的 以name作为搜索条件 找到对应数据 修改age 和 score
        stu_name = input('输入要修改学生的姓名')
        stu_obj = None
        # 以name为条件 搜索dict
        for stu in self.stu_list:
            if stu.name == stu_name:
                stu_obj = stu
                break
        if stu_obj is None:
            print('没有找到该学员')
            return
            # 修改stu_obj
        age = int(input('输入要修改的年龄: '))
        score = float(input("输入要修改的分数:"))
        stu_obj.age = age
        stu_obj.score = score
        print('修改成功')
        Csv.save_data_to_csv(self.stu_list)


    def sort_xs(self, func_key, _reverse: bool):
        # 根据传入的排序策略方法 以及 是否反转 来进行排序
        self.stu_list.sort(key=func_key, reverse=_reverse)
        # 排序后立即显示排序之后的结果
        self.show_xs()

    # 定义函数 显示菜单内容
    def show_menu(self):
        str_menu = '''
         1- 添加学生信息
         2- 显示所有学生信息
         3- 删除学生信息
         4- 修改学生信息
         5- 按年龄高-低展示学生信息
         6- 按年龄第-高展示学生信息
         7- 按成绩高-低展示学生信息
         8- 按成绩低-高展示学生信息
         9- 退出系统
           '''

        print(str_menu)
        choice = int(input('请输入你需要的功能'))
        if choice == 1:
            self.add_xs()
        if choice == 2:
            self.show_xs()
        if choice == 3:
            self.del_xs()
        if choice == 4:
            self.update_xs()
        if choice == 5:
            self.sort_xs(func_key=lambda x: x.age, _reverse=True)
        if choice == 6:
            self.sort_xs(func_key=lambda x: x.age, _reverse=False)
        if choice == 7:
            self.sort_xs(func_key=lambda x: x.score, _reverse=True)
        if choice == 8:
            self.sort_xs(func_key=lambda x: x.score, _reverse=False)
        elif choice == 9:
            # 结束程序
            sys.exit('退出程序')


stu_manager = StuManager()
while True:
    stu_manager.show_menu()
