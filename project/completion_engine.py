import pandas as pd


def build_completion_matrix(
    workbook,
    master_sheet,
    key_column,
    sheet_types
):

    master_df = workbook[master_sheet].copy()

    master_df[key_column] = (
        master_df[key_column]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    matrix = pd.DataFrame()

    matrix["Account"] = master_df[key_column]

    activity_sheets = [

        sheet_name

        for sheet_name, sheet_type

        in sheet_types.items()

        if sheet_type in [
            "ACTIVITY_PRESENCE",
            "ACTIVITY_STATUS"
        ]

    ]

    for sheet_name in activity_sheets:

        activity_df = workbook[sheet_name].copy()

        sheet_type = sheet_types[sheet_name]

        # =====================
        # PRESENCE ACTIVITY
        # =====================

        if sheet_type == "ACTIVITY_PRESENCE":

            best_overlap = 0
            best_col = None

            for col in activity_df.columns:

                try:

                    values = set(
                        activity_df[col]
                        .astype(str)
                        .str.strip()
                        .str.lower()
                        .dropna()
                    )

                    overlap = len(
                        values.intersection(
                            set(matrix["Account"])
                        )
                    )

                    overlap_rate = (
                        overlap /
                        max(len(values), 1)
                    )

                    if overlap_rate > best_overlap:

                        best_overlap = overlap_rate
                        best_col = col

                except:
                    continue

            if best_col is None:
                continue

            completed_users = set(
                activity_df[best_col]
                .astype(str)
                .str.strip()
                .str.lower()
                .dropna()
            )

            matrix[sheet_name] = (
                matrix["Account"]
                .apply(
                    lambda x:
                    1 if x in completed_users
                    else 0
                )
            )

        # =====================
        # STATUS ACTIVITY
        # =====================

        elif sheet_type == "ACTIVITY_STATUS":

            account_col = None

            for col in activity_df.columns:

                if "account" in str(col).lower():

                    account_col = col
                    break

            if account_col is None:
                continue

            status_cols = [

                col

                for col

                in activity_df.columns

                if str(col).lower()

                not in [
                    "no",
                    str(account_col).lower()
                ]

            ]

            total_status_cols = len(
                status_cols
            )

            activity_df[account_col] = (

                activity_df[account_col]

                .astype(str)

                .str.strip()

                .str.lower()

            )

            progress_map = {}

            for _, row in activity_df.iterrows():

                account = row[account_col]

                completed_count = (

                    row[status_cols]

                    .fillna(0)

                    .sum()

                )

                completion_percent = round(
                    (
                        completed_count
                        /
                        max(total_status_cols, 1)
                    ) * 100,
                    2
                )

                progress_map[
                    account
                ] = completion_percent

            matrix[sheet_name] = (
                matrix["Account"]
                .apply(
                    lambda x:
                    progress_map.get(
                        x,
                        0
                    )
                )
            )

    return matrix