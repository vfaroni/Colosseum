#!/usr/bin/env python3
"""
Compare KCEC and Hayden's detailed daily rainfall data
Read Hayden's first tab with daily data (B2:B367 dates, E2:E367 rainfall)
"""

import os
import pandas as pd
from datetime import datetime
import numpy as np

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "weather_data")

def read_hayden_daily_data():
    """Read Hayden's detailed daily data from first tab"""
    excel_file = os.path.join(DATA_DIR, "ACG_Weather_Data", "Hayden_Rain_Info_2024.xlsx")
    
    print(f"Reading Hayden's daily data from first sheet...")
    
    # Read the first sheet (index 0)
    df = pd.read_excel(excel_file, sheet_name=0)
    
    print(f"Columns: {list(df.columns)}")
    print(f"Shape: {df.shape}")
    
    # The data appears to be in columns B (Day/Date) and E (Precip)
    # Column indices: A=0, B=1, C=2, D=3, E=4
    hayden_data = pd.DataFrame()
    
    # Get date column (B = index 1)
    hayden_data['Date'] = df.iloc[:, 1]  # Column B
    hayden_data['High_Temp'] = df.iloc[:, 2]  # Column C
    hayden_data['Low_Temp'] = df.iloc[:, 3]  # Column D
    hayden_data['Precip_Inches'] = df.iloc[:, 4]  # Column E
    
    # Convert date to datetime
    hayden_data['Date'] = pd.to_datetime(hayden_data['Date'])
    
    # Filter to 2024 data only
    hayden_2024 = hayden_data[hayden_data['Date'].dt.year == 2024].copy()
    
    print(f"\nHayden's 2024 data:")
    print(f"  Days: {len(hayden_2024)}")
    print(f"  Date range: {hayden_2024['Date'].min()} to {hayden_2024['Date'].max()}")
    print(f"  Total rainfall: {hayden_2024['Precip_Inches'].sum():.2f} inches")
    
    return hayden_2024

def compare_daily_data():
    """Compare KCEC and Hayden data day by day"""
    
    # Read Hayden's daily data
    hayden_df = read_hayden_daily_data()
    
    # Read KCEC data
    import glob
    pattern = os.path.join(DATA_DIR, "kcec_full_2024_*.csv")
    files = glob.glob(pattern)
    
    if not files:
        print("ERROR: No full 2024 KCEC data found")
        return
    
    latest_file = max(files, key=os.path.getctime)
    kcec_df = pd.read_csv(latest_file)
    kcec_df['Date'] = pd.to_datetime(kcec_df['Date'])
    
    print(f"\nKCEC 2024 data:")
    print(f"  Days: {len(kcec_df)}")
    print(f"  Total rainfall: {kcec_df['Total_Inches'].sum():.2f} inches")
    
    # Merge the datasets on date
    merged = pd.merge(
        kcec_df[['Date', 'Total_Inches']],
        hayden_df[['Date', 'Precip_Inches', 'High_Temp', 'Low_Temp']],
        on='Date',
        how='outer',
        suffixes=('_KCEC', '_Hayden')
    )
    
    merged = merged.sort_values('Date')
    
    # Calculate differences
    merged['Diff_Inches'] = merged['Total_Inches'] - merged['Precip_Inches']
    merged['Both_Rain'] = (merged['Total_Inches'] >= 0.10) & (merged['Precip_Inches'] >= 0.10)
    merged['KCEC_Only'] = (merged['Total_Inches'] >= 0.10) & (merged['Precip_Inches'] < 0.10)
    merged['Hayden_Only'] = (merged['Total_Inches'] < 0.10) & (merged['Precip_Inches'] >= 0.10)
    
    print("\n" + "="*70)
    print("DAILY COMPARISON SUMMARY")
    print("="*70)
    
    # Days with significant differences (>0.05 inches)
    sig_diff = merged[abs(merged['Diff_Inches']) > 0.05].copy()
    print(f"\nDays with significant differences (>0.05\"):")
    print(f"Total: {len(sig_diff)} days")
    
    if len(sig_diff) > 0:
        print("\nLargest differences:")
        sig_diff['Abs_Diff'] = abs(sig_diff['Diff_Inches'])
        top_diffs = sig_diff.nlargest(10, 'Abs_Diff')
        
        print(f"\n{'Date':12} | {'KCEC':>8} | {'Hayden':>8} | {'Diff':>8} | {'Notes':>20}")
        print("-"*60)
        
        for idx, row in top_diffs.iterrows():
            date_str = row['Date'].strftime('%Y-%m-%d')
            kcec_val = f"{row['Total_Inches']:.2f}" if pd.notna(row['Total_Inches']) else "N/A"
            hayden_val = f"{row['Precip_Inches']:.2f}" if pd.notna(row['Precip_Inches']) else "N/A"
            diff_val = f"{row['Diff_Inches']:+.2f}" if pd.notna(row['Diff_Inches']) else "N/A"
            
            # Add notes about rain threshold
            notes = ""
            if pd.notna(row['Total_Inches']) and pd.notna(row['Precip_Inches']):
                if row['KCEC_Only']:
                    notes = "KCEC rain day only"
                elif row['Hayden_Only']:
                    notes = "Hayden rain day only"
                elif row['Both_Rain']:
                    notes = "Both rain days"
            
            print(f"{date_str:12} | {kcec_val:>8} | {hayden_val:>8} | {diff_val:>8} | {notes:>20}")
    
    # Contract rain day comparison (≥0.10")
    print("\n" + "="*70)
    print("CONTRACT RAIN DAY ANALYSIS (≥0.10\")")
    print("="*70)
    
    kcec_contract_days = (merged['Total_Inches'] >= 0.10).sum()
    hayden_contract_days = (merged['Precip_Inches'] >= 0.10).sum()
    both_contract_days = merged['Both_Rain'].sum()
    kcec_only_days = merged['KCEC_Only'].sum()
    hayden_only_days = merged['Hayden_Only'].sum()
    
    print(f"\nContract rain days (≥0.10\"):")
    print(f"  KCEC total: {kcec_contract_days} days")
    print(f"  Hayden total: {hayden_contract_days} days")
    print(f"  Both sources agree: {both_contract_days} days")
    print(f"  KCEC only: {kcec_only_days} days")
    print(f"  Hayden only: {hayden_only_days} days")
    
    # Show days where they disagree on contract rain
    disagree_days = merged[merged['KCEC_Only'] | merged['Hayden_Only']].copy()
    
    if len(disagree_days) > 0:
        print(f"\nDays with disagreement on contract rain (≥0.10\"):")
        print(f"\n{'Date':12} | {'KCEC':>8} | {'Hayden':>8} | {'Status':>20}")
        print("-"*50)
        
        for idx, row in disagree_days.iterrows():
            date_str = row['Date'].strftime('%Y-%m-%d')
            kcec_val = f"{row['Total_Inches']:.2f}" if pd.notna(row['Total_Inches']) else "N/A"
            hayden_val = f"{row['Precip_Inches']:.2f}" if pd.notna(row['Precip_Inches']) else "N/A"
            status = "KCEC only" if row['KCEC_Only'] else "Hayden only"
            
            print(f"{date_str:12} | {kcec_val:>8} | {hayden_val:>8} | {status:>20}")
    
    # Monthly comparison
    merged['Month'] = merged['Date'].dt.month
    monthly_comp = merged.groupby('Month').agg({
        'Total_Inches': 'sum',
        'Precip_Inches': 'sum',
        'Both_Rain': 'sum',
        'KCEC_Only': 'sum',
        'Hayden_Only': 'sum'
    })
    
    print("\n" + "="*70)
    print("MONTHLY COMPARISON")
    print("="*70)
    print(f"\n{'Month':10} | {'KCEC':>8} | {'Hayden':>8} | {'Diff':>8} | {'Contract Days':>20}")
    print(f"{'':10} | {'Total\"':>8} | {'Total\"':>8} | {'Inches':>8} | {'KCEC/Hayden/Both':>20}")
    print("-"*70)
    
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    for month_num in range(1, 13):
        if month_num in monthly_comp.index:
            month_name = month_names[month_num-1]
            kcec_total = monthly_comp.loc[month_num, 'Total_Inches']
            hayden_total = monthly_comp.loc[month_num, 'Precip_Inches']
            diff = kcec_total - hayden_total
            
            # Count contract rain days for the month
            month_data = merged[merged['Month'] == month_num]
            kcec_days = (month_data['Total_Inches'] >= 0.10).sum()
            hayden_days = (month_data['Precip_Inches'] >= 0.10).sum()
            both_days = monthly_comp.loc[month_num, 'Both_Rain']
            
            contract_str = f"{kcec_days}/{hayden_days}/{int(both_days)}"
            
            print(f"{month_name:10} | {kcec_total:8.2f} | {hayden_total:8.2f} | {diff:+8.2f} | {contract_str:>20}")
    
    # Save detailed comparison
    output_file = os.path.join(DATA_DIR, f"daily_comparison_detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    merged.to_csv(output_file, index=False)
    print(f"\nDetailed daily comparison saved to: {output_file}")
    
    return merged

if __name__ == "__main__":
    print("Comparing KCEC and Hayden's detailed daily rainfall data...")
    comparison = compare_daily_data()