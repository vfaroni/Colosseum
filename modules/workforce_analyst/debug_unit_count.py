#!/usr/bin/env python3
"""
Debug the unit count discrepancy (105 vs 102)
"""

import pandas as pd

def debug_unit_count():
    rent_roll_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Deals/Sunset Gardens - El Cajon, CA/02. Rent Roll/Sunset Gardens - Rent Roll - 6.23.2025.xlsx"
    
    df = pd.read_excel(rent_roll_path, sheet_name='Report1')
    
    # Start from header row 3 + 1 = row 4
    data_df = df.iloc[4:].copy()
    
    print("=== ANALYZING ALL ROWS FROM DATA SECTION ===")
    
    unit_col = 'Rent Roll'  # Column 0
    
    count = 0
    for idx, row in data_df.iterrows():
        unit_val = row[unit_col]
        unit_str = str(unit_val).strip()
        
        # Check if this should be excluded
        is_summary = any(term in unit_str.lower() for term in ['total', 'summary', 'future', 'vacant residents', 'applicants'])
        is_null = pd.isna(unit_val) or unit_str == '' or unit_str == 'nan'
        
        if not is_null and not is_summary:
            count += 1
            print(f"Row {idx}: '{unit_val}' -> INCLUDED")
        else:
            print(f"Row {idx}: '{unit_val}' -> excluded ({'null' if is_null else 'summary'})")
    
    print(f"\nTotal units counted: {count}")
    
    # Check the last few rows to see what might be causing the discrepancy
    print("\n=== LAST 10 ROWS OF DATA ===")
    last_10 = data_df.tail(10)
    for idx, row in last_10.iterrows():
        unit_val = row[unit_col]
        print(f"Row {idx}: '{unit_val}'")

if __name__ == "__main__":
    debug_unit_count()