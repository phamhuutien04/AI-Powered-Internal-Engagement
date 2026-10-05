import pandas as pd

from ai_reminder_engine import (
    DEFAULT_REMINDER_TEMPLATE,
    generate_reminder_template
)


def generate_reminders(
    pending_df
):

    try:
        template = generate_reminder_template()
    except Exception as error:
        print(
            "Gemini reminder generation failed; "
            f"using the default template. Details: {error}"
        )
        template = DEFAULT_REMINDER_TEMPLATE

    reminder_rows = []

    for _, row in pending_df.iterrows():

        account = row[
            "Account"
        ]

        missing = row[
            "Missing Activities"
        ]

        message = template.format(

            account=account,

            missing_activities=missing

        )

        reminder_rows.append({

            "Account":
                account,

            "Reminder":
                message

        })

    return pd.DataFrame(
        reminder_rows
    )
