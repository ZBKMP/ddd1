from celery import Task, Celery
from flask import Flask

# 将Celery对象与Flask对象进行绑定
def init_app(app:Flask):
    # 1 定义Flask环境下的任务类
    class FlaskTask(Task):
        def __call__(self,*args,**kwargs):
            # 代表着在Flask上下文环境下执行异步任务,才可以访问flask配置,db数据库等内容
            with app.app_context():
                return self.run(*args,**kwargs)

    # 2 创建Celery服务对象 并加载相关配置信息
    celery_app = Celery(app.name,task_cls=FlaskTask)
    celery_app.config_from_object(app.config['CELERY'])
    celery_app.set_default() # 如果没有获取到参数 则使用默认值

    # 3 将celery_app对象与Flask对象绑定
    app.extensions['celery'] = celery_app
