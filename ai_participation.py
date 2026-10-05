import pandas as pd
import matplotlib.pyplot as plt
import os

# =====================
# Setup
# =====================

os.makedirs("output", exist_ok=True)

file_path = r"data\data.xlsx"

# =====================
# Tổng nhân sự
# =====================

total_employee = 389

# =====================
# AWS
# =====================

aws_df = pd.read_excel(
    file_path,
    sheet_name="AWS Certified Generative AI Dev"
)

aws_count = aws_df.shape[0]

# =====================
# Claude
# =====================

claude_df = pd.read_excel(
    file_path,
    sheet_name="AI Claude Foundati Certificate "
)

claude_count = claude_df.shape[0]

# =====================
# Copilot
# =====================

copilot_df = pd.read_excel(
    file_path,
    sheet_name=" GitHub Copilot Certification ("
)

copilot_count = copilot_df.shape[0]

# =====================
# Summary
# =====================

summary = pd.DataFrame({
    "Program": [
        "AWS GenAI",
        "Claude Foundation",
        "GitHub Copilot"
    ],
    "Participants": [
        aws_count,
        claude_count,
        copilot_count
    ]
})

summary["Non-Participants"] = (
    total_employee
    - summary["Participants"]
)

summary["Participation Rate (%)"] = (
    summary["Participants"]
    / total_employee
    * 100
).round(2)

print("\n===== AI PARTICIPATION SUMMARY =====")
print(summary)

# Xuất kết quả
summary.to_excel(
    "output/AI_Participation_Summary.xlsx",
    index=False
)

# =====================
# Biểu đồ
# =====================

plt.figure(figsize=(8,5))

bars = plt.bar(
    summary["Program"],
    summary["Participation Rate (%)"]
)

plt.title(
    "Participation Rate by AI Certification Program"
)

plt.ylabel("Participation Rate (%)")

# Hiển thị số trên cột
for bar in bars:
    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width()/2,
        height,
        f"{height:.2f}%",
        ha="center",
        va="bottom"
    )

plt.tight_layout()

plt.savefig(
    "output/AI_Participation_Rate.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nĐã lưu:")
print("- output/AI_Participation_Summary.xlsx")
print("- output/AI_Participation_Rate.png")