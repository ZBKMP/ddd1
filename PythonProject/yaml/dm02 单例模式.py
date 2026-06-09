# 单例模式singleton : 类在整个项目运行过程中 仅能创建唯一对象
# 面向对象设计模式 : 23种

'''
在Python中，单例模式（Singleton Pattern）是一种常用的软件设计模式，
它确保一个类只有一个实例，并提供一个全局访问点。
以下是详细解释：
‌核心目的‌：
控制实例数量：确保类在整个程序运行期间只有一个实例
全局访问：提供统一的访问入口

    __new__: 构造函数 负责创建类的实例（对象），分配内存空间并返回新创建的实例。
    它是一个静态方法（虽然不需要显式声明），第一个参数是cls（类本身）

    __init__:负责初始化实例，设置实例的属性或执行其他初始化操作。
    它是一个实例方法，第一个参数是self（由__new__创建的实例）
    先调用__new__ 再用__init__初始化
'''

class Human(object):
    #单例模式: 定义一个类属性 用于存储__new__对象
    __instance = None

    def __new__(cls, *args, **kwargs):
        print('Human 构造方法........ new方法负责创建对象')
        # 如果重写了 __new__方法 一定要调用父类的__new__方法来创建对象

        # 单例模式 将new创建的对象存储于类属性__instance
        # 先必须判断 __instance是否为空,只有在其为空的前提下才创建对象,否则直接返回
        if cls.__instance is None :
             cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, name, age):
        print("Human 初始化方法......")
        self.name = name
        self.age = age

human = Human("jack", 18)
other = Human("yoyo", 20)

print(human == other)
print(human is other)

print(human.name,human.age)