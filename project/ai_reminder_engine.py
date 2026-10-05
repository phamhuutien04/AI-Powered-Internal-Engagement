from google import genai

from config import GEMINI_API_KEY, GEMINI_MODEL


DEFAULT_REMINDER_TEMPLATE = """Hello {account},

This is a friendly reminder to complete the following activities: {missing_activities}.

Please complete them at your earliest convenience. Thank you for your participation and support.
"""


def _get_client():
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it to project/.env."
        )

    return genai.Client(api_key=GEMINI_API_KEY)


def generate_reminder_template():

    prompt = """
Create ONE reusable reminder template.

Rules:

- Professional
- Friendly
- Encouraging
- Less than 100 words

Use placeholders:

{account}

{missing_activities}

Keep these placeholders unchanged.
"""

    client = _get_client()

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        template = response.text

        if not template:
            return DEFAULT_REMINDER_TEMPLATE

        return template
    finally:
        client.close()
