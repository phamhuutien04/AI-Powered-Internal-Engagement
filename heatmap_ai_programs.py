import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# ==================================
# Setup
# ==================================

os.makedirs("output", exist_ok=True)

file_path = r"data\data.xlsx"

# ==================================
# Employee Data
# ==================================

employee = pd.read_excel(
    file_path,
    sheet_name="Bảng nhân sự CMS"
)

employee.columns = employee.columns.str.strip()

# ==================================
# AWS
# ==================================

aws = pd.read_excel(
    file_path,
    sheet_name="AWS Certified Generative AI Dev"
)

aws_accounts = set(
    aws["List of employees"]
    .dropna()
    .astype(str)
)

# ==================================
# Claude
# ==================================

claude = pd.read_excel(
    file_path,
    sheet_name="AI Claude Foundati Certificate "
)

claude_accounts = set(
    claude["List of employees"]
    .dropna()
    .astype(str)
)

# ==================================
# Copilot
# ==================================

copilot = pd.read_excel(
    file_path,
    sheet_name=" GitHub Copilot Certification ("
)

copilot_accounts = set(
    copilot["List of employees"]
    .dropna()
    .astype(str)
)

# ==================================
# Gắn cờ tham gia
# ==================================

employee["AWS"] = employee["Account"].apply(
    lambda x: 1 if str(x) in aws_accounts else 0
)

employee["Claude"] = employee["Account"].apply(
    lambda x: 1 if str(x) in claude_accounts else 0
)

employee["Copilot"] = employee["Account"].apply(
    lambda x: 1 if str(x) in copilot_accounts else 0
)

# ==================================
# Project đã mã hóa
# ==================================

project_col = "Project Code3"

employee = employee[
    employee[project_col].notna()
]

# ==================================
# Chỉ giữ project có từ 3 người trở lên
# ==================================

project_size = employee.groupby(project_col).size()

valid_projects = project_size[
    project_size >= 3
].index

employee = employee[
    employee[project_col].isin(valid_projects)
]

# ==================================
# Participation Rate
# ==================================

heatmap_data = (
    employee
    .groupby(project_col)[["AWS", "Claude", "Copilot"]]
    .mean()
    * 100
).round(1)

# Sắp xếp project theo tổng mức độ tham gia

heatmap_data["Total"] = (
    heatmap_data["AWS"]
    + heatmap_data["Claude"]
    + heatmap_data["Copilot"]
)

heatmap_data = heatmap_data.sort_values(
    "Total",
    ascending=False
)

heatmap_data = heatmap_data.drop(
    columns=["Total"]
)

# Export Excel

heatmap_data.to_excel(
    "output/Project_AI_Heatmap_Data.xlsx"
)

# ==================================
# Đảo trục
# ==================================

heatmap_display = heatmap_data.T

# ==================================
# HEATMAP
# ==================================

plt.figure(figsize=(18, 6))

sns.heatmap(
    heatmap_display,
    annot=True,
    fmt=".1f",
    cmap="RdYlGn",
    linewidths=0.5,
    linecolor="white",
    cbar_kws={
        "label": "Participation Rate (%)"
    }
)

plt.title(
    "AI Participation Rate by Project (%)",
    fontsize=14,
    fontweight="bold"
)

plt.xlabel("Project")
plt.ylabel("AI Program")

plt.tight_layout()

plt.savefig(
    "output/Project_AI_Heatmap.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("DONE")
print("Generated:")
print("- output/Project_AI_Heatmap.png")
print("- output/Project_AI_Heatmap_Data.xlsx")