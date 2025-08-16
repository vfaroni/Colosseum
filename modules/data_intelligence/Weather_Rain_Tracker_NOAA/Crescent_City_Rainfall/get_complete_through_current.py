#!/usr/bin/env python3
"""
Get complete KCEC data from 2024 through most recent available date in 2025
Combine with existing 2024 data and format properly
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import glob

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

def download_2025_data():
    """Download 2025 data through most recent available"""
    
    # Load config
    config_path = os.path.join(BASE_DIR, "config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    noaa_token = config.get("noaa_token")
    if not noaa_token:
        print("ERROR: No NOAA token in config")
        return None
    
    # KCEC station
    correct_station = "GHCND:USW00024286"  # CRESCENT CITY MCNAMARA AIRPORT
    
    # Get 2025 data from Jan 1 to current date
    start_date = "2025-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Downloading 2025 KCEC data: {correct_station}")
    print(f"Date range: {start_date} to {end_date}")
    print("Using correct units (standard = inches, no conversion)")
    
    # Split into smaller chunks for 2025 (month by month to avoid API limits)
    all_data = {}
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    headers = {"token": noaa_token}
    
    # Generate monthly chunks for 2025
    current_month = datetime(2025, 1, 1)
    today = datetime.now()
    date_chunks = []
    
    while current_month < today:
        # Get last day of current month
        if current_month.month == 12:
            next_month = current_month.replace(year=current_month.year + 1, month=1)
        else:
            next_month = current_month.replace(month=current_month.month + 1)
        
        last_day = next_month - timedelta(days=1)
        
        # Don't go beyond today
        if last_day > today:
            last_day = today
        
        chunk_start = current_month.strftime("%Y-%m-%d")
        chunk_end = last_day.strftime("%Y-%m-%d")
        date_chunks.append((chunk_start, chunk_end))
        
        current_month = next_month
    
    print(f"Will download {len(date_chunks)} monthly chunks for 2025...")
    
    for chunk_start, chunk_end in date_chunks:
        print(f"  Downloading {chunk_start} to {chunk_end}...")
        
        params = {
            "datasetid": "GHCND",
            "stationid": correct_station,
            "datatypeid": "PRCP",
            "startdate": chunk_start,
            "enddate": chunk_end,
            "units": "standard",
            "limit": 100
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
        print("No 2025 data downloaded")
        return None
        
    print(f"Total 2025 records downloaded: {len(all_data)}")
    
    # Find the actual last date with data
    last_data_date = max(all_data.keys()) if all_data else start_date
    print(f"Most recent data available: {last_data_date}")
    
    # Create complete dataset for 2025
    results = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    last_date = datetime.strptime(last_data_date, "%Y-%m-%d")
    
    while current_date <= last_date:
        date_str = current_date.strftime('%Y-%m-%d')
        inches = all_data.get(date_str, 0.0)
        
        results.append({
            "Date": date_str + "T00:00:00",
            "Year": current_date.year,
            "Month": current_date.month,
            "Day": current_date.day,
            "Month_Name": current_date.strftime('%B'),
            "Day_of_Week": current_date.strftime('%A'),
            "Total_Inches": inches,
            "Category": get_rain_category(inches),
            "Measurable_0.01": 1 if inches >= 0.01 else 0,
            "Contract_0.10": 1 if inches >= 0.10 else 0,
            "Normal_0.25": 1 if inches >= 0.25 else 0,
            "Heavy_0.50": 1 if inches >= 0.50 else 0,
            "Light_0.01": 1 if 0.01 <= inches < 0.25 else 0,
            "Moderate_0.25": 1 if 0.25 <= inches < 0.5 else 0,
            "Heavy_0.5": 1 if 0.5 <= inches < 1.0 else 0,
            "Very_Heavy_1.0": 1 if inches >= 1.0 else 0,
            "Work_Suitable": 1 if inches < 0.5 else 0,
            "Timestamp": datetime.now().isoformat()
        })
        
        current_date += timedelta(days=1)
    
    # Save 2025 data
    output_file = os.path.join(DATA_DIR, f"kcec_2025_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    
    print(f"2025 data saved to: {output_file}")
    print(f"Records: {len(results)} days")
    
    return output_file, last_data_date

def combine_all_data_complete():
    """Combine 2024 and 2025 data into complete dataset"""
    
    print("\nCombining 2024 and 2025 data...")
    
    # Find the fixed 2024 file
    pattern_2024 = os.path.join(DATA_DIR, "kcec_complete_2024_FIXED_*.csv")
    files_2024 = glob.glob(pattern_2024)
    
    if not files_2024:
        print("ERROR: Fixed 2024 data not found")
        return None
    
    file_2024 = max(files_2024, key=os.path.getctime)
    print(f"Reading 2024 data: {file_2024}")
    
    # Find the 2025 file
    pattern_2025 = os.path.join(DATA_DIR, "kcec_2025_data_*.csv")
    files_2025 = glob.glob(pattern_2025)
    
    if not files_2025:
        print("ERROR: 2025 data not found")
        return None
    
    file_2025 = max(files_2025, key=os.path.getctime)
    print(f"Reading 2025 data: {file_2025}")
    
    # Read both datasets
    df_2024 = pd.read_csv(file_2024)
    df_2025 = pd.read_csv(file_2025)
    
    print(f"2024 records: {len(df_2024)}")
    print(f"2025 records: {len(df_2025)}")
    
    # Combine
    combined_df = pd.concat([df_2024, df_2025], ignore_index=True)
    combined_df['Date'] = pd.to_datetime(combined_df['Date'], format='mixed')
    combined_df = combined_df.sort_values('Date')
    
    # Get actual date range
    start_date = combined_df['Date'].min().strftime('%Y-%m-%d')
    end_date = combined_df['Date'].max().strftime('%Y-%m-%d')
    
    # Save combined dataset with accurate filename
    output_file = os.path.join(DATA_DIR, f"kcec_complete_{start_date}_to_{end_date}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    combined_df.to_csv(output_file, index=False)
    
    print(f"\nComplete dataset saved: {output_file}")
    print(f"Total records: {len(combined_df)}")
    print(f"Date range: {start_date} to {end_date}")
    
    # Summary statistics
    total_rain = combined_df['Total_Inches'].sum()
    contract_days = combined_df['Contract_0.10'].sum()
    normal_days = combined_df['Normal_0.25'].sum()
    heavy_days = combined_df['Heavy_0.50'].sum()
    
    print(f"\nOVERALL STATISTICS:")
    print(f"Total rainfall: {total_rain:.2f} inches")
    print(f"Contract days (≥0.10\"): {contract_days}")
    print(f"Normal days (≥0.25\"): {normal_days}")
    print(f"Heavy days (≥0.50\"): {heavy_days}")
    
    return output_file

def main():
    """Main function to get complete data through current date"""
    
    print("KCEC Complete Rainfall Data - 2024 through Current Date")
    print("="*60)
    
    # Download 2025 data
    result = download_2025_data()
    if not result:
        print("Failed to download 2025 data")
        return
    
    file_2025, last_date = result
    
    # Combine all data
    complete_file = combine_all_data_complete()
    if complete_file is None:
        print("Failed to combine data")
        return
    
    print(f"\n" + "="*60)
    print("COMPLETE DATA READY!")
    print(f"Dataset: {complete_file}")
    print(f"Coverage: 2024-01-01 through {last_date}")
    print("All threshold columns included (Contract_0.10, Normal_0.25, Heavy_0.50)")
    print("Format: 1/0 for easy Excel calculations")
    print("="*60)

if __name__ == "__main__":
    main()