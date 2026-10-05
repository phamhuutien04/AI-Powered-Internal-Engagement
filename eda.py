import pandas as pd
from openpyxl import load_workbook

# =====================
# Đọc file Excel
# =====================

file_path = r"data\data.xlsx"

# =====================
# Lấy các sheet đang hiện
# =====================

wb = load_workbook(file_path)

visible_sheets = [
    ws.title
    for ws in wb.worksheets
    if ws.sheet_state == "visible"
]

print("\nDanh sách sheet đang sử dụng:")
print(visible_sheets)

# =====================
# Đọc các sheet visible
# =====================

all_sheets = {}

for sheet in visible_sheets:

    all_sheets[sheet] = pd.read_excel(
        file_path,
        sheet_name=sheet
    )

# =====================
# EDA
# =====================

summary = []

for sheet_name, df in all_sheets.items():

    print("\n" + "=" * 60)
    print(f"SHEET: {sheet_name}")
    print("=" * 60)

    print(f"Số dòng: {df.shape[0]}")
    print(f"Số cột: {df.shape[1]}")

    print("\nTên cột:")
    print(df.columns.tolist())

    missing_count = df.isnull().sum().sum()

    duplicate_count = df.duplicated().sum()

    print(f"\nTổng giá trị thiếu: {missing_count}")
    print(f"Số dòng trùng lặp: {duplicate_count}")

    summary.append({
        "Sheet Name": sheet_name,
        "Rows": df.shape[0],
        "Columns": df.shape[1],
        "Missing Values": missing_count,
        "Duplicate Rows": duplicate_count
    })

# =====================
# Tổng quan workbook
# =====================

summary_df = pd.DataFrame(summary)

print("\n")
print("=" * 60)
print("TỔNG QUAN DỮ LIỆU")
print("=" * 60)

print(summary_df)

# =====================
# Xuất Excel
# =====================

summary_df.to_excel(
    "EDA_Summary.xlsx",
    index=False
)

print("\nĐã xuất file EDA_Summary.xlsx")