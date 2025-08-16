#!/usr/bin/env python3
"""
Extract the final unit mix table for user review
Target: Unit Type, Unit Count, AMI set aside, Gross Rent, Utility Allowance, Net Rent
"""

import pandas as pd

def extract_final_unit_table():
    file_path = '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data/2025_4pct_R1_25-464.xlsx'
    app_df = pd.read_excel(file_path, sheet_name='Application', header=None)

    print("🎯 FINAL UNIT MIX TABLE EXTRACTION")
    print("Target: Unit Type, Unit Count, AMI set aside, Gross Rent, Utility Allowance, Net Rent")
    print("=" * 80)

    # Extract the table starting at row 713 (where we found the header)
    table_start = 713
    
    print(f"📋 Table Header (Row {table_start}):")
    header_row = app_df.iloc[table_start, :6].values
    clean_header = []
    for x in header_row:
        if str(x) != 'nan':
            clean_header.append(str(x))
    print(f"   {clean_header}")

    print(f"\n🏠 Raw Unit Mix Data:")
    unit_rows = []
    
    # Extract data rows following the header
    for i in range(table_start + 1, table_start + 15):
        if i < len(app_df):
            row = app_df.iloc[i, :6].values
            clean_row = []
            for x in row:
                if str(x) != 'nan' and str(x).strip():
                    clean_row.append(str(x).strip())
            
            # Check if this looks like a unit data row
            if len(clean_row) >= 4:
                row_text = clean_row[0].lower()
                if 'bedroom' in row_text or 'studio' in row_text:
                    print(f"   Row {i:3d}: {clean_row}")
                    unit_rows.append(clean_row)

    # Create the requested table format
    print(f"\n📊 REQUESTED TABLE FORMAT:")
    print("Unit Type         | Unit Count | AMI set aside | Gross Rent | Utility Allowance | Net Rent")
    print("-" * 85)

    extracted_data = []
    
    for row_data in unit_rows:
        if len(row_data) >= 5:
            unit_type = row_data[0]
            unit_count = row_data[1]
            gross_rent = row_data[3]  # Column (d) from header
            utility_allowance = row_data[4]  # Column (e) from header
            
            # Calculate net rent
            try:
                net_rent = int(float(gross_rent)) - int(float(utility_allowance))
            except:
                net_rent = "Calc Error"
            
            # AMI info - need to find this in another section
            ami_set_aside = "TBD - Need to locate AMI section"
            
            # Format the row
            print(f"{unit_type:17s} | {unit_count:10s} | {ami_set_aside:12s} | ${gross_rent:9s} | ${utility_allowance:16s} | ${str(net_rent):8s}")
            
            extracted_data.append({
                'unit_type': unit_type,
                'unit_count': int(unit_count) if unit_count.isdigit() else unit_count,
                'gross_rent': float(gross_rent) if gross_rent.replace('.','').isdigit() else gross_rent,
                'utility_allowance': float(utility_allowance) if utility_allowance.replace('.','').isdigit() else utility_allowance,
                'net_rent': net_rent
            })

    print(f"\n✅ EXTRACTION SUMMARY:")
    print(f"   📊 Found {len(extracted_data)} unit types")
    print(f"   🏠 Total units: {sum(row['unit_count'] for row in extracted_data if isinstance(row['unit_count'], int))}")
    
    # Look for AMI information in the broader application
    print(f"\n🔍 SEARCHING FOR AMI SET-ASIDE INFORMATION:")
    ami_found = False
    
    # Search for AMI-related sections
    for i in range(len(app_df)):
        row = app_df.iloc[i, :10].values
        row_text = ' '.join([str(x) for x in row if str(x) != 'nan']).lower()
        
        if 'ami' in row_text and any(pct in row_text for pct in ['30%', '50%', '60%', '80%']):
            clean_row = [str(x) for x in row if str(x) != 'nan' and str(x).strip()]
            if clean_row:
                print(f"   Row {i:3d}: {clean_row}")
                ami_found = True
                if ami_found and i > 0:  # Show a few more rows for context
                    for j in range(1, 4):
                        if i + j < len(app_df):
                            next_row = app_df.iloc[i + j, :6].values
                            clean_next = [str(x) for x in next_row if str(x) != 'nan' and str(x).strip()]
                            if clean_next:
                                print(f"   Row {i+j:3d}: {clean_next}")
                    break

    return extracted_data

if __name__ == "__main__":
    data = extract_final_unit_table()