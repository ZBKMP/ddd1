import { post } from '@/utils/request'
import { type BaseResponse } from '@/models/base'
import { type PasswordLoginResponse } from '@/models/auth'

// 账号密码登录请求
export const passwordLogin = (email: string, password: string) => {
  return post<PasswordLoginResponse>(`/auth/password-login`, {
    body: { email, password },
  })
}

// 忘记密码：通过邮箱 + 原密码校验后重置
export const resetPassword = (email: string, oldPassword: string, password: string) => {
  return post<BaseResponse<any>>(`/auth/reset-password`, {
    body: { email, old_password: oldPassword, password },
  })
}

// 退出登录请求
export const logout = () => {
  return post<BaseResponse<any>>(`/auth/logout`)
}
