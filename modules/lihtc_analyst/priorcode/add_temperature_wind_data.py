#!/usr/bin/env python3
"""
Add temperature and wind data to the complete KCEC dataset
Download TMAX, TMIN, and AWND (wind) data and merge with existing precipitation data
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

def download_temperature_wind_data():
    """Download temperature and wind data for the complete date range"""
    
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
    
    # Get data for full range: 2024-01-01 to 2025-06-21
    print(f"Downloading temperature and wind data: {correct_station}")
    print("Data types: TMAX (high temp), TMIN (low temp), AWND (avg wind)")
    print("Using correct units (standard = °F and mph)")
    
    # Split into quarterly chunks to avoid API limits
    all_data = {}
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    headers = {"token": noaa_token}
    
    # Define date chunks (quarterly)
    date_chunks = [
        ("2024-01-01", "2024-03-31"),  # Q1 2024
        ("2024-04-01", "2024-06-30"),  # Q2 2024
        ("2024-07-01", "2024-09-30"),  # Q3 2024
        ("2024-10-01", "2024-12-31"),  # Q4 2024
        ("2025-01-01", "2025-03-31"),  # Q1 2025
        ("2025-04-01", "2025-06-21"),  # Q2 2025 (partial)
    ]
    
    print(f"Will download {len(date_chunks)} quarterly chunks...")
    
    for chunk_start, chunk_end in date_chunks:
        print(f"  Downloading {chunk_start} to {chunk_end}...")
        
        params = {
            "datasetid": "GHCND",
            "stationid": correct_station,
            "datatypeid": "TMAX,TMIN,AWND",  # Multiple data types
            "startdate": chunk_start,
            "enddate": chunk_end,
            "units": "standard",  # Returns °F and mph
            "limit": 1000
        }
        
        try:
            time.sleep(1)  # Rate limiting
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data:
                print(f"    Got {len(data['results'])} records")
                
                # Process the data by date and data type
                for item in data["results"]:
                    date = item["date"][:10]
                    datatype = item["datatype"]
                    value = item["value"] if item["value"] else None
                    
                    if date not in all_data:
                        all_data[date] = {}
                    
                    # Store by data type
                    if datatype == "TMAX":
                        all_data[date]["High_Temp_F"] = round(value, 1) if value else None
                    elif datatype == "TMIN":
                        all_data[date]["Low_Temp_F"] = round(value, 1) if value else None
                    elif datatype == "AWND":
                        all_data[date]["Avg_Wind_MPH"] = round(value, 1) if value else None
                        
            else:
                print(f"    No data for {chunk_start} to {chunk_end}")
                
        except Exception as e:
            print(f"    Error downloading {chunk_start} to {chunk_end}: {e}")
    
    print(f"Total dates with temperature/wind data: {len(all_data)}")
    
    return all_data

def merge_with_precipitation_data(temp_wind_data):
    """Merge temperature/wind data with existing precipitation dataset"""
    
    print("\nMerging temperature/wind data with precipitation data...")
    
    # Find the most recent complete precipitation dataset
    pattern = os.path.join(DATA_DIR, "kcec_complete_2024-01-01_to_2025-06-21_*.csv")
    files = glob.glob(pattern)
    
    if not files:
        print("ERROR: Complete precipitation dataset not found")
        return None
    
    precip_file = max(files, key=os.path.getctime)
    print(f"Reading precipitation data: {precip_file}")
    
    # Read precipitation data
    df = pd.read_csv(precip_file)
    print(f"Precipitation records: {len(df)}")
    
    # Add temperature and wind columns
    df['High_Temp_F'] = None
    df['Low_Temp_F'] = None
    df['Avg_Wind_MPH'] = None
    
    # Merge the data
    for index, row in df.iterrows():
        date_str = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
        
        if date_str in temp_wind_data:
            df.at[index, 'High_Temp_F'] = temp_wind_data[date_str].get('High_Temp_F')
            df.at[index, 'Low_Temp_F'] = temp_wind_data[date_str].get('Low_Temp_F')
            df.at[index, 'Avg_Wind_MPH'] = temp_wind_data[date_str].get('Avg_Wind_MPH')
    
    # Reorder columns to put temperature/wind after the basic info
    columns = [
        'Date', 'Year', 'Month', 'Day', 'Month_Name', 'Day_of_Week',
        'Total_Inches', 'High_Temp_F', 'Low_Temp_F', 'Avg_Wind_MPH',
        'Category', 'Measurable_0.01', 'Contract_0.10', 'Normal_0.25', 'Heavy_0.50',
        'Light_0.01', 'Moderate_0.25', 'Heavy_0.5', 'Very_Heavy_1.0',
        'Work_Suitable', 'Timestamp'
    ]
    
    df_enhanced = df[columns]
    
    # Save enhanced dataset
    start_date = pd.to_datetime(df_enhanced['Date']).min().strftime('%Y-%m-%d')
    end_date = pd.to_datetime(df_enhanced['Date']).max().strftime('%Y-%m-%d')
    
    output_file = os.path.join(DATA_DIR, f"kcec_complete_with_temp_wind_{start_date}_to_{end_date}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df_enhanced.to_csv(output_file, index=False)
    
    print(f"Enhanced dataset saved: {output_file}")
    print(f"Total records: {len(df_enhanced)}")
    
    # Show temperature/wind data coverage
    temp_coverage = df_enhanced['High_Temp_F'].notna().sum()
    wind_coverage = df_enhanced['Avg_Wind_MPH'].notna().sum()
    
    print(f"\nData Coverage:")
    print(f"Temperature data: {temp_coverage}/{len(df_enhanced)} days ({temp_coverage/len(df_enhanced)*100:.1f}%)")
    print(f"Wind data: {wind_coverage}/{len(df_enhanced)} days ({wind_coverage/len(df_enhanced)*100:.1f}%)")
    
    # Show sample data
    print(f"\nSample of enhanced data:")
    print(df_enhanced[['Date', 'Total_Inches', 'High_Temp_F', 'Low_Temp_F', 'Avg_Wind_MPH', 'Contract_0.10']].head(10))
    
    # Show temperature/wind statistics
    if temp_coverage > 0:
        print(f"\nTemperature Statistics:")
        print(f"High Temperature: {df_enhanced['High_Temp_F'].min():.1f}°F to {df_enhanced['High_Temp_F'].max():.1f}°F")
        print(f"Low Temperature: {df_enhanced['Low_Temp_F'].min():.1f}°F to {df_enhanced['Low_Temp_F'].max():.1f}°F")
        print(f"Average High: {df_enhanced['High_Temp_F'].mean():.1f}°F")
        print(f"Average Low: {df_enhanced['Low_Temp_F'].mean():.1f}°F")
    
    if wind_coverage > 0:
        print(f"\nWind Statistics:")
        print(f"Wind Speed: {df_enhanced['Avg_Wind_MPH'].min():.1f} to {df_enhanced['Avg_Wind_MPH'].max():.1f} mph")
        print(f"Average Wind: {df_enhanced['Avg_Wind_MPH'].mean():.1f} mph")
    
    return output_file

def main():
    """Main function to add temperature and wind data"""
    
    print("Adding Temperature and Wind Data to KCEC Dataset")
    print("="*60)
    
    # Download temperature and wind data
    temp_wind_data = download_temperature_wind_data()
    if not temp_wind_data:
        print("Failed to download temperature/wind data")
        return
    
    # Merge with precipitation data
    enhanced_file = merge_with_precipitation_data(temp_wind_data)
    if enhanced_file is None:
        print("Failed to merge data")
        return
    
    print(f"\n" + "="*60)
    print("ENHANCED DATASET READY!")
    print(f"File: {enhanced_file}")
    print("Added columns: High_Temp_F, Low_Temp_F, Avg_Wind_MPH")
    print("All rainfall thresholds preserved")
    print("Ready for comprehensive weather analysis!")
    print("="*60)

if __name__ == "__main__":
    main()