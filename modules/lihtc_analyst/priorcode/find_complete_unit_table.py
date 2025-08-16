#!/usr/bin/env python3
"""
Find the complete unit mix table with AMI, rents, and utility allowances
"""

import pandas as pd

def find_complete_unit_table():
    file_path = '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data/2025_4pct_R1_25-464.xlsx'
    
    print("🎯 FINDING COMPLETE UNIT MIX TABLE")
    print("Target: Unit Type, Unit Count, AMI set aside, Gross Rent, Utility Allowance, Net Rent")
    print("=" * 80)
    
    # Load Application tab
    app_df = pd.read_excel(file_path, sheet_name='Application', header=None)
    
    # Search for the rent table that usually appears before the unit counts
    print("🔍 Searching for rent table sections...")
    
    # Look for sections with rent-related keywords
    rent_sections = []
    for i in range(len(app_df) - 50):
        # Check 5-row windows for rent table indicators
        window_text = ""
        for j in range(5):
            if i + j < len(app_df):
                row_text = ' '.join([str(x) for x in app_df.iloc[i + j, :10].values if str(x) != 'nan'])
                window_text += row_text.lower() + " "
        
        # Look for rent table indicators
        if any(term in window_text for term in ['gross rent', 'utility allowance', 'net rent', 'ami']) and \
           any(term in window_text for term in ['studio', '1 br', '2 br', '3 br', 'bedroom']):
            rent_sections.append(i)
    
    print(f"📋 Found {len(rent_sections)} potential rent table sections")
    
    # Check each potential section
    for section_start in rent_sections[:3]:  # Check first 3 sections
        print(f"\n🎯 EXAMINING SECTION starting at Row {section_start}:")
        
        # Show 20 rows from this section
        for i in range(section_start, min(section_start + 20, len(app_df))):
            row = app_df.iloc[i, :15].values
            clean_row = [str(x) for x in row if str(x) != 'nan' and str(x).strip()]
            if clean_row:
                print(f"  {i:3d}: {clean_row}")
    
    # Also check the area we know has unit counts (around 752)
    print(f"\n🏠 EXAMINING KNOWN UNIT COUNT AREA (Row 740-800):")
    for i in range(740, min(800, len(app_df))):
        row = app_df.iloc[i, :20].values
        clean_row = [str(x) for x in row if str(x) != 'nan' and str(x).strip()]
        if clean_row and len(clean_row) > 1:
            # Show rows that have multiple columns (likely table data)
            print(f"  {i:3d}: {clean_row}")
    
    # Search broader for actual tabular data (rows with 4+ columns)
    print(f"\n📊 SEARCHING FOR TABULAR DATA (4+ columns):")
    table_rows = []
    
    for i in range(len(app_df)):
        row = app_df.iloc[i, :20].values
        clean_row = [str(x).strip() for x in row if str(x) != 'nan' and str(x).strip()]
        
        # Look for rows with 4+ meaningful columns
        if len(clean_row) >= 4:
            row_text = ' '.join(clean_row).lower()
            # Check if it contains unit-related terms
            if any(term in row_text for term in ['studio', '1 br', '2 br', '3 br', 'bedroom', 'unit']) or \
               any(term in row_text for term in ['rent', 'ami', 'utility', 'gross', 'net']):
                table_rows.append((i, clean_row))
    
    print(f"Found {len(table_rows)} potential table rows")
    for i, (row_num, row_data) in enumerate(table_rows[:15]):  # Show first 15
        print(f"  {row_num:3d}: {row_data}")

if __name__ == "__main__":
    find_complete_unit_table()