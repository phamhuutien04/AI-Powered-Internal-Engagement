def generate_summary(
    completion_matrix,
    sheet_types
):

    total_users = len(
        completion_matrix
    )

    presence_metrics = {}

    status_metrics = {}

    for column in completion_matrix.columns:

        if column == "Account":
            continue

        activity_type = (
            sheet_types.get(
                column
            )
        )

        # =====================
        # PRESENCE
        # =====================

        if activity_type == "ACTIVITY_PRESENCE":

            participation_rate = round(

                completion_matrix[
                    column
                ].mean()

                * 100,

                2
            )

            presence_metrics[
                column
            ] = participation_rate

        # =====================
        # STATUS
        # =====================

        elif activity_type == "ACTIVITY_STATUS":

            average_progress = round(

                completion_matrix[
                    column
                ].mean(),

                2
            )

            status_metrics[
                column
            ] = average_progress

    return {

        "total_users":
            total_users,

        "presence_metrics":
            presence_metrics,

        "status_metrics":
            status_metrics

    }