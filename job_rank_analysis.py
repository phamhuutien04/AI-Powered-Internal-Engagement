import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("output", exist_ok=True)

file_path = r"data\data.xlsx"

# ===========================
# Employee Data
# ===========================

employee = pd.read_excel(
    file_path,
    sheet_name="Bảng nhân sự CMS"
)

employee.columns = employee.columns.str.strip()

# ===========================
# AWS
# ===========================

aws = pd.read_excel(
    file_path,
    sheet_name="AWS Certified Generative AI Dev"
)

aws_accounts = set(
    aws["List of employees"]
    .dropna()
    .astype(str)
)

# ===========================
# Claude
# ===========================

claude = pd.read_excel(
    file_path,
    sheet_name="AI Claude Foundati Certificate "
)

claude_accounts = set(
    claude["List of employees"]
    .dropna()
    .astype(str)
)

# ===========================
# Copilot
# ===========================

copilot = pd.read_excel(
    file_path,
    sheet_name=" GitHub Copilot Certification ("
)

copilot_accounts = set(
    copilot["List of employees"]
    .dropna()
    .astype(str)
)

# ===========================
# AI Participation
# ===========================

all_ai_accounts = (
    aws_accounts
    | claude_accounts
    | copilot_accounts
)

employee["AI_Participation"] = employee["Account"].apply(
    lambda x: 1 if str(x) in all_ai_accounts else 0
)

# ===========================
# Job Rank Analysis
# ===========================

result = employee.groupby(
    "Job Rank"
)["AI_Participation"].agg(
    Participants="sum",
    Total_Employees="count"
)

# Chỉ lấy nhóm >= 5 người
result = result[
    result["Total_Employees"] >= 5
]

result["Participation Rate (%)"] = (
    result["Participants"]
    / result["Total_Employees"]
    * 100
).round(2)

result = result.sort_values(
    "Participants",
    ascending=False
)

print(result)

result.to_excel(
    "output/AI_Participation_By_JobRank.xlsx"
)

# ===========================
# Plot
# ===========================

plt.figure(figsize=(12,6))

bars = plt.bar(
    result.index,
    result["Participants"]
)

plt.title(
    "Number of AI Participants by Job Rank"
)

plt.ylabel(
    "Number of Participants"
)

plt.xticks(
    rotation=45,
    ha="right"
)

for bar in bars:

    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width()/2,
        height,
        f"{int(height)}",
        ha="center",
        va="bottom"
    )

plt.tight_layout()

plt.savefig(
    "output/AI_Participation_By_JobRank.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nDONE")