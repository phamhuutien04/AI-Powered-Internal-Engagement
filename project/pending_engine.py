import pandas as pd


PENDING_COLUMNS = ["Account", "Missing Activities", "Missing Count"]


def generate_pending_report(completion_matrix, sheet_types=None):
    """Return records with incomplete status or missing participation activities."""
    sheet_types = sheet_types or {}
    activity_cols = []

    for column in completion_matrix.columns:
        if column == "Account":
            continue
        values = pd.to_numeric(completion_matrix[column], errors="coerce").fillna(0)
        activity_type = sheet_types.get(column)
        if activity_type is None:
            activity_type = "ACTIVITY_STATUS" if values.max() > 1 else "ACTIVITY_PRESENCE"
        if activity_type in {"ACTIVITY_STATUS", "ACTIVITY_PRESENCE"}:
            activity_cols.append((column, activity_type))

    pending_rows = []
    for _, row in completion_matrix.iterrows():
        missing = []
        for activity, activity_type in activity_cols:
            progress = pd.to_numeric(
                pd.Series([row[activity]]), errors="coerce"
            ).fillna(0).iloc[0]
            progress = float(progress)
            if activity_type == "ACTIVITY_PRESENCE":
                if progress <= 0:
                    missing.append(activity)
                continue

            progress = max(0.0, min(100.0, progress))
            if progress < 100:
                label = activity if progress == 0 else f"{activity} ({progress:g}% complete)"
                missing.append(label)

        if missing:
            pending_rows.append({
                "Account": row["Account"],
                "Missing Activities": ", ".join(missing),
                "Missing Count": len(missing),
            })

    return pd.DataFrame(pending_rows, columns=PENDING_COLUMNS)
