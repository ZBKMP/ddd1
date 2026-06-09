# 不适用config 而使用函数式处理日志输出
'''
步骤：
    1、创建记录器（logging.getLogger），设置日志级别（后面的处理器的日志输入不能低于记录起的日志设计等级）
        处理器必须附加到记录器才能工作，但记录器可独立存在
        应用程序 → Logger → Handler → 输出目标
    2、创建想要输出到哪个平台（文件还是控制台）
        控制台：StreamHandler
        文件：FileHandler
    3、# 创建格式化器 Formatter
    4、将格式化器添加到处理器（FileHandler或StreamHandler）
    5、将处理器添加到记录器
'''
import logging
#1 直接创建日志工具
logger = logging.getLogger('mylog')
#级别
logger.setLevel(logging.DEBUG)
#创建输出的handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARN)
file_handler = logging.FileHandler(filename='demo03_log.log', encoding='utf-8', mode='a')
file_handler.setLevel(logging.DEBUG)
#设置日志输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
#5 handler与logger绑定
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.debug('调试 message')
logger.info('信息 message')
logger.warning('警告 message')
logger.error('错误 message')
logger.critical('严重错误 message')
