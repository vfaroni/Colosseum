#!/usr/bin/env python3
"""
Inspect QCT data structure and contents
"""

import pandas as pd
import os

def inspect_qct_data():
    """Inspect QCT data structure"""
    
    print("🔍 INSPECTING QCT DATA STRUCTURE")
    print("="*50)
    
    # Load QCT data
    qct_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data/qct_data_2025.xlsx"
    qct_data = pd.read_excel(qct_file)
    
    print(f"Total records: {len(qct_data)}")
    print(f"Columns: {list(qct_data.columns)}")
    
    # Show first few records
    print("\nFirst 3 records:")
    print(qct_data.head(3))
    
    # Check for Texas data (state code 48)
    if 'state' in qct_data.columns:
        texas_data = qct_data[qct_data['state'] == 48]
        print(f"\nTexas records (state=48): {len(texas_data)}")
        
        if len(texas_data) > 0:
            print("Sample Texas records:")
            print(texas_data.head(3))
            
            # Check unique counties in Texas
            unique_counties = texas_data['county'].unique()
            print(f"\nUnique Texas counties: {len(unique_counties)}")
            print(f"Sample counties: {sorted(unique_counties)[:10]}")
            
            # Check if 201 (Harris) exists
            if 201 in unique_counties:
                harris_data = texas_data[texas_data['county'] == 201]
                print(f"\nHarris County (201) records: {len(harris_data)}")
                if len(harris_data) > 0:
                    print("Harris County sample:")
                    print(harris_data.head())
            else:
                print(f"\n❌ Harris County (201) NOT FOUND")
                print(f"Available counties around 201: {[c for c in sorted(unique_counties) if 190 <= c <= 210]}")
    else:
        print("❌ No 'state' column found")
        
    # Check data types
    print(f"\nData types:")
    print(qct_data.dtypes)
    
    # Check for any QCT=1 records
    if 'qct' in qct_data.columns:
        qct_count = len(qct_data[qct_data['qct'] == 1])
        print(f"\nTotal QCT designated tracts: {qct_count}")

if __name__ == "__main__":
    inspect_qct_data()