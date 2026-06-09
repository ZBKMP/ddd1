import base64
import binascii
import hashlib
import re
from typing import Any

# 密码校验正则，密码最少包含一个字母、一个数字，并且长度在8-16
password_pattern = r"^(?=.*[a-zA-Z])(?=.*\d).{8,16}$"

# 校验传入的密码是否符合相应的匹配规则
def validate_password(password: str, pattern: str = password_pattern):
    """校验传入的密码是否符合相应的匹配规则"""
    if re.match(pattern, password) is None:
        raise ValueError("密码规则校验失败，至少包含一个字母，一个数字，并且长度为8-16位")
    return


# 将传入的密码+盐值进行哈希加密 返回字节串
def hash_password(password: str, salt: Any) -> bytes:
    """将传入的密码+盐值进行哈希加密"""
    # salt :防止彩虹表攻击 防御批量破解 避免哈希碰撞 增加唯一性
    # iterations : 迭代次数 故意减慢哈希计算速度，增加暴力破解的成本
    dk = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode("utf-8"),
        salt=salt,
        iterations=10000)
    return binascii.hexlify(dk)

# 根据传递的密码+盐值校验比对数据库内的密码(password_hashed_base64)是否一致
def compare_password(
        password: str,
        password_hashed_base64: Any,
        salt_base64: Any,
) -> bool:
    """根据传递的密码比对数据库中的密码+盐值是否一致"""
    if not password_hashed_base64 or not salt_base64:
        return False
    return (
            hash_password(password, base64.b64decode(salt_base64))
            == base64.b64decode(password_hashed_base64)
    )