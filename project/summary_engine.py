import pandas as pd


def _activity_type(column, values, sheet_types):
    activity_type = sheet_types.get(column)
    if activity_type is not None:
        return activity_type
    return "ACTIVITY_STATUS" if values.max() > 1 else "ACTIVITY_PRESENCE"


def generate_summary(completion_matrix, sheet_types=None):
    """Summarize mandatory progress separately from optional participation."""
    sheet_types = sheet_types or {}
    total_users = len(completion_matrix)
    presence_metrics = {}
    presence_counts = {}
    status_metrics = {}
    presence_scores = pd.DataFrame(index=completion_matrix.index)
    status_scores = pd.DataFrame(index=completion_matrix.index)

    for column in completion_matrix.columns:
        if column == "Account":
            continue

        values = pd.to_numeric(completion_matrix[column], errors="coerce").fillna(0)
        activity_type = _activity_type(column, values, sheet_types)

        if activity_type == "ACTIVITY_STATUS":
            scores = values.clip(lower=0, upper=100) / 100
            status_scores[column] = scores
            status_metrics[column] = round(float(scores.mean() * 100), 2)
        elif activity_type == "ACTIVITY_PRESENCE":
            scores = (values > 0).astype(float)
            presence_scores[column] = scores
            presence_counts[column] = int(scores.sum())
            presence_metrics[column] = round(float(scores.mean() * 100), 2)

    if status_scores.empty:
        mandatory_completed_users = 0
        mandatory_pending_users = 0
        mandatory_progress_rate = 0.0
    else:
        mandatory_completed_users = int(status_scores.ge(1).all(axis=1).sum())
        mandatory_pending_users = int(total_users - mandatory_completed_users)
        mandatory_progress_rate = round(float(status_scores.mean().mean() * 100), 1)

    optional_participants = (
        int(presence_scores.gt(0).any(axis=1).sum()) if not presence_scores.empty else 0
    )
    status_source_columns = completion_matrix.attrs.get("status_source_columns", {})
    required_field_count = sum(len(columns) for columns in status_source_columns.values())

    return {
        "total_users": total_users,
        "total_activities": len(status_scores.columns) + len(presence_scores.columns),
        "mandatory_activity_count": len(status_scores.columns),
        "required_field_count": required_field_count,
        "participation_activity_count": len(presence_scores.columns),
        "mandatory_completed_users": mandatory_completed_users,
        "mandatory_pending_users": mandatory_pending_users,
        "mandatory_progress_rate": mandatory_progress_rate,
        "optional_participants": optional_participants,
        "certificate_participants": optional_participants,
        "presence_counts": presence_counts,
        "presence_metrics": presence_metrics,
        "status_metrics": status_metrics,
        # Compatibility for older callers: completion now means mandatory status only.
        "fully_completed_users": mandatory_completed_users,
        "overall_completion_rate": mandatory_progress_rate,
    }
