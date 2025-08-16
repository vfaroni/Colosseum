#!/usr/bin/env python3
"""
Quick Unit Mix Extraction from CTCAC Application
Create the table requested: Unit Type, Unit Count, AMI set aside, Gross Rent, Utility Allowance, Net Rent
"""

import pandas as pd
from pathlib import Path

def extract_unit_mix_table():
    file_path = '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data/2025_4pct_R1_25-464.xlsx'
    
    print("🏠 QUICK UNIT MIX EXTRACTION")
    print("=" * 50)
    
    # Try the main Application tab
    app_df = pd.read_excel(file_path, sheet_name='Application', header=None)
    print(f"📊 Application tab size: {app_df.shape}")
    
    # Search for unit mix table by looking for bedroom types
    unit_indicators = ['studio', '1 br', '2 br', '3 br', '4 br', 'bedroom']
    rent_indicators = ['gross rent', 'utility', 'net rent', 'ami']
    
    # Scan for unit table
    unit_table_found = False
    for start_row in range(50, min(600, len(app_df))):
        # Check if this row contains unit types
        row_text = ' '.join([str(x) for x in app_df.iloc[start_row, :15].values if str(x) != 'nan']).lower()
        
        if any(indicator in row_text for indicator in unit_indicators):
            print(f"\n🎯 POTENTIAL UNIT TABLE at Row {start_row}")
            print(f"Content: {row_text}")
            
            # Show table structure
            print(f"\n📋 UNIT MIX TABLE STRUCTURE:")
            for i in range(max(0, start_row-2), min(start_row + 15, len(app_df))):
                row_data = app_df.iloc[i, :12].values
                clean_data = [str(x) for x in row_data if str(x) != 'nan']
                if clean_data:
                    print(f"Row {i:3d}: {clean_data}")
            
            unit_table_found = True
            break
    
    if not unit_table_found:
        print("\n❌ Unit mix table not found in typical locations")
        print("🔍 Searching entire Application tab...")
        
        # Broader search
        for row_idx in range(0, min(1000, len(app_df)), 50):
            sample_text = ' '.join([str(x) for x in app_df.iloc[row_idx:row_idx+10, :5].values.flatten() if str(x) != 'nan']).lower()
            if any(indicator in sample_text for indicator in unit_indicators):
                print(f"Found unit indicators around row {row_idx}")
                
                # Show surrounding area
                for i in range(row_idx, min(row_idx + 20, len(app_df))):
                    row_data = app_df.iloc[i, :8].values
                    clean_data = [str(x) for x in row_data if str(x) != 'nan' and len(str(x)) > 1]
                    if clean_data:
                        print(f"Row {i:3d}: {clean_data}")
                break
    
    # Also check other potential tabs
    print(f"\n🔍 CHECKING OTHER TABS FOR UNIT DATA:")
    excel_file = pd.ExcelFile(file_path)
    
    for tab_name in ['Basis & Credits', 'Points System']:
        if tab_name in excel_file.sheet_names:
            print(f"\n📋 Checking {tab_name}...")
            tab_df = pd.read_excel(file_path, sheet_name=tab_name, header=None)
            
            # Quick scan for unit indicators
            found_units = False
            for idx in range(min(200, len(tab_df))):
                row_text = ' '.join([str(x) for x in tab_df.iloc[idx, :10].values if str(x) != 'nan']).lower()
                if any(indicator in row_text for indicator in unit_indicators):
                    print(f"✅ Unit data found at row {idx}: {row_text}")
                    found_units = True
                    break
            
            if not found_units:
                print(f"❌ No unit data found in {tab_name}")

if __name__ == "__main__":
    extract_unit_mix_table()