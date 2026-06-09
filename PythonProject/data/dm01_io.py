# #文件io操作:通过python进行文本文件访问及文件读写操作
# # 从文本文件中读取文件内容
# #file 表示文件路径 mode表示操作模式(r读取 w写 a追加)encoding编码方式
# f=open(file='txt/test.txt', mode='r', encoding='utf-8')
# content = f.read()
# print(content)
# f.close()#在io操作完毕之后 必须关闭读写工具
#
# print('*'*100)
#
# #以行为单位读取文件内容 使用with关键字 省略关闭的操作
# with open(file='txt/test.txt', mode='r', encoding='utf-8') as f:
#     #后续代码需要缩进
#     while True:
#       content = f.readline()
#       if not content:
#           break
#       #文本文件中 每行结束就是 \n,输出时结尾不需要在使用\n
#       print(content,end='')
# print()
# print('*'*100)
# #将整个文件 以行为单位读取 结果生成列表
# with open(file='txt/test.txt', mode='r', encoding='utf-8') as f:
#     contents = f.readlines() #结果为list[]
#     for content in contents:
#         print(content,end='')
# print()

#######################################################

# 从文本文件写入内容 如果文件不存在 会自动创建文件
#mode = w 写入内容 会覆盖原有内容
with open(file='txt/01.txt', mode='w', encoding='utf-8') as f:
    content_01 = '你好 1 wor X \n'
    content_02 = 'hello Y\n'
    f.write(content_01) #-----.write一次写一行文字内容
    f.write(content_02)
# mode = a 追加写入 再原本的内容后追加内容
with open(file='txt/01.txt', mode='a', encoding='utf-8') as f:
        content_01 = '你好 1 wor X 456 \n'
        content_02 = 'hello 2033\n'
        list_content = [content_01, content_02]
        f.writelines(list_content) #----将列表中的每个元素都写入文件
