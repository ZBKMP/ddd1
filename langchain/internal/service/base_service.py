from typing import Any, Optional

from internal.exception import FailException
from pkg.sqlalchemy import SQLAlchemy


class BaseService:
    """基础服务，完善数据库的基础增删改查功能，简化代码"""
    db: SQLAlchemy

    # 通用的添加方法 传入db.Model类以及要添加的数据 ，返回db.Model对象(填充了ID)
    def create(self, model_class: Any, **kwargs) -> Any:
        """根据传递的模型类+键值对信息创建数据库记录"""
        with self.db.auto_commit():
            # 通过类 以及传入的数据创建对象
            model_instance = model_class(**kwargs)
            self.db.session.add(model_instance)
        return model_instance

    # delete单个数据 model_instance:Model对象
    def delete(self, model_instance: Any) -> Any:
        """根据传递的模型实例删除数据库记录"""
        with self.db.auto_commit():
            self.db.session.delete(model_instance)
        return model_instance

    # update单个数据  model_instance:Model对象  kwargs:要修改的数据(属性名:属性值)
    def update(self, model_instance: Any, **kwargs) -> Any:
        """根据传递的模型实例+键值对信息更新数据库记录"""
        with self.db.auto_commit():
            # 循环遍历传入的所有关键字参数
            for field, value in kwargs.items():
                # 对照kwargs 检索model_instance内的属性 进行修改
                if hasattr(model_instance, field):
                    # setattr修改对象中对应的属性
                    setattr(model_instance, field, value)
                else:  # 属性不匹配 则无法更新 抛出异常
                    raise FailException("更新数据失败")
        return model_instance

    # get单个数据  model:Model类名  primary_key:主键值
    def get(self, model: Any, primary_key: Any) -> Optional[Any]:
        """根据传递的模型类+主键的信息获取唯一数据"""
        return self.db.session.query(model).get(primary_key)
