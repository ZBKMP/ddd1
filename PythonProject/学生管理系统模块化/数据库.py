from 工具 import ConfigUtil,log_decorator
import pymysql
from 实体类 import Stu

# 连接管理类(单例)
class DBUtil:
    # 实现单例模式
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        config_util = ConfigUtil()  # 单例模式 实际只创建了一个对象
        self.__config = config_util.load_config('config.yaml')
        self.__conn = None
        self.__cursor = None

    # 获得连接
    def get_conn(self):
        self.__conn = pymysql.connect(
            # 通过访问配置信息 获取连接数据
            host=self.__config['mysql']['host'],  # 主机地址  localhost 表示本机
            port=self.__config['mysql']['port'],  # mysql的端口
            user=self.__config['mysql']['user'],  # 用户名
            passwd=self.__config['mysql']['passwd'],  # 密码
            database=self.__config['mysql']['database'],
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
    def add(self, stu: Stu):
        conn = None
        try:
            # 获取连接与游标
            conn, cursor = self.__dbUtil.get_conn()
            # 编辑sql语句
            insert_sql = ' insert into stunew(name,age,score) values(%s,%s,%s); '
            # 工具执行语句 结果表示执行的行数
            result = cursor.execute(insert_sql, args=[stu.name, stu.age, stu.score])
            conn.commit()
            return True  # 操作成功 或 失败2
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.__dbUtil.close_conn()

    # 修改
    @log_decorator
    def update(self, stu: Stu):
        conn = None
        try:
            # 获取连接与游标
            conn, cursor = self.__dbUtil.get_conn()
            update_sql = "update stunew set name=%s, age= %s , score=%s  where id = %s"
            # 工具执行语句 结果表示执行的行数
            result = cursor.execute(update_sql, args=[stu.name, stu.age, stu.score, stu.id])
            conn.commit()
            return True  # 操作成功 或 失败
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.__dbUtil.close_conn()

    # 删除
    @log_decorator
    def delete(self, id: int):
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
    def get(self, id: int):
        conn = None
        try:
            conn, cursor = self.__dbUtil.get_conn()
            select_sql = ' select * from stunew where id = %s'
            cursor.execute(select_sql, args=[id])
            # 按ID查询最多仅有一行结果
            row = cursor.fetchone()
            stu = Stu(*row)
            return stu
        except Exception as e:
            raise e
        finally:
            self.__dbUtil.close_conn()

    # 排序
    @log_decorator
    def orderby(self, colname, type):
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
