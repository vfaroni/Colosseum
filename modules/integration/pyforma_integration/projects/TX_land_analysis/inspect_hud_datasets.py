#!/usr/bin/env python3
"""
Inspect the actual structure of the 4 HUD QCT/DDA datasets to understand column names
"""

import pandas as pd
import os

def inspect_datasets():
    """Inspect all 4 HUD datasets to understand their structure"""
    
    data_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
    
    print("🔍 INSPECTING ALL 4 HUD QCT/DDA DATASETS")
    print("=" * 60)
    
    # 1. QCT Data 2025 (should contain both Metro and Non-Metro)
    qct_file = os.path.join(data_path, "qct_data_2025.xlsx")
    if os.path.exists(qct_file):
        print(f"\n1. QCT DATA 2025: {qct_file}")
        df = pd.read_excel(qct_file)
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        
        if len(df) > 0:
            print(f"   Sample record:")
            for col in df.columns:
                print(f"     {col}: {df[col].iloc[0]}")
        
        # Check for Texas data specifically
        if 'State' in df.columns:
            tx_count = len(df[df['State'] == 'TX'])
            print(f"   Texas records: {tx_count}")
        elif 'STATE' in df.columns:
            tx_count = len(df[df['STATE'] == '48'])
            print(f"   Texas records (FIPS 48): {tx_count}")
    
    # 2. Non-Metro QCT CSV
    nonmetro_qct_file = os.path.join(data_path, "QCT2025.csv")
    if os.path.exists(nonmetro_qct_file):
        print(f"\n2. NON-METRO QCT CSV: {nonmetro_qct_file}")
        df = pd.read_csv(nonmetro_qct_file)
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        
        if len(df) > 0:
            print(f"   Sample record:")
            for col in df.columns:
                print(f"     {col}: {df[col].iloc[0]}")
        
        # Check for Texas data
        if 'STATE' in df.columns:
            tx_count = len(df[df['STATE'] == '48'])
            print(f"   Texas records (FIPS 48): {tx_count}")
    
    # 3. Metro DDA Data
    metro_dda_file = os.path.join(data_path, "2025-DDAs-Data-Used-to-Designate.xlsx")
    if os.path.exists(metro_dda_file):
        print(f"\n3. METRO DDA DATA: {metro_dda_file}")
        df = pd.read_excel(metro_dda_file)
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        
        if len(df) > 0:
            print(f"   Sample record:")
            for col in df.columns:
                print(f"     {col}: {df[col].iloc[0]}")
        
        # Check for Texas data
        if 'State' in df.columns:
            tx_count = len(df[df['State'] == 'TX'])
            print(f"   Texas records: {tx_count}")
        elif 'STATE' in df.columns:
            tx_count = len(df[df['STATE'] == '48'])
            print(f"   Texas records (FIPS 48): {tx_count}")
    
    # 4. Non-Metro DDA Data
    nonmetro_dda_file = os.path.join(data_path, "nonmetro_dda_2025.csv")
    if os.path.exists(nonmetro_dda_file):
        print(f"\n4. NON-METRO DDA DATA: {nonmetro_dda_file}")
        df = pd.read_csv(nonmetro_dda_file)
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        
        if len(df) > 0:
            print(f"   Sample record:")
            for col in df.columns:
                print(f"     {col}: {df[col].iloc[0]}")
        
        # Check for Texas data
        if 'State' in df.columns:
            tx_count = len(df[df['State'] == 'TX'])
            print(f"   Texas records: {tx_count}")
        elif 'STATE' in df.columns:
            tx_count = len(df[df['STATE'] == '48'])
            print(f"   Texas records (FIPS 48): {tx_count}")
    
    print(f"\n" + "=" * 60)
    print("🎯 SUMMARY FOR TEXAS QCT/DDA ANALYSIS")
    print("Now you can see the actual column names to use in the comprehensive analyzer!")

if __name__ == "__main__":
    inspect_datasets()