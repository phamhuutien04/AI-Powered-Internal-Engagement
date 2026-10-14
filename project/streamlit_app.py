import streamlit as st
import pandas as pd

from workbook_scanner import (
    load_visible_workbook,
    detect_master_sheet,
    detect_key_column,
    classify_sheets
)

from completion_engine import (
    build_completion_matrix
)

from summary_engine import (
    generate_summary
)

from pending_engine import (
    generate_pending_report
)

from reminder_engine import (
    generate_reminders
)

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="AI Internal Engagement",
    page_icon="🤖",
    layout="wide"
)

st.title(
    "🤖 AI-Powered Internal Engagement"
)

st.caption(
    "Internal Engagement Tracking Dashboard"
)

# =====================================
# INPUT
# =====================================

uploaded_file = st.file_uploader(
    "Upload Excel Workbook",
    type=["xlsx"]
)

# =====================================
# MAIN FLOW
# =====================================

if uploaded_file:

    with st.spinner(
        "Analyzing workbook..."
    ):

        workbook = load_visible_workbook(
            uploaded_file
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

        summary = generate_summary(
            completion_matrix,
            sheet_types
        )

        pending_df = (
            generate_pending_report(
                completion_matrix,
                sheet_types
            )
        )

        reminder_df = (
            generate_reminders(
                pending_df
            )
        )

    # =====================================
    # TABS
    # =====================================

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Workbook",
            "Dashboard",
            "Completion Matrix",
            "Pending Users",
            "Reminder Center"
        ]
    )

    # =====================================
    # TAB 1
    # =====================================

    with tab1:

        st.subheader(
            "Workbook Analysis"
        )

        st.write(
            "Master Sheet:",
            master_sheet
        )

        st.write(
            "Key Column:",
            key_column
        )

        classification_data = []

        for sheet, sheet_type in sheet_types.items():

            classification_data.append(
                {
                    "Sheet": sheet,
                    "Type": sheet_type
                }
            )

        st.dataframe(
            pd.DataFrame(
                classification_data
            ),
            use_container_width=True
        )

    # =====================================
    # TAB 2
    # =====================================

    with tab2:

        st.subheader(
            "Dashboard"
        )

        st.metric(
            "Total Users",
            summary["total_users"]
        )

        st.divider()

        st.subheader(
            "Participation Activities"
        )

        presence_metrics = summary.get(
            "presence_metrics",
            {}
        )

        if len(presence_metrics) > 0:

            presence_df = pd.DataFrame(
                {
                    "Activity":
                        list(
                            presence_metrics.keys()
                        ),

                    "Participation Rate":
                        list(
                            presence_metrics.values()
                        )
                }
            )

            st.bar_chart(
                presence_df.set_index(
                    "Activity"
                )
            )

            cols = st.columns(
                len(presence_metrics)
            )

            for idx, (
                activity,
                rate
            ) in enumerate(
                presence_metrics.items()
            ):

                cols[idx].metric(
                    activity,
                    f"{rate}%"
                )

        st.divider()

        st.subheader(
            "Status Activities"
        )

        status_metrics = summary.get(
            "status_metrics",
            {}
        )

        if len(status_metrics) > 0:

            status_df = pd.DataFrame(
                {
                    "Activity":
                        list(
                            status_metrics.keys()
                        ),

                    "Progress":
                        list(
                            status_metrics.values()
                        )
                }
            )

            st.bar_chart(
                status_df.set_index(
                    "Activity"
                )
            )

            cols = st.columns(
                len(status_metrics)
            )

            for idx, (
                activity,
                rate
            ) in enumerate(
                status_metrics.items()
            ):

                cols[idx].metric(
                    activity,
                    f"{rate}%"
                )

    # =====================================
    # TAB 3
    # =====================================

    with tab3:

        st.subheader(
            "Completion Matrix"
        )

        st.dataframe(
            completion_matrix,
            use_container_width=True
        )

    # =====================================
    # TAB 4
    # =====================================

    with tab4:

        st.subheader(
            "Pending Users"
        )

        if pending_df.empty:

            st.info(
                "No pending users found."
            )

        else:

            search = st.text_input(
                "Search Account"
            )

            filtered_df = (
                pending_df.copy()
            )

            if (
                search
                and
                "Account"
                in filtered_df.columns
            ):

                filtered_df = filtered_df[
                    filtered_df[
                        "Account"
                    ]
                    .astype(str)
                    .str.contains(
                        search,
                        case=False,
                        na=False
                    )
                ]

            st.dataframe(
                filtered_df,
                use_container_width=True
            )

            csv = filtered_df.to_csv(
                index=False
            )

            st.download_button(
                label="Download Pending Report",
                data=csv,
                file_name="pending_report.csv",
                mime="text/csv"
            )

    # =====================================
    # TAB 5
    # =====================================

    with tab5:

        st.subheader(
            "Reminder Center"
        )

        if reminder_df.empty:

            st.info(
                "No reminder data found."
            )

        else:

            st.dataframe(
                reminder_df,
                use_container_width=True
            )

            reminder_csv = (
                reminder_df.to_csv(
                    index=False
                )
            )

            st.download_button(
                label="Download Reminder Report",
                data=reminder_csv,
                file_name="reminder_report.csv",
                mime="text/csv"
            )

else:

    st.info(
        "Upload an Excel workbook to begin."
    )
