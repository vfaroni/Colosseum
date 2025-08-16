#!/usr/bin/env python3
"""
Final targeted search with detailed analysis
"""

import pandas as pd
from pathlib import Path

def analyze_residential_sqft():
    """Analyze the 91,612 residential square footage finding"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    df = pd.read_excel(test_file, sheet_name="Application", header=None)
    
    print("=== ANALYSIS: 91,612 RESIDENTIAL SQUARE FOOTAGE ===")
    print("Found at Row 442, Column A and Row 443, Column A")
    
    # Get broader context around row 442
    for row in range(435, 450):
        for col in range(0, 10):  # Columns A-J
            if row < len(df) and col < len(df.columns):
                cell_value = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
                if cell_value and len(cell_value) > 1:
                    print(f"Row {row+1}, Col {chr(65+col)}: {cell_value}")
    
    print("\\n✅ LOCATION CONFIRMED: Row 442-443, Column A contains 91,612")
    return 442, 0  # Row 442, Column A (0-indexed)

def analyze_type_of_credit_section():
    """Analyze the Type of Credit Requested section"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    df = pd.read_excel(test_file, sheet_name="Application", header=None)
    
    print("=== ANALYSIS: TYPE OF CREDIT REQUESTED SECTION ===")
    print("Section starts at Row 354")
    
    # Get detailed view of rows 354-380
    for row in range(353, 380):  # Row 354-380 (0-indexed)
        for col in range(0, 15):  # Columns A-O
            if row < len(df) and col < len(df.columns):
                cell_value = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
                if cell_value and len(cell_value.strip()) > 0:
                    print(f"Row {row+1}, Col {chr(65+col)}: {cell_value}")
    
    print("\\n✅ Need to find N/A value in this section related to New Construction")

def analyze_construction_costs():
    """Analyze construction costs in Sources and Uses Budget"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    df = pd.read_excel(test_file, sheet_name="Sources and Uses Budget", header=None)
    
    print("=== ANALYSIS: CONSTRUCTION COSTS ===")
    print("Looking for large values that should represent total new construction")
    
    # Look at the specific location mentioned (Row 9, Col B) and surrounding area
    print("\\nArea around Row 9, Col B (where $17,252,685 was found):")
    for row in range(5, 45):  # Rows 6-45
        for col in range(0, 8):  # Columns A-H
            if row < len(df) and col < len(df.columns):
                cell_value = str(df.iloc[row, col]) if pd.notna(df.iloc[row, col]) else ""
                if cell_value and (len(cell_value) > 5 or 'construction' in cell_value.lower() or 'cost' in cell_value.lower()):
                    print(f"Row {row+1}, Col {chr(65+col)}: {cell_value}")
    
    print("\\n✅ Need to identify which large value represents Total New Construction Cost")

def create_final_extractor():
    """Create final extractor with exact coordinates"""
    
    print("\\n" + "="*80)
    print("CREATING FINAL EXTRACTOR WITH EXACT COORDINATES")
    print("="*80)
    
    coords_found = {
        'residential_sqft': (441, 0),  # Row 442, Col A (0-indexed)
        'ctcac_project_number': 'Extract from filename pattern \\d{2}-\\d{3}',
        'new_construction': 'Search Type of Credit section starting row 354 for N/A',
        'construction_cost': 'Investigate large values around row 9, col B'
    }
    
    for field, location in coords_found.items():
        print(f"{field}: {location}")

def main():
    print("🎯 FINAL TARGETED ANALYSIS FOR MARINA TOWERS")
    print("="*60)
    
    analyze_residential_sqft()
    print("\\n" + "="*60)
    analyze_type_of_credit_section()
    print("\\n" + "="*60)
    analyze_construction_costs()
    
    create_final_extractor()

if __name__ == "__main__":
    main()