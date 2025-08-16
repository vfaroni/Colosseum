#!/usr/bin/env python3
"""
Fix the CSV format issues:
1. Update filename to reflect correct date range (2024 only)
2. Change Yes/No to 1/0 for rainfall categories
3. Add dedicated threshold columns for easy counting
"""

import os
import pandas as pd
from datetime import datetime
import glob

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "weather_data")

def fix_csv_format():
    """Fix the CSV format with correct columns and filename"""
    
    print("Fixing CSV format issues...")
    
    # Find the most recent complete dataset
    pattern = os.path.join(DATA_DIR, "kcec_complete_2024_to_present_*.csv")
    files = glob.glob(pattern)
    
    if not files:
        print("ERROR: No complete dataset found")
        return None
    
    latest_file = max(files, key=os.path.getctime)
    print(f"Reading: {latest_file}")
    
    # Read the data
    df = pd.read_csv(latest_file)
    print(f"Original records: {len(df)}")
    
    # Convert Yes/No to 1/0 for easier calculations
    df['Measurable_0.01'] = (df['Total_Inches'] >= 0.01).astype(int)
    df['Light_0.01'] = ((df['Total_Inches'] >= 0.01) & (df['Total_Inches'] < 0.25)).astype(int)
    df['Moderate_0.25'] = ((df['Total_Inches'] >= 0.25) & (df['Total_Inches'] < 0.5)).astype(int)
    df['Heavy_0.5'] = ((df['Total_Inches'] >= 0.5) & (df['Total_Inches'] < 1.0)).astype(int)
    df['Very_Heavy_1.0'] = (df['Total_Inches'] >= 1.0).astype(int)
    
    # Add dedicated threshold columns for easy counting
    df['Contract_0.10'] = (df['Total_Inches'] >= 0.10).astype(int)  # Contract threshold
    df['Normal_0.25'] = (df['Total_Inches'] >= 0.25).astype(int)    # Normal threshold
    df['Heavy_0.50'] = (df['Total_Inches'] >= 0.50).astype(int)     # Heavy threshold
    
    # Update work suitability to 1/0
    df['Work_Suitable'] = (df['Total_Inches'] < 0.5).astype(int)  # 1 = suitable, 0 = not suitable
    
    # Add date components for analysis
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    df['Day_of_Week'] = df['Date'].dt.day_name()
    df['Month_Name'] = df['Date'].dt.strftime('%B')
    
    # Verify date range
    start_date = df['Date'].min()
    end_date = df['Date'].max()
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Reorder columns for logical flow
    columns = [
        'Date', 'Year', 'Month', 'Day', 'Month_Name', 'Day_of_Week',
        'Total_Inches', 'Category',
        'Measurable_0.01', 'Contract_0.10', 'Normal_0.25', 'Heavy_0.50',
        'Light_0.01', 'Moderate_0.25', 'Heavy_0.5', 'Very_Heavy_1.0',
        'Work_Suitable', 'Timestamp'
    ]
    
    df_fixed = df[columns]
    
    # Create corrected filename
    output_file = os.path.join(DATA_DIR, f"kcec_complete_2024_FIXED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df_fixed.to_csv(output_file, index=False)
    
    print(f"\nFixed dataset saved to: {output_file}")
    
    # Show summary of threshold columns
    print(f"\nSUMMARY OF THRESHOLD COLUMNS:")
    print(f"Contract_0.10 (≥0.10\"): {df_fixed['Contract_0.10'].sum()} days")
    print(f"Normal_0.25 (≥0.25\"):   {df_fixed['Normal_0.25'].sum()} days") 
    print(f"Heavy_0.50 (≥0.50\"):    {df_fixed['Heavy_0.50'].sum()} days")
    
    # Show first few rows to verify format
    print(f"\nFIRST 5 ROWS (verification):")
    print(df_fixed[['Date', 'Total_Inches', 'Contract_0.10', 'Normal_0.25', 'Heavy_0.50']].head())
    
    # Monthly summary using the new columns
    print(f"\nMONTHLY SUMMARY USING NEW COLUMNS:")
    monthly = df_fixed.groupby(['Month', 'Month_Name']).agg({
        'Total_Inches': 'sum',
        'Contract_0.10': 'sum',
        'Normal_0.25': 'sum',
        'Heavy_0.50': 'sum'
    }).reset_index()
    
    print(f"{'Month':10} | {'Total':>8} | {'≥0.10\"':>7} | {'≥0.25\"':>7} | {'≥0.50\"':>7}")
    print(f"{'':10} | {'Inches':>8} | {'Days':>7} | {'Days':>7} | {'Days':>7}")
    print("-" * 50)
    
    for _, row in monthly.iterrows():
        month_name = row['Month_Name']
        total = row['Total_Inches']
        contract = int(row['Contract_0.10'])
        normal = int(row['Normal_0.25'])
        heavy = int(row['Heavy_0.50'])
        
        print(f"{month_name:10} | {total:8.2f} | {contract:7d} | {normal:7d} | {heavy:7d}")
    
    return output_file

if __name__ == "__main__":
    print("Fixing CSV format issues")
    print("="*40)
    
    fixed_file = fix_csv_format()
    
    if fixed_file:
        print(f"\n*** SUCCESS! ***")
        print("Issues fixed:")
        print("1. ✅ Filename now reflects 2024 data only")
        print("2. ✅ Yes/No changed to 1/0 for easy calculations")
        print("3. ✅ Added Contract_0.10 column for ≥0.10\" days")
        print("4. ✅ Added Normal_0.25 column for ≥0.25\" days")
        print("5. ✅ Added Heavy_0.50 column for ≥0.50\" days")
        print(f"\nFixed file: {fixed_file}")
    else:
        print("Failed to fix CSV format")