#tuple 元组 不可变序列容器 允许包含任何类型及重复元素
tuple_1 = (1,2,3,'4',True,False,[1,2,3],(1,2,3))
print(tuple_1,type(tuple_1))

#1 定义元组可以使用简略写法
tuple_1 = 'jojo','bb','aa','joke','zb','titi'
print(tuple_1,type(tuple_1))
tuple_1 = 'dd', #   一个数据加逗号判定为元组
print(tuple_1,type(tuple_1))
tuple_1 = ('dd') #使用了括号，而没有逗号，仅是一个数据，非元组
print(tuple_1,type(tuple_1))

#2 基于元组的操作
# + 拼接两个元组
tuple_1 = 'jojo','bb','aa','joke','zb','titi'
tuple_2 = '九九','八八','安安','小丑','左边','提提'
result = tuple_1 + tuple_2
print(result)

# in 判断是否包含某个元素
print('jojo'in result)

# for 循环遍历
for item in result:
    print(item,end='  ')
print()

#索引与切片
print(result[4])
print(result[1:4])
print(result[::-1])
print('*'* 100)
#len max min sum
print(len(result))
print(max(result))
print(min(result))
print(sum((1,2,3,)))

#二维元组
tuple_2D = ((1,2,3),(4,5,6),(7,8,9))
print(tuple_2D)
print(tuple_2D[0][1])
print('*'* 100)

# 与列表的关联操作
#相互转换
list_1 = [1,2,3]
tuple_11 = (1,2,3)
print(tuple(list_1)) #list->tuple
print(list(tuple_11)) #tuple->list
print('*'* 100)

#列表/元组 拆包unpack
a,b,c = list_1
print(a,b,c)
a,b,c = tuple_11
print(a,b,c)
print('*'* 100)

# 数量不对等时，*变量接受多个元素
a,b,*c = list_1
print(a,b,c,type(c))
a,b,*c = tuple_11
print(a,b,c,type(c))
tuple_11 = (1,2,3,4,5)
a,b,*c = tuple_11
print(a,b,c,type(c))
str_1 = 'zbkmp'
a,b,*c = str_1
print(a,b,c,type(c))
print('*'* 100)

# *应该理解为是拆包操作符
print(*list_1)
print(*str_1)
print('*'* 100)

########################
# 集合 set 可变的无序序列 不允许包含重复信息
set_1 = {1,2,3,'4','4',True,False,1.23}
print(set_1)
print('*'* 100)

# 1 针对集合的操作
#差集
set_a = {1,2,3,4,5}
set_b = {4,5,6,7,8}
result = set_a - set_b
print('差集:',result)

#并集 合并-去重
result = set_a | set_b
print('并集:',result)
#交集
result = set_a.intersection(set_b) # result = set_a & set_b  也可以这么写
print('交集:',result)
#异或
result = set_a ^ set_b
print('异或',result)


'''
#in
print(4 in set_a)

#for in
for item in set_a:
    print(item,end='')
print()

#索引 切片
###print(set_a[:]) 集合不支持索引/切片操作 'set' object is not subscriptable 报错

#集合提供的功能函数
#set集合是可变的 修改集合本身
print(set_a.add(200)) #添加元素
print(set_a)
set_a.update((11,12)) #把其他容器的数据添加到集合内
set_a.update([20,22])
print(set_a)
print('*'* 100)
deleted = set_a.pop() #删除第一个元素
print(deleted)
print(set_a)
print('*'* 100)
set_a.remove(200) #指定删除一个数据
print(set_a)
'''
'''
set_a.clear() #清空所有元素
print(set_a)
'''

