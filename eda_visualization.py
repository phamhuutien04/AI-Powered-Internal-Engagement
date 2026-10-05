import pandas as pd
import matplotlib.pyplot as plt
import os

# =======================
# Tạo thư mục output
# =======================

os.makedirs("output", exist_ok=True)

# =======================
# Đọc dữ liệu
# =======================

df = pd.read_excel(
    r"data\data.xlsx",
    sheet_name="Bảng nhân sự CMS"
)

# Xóa khoảng trắng thừa tên cột
df.columns = df.columns.str.strip()

print(df.columns.tolist())

# =======================
# Danh sách cột cần vẽ
# =======================

columns_to_plot = [
    "Contract Type",
    "Job Rank",
    "Department",
    "Main Skill",
    "Current Skill",
    "Location",
    "Project Type",
    "Role"
]

# =======================
# Vẽ từng biểu đồ
# =======================

for col in columns_to_plot:

    if col not in df.columns:
        print(f"Không tìm thấy cột: {col}")
        continue

    plt.figure(figsize=(10,5))

    df[col].value_counts().head(10).plot(
        kind="bar"
    )

    plt.title(col)
    plt.xlabel("")
    plt.ylabel("Count")

    plt.tight_layout()

    filename = col.replace(" ", "_")

    plt.savefig(
        f"output/{filename}.png",
        dpi=300
    )

    plt.close()

    print(f"Đã lưu: {filename}.png")

print("\nHoàn thành!")