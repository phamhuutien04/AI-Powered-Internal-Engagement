from workbook_scanner import (
    load_visible_workbook,
    detect_master_sheet,
    detect_key_column,
    classify_sheets
)

from completion_engine import (
    build_completion_matrix
)

file_path = "Data/Data.xlsx"

workbook = load_visible_workbook(
    file_path
)

master_sheet = detect_master_sheet(
    workbook
)

key_column = detect_key_column(
    workbook[master_sheet]
)

sheet_types = classify_sheets(
    workbook,
    master_sheet,
    key_column
)

matrix = build_completion_matrix(
    workbook,
    master_sheet,
    key_column,
    sheet_types
)

print(matrix.head())

print("\nROWS:")
print(len(matrix))