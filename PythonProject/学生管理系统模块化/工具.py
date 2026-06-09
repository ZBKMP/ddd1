import yaml
import logging
# 配置工具类(单例)
class ConfigUtil(object):
    # 实现单例模式
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    # 根据路径加载配置文件 返回字典
    def load_config(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f) or {}
            return conf  # dict

########################################################################################
# 进行日志配置
# 先加载配置信息
config_util = ConfigUtil()
config = config_util.load_config('config.yaml')
logging.basicConfig(
    # 配置多个日志输出目标
    handlers=[
        # 输出到控制台
        logging.StreamHandler(),
        logging.FileHandler(filename='../学生管理系统/stu_munager_6.log', mode='a+', encoding='utf-8'),
    ],
    level=config['log']['level'],  # 从配置信息中提取日志级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s -%(lineno)d - %(thread)d -%(filename)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
# 创建日志工具
logger = logging.getLogger("stu_manager_log")
# 定义装饰器
def log_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            # 日志输出原函数的参数
            logger.info(f'func_name:{func.__name__} *args: {args} , **kwargs: {kwargs}')
            # 原函数没有处理异常 而是再通过raise抛出异常 这样才能被装饰器捕获该异常
            return_value = func(*args, **kwargs)
            logger.info(f'func_name:{func.__name__} return_value: {return_value}')
            return return_value
        except Exception as e:
            logger.error(f'func_name:{func.__name__} error: {e}')
            # traceback.print_exc()

    return wrapper