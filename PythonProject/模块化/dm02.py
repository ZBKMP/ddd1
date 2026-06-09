# 日期时间模块
from datetime import datetime, timezone, timedelta
from time import time

# 获得当前时间
datetime_now = datetime.now()
print(datetime_now)
datetime_now = datetime.now(timezone(timedelta(hours=8)))  # 当前时区的当前时间
print(datetime_now)
time_now = time()
print(time_now)

# 指定具体的时间
date = datetime(2025, 11, 4, 14, 52, 30)
print(date)

# 获取时间的部分
print(date.year, date.month, date.day, date.hour, date.minute, date.second)  # 各个时间部分
print(date.date(), date.time(), date.weekday())  # 日期部分 时间部分 星期几

# 针对日期数据常用 操作
# 修改日期部分值
print(date.replace(month=12, day=30))  # 修改时间部分,要注意数据范围

# str 与datetime之间的转换
print(date.strftime("%Y年%m月%d日 %H:%M:%S"))  # 日期格式化转换为字符串
date = datetime.strptime("2027-07-16", "%Y-%m-%d")  # 格式化字符串转日期
print(date, type(date))

# 日期的运算
datetime_now = datetime.now()
date_diff = date - datetime_now # 日期之间做减法(同一时区内定义的时间)
print(date_diff,type(date_diff))

# 时间区间
print(date_diff,type(date_diff)) #表示时间区间 n天n小时n分钟n秒
print(date_diff.total_seconds()) #从时间区间中计算出总秒数
print("date_diff",date_diff.days,date_diff.seconds) #时间间隔内的天数 以及余下的秒数

td = timedelta(weeks=1,days=1,hours=1,minutes=1,seconds=1) #自定义时间段
print(td)
print(date+td)#计算 日期时间+时间区间

#小案例   定义函数，根据输入的年月日 获取当天是星期几
#小案例  定义函数根据输入的年月日 计算距今多少天