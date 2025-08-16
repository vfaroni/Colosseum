#!/usr/bin/env python3
"""
Texas QCT/DDA Checker - Full Processing Version (Clean)
Processes all properties in the Excel file
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import requests
import json
from pathlib import Path
import time

# CONFIGURATION
POSITIONSTACK_API_KEY = "41b80ed51d92978904592126d2bb8f7e"  # Your API key
INPUT_FILE = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Costar/TX/CS_Land_TX-1-10ac_05312025.xlsx"
OUTPUT_DIR = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code"

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
    """Geocode using Positionstack API"""
    
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
            
            # Debug: Print status
            print(f"    Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"    Error Response: {response.text}")
                continue
                
            data = response.json()
            
            # Check if we have results
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
    print("TEXAS QCT/DDA CHECKER - FULL PROCESSING")
    print("="*60)
    
    # Load data
    qct_data, dda_data = load_hud_data()
    
    # Read Excel file
    print(f"\nReading: {Path(INPUT_FILE).name}")
    df = pd.read_excel(INPUT_FILE)
    total_properties = len(df)
    print(f"Total properties: {total_properties}")
    print(f"Processing ALL properties...\n")
    
    # Add result columns
    df['Geocoded'] = False
    df['Latitude'] = None
    df['Longitude'] = None
    df['QCT'] = False
    df['DDA'] = False
    df['Federal_Boost'] = False
    df['Error'] = None
    
    # Initialize counters and timing
    success_count = 0
    qct_count = 0
    dda_count = 0
    start_time = time.time()
    property_times = []
    
    # Process each property
    for idx, row in df.iterrows():
        property_start = time.time()
        current_num = idx + 1
        
        print(f"\n{'='*50}")
        print(f"Property {current_num}/{total_properties}")
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
            
            df.at[idx, 'Geocoded'] = True
            df.at[idx, 'Latitude'] = lat
            df.at[idx, 'Longitude'] = lon
            
            # Check QCT/DDA
            qct_dda = check_qct_dda(lat, lon, qct_data, dda_data)
            
            df.at[idx, 'QCT'] = qct_dda['qct']
            df.at[idx, 'DDA'] = qct_dda['dda']
            df.at[idx, 'Federal_Boost'] = qct_dda['federal_boost']
            
            if qct_dda['qct']:
                qct_count += 1
                print("  🎯 QCT: YES")
            if qct_dda['dda']:
                dda_count += 1
                print("  🎯 DDA: YES")
            if qct_dda['federal_boost']:
                print("  ✅ FEDERAL BASIS BOOST: YES")
                
        else:
            df.at[idx, 'Error'] = geo_result.get('error', 'Unknown error')
            print(f"  ❌ GEOCODING FAILED")
        
        # Calculate time for this property
        property_duration = time.time() - property_start
        property_times.append(property_duration)
        print(f"  ⏱️  Time for this property: {property_duration:.1f} seconds")
        
        # Progress tracking every 10 properties
        if current_num % 10 == 0:
            avg_time = sum(property_times) / len(property_times)
            total_elapsed = time.time() - start_time
            remaining = total_properties - current_num
            eta_seconds = remaining * avg_time
            
            print(f"\n  📊 TIMING STATS:")
            print(f"     Average per property: {avg_time:.1f} seconds")
            print(f"     Total elapsed: {total_elapsed/60:.1f} minutes")
            print(f"     Estimated remaining: {eta_seconds/60:.1f} minutes")
            print(f"     Progress: {current_num}/{total_properties} ({current_num/total_properties*100:.1f}%)")
        
        # Save progress every 50 properties
        if current_num % 50 == 0:
            progress_file = f"{OUTPUT_DIR}/texas_qct_progress_{current_num}.xlsx"
            df.to_excel(progress_file, index=False)
            print(f"  📁 Progress saved: {progress_file}")
    
    # Save final results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"{OUTPUT_DIR}/texas_qct_full_{timestamp}.xlsx"
    df.to_excel(output_file, index=False)
    
    # Create filtered file with only QCT/DDA properties
    federal_properties = df[df['Federal_Boost'] == True].copy()
    if len(federal_properties) > 0:
        # Sort by best opportunities
        federal_properties = federal_properties.sort_values(
            by=['QCT', 'DDA', 'Land Area (AC)', 'Price Per AC Land'],
            ascending=[False, False, False, True]
        )
        
        filtered_file = f"{OUTPUT_DIR}/texas_qct_FEDERAL_ONLY_{timestamp}.xlsx"
        federal_properties.to_excel(filtered_file, index=False)
    
    # Calculate total time
    total_time = time.time() - start_time
    avg_time_per_property = total_time / total_properties
    
    # Summary
    print(f"\n{'='*60}")
    print("PROCESSING COMPLETE!")
    print(f"{'='*60}")
    print(f"Properties processed: {total_properties}")
    print(f"Successfully geocoded: {success_count} ({success_count/total_properties*100:.1f}%)")
    print(f"Properties in QCT: {qct_count} ({qct_count/total_properties*100:.1f}%)")
    print(f"Properties in DDA: {dda_count} ({dda_count/total_properties*100:.1f}%)")
    print(f"Properties with Federal Boost: {len(federal_properties)} ({len(federal_properties)/total_properties*100:.1f}%)")
    
    print(f"\n⏱️  TIMING SUMMARY:")
    print(f"   Total processing time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print(f"   Average time per property: {avg_time_per_property:.1f} seconds")
    if property_times:
        print(f"   Fastest property: {min(property_times):.1f} seconds")
        print(f"   Slowest property: {max(property_times):.1f} seconds")
        print(f"   Properties per minute: {60/avg_time_per_property:.1f}")
    
    print(f"\nOutput files:")
    print(f"  - Full results: {output_file}")
    if len(federal_properties) > 0:
        print(f"  - Federal boost only: {filtered_file}")
        
        # Show top opportunities
        print(f"\n🏆 TOP 10 QCT/DDA OPPORTUNITIES:")
        for i, (_, prop) in enumerate(federal_properties.head(10).iterrows(), 1):
            print(f"\n  {i}. {prop['Address']}, {prop['City']}")
            print(f"     Land: {prop['Land Area (AC)']:.2f} acres | Price/AC: ${prop['Price Per AC Land']:,.0f}")
            status = []
            if prop['QCT']:
                status.append("QCT")
            if prop['DDA']:
                status.append("DDA")
            print(f"     Status: {' + '.join(status)}")
    else:
        print("\n  No properties found with Federal Basis Boost eligibility.")


if __name__ == "__main__":
    main()
