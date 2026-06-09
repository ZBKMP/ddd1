# 为每个CRUD方法增加日志输出:调用函数使得参数 ,函数的返回值,过程中的异常信息
# 使用装饰器去实现日志输出,为每个函数增加通用的日志输出逻辑

# 把数据库连接 日志级别信息写在配置文件种 通过配置类的加载配置方法去读取

import sys
import pymysql
import logging

# 先进行日志配置
logging.basicConfig(
    # 配置多个日志输出目标
    handlers=[
        # 输出到控制台
        logging.StreamHandler(),
        logging.FileHandler(filename='demo05_log_decorator.log', mode='a+', encoding='utf-8'),
    ],
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s -%(lineno)d - %(thread)d -%(filename)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
# 创建日志工具
logger = logging.getLogger("stu_manager_log")
# 定义装饰器
def log_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            # 日志输出原函数的参数
            logger.info(f'func_name:{func.__name__} *args: {args} , **kwargs: {kwargs}')
            # 原函数没有处理异常 而是再通过raise抛出异常 这样才能被装饰器捕获该异常
            return_value = func(*args, **kwargs)
            logger.info(f'func_name:{func.__name__} return_value: {return_value}')
            return return_value
        except Exception as e:
            logger.error(f'func_name:{func.__name__} error: {e}')
            #traceback.print_exc()
    return wrapper


##############################################################################################

# 定义学生类 实体类
class Stu:
    def __init__(self, id, name, age, score):
        self.id = id
        self.name = name
        self.age = age
        self.score = score

    def __str__(self):
        return f'stu_id:{self.id} stu_name:{self.name} stu_age:{self.age} stu_score:{self.score}'


###################################################################################################

# 连接管理类
class DBUtil:
    def __init__(self):
        self.__conn = None
        self.__cursor = None

    # 获得连接
    def get_conn(self):
        self.__conn = pymysql.connect(
            host='127.0.0.1',  # 主机地址  localhost 表示本机
            port=3306,  # mysql的端口
            user='root',  # 用户名
            passwd='root',  # 密码
            database='sx',
            charset='utf8'
        )
        self.__cursor = self.__conn.cursor()
        return self.__conn, self.__cursor  # 将两个对象合并成一个元组返回

    # 关闭连接
    def close_conn(self):
        if self.__conn is not None and self.__cursor is not None:
            self.__cursor.close()
            self.__conn.close()


###########################################################################################
# 数据操作类
class StuCRUD:
    def __init__(self):
        # 每个操作都需要获取连接 以及关闭连接 将DBUtil定义成属性
        self.__dbUtil = DBUtil()

    # 添加 以Stu对象作为参数
    @log_decorator
    def add(self, stunew: Stu):
        conn = None
        try:
            # 获取连接与游标
            conn, cursor = self.__dbUtil.get_conn()
            # 编辑sql语句
            insert_sql = ' insert into stunew(name,age,score) values(%s,%s,%s); '
            # 工具执行语句 结果表示执行的行数
            result = cursor.execute(insert_sql, args=[stunew.name, stunew.age, stunew.score])
            conn.commit()
            return True  # 操作成功 或 失败2
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.__dbUtil.close_conn()


    # 修改
    @log_decorator
    def update(self, stunew: Stu):
        conn = None
        try:
            # 获取连接与游标
            conn, cursor = self.__dbUtil.get_conn()
            update_sql = "update stunew set name=%s, age= %s , score=%s  where id = %s"
            # 工具执行语句 结果表示执行的行数
            result = cursor.execute(update_sql, args=[stunew.name, stunew.age, stunew.score, stunew.id])
            conn.commit()
            return True  # 操作成功 或 失败
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.__dbUtil.close_conn()


    # 删除
    @log_decorator
    def delete(self, id:int):
        conn = None
        try:
            # 获取连接与游标
            conn, cursor = self.__dbUtil.get_conn()
            update_sql = "delete from stunew where id = %s"
            # 工具执行语句 结果表示执行的行数
            result = cursor.execute(update_sql, args=[id])
            conn.commit()
            return True  # 操作成功 或 失败
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.__dbUtil.close_conn()


    # 查询(多行)
    @log_decorator
    def query(self):
        conn = None
        stu_list = []
        try:
            conn, cursor = self.__dbUtil.get_conn()
            select_sql = ' select * from stunew'
            cursor.execute(select_sql)
            for row in cursor.fetchall():
                # 每行数据 转为Stu对象 添加到列表中
                stu_list.append(Stu(*row))
        except Exception as e:
            raise e
        finally:
            self.__dbUtil.close_conn()
        return stu_list

    # 查询(按ID)
    @log_decorator
    def get(self,id:int):
        conn = None
        try:
            conn, cursor = self.__dbUtil.get_conn()
            select_sql = ' select * from stunew where id = %s'
            cursor.execute(select_sql, args=[id])
            # 按ID查询最多仅有一行结果
            row = cursor.fetchone()
            stustunew  = Stu(*row)
            return  stustunew
        except Exception as e:
            raise e
        finally:
            self.__dbUtil.close_conn()



    # 排序
    @log_decorator
    def orderby(self,colname,type):
        conn = None
        stu_list = []
        try:
            conn, cursor = self.__dbUtil.get_conn()
            # 直接将排序的列名 以及 排序方向 以字符串的形式拼接到sql语句中
            select_sql = f' select * from stunew order by {colname} {type} '
            cursor.execute(select_sql)
            for row in cursor.fetchall():
                # 每行数据 转为Stu对象 添加到列表中
                stu_list.append(Stu(*row))
        except Exception as e:
            raise e
        finally:
            self.__dbUtil.close_conn()
        return stu_list


#############################################################################################

# 学生管理工具类
class StuManager:

    def __init__(self):
        # 将数据操作类对象 作为属性
        self.__stuCRUD = StuCRUD()

    # 把每个功能封装函数 在菜单中去调用
    def add_student(self):
        # 添加学生 先进行数据输入
        stu_name = input("请输入学生姓名:")
        stu_age = int(input("请输入学生年龄:"))
        stu_score = float(input("请输入学生成绩:"))
        # 数据封装为对象
        stunew = Stu(0, stu_name, stu_age, stu_score)
        result = self.__stuCRUD.add(stunew)
        if result:
            print("数据添加成功")
        else:
            print("数据添加失败")

    def show_students(self):
        # 展示所有学生信息
        print("所有学生信息如下:")
        stu_list = self.__stuCRUD.query()
        for stunew in stu_list:
            print(stunew)

    def del_student(self):
        stu_name = input("请输入你要删除的学生ID:")
        result = self.__stuCRUD.delete(int(stu_name))
        if result:
            print("数据删除成功")
        else:
            print("数据删除失败")

    def update_student(self):
        id = input("请输入你要修改的学生ID:")
        name = input("请输入要修改的姓名:")
        age = int(input("请输入要修改的年龄:"))
        score = float(input("请输入要修改的分数:"))
        stunew  = Stu(id, name, age, score)
        result = self.__stuCRUD.update(stunew)
        if result:
            print("数据修改成功")
        else:
            print("数据修改失败")

    def sort_student(self, colname, type):
        stu_list = self.__stuCRUD.orderby(colname, type)
        for stunew in stu_list:
            print(stunew)

    def show_student(self):
        id = input("请输入你要修改的学生ID:")
        stunew = self.__stuCRUD.get(int(id))
        print(stunew)

    # 定义函数 显示菜单内容
    def show_menu(self):
        str_memu = '''
        1) 添加学生信息
        2) 显示所有学生信息
        3) 删除学生信息
        4) 修改学生信息
        5) 按年龄高-低展示学生信息
        6) 按年龄低-高展示学生信息
        7) 按成绩高-低展示学生信息
        8) 按成绩低-高展示学生信息
        9) 按ID查询单个数据
        0) 退出系统
        '''
        print(str_memu)
        choice = int(input("请输入你需要的功能:"))
        if choice == 1:
            self.add_student()  # 添加学生
        elif choice == 2:
            self.show_students()  # 显示所有学生
        elif choice == 3:
            self.del_student()  # 删除学生
        elif choice == 4:
            self.update_student()  # 修改学生
        elif choice == 5:
            self.sort_student('age','desc')  # 按照年龄降序排序
        elif choice == 6:
            self.sort_student('age','asc')  # 按照年龄升序排序
        elif choice == 7:
            self.sort_student('score','desc')  # 按照成绩降序排序
        elif choice == 8:
            self.sort_student('score','asc')  # 按照年龄生序排序
        elif choice == 9:
            self.show_student()
        elif choice == 0:
            # 结束程序
            sys.exit(0)


# 执行程序
stu_manager = StuManager()  # 创建管理工具对象
while True:
    stu_manager.show_menu()  # 调用对象的显示菜单方法