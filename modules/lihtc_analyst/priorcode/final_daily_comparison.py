#!/usr/bin/env python3
"""
Final comparison of KCEC vs Hayden's daily rainfall data
Handles the year mismatch in Hayden's data (shows 2025 but represents 2024)
"""

import os
import pandas as pd
from datetime import datetime
import numpy as np
import openpyxl

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "weather_data")

def read_hayden_daily_2024():
    """Read Hayden's daily data and convert 2025 dates to 2024"""
    excel_file = os.path.join(DATA_DIR, "ACG_Weather_Data", "Hayden_Rain_Info_2024.xlsx")
    
    print("Reading Hayden's daily rainfall data...")
    
    # Read the first sheet
    df = pd.read_excel(excel_file, sheet_name=0)
    
    # Create clean dataframe with the data we need
    hayden_data = pd.DataFrame()
    
    # Column B (index 1) has dates, Column E (index 4) has precipitation
    hayden_data['Date'] = pd.to_datetime(df.iloc[:, 1])  # Column B
    hayden_data['High_Temp'] = df.iloc[:, 2]  # Column C
    hayden_data['Low_Temp'] = df.iloc[:, 3]  # Column D  
    hayden_data['Precip_Hayden'] = df.iloc[:, 4]  # Column E
    
    # Convert 2025 dates to 2024 (since this is actually 2024 data)
    # Also handle leap year properly
    hayden_data['Date'] = hayden_data['Date'].apply(lambda x: x.replace(year=2024) if x.year == 2025 else x)
    
    # Filter to only 2024 data
    hayden_2024 = hayden_data[hayden_data['Date'].dt.year == 2024].copy()
    
    print(f"  Loaded {len(hayden_2024)} days of Hayden's 2024 data")
    print(f"  Date range: {hayden_2024['Date'].min().strftime('%Y-%m-%d')} to {hayden_2024['Date'].max().strftime('%Y-%m-%d')}")
    
    return hayden_2024

def read_kcec_2024():
    """Read our KCEC 2024 data"""
    # Use the full 2024 file we already have
    kcec_file = os.path.join(DATA_DIR, "kcec_full_2024_20250623_181642.csv")
    
    print("\nReading KCEC weather station data...")
    
    df = pd.read_csv(kcec_file)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Rename precipitation column for clarity
    df['Precip_KCEC'] = df['Total_Inches']
    
    print(f"  Loaded {len(df)} days of KCEC 2024 data")
    print(f"  Date range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
    
    return df

def compare_daily_rainfall():
    """Create detailed daily comparison"""
    
    # Read both datasets
    hayden_df = read_hayden_daily_2024()
    kcec_df = read_kcec_2024()
    
    # Merge on date
    comparison = pd.merge(
        kcec_df[['Date', 'Precip_KCEC']],
        hayden_df[['Date', 'Precip_Hayden', 'High_Temp', 'Low_Temp']],
        on='Date',
        how='outer',
        indicator=True
    )
    
    comparison = comparison.sort_values('Date')
    
    # Calculate differences and rain day flags
    comparison['Diff_Inches'] = comparison['Precip_KCEC'] - comparison['Precip_Hayden']
    comparison['KCEC_Rain_0.10'] = comparison['Precip_KCEC'] >= 0.10
    comparison['Hayden_Rain_0.10'] = comparison['Precip_Hayden'] >= 0.10
    comparison['Both_Agree_0.10'] = comparison['KCEC_Rain_0.10'] == comparison['Hayden_Rain_0.10']
    
    print("\n" + "="*80)
    print("DAILY RAINFALL COMPARISON - 2024 FULL YEAR")
    print("="*80)
    
    # Overall statistics
    total_days = len(comparison)
    both_have_data = comparison[comparison['_merge'] == 'both']
    
    print(f"\nData Coverage:")
    print(f"  Total days: {total_days}")
    print(f"  Days with both sources: {len(both_have_data)}")
    print(f"  KCEC only: {len(comparison[comparison['_merge'] == 'left_only'])}")
    print(f"  Hayden only: {len(comparison[comparison['_merge'] == 'right_only'])}")
    
    # Rain day comparison (0.10" contract threshold)
    print(f"\nContract Rain Days (≥0.10\"):")
    kcec_rain_days = comparison['KCEC_Rain_0.10'].sum()
    hayden_rain_days = comparison['Hayden_Rain_0.10'].sum()
    
    # For days where both have data
    both_data = both_have_data.copy()
    agree_days = both_data['Both_Agree_0.10'].sum()
    disagree_days = len(both_data) - agree_days
    
    print(f"  KCEC total: {kcec_rain_days} days")
    print(f"  Hayden total: {hayden_rain_days} days")
    print(f"  Agreement rate: {agree_days}/{len(both_data)} days ({agree_days/len(both_data)*100:.1f}%)")
    
    # Show disagreements
    disagreements = both_data[~both_data['Both_Agree_0.10']].copy()
    
    if len(disagreements) > 0:
        print(f"\nDays with disagreement on contract rain (≥0.10\"):")
        print(f"Total: {len(disagreements)} days")
        
        print(f"\n{'Date':12} | {'KCEC':>8} | {'Hayden':>8} | {'Diff':>8} | {'Issue':>25}")
        print("-"*70)
        
        for idx, row in disagreements.head(20).iterrows():
            date_str = row['Date'].strftime('%Y-%m-%d')
            kcec_val = f"{row['Precip_KCEC']:.2f}"
            hayden_val = f"{row['Precip_Hayden']:.2f}"
            diff_val = f"{row['Diff_Inches']:+.2f}"
            
            if row['KCEC_Rain_0.10'] and not row['Hayden_Rain_0.10']:
                issue = "KCEC shows rain, Hayden doesn't"
            else:
                issue = "Hayden shows rain, KCEC doesn't"
            
            print(f"{date_str:12} | {kcec_val:>8} | {hayden_val:>8} | {diff_val:>8} | {issue:>25}")
        
        if len(disagreements) > 20:
            print(f"... and {len(disagreements) - 20} more disagreements")
    
    # Monthly comparison
    comparison['Month'] = comparison['Date'].dt.month
    
    # Create monthly summary manually to avoid lambda column name issues
    monthly_summary = []
    for month_num in range(1, 13):
        month_data = comparison[comparison['Month'] == month_num]
        if len(month_data) > 0:
            kcec_total = month_data['Precip_KCEC'].sum()
            hayden_total = month_data['Precip_Hayden'].sum()
            kcec_rain_days = (month_data['Precip_KCEC'] >= 0.10).sum()
            hayden_rain_days = (month_data['Precip_Hayden'] >= 0.10).sum()
            agreement = month_data['Both_Agree_0.10'].sum()
        else:
            kcec_total = hayden_total = kcec_rain_days = hayden_rain_days = agreement = 0
        
        monthly_summary.append({
            'Month': month_num,
            'KCEC_Total': kcec_total,
            'Hayden_Total': hayden_total,
            'KCEC_Days': kcec_rain_days,
            'Hayden_Days': hayden_rain_days,
            'Agreement': agreement
        })
    
    print("\n" + "="*80)
    print("MONTHLY COMPARISON")
    print("="*80)
    print(f"\n{'Month':10} | {'KCEC':>12} | {'Hayden':>12} | {'KCEC':>12} | {'Hayden':>12}")
    print(f"{'':10} | {'Total \"':>12} | {'Total \"':>12} | {'Rain Days':>12} | {'Rain Days':>12}")
    print("-"*70)
    
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    total_kcec_rain = 0
    total_hayden_rain = 0
    total_kcec_days = 0
    total_hayden_days = 0
    
    for month_data in monthly_summary:
        month_num = month_data['Month']
        month_name = month_names[month_num-1]
        
        kcec_total = month_data['KCEC_Total']
        hayden_total = month_data['Hayden_Total']
        kcec_days = month_data['KCEC_Days']
        hayden_days = month_data['Hayden_Days']
        
        total_kcec_rain += kcec_total
        total_hayden_rain += hayden_total
        total_kcec_days += kcec_days
        total_hayden_days += hayden_days
        
        print(f"{month_name:10} | {kcec_total:12.2f} | {hayden_total:12.2f} | {kcec_days:12d} | {hayden_days:12d}")
    
    print("-"*70)
    print(f"{'TOTAL':10} | {total_kcec_rain:12.2f} | {total_hayden_rain:12.2f} | {total_kcec_days:12d} | {total_hayden_days:12d}")
    
    # Save detailed comparison
    output_file = os.path.join(DATA_DIR, f"final_daily_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    # Clean up for export
    export_df = comparison.drop('_merge', axis=1)
    export_df['Day_of_Week'] = export_df['Date'].dt.day_name()
    export_df = export_df[['Date', 'Day_of_Week', 'Precip_KCEC', 'Precip_Hayden', 
                          'Diff_Inches', 'High_Temp', 'Low_Temp',
                          'KCEC_Rain_0.10', 'Hayden_Rain_0.10', 'Both_Agree_0.10']]
    
    export_df.to_csv(output_file, index=False)
    print(f"\nDetailed comparison saved to: {output_file}")
    
    print("\n" + "="*80)
    print("KEY FINDINGS:")
    print("="*80)
    print(f"1. Total rainfall difference: {total_kcec_rain - total_hayden_rain:+.2f} inches")
    print(f"2. Contract rain days difference: {total_kcec_days - total_hayden_days:+d} days")
    print(f"3. Agreement rate on contract rain days: {agree_days/len(both_data)*100:.1f}%")
    
    return export_df

if __name__ == "__main__":
    print("Final KCEC vs Hayden Daily Rainfall Comparison")
    print("Using 0.10\" contract threshold for rain day counting")
    print("-"*50)
    
    comparison_df = compare_daily_rainfall()
    
    print("\nComparison complete!")
    print("You can upload the CSV file to your Google Sheets for further analysis.")
    print("Google Sheets link: https://docs.google.com/spreadsheets/d/1sVo6MOtIwqX2_0nxANHnkOODQnUvzlCSynr91ORI1Ms/")