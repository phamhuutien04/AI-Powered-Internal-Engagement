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

from reminder_engine import (
    generate_reminders
)

file_path = "data/Data.xlsx"

print("START")

# ===========================
# LOAD WORKBOOK
# ===========================

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

# ===========================
# COMPLETION MATRIX
# ===========================

completion_matrix = build_completion_matrix(
    workbook,
    master_sheet,
    key_column,
    sheet_types
)

# ===========================
# PENDING REPORT
# ===========================

pending_df = generate_pending_report(
    completion_matrix
)

print("\nPENDING USERS")

print(
    pending_df.head()
)

# ===========================
# REMINDER REPORT
# ===========================

reminder_df = generate_reminders(
    pending_df
)

print("\nREMINDER REPORT")

print(
    reminder_df.head()
)