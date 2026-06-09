#导入pymysql模块 执行mysql访问
import pymysql
import traceback



#执行增删改查操作
#创建连接对象

conn=None
cursor=None
'''
try:
    conn = pymysql.connect(
        host='localhost',  # 主机地址
        port=3306,  # 端口
        user='root',  # 用户名
        passwd='root',
        database='sx',
        charset='utf8'
    )
    # 得到操作工具
    cursor = conn.cursor()
    print(conn)
    print(cursor)
    # 添加操作
    insert_sql = 'insert into student(stu_no,stu_name,stu_sex,stu_age,stu_birthday,stu_score) values(%s,%s,%s,%s,%s,%s);'
    # 工具执行语句 结果表示执行的行数
    result = cursor.execute(insert_sql, ['ZB002', 'ZA', 'MAN', 21, '2020-04-07', 81])
    print(result)
    # 增删改之后必须执行事务的提交
    conn.commit()
except Exception as e:#执行出现异常 要回滚事务
    print(e,type(e))
    traceback.print_exc()
    conn.rollback()

finally:
    print("关闭连接")
#关闭连接 以及操作工具
cursor.close()
conn.close()
'''

'''
#2 更新SQL
conn=None
cursor=None

try:
    conn = pymysql.connect(
        host='localhost',  # 主机地址
        port=3306,  # 端口
        user='root',  # 用户名
        passwd='root',
        database='sx',
        charset='utf8'
    )
    # 得到操作工具
    cursor = conn.cursor()
    print(conn)
    print(cursor)
    # 更新SQL语句 根据ID为条件 修改其他所有列
    update_sql = 'update student set stu_no=%s,stu_name=%s,stu_sex=%s,stu_age=%s,stu_birthday=%s,stu_score=%s where id=%s'
    # 工具执行语句 结果表示执行的行数
    result = cursor.execute(update_sql, ['ZB001', 'ZA', 'MAN', 21,'2020-04-05', 80,1])
    print(result)
    # 增删改之后必须执行事务的提交
    conn.commit()
except Exception as e:#执行出现异常 要回滚事务
    print(e,type(e))
    traceback.print_exc()
    conn.rollback()

finally:
    print("关闭连接")
#关闭连接 以及操作工具
cursor.close()
conn.close()
'''

'''
#删除SQL
conn=None
cursor=None

try:
    conn = pymysql.connect(
        host='localhost',  # 主机地址
        port=3306,  # 端口
        user='root',  # 用户名
        passwd='root',
        database='sx',
        charset='utf8'
    )
    # 得到操作工具
    cursor = conn.cursor()
    print(conn)
    print(cursor)
    # 更新SQL语句 根据ID为条件 删除指定行数据
    delete_sql = 'delete from student   where id=%s'
    # 工具执行语句 结果表示执行的行数
    result = cursor.execute(delete_sql, [1])
    print(result)
    # 增删改之后必须执行事务的提交
    conn.commit()
except Exception as e:#执行出现异常 要回滚事务
    print(e,type(e))
    traceback.print_exc()
    conn.rollback()

finally:
    print("关闭连接")
#关闭连接 以及操作工具
cursor.close()
conn.close()
'''

'''
#查询SQL
try:


 conn = pymysql.connect(
        host='localhost',  # 主机地址
        port=3306,  # 端口
        user='root',  # 用户名
        passwd='root',
        database='sx',
        charset='utf8'
 )
 with conn as cn:
    # 得到操作工具
    cursor = conn.cursor()
    #查询语句
    select_stc = 'select * from student '
    result=cursor.execute(select_stc)
    print(result) #结果行数

    #数据保存cursor内
    for row in cursor.fetchall():
        print(row) #row类型为tuple

except Exception as e:
  print(e,type(e))
finally:
  print('其他')
'''

# 根据id查询单条数据
try:


 conn = pymysql.connect(
        host='localhost',  # 主机地址
        port=3306,  # 端口
        user='root',  # 用户名
        passwd='root',
        database='sx',
        charset='utf8'
 )
 with conn as cn:
    # 得到操作工具
    cursor = conn.cursor()
    #查询语句
    select_stc = 'select * from student where id=%s '
    result=cursor.execute(select_stc, [4 ])
    print(result) #结果行数
#根据ID查询必然只有一行数据,不用循环
    row = cursor.fetchone()
    print(row)
    cursor.close()

except Exception as e:
  print(e,type(e))
finally:
  print('其他')




