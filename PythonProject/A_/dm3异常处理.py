#程序中的异常处理

#使用 try except else finally 对异常进行处理:自定义错误信息 避免因异常而程序终止
#Exception 异常类 所有常用异常类型的基类
#except 可以写多块 专用于处理一种特定类型的异常
#try把发现的异常 封装到Exception对象 传递到except块中
try:
    n = 100
    num = int(input('输入数字'))
    result = n / num
    print(result)

except ValueError as e:
    print(e)
    print('值错误')
except ZeroDivisionError as e:
    print(e)
    print('除数不能为0')
except Exception as e:#如果上述except没有解决的问题，交给Exception解决
    print(e,type(e))
    print("出现了异常")
else:#没有出现异常 会执行的代码
    print('正常执行')
finally:#无论是否有异常 都会执行的代码
    print('收尾')
print('other')