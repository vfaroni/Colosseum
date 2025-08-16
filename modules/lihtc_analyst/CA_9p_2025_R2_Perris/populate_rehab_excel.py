#!/usr/bin/env python3
"""
Script to populate the Rehabilitation Summary Excel file with construction cost data.
This script reads construction cost data from a markdown file and populates the 
Excel template starting at cell B7, maintaining the same order and categories.
"""

import openpyxl
from pathlib import Path
import re
from typing import Dict, List, Tuple

# File paths
excel_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CA_9p_2025_R2_Perris/9_Percent_Applications/TAB_08__Rehabilitation_Credit_Applications/Exhbit-B-RAWFILE_Att-8-Rehab Summary.xlsx")
output_file = excel_file.parent / "Exhbit-B-POPULATED_Att-8-Rehab Summary.xlsx"

# Example construction cost data structure
# Replace this with actual data parsed from your markdown file
# Format: (description, number_of_units, percentage, estimated_useful_life)
construction_data = {
    # SITE section (starts at row 7)
    "Carports/Garages": ("Replace carport roofing and structural repairs", "", "", "15 years"),
    "Drainage": ("Improve site drainage and storm water management", "", "", "20 years"),
    "Fencing": ("Replace perimeter fencing", "", "", "15 years"),
    "Landscaping/Topography": ("Refresh landscaping and irrigation", "", "", "10 years"),
    "Lighting": ("LED retrofit for site lighting", "", "", "20 years"),
    "Parking/Roadways": ("Resurface parking areas and striping", "", "", "15 years"),
    "Recreation Areas": ("Upgrade playground equipment", "", "", "15 years"),
    "Sidewalks/Pedestrian Areas": ("Repair concrete walkways", "", "", "20 years"),
    "Signage": ("Replace wayfinding and unit signage", "", "", "10 years"),
    "Trash Facilities": ("Upgrade trash enclosures", "", "", "15 years"),
    "Maintenance Shed": ("", "", "", ""),
    "Utilities": ("Underground utility upgrades", "", "", "25 years"),
    # Add more items as needed...
}

def parse_markdown_file(markdown_path: Path) -> Dict[str, Tuple[str, str, str, str]]:
    """
    Parse construction cost data from a markdown file.
    
    This is a placeholder function - modify it to match your markdown file format.
    Expected to return a dictionary mapping rehabilitation items to their details.
    """
    # TODO: Implement actual markdown parsing logic based on your file format
    # For now, returning the example data
    return construction_data

def populate_excel(data: Dict[str, Tuple[str, str, str, str]]):
    """
    Populate the Excel file with construction cost data.
    """
    print(f"Loading Excel file: {excel_file}")
    wb = openpyxl.load_workbook(excel_file)
    sheet = wb.active
    
    # Column mapping
    col_description = 'B'  # Comments/Brief Description (merged with C)
    col_units = 'D'        # Number of Units
    col_percentage = 'E'   # Percentage
    col_useful_life = 'F'  # Estimated Remaining Useful Life
    
    # Track which rows have been populated
    populated_rows = []
    
    # Iterate through the Excel file to find matching items
    for row in range(7, sheet.max_row + 1):
        cell_a = sheet[f'A{row}']
        if cell_a.value and isinstance(cell_a.value, str):
            item_name = cell_a.value.strip()
            
            # Check if we have data for this item
            if item_name in data:
                description, units, percentage, useful_life = data[item_name]
                
                # Populate the cells
                if description:
                    sheet[f'{col_description}{row}'] = description
                if units:
                    sheet[f'{col_units}{row}'] = units
                if percentage:
                    sheet[f'{col_percentage}{row}'] = percentage
                if useful_life:
                    sheet[f'{col_useful_life}{row}'] = useful_life
                
                populated_rows.append(row)
                print(f"Populated row {row}: {item_name}")
    
    # Save the populated file
    wb.save(output_file)
    print(f"\nFile saved as: {output_file}")
    print(f"Total rows populated: {len(populated_rows)}")
    
    return populated_rows

def main():
    """
    Main function to coordinate the population process.
    """
    print("Rehabilitation Summary Excel Population Script")
    print("=" * 50)
    
    # TODO: Update this to point to your actual markdown file
    # markdown_file = Path("path/to/your/construction_costs.md")
    # data = parse_markdown_file(markdown_file)
    
    # For now, using the example data
    data = construction_data
    
    # Populate the Excel file
    populated_rows = populate_excel(data)
    
    print("\nProcess completed successfully!")
    
    # Display summary of populated items
    print("\nPopulated items:")
    for item, (desc, units, pct, life) in data.items():
        if desc:  # Only show items with descriptions
            print(f"  - {item}: {desc[:50]}...")

if __name__ == "__main__":
    main()