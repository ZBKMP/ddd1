# 函数闭包 函数内还可以定义内部函数,将内部函数作为返回值


# 1 语法定义:
def func_1():
    print("func_1")
    data = 100

    # 在一个函数的内部再定义一个函数
    def func_2():
        # 闭包函数可以使用外部函数定义的数据
        # 如果内部又定义了和外部函数同名的变量 会覆盖外部的
        # 不能直接修改外部函数的数据 除非使用nonlocal关键字修饰
        nonlocal data
        data += 200
        print(f"func_2 {data}")

    # 将闭包函数作为返回值
    return func_2


# 调用返回闭包函数的函数
result = func_1()
result()


# 2 使用场景: 再原有功能的基础上 增加新功能 而不去改变原有代码
# 结合 函数参数 与 函数返回值 实现
def method_old():
    print("method_old")


def method_other():
    print("method_other")


# 传入函数 给传入的函数前后增加新的业务逻辑
def create_new_method(method):
    # 在内部定义新函数
    def new_method():
        print("method new being.....")
        method()
        print("method new end.....")

    return new_method


# 调用新函数返回结果
result = create_new_method(method_old)
result()
result = create_new_method(method_other)
result()


# 3 为函数增加参数与返回值
def set_age(age: int):
    print(f"your age is :{age}")
    return age + 10


def set_age_name(age: int, name: str):
    print(f"your age is :{age}")
    print(f"your name is :{name}")
    return f'age:{age} name:{name}'


def create_new_method_full(method):
    # 以method参数为基础 创建新函数 包含method原有的参数
    def new_method(*args, **kwargs):  # *args,**kwargs可以描述所有的参数形式
        print("method new being.....")
        return_value = method(*args, **kwargs)  # 使用闭包结果函数时 将参数原样传递给被包装的函数
        print("method new end.....")
        # 新函数应该返回被包装函数的返回值
        return return_value

    return new_method


# 调用生成的新函数
result = create_new_method_full(set_age)
return_value = result(100)  # 根据原函数的参数需求传递参数
print(return_value)
result = create_new_method_full(set_age_name)
return_value = result(age=100, name='jack')  # 根据原函数的参数需求传递参数
print(return_value)


# 4 对上述闭包函数的调用进行简化 以装饰器模式对原函数进行装饰
@create_new_method_full
def set_age_name_sex(age: int, name: str, sex: str):
    print(f"your age is :{age}")
    print(f"your name is :{name}")
    print(f'your sex is :{sex}')
    return f'age:{age} name:{name} sex:{sex}'


# 直接调用原函数 实际它已经是被装饰之后的结果了
return_value = set_age_name_sex(20, 'jack', 'male')
print(return_value)

print("*"*50)
######################################################################
# 小案例 ：方法传入参数表示年龄，通过闭包实现在调佣该方法前会进行对参数进行年龄范围判断
#         如果年龄判断不合法,抛出异常
def check_age(func):
    def wrapper(*args, **kwargs):
        # 从参数列表中获取 传入的age参数
        if args:
            age = args[0]
        elif kwargs:
            age = kwargs['age']
        # 参数合法 才执行函数
        if age >= 0 and age <= 150:
            return_value = func(*args, **kwargs)
            return return_value
        else:
            #参数错误 则抛出异常
            raise Exception('age must be between 0 and 150')
    return wrapper

@check_age
def my_set_age(age: int):
    print(f"set age is :{age}")

my_set_age(-90)
my_set_age(age=100)
