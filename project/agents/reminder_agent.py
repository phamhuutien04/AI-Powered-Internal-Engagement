# agents/reminder_agent.py

from google import genai


def generate_reminder(
    employee,
    missing_activities,
    api_key
):

    client = genai.Client(api_key=api_key)

    prompt = f"""
    Write a professional reminder.

    Employee:
    {employee}

    Missing Activities:
    {missing_activities}

    Friendly tone.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
