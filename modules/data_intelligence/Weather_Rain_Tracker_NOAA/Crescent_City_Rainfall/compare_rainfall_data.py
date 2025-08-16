#!/usr/bin/env python3
"""
Compare KCEC weather data with external Hayden Rain Info data
"""

import os
import pandas as pd
from datetime import datetime
import openpyxl

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "weather_data")

def read_hayden_data():
    """Read and parse Hayden's rain data from Excel"""
    excel_file = os.path.join(DATA_DIR, "ACG_Weather_Data", "Hayden_Rain_Info_2024.xlsx")
    
    print(f"Reading Hayden's data from: {excel_file}")
    
    # Read Excel file
    df = pd.read_excel(excel_file)
    
    # Print column names to understand structure
    print(f"\nColumns in Hayden's data: {list(df.columns)}")
    print(f"First few rows:")
    print(df.head())
    
    return df

def read_kcec_data():
    """Read our KCEC data"""
    # Find the most recent full 2024 file
    import glob
    pattern = os.path.join(DATA_DIR, "kcec_full_2024_*.csv")
    files = glob.glob(pattern)
    
    if not files:
        print("ERROR: No full 2024 KCEC data found")
        return None
    
    # Get most recent file
    latest_file = max(files, key=os.path.getctime)
    print(f"Reading KCEC data from: {latest_file}")
    
    df = pd.read_csv(latest_file)
    df['Date'] = pd.to_datetime(df['Date'])
    
    return df

def compare_data():
    """Compare the two datasets"""
    
    # Read both datasets
    hayden_df = read_hayden_data()
    kcec_df = read_kcec_data()
    
    if kcec_df is None:
        return
    
    print("\n" + "="*60)
    print("DATA COMPARISON ANALYSIS")
    print("="*60)
    
    # KCEC Summary
    print("\nKCEC Weather Station Data Summary:")
    print(f"Total days: {len(kcec_df)}")
    
    kcec_rainy = (kcec_df['Total_Inches'] > 0).sum()
    kcec_measurable = (kcec_df['Total_Inches'] >= 0.01).sum()
    kcec_total = kcec_df['Total_Inches'].sum()
    
    print(f"Days with any rain (>0): {kcec_rainy}")
    print(f"Days with measurable rain (≥0.01\"): {kcec_measurable}")
    print(f"Total rainfall: {kcec_total:.2f} inches")
    
    # Monthly breakdown for KCEC
    kcec_df['Month'] = kcec_df['Date'].dt.month
    kcec_monthly = kcec_df.groupby('Month').agg({
        'Total_Inches': ['sum', lambda x: (x > 0).sum(), lambda x: (x >= 0.01).sum()]
    })
    kcec_monthly.columns = ['Total_Inches', 'Any_Rain_Days', 'Measurable_Days']
    
    print("\nKCEC Monthly Breakdown:")
    print("-" * 50)
    for month, row in kcec_monthly.iterrows():
        month_name = datetime(2024, month, 1).strftime('%B')
        print(f"{month_name:10} | {row['Total_Inches']:6.2f}\" | Any rain: {int(row['Any_Rain_Days']):2d} | Measurable: {int(row['Measurable_Days']):2d}")
    
    # Create comparison output
    output_file = os.path.join(DATA_DIR, f"rainfall_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    with open(output_file, 'w') as f:
        f.write("KCEC vs External Data Comparison\n")
        f.write("="*60 + "\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("KCEC Weather Station Summary:\n")
        f.write(f"Total days: {len(kcec_df)}\n")
        f.write(f"Days with any rain: {kcec_rainy}\n")
        f.write(f"Days with measurable rain (≥0.01\"): {kcec_measurable}\n")
        f.write(f"Total rainfall: {kcec_total:.2f} inches\n\n")
        
        f.write("Monthly Breakdown:\n")
        f.write("-" * 50 + "\n")
        for month, row in kcec_monthly.iterrows():
            month_name = datetime(2024, month, 1).strftime('%B')
            f.write(f"{month_name:10} | {row['Total_Inches']:6.2f}\" | Any rain: {int(row['Any_Rain_Days']):2d} | Measurable: {int(row['Measurable_Days']):2d}\n")
    
    print(f"\nComparison saved to: {output_file}")
    
    # Also save a detailed daily comparison CSV
    daily_file = os.path.join(DATA_DIR, f"daily_rain_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    # Create daily comparison dataframe
    daily_comp = kcec_df[['Date', 'Total_Inches']].copy()
    daily_comp['Has_Rain'] = daily_comp['Total_Inches'] > 0
    daily_comp['Has_Measurable'] = daily_comp['Total_Inches'] >= 0.01
    daily_comp['Category'] = kcec_df['Category']
    
    daily_comp.to_csv(daily_file, index=False)
    print(f"Daily data saved to: {daily_file}")
    
    return hayden_df, kcec_df

if __name__ == "__main__":
    print("Comparing KCEC weather data with external data...")
    hayden_df, kcec_df = compare_data()
    
    # Note about Google Sheets
    print("\n" + "="*60)
    print("NOTE: I don't have direct access to your Google Sheets.")
    print("You mentioned a sheet at:")
    print("https://docs.google.com/spreadsheets/d/1sVo6MOtIwqX2_0nxANHnkOODQnUvzlCSynr91ORI1Ms/")
    print("\nThe KCEC data has been prepared for comparison.")
    print("You can upload the daily comparison CSV to Google Sheets for further analysis.")