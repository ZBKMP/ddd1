#流程控制 循环 在满足某种条件下会重复执行一段代码
# while 条件成立后循环的代码，如不成立则退出循环
'''
while True:
    print('循环执行')
'''

'''
#使用while可控制次数循环,及嵌套
day = 1
while day <= 5:
     print(f"---今天星期{day}搬砖---")
     day += 1
     hour = 1
     while hour <= 8:
         print(f"搬砖第{hour}小时")
         hour += 1
'''

'''
#for 迭代循环 迭代遍历某个数据结构内的所有元素
#使用for循环遍历str
str_1 ='EMMMM!!!哟'
for c in str_1:
    print(c, end=' ')
print()
#配合 range 函数 实现数字循环
for i in range(1,10,2):#设置开始及结束及步长
    print(i, end=' ')
print()
'''
'''
# break 在循环过程中 如果执行了break 则会立即退出循环
for i in range(1,6):
    print(f'今天星期{i} 夜跑' )
    for s in range(1, 6):
        print(f'跑了第{s} 圈')
        if s == 3:
            print('休息会')
            break #退出当前循环，外层无法

    if s == 2:
        print('休息')
        break

'''
#contine 在某次循环过程中 如果执行continue 则本次代码不执行 继而执行下一次循环
t = 1
while t <= 10:
    print(f'开始做第{t}题')
    if t ==5:
        print(f'第{t}题太难，跳过')
        t += 1
    continue   #跳过后面的代码 继续执行前面循环
    print(f'第{t}提做完了')
    t += 1
'''
'''
'''
#使用sum函数实现 累加1-100
E100 = sum(range(1,101))
print(E100)
#99乘法表
for i in range(1,10):

   for j in range(1,i+1):
       print(f'{i}*{j}={i*j}',end='\t')
   print()
#字符含义
'''

'''
\t 制表符 多个空格对齐
\n 换行
'''

'''
#程序运行时自动产生1-100之间的随机数，让玩家来猜
import random   #import导入模块,#random 随机数生成模块
num = random.randint(1,100)
print(num)
'''

