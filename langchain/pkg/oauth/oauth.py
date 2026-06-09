from abc import ABC, abstractmethod
from dataclasses import dataclass


# OAuth用户基础信息(第三方授权登录)
@dataclass
class  OAuthUserInfo:
    """OAuth用户基础信息，只记录id/name/email"""
    id: str
    name: str
    email: str


@dataclass
class OAuth(ABC):
    """第三方OAuth授权认证基础类"""
    # 客户端id 例如env配置的:GITHUB_CLIENT_ID
    client_id: str
    # 客户端秘钥 例如env配置的:GITHUB_CLIENT_SECRET
    client_secret: str
    # 重定向uri 例如env配置的:GITHUB_REDIRECT_URI
    redirect_uri: str

    # 抽象方法
    @abstractmethod
    def get_provider(self) -> str:
        """获取服务提供者对应的名字"""
        pass

    @abstractmethod
    def get_authorization_url(self) -> str:
        """获取第三方授权认证的URL地址"""
        pass

    @abstractmethod
    def get_access_token(self, code: str) -> str:
        """根据传入的code代码获取第三方的授权令牌"""
        pass

    @abstractmethod
    def get_raw_user_info(self, token: str) -> dict:
        """根据传入的第三方的授权令牌 获取OAuth原始字典信息(payload) """
        pass

    # 抽象方法
    @abstractmethod
    def _transform_user_info(
                self, raw_info: dict
        ) -> OAuthUserInfo:
            """将OAuth原始字典信息转换成OAuthUserInfo"""
            pass


    # 实例方法
    def get_user_info(
            self, token: str
    ) -> OAuthUserInfo:
        """根据传入的token获取OAuthUserInfo信息"""
        # 先根据传入的token获取OAuth原始信息
        raw_info = self.get_raw_user_info(token)
        # 再将OAuth原始信息转换成OAuthUserInfo
        return self._transform_user_info(raw_info)