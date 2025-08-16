#!/usr/bin/env python3
"""
Final comparison of KCEC 2024 data vs Hayden's rain day counts
"""

import os
import pandas as pd
from datetime import datetime
import numpy as np

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "weather_data")

def get_kcec_2024_summary():
    """Get KCEC 2024 summary by month"""
    # Find the most recent full 2024 file
    import glob
    pattern = os.path.join(DATA_DIR, "kcec_full_2024_*.csv")
    files = glob.glob(pattern)
    
    if not files:
        print("ERROR: No full 2024 KCEC data found")
        return None
    
    latest_file = max(files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.month
    
    # Monthly summary
    monthly = df.groupby('Month').agg({
        'Total_Inches': ['sum', lambda x: (x > 0).sum(), lambda x: (x >= 0.01).sum()]
    })
    monthly.columns = ['Total_Inches', 'Any_Rain_Days', 'Measurable_Days']
    
    return monthly, df

def get_hayden_counts():
    """Get Hayden's rain day counts from the second sheet"""
    excel_file = os.path.join(DATA_DIR, "ACG_Weather_Data", "Hayden_Rain_Info_2024.xlsx")
    
    # Read the "Rain Days Per Hayden Schedule" sheet
    df = pd.read_excel(excel_file, sheet_name='Rain Days Per Hayden Schedule')
    
    # Print columns to debug
    print(f"Hayden sheet columns: {list(df.columns)}")
    
    # Create a dictionary of month to rain days
    hayden_counts = {}
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    # The first column seems to contain month names
    first_col = df.columns[0]
    second_col = df.columns[1] if len(df.columns) > 1 else None
    
    for i, month in enumerate(month_names):
        # Find the row for this month
        month_row = df[df[first_col] == month]
        if not month_row.empty and second_col:
            count = month_row[second_col].iloc[0]
            # Handle NaN values
            hayden_counts[i+1] = int(count) if pd.notna(count) else None
    
    return hayden_counts

def create_comparison_report():
    """Create detailed comparison report"""
    
    print("Creating KCEC vs Hayden Rain Day Comparison for 2024")
    print("="*60)
    
    # Get KCEC data
    kcec_monthly, kcec_daily = get_kcec_2024_summary()
    
    # Get Hayden's counts
    hayden_counts = get_hayden_counts()
    
    # Create comparison table
    comparison_data = []
    
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    print("\nMonthly Rain Day Comparison:")
    print("-"*70)
    print(f"{'Month':10} | {'KCEC Days':>10} | {'Hayden Days':>12} | {'Difference':>10} | {'KCEC Total':>10}")
    print("-"*70)
    
    total_kcec = 0
    total_hayden = 0
    months_with_data = 0
    
    for month_num in range(1, 13):
        month_name = month_names[month_num-1]
        
        # Get KCEC count
        if month_num in kcec_monthly.index:
            kcec_count = int(kcec_monthly.loc[month_num, 'Any_Rain_Days'])
            kcec_total = kcec_monthly.loc[month_num, 'Total_Inches']
        else:
            kcec_count = 0
            kcec_total = 0.0
        
        # Get Hayden count
        hayden_count = hayden_counts.get(month_num, None)
        
        # Calculate difference
        if hayden_count is not None:
            diff = kcec_count - hayden_count
            diff_str = f"{diff:+d}"
            total_kcec += kcec_count
            total_hayden += hayden_count
            months_with_data += 1
            hayden_str = str(hayden_count)
        else:
            diff_str = "N/A"
            hayden_str = "N/A"
        
        print(f"{month_name:10} | {kcec_count:10d} | {hayden_str:>12} | {diff_str:>10} | {kcec_total:9.2f}\"")
        
        comparison_data.append({
            'Month': month_name,
            'KCEC_Rain_Days': kcec_count,
            'Hayden_Rain_Days': hayden_count,
            'Difference': diff if hayden_count is not None else None,
            'KCEC_Total_Inches': kcec_total
        })
    
    print("-"*70)
    
    # Calculate totals for months with Hayden data
    if months_with_data > 0:
        print(f"{'TOTAL':10} | {total_kcec:10d} | {total_hayden:12d} | {total_kcec-total_hayden:+10d} |")
        print(f"\nNote: Totals only include months where Hayden provided data ({months_with_data} months)")
    
    # Additional analysis
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY:")
    print("="*60)
    
    # Full year KCEC stats
    total_kcec_days = int(kcec_monthly['Any_Rain_Days'].sum())
    total_kcec_rain = kcec_monthly['Total_Inches'].sum()
    
    print(f"\nKCEC Full Year 2024 Statistics:")
    print(f"  Total rain days: {total_kcec_days}")
    print(f"  Total rainfall: {total_kcec_rain:.2f} inches")
    print(f"  Average rainfall per rainy day: {total_kcec_rain/total_kcec_days:.2f} inches")
    
    # Hayden comparison for available months
    if months_with_data > 0:
        print(f"\nFor months with Hayden data ({months_with_data} months):")
        print(f"  KCEC rain days: {total_kcec}")
        print(f"  Hayden rain days: {total_hayden}")
        print(f"  Difference: {total_kcec - total_hayden} days ({((total_kcec-total_hayden)/total_hayden*100):.1f}% more in KCEC)")
    
    # Save to file
    output_file = os.path.join(DATA_DIR, f"final_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    with open(output_file, 'w') as f:
        f.write("KCEC vs Hayden Rain Day Comparison for 2024\n")
        f.write("="*60 + "\n\n")
        
        f.write("Monthly Rain Day Comparison:\n")
        f.write("-"*70 + "\n")
        f.write(f"{'Month':10} | {'KCEC Days':>10} | {'Hayden Days':>12} | {'Difference':>10} | {'KCEC Total':>10}\n")
        f.write("-"*70 + "\n")
        
        for row in comparison_data:
            hayden_str = str(row['Hayden_Rain_Days']) if row['Hayden_Rain_Days'] is not None else "N/A"
            diff_str = f"{row['Difference']:+d}" if row['Difference'] is not None else "N/A"
            f.write(f"{row['Month']:10} | {row['KCEC_Rain_Days']:10d} | {hayden_str:>12} | {diff_str:>10} | {row['KCEC_Total_Inches']:9.2f}\"\n")
        
        f.write("-"*70 + "\n")
        f.write(f"{'TOTAL':10} | {total_kcec:10d} | {total_hayden:12d} | {total_kcec-total_hayden:+10d} |\n")
        
        f.write(f"\n\nFull Year KCEC Statistics:\n")
        f.write(f"  Total rain days: {total_kcec_days}\n")
        f.write(f"  Total rainfall: {total_kcec_rain:.2f} inches\n")
        f.write(f"  Average rainfall per rainy day: {total_kcec_rain/total_kcec_days:.2f} inches\n")
    
    # Save comparison CSV
    comparison_df = pd.DataFrame(comparison_data)
    csv_file = os.path.join(DATA_DIR, f"comparison_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    comparison_df.to_csv(csv_file, index=False)
    
    print(f"\nFiles saved:")
    print(f"  Report: {output_file}")
    print(f"  CSV: {csv_file}")
    
    return comparison_df

if __name__ == "__main__":
    create_comparison_report()
    
    print("\n" + "="*60)
    print("NOTES:")
    print("- KCEC data is from the official NOAA weather station")
    print("- Some months show N/A for Hayden's data (not provided)")
    print("- Differences may be due to different rain thresholds or observation methods")
    print("- Your Google Sheets link: https://docs.google.com/spreadsheets/d/1sVo6MOtIwqX2_0nxANHnkOODQnUvzlCSynr91ORI1Ms/")