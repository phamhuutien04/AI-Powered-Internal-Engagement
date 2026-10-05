# agents/workbook_agent.py

import pandas as pd
from google import genai
from config import GEMINI_API_KEY

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def analyze_workbook_structure(uploaded_file):

    excel = pd.ExcelFile(uploaded_file)

    workbook_preview = {}

    for sheet in excel.sheet_names:

        df = pd.read_excel(
            uploaded_file,
            sheet_name=sheet,
            nrows=10
        )

        workbook_preview[sheet] = {
            "columns": list(df.columns),
            "sample_rows": df.head(3).to_dict(
                orient="records"
            )
        }

    prompt = f"""
You are a data analyst AI.

Analyze the following Excel workbook structure.

Workbook Preview:

{workbook_preview}

YOUR TASKS:

1. Explain the purpose of this workbook.
2. Identify the main entity being tracked.
3. Identify important sheets.
4. Explain relationships between sheets.
5. Suggest how participation/completion could be measured.
6. Recommend a processing strategy.

Return ONLY valid JSON.

Output format:

{{
    "workbook_purpose": "",
    "main_entity": "",
    "important_sheets": [],
    "relationships": [],
    "analysis_strategy": "",
    "reasoning": ""
}}
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text