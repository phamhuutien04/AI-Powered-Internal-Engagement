import pandas as pd

file_path = r"data\data.xlsx"

sheets = [
    "AWS Certified Generative AI Dev",
    "AI Claude Foundati Certificate ",
    " GitHub Copilot Certification (",
    "Update Agent usage sync"
]

for sheet in sheets:

    print("\n" + "="*60)
    print(sheet)
    print("="*60)

    df = pd.read_excel(
        file_path,
        sheet_name=sheet
    )

    print(df.head())

    print("\nColumns:")
    print(df.columns.tolist())