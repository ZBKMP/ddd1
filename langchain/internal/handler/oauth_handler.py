from dataclasses import dataclass
from injector import inject
from internal.schema import AuthorizeReq, AuthorizeResp
from internal.service import OAuthService
from pkg.response import success_json, validation_error_json


@inject
@dataclass
class OAuthHandler:
    # 依赖注入
    oauth_service: OAuthService

    # 根据传递的提供商名字获取授权认证重定向地址
    def provider(self, provider_name: str):
        """根据传递的提供商名字获取授权认证重定向地址"""
        # 1.调用业务层 根据provider_name获取授权服务提供商对象
        oauth =self.oauth_service.get_oauth_by_provider_name(
            provider_name=provider_name
        )
        # 2 从第三方登录工具对象中 获取授权认证重定向地址
        redirect_url = oauth.get_authorization_url()

        return success_json(data={"redirect_url":redirect_url})

    # 根据传递的提供商名字+code获取第三方授权信息
    def authorize(self, provider_name: str):
        """根据传递的提供商名字+code获取第三方授权信息"""
        # 1.提取请求数据并校验 必须包含code
        req = AuthorizeReq()
        if not req.validate():
            return validation_error_json(req.errors)

        # 2.调用服务实现登录账号
        llmops_token_dict = self.oauth_service.oauth_login(
            provider_name=provider_name,
            code=req.code.data
        )

        # 3 响应结果
        return success_json(data =AuthorizeResp().dump(llmops_token_dict))
