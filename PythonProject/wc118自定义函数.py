#  函数(方法)
#将一段代码进行包装取名，可以被反复调用，调用时可能需要传入参数，调用后可能返回结果
from typing import AnyStr,Any
#1 自定义函数
#无参数也返还值
def say_hello():
    print('hello')
#调用无参数 无返回值
say_hello()
say_hello()

#包含参数的函数 :str 作为传输参数的类型建议 没有约束力
def say_hello_to_someone(someone:str,times:int):
   for i in range(times):
       print(f'hello{someone}{i}')
#调用有参数的函数
say_hello_to_someone('jokre',5)

#包含返回值的函数 其中需要通过return数据 表示函数返回的结果->return_type 建议返回类型
def add_function(num1:int,num2:int)-> int:
    result = num1 + num2
    return result
# 调用有返回值的函数
fhjg = add_function(10,10)
print(fhjg)

# return 在函数中的使用意义
# 函数一旦执行了return就表示函数已经结束了
# 函数中没有返回值 也可以执行return 表示函数结束 或者返回None

def my_loop_func():
    for i in range(10):
        for j in range(i):
            print(f'{i}*{j}={i*j}',end='\t')
            if j == 3:
                return #直接结束整个循环 可以退出多个循环
        print()
my_loop_func()
print()
# 函数中如果包含条件选择，每个分支都可以有return 但最终只会执行一个return语句
def my_age(age:int)->str:
    if age >= 60:
        return '老年'
    if age >= 40:
        return  '中年'
    if age >= 18:
      return '青年'
    return '未成年'
age_str = my_age(1)
print(age_str)
print()
#函数只能返回一个结果,逗号分隔多个数据会字典合并为元组
def my_math(num1:int,num2:int) :
    result1 = num1+num2
    result2 = num1*num2
    return result1,result2
result = my_math(1,1)
print(result,type(result))
print()

# 2 函数的调用传参 （传参就是"给函数传递它需要的数据"。）
num = 100 #全局变量 在后续的每个函数中 都可以使用全局变量
def my_area_test():
    num = 200#如果函数内部有变量与全局变量重名，内部优先
    my_data= 10 #局部变量 仅能在函数内部使用 外部无法使用
    print(f'num:{num}')


my_area_test()



def my_global():
    #1  global就是"在函数里对窗外大喊：我要改的是外面那个全局变量！"的声明
    global num
    num += 100
    print(f'num:{num}')
    #2  global 将局部变量升级为全局变量 函数执行完之后 外部也可以使用
    global mydata
    mydata = 10
my_global()
print(f'mydata:{mydata}')

print("*"*100)

# 3函数调用时的参数传递
def my_arg(a1:int,a2:int,a3:int)->None:
    print(a1)
    print(a2)
    print(a3)
my_arg(10,20,30)
my_arg(a1=1,a2=2,a3=3) #在函数调用时可以使用 参数名=参数值的方式传递参数 关键字传参

# 将多个参数包含在容器中,将容器进行拆包操作作为参数传递
list_args = [7,8,9]
my_arg(*list_args) #  * 拆包 list tuple set str
tuple_args = [4,5,6]
my_arg(*tuple_args)
str_args = '123'
my_arg(*str_args)
print("*"*100)
#字典拆包
dict_args = {6:36,8:12,4:213}
my_arg(*dict_args) #默认拆包key
my_arg(*dict_args.keys())# 指明开包keys
my_arg(*dict_args.values())# 指明开包values
my_arg(*dict_args.items()) #指明开包items

# **拆包字典 作为参数传递给函数 要求一定要以参数名作为kes(str) 重点使用方式~~~~~~~~~~~！！！！！！！！！！！！！！！！！！！！
dict_args = {'a1':10,'a2':20,'a3':50}
my_arg(**dict_args)

# 在定义参数时,可以使用 * 分割 位置参数与关键字参数
def my_arg2(p1,*,p2)->None:
    print(p1)
    print(p2)
# *之前可以按顺序传递参数或使用关键字传参, *之后必须使用关键字传参
my_arg2(100,p2=200)
my_arg2(p1=100,p2=200)

#在定义参数是 可以在参数前增加 * ,表示该参数为元组传参，该参数可以接收多个参数
# 如果在 *p 参数之后，还有其他参数定义，这些参数必须使用关键字传参
print("*"*100)
def my_arg3(P1,*P2,P3)->None:
    print(P1)
    print(P2) #接收结果为元组---------------------------------
    print(P3)
 # *P2 可以接受第一个参数之后 所有的参数
my_arg3('NIHAO','yoyo','33','dd',P3='DIDI')

print("*"*100)

#参数在定义时可以设置默认值，则调用时该参数可以不传递
def my_arg4(p1,p2=11,p3=20,p4:int|None=None)->None:
    print(p1)
    print(p2)
    print(p3)
my_arg4(100)
my_arg4(100,p2=200,)

# 定义函数时,在参数名前面可以使用 ** 表示可以接受多个关键字参数
# ** kwargs 必须放置在参数列表的最后面——————————————————————————————————
def my_arg5(p1,**p2,)->None:
    print(p1)
    print(p2) #接收结果为字典-------------------------------
my_arg5(100,K1=183,K2=152,K3='4005')
print("*"*100)

#综合案例
def my_arg6(p1,p2,p3=2,*P4,**p5)->None:
    print(p1)
    print(p2)
    print(p3)
    print(P4)
    print(p5)

my_arg6(166,20,5,4,5,K1=183,K2=152,K3='4005')








