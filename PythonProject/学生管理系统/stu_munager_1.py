# 以list/dict 实现简单学生管理系统
# 学生信息字典 包含:名字nae 年龄age 成绩score
'''
stu_list = [
{},
{},
{}
]
通过list或字典保存学生信息 每个功能封装为独立的函数
'''
import sys

# 定义全局变量 stu_list 用于存储所有的学生信息
stu_list = []


# 把每个功能封装函数 在菜单去调用
def add_xs():
    # 添加学生 进行数据输入
    stu_name = input('请输入学生姓名:')
    stu_age = int(input('请输入学生年龄:'))
    stu_score = float(input('请输入学生成绩:'))
    # 将输入的三个数据 组装成字典
    stu_dict = {}
    stu_dict['name'] = stu_name
    stu_dict['age'] = stu_age
    stu_dict['score'] = stu_score
    # 将生成的学生字典加入到 stu_list列表中
    stu_list.append(stu_dict)


def show_xs():
    # 展示所有学生信息
    print("所有学生信息如下:")
    for stu in stu_list:
        print(f'stu_name:{stu["name"]} stu_age:{stu["age"]} stu_score:{stu["score"]}')


def del_xs():
    # 前提在列表中 name是唯一的 以name作为搜索条件 找到对应数据 从列表中删除
    stu_name = input('输入要删除学生的姓名')
    stu_dict = None
    # 以name为条件 搜索dict
    for stu in stu_list:
        if stu['name'] == stu_name:
            stu_dict = stu
            break
    if stu_dict is None:
        print('没有找到该学员')
        return
    # 从列表中删除该字典
    stu_list.remove (stu_dict)
    print('数据已删除')



def update_xs():
    # 前提在列表中 name是唯一的 以name作为搜索条件 找到对应数据 修改age 和 score
    stu_name = input('输入要修改学生的姓名')
    stu_dict = None
    # 以name为条件 搜索dict
    for stu in stu_list:
        if stu['name'] == stu_name:
            stu_dict = stu
            break
    if stu_dict is None:
        print('没有找到该学员')
        return
    # 修改stu_dict
    age = int(input('输入要修改的年龄: '))
    score = float(input("输入要修改的分数:"))
    stu_dict['age'] = age
    stu_dict['score'] = score
    print('修改成功')

def sort_xs(_key,_reverse:bool):
    #根据传入的排序策略方法 以及 是否反转 来进行排序
    stu_list.sort(key=_key,reverse=_reverse)
    #排序后立即显示排序之后的结果
    show_xs()


# 定义函数 显示菜单内容
def show_menu():
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
        add_xs()
    if choice == 2:
        show_xs()
    if choice == 3:
        del_xs()
    if choice == 4:
        update_xs()
    if choice == 5:
        sort_xs(_key=lambda x:x['age'],_reverse=True)
    if choice == 6:
        sort_xs(_key=lambda x:x['age'],_reverse=False)
    if choice == 7:
        sort_xs(_key=lambda x:x['score'],_reverse=True)
    if choice == 8:
        sort_xs(_key=lambda x:x['score'],_reverse=False)
    elif choice == 9:
        # 结束程序
        sys.exit('退出程序')


# 执行程序
while True:
    show_menu()
