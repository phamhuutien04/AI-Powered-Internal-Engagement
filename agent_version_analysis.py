import pandas as pd
import matplotlib.pyplot as plt
import os

# ==================
# Setup
# ==================

os.makedirs("output", exist_ok=True)

file_path = r"data\data.xlsx"

# ==================
# Đọc dữ liệu
# ==================

df = pd.read_excel(
    file_path,
    sheet_name="Update Agent usage sync"
)

# ==================
# Danh sách version
# ==================

versions = [
    "v0.10.5",
    "v0.10.8",
    "v0.10.10",
    "v0.10.12",
    "v0.10.13",
    "v0.0.15"
]

total_employee = len(df)

summary = []

# ==================
# Tính tỷ lệ cập nhật
# ==================

for version in versions:

    updated = df[version].sum()

    not_updated = total_employee - updated

    update_rate = round(
        updated / total_employee * 100,
        2
    )

    summary.append({
        "Version": version,
        "Updated": updated,
        "Not Updated": not_updated,
        "Update Rate (%)": update_rate
    })

summary_df = pd.DataFrame(summary)

print("\n===== AGENT VERSION UPDATE =====\n")
print(summary_df)

# ==================
# Xuất Excel
# ==================

summary_df.to_excel(
    "output/Agent_Version_Summary.xlsx",
    index=False
)

# ==================
# Vẽ biểu đồ
# ==================

plt.figure(figsize=(10,6))

bars = plt.bar(
    summary_df["Version"],
    summary_df["Update Rate (%)"]
)

plt.title(
    "Agent Version Update Rate"
)

plt.xlabel("Version")
plt.ylabel("Update Rate (%)")

for bar in bars:

    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width()/2,
        height,
        f"{height:.1f}%",
        ha="center",
        va="bottom"
    )

plt.tight_layout()

plt.savefig(
    "output/Agent_Version_Update_Rate.png",
    dpi=300
)

plt.close()

print("\nDone!")
print("File saved:")
print("output/Agent_Version_Summary.xlsx")
print("output/Agent_Version_Update_Rate.png")