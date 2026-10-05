from workbook_scanner import (
    load_visible_workbook,
    detect_master_sheet,
    detect_key_column,
    classify_sheets
)

file_path = "../Data/Data.xlsx"

print("START")

workbook = load_visible_workbook(
    file_path
)

print("WORKBOOK LOADED")

master_sheet = detect_master_sheet(
    workbook
)

print("MASTER DETECTED")

master_df = workbook[
    master_sheet
]

key_column = detect_key_column(
    master_df
)

print("KEY DETECTED")

sheet_types = classify_sheets(
    workbook,
    master_sheet,
    key_column
)

print("CLASSIFICATION DONE")

print(
    "MASTER SHEET:",
    master_sheet
)

print(
    "KEY COLUMN:",
    key_column
)

print("\nSHEET TYPES:")

for sheet, sheet_type in sheet_types.items():

    print(
        f"{sheet} -> {sheet_type}"
    )