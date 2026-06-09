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