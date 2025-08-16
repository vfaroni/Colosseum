#!/usr/bin/env python3
"""
Debug NOAA API data formats to understand the conversion issues
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
NOAA_TOKEN = 'oaLvXPjjAWoSCizEBvNoHPNhATmdDmQA'
STATION_ID = "GHCND:USW00093814"

def debug_api_response():
    """Get a small sample and examine the raw data"""
    
    # Get just a few days of recent data
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    
    print(f"Debugging NOAA API response for {start_date} to {end_date}")
    print("=" * 60)
    
    # Try different unit settings
    for units in ["standard", "metric"]:
        print(f"\n--- Testing with units='{units}' ---")
        
        url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
        params = {
            "datasetid": "GHCND",
            "stationid": STATION_ID,
            "datatypeid": "PRCP,TMAX,TMIN",
            "startdate": start_date,
            "enddate": end_date,
            "limit": 20,
            "units": units
        }
        
        headers = {"token": NOAA_TOKEN}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if "results" in data:
                print(f"Found {len(data['results'])} records")
                
                # Show first few records for each data type
                for datatype in ["PRCP", "TMAX", "TMIN"]:
                    examples = [r for r in data["results"] if r["datatype"] == datatype][:3]
                    if examples:
                        print(f"\n{datatype} examples:")
                        for ex in examples:
                            print(f"  Date: {ex['date']}, Value: {ex['value']}, Units: {ex.get('unitCode', 'N/A')}")
                            
                            # Show conversion attempts
                            if datatype == "PRCP":
                                # Original conversion: value / 10 / 25.4
                                orig_conversion = ex['value'] / 10 / 25.4
                                # Alternative: value directly in tenths of mm, so /10 to get mm, /25.4 to get inches
                                alt_conversion = ex['value'] / 254.0  # Direct to inches if value is in tenths of mm
                                # Maybe it's already in inches?
                                direct_inches = ex['value']
                                print(f"    Original conversion: {orig_conversion:.4f} inches")
                                print(f"    Alternative: {alt_conversion:.4f} inches")
                                print(f"    Direct value: {direct_inches:.4f} inches")
                                
                            elif datatype in ["TMAX", "TMIN"]:
                                # Check if already in F or needs C to F conversion
                                direct_f = ex['value']
                                c_to_f = ex['value'] * 9/5 + 32
                                print(f"    Direct F: {direct_f}°F")
                                print(f"    C to F: {c_to_f}°F")
            else:
                print("No results found")
                
        except Exception as e:
            print(f"Error: {e}")

def check_station_metadata():
    """Check what the station metadata says about units"""
    print("\n" + "=" * 60)
    print("STATION METADATA")
    print("=" * 60)
    
    try:
        # Get station info
        url = f"https://www.ncdc.noaa.gov/cdo-web/api/v2/stations/{STATION_ID}"
        headers = {"token": NOAA_TOKEN}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        station_data = response.json()
        print("Station Info:")
        print(f"  Name: {station_data.get('name', 'N/A')}")
        print(f"  Elevation: {station_data.get('elevation', 'N/A')}")
        print(f"  Location: {station_data.get('latitude', 'N/A')}, {station_data.get('longitude', 'N/A')}")
        
    except Exception as e:
        print(f"Error getting station info: {e}")

def test_known_rainy_period():
    """Test a period that should definitely have rain in Crescent City"""
    print("\n" + "=" * 60)
    print("TESTING KNOWN RAINY PERIOD (Winter 2024)")
    print("=" * 60)
    
    # Test January 2024 - should be rainy season
    start_date = "2024-01-01"
    end_date = "2024-01-31"
    
    url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
    params = {
        "datasetid": "GHCND",
        "stationid": STATION_ID,
        "datatypeid": "PRCP",
        "startdate": start_date,
        "enddate": end_date,
        "limit": 100,
        "units": "standard"
    }
    
    headers = {"token": NOAA_TOKEN}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if "results" in data:
            precip_values = [r["value"] for r in data["results"]]
            print(f"January 2024 precipitation values (first 10): {precip_values[:10]}")
            print(f"Max value: {max(precip_values)}")
            print(f"Values > 0: {len([v for v in precip_values if v > 0])}")
            
            # Test different conversion approaches
            print("\nConversion testing on max value:")
            max_val = max(precip_values)
            print(f"  Raw value: {max_val}")
            print(f"  /10/25.4 = {max_val/10/25.4:.4f} inches")
            print(f"  /254 = {max_val/254:.4f} inches") 
            print(f"  /100 = {max_val/100:.4f} inches")
            print(f"  /1000 = {max_val/1000:.4f} inches")
            
        else:
            print("No precipitation data found for January 2024")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_api_response()
    check_station_metadata()
    test_known_rainy_period()