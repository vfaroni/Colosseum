#!/usr/bin/env python3
"""
Check available Texas QCT files
"""

import pandas as pd
import os

def check_texas_qct_files():
    """Check Texas QCT files"""
    
    print("🔍 CHECKING TEXAS QCT FILES")
    print("="*50)
    
    # Files to check
    files_to_check = [
        "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data/QCT2025.csv",
        "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/texas_qct_FEDERAL_ONLY_20250531_183850.xlsx",
        "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Costar/TX/CS_Land_TX_1_10ac_05312025_DDAQCT_ONLY.xlsx"
    ]
    
    for file_path in files_to_check:
        print(f"\n📁 Checking: {os.path.basename(file_path)}")
        
        if os.path.exists(file_path):
            print("✅ File exists")
            
            try:
                # Try to load based on extension
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                print(f"   Records: {len(df)}")
                print(f"   Columns: {list(df.columns)[:10]}")  # First 10 columns
                
                # Check for Texas data
                texas_indicators = ['TX', 'Texas', '48']
                texas_found = False
                
                for col in df.columns:
                    if df[col].dtype == 'object':
                        for indicator in texas_indicators:
                            if df[col].astype(str).str.contains(indicator, na=False).any():
                                texas_count = df[col].astype(str).str.contains(indicator, na=False).sum()
                                print(f"   ✅ Found {texas_count} {indicator} records in column '{col}'")
                                texas_found = True
                                break
                    elif col.lower() in ['state', 'state_code', 'fips_state']:
                        if 48 in df[col].values:
                            texas_count = (df[col] == 48).sum()
                            print(f"   ✅ Found {texas_count} Texas records (state=48) in column '{col}'")
                            texas_found = True
                
                if not texas_found:
                    print("   ❌ No Texas data found")
                
                # Show sample
                print("   Sample records:")
                print(df.head(2).to_string())
                
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
        else:
            print("❌ File not found")

if __name__ == "__main__":
    check_texas_qct_files()