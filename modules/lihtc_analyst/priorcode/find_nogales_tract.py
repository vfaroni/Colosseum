#!/usr/bin/env python3
"""
Find the specific census tract for United Church Village Apartments in Nogales
and check for both QCT and DDA status
"""

import pandas as pd
import requests
import json
import time

def get_tract_for_coordinates(lat, lon):
    """Get census tract for given coordinates using Census Geocoding API"""
    
    # Census Geocoding API
    url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
    params = {
        "x": lon,
        "y": lat,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('result') and data['result'].get('geographies'):
            geogs = data['result']['geographies']
            
            # Extract tract info
            if 'Census Tracts' in geogs and geogs['Census Tracts']:
                tract_info = geogs['Census Tracts'][0]
                return {
                    'state': tract_info.get('STATE'),
                    'county': tract_info.get('COUNTY'), 
                    'tract': tract_info.get('TRACT'),
                    'geoid': tract_info.get('GEOID'),
                    'name': tract_info.get('NAME')
                }
    except Exception as e:
        print(f"Error getting tract info: {e}")
        
    return None

def check_nogales_location():
    """Check the specific location of United Church Village Apartments"""
    
    # United Church Village Apartments coordinates
    lat = 31.3713391
    lon = -110.9240253
    
    print("="*70)
    print("FINDING CENSUS TRACT FOR UNITED CHURCH VILLAGE APARTMENTS")
    print("="*70)
    print(f"Location: {lat}, {lon}")
    print("Address: Nogales, Arizona")
    
    # Get tract information
    tract_info = get_tract_for_coordinates(lat, lon)
    
    if tract_info:
        print(f"\nCensus Tract Information:")
        print(f"State FIPS: {tract_info['state']}")
        print(f"County FIPS: {tract_info['county']}")  
        print(f"Tract: {tract_info['tract']}")
        print(f"GEOID: {tract_info['geoid']}")
        print(f"Name: {tract_info['name']}")
        
        # Now check this tract in our QCT data
        check_tract_in_qct_data(tract_info)
    else:
        print("Could not determine census tract for this location")

def check_tract_in_qct_data(tract_info):
    """Check if the specific tract is in our QCT data"""
    
    base_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
    excel_file = f"{base_path}/qct_data_2025.xlsx"
    
    print(f"\n" + "="*70)
    print("CHECKING TRACT IN QCT DATABASE")
    print("="*70)
    
    df = pd.read_excel(excel_file)
    
    # Convert tract info to match our data format
    state_code = int(tract_info['state'])
    county_code = int(tract_info['county'])
    tract_num = float(tract_info['tract'])
    
    # Find matching record
    matching_tract = df[
        (df['state'] == state_code) & 
        (df['county'] == county_code) & 
        (df['tract'] == tract_num)
    ]
    
    if len(matching_tract) > 0:
        print(f"Found tract in QCT database:")
        record = matching_tract.iloc[0]
        print(f"State: {record['state']}")
        print(f"County: {record['county']}")  
        print(f"Tract: {record['tract']}")
        print(f"QCT Status: {record['qct']} ({'QCT' if record['qct'] == 1 else 'Not QCT'})")
        
        # Show additional data
        print(f"\nAdditional Information:")
        print(f"Metro/Non-metro: {record.get('metro', 'N/A')}")
        print(f"CBSA: {record.get('cbsa', 'N/A')}")
        if 'pov_rate_22' in record:
            print(f"Poverty Rate 2022: {record['pov_rate_22']:.1%}")
            
    else:
        print(f"Tract not found in QCT database!")
        print(f"Looking for: State={state_code}, County={county_code}, Tract={tract_num}")
        
        # Show what tracts we do have for Santa Cruz County
        santa_cruz = df[(df['state'] == 4) & (df['county'] == 23)]
        print(f"\nSanta Cruz County tracts in database:")
        print(santa_cruz[['state', 'county', 'tract', 'qct']].sort_values('tract'))

def download_dda_data():
    """Try to download DDA data as well"""
    
    print(f"\n" + "="*70)
    print("DOWNLOADING DDA DATA")
    print("="*70)
    
    # DDA data URLs from HUD
    dda_urls = [
        "https://www.huduser.gov/portal/datasets/qct/DDA2025M.pdf",  # Metro DDAs
        "https://www.huduser.gov/portal/datasets/qct/DDA2025NM.pdf"  # Non-metro DDAs
    ]
    
    print("DDA data is typically provided in PDF format by HUD.")
    print("For programmatic access, we need to check if there are CSV/Excel versions.")
    
    # Let me search for DDA data files
    import os
    base_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
    
    print(f"\nChecking for existing DDA files in: {base_path}")
    
    for file in os.listdir(base_path):
        if 'dda' in file.lower():
            print(f"Found DDA file: {file}")

if __name__ == "__main__":
    check_nogales_location()
    download_dda_data()