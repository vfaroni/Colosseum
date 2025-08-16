#!/usr/bin/env python3
"""
Download historical KCEC weather data for multiple years
Using the same format as the existing 2024 data
"""

import os
import sys
import json
import requests
import pandas as pd
from datetime import datetime
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

def download_year_data(year, noaa_token):
    """Download data for a specific year"""
    
    print(f"\nDownloading {year} data...")
    
    # NOAA API parameters
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    params = {
        "datasetid": "GHCND",
        "stationid": "GHCND:USW00093814",  # KCEC station
        "datatypeid": "PRCP,TMAX,TMIN,AWND",  # Precipitation, max temp, min temp, avg wind
        "startdate": f"{year}-01-01",
        "enddate": f"{year}-12-31",
        "units": "standard",
        "limit": 1000
    }
    headers = {"token": noaa_token}
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if "results" not in data:
            print(f"No data found for {year}")
            return None
        
        # Process the data - organize by date
        daily_data = {}
        
        for item in data["results"]:
            date = item["date"][:10]  # Get just YYYY-MM-DD
            
            if date not in daily_data:
                daily_data[date] = {
                    "Date": date + "T00:00:00",
                    "Total_Inches": 0.0,
                    "Max_Temp_F": None,
                    "Min_Temp_F": None,
                    "Avg_Wind_MPH": None
                }
            
            # Process by datatype
            if item["datatype"] == "PRCP":
                # Convert from tenths of mm to inches
                inches = item["value"] / 10 / 25.4 if item["value"] is not None else 0.0
                daily_data[date]["Total_Inches"] = round(inches, 2)
            elif item["datatype"] == "TMAX":
                # Convert from tenths of Celsius to Fahrenheit
                if item["value"] is not None:
                    celsius = item["value"] / 10
                    fahrenheit = (celsius * 9/5) + 32
                    daily_data[date]["Max_Temp_F"] = round(fahrenheit, 0)
            elif item["datatype"] == "TMIN":
                # Convert from tenths of Celsius to Fahrenheit
                if item["value"] is not None:
                    celsius = item["value"] / 10
                    fahrenheit = (celsius * 9/5) + 32
                    daily_data[date]["Min_Temp_F"] = round(fahrenheit, 0)
            elif item["datatype"] == "AWND":
                # Convert from tenths of meters per second to mph
                if item["value"] is not None:
                    mps = item["value"] / 10
                    mph = mps * 2.237
                    daily_data[date]["Avg_Wind_MPH"] = round(mph, 1)
        
        # Convert to list and add calculated fields
        results = []
        for date, data in sorted(daily_data.items()):
            inches = data["Total_Inches"]
            
            # Add category fields
            data["Category"] = get_rain_category(inches)
            data["Measurable_0.01"] = "Yes" if inches >= 0.01 else "No"
            data["Light_0.01"] = "Yes" if 0.01 <= inches < 0.25 else "No"
            data["Moderate_0.25"] = "Yes" if 0.25 <= inches < 0.5 else "No"
            data["Heavy_0.5"] = "Yes" if 0.5 <= inches < 1.0 else "No"
            data["Very_Heavy_1.0"] = "Yes" if inches >= 1.0 else "No"
            
            # Work suitability (simplified - no wind means assume suitable if not heavy rain)
            if data["Avg_Wind_MPH"] is not None:
                data["Work_Suitable"] = "No" if (inches >= 0.5 or data["Avg_Wind_MPH"] > 35) else "Yes"
            else:
                data["Work_Suitable"] = "No" if inches >= 0.5 else "Yes"
            
            data["Timestamp"] = datetime.now().isoformat()
            
            results.append(data)
        
        # Save to file
        output_file = os.path.join(DATA_DIR, f"kcec_historical_{year}.csv")
        df = pd.DataFrame(results)
        
        # Ensure all columns are present in the right order
        columns = [
            "Date", "Total_Inches", "Category", "Measurable_0.01", "Light_0.01", 
            "Moderate_0.25", "Heavy_0.5", "Very_Heavy_1.0", "Max_Temp_F", 
            "Min_Temp_F", "Avg_Wind_MPH", "Work_Suitable", "Timestamp"
        ]
        
        # Add missing columns with default values
        for col in columns:
            if col not in df.columns:
                df[col] = None
        
        df = df[columns]
        df.to_csv(output_file, index=False)
        
        print(f"Saved {len(results)} days to {output_file}")
        
        # Print summary
        rainy_days = sum(1 for r in results if r["Total_Inches"] > 0)
        contract_days = sum(1 for r in results if r["Total_Inches"] >= 0.10)
        total_rain = sum(r["Total_Inches"] for r in results)
        
        print(f"  Rainy days (>0\"): {rainy_days}")
        print(f"  Contract days (≥0.10\"): {contract_days}")
        print(f"  Total rainfall: {total_rain:.2f} inches")
        
        return output_file
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {year} data: {e}")
        return None

def main():
    """Download multiple years of historical data"""
    
    # Load config
    config_path = os.path.join(BASE_DIR, "config.json")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("ERROR: config.json not found")
        return
    
    noaa_token = config.get("noaa_token")
    if not noaa_token:
        print("ERROR: No NOAA token in config")
        return
    
    # Create data directory if needed
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Years to download
    years = [2023, 2022, 2021]  # Can add more years as needed
    
    print(f"Downloading KCEC historical data for years: {years}")
    print("This may take a few minutes due to API rate limits...")
    
    downloaded_files = []
    
    for year in years:
        # Add a small delay to avoid hitting rate limits
        if len(downloaded_files) > 0:
            print("Waiting 2 seconds before next request...")
            time.sleep(2)
        
        file_path = download_year_data(year, noaa_token)
        if file_path:
            downloaded_files.append(file_path)
    
    # Create a combined multi-year file
    if downloaded_files:
        print("\nCreating combined multi-year file...")
        
        all_data = []
        for file_path in downloaded_files:
            df = pd.read_csv(file_path)
            all_data.append(df)
        
        # Add 2024 data if it exists
        import glob
        pattern = os.path.join(DATA_DIR, "kcec_full_2024_*.csv")
        files_2024 = glob.glob(pattern)
        if files_2024:
            latest_2024 = max(files_2024, key=os.path.getctime)
            df_2024 = pd.read_csv(latest_2024)
            all_data.append(df_2024)
            years.append(2024)
        
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df['Date'] = pd.to_datetime(combined_df['Date'])
        combined_df = combined_df.sort_values('Date')
        
        output_file = os.path.join(DATA_DIR, f"kcec_multi_year_{min(years)}_{max(years)}.csv")
        combined_df.to_csv(output_file, index=False)
        
        print(f"\nCombined data saved to: {output_file}")
        print(f"Total records: {len(combined_df)}")
        
        # Print yearly summary
        combined_df['Year'] = combined_df['Date'].dt.year
        yearly_summary = combined_df.groupby('Year').agg({
            'Total_Inches': ['sum', lambda x: (x > 0).sum(), lambda x: (x >= 0.10).sum()]
        })
        yearly_summary.columns = ['Total_Rainfall', 'Rainy_Days', 'Contract_Days']
        
        print("\nYearly Summary:")
        print(yearly_summary)

if __name__ == "__main__":
    main()