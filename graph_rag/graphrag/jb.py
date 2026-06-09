import os
import pandas as pd

src_dir = r"import_data/exported_data"
dest_dir = r"test_csv/input"

# 先清空旧的 input 目录，防止残留文件干扰
if os.path.exists(dest_dir):
    for f in os.listdir(dest_dir):
        if f.endswith('.csv'):
            os.remove(os.path.join(dest_dir, f))
os.makedirs(dest_dir, exist_ok=True)

combined_rows = []

# 遍历处理每一个业务 CSV
for file_name in os.listdir(src_dir):
    if file_name.endswith('.csv'):
        file_path = os.path.join(src_dir, file_name)
        df = pd.read_csv(file_path)
        table_name = file_name.replace('.csv', '')

        # 将每一行的数据转换为一段充满上下文的描述性文本
        for idx, row in df.iterrows():
            row_dict = row.dropna().to_dict()
            # 拼接成类似: "在表categories中: CategoryID是1, CategoryName是智能音箱..."
            details = ", ".join([f"{k}是{v}" for k, v in row_dict.items()])
            text_context = f"属于业务模块【{table_name}】的数据明细：{details}"

            # 生成唯一的 ID
            unique_id = f"{table_name}_{idx}"
            combined_rows.append({"id": unique_id, "text": text_context})

# 打包成唯一的标准格式 CSV
result_df = pd.DataFrame(combined_rows)
result_df.to_csv(os.path.join(dest_dir, "combined_business_data.csv"), index=False, encoding='utf-8')
print("🎉 所有业务 CSV 已完美融合为单张标准图 RAG 表：combined_business_data.csv")