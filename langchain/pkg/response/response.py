# 规范所有接口响应结果的格式
from dataclasses import dataclass, field
from typing import Any, Union, Generator
from flask import jsonify
from .http_code import HttpCode


@dataclass  # 装饰器 自动生成init函数
class Response(object):
    """基础HTTP接口响应格式"""
    # 响应状态码 默认success
    code: str = "success"
    # 响应文本消息
    message: str = ""
    # 业务响应数据 默认为{} 但使用filed的默认工厂函数产生空字典
    data: Any = field(default_factory=dict)


# 将可能的各种响应模式都定义成方法
def to_json(response:Response = None):
    return jsonify(response)

# 1 所有响应结果包含 data的方法
def success_json(data: Any) :
    return to_json(
        Response(code=HttpCode.SUCCESS, message="", data=data)
    )
def validation_error_json(data: Any):
    return to_json(
        Response(code=HttpCode.VALIDATION_ERROR, message="", data=data)
    )

# 2 所有响应结果包含 msg的方法
def success_message(msg:str):
    return to_json(
        Response(code=HttpCode.SUCCESS, message=msg, data=None)
    )

def fail_message(msg:str):
    return to_json(
        Response(code=HttpCode.FAIL, message=msg, data=None)
    )
def not_found_message(msg:str):
    return to_json(
        Response(code=HttpCode.NOT_FOUND, message=msg, data=None)
    )
# 填充代码 定义方法 放回他各种错误情况下的响应结果 结果中仅包含 message即可

#########################################################
from flask import Response as FlaskResponse
from flask import stream_with_context


# 统一合并处理 块输出 以及 流式事件 输出
# 以 自定义Response对象 或者是 生成器 作为参数,返回Flask中的Response对象
def compact_generate_response(
        response: Union[Response, Generator]
) -> FlaskResponse:
    """统一合并处理块输出以及流式事件输出"""
    # 1.检测下是否为块输出(response参数为自定义Response类型),是则直接输出结果
    if isinstance(response, Response):
        return to_json(response)
    else:
        # 2.response参数为生成器类型，代表本次响应需要执行流式事件输出
        # 构建generate函数,返回一个生成器,以传入的生成器作为返回数据源
        def generate() -> Generator:
            yield from response

        # 3.返回携带上下文的流式事件输出FlaskResponse对象
        # stream_with_context 将生成器函数做为响应内容
        return FlaskResponse(
            response=stream_with_context(generate()),
            mimetype="text/event-stream",  # mimetype 为流式输出
            status=200,
        )


