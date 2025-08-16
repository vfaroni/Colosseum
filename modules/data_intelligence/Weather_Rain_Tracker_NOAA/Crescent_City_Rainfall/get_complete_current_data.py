#!/usr/bin/env python3
"""
Get complete current KCEC rainfall data through most recent available date
Combine with our fixed Jan-Apr data and create comprehensive analysis
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "weather_data")

def get_rain_category(inches):
    """Categorize rainfall amount"""
    if inches == 0:
        return "None"
    elif inches < 0.25:
        return "Light"
    elif inches < 0.5:
        return "Moderate"
    elif inches < 1.0:
        return "Heavy"
    else:
        return "Very Heavy"

def download_current_kcec_data():
    """Download KCEC data from May 2024 through most recent available"""
    
    # Load config
    config_path = os.path.join(BASE_DIR, "config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    noaa_token = config.get("noaa_token")
    if not noaa_token:
        print("ERROR: No NOAA token in config")
        return None
    
    # KCEC station with correct units
    correct_station = "GHCND:USW00024286"  # CRESCENT CITY MCNAMARA AIRPORT
    
    # Get data from May 1, 2024 to end of 2024 (don't go into 2025 yet)
    start_date = "2024-05-01"
    end_date = "2024-12-31"  # Just get through end of 2024 for now
    
    print(f"Downloading current KCEC data: {correct_station}")
    print(f"Date range: {start_date} to {end_date}")
    print("Using correct units (standard = inches, no conversion)")
    
    # Split into smaller chunks (3 months each) to avoid API limits
    all_data = {}
    
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    headers = {"token": noaa_token}
    
    # Define date chunks
    date_chunks = [
        ("2024-05-01", "2024-07-31"),  # May-July
        ("2024-08-01", "2024-10-31"),  # Aug-Oct  
        ("2024-11-01", "2024-12-31"),  # Nov-Dec
    ]
    
    for chunk_start, chunk_end in date_chunks:
        print(f"  Downloading {chunk_start} to {chunk_end}...")
        
        params = {
            "datasetid": "GHCND",
            "stationid": correct_station,
            "datatypeid": "PRCP",
            "startdate": chunk_start,
            "enddate": chunk_end,
            "units": "standard",
            "limit": 500
        }
        
        try:
            time.sleep(1)  # Rate limiting
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data:
                print(f"    Got {len(data['results'])} records")
                
                # Process the data (no conversion needed)
                for item in data["results"]:
                    date = item["date"][:10]
                    inches = item["value"] if item["value"] else 0.0
                    all_data[date] = round(inches, 2)
            else:
                print(f"    No data for {chunk_start} to {chunk_end}")
                
        except Exception as e:
            print(f"    Error downloading {chunk_start} to {chunk_end}: {e}")
    
    if not all_data:
        print("No data downloaded")
        return None
        
    print(f"Total records downloaded: {len(all_data)}")
    
    # Create complete dataset
    results = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    
    while current_date <= end_date_obj:
        date_str = current_date.strftime('%Y-%m-%d')
        inches = all_data.get(date_str, 0.0)
        
        results.append({
            "Date": date_str + "T00:00:00",
            "Total_Inches": inches,
            "Category": get_rain_category(inches),
            "Measurable_0.01": "Yes" if inches >= 0.01 else "No",
            "Light_0.01": "Yes" if 0.01 <= inches < 0.25 else "No",
            "Moderate_0.25": "Yes" if 0.25 <= inches < 0.5 else "No",
            "Heavy_0.5": "Yes" if 0.5 <= inches < 1.0 else "No",
            "Very_Heavy_1.0": "Yes" if inches >= 1.0 else "No",
            "Work_Suitable": "No" if inches >= 0.5 else "Yes",
            "Timestamp": datetime.now().isoformat()
        })
        
        current_date += timedelta(days=1)
    
    # Save current data
    output_file = os.path.join(DATA_DIR, f"kcec_current_may_to_dec2024_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    
    print(f"Current data saved to: {output_file}")
    print(f"Records: {len(results)} days")
    
    return output_file

def combine_all_data():
    """Combine fixed Jan-Apr data with current May-present data"""
    
    print("\nCombining all KCEC data...")
    
    # Find the fixed Jan-Apr file
    import glob
    jan_apr_pattern = os.path.join(DATA_DIR, "kcec_FIXED_jan_apr_2024_*.csv")
    jan_apr_files = glob.glob(jan_apr_pattern)
    
    if not jan_apr_files:
        print("ERROR: Fixed Jan-Apr data not found")
        return None
    
    jan_apr_file = max(jan_apr_files, key=os.path.getctime)
    print(f"Reading fixed Jan-Apr data: {jan_apr_file}")
    
    # Find the current May-Dec file
    current_pattern = os.path.join(DATA_DIR, "kcec_current_may_to_dec2024_*.csv")
    current_files = glob.glob(current_pattern)
    
    if not current_files:
        print("ERROR: Current data not found")
        return None
    
    current_file = max(current_files, key=os.path.getctime)
    print(f"Reading current data: {current_file}")
    
    # Read both datasets
    jan_apr_df = pd.read_csv(jan_apr_file)
    current_df = pd.read_csv(current_file)
    
    print(f"Jan-Apr records: {len(jan_apr_df)}")
    print(f"May-present records: {len(current_df)}")
    
    # Combine
    combined_df = pd.concat([jan_apr_df, current_df], ignore_index=True)
    combined_df['Date'] = pd.to_datetime(combined_df['Date'])
    combined_df = combined_df.sort_values('Date')
    
    # Save combined dataset
    output_file = os.path.join(DATA_DIR, f"kcec_complete_2024_to_present_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    combined_df.to_csv(output_file, index=False)
    
    print(f"\nCombined dataset saved: {output_file}")
    print(f"Total records: {len(combined_df)}")
    print(f"Date range: {combined_df['Date'].min().strftime('%Y-%m-%d')} to {combined_df['Date'].max().strftime('%Y-%m-%d')}")
    
    return output_file, combined_df

def comprehensive_rainfall_analysis(df):
    """Create comprehensive rainfall analysis by thresholds"""
    
    print("\n" + "="*80)
    print("COMPREHENSIVE KCEC RAINFALL ANALYSIS")
    print("="*80)
    
    # Add threshold columns
    df['Rain_0.10'] = df['Total_Inches'] >= 0.10  # Contract threshold
    df['Rain_0.25'] = df['Total_Inches'] >= 0.25  # Normal threshold  
    df['Rain_0.50'] = df['Total_Inches'] >= 0.50  # Heavy threshold
    df['Rain_1.00'] = df['Total_Inches'] >= 1.00  # Very heavy threshold
    
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    df['Month_Name'] = df['Date'].dt.strftime('%B')
    df['Year_Month'] = df['Date'].dt.strftime('%Y-%m')
    
    # Overall statistics
    total_days = len(df)
    total_rainfall = df['Total_Inches'].sum()
    
    print(f"\nOVERALL STATISTICS:")
    print(f"Period: {df['Date'].min().strftime('%B %d, %Y')} to {df['Date'].max().strftime('%B %d, %Y')}")
    print(f"Total days: {total_days}")
    print(f"Total rainfall: {total_rainfall:.2f} inches")
    print(f"Average daily rainfall: {total_rainfall/total_days:.3f} inches")
    
    # Days by threshold
    print(f"\nRAIN DAYS BY THRESHOLD:")
    rain_010 = df['Rain_0.10'].sum()
    rain_025 = df['Rain_0.25'].sum() 
    rain_050 = df['Rain_0.50'].sum()
    rain_100 = df['Rain_1.00'].sum()
    
    print(f"  ≥0.10\" (Contract):     {rain_010:3d} days ({rain_010/total_days*100:.1f}%)")
    print(f"  ≥0.25\" (Normal):       {rain_025:3d} days ({rain_025/total_days*100:.1f}%)")
    print(f"  ≥0.50\" (Heavy):        {rain_050:3d} days ({rain_050/total_days*100:.1f}%)")
    print(f"  ≥1.00\" (Very Heavy):   {rain_100:3d} days ({rain_100/total_days*100:.1f}%)")
    
    # Monthly analysis
    monthly = df.groupby(['Year', 'Month', 'Month_Name']).agg({
        'Total_Inches': 'sum',
        'Rain_0.10': 'sum',
        'Rain_0.25': 'sum', 
        'Rain_0.50': 'sum',
        'Rain_1.00': 'sum'
    }).reset_index()
    
    print(f"\n" + "="*90)
    print("MONTHLY BREAKDOWN:")
    print("="*90)
    print(f"{'Month':12} | {'Total':>8} | {'≥0.10\"':>7} | {'≥0.25\"':>7} | {'≥0.50\"':>7} | {'≥1.00\"':>7}")
    print(f"{'':12} | {'Inches':>8} | {'Days':>7} | {'Days':>7} | {'Days':>7} | {'Days':>7}")
    print("-"*90)
    
    total_monthly_rain = 0
    total_010_days = 0
    total_025_days = 0
    total_050_days = 0
    total_100_days = 0
    
    for _, row in monthly.iterrows():
        month_year = f"{row['Month_Name']} {row['Year']}"
        total_rain = row['Total_Inches']
        days_010 = int(row['Rain_0.10'])
        days_025 = int(row['Rain_0.25'])
        days_050 = int(row['Rain_0.50'])
        days_100 = int(row['Rain_1.00'])
        
        total_monthly_rain += total_rain
        total_010_days += days_010
        total_025_days += days_025
        total_050_days += days_050
        total_100_days += days_100
        
        print(f"{month_year:12} | {total_rain:8.2f} | {days_010:7d} | {days_025:7d} | {days_050:7d} | {days_100:7d}")
    
    print("-"*90)
    print(f"{'TOTAL':12} | {total_monthly_rain:8.2f} | {total_010_days:7d} | {total_025_days:7d} | {total_050_days:7d} | {total_100_days:7d}")
    
    # Wettest and driest months
    print(f"\n" + "="*60)
    print("RECORDS:")
    print("="*60)
    
    wettest_month = monthly.loc[monthly['Total_Inches'].idxmax()]
    driest_month = monthly.loc[monthly['Total_Inches'].idxmin()]
    most_rain_days = monthly.loc[monthly['Rain_0.10'].idxmax()]
    
    print(f"Wettest month: {wettest_month['Month_Name']} {wettest_month['Year']} ({wettest_month['Total_Inches']:.2f}\")")
    print(f"Driest month: {driest_month['Month_Name']} {driest_month['Year']} ({driest_month['Total_Inches']:.2f}\")")
    print(f"Most contract rain days: {most_rain_days['Month_Name']} {most_rain_days['Year']} ({int(most_rain_days['Rain_0.10'])} days)")
    
    # Single wettest days
    wettest_days = df.nlargest(10, 'Total_Inches')
    print(f"\nTOP 10 WETTEST DAYS:")
    print(f"{'Date':12} | {'Rainfall':>8} | {'Category':>12}")
    print("-"*35)
    
    for _, row in wettest_days.iterrows():
        date_str = row['Date'].strftime('%Y-%m-%d')
        rainfall = row['Total_Inches']
        category = row['Category']
        print(f"{date_str:12} | {rainfall:8.2f} | {category:>12}")
    
    # Save detailed analysis
    analysis_file = os.path.join(DATA_DIR, f"rainfall_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    # Create analysis summary dataframe
    analysis_summary = monthly.copy()
    analysis_summary.to_csv(analysis_file, index=False)
    
    print(f"\nDetailed analysis saved to: {analysis_file}")
    
    return monthly

def main():
    """Main function to get current data and perform analysis"""
    
    print("KCEC Complete Rainfall Analysis")
    print("Getting current data through most recent available date")
    print("="*60)
    
    # Download current data
    current_file = download_current_kcec_data()
    if not current_file:
        print("Failed to download current data")
        return
    
    # Combine all data
    combined_file, combined_df = combine_all_data()
    if combined_file is None:
        print("Failed to combine data")
        return
    
    # Perform comprehensive analysis
    monthly_analysis = comprehensive_rainfall_analysis(combined_df)
    
    print(f"\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print(f"Complete dataset: {combined_file}")
    print("All rainfall thresholds calculated: 0.10\", 0.25\", 0.50\", 1.00\"")
    print("Monthly and daily statistics generated")
    print("="*60)

if __name__ == "__main__":
    main()