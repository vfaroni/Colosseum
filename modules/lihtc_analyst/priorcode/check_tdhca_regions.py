#!/usr/bin/env python3

import pandas as pd

def check_tdhca_regions_file():
    """Check the TDHCA_Regions.xlsx file to understand its structure"""
    
    regions_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/TDHCA_Regions/TDHCA_Regions.xlsx"
    
    print("="*80)
    print("TDHCA REGIONS FILE ANALYSIS")
    print("="*80)
    
    try:
        # Read the Excel file
        excel_file = pd.ExcelFile(regions_file)
        print(f"📊 Sheet names: {excel_file.sheet_names}")
        print()
        
        # Check each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"🔍 SHEET: {sheet_name}")
            print("-" * 50)
            
            df = pd.read_excel(regions_file, sheet_name=sheet_name)
            print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            print(f"Columns: {list(df.columns)}")
            
            # Show first few rows
            print("First 5 rows:")
            print(df.head().to_string(index=True))
            print()
            
            # Check for county-region mapping
            if any('county' in col.lower() for col in df.columns) and any('region' in col.lower() for col in df.columns):
                county_col = None
                region_col = None
                
                for col in df.columns:
                    if 'county' in col.lower():
                        county_col = col
                    if 'region' in col.lower():
                        region_col = col
                
                if county_col and region_col:
                    print(f"🎯 FOUND COUNTY-REGION MAPPING!")
                    print(f"County column: {county_col}")
                    print(f"Region column: {region_col}")
                    print(f"Unique counties: {df[county_col].nunique()}")
                    print(f"Unique regions: {df[region_col].nunique()}")
                    
                    # Show mapping sample
                    print("\nSample county-region mappings:")
                    sample_mapping = df[[county_col, region_col]].drop_duplicates().head(10)
                    print(sample_mapping.to_string(index=False))
                    
            print("\n" + "="*50 + "\n")
            
    except Exception as e:
        print(f"❌ ERROR reading file: {str(e)}")
        return None
    
    return True

if __name__ == "__main__":
    check_tdhca_regions_file()