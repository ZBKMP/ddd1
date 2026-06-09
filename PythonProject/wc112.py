#流程控制 --条件判断语句
'''
1.条件判断
if 条件（比较操作OR加上逻辑操作符 得到一个bool值）

'''
'''
#int整数,input用于从用户获取输入
lvl =int(input("输入等级"))
#等级在180以上才算高级玩家
if lvl >= 180:
    print("等级符合")
'''
'''
#等级在180以上or1000点卷进入
lvl =int(input('你的等级'))
Points =int(input('点卷数量'))
if lvl >= 180 and Points >= 1000:
    print("进去吧")
if lvl < 180 or Points < 1000:
    print("不让进")
'''
'''
# and or 实现短路
bool_value =  1==1 and print('11and')
bool_value =  1==1 or print('11or')

bool_value =  1==0 and print('11and2')
bool_value =  1==0 or print('11or2')
'''
'''
#not 取反
lvl =180
print(not bool_value)
if not lvl >180:
    print('未达到lv')
'''
'''
2 条件选择
if条件：条件成立则执行的代码
else：条件不成立则执行的代码
'''
'''
lvl =int(input('你的等级'))
if lvl >180:
    print('进入副本')
else:
    print('请出去')
'''
'''
3.多重else if 条件选择
else：多重条件均不满足执行的代码
'''
'''
lvl = int(input("输入你的lv"))
if lvl>= 180:
    print('进阶')
elif lvl>= 150:
    print('高级')
elif lvl>= 100:
    print('普通')
else:
    print('去升级!')
'''
# 4 条件语句的嵌套
#
lvl =int(input('你的lv'))
Points =int(input('你的点卷'))
if lvl >= 180:
    pass
else:
    print('去升级!')