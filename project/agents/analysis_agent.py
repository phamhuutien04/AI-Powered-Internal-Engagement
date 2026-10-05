from google import genai
from config import GEMINI_API_KEY

client = genai.Client(
    api_key=GEMINI_API_KEY
)

def analyze_workbook_content(
    workbook_analysis
):

    prompt = f"""
You are an Internal Engagement Analyst.

Based on this workbook analysis:

{workbook_analysis}

Provide:

1. Key Findings
2. Potential Risks
3. Recommendations
4. Suggested Dashboard Metrics

Return JSON only.

Format:

{{
    "key_findings": [],
    "risks": [],
    "recommendations": [],
    "dashboard_metrics": []
}}
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text