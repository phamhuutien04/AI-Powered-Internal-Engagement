from agents.workbook_agent import (
    analyze_workbook_structure
)

from agents.analysis_agent import (
    analyze_workbook_content
)

file_path = "EDA_Summary.xlsx"

workbook_result = (
    analyze_workbook_structure(
        file_path
    )
)

print("\n=== WORKBOOK ===\n")
print(workbook_result)

analysis_result = (
    analyze_workbook_content(
        workbook_result
    )
)

print("\n=== ANALYSIS ===\n")
print(analysis_result)