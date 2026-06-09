# 使用 yaml 文件进行项目配置
# python  -m pip install pyyaml  -i https://pypi.tuna.tsinghua.edu.cn/simple
# python -m pip install pyyaml -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com

import yaml

with open('config.yaml', 'r', encoding='utf-8') as f:
    # 加载yaml配置文件的配置信息 结果为字典 每个配置称为子字典
    conf = yaml.safe_load(f) or {}
    print(conf)
    print(conf['mysql']['database'])
    print(conf['log']['level'])
