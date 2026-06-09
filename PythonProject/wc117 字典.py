# dict可变键值对容器 每个元素由 key--value组成 key不可重复 value可以重复
dict_1 = {'key': 'value', 1: False, 2: False, 'list': [1, 2, 3], (): (1, 2, 3), 'dict_key': {1, 2, 3}}
print(dict_1)

# 只有 不可变 类型的数据才能作为key
print(dict_1, type(dict_1))
# 尽量做到数据类型统一
dict_2 = {1: 'a', 2: 'b', 3: 'c'}
print(dict_1)
print('*' * 100)

# 字典的操作
# 通过key去获取元素
print(dict_2[1])  # 找不到key 就会报错
print(dict_2.get(2))  # get方法等价于[key]获取数据，不能赋值
print('*' * 100)

# 字典是可变的
dict_2[1] = '啊啊'
print(dict_2)
print('*' * 100)
# in 操作 判断字典中是否包含某个key
print(4 in dict_2)
# for in 遍历字典中所有的key----------------------------------
for k in dict_2:
    print(k, dict_2[k])

# del delete 删除元素
del dict_2[1]
print(dict_2)

# 2 dict 本身包含的操作方法
# update 修改 添加 新元素
dict_2.update({3:'tt', 4:'gaga', 5:'小五', 6:'老六'})
print(dict_2)
'''
# pop 删除元素 
dict_2.pop(5)
print(dict_2)
'''
# pop 删除元素 返回被删除的value
deleted_value = dict_2.pop(5)
print(deleted_value)
print(dict_2)

# popitem  删除最后一个 返回由key和value组成的元组
deleted_item = dict_2.popitem()
print(deleted_item,type(deleted_item))
print(dict_2,type(dict_2))
'''
# celar 清空字典内容
dict_2.clear()
print(dict_2)
'''

# keys() values() items() 分别获取所有key、value、items
for k in dict_2.keys():
    print(k)
for v in dict_2.values():
        print(v)
for k,v in dict_2.items():
    print(k,v)

#    字典推导式------------------------
list_k = ['k1', 'k2', 'k3', 'k4', 'k5']
list_v = ['value1', 'value2', 'value3', 'value4', 'value5']
#推导出每个k:v组合成新列表
dict_test = {list_k[i]:list_v[i] for i in range(len(list_k))}
print(dict_test)

#将dict_1的k，v对调生成新字典
dict_new = {v:k for k,v in dict_test.items()}
print(dict_new)

# 4 dict list tuple 之间的转化 ---------------
dict_2 = {1: 'a', 2: 'b', 3: 'c', 4: 'd',}
#字典直接转换成list和tuple 仅能获取所有的key
list_key = list(dict_2)
print(list_key)
list_key = tuple(dict_2)
print(list_key)
list_keys =list(dict_2.keys())
print(list_key)
list_value = list(dict_2.values())
print(list_value)
list_i = list(dict_2.items())
print(list_i)

# 如果 列表或者元组 元素仅一个值 无法转换字典
#只有每个元素都包含两个元素(1,a)，才可转成字典
list_datas = [(1,'a'),(2,"B"),(3,'c'),[4,'d']]
dict_nwe = dict(list_datas)
print(dict_nwe)

# zip 压缩和合并多个列表和元组 结果为短板数量，数据要符合一致，否则以短的为输出
list_k = ['k1', 'k2', 'k3', 'k4', 'k5']
list_v = ['value1', 'value2', 'value3', 'value4', 'value5']
tuple_v = ('vvalue1', 'vvalue2', 'vvalue3', 'vvalue4', 'vvalue5')
list_zip_data = list(zip(list_k,list_v,tuple_v))
print(list_zip_data)

# zip压缩两个list/tuple转dict，字典压缩只能压缩两个，多了出不来
dict_zip_data = dict(zip(list_k,list_v))
print(dict_zip_data)
print('*' * 100)

#python 中能去操作容器的常用方法  sorted排序 zip压缩--any函数---------------------------------
#any函数套用在一个由boolean组成的 列表与元组
#0,0.0,'',None,{},[]，(),set()都可以看成是False，其余都是True。
print(any([False, False]))  #-------元素中只要有一个True，结果为True

#all函数 #any函数套用在一个由boolean组成的 列表与元组-必须所有结果都是True，结果为True
print(all([True, True]))

#判断列表中有没有大于10的元素
nums = [1,2,3,5,4,18]
flag= any([i>10 for i in nums])
print(flag)

#判断字符串内容是否都是小写字母
user = 'tOto'
flag = all([ch.islower() for ch in user])
print(flag)
