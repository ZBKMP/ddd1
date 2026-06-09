import logging
import time
from socket import SocketIO
from uuid import UUID
from celery import shared_task
from flask import current_app  #当前运行的flask应用


# 测试异步任务 定义Celery框架下的异步任务
@shared_task
def demo_task(id:UUID)->str:
    """测试异步任务"""
    logging.info("睡眠5秒")
    time.sleep(5)  # 可以使用time.sleep实现休眠
    logging.info(f"id的值:{id}")
    # 检测异步任务是否运行于Flask上下文之中:测试查看当前flask应用的配置信息
    logging.info(f"配置信息:{current_app.config}")
    return "小白子"