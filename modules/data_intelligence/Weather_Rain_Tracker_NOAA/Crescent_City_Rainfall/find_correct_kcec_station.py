#!/usr/bin/env python3
"""
Find the correct NOAA station code for Crescent City Airport (KCEC)
"""

import os
import json
import requests
import pandas as pd

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def search_kcec_stations():
    """Search for NOAA stations near Crescent City, CA"""
    
    # Load config
    config_path = os.path.join(BASE_DIR, "config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    noaa_token = config.get("noaa_token")
    if not noaa_token:
        print("ERROR: No NOAA token in config")
        return
    
    # Search for stations near Crescent City
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/stations"
    
    # First, search by location name
    params = {
        "locationid": "CITY:CA000045",  # Try Crescent City location ID
        "datasetid": "GHCND",
        "limit": 50
    }
    headers = {"token": noaa_token}
    
    print("Searching for stations near Crescent City, CA...")
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data:
            print(f"Found {len(data['results'])} stations")
            for station in data['results']:
                print(f"  {station['id']} - {station['name']}")
                if 'elevation' in station:
                    print(f"    Elevation: {station['elevation']}m")
                if 'mindate' in station and 'maxdate' in station:
                    print(f"    Date range: {station['mindate']} to {station['maxdate']}")
                print()
        else:
            print("No stations found with location search")
    except Exception as e:
        print(f"Location search failed: {e}")
    
    # Search by coordinates (Crescent City Airport coordinates)
    print("\nSearching by coordinates near KCEC...")
    
    # KCEC coordinates: approximately 41.7802°N, 124.2366°W
    params = {
        "extent": "41.5,-124.5,42.0,-124.0",  # Bounding box around Crescent City
        "datasetid": "GHCND",
        "limit": 50
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data:
            print(f"Found {len(data['results'])} stations in area")
            for station in data['results']:
                name = station.get('name', 'Unknown')
                station_id = station['id']
                
                # Look for airport or KCEC related stations
                if any(keyword in name.upper() for keyword in ['AIRPORT', 'KCEC', 'CRESCENT CITY']):
                    print(f"*** POTENTIAL MATCH: {station_id} - {name}")
                else:
                    print(f"  {station_id} - {name}")
                
                if 'elevation' in station:
                    print(f"    Elevation: {station['elevation']}m")
                if 'mindate' in station and 'maxdate' in station:
                    print(f"    Date range: {station['mindate']} to {station['maxdate']}")
                print()
        else:
            print("No stations found in coordinate search")
    except Exception as e:
        print(f"Coordinate search failed: {e}")
    
    # Search for stations with "CRESCENT" in the name
    print("\nSearching for stations with 'CRESCENT' in name...")
    
    params = {
        "datasetid": "GHCND",
        "limit": 1000  # Get many stations to search through
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data:
            crescent_stations = []
            for station in data['results']:
                name = station.get('name', '').upper()
                if 'CRESCENT' in name or 'KCEC' in name:
                    crescent_stations.append(station)
            
            if crescent_stations:
                print(f"Found {len(crescent_stations)} stations with 'CRESCENT' or 'KCEC':")
                for station in crescent_stations:
                    print(f"*** {station['id']} - {station['name']}")
                    if 'elevation' in station:
                        print(f"    Elevation: {station['elevation']}m")
                    if 'mindate' in station and 'maxdate' in station:
                        print(f"    Date range: {station['mindate']} to {station['maxdate']}")
                    print()
            else:
                print("No stations found with 'CRESCENT' or 'KCEC' in name")
    except Exception as e:
        print(f"Name search failed: {e}")

def test_station_data(station_id):
    """Test getting data from a specific station"""
    
    # Load config
    config_path = os.path.join(BASE_DIR, "config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    noaa_token = config.get("noaa_token")
    
    print(f"\nTesting data retrieval for station: {station_id}")
    
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    params = {
        "datasetid": "GHCND",
        "stationid": station_id,
        "datatypeid": "PRCP",
        "startdate": "2024-01-01",
        "enddate": "2024-01-31",  # Just test January
        "units": "standard",
        "limit": 100
    }
    headers = {"token": noaa_token}
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data:
            print(f"Success! Found {len(data['results'])} precipitation records for January 2024")
            
            # Show first few records
            for i, record in enumerate(data['results'][:5]):
                date = record['date'][:10]
                precip_mm = record['value'] / 10 if record['value'] else 0  # tenths of mm to mm
                precip_inches = precip_mm / 25.4  # mm to inches
                print(f"  {date}: {precip_inches:.2f} inches")
            
            # Calculate total for January
            total_mm = sum(r['value'] / 10 for r in data['results'] if r['value'])
            total_inches = total_mm / 25.4
            print(f"  January 2024 total: {total_inches:.2f} inches")
            
            return True
        else:
            print("No precipitation data found for this station")
            return False
    except Exception as e:
        print(f"Error testing station {station_id}: {e}")
        return False

if __name__ == "__main__":
    print("Finding correct NOAA station for KCEC - Crescent City Airport")
    print("="*60)
    
    search_kcec_stations()
    
    # Test some common station patterns
    test_stations = [
        "GHCND:USW00093814",  # Current one we're using
        "GHCND:USC00041897",  # Crescent City pattern
        "GHCND:USW00024284",  # Another airport pattern
    ]
    
    print("\n" + "="*60)
    print("TESTING KNOWN STATION PATTERNS")
    print("="*60)
    
    for station in test_stations:
        success = test_station_data(station)
        if success:
            print(f"*** STATION {station} HAS GOOD DATA ***")
        print()