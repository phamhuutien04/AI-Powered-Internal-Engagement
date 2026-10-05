import pandas as pd


def load_workbook(file):

    excel = pd.ExcelFile(file)

    workbook = {}

    for sheet in excel.sheet_names:

        workbook[sheet] = pd.read_excel(
            file,
            sheet_name=sheet
        )

    return workbook