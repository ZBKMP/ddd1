from dataclasses import dataclass

from flask_login import login_required
from injector import inject

from internal.schema import GetCurrentUserResp, UpdatePasswordReq, UpdateAvatarReq, UpdateNameReq
from internal.service import AccountService
from flask_login import current_user # 获取当前登录的Account信息
from pkg.response import success_json, validation_error_json, success_message


# 账号设置处理器类
@inject
@dataclass
class AccountHandler:
    """账号设置处理器"""
    account_service: AccountService

    # 获取当前登录账号信息方法 必须经过登录之后才可访问
    @login_required
    def get_current_user(self):
        resp = GetCurrentUserResp()
        # current_user 获取当前登录的账号信息
        return success_json(resp.dump(current_user))

    @login_required
    def update_name(self):
        """更新当前登录账号名称"""
        # 1.提取请求数据并校验
        req = UpdateNameReq()
        if not req.validate():
            return validation_error_json(req.errors)

        # 2.调用服务更新账号名称
        self.account_service.update_account(
            current_user,
            name=req.name.data
        )

        return success_message("更新账号名称成功")

    @login_required
    def update_avatar(self):
        """更新当前账号头像信息"""
        # 1.提取请求数据并校验
        req = UpdateAvatarReq()
        if not req.validate():
            return validation_error_json(req.errors)

        # 2.调用服务更新账号名称
        self.account_service.update_account(
            current_user,
            avatar=req.avatar.data
        )

        return success_message("更新账号头像成功")

    # 更新当前登录账号密码
    @login_required
    def update_password(self):
        """更新当前登录账号密码"""
        # 1.提取请求数据并校验
        req = UpdatePasswordReq()
        if not req.validate():
            return validation_error_json(req.errors)

        # 2.校验原密码后更新账号密码
        self.account_service.update_password(
            password=req.password.data,
            account=current_user,
            old_password=req.old_password.data,
        )

        # 3 响应结果
        return success_message("更新账号密码成功")
