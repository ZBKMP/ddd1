# lamba 定义简单的匿名函数
# 语法: lambda 参数1,参数2:返回值

# 1 定义 lambda 表达式
def say_hello(someone):
    return f'hello {someone}'


# 使用 lambada 表达式简化上述代码
f = lambda someone: f'hello {someone}'
print(f('dd'))
# 2 多个参数的形式
# 定义lambda表达式 返回两个数字中最大的那一个
f = lambda x,y: x if x<y else y
print(f(101, 100))

#3 将上一个案例的多个函数改为lambda表达式 的简化代码
list_data = [11,9,3,10,5]
def find_item(list_data,condition_fc):
    for item in list_data:
        #将准备好的条件函数作为参数传润 需要什么样的判断 就传什么函数
        if condition_fc(item):
            return item
    return None
first_gt_10 = find_item(list_data,lambda x:x>10)
print(first_gt_10)
first_lt_5 = find_item(list_data,lambda x:x<5)
print(first_lt_5)
first_os = find_item(list_data,lambda x:x%2 ==0)
print(first_os)
first_js = find_item(list_data,lambda x:x%2 !=0)
print(first_js)

# python中 系统已经定义好的一些高阶函数
#sorted / list.sort
list_data = [11,9,-3,-10,5]
# key参数表示传递一个函数 这个函数作为排序的策略，函数的参数就是容器的每个元素，函数的返回值作为排序比较大小的工具
list_data.sort(key=lambda x:x,reverse=False)
print(list_data)
#改变策略 以数据的绝对值作为排序的依据
list_data.sort(key=lambda x:abs(x),reverse=False)
print(list_data)

# max / min
list_data = [11,9,-3,-10,5]
max_value = max(list_data,key=lambda x:abs(x))
min_value = min(list_data,key=lambda x:abs(x))
print(max_value)
print(min_value)

#filetr 通过设置条件函数 筛选出容器中符合要求的元素
list_data = [5,6,1,25,12,25,18]
list_new = list(filter(lambda x:x%3==0 or x%5 == 0,list_data))
print(list_new)

# map 通过传入函数参数,将容器的每个元素转换成新元素
list_data = [5,6,1,25,12,25,18]
list_new = list(map(lambda x:x%5,list_data))
print(list_new)











