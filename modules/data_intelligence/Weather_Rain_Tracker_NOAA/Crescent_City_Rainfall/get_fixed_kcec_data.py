#!/usr/bin/env python3
"""
Get KCEC data with CORRECT units handling
NOAA API with units=standard returns values already in inches!
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

def download_fixed_kcec_data():
    """Download KCEC data with correct units (no double conversion)"""
    
    # Load config
    config_path = os.path.join(BASE_DIR, "config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    noaa_token = config.get("noaa_token")
    if not noaa_token:
        print("ERROR: No NOAA token in config")
        return
    
    # Correct KCEC station
    correct_station = "GHCND:USW00024286"  # CRESCENT CITY MCNAMARA AIRPORT
    
    print(f"Downloading CORRECTED KCEC data: {correct_station}")
    print("Using units=standard (values already in inches - NO conversion needed)")
    print("Date range: January 1 - April 30, 2024")
    
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    params = {
        "datasetid": "GHCND",
        "stationid": correct_station,
        "datatypeid": "PRCP",
        "startdate": "2024-01-01",
        "enddate": "2024-04-30",
        "units": "standard",  # This returns values in inches!
        "limit": 500
    }
    headers = {"token": noaa_token}
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data:
            print(f"Downloaded {len(data['results'])} records")
            
            # Process the data - NO CONVERSION NEEDED!
            daily_data = {}
            for item in data["results"]:
                date = item["date"][:10]  # Get just YYYY-MM-DD
                inches = item["value"] if item["value"] else 0.0  # Already in inches!
                daily_data[date] = round(inches, 2)
            
            # Show first few days as verification
            print(f"\nFirst few days (should match Hayden's data now):")
            for i, (date, inches) in enumerate(list(daily_data.items())[:10]):
                print(f"  {date}: {inches:.2f} inches")
                if i == 1 and inches == 1.02:  # Jan 2 should be 1.02
                    print("    *** MATCH! This confirms units are correct ***")
            
            # Create complete dataset with all days
            results = []
            current_date = datetime(2024, 1, 1)
            end_date = datetime(2024, 4, 30)
            
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                inches = daily_data.get(date_str, 0.0)
                
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
            
            # Save corrected data
            output_file = os.path.join(DATA_DIR, f"kcec_FIXED_jan_apr_2024_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            df = pd.DataFrame(results)
            df.to_csv(output_file, index=False)
            
            print(f"\nFIXED data saved to: {output_file}")
            
            # Summary statistics
            rainy_days = sum(1 for r in results if r["Total_Inches"] > 0)
            contract_days = sum(1 for r in results if r["Total_Inches"] >= 0.10)
            total_rain = sum(r["Total_Inches"] for r in results)
            
            print(f"\nCorrected Summary for Jan-Apr 2024:")
            print(f"  Total days: {len(results)}")
            print(f"  Rainy days (>0\"): {rainy_days}")
            print(f"  Contract days (≥0.10\"): {contract_days}")
            print(f"  Total rainfall: {total_rain:.2f} inches")
            
            # Monthly breakdown
            monthly = {1: {"total": 0, "days": 0, "contract": 0},
                      2: {"total": 0, "days": 0, "contract": 0},
                      3: {"total": 0, "days": 0, "contract": 0},
                      4: {"total": 0, "days": 0, "contract": 0}}
            
            for result in results:
                month = int(result["Date"][5:7])
                monthly[month]["total"] += result["Total_Inches"]
                if result["Total_Inches"] > 0:
                    monthly[month]["days"] += 1
                if result["Total_Inches"] >= 0.10:
                    monthly[month]["contract"] += 1
            
            month_names = ["", "January", "February", "March", "April"]
            print(f"\nMonthly breakdown:")
            for month in [1, 2, 3, 4]:
                print(f"  {month_names[month]}: {monthly[month]['total']:.2f}\" total, "
                      f"{monthly[month]['days']} rainy days, {monthly[month]['contract']} contract days")
            
            return output_file
            
        else:
            print("No results found")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("Getting FIXED KCEC data with correct units handling")
    print("*** NO DOUBLE CONVERSION - NOAA standard units = inches! ***")
    print("="*60)
    
    fixed_file = download_fixed_kcec_data()
    
    if fixed_file:
        print(f"\n*** BREAKTHROUGH! ***")
        print(f"Fixed KCEC data saved to: {fixed_file}")
        print("\nThis should now match Hayden's data perfectly!")
        print("The issue was double-conversion: NOAA was already giving us inches.")
    else:
        print("\nFailed to get fixed data")