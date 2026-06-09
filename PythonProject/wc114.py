# str 容器
from ctypes import string_at
from turtledemo.penrose import start

str_1 = 'emmmm'
print(str_1, type(str_1))
str_1 = '@ s151ds'
print(str_1, type(str_1))

# 字符串拼接
str_1 = 'emmmm'
str_2 = 'OMMMMM'
jg = str_1 + ' ' + str_2 + ' 1977 '
print(jg)
year = 1977
jg = f'{str_1} {str_2} {year}'
print(jg)

# in 关键词判断 str中是否包含某个 子串
long_str = 'emmmm OMMMMM 1977'
print(str_1 in long_str)
print(str_2 in long_str)
print('1977' in long_str)
# for in 循环遍历str中每个字符
for c in long_str:
    print(c, end=' ')
print()

# 索引 访问容器的部分元素 从左开始0 到长度为该值的—1结束 从右-1开始，切片必须有:
print(long_str[:])
# 切片结果 会在内存中生成一个新数据
print(long_str == long_str[:])
print(long_str is long_str[:])
print()
'''
# 字符串可以提供大量进行内容操作的功能
# 1 find 在字符串中搜索的索引 有则0 没有则-1
print(long_str.find('ll'))
# 设置搜索的开始结束范围
print(long_str.find(__sub:'em',__start:3,__end:4))
print(long_str.find(__sub:'em',__start:3))


# 2 index 类似于find 没有会抛出异常
print(long_str.index('O',0))
print('*'*50)

# 3 count 统计str某段内容的个数
print(long_str.count('m'))
print(long_str.count( 'm',0,100))
print('*'*50)

# 4 startswith 是不是以它开头 endswith 是不是以它结尾
print(long_str.startswith('emmm'))
print(long_str.endswith('1977'))

print('*'*50)

# 5 判断内容是否属于某种形式的文字
wz = 'aaa'
print(wz.islower()) #判断是否小写
wz = 'AAA'
print(wz.isupper()) #判断是否大写
wz = '123'
print(wz.isdigit()) #判断是否数字

print('*'*50)

# 输入用户名 要求用户名中不能包含数字
username = input('输入用户名')
flag = False #假设字符串没有数字
for a in username:
    if a.isdigit():
        flag = True
        break
if flag:
    print('用户名不合法')
else:
    print('可以使用')
'''
#6修改字符串内容 replace 所有匹配的内容 都会被修改 本体不变
print(long_str.replace('emmmm ','amm'))
print('*'*50)

# 7 更改大小写
# 首字母改大写 其他都小写
print(long_str.capitalize())
# 全改为大写
print(long_str.upper())
# 全改为小写
print(long_str.lower())

# 8 字符串分割 str -->list（列表）split-分割
ip_str ='192.168.0.1'
ip_list = ip_str.split('.')
print(ip_list, type(ip_list))
print('*'*50)
#字符串的连接符-join
Lj_str = '-'.join(ip_list)
print(Lj_str)
print('*'*50)

#9 字符之间的比较
str_a = 'emmm'
str_b = 'emmm'
print(str_a == str_b)
print(str_a is str_b)
print(str_a.__eq__(str_b)) #eq 等于
# 比较大小
str_a = 'emmm'
str_b = 'ommm'
print(str_a.__gt__(str_b)) #gt 大于
print(str_a.__ge__(str_b)) #gt 大于或等于
print(str_a.__lt__(str_b)) #lt 小于
print(str_a.__le__(str_b))#le 小于或等于

print('*'*50)
