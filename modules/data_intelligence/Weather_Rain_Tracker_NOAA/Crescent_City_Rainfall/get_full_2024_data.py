#!/usr/bin/env python3
"""
Get full 2024 KCEC weather data and prepare for comparison
"""

import os
import sys
import json
import requests
import pandas as pd
from datetime import datetime
import csv

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "weather_data")

def download_missing_2024_data():
    """Download Jan 1 - Apr 30, 2024 data directly using NOAA API"""
    
    # Load config
    config_path = os.path.join(BASE_DIR, "config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    noaa_token = config.get("noaa_token")
    if not noaa_token:
        print("ERROR: No NOAA token in config")
        return None
    
    # NOAA API parameters
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    params = {
        "datasetid": "GHCND",
        "stationid": "GHCND:USW00093814",  # KCEC station
        "datatypeid": "PRCP",  # Precipitation
        "startdate": "2024-01-01",
        "enddate": "2024-04-30",
        "units": "standard",
        "limit": 1000
    }
    headers = {"token": noaa_token}
    
    print("Downloading from NOAA API...")
    response = requests.get(base_url, params=params, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    
    if "results" in data:
        # Process the data
        results = []
        for item in data["results"]:
            date = item["date"][:10]  # Get just YYYY-MM-DD
            # Convert from tenths of mm to inches
            inches = item["value"] / 10 / 25.4 if item["value"] is not None else 0.0
            
            results.append({
                "Date": date + "T00:00:00",
                "Total_Inches": round(inches, 2),
                "Category": get_rain_category(inches),
                "Measurable_0.01": "Yes" if inches >= 0.01 else "No",
                "Light_0.01": "Yes" if 0.01 <= inches < 0.25 else "No",
                "Moderate_0.25": "Yes" if 0.25 <= inches < 0.5 else "No",
                "Heavy_0.5": "Yes" if 0.5 <= inches < 1.0 else "No",
                "Very_Heavy_1.0": "Yes" if inches >= 1.0 else "No",
                "Timestamp": datetime.now().isoformat()
            })
        
        # Save to file
        output_file = os.path.join(DATA_DIR, "kcec_jan_apr_2024.csv")
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False)
        print(f"Saved {len(results)} days to {output_file}")
        return output_file
    else:
        print("No data found")
        return None

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

def combine_full_year_2024():
    """Combine all 2024 data into one file"""
    
    # Get Jan-Apr data
    jan_apr_file = os.path.join(DATA_DIR, "kcec_jan_apr_2024.csv")
    if not os.path.exists(jan_apr_file):
        print("Downloading Jan-Apr 2024 data first...")
        download_missing_2024_data()
    
    # Read Jan-Apr data
    jan_apr_df = pd.read_csv(jan_apr_file)
    
    # Read May-Dec data from existing file
    may_dec_file = os.path.join(BASE_DIR, "kcec_corrected_historical_2024-05-01_to_2025-06-11.csv")
    may_dec_df = pd.read_csv(may_dec_file)
    
    # Filter only 2024 data
    may_dec_2024 = may_dec_df[may_dec_df['Date'].str.startswith('2024')]
    
    # Combine
    full_2024 = pd.concat([jan_apr_df, may_dec_2024], ignore_index=True)
    full_2024['Date'] = pd.to_datetime(full_2024['Date'])
    full_2024 = full_2024.sort_values('Date')
    
    # Save combined file
    output_file = os.path.join(DATA_DIR, f"kcec_full_2024_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    full_2024.to_csv(output_file, index=False)
    
    # Print summary
    print(f"\nCombined 2024 data saved to: {output_file}")
    print(f"Total days in 2024: {len(full_2024)}")
    
    rainy_days = (full_2024['Total_Inches'] > 0).sum()
    total_rainfall = full_2024['Total_Inches'].sum()
    
    print(f"Rainy days: {rainy_days}")
    print(f"Total rainfall: {total_rainfall:.2f} inches")
    
    # Monthly breakdown
    full_2024['Month'] = full_2024['Date'].dt.month
    monthly = full_2024.groupby('Month').agg({
        'Total_Inches': ['sum', lambda x: (x > 0).sum()]
    })
    monthly.columns = ['Total_Inches', 'Rainy_Days']
    
    print("\nMonthly breakdown:")
    for month, row in monthly.iterrows():
        month_name = datetime(2024, month, 1).strftime('%B')
        print(f"{month_name}: {row['Total_Inches']:.2f} inches, {int(row['Rainy_Days'])} rainy days")
    
    return output_file

if __name__ == "__main__":
    # Create data directory if needed
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print("Getting full 2024 KCEC weather data...")
    output_file = combine_full_year_2024()
    
    if output_file:
        print(f"\nSuccess! Full 2024 data is ready at: {output_file}")
        print("\nYou can now compare this with the external data.")