#!/usr/bin/env python3
"""Check D'Marco Excel files to find the actual property data"""

import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def check_file(file_path):
    """Check an Excel file for property data"""
    print(f"\nChecking: {file_path.name}")
    
    try:
        # Try to read all sheets
        excel_file = pd.ExcelFile(file_path)
        print(f"  Sheets: {excel_file.sheet_names}")
        
        for sheet in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet)
            print(f"\n  Sheet '{sheet}': {len(df)} rows")
            if len(df) > 0:
                print(f"  First few columns: {list(df.columns[:5])}")
                
                # Check for QCT/DDA columns
                qct_dda_cols = [col for col in df.columns if any(term in str(col).upper() for term in ['QCT', 'DDA'])]
                if qct_dda_cols:
                    print(f"  QCT/DDA columns found: {qct_dda_cols}")
                    for col in qct_dda_cols:
                        non_null = df[col].notna().sum()
                        if non_null > 0:
                            print(f"    {col}: {non_null} non-null values")
                
    except Exception as e:
        print(f"  Error reading file: {e}")

# Check all D'Marco files
files_to_check = [
    "DMarco_Sites_Analysis_20250618_233123.xlsx",
    "DMarco_Sites_Analysis_20250618_233604.xlsx", 
    "DMarco_Sites_Final_PositionStack_20250618_235606.xlsx"
]

for filename in files_to_check:
    file_path = Path(filename)
    if file_path.exists():
        check_file(file_path)