import pandas as pd


def generate_pending_report(
    completion_matrix
):

    activity_cols = list(
        completion_matrix.columns[1:]
    )

    pending_rows = []

    for _, row in completion_matrix.iterrows():

        missing = []

        for activity in activity_cols:

            if row[activity] == 0:

                missing.append(
                    activity
                )

        if len(missing) > 0:

            pending_rows.append({

                "Account":
                    row["Account"],

                "Missing Activities":
                    ", ".join(
                        missing
                    ),

                "Missing Count":
                    len(missing)
            })

    return pd.DataFrame(
        pending_rows
    )