#!/usr/bin/env python3
"""
Get missing temperature and wind data for April-June 2025
Break into smaller chunks to avoid server errors
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

def get_missing_temp_wind_data():
    """Get missing temperature and wind data for April-June 2025"""
    
    # Load config
    config_path = os.path.join(BASE_DIR, "config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    noaa_token = config.get("noaa_token")
    if not noaa_token:
        print("ERROR: No NOAA token in config")
        return None
    
    # KCEC station
    correct_station = "GHCND:USW00024286"
    
    print(f"Getting missing temperature/wind data for April-June 2025")
    print(f"Station: {correct_station}")
    
    # Break into monthly chunks
    all_data = {}
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    headers = {"token": noaa_token}
    
    # Monthly chunks for 2025
    date_chunks = [
        ("2025-04-01", "2025-04-30"),  # April 2025
        ("2025-05-01", "2025-05-31"),  # May 2025
        ("2025-06-01", "2025-06-21"),  # June 2025 (partial)
    ]
    
    for chunk_start, chunk_end in date_chunks:
        print(f"  Downloading {chunk_start} to {chunk_end}...")
        
        params = {
            "datasetid": "GHCND",
            "stationid": correct_station,
            "datatypeid": "TMAX,TMIN,AWND",
            "startdate": chunk_start,
            "enddate": chunk_end,
            "units": "standard",
            "limit": 300
        }
        
        try:
            time.sleep(2)  # Longer rate limiting
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data:
                print(f"    Got {len(data['results'])} records")
                
                # Process the data
                for item in data["results"]:
                    date = item["date"][:10]
                    datatype = item["datatype"]
                    value = item["value"] if item["value"] else None
                    
                    if date not in all_data:
                        all_data[date] = {}
                    
                    if datatype == "TMAX":
                        all_data[date]["High_Temp_F"] = round(value, 1) if value else None
                    elif datatype == "TMIN":
                        all_data[date]["Low_Temp_F"] = round(value, 1) if value else None
                    elif datatype == "AWND":
                        all_data[date]["Avg_Wind_MPH"] = round(value, 1) if value else None
                        
            else:
                print(f"    No data for {chunk_start} to {chunk_end}")
                
        except Exception as e:
            print(f"    Error: {e}")
            
            # If monthly chunk fails, try weekly chunks
            print(f"    Trying weekly chunks for {chunk_start} to {chunk_end}...")
            
            start_date = datetime.strptime(chunk_start, "%Y-%m-%d")
            end_date = datetime.strptime(chunk_end, "%Y-%m-%d")
            
            current_date = start_date
            while current_date <= end_date:
                week_end = min(current_date + timedelta(days=6), end_date)
                
                week_start_str = current_date.strftime("%Y-%m-%d")
                week_end_str = week_end.strftime("%Y-%m-%d")
                
                print(f"      Weekly: {week_start_str} to {week_end_str}...")
                
                params_weekly = {
                    "datasetid": "GHCND",
                    "stationid": correct_station,
                    "datatypeid": "TMAX,TMIN,AWND",
                    "startdate": week_start_str,
                    "enddate": week_end_str,
                    "units": "standard",
                    "limit": 100
                }
                
                try:
                    time.sleep(2)
                    response = requests.get(base_url, params=params_weekly, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    if "results" in data:
                        print(f"        Got {len(data['results'])} records")
                        
                        for item in data["results"]:
                            date = item["date"][:10]
                            datatype = item["datatype"]
                            value = item["value"] if item["value"] else None
                            
                            if date not in all_data:
                                all_data[date] = {}
                            
                            if datatype == "TMAX":
                                all_data[date]["High_Temp_F"] = round(value, 1) if value else None
                            elif datatype == "TMIN":
                                all_data[date]["Low_Temp_F"] = round(value, 1) if value else None
                            elif datatype == "AWND":
                                all_data[date]["Avg_Wind_MPH"] = round(value, 1) if value else None
                                
                except Exception as week_error:
                    print(f"        Weekly error: {week_error}")
                
                current_date = week_end + timedelta(days=1)
    
    print(f"Total dates with missing data retrieved: {len(all_data)}")
    return all_data

def update_dataset_with_missing_data(missing_data):
    """Update the existing dataset with missing temperature/wind data"""
    
    print("\nUpdating dataset with missing temperature/wind data...")
    
    # Find the most recent enhanced dataset
    pattern = os.path.join(DATA_DIR, "kcec_complete_with_temp_wind_*_20250623_191730.csv")
    files = glob.glob(pattern)
    
    if not files:
        print("ERROR: Enhanced dataset not found")
        return None
    
    dataset_file = files[0]  # Should only be one from this session
    print(f"Reading: {dataset_file}")
    
    # Read the dataset
    df = pd.read_csv(dataset_file)
    print(f"Original records: {len(df)}")
    
    # Update missing data
    updates_made = 0
    for index, row in df.iterrows():
        date_str = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
        
        if date_str in missing_data:
            # Check if data is actually missing and update
            if pd.isna(row['High_Temp_F']) and missing_data[date_str].get('High_Temp_F'):
                df.at[index, 'High_Temp_F'] = missing_data[date_str]['High_Temp_F']
                updates_made += 1
            
            if pd.isna(row['Low_Temp_F']) and missing_data[date_str].get('Low_Temp_F'):
                df.at[index, 'Low_Temp_F'] = missing_data[date_str]['Low_Temp_F']
                updates_made += 1
                
            if pd.isna(row['Avg_Wind_MPH']) and missing_data[date_str].get('Avg_Wind_MPH'):
                df.at[index, 'Avg_Wind_MPH'] = missing_data[date_str]['Avg_Wind_MPH']
                updates_made += 1
    
    print(f"Updates made: {updates_made}")
    
    # Save updated dataset
    start_date = pd.to_datetime(df['Date']).min().strftime('%Y-%m-%d')
    end_date = pd.to_datetime(df['Date']).max().strftime('%Y-%m-%d')
    
    output_file = os.path.join(DATA_DIR, f"kcec_complete_FINAL_{start_date}_to_{end_date}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(output_file, index=False)
    
    print(f"Updated dataset saved: {output_file}")
    
    # Show final coverage
    temp_coverage = df['High_Temp_F'].notna().sum()
    wind_coverage = df['Avg_Wind_MPH'].notna().sum()
    
    print(f"\nFinal Data Coverage:")
    print(f"Temperature data: {temp_coverage}/{len(df)} days ({temp_coverage/len(df)*100:.1f}%)")
    print(f"Wind data: {wind_coverage}/{len(df)} days ({wind_coverage/len(df)*100:.1f}%)")
    
    # Show April-June 2025 coverage specifically
    april_june_2025 = df[(pd.to_datetime(df['Date']) >= '2025-04-01') & (pd.to_datetime(df['Date']) <= '2025-06-21')]
    if len(april_june_2025) > 0:
        april_june_temp = april_june_2025['High_Temp_F'].notna().sum()
        april_june_wind = april_june_2025['Avg_Wind_MPH'].notna().sum()
        
        print(f"\nApril-June 2025 Coverage:")
        print(f"Temperature: {april_june_temp}/{len(april_june_2025)} days ({april_june_temp/len(april_june_2025)*100:.1f}%)")
        print(f"Wind: {april_june_wind}/{len(april_june_2025)} days ({april_june_wind/len(april_june_2025)*100:.1f}%)")
    
    return output_file

def main():
    """Main function to get missing temperature/wind data"""
    
    print("Getting Missing Temperature/Wind Data for April-June 2025")
    print("="*60)
    
    # Get missing data
    missing_data = get_missing_temp_wind_data()
    if not missing_data:
        print("No missing data retrieved")
        return
    
    # Update dataset
    final_file = update_dataset_with_missing_data(missing_data)
    if final_file is None:
        print("Failed to update dataset")
        return
    
    print(f"\n" + "="*60)
    print("FINAL COMPLETE DATASET READY!")
    print(f"File: {final_file}")
    print("Attempted to fill missing temperature/wind data for Apr-Jun 2025")
    print("="*60)

if __name__ == "__main__":
    main()