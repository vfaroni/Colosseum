#!/usr/bin/env python3
"""
Find the unit mix table in CTCAC applications
"""

import pandas as pd

def find_unit_mix_data():
    file_path = '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data/2025_4pct_R1_25-464.xlsx'
    
    print("🔍 SEARCHING FOR UNIT MIX TABLE")
    print("=" * 50)
    
    # Check multiple tabs that might contain unit data
    excel_file = pd.ExcelFile(file_path)
    tabs_to_check = ['Application', 'Basis & Credits', 'Points System']
    
    for tab_name in tabs_to_check:
        if tab_name in excel_file.sheet_names:
            print(f"\n📋 Checking tab: {tab_name}")
            df = pd.read_excel(file_path, sheet_name=tab_name, header=None)
            
            # Look for unit mix table headers
            for idx in range(min(400, len(df))):
                row = df.iloc[idx, :15].values
                row_str = ' '.join([str(x) for x in row if str(x) != 'nan']).lower()
                
                # Look for unit mix indicators
                if any(term in row_str for term in ['studio', '1 br', '2 br', '3 br', 'bedroom']):
                    print(f"\nRow {idx}: POTENTIAL UNIT TABLE")
                    
                    # Show this row and next few rows
                    for show_idx in range(idx, min(idx + 8, len(df))):
                        show_row = df.iloc[show_idx, :12].values
                        clean_row = [str(x) for x in show_row if str(x) != 'nan']
                        if clean_row:
                            print(f"  {show_idx:3d}: {clean_row}")
                    break
    
    # Also check for specific ranges where unit data is typically found
    print(f"\n🎯 CHECKING TYPICAL UNIT MIX LOCATIONS")
    app_df = pd.read_excel(file_path, sheet_name='Application', header=None)
    
    # Check rows 300-500 where unit mix is often located
    for idx in range(300, min(500, len(app_df))):
        row = app_df.iloc[idx, :10].values
        if any(str(x).lower() in ['studio', '1 br', '2 br', '3 br'] for x in row):
            print(f"\nFOUND UNIT TABLE at Row {idx}:")
            for show_idx in range(idx-2, min(idx + 10, len(app_df))):
                show_row = app_df.iloc[show_idx, :10].values
                clean_row = [str(x) for x in show_row if str(x) != 'nan']
                if clean_row:
                    print(f"  {show_idx:3d}: {clean_row}")
            break

if __name__ == "__main__":
    find_unit_mix_data()