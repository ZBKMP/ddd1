#list 列表 可变序列容器 可以包含任何类型数据
from wc114 import long_str

list = [1,2,3,"2",True,[1,2,3]]
print(list,type(list))

#针对列表的操作
#一般使用 + 拼接两个列表
list_a = [1,2,3]
list_b = [4,5,6]
result = list_a + list_b
print(result)

#通过 in 判断是否包含某个元素
print(1 in list_a)
print('2' in list)

#for in 遍历list的每个元素
for  i in list:
    print(i,end=" ")
print()

#len max min sum
print(len(list_a))
print(max(list_a))
print(min(list_a))
print(sum(list_a))
print(sum([1,2,3]))

#2 列表索引 切片
list_name = ['yoyo','token','bk','啊勃','806','703','cf','cf']
# 索引
print(list_name[4])
# 切片
print(list_name[:]) #会生成一个新列表结果
print(list_name == list_name[:]) #比较内容
print(list_name is list_name[:]) #比较地址
print(list_name [0:3:1]) #第三个数字表示步长

print(list_name [-1:-3:-1]) #步长设置为负数实现从右往左截取

#列表是可变的 所以可以通过索引去更改元素内容
list_name[0]='krv'
print(list_name)

#2 二维列表
list_2d =[[1,2,3],[4,5,6],[7,8,9]]
print(list_2d,type(list_2d))
#定位到指定的单个元素 需要两层索引
print(list_2d[0][1])
print('*'*100)
# 3列表自身也提供大量可操作的方法
print(list_name.count('cf')) #count 统计数量
print(list_name.index('token',0,3)) #获取元素的索引
# 对列表的修改 修改的是列表的本身
list_name.insert(3,'hello') #在指定位置加入新元素
print(list_name)
deleted = list_name.pop(5) #删除一个元素 默认删除最后一个 返回被删除的元素
print(deleted)
print(list_name)
print('*'*100)
list_name.remove('zbk') #指定删除某个元素 如果有多个 仅删除一个 且不会返回被删除元素
print(list_name)
# list_name.clear() #清空整个列表
# print(list_name)

list_name.append('dd')#在列表最后追加一个新元素
print(list_name)
# list_name.append(['da','dk'])#在列表最后追加一个新元素 如果又是列表 也会当初一个元素看待
# print(list_name)
list_name.extend(['aa','bb','cc'])#扩展列表，相当于两个列表之间使用+
print(list_name)
list_name.reverse()#列表反转
print(list_name)
list_name.sort()#列表排序 元素类型必须统一
print(list_name)
jg = sorted(list_name,reverse=True) #容器list排序 返回排序之后的结果 不会更改原数据
print(jg)
print(list_name)
print('*'*100)
#随机打乱列表中元素的顺序
import random
random.shuffle(list_name) #随机修改列表本体
print(list_name)
print('*'*100)
#数据复制
copy_1 = list_name.copy()#列表复制
print(copy_1)
print(list_name == copy_1) #==号比较内容
print(list_name is copy_1) #is比较内存地址

# 浅拷贝 仅复制列表中的一级元素，如果某个元素又是列表 则该元素不会复制，新/旧两个列表共享一个二维元素
print('浅copy--------------')
list_addr =['湖南',['长沙','湘潭'],'江西','湖北']
list_addr_copy = list_addr.copy()
print(f'old:{list_addr}')
print(f'copy:{list_addr_copy}')
#对copy出列表中 元素中嵌套子列表进行修改
list_addr_copy[0]='广东'
list_addr_copy[1][1]='株洲'
print(f'old:{list_addr}')
print(f'copy:{list_addr_copy}')

# 深拷贝 将列表中所有的元素都复制 包含二维元素
import copy
print('深copy--------------')
list_addr =['湖南',['长沙','湘潭'],'江西','湖北']
list_addr_copy = copy.deepcopy(list_addr) #深拷贝
print(f'old:{list_addr}')
print(f'copy:{list_addr_copy}')
#对copy出列表中 元素中嵌套子列表进行修改
list_addr_copy[0]='广东'
list_addr_copy[1][1]='株洲'
print(f'old:{list_addr}')
print(f'copy:{list_addr_copy}')




