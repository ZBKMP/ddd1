from dataclasses import dataclass

from flask_login import login_required, logout_user
from injector import inject

from internal.exception import FailException
from internal.schema import PasswordLoginReq, PasswordLoginResp, ResetPasswordReq
from internal.service import AccountService
from pkg.response import validation_error_json, success_json, success_message


@inject
@dataclass
class AuthHandler:
    """LLMOps平台自有授权认证处理器"""
    account_service: AccountService

    # 账号密码登录
    def password_login(self):
        """账号密码登录"""
        req = PasswordLoginReq()
        if not req.validate():
            return validation_error_json(req.errors)

        login_dict = self.account_service.password_login(
            email=req.email.data,
            password=req.password.data
        )
        return success_json(data=PasswordLoginResp().dump(login_dict))

    def reset_password(self):
        """忘记密码：通过邮箱 + 原密码校验后重置（无需登录）"""
        req = ResetPasswordReq()
        if not req.validate():
            return validation_error_json(req.errors)

        account = self.account_service.get_account_by_email(req.email.data)
        if not account:
            raise FailException("该邮箱未注册，请核实后重试")

        self.account_service.update_password(
            password=req.password.data,
            account=account,
            old_password=req.old_password.data,
        )
        return success_message("密码重置成功，请使用新密码登录")

    # 退出登录，用于提示前端清除授权凭证
    @login_required
    def logout(self):
        """退出登录，用于提示前端清除授权凭证"""
        logout_user()
        return success_message("退出登陆成功")
