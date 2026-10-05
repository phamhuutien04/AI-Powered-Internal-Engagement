import json

from google import genai
from config import GEMINI_API_KEY

client = genai.Client(
    api_key=GEMINI_API_KEY
)

def build_analysis_plan(
    workbook_analysis
):

    prompt = f"""
You are an AI data analyst.

Workbook Analysis:

{workbook_analysis}

Determine:

1. What should be tracked?
2. What records represent completion?
3. How should participation be measured?
4. What users should be considered pending?
5. What output reports should be generated?

Return JSON only.

Format:

{{
  "tracking_entity":"",
  "completion_logic":"",
  "pending_logic":"",
  "required_reports":[]
}}
"""
    
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text