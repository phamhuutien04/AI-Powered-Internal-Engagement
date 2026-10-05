from workbook_scanner import (
    load_visible_workbook,
    detect_master_sheet,
    detect_key_column,
    classify_sheets
)

from completion_engine import (
    build_completion_matrix
)

from pending_engine import (
    generate_pending_report
)


file_path = "data/Data.xlsx"

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

completion_matrix = (
    build_completion_matrix(
        workbook,
        master_sheet,
        key_column,
        sheet_types
    )
)

pending_df = generate_pending_report(
    completion_matrix
)

print("\nPENDING USERS")

print(
    pending_df.head(20)
)

print(
    "\nTOTAL PENDING:",
    len(pending_df)
)