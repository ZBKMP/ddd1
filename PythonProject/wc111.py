# print 将内容输出到控制台
print("hello world")
print("hello world", 123, 124.151, sep=" * ", end="~~~~~\n")
print("-_-")
# 定义变量
name = 'Jack'
firstName = 'john'
age = 18
print(name, age)
# python弱类型语言 不限定数据输出
num1 = 1
print(num1, type(num1))
num2 = 1.11
print(num2, type(num2))
num3 = True
print(num3, type(num3))
num3 = False
print(num3, type(num3))

str_1 = "呵呵呵"
print(str_1, type(str_1))
str_2 = '''
随便写点啥
啊啊啊1
啊啊啊2
'''
print(str_2, type(str_2))

# 多变量字符串
name = "abb"
occ = "新手"
lvl = 188
is_ban = False
id = 6
Hp = 50000
Mp = 20000
# 字符串占位
print("姓名：%s 职业：%s 等级：%d 封禁：%d 编号：%03d 血量：%.0f 蓝量：%.0f" % (name, occ, lvl, is_ban, id, Hp, Mp))
# 格式化输出
print(f"姓名：{name} 职业：{occ} 等级：{lvl} 封禁：{is_ban} 编号：{id} 血量：{Hp} 蓝量：{Mp}")
# format 格式化输出
print("姓名: {0} 职业:{1} 等级：{2} 封禁：{3} 编号：{4} 血量：{5} 蓝量：{6}".format(name, occ, lvl, is_ban, id, Hp, Mp))

# 字符串 数据保存二进制模式 不支持文字
byte_str = b'emmmmm110'
print(byte_str)
str_1 = 'emmm一缪!'
byte_str = str_1.encode('utf-8')  # 用encode将str编码字节串
print(byte_str)
str_1 = byte_str.decode('utf-8')  # 解码
print(str_1)

# 操作符
# 1算术操作符 + - * / // % ** +-
k1 = 20
k2 = 6
result = k1 + k2  # result 结果 type类型
print(result, type(result))
result = (2 ** 2 + 4 / (3 - 1))
print(result)
#+=
lvl=188
lvl += 10
print(lvl)

lvl %= 7
print(lvl)

#赋值操作符，从右往左
k=r=v=3
print(k, r, v)

#比较操作符 <>=
lvl = 188
result =lvl >187
print(result)

#逻辑操作符 and or not 与或非
'''
#输入函数 input 输入内容都是字符串
name = input("输入名称")
lvl = input("输入等级")
occ = input("输入职业")
print(f"名称：{name} 等级：{lvl} 职业：{occ}")
'''
#多种数据类型转换 int？-->int value:值
value =int("111")
print(value)
value =int(13.12)
print(value)
value =int(False)
print(value)

#str?-->str type类型
value = str(True)
print(value,type(value))

#bool？-->str
value = bool(None) #非0（包括空）都为True
print(value,type(value))

#单字符->int ASCII码
ascii_code = ord("a") #内置函数，用于获取字符的码点
print(ascii_code)
#ascii->char 字符就是长度为 1 的字符串
char = chr(ascii_code)
print(char)



