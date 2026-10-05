import pandas as pd

file_path = r"data\data.xlsx"

aws = pd.read_excel(
    file_path,
    sheet_name="AWS Certified Generative AI Dev"
)

print(aws["List of employees"].head(20))