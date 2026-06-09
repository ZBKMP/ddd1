import logging
import os
from logging.handlers import TimedRotatingFileHandler
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler
from flask import Flask


# 日志初始化函数 关联Flask对象 设置日志相关配置
def init_app(app: Flask):

    # 定位日志文件存储目录的路径
    # os.getcwd() 获取当前位置的根路径
    log_folder = os.path.join(os.getcwd(), 'storage','log')
    # 目录如果不存在 则创建
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    # 定位每日日志文件路径
    log_file = os.path.join(log_folder, 'app.log')

    # 使用 TimedRotatingFileHandler 实现将每天的日志内容保存到专属文件
    # 每隔一天(0点后),生成新app.log,原文件改名加上日期后缀
    # handler = TimedRotatingFileHandler()

    # 5 运维优化配置:使用concurrent_log_handler替换内置处理器
    handler = ConcurrentTimedRotatingFileHandler(
        filename=log_file,
        when='midnight', # 生成新文件的时间点
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )

    # 定义日志输出格式
    formatter = logging.Formatter(
        "[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s]: %(message)s"
    )
    handler.setFormatter(formatter)

    # 处理文件日志输出
    # 规定日志级别 高于该级别的日志才会记录
    # handler.setLevel(logging.DEBUG)
    # 5 运维优化配置:根据不同的环境设置logging根处理器的日志级别
    handler.setLevel(
        logging.DEBUG if app.debug   else logging.WARNING
    )

    # 6 注册日志处理器
    logging.getLogger().addHandler(handler)

    # 7 如果是开发阶段 还可以将日志信息输出到控制台
    if app.debug:
        # 注册一个控制台日志处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)