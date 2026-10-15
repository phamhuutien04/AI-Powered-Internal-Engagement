import re
import unicodedata

import pandas as pd


TRUE_VALUES = {
    "1", "yes", "y", "true", "done", "complete", "completed", "co",
    "da co", "da hoan thanh", "hoan thanh", "x",
}
FALSE_VALUES = {
    "0", "no", "n", "false", "pending", "incomplete", "not complete",
    "not completed", "khong", "chua", "chua co", "chua hoan thanh", "",
}
STATUS_HEADER_WORDS = {
    "status", "state", "completion", "complete", "completed", "done",
    "trang thai", "tinh trang", "hoan thanh", "ket qua",
}


def _normalize_text(value):
    if pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text).strip().lower()


def _status_flag(value):
    """Convert common spreadsheet status values to 1/0, or None if unknown."""
    if pd.isna(value):
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(float(value) > 0)

    text = _normalize_text(value)
    if text in TRUE_VALUES:
        return 1
    if text in FALSE_VALUES:
        return 0
    return None


def _looks_like_status_header(column):
    header = _normalize_text(column)
    return any(word in header for word in STATUS_HEADER_WORDS)


def _status_series(series):
    converted = series.map(_status_flag)
    known_non_blank = converted[series.notna()].notna()
    if series.notna().sum() and float(known_non_blank.mean()) >= 0.8:
        return converted.fillna(0).astype(float)
    return None


def _find_account_column(activity_df, master_accounts):
    best_col = None
    best_overlap = 0
    for column in activity_df.columns:
        values = set(
            activity_df[column].dropna().astype(str).str.strip().str.lower()
        )
        if not values:
            continue
        overlap = len(values.intersection(master_accounts))
        if overlap > best_overlap:
            best_overlap = overlap
            best_col = column
    return best_col


def _add_inline_status_activities(matrix, master_df, key_column, sheet_types):
    """Use status columns inside a one-sheet/list-style workbook."""
    candidates = []
    for column in master_df.columns:
        if column == key_column or not _looks_like_status_header(column):
            continue
        converted = _status_series(master_df[column])
        if converted is not None:
            candidates.append((column, converted))

    for column, converted in candidates:
        label = str(column).strip() or "Required status"
        if label in matrix.columns:
            label = f"{label} status"
        matrix[label] = converted.reset_index(drop=True) * 100
        sheet_types[label] = "ACTIVITY_STATUS"


def build_completion_matrix(workbook, master_sheet, key_column, sheet_types):
    master_df = workbook[master_sheet].copy().reset_index(drop=True)
    valid_keys = master_df[key_column].notna() & master_df[key_column].astype(str).str.strip().ne("")
    master_df = master_df.loc[valid_keys].copy().drop_duplicates(subset=[key_column])
    master_df = master_df.reset_index(drop=True)
    master_df[key_column] = master_df[key_column].astype(str).str.strip().str.lower()

    matrix = pd.DataFrame({"Account": master_df[key_column]})
    status_source_columns = {}
    master_accounts = set(matrix["Account"])
    activity_sheets = [
        sheet_name
        for sheet_name, sheet_type in list(sheet_types.items())
        if sheet_type in ["ACTIVITY_PRESENCE", "ACTIVITY_STATUS"]
        and sheet_name in workbook
    ]

    for sheet_name in activity_sheets:
        activity_df = workbook[sheet_name].copy()
        sheet_type = sheet_types[sheet_name]
        account_col = _find_account_column(activity_df, master_accounts)
        if account_col is None:
            continue

        activity_df[account_col] = (
            activity_df[account_col].astype(str).str.strip().str.lower()
        )

        if sheet_type == "ACTIVITY_PRESENCE":
            completed_users = set(activity_df[account_col].dropna())
            matrix[sheet_name] = matrix["Account"].map(
                lambda account: 1 if account in completed_users else 0
            )
            continue

        status_cols = []
        for column in activity_df.columns:
            if column == account_col or _normalize_text(column) in {"no", "stt", "index"}:
                continue
            if _status_series(activity_df[column]) is not None:
                status_cols.append(column)
        status_source_columns[sheet_name] = [str(column) for column in status_cols]
        progress_map = {}
        for _, row in activity_df.iterrows():
            flags = []
            for column in status_cols:
                flag = _status_flag(row[column])
                if flag is not None:
                    flags.append(flag)
            progress_map[row[account_col]] = round(sum(flags) / max(len(flags), 1) * 100, 2)

        matrix[sheet_name] = matrix["Account"].map(
            lambda account: progress_map.get(account, 0)
        )

    if len(matrix.columns) == 1:
        _add_inline_status_activities(matrix, master_df, key_column, sheet_types)

    # Keep the exact source fields used by the calculation.  The desktop UI
    # exposes this count so two installations can be compared at a glance.
    matrix.attrs["status_source_columns"] = status_source_columns

    return matrix
