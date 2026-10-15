import pandas as pd
import openpyxl


def load_visible_workbook(file_obj):

    file_obj.seek(0)

    wb = openpyxl.load_workbook(
        file_obj,
        read_only=True
    )

    workbook = {}

    for sheet in wb.worksheets:

        # bỏ sheet hidden
        if sheet.sheet_state != "visible":
            continue

        sheet_name = sheet.title

        try:

            file_obj.seek(0)

            df = pd.read_excel(
                file_obj,
                sheet_name=sheet_name
            )

            workbook[sheet_name] = df

        except Exception as e:

            print(
                f"Cannot load sheet {sheet_name}: {e}"
            )

    return workbook


def detect_master_sheet(workbook):

    sheet_names = list(
        workbook.keys()
    )

    if len(sheet_names) == 0:

        raise ValueError(
            "No visible sheet found."
        )

    identity_words = [
        "account", "email", "username", "user id", "userid",
        "employee id", "employee code", "staff id", "staff code",
    ]
    master_name_words = [
        "master", "employee", "staff", "personnel", "roster",
        "nhân sự", "nhan su", "danh sách", "danh sach", "account list",
    ]

    def sheet_score(item):
        position, (sheet_name, dataframe) = item
        columns = [str(column).strip().lower() for column in dataframe.columns]
        normalized_name = str(sheet_name).strip().lower()
        has_identity = any(
            any(word in column for word in identity_words)
            or column == "id"
            for column in columns
        )
        has_master_name = any(word in normalized_name for word in master_name_words)
        # A status/activity sheet can contain more rows than the employee master
        # because of duplicates or historical records. Prefer semantic master
        # names and a wider record schema before comparing row counts.
        return (
            int(has_identity),
            int(has_master_name),
            len(dataframe.columns),
            len(dataframe),
            -position,
        )

    _, (best_sheet, _) = max(enumerate(workbook.items()), key=sheet_score)
    return best_sheet


def detect_key_column(master_df):

    print("\nMASTER COLUMNS:")

    for col in master_df.columns:

        print(col)

    priority_keywords = [
        "account", "email", "username", "user id", "userid",
        "employee id", "employee code", "staff id", "staff code",
    ]

    # ưu tiên account/email
    for keyword in priority_keywords:

        for col in master_df.columns:

            col_lower = str(
                col
            ).lower()

            if keyword in col_lower:

                print(
                    f"\nKEY COLUMN FOUND: {col}"
                )

                return col

    for col in master_df.columns:
        if str(col).strip().lower() == "id":
            print(f"\nKEY COLUMN FOUND: {col}")
            return col

    # fallback
    best_col = None
    best_score = 0

    for col in master_df.columns:

        try:

            unique_count = (
                master_df[col]
                .dropna()
                .nunique()
            )

            if unique_count > best_score:

                best_score = unique_count

                best_col = col

        except:
            continue

    print(
        f"\nFALLBACK KEY COLUMN: {best_col}"
    )

    return best_col


def classify_sheets(
    workbook,
    master_sheet,
    master_key_column
):

    master_df = workbook[
        master_sheet
    ]

    master_size = len(
        master_df
    )

    master_users = set(
        master_df[master_key_column]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
    )
    master_users.discard("")

    sheet_types = {}

    sheet_types[
        master_sheet
    ] = "MASTER"

    for sheet_name, df in workbook.items():

        if sheet_name == master_sheet:
            continue

        best_overlap = 0

        for col in df.columns:

            try:

                values = set(
                    df[col]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .dropna()
                )

                if len(values) == 0:
                    continue

                overlap = len(
                    values.intersection(
                        master_users
                    )
                )

                overlap_rate = (
                    overlap /
                    len(values)
                )

                if overlap_rate > best_overlap:

                    best_overlap = overlap_rate

            except:
                continue

        coverage_ratio = (
            len(df)
            /
            max(master_size, 1)
        )

        print(
            f"{sheet_name} | "
            f"Overlap: {best_overlap:.2f} | "
            f"Coverage: {coverage_ratio:.2f}"
        )

        # Không đủ overlap => Reference
        if best_overlap < 0.6:

            sheet_types[
                sheet_name
            ] = "REFERENCE"

            continue

        # >= 90% số lượng master
        # => Status Tracking Sheet
        if coverage_ratio >= 0.9:

            sheet_types[
                sheet_name
            ] = "ACTIVITY_STATUS"

        # < 90%
        # => Presence Sheet
        else:

            sheet_types[
                sheet_name
            ] = "ACTIVITY_PRESENCE"

    return sheet_types
