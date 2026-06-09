# 日志输出到文件
import logging



# 1 配置文件输出
logging.basicConfig(
  level=logging.DEBUG,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s -%(lineno)d - %(thread)d -%(filename)s',
  datefmt='%Y-%m-%d %H:%M:%S',
  filename = 'dm02.log',
  filemode='a',
  encoding='utf-8'
)
logger=logging.getLogger('mylog')
logger.debug('调试异常')
logger.info('一般异常')
logger.warning('警告异常')
logger.error('错误')
logger.critical('严重错误')
logger.fatal('程序崩溃')