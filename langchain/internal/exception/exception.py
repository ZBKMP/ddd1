from dataclasses import field
from typing import Any

from pkg.response import HttpCode


# 程序中抛出自定义异常类对象,要实现和response输出相同的效果
class CustomException(Exception):
    """基础自定义异常信息类"""
    code: HttpCode = HttpCode.FAIL  # 业务状态码
    message: str  # 异常消息信息
    data: Any = field(default_factory=dict) # 数据 默认值为{}

    # 仅传递 message 与 data
    def __init__(self,message:str=None,data:Any=None):
        super().__init__()
        self.message = message
        self.data = data


class FailException(CustomException):
    """通用失败异常"""
    pass

class  NotFoundException(CustomException):
    """未找到数据异常"""
    code = HttpCode.NOT_FOUND

class UnauthorizedException(CustomException):
    """未授权异常"""
    code = HttpCode.UNAUTHORIZED

class ForbiddenException(CustomException):
    """无权限异常"""
    code = HttpCode.FORBIDDEN

class ValidationException(CustomException):
    """数据验证异常"""
    code = HttpCode.VALIDATION_ERROR



