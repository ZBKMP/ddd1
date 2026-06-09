import os

# ==================== 配置区域 ====================
OLD_IP = "192.168.58.129"  # 老师的向量库 IP
NEW_IP = "192.168.172.129"  # 你的向量库 IP

# 允许检索和替换的文件后缀（扩展名）
TARGET_EXTENSIONS = [".py", ".txt", ".env", ".yaml", ".yml", ".json", ".ini", ".conf"]

# 需要严格忽略的目录（防止破坏虚拟环境和系统文件）
IGNORE_DIRS = [
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".git",
    ".idea",
    ".vscode"
]


# ==================================================

def batch_replace_ip():
    print(f"🚀 开始在项目根目录下检索并替换向量库 IP...")
    print(f"🔍 目标: 将 '{OLD_IP}' 替换为 '{NEW_IP}'\n" + "-" * 50)

    replace_count = 0
    file_count = 0
    root_dir = os.path.abspath(os.path.dirname(__file__))

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 动态过滤掉不需要扫描的目录
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for filename in filenames:
            # 检查文件后缀是否在允许范围内
            ext = os.path.splitext(filename)[1].lower()
            if ext not in TARGET_EXTENSIONS:
                continue

            # 排除脚本自身，防止死循环
            if filename == os.path.basename(__file__):
                continue

            file_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(file_path, root_dir)

            try:
                # 1. 以 utf-8 编码读取文件内容
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # 2. 如果包含旧 IP，进行替换并写回
                if OLD_IP in content:
                    occurrences = content.count(OLD_IP)
                    new_content = content.replace(OLD_IP, NEW_IP)

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    print(f"✅ 成功替换: {relative_path} (替换了 {occurrences} 处)")
                    replace_count += occurrences
                    file_count += 1
            except Exception as e:
                # 略过无法读取的二进制文件或编码错误文件
                pass

    print("-" * 50)
    print(f"🎉 替换完成！共修改了 {file_count} 个文件，成功替换了 {replace_count} 处 IP 地址。")


if __name__ == "__main__":
    batch_replace_ip()