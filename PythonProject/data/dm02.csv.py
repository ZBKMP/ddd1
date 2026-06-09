# 对csv文件进行读写操作 *.csv 类似于电子表格文本文件

import csv

# 1将内容写入到csv文件内
# newline='' 避免每行之间空行
with open(file='txt/data.csv', mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'age', 'score'])
    writer.writerow(['zbk', 22, 59.5])
    writer.writerow(['zbc', 20, 61.5])

# mode = a 追加模式
with open(file='txt/data.csv', mode='a', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    # 二维列表 表示有多行数据需要一次性写入文件中
    list_datas = [
        ['kmp', 25, 70.5],
        ['cs', 26, 63.5],
    ]
    # 一次性写入多行
    writer.writerow(list_datas)
##########################################

# 2 读取csv文件的内容
with open(file='txt/data.csv', mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    # 文件的每行内容已经包含在reader中
    # 读取的结果 每行自动包装为list 元素均为str
    for row in reader:
        print(row, type(row))

##############################################

# 以字典为单位 对csv文件进行读写操作
with open(file='txt/data.csv', mode='w', encoding='utf-8',newline='') as f:
    # fieldnames 会在结果的第一行 生成列名 会作为字典的key
    writer = csv.DictWriter(f, fieldnames=['name', 'age', 'score'])
    writer.writeheader()  # 写一行作为表头
    # 每行以字典为单位写入
    writer.writerow({'name': 'kmp', 'age': 21, 'score': 59.5})
    writer.writerow({'name': 'kma', 'age': 22, 'score': 58.5})
# 追加模式写入 一次写入多个数据
with (open(file='txt/data.csv', mode='a', encoding='utf-8',newline='') as f):
    writer = csv.DictWriter(f, fieldnames=['name', 'age', 'score'])
    list_dicts = [
          {'name': 'sb', 'age': 19, 'score': 70.5},
          {'name': 'sa', 'age': 18, 'score': 62.5}
    ]
    writer.writerows(list_dicts)

#以dict为单位 从csv读取 一定要保证 首行有列名，会将首行的每个列作为key
with (open(file='txt/data.csv', mode='r', encoding='utf-8',newline='') as f):
    reader = csv.DictReader(f)
    for row in reader:
        #每行读取的结果配合首航的列明 从而生成字典
        print(row, type(row))
