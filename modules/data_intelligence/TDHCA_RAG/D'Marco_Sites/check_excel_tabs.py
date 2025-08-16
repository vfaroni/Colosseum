#!/usr/bin/env python3
"""
Check Excel file tab structure for QCT data
"""

import pandas as pd
import os

def check_excel_tabs():
    """Check all tabs in the QCT Excel file"""
    
    print("🔍 CHECKING QCT EXCEL FILE STRUCTURE")
    print("="*50)
    
    qct_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data/qct_data_2025.xlsx"
    
    if not os.path.exists(qct_file):
        print("❌ QCT file not found")
        return
        
    try:
        # Get all sheet names
        excel_file = pd.ExcelFile(qct_file)
        sheet_names = excel_file.sheet_names
        
        print(f"📋 Found {len(sheet_names)} tabs/sheets:")
        for i, sheet in enumerate(sheet_names, 1):
            print(f"   {i}. {sheet}")
        
        # Check each sheet for data
        for sheet_name in sheet_names:
            print(f"\n📊 SHEET: {sheet_name}")
            print("-" * 30)
            
            try:
                df = pd.read_excel(qct_file, sheet_name=sheet_name)
                print(f"   Records: {len(df)}")
                
                if len(df) > 0:
                    print(f"   Columns: {list(df.columns)[:5]}...")  # First 5 columns
                    
                    # Check for Texas (state=48)
                    if 'state' in df.columns:
                        unique_states = sorted(df['state'].unique())
                        print(f"   State range: {min(unique_states)} to {max(unique_states)}")
                        
                        if 48 in unique_states:
                            texas_count = (df['state'] == 48).sum()
                            print(f"   ✅ TEXAS FOUND: {texas_count} records (state=48)")
                            
                            # Check Harris County (201) specifically
                            if 'county' in df.columns:
                                harris_count = ((df['state'] == 48) & (df['county'] == 201)).sum()
                                print(f"   🏙️ Harris County: {harris_count} tracts")
                                
                                if harris_count > 0:
                                    # Show sample Harris County QCT tract
                                    harris_sample = df[(df['state'] == 48) & (df['county'] == 201) & (df['qct'] == 1)]
                                    if len(harris_sample) > 0:
                                        sample = harris_sample.iloc[0]
                                        print(f"   🎯 Sample Harris QCT: State={sample['state']}, County={sample['county']}, Tract={sample['tract']}")
                        else:
                            print("   ❌ No Texas data in this sheet")
                    else:
                        print("   ⚠️ No 'state' column found")
                        
                    # Show sample records
                    print("   Sample records:")
                    print(df.head(2).to_string())
                        
            except Exception as e:
                print(f"   ❌ Error reading sheet: {e}")
        
    except Exception as e:
        print(f"❌ Error opening Excel file: {e}")

if __name__ == "__main__":
    check_excel_tabs()