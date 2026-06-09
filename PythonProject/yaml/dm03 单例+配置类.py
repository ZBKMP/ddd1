# 定义配置工具类 并为其实现单例模式
import yaml

# 配置工具类
class ConfigUtil(object):
    # 实现单例模式
    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance
    # 根据路径加载配置文件 返回字典
    def load_config(self,path):
        with open(path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f) or {}
            return conf # dict

config_util = ConfigUtil()
config = config_util.load_config('config.yaml')
print(config)
config_util = ConfigUtil()
config = config_util.load_config('config.yaml')
print(config)