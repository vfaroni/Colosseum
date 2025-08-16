#!/usr/bin/env python3
"""
Show the complete unit mix table structure
"""

import pandas as pd

def show_complete_table():
    file_path = '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data/2025_4pct_R1_25-464.xlsx'
    app_df = pd.read_excel(file_path, sheet_name='Application', header=None)

    print("🎯 COMPLETE UNIT MIX TABLE STRUCTURE")
    print("Previously found: Row 713 header, Row 717-718 data")
    print("=" * 70)

    # Show rows 710-730 to get the complete table context
    for i in range(710, 730):
        if i < len(app_df):
            row = app_df.iloc[i, :8].values
            clean_row = []
            for x in row:
                if str(x) != 'nan':
                    clean_row.append(str(x))
            
            if clean_row:  # Only show non-empty rows
                print(f"Row {i:3d}: {clean_row}")

    print(f"\n📊 CREATING FINAL TABLE:")
    print("Unit Type | Unit Count | AMI set aside | Gross Rent | Utility Allowance (UA) | Net Rent")
    print("-" * 85)

    # Extract the specific data rows we found earlier
    for row_num in [717, 718]:
        if row_num < len(app_df):
            row = app_df.iloc[row_num, :6].values
            clean_row = []
            for x in row:
                if str(x) != 'nan' and str(x).strip():
                    clean_row.append(str(x).strip())
            
            if len(clean_row) >= 5:
                unit_type = clean_row[0]
                unit_count = clean_row[1]
                gross_rent = clean_row[3]
                utility_allowance = clean_row[4]
                
                # Calculate net rent
                try:
                    net_rent = int(gross_rent) - int(utility_allowance)
                except:
                    net_rent = "Error"
                
                # For AMI, we need to determine based on rent levels
                # LIHTC rent of $770 suggests 60% AMI, $1596 suggests market rate
                if gross_rent == "770":
                    ami_set_aside = "60% AMI"
                elif gross_rent == "1596":
                    ami_set_aside = "Market Rate"
                else:
                    ami_set_aside = "TBD"
                
                print(f"{unit_type:9s} | {unit_count:10s} | {ami_set_aside:12s} | ${gross_rent:9s} | ${utility_allowance:21s} | ${net_rent}")

if __name__ == "__main__":
    show_complete_table()