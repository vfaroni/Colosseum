#!/usr/bin/env python3
"""
Find the correct NOAA station ID for KCEC Crescent City
"""

import requests
import json

NOAA_TOKEN = 'oaLvXPjjAWoSCizEBvNoHPNhATmdDmQA'

def search_stations():
    """Search for stations near Crescent City, CA"""
    
    print("Searching for KCEC and Crescent City stations...")
    print("=" * 60)
    
    # Search by location - Crescent City coordinates
    # Crescent City, CA is approximately 41.7558° N, 124.2026° W
    
    params = {
        "datasetid": "GHCND",
        "locationid": "FIPS:06015",  # Del Norte County, CA
        "limit": 50
    }
    
    headers = {"token": NOAA_TOKEN}
    
    try:
        url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/stations"
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if "results" in data:
            print(f"Found {len(data['results'])} stations in Del Norte County")
            
            # Look for stations with "CRESCENT" or airport codes
            relevant_stations = []
            for station in data["results"]:
                name = station.get("name", "").upper()
                station_id = station.get("id", "")
                
                if any(keyword in name for keyword in ["CRESCENT", "KCEC", "MCNAMARA", "AIRPORT"]):
                    relevant_stations.append(station)
                    print(f"\n✓ FOUND: {station_id}")
                    print(f"   Name: {station.get('name')}")
                    print(f"   Lat/Lon: {station.get('latitude')}, {station.get('longitude')}")
                    print(f"   Elevation: {station.get('elevation')} m")
                    print(f"   Min Date: {station.get('mindate')}")
                    print(f"   Max Date: {station.get('maxdate')}")
                    
            if not relevant_stations:
                print("\nNo obvious Crescent City stations found. Showing all stations:")
                for station in data["results"][:10]:  # Show first 10
                    print(f"  {station.get('id')}: {station.get('name')}")
                    
        else:
            print("No stations found")
            
    except Exception as e:
        print(f"Error searching stations: {e}")

def try_direct_kcec_variations():
    """Try different possible KCEC station ID formats"""
    
    print("\n" + "=" * 60)
    print("TESTING DIRECT KCEC STATION ID VARIATIONS")
    print("=" * 60)
    
    # Common NOAA station ID patterns for airports
    possible_ids = [
        "GHCND:USW00024283",  # Another common format
        "GHCND:US1CADN0001",  # US Climate Reference Network format
        "GHCND:USC00041790",  # Cooperative Observer format
        "GHCND:USS0021B02S",  # SNOTEL format
        "KCEC",  # Direct airport code
        "GHCND:KCEC"  # Airport code with prefix
    ]
    
    headers = {"token": NOAA_TOKEN}
    
    for station_id in possible_ids:
        try:
            url = f"https://www.ncdc.noaa.gov/cdo-web/api/v2/stations/{station_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                station_data = response.json()
                print(f"✓ FOUND: {station_id}")
                print(f"   Name: {station_data.get('name')}")
                print(f"   Location: {station_data.get('latitude')}, {station_data.get('longitude')}")
                
                # Test if it has recent precipitation data
                test_data_url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
                test_params = {
                    "datasetid": "GHCND",
                    "stationid": station_id,
                    "datatypeid": "PRCP",
                    "startdate": "2024-01-01",
                    "enddate": "2024-01-31",
                    "limit": 10
                }
                
                test_response = requests.get(test_data_url, params=test_params, headers=headers)
                if test_response.status_code == 200:
                    test_data = test_response.json()
                    if "results" in test_data and test_data["results"]:
                        print(f"   ✓ Has precipitation data! Sample: {test_data['results'][0]['value']}")
                    else:
                        print(f"   ✗ No precipitation data found")
                        
            else:
                print(f"✗ {station_id}: Not found (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"✗ {station_id}: Error - {e}")

def search_by_coordinates():
    """Search for stations near Crescent City coordinates"""
    
    print("\n" + "=" * 60)
    print("SEARCHING BY COORDINATES")
    print("=" * 60)
    
    # Crescent City coordinates: 41.7558° N, 124.2026° W
    # Search within ~25km radius
    
    headers = {"token": NOAA_TOKEN}
    
    try:
        url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/stations"
        params = {
            "datasetid": "GHCND",
            "extent": "41.6,-124.4,41.9,-123.9",  # Bounding box around Crescent City
            "limit": 50
        }
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if "results" in data:
            print(f"Found {len(data['results'])} stations near Crescent City")
            
            for station in data["results"]:
                name = station.get("name", "")
                station_id = station.get("id", "")
                lat = station.get("latitude", 0)
                lon = station.get("longitude", 0)
                
                # Calculate approximate distance from Crescent City center
                import math
                cc_lat, cc_lon = 41.7558, -124.2026
                distance = math.sqrt((lat - cc_lat)**2 + (lon - cc_lon)**2) * 111  # Rough km conversion
                
                print(f"{station_id}: {name}")
                print(f"   Location: {lat}, {lon} (~{distance:.1f}km from CC)")
                print(f"   Dates: {station.get('mindate')} to {station.get('maxdate')}")
                print()
                
        else:
            print("No stations found in area")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_stations()
    try_direct_kcec_variations()
    search_by_coordinates()