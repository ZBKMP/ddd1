from wtforms import Field

# 自定义的FlaskForm下的列表数据类型
class ListField(Field):
    """自定义ListField字段，用于存储列表型数据"""
    # 重写父类中的属性 改为list类型
    data: list = None

    # 重写父类中的方法 用于验证传入的数据是否为列表 是则赋值给data属性
    def process_formdata(self, valuelist):
        # 参数数据不为空 且是列表 则赋值给data属性
        if valuelist is not None and isinstance(valuelist, list):
            self.data = valuelist

    def _value(self):
        # 有数据则返回该数据 没有返回空列表
        return self.data if self.data else []


# 自定义的FlaskForm下的字典数据类型
class DictField(Field):
    """自定义dict字段 用于存储字典型数据"""
    data: dict = None

    def process_formdata(self, valuelist):
        # 参数数据不为空 且valuelist第0个元素是字典 将valuelist第0个元素赋值给data属性
        if valuelist is not None and len(valuelist) > 0 and isinstance(valuelist[0], dict):
            self.data = valuelist[0]

    def _value(self):
        # 有数据则返回该数据 没有返回None
        return self.data