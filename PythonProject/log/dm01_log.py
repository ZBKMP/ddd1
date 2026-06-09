#日志操作基本概念
import  logging
#配置日志输出
logging.basicConfig(
    level=logging.DEBUG,# 仅会输出该级别及以上的日志信息
    # 设置日志输出的格式
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s -%(lineno)d - %(thread)d -%(filename)s',  # 设置日志输出的格式
     # 设置日志输出的时间格式
    datefmt='%Y-%m-%d %H:%M:%S',
)
#使用 logger实现日志输出
logger = logging.getLogger('mylog')
# 使用各种级别输出日志
logger.debug('debug message')
logger.info('info message')
logger.warning('warning message')
logger.error('error message')
logger.critical('critical message')
