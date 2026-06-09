import os

# 1. 定义你要读取的代码文件夹路径（根据你的实际目录名字微调）
TARGET_FOLDERS = ['app', 'internal','config','pkg','storage','z_readme']
# 2. 允许读取的文件后缀
ALLOWED_EXTENSIONS = ('.py', '.vue','.yaml','.md')
# 3. 输出的合并文件名
OUTPUT_FILE = 'dm_to_txt.txt'


def merge_project_files():
    total_files = 0
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        # 遍历指定的文件夹
        for folder in TARGET_FOLDERS:
            if not os.path.exists(folder):
                continue
            for root, dirs, files in os.walk(folder):
                # 自动过滤掉缓存目录，防止噪声
                if '__pycache__' in root or '.pytest_cache' in root:
                    continue
                for file in files:
                    if file.endswith(ALLOWED_EXTENSIONS):
                        file_path = os.path.join(root, file)
                        # 写入清晰的文件分隔符，方便大模型识别目录结构
                        outfile.write(f"\n\n{'=' * 50}\n")
                        outfile.write(f"📄 FILE: {file_path}\n")
                        outfile.write(f"{'=' * 50}\n\n")

                        try:
                            with open(file_path, 'r', encoding='utf-8') as infile:
                                outfile.write(infile.read())
                            total_files += 1
                        except Exception as e:
                            outfile.write(f"// 读取文件失败: {str(e)}\n")

    print(f"✨ 大功告成！已成功合并 {total_files} 个代码文件到 {OUTPUT_FILE} 中！")


if __name__ == '__main__':
    merge_project_files()