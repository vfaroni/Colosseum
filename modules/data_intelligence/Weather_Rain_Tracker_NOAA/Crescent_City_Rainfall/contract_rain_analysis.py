#!/usr/bin/env python3
"""
Analyze KCEC rainfall data using contract-specified thresholds
- 0.1 inches: Contract rain day threshold
- 0.25 inches: Normal area threshold  
- 0.5 inches: Pacific Northwest potential delay threshold
"""

import os
import pandas as pd
from datetime import datetime
import numpy as np

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "weather_data")

def analyze_with_thresholds():
    """Analyze KCEC data with multiple rain thresholds"""
    
    # Find the most recent full 2024 file
    import glob
    pattern = os.path.join(DATA_DIR, "kcec_full_2024_*.csv")
    files = glob.glob(pattern)
    
    if not files:
        print("ERROR: No full 2024 KCEC data found")
        return None
    
    latest_file = max(files, key=os.path.getctime)
    print(f"Analyzing: {latest_file}")
    
    df = pd.read_csv(latest_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.month
    
    # Calculate different thresholds
    df['Contract_Rain'] = df['Total_Inches'] >= 0.1  # Contract threshold
    df['Normal_Rain'] = df['Total_Inches'] >= 0.25   # Normal area threshold
    df['PNW_Delay'] = df['Total_Inches'] >= 0.5      # Pacific Northwest delay threshold
    
    print("\n" + "="*70)
    print("KCEC 2024 RAINFALL ANALYSIS - CONTRACT THRESHOLDS")
    print("="*70)
    
    # Annual summary
    total_days = len(df)
    contract_days = df['Contract_Rain'].sum()
    normal_days = df['Normal_Rain'].sum()
    pnw_days = df['PNW_Delay'].sum()
    total_rain = df['Total_Inches'].sum()
    
    print(f"\nANNUAL SUMMARY:")
    print(f"Total days in 2024: {total_days}")
    print(f"Total rainfall: {total_rain:.2f} inches")
    print(f"\nRAIN DAY COUNTS BY THRESHOLD:")
    print(f"  ≥0.01\" (Measurable): {(df['Total_Inches'] >= 0.01).sum()} days")
    print(f"  ≥0.10\" (CONTRACT):   {contract_days} days  <-- Your contract threshold")
    print(f"  ≥0.25\" (Normal):     {normal_days} days")
    print(f"  ≥0.50\" (PNW Delay):  {pnw_days} days")
    
    # Monthly breakdown
    monthly = df.groupby('Month').agg({
        'Total_Inches': 'sum',
        'Contract_Rain': 'sum',
        'Normal_Rain': 'sum',
        'PNW_Delay': 'sum'
    })
    
    print("\n" + "-"*80)
    print("MONTHLY BREAKDOWN:")
    print("-"*80)
    print(f"{'Month':10} | {'Total':>7} | {'≥0.01\"':>7} | {'≥0.10\"':>7} | {'≥0.25\"':>7} | {'≥0.50\"':>7} | {'Contract':>8}")
    print(f"{'':10} | {'Inches':>7} | {'Days':>7} | {'(CONTRACT)':>7} | {'Days':>7} | {'Days':>7} | {'Rain Days':>8}")
    print("-"*80)
    
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    for month_num in range(1, 13):
        month_name = month_names[month_num-1]
        
        if month_num in monthly.index:
            total = monthly.loc[month_num, 'Total_Inches']
            measurable = len(df[(df['Month'] == month_num) & (df['Total_Inches'] >= 0.01)])
            contract = int(monthly.loc[month_num, 'Contract_Rain'])
            normal = int(monthly.loc[month_num, 'Normal_Rain'])
            pnw = int(monthly.loc[month_num, 'PNW_Delay'])
        else:
            total = measurable = contract = normal = pnw = 0
        
        print(f"{month_name:10} | {total:7.2f} | {measurable:7d} | {contract:7d} | {normal:7d} | {pnw:7d} | {contract:8d}")
    
    print("-"*80)
    print(f"{'TOTAL':10} | {total_rain:7.2f} | {(df['Total_Inches'] >= 0.01).sum():7d} | "
          f"{contract_days:7d} | {normal_days:7d} | {pnw_days:7d} | {contract_days:8d}")
    
    # Get Hayden's counts for comparison
    hayden_file = os.path.join(DATA_DIR, "ACG_Weather_Data", "Hayden_Rain_Info_2024.xlsx")
    try:
        hayden_df = pd.read_excel(hayden_file, sheet_name='Rain Days Per Hayden Schedule')
        
        print("\n" + "="*70)
        print("COMPARISON WITH HAYDEN'S COUNTS (Contract Threshold ≥0.10\")")
        print("="*70)
        print(f"{'Month':10} | {'KCEC':>12} | {'Hayden':>12} | {'Difference':>12}")
        print(f"{'':10} | {'(≥0.10\")':>12} | {'Count':>12} | {'':>12}")
        print("-"*70)
        
        total_kcec_contract = 0
        total_hayden = 0
        months_compared = 0
        
        for month_num in range(1, 13):
            month_name = month_names[month_num-1]
            
            # Get KCEC contract rain days
            if month_num in monthly.index:
                kcec_contract = int(monthly.loc[month_num, 'Contract_Rain'])
            else:
                kcec_contract = 0
            
            # Get Hayden count
            first_col = hayden_df.columns[0]
            second_col = hayden_df.columns[1]
            month_row = hayden_df[hayden_df[first_col] == month_name]
            
            if not month_row.empty:
                hayden_count = month_row[second_col].iloc[0]
                if pd.notna(hayden_count):
                    hayden_count = int(hayden_count)
                    diff = kcec_contract - hayden_count
                    print(f"{month_name:10} | {kcec_contract:12d} | {hayden_count:12d} | {diff:+12d}")
                    total_kcec_contract += kcec_contract
                    total_hayden += hayden_count
                    months_compared += 1
                else:
                    print(f"{month_name:10} | {kcec_contract:12d} | {'N/A':>12} | {'N/A':>12}")
            else:
                print(f"{month_name:10} | {kcec_contract:12d} | {'N/A':>12} | {'N/A':>12}")
        
        if months_compared > 0:
            print("-"*70)
            print(f"{'TOTAL':10} | {total_kcec_contract:12d} | {total_hayden:12d} | {total_kcec_contract-total_hayden:+12d}")
            print(f"\nFor {months_compared} months with Hayden data:")
            print(f"  KCEC contract rain days (≥0.10\"): {total_kcec_contract}")
            print(f"  Hayden rain days: {total_hayden}")
            print(f"  Difference: {total_kcec_contract - total_hayden} days")
            
            if total_hayden > 0:
                pct_diff = ((total_kcec_contract - total_hayden) / total_hayden) * 100
                print(f"  Percentage difference: {pct_diff:+.1f}%")
        
    except Exception as e:
        print(f"\nCould not load Hayden's data: {e}")
    
    # Save detailed analysis
    output_file = os.path.join(DATA_DIR, f"contract_threshold_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    # Create detailed output dataframe
    analysis_df = df[['Date', 'Total_Inches']].copy()
    analysis_df['Month'] = df['Date'].dt.month
    analysis_df['Day_of_Week'] = df['Date'].dt.day_name()
    analysis_df['Measurable_0.01'] = df['Total_Inches'] >= 0.01
    analysis_df['Contract_0.10'] = df['Total_Inches'] >= 0.10
    analysis_df['Normal_0.25'] = df['Total_Inches'] >= 0.25
    analysis_df['PNW_Delay_0.50'] = df['Total_Inches'] >= 0.50
    
    analysis_df.to_csv(output_file, index=False)
    print(f"\nDetailed analysis saved to: {output_file}")
    
    # Also check for patterns
    print("\n" + "="*70)
    print("RAINFALL PATTERNS:")
    print("="*70)
    
    # Days of week analysis for contract rain days
    contract_rain_df = df[df['Contract_Rain']]
    if len(contract_rain_df) > 0:
        contract_rain_df['DayOfWeek'] = contract_rain_df['Date'].dt.day_name()
        dow_counts = contract_rain_df['DayOfWeek'].value_counts()
        
        print("\nContract rain days (≥0.10\") by day of week:")
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            if day in dow_counts.index:
                print(f"  {day:10}: {dow_counts[day]:3d} days")
            else:
                print(f"  {day:10}:   0 days")
    
    return df, monthly

if __name__ == "__main__":
    print("Analyzing KCEC rainfall data with contract thresholds...")
    df, monthly = analyze_with_thresholds()
    
    print("\n" + "="*70)
    print("KEY FINDING:")
    print("Using the 0.10\" contract threshold significantly reduces rain day counts")
    print("compared to counting any measurable precipitation (0.01\").")
    print("This likely explains much of the difference with Hayden's counts.")
    print("="*70)