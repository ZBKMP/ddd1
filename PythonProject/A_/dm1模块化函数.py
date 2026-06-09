# 函数编程
from tkinter.constants import FIRST


# 函数的间接调用
#1 将函数赋值给一个变量
def my_func():
    print('123')
f = my_func
f()

# b 将函数作为参数,传递到其他函数中，在其他函数中被调用
def fc_a():
    print('1234')
def fc_b():
    print('1234b')
def fc_t_1(fc):
    print('调用传入的函数:')
    fc()
def fc_t_2(fc1,fc2):
    print('调用传入的多个函数:')
    fc1()
    fc2()

fc_t_1(fc_a)
fc_t_1(fc_b)
fc_t_2(fc_a,fc_b)
print('*'*100)

# 2 函数式编程的作用及意义
list_data = [11,9,3,10,5]
# 编写函数 查找列表中第一个大于10的元素
def find_gt_10(list_data):
    for item in list_data:
        if item > 10:
            return item
    return None
# 编写函数 找到列表中一个小于5的元素
def find_lt_5(list_data):
    for item in list_data:
        if item < 5:
          return item
    return  None
########################################################
#将上述两个函数合并成一个 通过传入函数参数 灵活变动条件判断的部分
def condition_fc_gt_10(num):
    return num > 10
def condition_fc_lt_5(num):
    return num < 5
def condition_fc_os(num):
    return num % 2 == 0
def condition_fc_js(num):
    return num % 2 != 0

# 高阶函数 使用其他函数作为参数

def find_item(list_data,condition_fc):
    for item in list_data:
        #将准备好的条件函数作为参数传润 需要什么样的判断 就传什么函数
        if condition_fc(item):
            return item
    return None
first_gt_10 = find_item(list_data,condition_fc_gt_10)
print(first_gt_10)
first_lt_5 = find_item(list_data,condition_fc_lt_5)
print(first_lt_5)
first_os = find_item(list_data,condition_fc_os)
print(first_os)
first_js = find_item(list_data,condition_fc_js)
print(first_js)
