#!/usr/bin/env python3
"""
Investigate NOAA units and potential conversion issues
Check what units NOAA actually uses for airport precipitation data
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def check_noaa_units():
    """Check NOAA API documentation and raw data units"""
    
    # Load config
    config_path = os.path.join(BASE_DIR, "config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    noaa_token = config.get("noaa_token")
    
    print("Investigating NOAA precipitation units...")
    print("="*50)
    
    # Check the datatypes endpoint for precipitation info
    print("\n1. Checking NOAA datatypes for precipitation...")
    
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/datatypes"
    params = {
        "datatypeid": "PRCP",
        "limit": 10
    }
    headers = {"token": noaa_token}
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data:
            for datatype in data["results"]:
                print(f"  ID: {datatype['id']}")
                print(f"  Name: {datatype['name']}")
                if 'minvalue' in datatype:
                    print(f"  Min value: {datatype['minvalue']}")
                if 'maxvalue' in datatype:
                    print(f"  Max value: {datatype['maxvalue']}")
                if 'units' in datatype:
                    print(f"  Units: {datatype['units']}")
                print()
    except Exception as e:
        print(f"Error checking datatypes: {e}")
    
    # Get raw data and check the actual values vs what we're getting
    print("\n2. Getting raw NOAA data for KCEC to check units...")
    
    correct_station = "GHCND:USW00024286"  # KCEC
    
    # Test with different unit parameters
    unit_tests = [
        ("standard", "Standard units"),
        ("metric", "Metric units"),
        (None, "Default units")
    ]
    
    for units_param, description in unit_tests:
        print(f"\n   Testing with {description}:")
        
        base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
        params = {
            "datasetid": "GHCND",
            "stationid": correct_station,
            "datatypeid": "PRCP",
            "startdate": "2024-01-13",  # Day we know has 0.01" rain
            "enddate": "2024-01-13",
            "limit": 10
        }
        
        if units_param:
            params["units"] = units_param
            
        headers = {"token": noaa_token}
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data and len(data["results"]) > 0:
                record = data["results"][0]
                raw_value = record["value"]
                
                print(f"     Raw value: {raw_value}")
                print(f"     Date: {record['date']}")
                print(f"     Station: {record['station']}")
                
                # Try different conversion methods
                print(f"     Conversions:")
                print(f"       Raw value: {raw_value}")
                print(f"       Divide by 10: {raw_value / 10}")
                print(f"       Divide by 100: {raw_value / 100}")
                print(f"       Divide by 254: {raw_value / 254}")
                print(f"       Current method (÷10÷25.4): {raw_value / 10 / 25.4:.4f}")
                print(f"       Direct ÷25.4: {raw_value / 25.4:.4f}")
                print(f"       ÷1000÷25.4: {raw_value / 1000 / 25.4:.4f}")
                
            else:
                print(f"     No data found")
                
        except Exception as e:
            print(f"     Error: {e}")
    
    # Check a day that should have significant rainfall according to Hayden
    print(f"\n3. Checking January 2nd (Hayden shows 1.02 inches)...")
    
    params = {
        "datasetid": "GHCND",
        "stationid": correct_station,
        "datatypeid": "PRCP",
        "startdate": "2024-01-02",
        "enddate": "2024-01-02",
        "units": "standard",
        "limit": 10
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            record = data["results"][0]
            raw_value = record["value"]
            
            print(f"   Raw value for Jan 2: {raw_value}")
            print(f"   Hayden shows: 1.02 inches")
            print(f"   Our conversion: {raw_value / 10 / 25.4:.4f} inches")
            
            # See if any conversion gives us close to 1.02
            print(f"   Trying to match 1.02 inches:")
            if raw_value:
                print(f"     Raw value: {raw_value}")
                print(f"     Raw × 0.001: {raw_value * 0.001:.4f}")
                print(f"     Raw × 0.01: {raw_value * 0.01:.4f}")
                print(f"     Raw × 0.1: {raw_value * 0.1:.4f}")
                print(f"     Raw ÷ 10: {raw_value / 10:.4f}")
                print(f"     Raw ÷ 100: {raw_value / 100:.4f}")
                
        else:
            print(f"   No data found for Jan 2 - might be why it shows 0!")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check documentation about GHCND units
    print(f"\n4. GHCND Dataset Information:")
    print(f"   According to NOAA documentation:")
    print(f"   - GHCND precipitation is typically in tenths of millimeters")
    print(f"   - Value of 100 = 10.0 mm = 0.394 inches")
    print(f"   - Value of 254 = 25.4 mm = 1.0 inches")
    print(f"   - Our current conversion: value ÷ 10 ÷ 25.4 should be correct")
    
    print(f"\n5. Theory: Missing data vs wrong conversion")
    print(f"   If Hayden shows significant rain on days NOAA shows 0,")
    print(f"   it might be missing data rather than conversion error.")
    print(f"   Some weather stations don't report all precipitation events.")

if __name__ == "__main__":
    check_noaa_units()