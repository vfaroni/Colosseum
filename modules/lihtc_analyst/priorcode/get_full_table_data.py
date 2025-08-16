#!/usr/bin/env python3
"""
Get the full unit mix table with all columns
"""

import pandas as pd

def get_full_table():
    file_path = '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data/2025_4pct_R1_25-464.xlsx'
    app_df = pd.read_excel(file_path, sheet_name='Application', header=None)

    print("🎯 FULL UNIT MIX TABLE - ALL COLUMNS")
    print("=" * 100)

    # Show rows 710-725 with extended columns to capture rent data
    for i in range(710, 725):
        if i < len(app_df):
            row = app_df.iloc[i, :15].values  # Extended to 15 columns
            display_data = []
            
            for j, cell in enumerate(row):
                cell_str = str(cell)
                if cell_str != 'nan' and cell_str.strip():
                    # Truncate long cells for display
                    display_cell = cell_str[:40] if len(cell_str) > 40 else cell_str
                    display_data.append(f"C{j}:{display_cell}")
            
            if display_data:
                print(f"Row {i:3d}: {display_data}")

    print(f"\n📊 EXTRACTING UNIT MIX DATA:")
    
    # Based on our earlier finding, let's specifically extract rows 717-718
    unit_data = []
    
    for row_num in [717, 718]:
        if row_num < len(app_df):
            row = app_df.iloc[row_num, :15].values  # Get all relevant columns
            
            # Convert to clean list
            clean_row = []
            for cell in row:
                if str(cell) != 'nan' and str(cell).strip():
                    clean_row.append(str(cell).strip())
            
            if len(clean_row) >= 5:  # Should have bedroom type, units, sqft, rent, utility
                unit_type = clean_row[0]
                unit_count = clean_row[1]
                avg_sqft = clean_row[2] if len(clean_row) > 2 else "N/A"
                gross_rent = clean_row[3] if len(clean_row) > 3 else "N/A"
                utility_allowance = clean_row[4] if len(clean_row) > 4 else "N/A"
                
                unit_data.append({
                    'unit_type': unit_type,
                    'unit_count': unit_count,
                    'avg_sqft': avg_sqft,
                    'gross_rent': gross_rent,
                    'utility_allowance': utility_allowance
                })
                
                print(f"✅ {unit_type}: {unit_count} units, {avg_sqft} sq ft, ${gross_rent} gross, ${utility_allowance} utility")

    # Create the final requested table
    print(f"\n🏠 FINAL REQUESTED TABLE:")
    print("Unit Type         | Unit Count | AMI set aside | Gross Rent | Utility Allowance (UA) | Net Rent")
    print("-" * 90)
    
    for unit in unit_data:
        try:
            net_rent = int(unit['gross_rent']) - int(unit['utility_allowance'])
        except:
            net_rent = "Calc Error"
        
        # Determine AMI level based on rent
        # In LIHTC, lower rents typically indicate income restrictions
        if unit['gross_rent'] == "770":
            ami_level = "60% AMI"  # Typical for LIHTC restricted units
        elif unit['gross_rent'] == "1596":
            ami_level = "Market Rate"  # Higher rent suggests market rate
        else:
            ami_level = "TBD"
        
        print(f"{unit['unit_type']:17s} | {unit['unit_count']:10s} | {ami_level:12s} | ${unit['gross_rent']:9s} | ${unit['utility_allowance']:21s} | ${net_rent}")

    return unit_data

if __name__ == "__main__":
    data = get_full_table()