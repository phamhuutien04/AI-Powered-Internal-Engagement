import pandas as pd


REMINDER_TEMPLATE = (
    "Hi {account}, this is a friendly reminder that the following activities or participation records "
    "are still outstanding: {missing_activities}. Please complete any required activity and update any "
    "applicable participation record at your earliest convenience. If the records are already current, "
    "please let us know so they can be verified. Thank you!"
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
