import pandas as pd


REMINDER_TEMPLATE = (
    "Hi {account}, this is a friendly reminder that the following activities are still pending: "
    "{missing_activities}. Please complete them and update your progress at your earliest convenience. "
    "If you have already completed them, please let us know so we can verify the records. Thank you!"
)


def generate_reminders(
    pending_df
):

    reminder_rows = []

    for _, row in pending_df.iterrows():

        account = row[
            "Account"
        ]

        missing = row[
            "Missing Activities"
        ]

        message = REMINDER_TEMPLATE.format(

            account=account,

            missing_activities=missing

        )
        message = " ".join(message.split())

        reminder_rows.append({

            "Account":
                account,

            "Reminder":
                message

        })

    return pd.DataFrame(
        reminder_rows
    )
