import urllib.parse

import requests

from . import OAuthUserInfo
from .oauth import OAuth


class GithubOAuth(OAuth):
    """GithubOAuth第三方授权认证类"""
    # GITHUB 跳转授权接口
    _AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    # GITHUB 获取授权令牌接口
    _ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
    # GITHUB 获取用户原始信息接口
    _USER_INFO_URL = "https://api.github.com/user"
    # GITHUB 获取用户邮箱接口
    _EMAIL_INFO_URL = "https://api.github.com/user/emails"

    def get_provider(self) -> str:
        """获取服务提供者对应的名字"""
        return "github"

    def get_authorization_url(self) -> str:
        """获取第三方授权认证的URL地址"""
        # 参数字典
        params = {
            # 客户端id 例如env配置的:GITHUB_CLIENT_ID
            "client_id": self.client_id,
            # 重定向uri 例如env配置的:GITHUB_REDIRECT_URI
            "redirect_uri": self.redirect_uri,
            # 只请求用户的基本信息
            "scope": "user:email"
        }
        return f"{self._AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

    # 根据传入的code代码(GITHUB在回调GITHUB_REDIRECT_URI时会传回code)
    # 再向github获取授权令牌
    # 此时必须在GITHUB上登录账号,才能得到该账号的TOKEN令牌
    def get_access_token(self, code: str) -> str:
        """根据传入的code代码获取第三方的授权令牌"""
        # 1.组装请求参数数据
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
        }

        # 2.发起post请求并获取相应的数据
        resp = requests.post(
            self._ACCESS_TOKEN_URL,
            data=data,
            headers={"Accept": "application/json"}
        )
        # 如果响应状态码不是200 会抛出异常
        resp.raise_for_status()
        # 响应结果转换为JSON_dict
        resp_json = resp.json()

        # 3.从github响应的结果中 提取access_token对应的token数据
        access_token = resp_json.get("access_token")
        if not access_token:
            raise ValueError(f"Github OAuth授权失败: {resp_json}")
        return access_token

    # 根据GITHUB传回的token获取GITHUB中已登录账号的OAuth原始信息(用户数据和用户邮箱)
    def get_raw_user_info(self, token: str) -> dict:
        """根据传入的第三方的授权令牌 获取OAuth原始字典信息(payload) """
        # 1.组装请求头数据 按GITHUB要求组装Authorization请求头
        headers = {"Authorization": f"token {token}"}

        # 2.发起get请求获取用户数据
        resp = requests.get(
            self._USER_INFO_URL,
            headers=headers
        )
        resp.raise_for_status()
        raw_info = resp.json() # 字典(id login)
        print(f"GITHUB user info:{raw_info}")

        # 3.发起get请求获取用户邮箱
        email_resp = requests.get(
            self._EMAIL_INFO_URL,
            headers=headers
        )
        email_resp.raise_for_status()
        email_info = email_resp.json()# 列表[字典]
        print(f"GITHUB email info :{email_info}")

        # 4.提取邮箱数据  next获取可迭代对象的下一个元素,若没有内容则返回None
        # 提取GITHUB用户邮箱信息中的primary主邮箱地址
        primary_email = next(
            (email for email in email_info if email.get("primary",None)),
            None,
        )
        # 5 合并用户数据和邮箱信息为字典,并返回
        return {
            **raw_info,
            "email": primary_email.get("email",None),
        }

    # 将OAuth原始信息转换成OAuthUserInfo
    def _transform_user_info(self, raw_info: dict) -> OAuthUserInfo:
        """将OAuth原始字典信息转换成OAuthUserInfo"""
        # 1.提取邮箱，如果不存在设置一个默认邮箱(虚拟的邮箱地址)
        email = raw_info.get("email")
        if not email :
            email = f"{raw_info.get('id')}+{raw_info.get('login')}@user.no-reply@github.com"
                                            #github传回的用户信息中 用户名标记为login
        # 2 返回对象
        return  OAuthUserInfo(
            id = str(raw_info.get("id")),
            name = str(raw_info.get("login")), #github传回的用户信息中 用户名标记为login
            email = str(email),
        )
