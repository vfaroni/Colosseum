#!/usr/bin/env python3
"""
Examine the new HUD QCT 2025 data to understand its structure and check for Arizona
"""

import pandas as pd
import os

def examine_qct_data():
    """Examine the new QCT data files"""
    
    base_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
    
    # First, read the data dictionary
    dict_file = os.path.join(base_path, "QCT2025csv_dictonary.txt")
    if os.path.exists(dict_file):
        print("="*60)
        print("QCT 2025 DATA DICTIONARY")
        print("="*60)
        with open(dict_file, 'r') as f:
            print(f.read())
    
    # Examine the CSV file
    csv_file = os.path.join(base_path, "QCT2025.csv")
    if os.path.exists(csv_file):
        print("\n" + "="*60)
        print("QCT 2025 CSV DATA STRUCTURE")
        print("="*60)
        
        # Read the CSV
        df = pd.read_csv(csv_file)
        
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Show first few rows
        print(f"\nFirst 5 rows:")
        print(df.head())
        
        # Check for Arizona data
        if 'STATE' in df.columns:
            az_data = df[df['STATE'] == 'AZ']
            print(f"\nArizona records: {len(az_data)}")
            if len(az_data) > 0:
                print(f"Arizona QCT tracts:")
                print(az_data[['STATE', 'COUNTY', 'TRACT', 'QCT']].head(10))
        elif 'State' in df.columns:
            az_data = df[df['State'] == 'AZ']
            print(f"\nArizona records: {len(az_data)}")
            if len(az_data) > 0:
                print(f"Arizona QCT tracts:")
                print(az_data[['State', 'County', 'Tract']].head(10))
        else:
            print("\nNo obvious state field found")
            print(f"Available columns: {df.columns.tolist()}")
            
        # Check unique values in QCT field if it exists
        if 'QCT' in df.columns:
            qct_values = df['QCT'].unique()
            print(f"\nUnique QCT values: {qct_values}")
            qct_count = df['QCT'].value_counts()
            print(f"\nQCT value counts:")
            print(qct_count)
            
    # Examine the Excel file
    excel_file = os.path.join(base_path, "qct_data_2025.xlsx")
    if os.path.exists(excel_file):
        print("\n" + "="*60)
        print("QCT 2025 EXCEL DATA STRUCTURE")
        print("="*60)
        
        # Read the Excel file
        df_excel = pd.read_excel(excel_file)
        
        print(f"Shape: {df_excel.shape}")
        print(f"Columns: {list(df_excel.columns)}")
        
        # Show first few rows
        print(f"\nFirst 5 rows:")
        print(df_excel.head())
        
        # Check for Arizona data
        state_cols = [col for col in df_excel.columns if 'state' in col.lower()]
        if state_cols:
            state_col = state_cols[0]
            az_data = df_excel[df_excel[state_col] == 'AZ']
            print(f"\nArizona records: {len(az_data)}")
            if len(az_data) > 0:
                print(f"Sample Arizona data:")
                print(az_data.head(10))
        else:
            print("\nNo obvious state field found")
            print(f"Available columns: {df_excel.columns.tolist()}")
            
        # Check for QCT designation fields
        qct_cols = [col for col in df_excel.columns if 'qct' in col.lower()]
        if qct_cols:
            print(f"\nQCT-related columns: {qct_cols}")
            for col in qct_cols:
                unique_vals = df_excel[col].unique()
                print(f"Unique values in '{col}': {unique_vals}")

def check_nogales_area():
    """Specifically check for data around Nogales, Arizona"""
    
    base_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
    csv_file = os.path.join(base_path, "QCT2025.csv")
    excel_file = os.path.join(base_path, "qct_data_2025.xlsx")
    
    # Nogales is in Santa Cruz County, Arizona
    # United Church Village Apts is at 31.3713391, -110.9240253
    
    print("\n" + "="*60)
    print("CHECKING NOGALES AREA SPECIFICALLY")
    print("="*60)
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        
        # Look for Santa Cruz County, Arizona
        if 'STATE' in df.columns and 'COUNTY' in df.columns:
            az_data = df[df['STATE'] == 'AZ']
            print(f"All Arizona counties in dataset:")
            if len(az_data) > 0:
                counties = az_data['COUNTY'].unique()
                print(counties)
                
                # Look specifically for Santa Cruz County
                santa_cruz = az_data[az_data['COUNTY'].str.contains('Santa Cruz', case=False, na=False)]
                if len(santa_cruz) > 0:
                    print(f"\nSanta Cruz County, AZ data:")
                    print(santa_cruz[['STATE', 'COUNTY', 'TRACT', 'QCT']])
                else:
                    print(f"\nNo Santa Cruz County found. Available AZ counties:")
                    print(sorted(counties))
            
    if os.path.exists(excel_file):
        df_excel = pd.read_excel(excel_file)
        
        # Find state and county columns
        state_cols = [col for col in df_excel.columns if 'state' in col.lower()]
        county_cols = [col for col in df_excel.columns if 'county' in col.lower()]
        
        if state_cols and county_cols:
            state_col = state_cols[0]
            county_col = county_cols[0]
            
            az_data = df_excel[df_excel[state_col] == 'AZ']
            print(f"\nExcel file - All Arizona counties:")
            if len(az_data) > 0:
                counties = az_data[county_col].unique()
                print(sorted(counties))
                
                # Look for Santa Cruz County
                santa_cruz = az_data[az_data[county_col].str.contains('Santa Cruz', case=False, na=False)]
                if len(santa_cruz) > 0:
                    print(f"\nSanta Cruz County, AZ data from Excel:")
                    print(santa_cruz.head())

if __name__ == "__main__":
    examine_qct_data()
    check_nogales_area()