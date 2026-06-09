from enum import Enum


# 通过枚举类 规范每次接口响应结果中 code
class HttpCode(str,Enum):
    """ http基础业务状态码 """
    SUCCESS = "success",  # 成功状态
    
    FAIL = "fail",  # 失败状态
    NOT_FOUND = "not_found",  # 未找到
    UNAUTHORIZED = "unauthorized",  # 未授权
    FORBIDDEN = "forbidden",  # 无权限
    VALIDATION_ERROR = "validation_error",  # 数据验证错误