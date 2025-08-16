#!/usr/bin/env python3
"""
Simplified Texas QCT/DDA Checker - All in one file
Tests with first 20 properties only
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import requests
import json
from pathlib import Path
import time

# CONFIGURATION - Edit these values
POSITIONSTACK_API_KEY = "41b80ed51d92978904592126d2bb8f7e"  # Correct key without sk_ prefix
INPUT_FILE = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Costar/TX/CS_Land_TX-1-10ac_05312025.xlsx"
OUTPUT_DIR = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code"
TEST_LIMIT = None  # Process ALL properties (set to a number to limit)

# HUD Data paths
HUD_PATH = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD DDA QCT"
QCT_FILE = f"{HUD_PATH}/QUALIFIED_CENSUS_TRACTS_7341711606021821459.gpkg"
DDA_FILE = f"{HUD_PATH}/Difficult_Development_Areas_-4200740390724245794.gpkg"


def load_hud_data():
    """Load QCT and DDA shapefiles"""
    print("Loading HUD QCT/DDA data...")
    
    qct_data = None
    dda_data = None
    
    try:
        if Path(QCT_FILE).exists():
            qct_data = gpd.read_file(QCT_FILE)
            if qct_data.crs != 'EPSG:4326':
                qct_data = qct_data.to_crs('EPSG:4326')
            print(f"✅ Loaded {len(qct_data)} QCT features")
        else:
            print(f"❌ QCT file not found")
            
        if Path(DDA_FILE).exists():
            dda_data = gpd.read_file(DDA_FILE)
            if dda_data.crs != 'EPSG:4326':
                dda_data = dda_data.to_crs('EPSG:4326')
            print(f"✅ Loaded {len(dda_data)} DDA features")
        else:
            print(f"❌ DDA file not found")
            
    except Exception as e:
        print(f"❌ Error loading HUD data: {e}")
    
    return qct_data, dda_data


def geocode_address(address, city, state, zip_code):
    """Geocode using Positionstack API with detailed debugging"""
    
    # Try different address formats
    addresses_to_try = [
        f"{address}, {city}, {state} {zip_code}",  # Full address
        f"{address}, {city}, TX",                  # Without ZIP
        f"{address}, {city}, Texas",               # State name
        f"{city}, TX {zip_code}",                  # Just city and ZIP
    ]
    
    for i, query_address in enumerate(addresses_to_try):
        print(f"  Attempt {i+1}: {query_address}")
        
        try:
            url = "http://api.positionstack.com/v1/forward"
            params = {
                'access_key': POSITIONSTACK_API_KEY,
                'query': query_address,
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            # Debug: Print status and response
            print(f"    Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"    Error Response: {response.text}")
                continue
                
            data = response.json()
            
            # Debug: Check if we have results
            if 'error' in data:
                print(f"    API Error: {data['error']}")
                continue
                
            if data.get('data') and len(data['data']) > 0:
                location = data['data'][0]
                print(f"    ✅ Found: {location.get('label', 'No label')}")
                print(f"    Coordinates: {location['latitude']}, {location['longitude']}")
                
                return {
                    "success": True,
                    "latitude": location['latitude'],
                    "longitude": location['longitude'],
                    "confidence": location.get('confidence', 0),
                    "matched_address": location.get('label', query_address)
                }
            else:
                print(f"    No results returned")
                
        except Exception as e:
            print(f"    Exception: {type(e).__name__}: {e}")
        
        # Small delay between attempts
        time.sleep(0.5)
    
    return {"success": False, "error": "All geocoding attempts failed"}


def check_qct_dda(lat, lon, qct_data, dda_data):
    """Check if coordinates are in QCT or DDA"""
    result = {
        "qct": False,
        "dda": False,
        "federal_boost": False
    }
    
    try:
        point = Point(lon, lat)
        
        if qct_data is not None:
            qct_matches = qct_data[qct_data.contains(point)]
            if not qct_matches.empty:
                result["qct"] = True
                result["federal_boost"] = True
                
        if dda_data is not None:
            dda_matches = dda_data[dda_data.contains(point)]
            if not dda_matches.empty:
                result["dda"] = True
                result["federal_boost"] = True
                
    except Exception as e:
        print(f"    Error checking QCT/DDA: {e}")
    
    return result


def main():
    """Main processing function"""
    print("="*60)
    print("TEXAS QCT/DDA CHECKER - SIMPLIFIED VERSION")
    print("="*60)
    
    # Load data
    qct_data, dda_data = load_hud_data()
    
    # Read Excel file
    print(f"\nReading: {Path(INPUT_FILE).name}")
    df = pd.read_excel(INPUT_FILE)
    print(f"Total properties: {len(df)}")
    print(f"Testing first {TEST_LIMIT} properties only\n")
    
    # Take only first 20 for testing
    df_test = df.head(TEST_LIMIT).copy()
    
    # Add result columns
    df_test['Geocoded'] = False
    df_test['Latitude'] = None
    df_test['Longitude'] = None
    df_test['QCT'] = False
    df_test['DDA'] = False
    df_test['Federal_Boost'] = False
    df_test['Error'] = None
    
    # Process each property
    success_count = 0
    qct_count = 0
    dda_count = 0
    
    for idx, row in df_test.iterrows():
        print(f"\n{'='*50}")
        print(f"Property {idx + 1}/{TEST_LIMIT}")
        print(f"Address: {row['Address']}")
        print(f"City: {row['City']}, State: {row['State']}, ZIP: {row['Zip']}")
        
        # Geocode
        geo_result = geocode_address(
            str(row['Address']), 
            str(row['City']), 
            str(row['State']), 
            str(row['Zip'])
        )
        
        if geo_result['success']:
            success_count += 1
            lat = geo_result['latitude']
            lon = geo_result['longitude']
            
            df_test.at[idx, 'Geocoded'] = True
            df_test.at[idx, 'Latitude'] = lat
            df_test.at[idx, 'Longitude'] = lon
            
            # Check QCT/DDA
            qct_dda = check_qct_dda(lat, lon, qct_data, dda_data)
            
            df_test.at[idx, 'QCT'] = qct_dda['qct']
            df_test.at[idx, 'DDA'] = qct_dda['dda']
            df_test.at[idx, 'Federal_Boost'] = qct_dda['federal_boost']
            
            if qct_dda['qct']:
                qct_count += 1
                print("  🎯 QCT: YES")
            if qct_dda['dda']:
                dda_count += 1
                print("  🎯 DDA: YES")
            if qct_dda['federal_boost']:
                print("  ✅ FEDERAL BASIS BOOST: YES")
                
        else:
            df_test.at[idx, 'Error'] = geo_result.get('error', 'Unknown error')
            print(f"  ❌ GEOCODING FAILED")
    
    # Save results
    output_file = f"{OUTPUT_DIR}/texas_qct_test_{TEST_LIMIT}.xlsx"
    df_test.to_excel(output_file, index=False)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY:")
    print(f"Properties tested: {TEST_LIMIT}")
    print(f"Successfully geocoded: {success_count} ({success_count/properties_to_process*100:.1f}%)")
    print(f"Properties in QCT: {qct_count}")
    print(f"Properties in DDA: {dda_count}")
    print(f"Properties with Federal Boost: {len(df_test[df_test['Federal_Boost'] == True])}")
    print(f"\nOutput saved to: {output_file}")
    
    # Show any with federal boost
    federal_properties = df_test[df_test['Federal_Boost'] == True]
    if len(federal_properties) > 0:
        print(f"\n🏆 PROPERTIES WITH FEDERAL BASIS BOOST:")
        for _, prop in federal_properties.iterrows():
            print(f"  • {prop['Address']}, {prop['City']}")
            if prop['QCT'] and prop['DDA']:
                print(f"    Status: QCT + DDA")
            elif prop['QCT']:
                print(f"    Status: QCT")
            else:
                print(f"    Status: DDA")


if __name__ == "__main__":
    main()
