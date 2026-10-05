from workbook_scanner import (
    load_visible_workbook,
    detect_master_sheet,
    detect_key_column,
    classify_sheets
)

from completion_engine import (
    build_completion_matrix
)

from summary_engine import (
    generate_summary
)


file_path = "data/Data.xlsx"

print("START")

# ====================================
# LOAD WORKBOOK
# ====================================

workbook = load_visible_workbook(
    file_path
)

print("WORKBOOK LOADED")


# ====================================
# DETECT MASTER
# ====================================

master_sheet = detect_master_sheet(
    workbook
)

print(
    "MASTER SHEET:",
    master_sheet
)


# ====================================
# DETECT KEY COLUMN
# ====================================

key_column = detect_key_column(
    workbook[master_sheet]
)

print(
    "KEY COLUMN:",
    key_column
)


# ====================================
# CLASSIFY SHEETS
# ====================================

sheet_types = classify_sheets(
    workbook,
    master_sheet,
    key_column
)

print("\nSHEET TYPES:")

for sheet, sheet_type in sheet_types.items():

    print(
        f"{sheet} -> {sheet_type}"
    )


# ====================================
# BUILD COMPLETION MATRIX
# ====================================

completion_matrix = build_completion_matrix(
    workbook,
    master_sheet,
    key_column,
    sheet_types
)

print("\nCOMPLETION MATRIX")

print(
    completion_matrix.head()
)

print(
    "\nTOTAL ROWS:",
    len(completion_matrix)
)


# ====================================
# GENERATE SUMMARY
# ====================================

summary = generate_summary(
    completion_matrix
)

print("\nSUMMARY")

for key, value in summary.items():

    print(
        f"{key}: {value}"
    )