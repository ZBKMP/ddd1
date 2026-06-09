import importlib


# 动态导入模块 以字符串的模式去表示要动态导入的模块
module = importlib.import_module('math')
# 使用动态导入的模块 计算平方根
print(module.sqrt(16))

# 以上代码等同于
# import math
# import time
# print(math.sqrt(16))
# print(time.time())