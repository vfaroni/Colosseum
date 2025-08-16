#!/usr/bin/env python3
"""
Script to extract all rehabilitation categories from the Excel template.
This will help identify what data needs to be mapped from the markdown file.
"""

import openpyxl
from pathlib import Path

# Define the Excel file path
excel_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CA_9p_2025_R2_Perris/9_Percent_Applications/TAB_08__Rehabilitation_Credit_Applications/Exhbit-B-RAWFILE_Att-8-Rehab Summary.xlsx")

print(f"Extracting rehabilitation categories from: {excel_file.name}")
print("=" * 80)

# Load the workbook
wb = openpyxl.load_workbook(excel_file)
sheet = wb.active

# Track categories and items
current_category = None
categories = {}

# Extract all items from column A
for row in range(1, sheet.max_row + 1):
    cell_a = sheet[f'A{row}']
    if cell_a.value and isinstance(cell_a.value, str):
        value = cell_a.value.strip()
        
        # Check if this is a category header (usually in all caps)
        if value.isupper() and len(value) > 3 and value not in ["REHABILITATION ITEMS", "PROJECT NAME:"]:
            current_category = value
            categories[current_category] = []
            print(f"\n{current_category}")
            print("-" * len(current_category))
        elif current_category and not value.isupper() and "Project Name:" not in value:
            categories[current_category].append((row, value))
            print(f"  Row {row:3d}: {value}")

# Create a template dictionary for the construction data
print("\n" + "=" * 80)
print("PYTHON DICTIONARY TEMPLATE FOR CONSTRUCTION DATA:")
print("=" * 80)
print("\nconstruction_data = {")

for category, items in categories.items():
    if items:  # Only show categories with items
        print(f"    # {category}")
        for row, item in items:
            print(f'    "{item}": ("description", "units", "percentage", "useful_life"),  # Row {row}')
        print()

print("}")

# Also create a markdown template
print("\n" + "=" * 80)
print("MARKDOWN TEMPLATE FOR CONSTRUCTION COST DATA:")
print("=" * 80)

for category, items in categories.items():
    if items:
        print(f"\n## {category}")
        for row, item in items:
            print(f"- **{item}**: [description] | Units: [X] | Percentage: [X%] | Useful Life: [X years]")

print("\n" + "=" * 80)
print("Script completed.")