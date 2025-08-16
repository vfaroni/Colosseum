#!/usr/bin/env python3
"""
Extract the specific unit mix table data from CTCAC application
"""

import pandas as pd

def extract_unit_mix():
    file_path = '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data/2025_4pct_R1_25-464.xlsx'
    app_df = pd.read_excel(file_path, sheet_name='Application', header=None)

    print("🏠 UNIT MIX TABLE EXTRACTION")
    print("=" * 50)

    # Search around the area where we found unit data
    start_row = 740
    end_row = 800
    
    unit_data = []
    
    print(f"📊 Scanning rows {start_row}-{end_row} for unit mix table:")
    print()
    
    for i in range(start_row, min(end_row, len(app_df))):
        row = app_df.iloc[i, :15].values
        clean_row = []
        for x in row:
            if str(x) != 'nan':
                clean_row.append(str(x))
        
        if clean_row:
            row_text = ' '.join(clean_row).lower()
            
            # Print relevant rows
            if any(term in row_text for term in ['unit', 'bedroom', 'rent', 'ami', 'gross', 'utility']) or \
               any(item.isdigit() and len(item) <= 3 for item in clean_row):
                print(f"Row {i:3d}: {clean_row}")
    
    # Now look for the actual unit mix table structure
    print(f"\n🎯 LOOKING FOR UNIT MIX TABLE STRUCTURE:")
    print("Searching for standard CTCAC unit mix format...")
    
    # Look for table headers like "Unit Type", "Number of Units", etc.
    for i in range(400, min(900, len(app_df))):
        row = app_df.iloc[i, :20].values
        row_str = ' '.join([str(x) for x in row if str(x) != 'nan']).lower()
        
        # Check for unit table indicators
        if 'studio' in row_str or '1 br' in row_str or '2 br' in row_str:
            print(f"\n✅ FOUND POTENTIAL UNIT TABLE at Row {i}:")
            
            # Show table structure (this row and next 10 rows)
            for j in range(i, min(i + 12, len(app_df))):
                table_row = app_df.iloc[j, :15].values
                clean_table_row = [str(x) for x in table_row if str(x) != 'nan']
                if clean_table_row:
                    print(f"  {j:3d}: {clean_table_row}")
            break

if __name__ == "__main__":
    extract_unit_mix()