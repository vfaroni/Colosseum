#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path

def check_excel_data_quality():
    """Check the data quality of the QCT_DDA_Comprehensive_Analysis Excel file"""
    
    file_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/Final_Corrected_QCT_DDA_Analysis_20250620_215624.xlsx"
    
    print("="*80)
    print("EXCEL DATA QUALITY VERIFICATION REPORT")
    print("="*80)
    print(f"File: {Path(file_path).name}")
    print()
    
    try:
        # Read the Excel file
        excel_file = pd.ExcelFile(file_path)
        print(f"📊 Sheet names: {excel_file.sheet_names}")
        print()
        
        # Focus on the main data sheet
        if "All_QCT_DDA_Sites" in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name="All_QCT_DDA_Sites")
        else:
            # Try first sheet
            df = pd.read_excel(file_path, sheet_name=0)
        
        print(f"📋 Dataset shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print()
        
        # Column analysis
        print("📝 COLUMN ANALYSIS")
        print("-" * 50)
        print(f"Columns: {list(df.columns)}")
        print()
        
        # Issue 1: Check TDHCA_Region population
        print("🏛️  ISSUE 1: TDHCA_Region Population Check")
        print("-" * 50)
        if 'TDHCA_Region' in df.columns:
            region_stats = df['TDHCA_Region'].value_counts(dropna=False)
            null_count = df['TDHCA_Region'].isnull().sum()
            print(f"✅ TDHCA_Region column exists")
            print(f"✅ Total records: {len(df)}")
            print(f"✅ Null/empty values: {null_count}")
            print(f"✅ Populated values: {len(df) - null_count}")
            if null_count == 0:
                print("✅ SUCCESS: All TDHCA_Region values are populated!")
            else:
                print(f"❌ ISSUE: {null_count} records missing TDHCA_Region")
            print(f"Region distribution: {dict(region_stats)}")
        else:
            print("❌ MISSING: TDHCA_Region column not found")
        print()
        
        # Issue 2: Check Land_Acres data quality
        print("🏞️  ISSUE 2: Land_Acres Data Quality")
        print("-" * 50)
        if 'Land_Acres' in df.columns:
            acres_stats = df['Land_Acres'].describe()
            null_count = df['Land_Acres'].isnull().sum()
            print(f"✅ Land_Acres column exists")
            print(f"✅ Null values: {null_count}")
            print(f"✅ Data type: {df['Land_Acres'].dtype}")
            print(f"✅ Sample values: {df['Land_Acres'].head().tolist()}")
            print(f"✅ Statistics:\n{acres_stats}")
            
            # Check for duplicate "Land Area (AC)" issue
            has_text_issue = df['Land_Acres'].astype(str).str.contains('Land Area', na=False).any()
            if has_text_issue:
                print("❌ ISSUE: Found 'Land Area (AC)' text in data")
            else:
                print("✅ SUCCESS: No 'Land Area (AC)' text found")
        else:
            print("❌ MISSING: Land_Acres column not found")
        print()
        
        # Issue 3: Check Poverty_Rate formatting
        print("📊 ISSUE 3: Poverty_Rate Percentage Formatting")
        print("-" * 50)
        if 'Poverty_Rate' in df.columns:
            poverty_stats = df['Poverty_Rate'].describe()
            null_count = df['Poverty_Rate'].isnull().sum()
            sample_values = df['Poverty_Rate'].dropna().head(10).tolist()
            print(f"✅ Poverty_Rate column exists")
            print(f"✅ Null values: {null_count}")
            print(f"✅ Data type: {df['Poverty_Rate'].dtype}")
            print(f"✅ Sample values: {sample_values}")
            print(f"✅ Statistics:\n{poverty_stats}")
            
            # Check if values are in percentage format
            sample_str = str(sample_values[0]) if sample_values else ""
            if "%" in sample_str:
                print("✅ SUCCESS: Values are in percentage format with % symbol (e.g., 37.76%)")
            else:
                print("❌ ISSUE: Values may not be in proper percentage format")
        else:
            print("❌ MISSING: Poverty_Rate column not found")
        print()
        
        # Issue 4: Check FEMA_Zone population
        print("🌊 ISSUE 4: FEMA_Zone Population Check")
        print("-" * 50)
        if 'FEMA_Zone' in df.columns:
            fema_stats = df['FEMA_Zone'].value_counts(dropna=False)
            unknown_count = (df['FEMA_Zone'] == 'Unknown').sum()
            total_records = len(df)
            print(f"✅ FEMA_Zone column exists")
            print(f"✅ Total records: {total_records}")
            print(f"✅ 'Unknown' values: {unknown_count}")
            print(f"✅ Known zones: {total_records - unknown_count}")
            print(f"✅ Zone distribution: {dict(fema_stats)}")
            
            if unknown_count == total_records:
                print("❌ ISSUE: All FEMA_Zone values are 'Unknown'")
            elif unknown_count == 0:
                print("✅ SUCCESS: No 'Unknown' FEMA_Zone values!")
            else:
                print(f"✅ PARTIAL: {total_records - unknown_count} zones properly identified")
        else:
            print("❌ MISSING: FEMA_Zone column not found")
        print()
        
        # Issue 5: Check data variation between rows
        print("🔄 ISSUE 5: Data Variation Between Rows")
        print("-" * 50)
        key_columns = ['TDHCA_Region', 'Land_Acres', 'Poverty_Rate', 'FEMA_Zone']
        for col in key_columns:
            if col in df.columns:
                unique_count = df[col].nunique()
                total_count = len(df)
                print(f"✅ {col}: {unique_count} unique values out of {total_count} records")
                if unique_count == 1:
                    print(f"❌ WARNING: {col} has same value for all records")
                elif unique_count > 1:
                    print(f"✅ SUCCESS: {col} has proper variation")
        print()
        
        # Issue 6: Check Weighted_AMI_Rent variation by county
        print("💰 ISSUE 6: Weighted_AMI_Rent County Variation")
        print("-" * 50)
        if 'Weighted_AMI_Rent' in df.columns and 'County' in df.columns:
            rent_by_county = df.groupby('County')['Weighted_AMI_Rent'].agg(['count', 'mean', 'std', 'nunique']).round(2)
            print(f"✅ AMI Rent variation by county:")
            print(rent_by_county.head(10))
            
            total_unique_rents = df['Weighted_AMI_Rent'].nunique()
            total_counties = df['County'].nunique()
            print(f"✅ Total unique rent values: {total_unique_rents}")
            print(f"✅ Total counties: {total_counties}")
            
            if total_unique_rents > 1:
                print("✅ SUCCESS: AMI rents vary properly")
            else:
                print("❌ ISSUE: All AMI rents are identical")
        else:
            missing_cols = []
            if 'Weighted_AMI_Rent' not in df.columns:
                missing_cols.append('Weighted_AMI_Rent')
            if 'County' not in df.columns:
                missing_cols.append('County')
            print(f"❌ MISSING: Columns not found: {missing_cols}")
        print()
        
        # Issue 7: Check for empty columns
        print("🗂️  ISSUE 7: Empty Column Check")
        print("-" * 50)
        empty_columns = []
        for col in df.columns:
            if df[col].isnull().all():
                empty_columns.append(col)
        
        if empty_columns:
            print(f"❌ FOUND {len(empty_columns)} empty columns: {empty_columns}")
        else:
            print("✅ SUCCESS: No completely empty columns found!")
        print()
        
        # Overall summary
        print("📋 OVERALL DATA QUALITY SUMMARY")
        print("-" * 50)
        print(f"✅ Total records: {len(df)}")
        print(f"✅ Total columns: {len(df.columns)}")
        
        # Check first few rows for duplicate data issue
        print("\n🔍 FIRST 5 ROWS SAMPLE:")
        print("-" * 50)
        display_cols = ['TDHCA_Region', 'Land_Acres', 'Poverty_Rate', 'FEMA_Zone', 'Weighted_AMI_Rent']
        available_cols = [col for col in display_cols if col in df.columns]
        if available_cols:
            print(df[available_cols].head().to_string(index=True))
        else:
            print("No key columns available for display")
        
        print("\n" + "="*80)
        print("VERIFICATION COMPLETE")
        print("="*80)
        
    except Exception as e:
        print(f"❌ ERROR reading file: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    check_excel_data_quality()