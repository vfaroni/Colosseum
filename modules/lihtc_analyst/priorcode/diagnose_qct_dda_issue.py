#!/usr/bin/env python3
"""Diagnose why only 9 QCT/DDA sites are being included"""

import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def diagnose_qct_dda():
    """Examine QCT/DDA columns in both Excel files"""
    
    # File paths
    dmarco_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/DMarco_Sites_Final_PositionStack_20250618_235606.xlsx")
    costar_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/CoStar_Land_Analysis_With_Counties_20250617_223737.xlsx")
    
    print("=" * 80)
    print("QCT/DDA DIAGNOSIS REPORT")
    print("=" * 80)
    
    # Check D'Marco file
    if dmarco_file.exists():
        print("\n1. D'Marco Sites Analysis:")
        dmarco_df = pd.read_excel(dmarco_file)
        print(f"   Total rows: {len(dmarco_df)}")
        print("\n   Columns in file:")
        for col in dmarco_df.columns:
            print(f"   - {col}")
        
        # Look for QCT/DDA related columns
        qct_dda_cols = [col for col in dmarco_df.columns if any(term in col.upper() for term in ['QCT', 'DDA', 'QUALIFIED', 'DIFFICULT'])]
        print(f"\n   QCT/DDA related columns: {qct_dda_cols}")
        
        if qct_dda_cols:
            for col in qct_dda_cols:
                print(f"\n   {col} value counts:")
                print(dmarco_df[col].value_counts())
                print(f"   Non-null count: {dmarco_df[col].notna().sum()}")
    else:
        print(f"\nD'Marco file not found: {dmarco_file}")
    
    # Check CoStar file
    if costar_file.exists():
        print("\n\n2. CoStar Land Analysis:")
        costar_df = pd.read_excel(costar_file)
        print(f"   Total rows: {len(costar_df)}")
        print("\n   Columns in file:")
        for col in costar_df.columns:
            print(f"   - {col}")
        
        # Look for QCT/DDA related columns
        qct_dda_cols = [col for col in costar_df.columns if any(term in col.upper() for term in ['QCT', 'DDA', 'QUALIFIED', 'DIFFICULT'])]
        print(f"\n   QCT/DDA related columns: {qct_dda_cols}")
        
        if qct_dda_cols:
            for col in qct_dda_cols:
                print(f"\n   {col} value counts:")
                print(costar_df[col].value_counts())
                print(f"   Non-null count: {costar_df[col].notna().sum()}")
    else:
        print(f"\nCoStar file not found: {costar_file}")
    
    # Check Brian's CSV file
    brian_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/State Specific/TX/TDHCA_RAG/D'Marco_Sites/From_Brian_06202025.csv")
    
    if brian_file.exists():
        print("\n\n3. Brian's D'Marco Sites CSV:")
        brian_df = pd.read_csv(brian_file)
        print(f"   Total rows: {len(brian_df)}")
        print("\n   Columns in file:")
        for col in brian_df.columns:
            print(f"   - {col}")
        
        # Look for QCT/DDA column
        if 'QCT/DDA' in brian_df.columns:
            print(f"\n   QCT/DDA column value counts:")
            print(brian_df['QCT/DDA'].value_counts())
            print(f"   Non-null count: {brian_df['QCT/DDA'].notna().sum()}")
            
            # Show some examples
            print("\n   Examples of QCT/DDA values:")
            qct_dda_sites = brian_df[brian_df['QCT/DDA'].notna()]
            if len(qct_dda_sites) > 0:
                for idx, row in qct_dda_sites.head(10).iterrows():
                    print(f"   - {row.get('Name', 'Unknown')}: '{row['QCT/DDA']}'")
    else:
        print(f"\nBrian's file not found: {brian_file}")
    
    # Check analyzer output
    print("\n\n4. Checking recent QCT/DDA analysis outputs:")
    output_pattern = "QCT_DDA_Corrected_Analysis_*.xlsx"
    output_files = list(Path(".").glob(output_pattern))
    
    if output_files:
        latest_output = sorted(output_files)[-1]
        print(f"   Latest output file: {latest_output}")
        output_df = pd.read_excel(latest_output)
        print(f"   Total sites in output: {len(output_df)}")
        
        # Check sources
        if 'Source' in output_df.columns:
            print("\n   Sites by source:")
            print(output_df['Source'].value_counts())
    else:
        print("   No output files found")

if __name__ == "__main__":
    diagnose_qct_dda()