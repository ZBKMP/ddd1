
'''
#固定汇率
hl = 6.9
RMB =float(input("输入人民币金额"))
USD1= RMB / hl
print('USD金额 = %.2f' % USD1)
USD =float(input("输入USD金额"))
RMB1= USD * hl
print("RMB金额 = %.2f" % RMB1)
'''


'''
# 治愈比例计算程序
QZ = 1000
ZL = 850

rate = ZL / QZ * 100
print(f"确诊人数: {QZ}")
print(f"治愈人数: {ZL}")
print(f"治愈比例: {rate:.2f}%")
'''

'''
# 古代重量换算: 1斤=16两

# 设置换算率
RATE = 16

# 测试数据
jin = 10
liang = 2

# 斤转两计算
jtol = jin * RATE
print(f"{jin}斤 = {jtol}两")

# 两转斤计算
ltojin = liang / RATE
print(f"{liang}两 = {ltojin:.2f}斤")
'''

'''
# 输入一个四位数，计算各位数字之和
# 测试数据

''‘
num = int(input("输入四位数"))
if num < 1000 or num> 9999:
    print("不满足要求")
else:
    q = num // 1000
    b = num % 1000 // 100
    s = num % 100 // 10
    g = num % 10
    result = q + b + s + g
    print(result)
'''

'''
#相亲及年龄收入
age =int(input('请输入你的年龄'))
if age < 18 or age > 30:
   print("不行")
else:
  money =int(input('输入你的月收入'))
  if money < 10000:
     print('不行')
  elif money >= 10000:
     print('nice')
     
'''

'''
#使用while 嵌套循环99乘法口诀表
a = 1
while a <= 9:
    b = 1
    while b <= a:
        print(f"{b}*{a}={a*b}", end='\t')
        b += 1
    print()
    a += 1
'''

'''
# 计算用户输入的年份离1990年1月1日相距多少天 （注意闰年，每个月天数不一样）
year = int(input('输入当前的年份'))
month = int(input('输入当前的月份'))
date = int(input('输入当前的天数'))
jg = 0  # 总计累加的结果
# 1 1900-2024天数之和
for y in range(1900, year):
    if y % 4 == 0 and y % 100 != 0 or y % 400 == 0:
        jg += 366
    else:
        jg += 365

    # 2 1到所输入月份前一个月数之和
for m in range(1, month):
    if m == 2:
        # 判断当前年份是否为润年
        if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
            jg += 29
        else:
            jg += 28

    elif m in (4, 6, 9, 11):
        jg += 30
    else:
        jg += 31
    # 3 最后加上所输入的日期
jg += date
print(f'总计{jg}天')
'''
# 使用死循环+break实现  #循环输入数字进行累加 直到输入的数字为0，就结束循环，并最后输出累加的结果 利用输入来控制循环的次数
# 方案1
'''
n = 1
total = 0
while n!= 0:
    n = int(input('输入一个数字'))
    total += n
print(f'所有数字累加为{total}')
'''

'''
#方案2 ~逻辑清晰
total = 0
while True:
    n =int(input('输入数字'))
    total += n
    if n == 0:
      break
print(f'所有数字累加为{total}')
'''

'''
# 一个球从100米高度自由落下，每次落地反跳回原高度的一半
#再落下，求它在第10次落地时，共经历过多少米?第10次反弹多高
#第一次落地是单独的 后九次的处理逻辑是一致的
height = 100
total = 0 #累计运行距离
for i in range(1, 10):
    #每次距离是上一次的一半 上下运行两次
     height /= 2
     total += height*2
total += height
print(f'总距离{total}')
'''

'''
#程序运行时自动产生一个1-100之间的随机数，让游戏者来猜这个数。当键盘接收到游戏者输入的数据后 程序给出相应的提示、
import random
num = random.randint(1, 100)
while True: #无法预计循环次数 当输入的数字与num相同 则退出
    n =int(input('请输入100以内的数字:'))
    if n == num:
        print('猜对了')
    if n > num :
        print('猜大了')
    if n < num :
        print('猜小了')
'''
'''
#有30人，包括男人女人小孩 他们在一饭店共消费50先令，
#其中每个男人花3先令，每个女人花费2先令，每个小孩花1先令，求男人 女人 小孩各多少人
#man 0-16 women 0-25 child 0-30
for i in range(0, 17):#男性可能的数量
    for j in range(0, 26):#女性可能的数量
     for k in range(0, 31): #小孩可能的数量
       if i+j+k == 30 and i*3+j*2+k == 50:
           print(i, j, k,sep='\t')
'''
'''
# 用户名必须包含 大写 小写 数字 这三种字符
suername = 'Wc123'
#定义 三个数字及累计各类文字的个数
u=l=d=0
for i in suername:
  if i.isupper():
    u += 1
  if i.islower():
      l += 1
  if i.isdigit():
      d += 1
if u==0 or l==0 or d==0:
  print('格式不对')
if u==1 or l==1 or d==1:
    print('格式正确')
'''

'''
# 判断一个字符串是否为回文串
# 一个字符串若从头阅读与从尾阅读是相同的则是回文字符串如:wc111w
str_1 = 'wc111w'
hui_str = str_1[::-1]
print(hui_str)
'''

'''
# 验证电子邮件字符串的合法性，1.必须包含@和.而且@只能有一个，2.不能以@或.开头以及结尾，3.@必须出现在.之前
email = '132@gmail.com'
if (email.count('@') == 1 and
        email.count('.') == 1 and
        not email.startswith('@') and
        not email.startswith('.') and
        not email.endswith('@') and
        not email.endswith('@') and
        email.find('@') < email.find('.')):
    print("格式正确")
else:
    print('格式不正确')
'''

'''
# 小案例:彩票双色球
# 红球6个 1-32之间 不可重复，蓝色1个 1-15之间
# 1.随机产生一组彩票-前6个为红球 最后一个为蓝球
# 2.输入一组彩票数据，判断是否正确
import random #导入random随机数模块
list_t = [] #list = 列表=空值
# 随机产生1-32之间的数字 可能有重复 重复结果要作废
while 1: #无限循环

    if len(list_t) == 6: #如果list的字符长度=6 6个球
      break #结束循环流程
    num = random.randint(1,33) #num=随机生成的1-32之间的数

    if num not in list_t: #如果mun没有在list里，在list后面塞一个元素
        list_t.append(num)
print('red:',list_t)
print('bule:',random.randint(1,16))

# 2
num2 = input('输入六个双色球数字，用空格隔开')
list_num2 = num2.split(' ') #用户输入的内容分割成空格，并且转换成列表
print(list_num2)
flag = True #打开开关
for num in list_num2:
    if list_num2.count(num) >= 2:
        flag = False #关闭开关
    break
print(flag)
'''

'''
# 小练习 使用列表推导式 获取1-10之间每个数字的立方
lf = [lifa ** 3 for lifa in range(1,11)]
print(lf)
# 小练习 使用列表推导式 实现获取10-30之间能被3或5整除的数字
zc = [zhenchu for zhenchu in range(10, 31) if zhenchu % 3 == 0 or zhenchu % 5 == 0]
print(zc)
# 小练习 使用列表推导式 摘取字符串中所有的大写字母形成一个列表
jg = [ lb for lb in 'Hello,worD'if lb.isupper()]
print(jg)
'''

'''
#题目 两个列表[1,5,7,9]和[2,2,6,8]合并为[1,2,2,5,6,7,8,9] 还需排序
list_sz = [1,5,7,9]
list_sz.extend([2,2,6,8])
list_sz.sort()
print(list_sz)

#题目 一行代码实现1--100之和 利用sum() 函数求和
print(sum(range(1,101)))

#题目 [[1,2],[3,4],[5,6]] 一行代码展开该列表，得出[1,2,3,4,5,6]
print([num for list in [[1,2],[3,4],[5,6]] for num in list])

#题目 x='abc',y='def',z=['d','e','f'] 分别求出 x.join(y)和join(z)
x='abc'
y='def'
z=['d','e','f']
print(x.join(y))
print(x.join(z))
join 字符串连接规则: x = 分隔符， d x e x f = dabceabcf
'''

'''
print('*'*100)
#题目--- s='asdddwefasdsagfzscx'，去重并且从小到大排序
s='asdddwefasdsagfzscx'
set_s = set(s)
list_s = list(set_s)
list_s.sort()
print(''.join(list_s))
'''

'''
#题目 使用pop和del删除字典中的"nam"字段， dic={"nam":"zx"，"age":18}
dic={"nam":"zx","age":18}
dic.pop("nam")
print(dic)
dic={"nam":"zx","age":18}
del dic["nam"]
print(dic)
'''

'''
#题目--- 结合三元操作符 return value1 if money<500 else value2
age = 15
result = '成年' if age>= 18 else '未成年' #三元操作符
print(result)
def money(money,point):
    return money * 0.8 if point >= 1000 else money
print(money(10000,2000))
'''

'''
# 题目---定义函数 传入年月，获取当月有多少天， 注意月风魔判断及2月的润年问题
def days(year, month):
    if month == 2:
        if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
            return 29
    if month in [4, 6, 9, 11]:
        return 30
    return 31
print(days(2026, 4))
'''

'''
# 题目---定义函数，参数为列表 将列表内的偶数值的平方组合新列表返回
def mylist(list_num: list[int]) -> list:
    if type(list_num) != list:
        return  # 没有返回 结果为None
    for num in list_num:
        if type(num) != int:
            return
    list_1 = [x ** 2 for x in list_num if x % 2 == 0]
    return list_1
print(list([1, 2, 3, 4, ]))
print(list((1, 2, 3, 4, )))
'''

'''
#题目 使用lambda表达式 求得列表的最大值或最小值
data = [8,4,10,16,2]
def f (data,fc):
    for num in data:
        if fc(num):
            return  num
    return None
gt_10 =f(data,lambda x:x>10)
print(gt_10)
lt_5 =f(data,lambda x:x<5)
print(lt_5)
'''

'''
#题目 使用函数式编程实现:在列表中按元素奇数或偶数进行判断挑选元素
lis_data = [7,8,3,4,10]
def nwe_list (lis:list,condition_func,calc_fun):
    return [ calc_fun(i) for i in lis if condition_func(i)]
print(nwe_list(lis_data,condition_func=lambda x:x%2==0,calc_fun=lambda x:x**2))
print(nwe_list(lis_data,condition_func=lambda x:x%2!=0,calc_fun=lambda x:x**3))

#题目 使用函数式编程实现:求得列表中的最大值和最小值(使用自定义/max min 函数实现)
def get_max_min(lis_data,condition_func):
     value = lis_data[0] #假设列表的第一个元素是最大的
     for i in range(1,len(lis_data)):
       if condition_func(lis_data[i],value):
         value = lis_data[i]
     return value
print(get_max_min(lis_data,lambda x,y:x>y)) #求最大值
print(get_max_min(lis_data,lambda x,y:x<y)) #求最小值

# 通过lambda表达式实现 灵活统计多个employee字典的年龄key或工资key对应value的和
list_emp = [
    {'name':'zb','age':18,'salary':10000},
    {'name':'zx','age':22,'salary':12000},
    {'name':'zc','age':26,'salary':15000},
]
def sum_total(list_emp:list[dict],func_cum):
    total = 0
    for i in list_emp:
        total += func_cum(i) #将每个元素传递到函数参数内，得到对应结果
    return total
total = sum_total(list_emp,lambda x:x['salary'])
print(total)
total = sum_total(list_emp,lambda x:x['age'])
print(total)

# 定义函数 传入列表，过滤出其中大于0的偶数，并返回新列表
#filter的lambda表达式必须返回bool值，每个元素经过lambda运算后结果为true，才能被筛选
list_data=[1,3,5,2,8,6]
result = filter(lambda x:x>0 and x%2==0,list_data)
print(list(result))

#定义函数利用map和filter,lambda表达式，传入列表，将其中偶数/奇数 变为该数的平方/立方，结果生成新集合
list_new = map(lambda x:x**2,filter(lambda x:x%2==0,list_data))
print(list(list_new))

#根据字符串长度排序列表
list_str = ['zbk','zbkmp','kmpa','zs']
list_str.sort(key=lambda x:len(x))
print(list_str)
'''


'''
# 小案例 ：方法传入参数表示年龄，通过闭包实现在调佣该方法前会进行对参数进行年龄范围判断
#         如果年龄判断不合法,抛出异常
def age_filter(func):
   def wrapper(age,*args,**kwargs):
      if age < 0 or age > 130:
        raise ValueError("年龄必须在 1-130 之间")
      if type(age) != int:
        raise TypeError("年龄必须是整数")
      else:
        print('校验通过')
        return func(age,*args,**kwargs)
   return wrapper

@age_filter
def update_database(age):
    print(f"数据已写入：学生年龄为 {age}")

update_database(130)

'''


# 编写以下继承体系:
# 职员 Employee (属性：id,name,sex 方法:__str__)
#
# 文员 Clerk (属性：id,name,sex,age,jx(绩效),重写方法:__str__,work(处理文档))
# 销售 Seller (属性：id,name,sex,age,xs(销售额),重写方法:__str__,sale(销售))
# 经理 Manager (属性：id,name,sex,age,bm(部门),重写方法:__str__,manage(管理))
#
# 重写 __gt__ __lt__ __ge__ __le__




































































# 问答题 讲述all函数和any函数的作用
# all() = 全都对才算对
# any() = 有一个对就算

# 问答题 a=(1,) b=(1)  c=("1")
# a=元组 tuple:允许包含任何类型及重复元素,b=int 整数 c=str 字符串


# 面试题----------------------------------------------------------------~~~~~~!!!!!!!!!!!!!!!!!!
# 问答题 --- 列出python中可变数据类型和不可变数据类型，并简述原理
# 不可变类型（创建后不能修改）：数字：int, float, bool
# 字符串：str，元组：tuple，字节：bytes
# 可变类型（创建后可以修改）：列表：list，字典：dict，集合：set，字节数组：bytearray
# 原理：不可变类型修改时会创建新对象（如a=1; a+=1创建新整数2）
# 可变类型修改时直接改原对象（如lst=[1]; lst.append(2)还是同一个列表）
# 关键区别：不可变对象可哈希，能作字典键；可变对象不可哈希，不能作字典键。


# 案例 python中交换两个数值
'''
a,b = 1,2
a,b = b,a
print(a,b)
Python 先计算 b, a。它会创建一个临时的元组，把当时 b 和 a 的值放进去，结果是 (2, 1)
'''
# 案例 --- python中copy和deepcopy区别
# .copy 列表复制 浅拷贝 仅复制列表中的一级元素，如果某个元素又是列表 则该元素不会复制，新/旧两个列表共享一个二维元素
# .deepcopy将列表中所有的元素都复制 包含二维元素


# 案例 --- 分析一下代码运行结果--------------------------
'''
def fn(k,v,dic={}):
    dic[k] = v
    print(dic)
fn('one',1)
fn('two',2)
fn('three',3,{})
'''
# 代码运行结果是：第一次调用打印 {'one': 1}，第二次调用打印 {'one': 1, 'two': 2}，第三次调用打印 {'three': 3}。
# dic={}空字典在函数定义时创建一次。第一次调用往这个共享字典添加了 'one': 1，第二次调用在同一个字典上添加了 'two': 2。
# 第三次调用传参了空字典 ，把之前第一次和第二次的传参干掉了，所以只打印第三次的结果


# 案例题------讲述fun(*args,**kwargs)中的*args,**kwargs是什么意思
#    *  表示该参数为元组传参，该参数可以接收多个参数
#    如果在 * 参数之后，还有其他参数定义，这些参数必须使用关键字传参
#    ** 表示字典传参，可以接受多个关键字参数，，** kwargs 必须放置在参数列表的最后面


# 案例题------pyhon传参数是值传递还是地址传递
# 对不可变对象是值传递，对可变对象是列表传递，实质都是传递对象的引用。
#基本类型 不可变数据类型 都是值传递调用函数时传递的是数据变量数据的地址 而不俗变量本身的地址
# num = 100
# def change_num(n):
#      n = n + 100
# change_num(num)
# print(num)
# num1 = [1,2,3]
# #可变类型 作为参数传递 传递进去的参数本身的地址
# def change_list(lis):
#     lis.extend([3,2,1])
# change_list(num1)
# print(num1)
