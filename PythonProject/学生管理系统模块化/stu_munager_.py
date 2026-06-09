# 拆分项目代码,把每个模块迁移到专属的文件中去

import sys
from 数据库 import StuCRUD
from 实体类 import Stu


#############################################################################################

# 学生管理工具类
class StuManager:

    def __init__(self):
        # 将数据操作类对象 作为属性
        self.__stuCRUD = StuCRUD()

    # 把每个功能封装函数 在菜单中去调用
    def add_student(self):
        # 添加学生 先进行数据输入
        stu_name = input("请输入学生姓名:")
        stu_age = int(input("请输入学生年龄:"))
        stu_score = float(input("请输入学生成绩:"))
        # 数据封装为对象
        stu = Stu(0, stu_name, stu_age, stu_score)
        result = self.__stuCRUD.add(stu)
        if result:
            print("数据添加成功")
        else:
            print("数据添加失败")

    def show_students(self):
        # 展示所有学生信息
        print("所有学生信息如下:")
        stu_list = self.__stuCRUD.query()
        for stu in stu_list:
            print(stu)

    def del_student(self):
        stu_name = input("请输入你要删除的学生ID:")
        result = self.__stuCRUD.delete(int(stu_name))
        if result:
            print("数据删除成功")
        else:
            print("数据删除失败")

    def update_student(self):
        id = input("请输入你要修改的学生ID:")
        name = input("请输入要修改的姓名:")
        age = int(input("请输入要修改的年龄:"))
        score = float(input("请输入要修改的分数:"))
        stu = Stu(id, name, age, score)
        result = self.__stuCRUD.update(stu)
        if result:
            print("数据修改成功")
        else:
            print("数据修改失败")

    def sort_student(self, colname, type):
        stu_list = self.__stuCRUD.orderby(colname, type)
        for stu in stu_list:
            print(stu)

    def show_student(self):
        id = input("请输入你要修改的学生ID:")
        stu = self.__stuCRUD.get(int(id))
        print(stu)

    # 定义函数 显示菜单内容
    def show_menu(self):
        str_memu = '''
        1) 添加学生信息
        2) 显示所有学生信息
        3) 删除学生信息
        4) 修改学生信息
        5) 按年龄高-低展示学生信息
        6) 按年龄低-高展示学生信息
        7) 按成绩高-低展示学生信息
        8) 按成绩低-高展示学生信息
        9) 按ID查询单个数据
        0) 退出系统
        '''
        print(str_memu)
        choice = int(input("请输入你需要的功能:"))
        if choice == 1:
            self.add_student()  # 添加学生
        elif choice == 2:
            self.show_students()  # 显示所有学生
        elif choice == 3:
            self.del_student()  # 删除学生
        elif choice == 4:
            self.update_student()  # 修改学生
        elif choice == 5:
            self.sort_student('age', 'desc')  # 按照年龄降序排序
        elif choice == 6:
            self.sort_student('age', 'asc')  # 按照年龄升序排序
        elif choice == 7:
            self.sort_student('score', 'desc')  # 按照成绩降序排序
        elif choice == 8:
            self.sort_student('score', 'asc')  # 按照年龄生序排序
        elif choice == 9:
            self.show_student()
        elif choice == 0:
            # 结束程序
            sys.exit(0)


if __name__ == '__main__':
    # 执行程序
    stu_manager = StuManager()  # 创建管理工具对象
    while True:
        stu_manager.show_menu()  # 调用对象的显示菜单方法
