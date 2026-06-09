"""
重置 LLMOPS 账号密码（忘记密码时使用，无需改登录逻辑）。

用法（在项目根目录）:
  .venv\\Scripts\\python.exe scripts\\reset_password.py --email 你的邮箱@example.com
  .venv\\Scripts\\python.exe scripts\\reset_password.py --email 你的邮箱@example.com --password Admin12345

重置后用该邮箱 + 新密码调用 POST /auth/password-login 获取 JWT。
"""
from __future__ import annotations

import argparse
import base64
import os
import secrets
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pkg.password import hash_password, validate_password  # noqa: E402

DEFAULT_PASSWORD = "Admin12345"


def reset_password(email: str, password: str) -> None:
    validate_password(password)
    uri = os.getenv("SQLALCHEMY_DATABASE_URI")
    if not uri:
        raise SystemExit("未找到 SQLALCHEMY_DATABASE_URI，请检查 .env")

    salt = secrets.token_bytes(16)
    hashed = hash_password(password, salt)
    pw_b64 = base64.b64encode(hashed).decode()
    salt_b64 = base64.b64encode(salt).decode()

    engine = create_engine(uri)
    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                UPDATE account
                SET password = :password, password_salt = :salt
                WHERE email = :email
                """
            ),
            {"password": pw_b64, "salt": salt_b64, "email": email},
        )
        if result.rowcount == 0:
            raise SystemExit(f"未找到邮箱为 {email!r} 的账号，请先在库中确认 email 或改用 GitHub 登录后绑定。")

    print(f"已重置账号 {email} 的密码，请使用新密码登录。")


def main() -> None:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description="重置 LLMOPS 账号密码")
    parser.add_argument("--email", required=True, help="账号邮箱")
    parser.add_argument(
        "--password",
        default=DEFAULT_PASSWORD,
        help=f"新密码（默认 {DEFAULT_PASSWORD}，须含字母+数字，8-16 位）",
    )
    args = parser.parse_args()
    reset_password(args.email.strip(), args.password)


if __name__ == "__main__":
    main()
