import uuid
from dataclasses import dataclass

from inject_test import inject
from internal.model import App
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class AppService:
    """ app模块中 所有的业务操作写在此类中 """

    # 依赖注入
    db: SQLAlchemy  # 已经实现了SQLAlchemy类与db对象的绑定

    # 测试 添加操作
    def create_app(self) -> App:
        with self.db.auto_commit():
            app = App(
                name="测试AI机器人_3",
                account_id=uuid.uuid4(),
                icon="http://image.cn/xxx.jpg",
                description="这是一个简单的聊天机器人",
            )
            self.db.session.add(app)
            # 添加成功之后 生成的ID会存到当前对象中
            return app

    # 测试根据ID获取APP 注意get获取不到会抛异常
    def get_app(self, id: uuid.UUID) -> App:
        app = self.db.session.query(App).get(id)
        return app

    # 测试修改
    def update_app(self, id: uuid.UUID) -> App:
        # 重写了SQLAlchemy之后,使用上下文方式实现自动提交
        with self.db.auto_commit():
            app = self.get_app(id)
            app.name = "Updated聊天机器人"
            return app

    # 测试删除
    def delete_app(self, id: uuid.UUID) -> App:
        # 重写了SQLAlchemy之后,使用上下文方式实现自动提交
        with self.db.auto_commit():
            app = self.get_app(id)
            self.db.session.delete(app)
            return app
