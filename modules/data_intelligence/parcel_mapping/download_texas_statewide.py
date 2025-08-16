#!/usr/bin/env python3

"""
Texas Statewide Parcel Data Downloader - Simple Approach
Downloads available Texas parcel data from TxGIO and other sources
Output: /data_sets/Texas/Parcels/texas_parcels.geojson
"""

import os
import requests
import json
from datetime import datetime

def create_output_directory():
    """Create the Texas parcels directory if it doesn't exist"""
    output_dir = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/Texas/Parcels"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def download_from_manual_search():
    """Manual approach - let's just create the structure and guide manual download"""
    print("🏢 TEXAS PARCEL DATA MANUAL DOWNLOAD GUIDE")
    print("=" * 60)
    
    output_dir = create_output_directory()
    
    print("📋 MANUAL DOWNLOAD INSTRUCTIONS:")
    print("")
    print("1. DALLAS-FORT WORTH:")
    print("   📍 Go to: https://data-nctcoggis.hub.arcgis.com/")
    print("   🔍 Search for 'parcels' or 'property'")
    print("   💾 Download as GeoJSON or Shapefile")
    print("   📁 Save as: dfw_parcels.geojson")
    print("")
    
    print("2. SAN ANTONIO (BEXAR COUNTY):")
    print("   📍 Go to: https://gis-bcad.opendata.arcgis.com/")
    print("   🔍 Search for 'parcels' or 'BCAD'")
    print("   💾 Download as GeoJSON")
    print("   📁 Save as: san_antonio_parcels.geojson")
    print("")
    
    print("3. AUSTIN (TRAVIS COUNTY):")
    print("   📍 Go to: https://data.austintexas.gov/")
    print("   🔍 Search for 'Property' or 'Parcels'")
    print("   💾 Download as GeoJSON")
    print("   📁 Save as: austin_parcels.geojson")
    print("")
    
    print("4. HOUSTON (HARRIS COUNTY):")
    print("   📍 Go to: https://hcad.org/")
    print("   🔍 Look for GIS or Data Downloads")
    print("   💾 Download parcel data")
    print("   📁 Save as: houston_parcels.geojson")
    print("")
    
    print("5. TEXAS STATEWIDE:")
    print("   📍 Go to: https://data.tnris.org/")
    print("   🔍 Search for 'cadastral' or 'parcels'")
    print("   💾 Download available county data")
    print("   📁 Save individual county files")
    print("")
    
    print(f"💾 SAVE ALL FILES TO: {output_dir}")
    print("")
    print("🎯 GOAL: Get at least one major metro area working")
    print("   Priority: Dallas, San Antonio, Austin, or Houston")
    print("   Any one success = can test bulk processing!")
    print("")
    
    # Create a simple test file to verify the directory works
    test_file = os.path.join(output_dir, "README_MANUAL_DOWNLOAD.txt")
    with open(test_file, 'w') as f:
        f.write("TEXAS PARCEL DATA MANUAL DOWNLOAD\n")
        f.write("=" * 40 + "\n\n")
        f.write("Download parcel data files and save them here:\n\n")
        f.write("PRIORITY FILES NEEDED:\n")
        f.write("- dfw_parcels.geojson (Dallas-Fort Worth)\n")
        f.write("- san_antonio_parcels.geojson (Bexar County)\n")
        f.write("- austin_parcels.geojson (Travis County)\n")
        f.write("- houston_parcels.geojson (Harris County)\n\n")
        f.write("FILE FORMAT: GeoJSON preferred\n")
        f.write("SCHEMA: Should include parcel boundaries as polygons\n")
        f.write("COORDINATE SYSTEM: WGS84 (EPSG:4326) preferred\n\n")
        f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"📋 Created instructions file: {test_file}")
    print("")
    print("🚀 ALTERNATIVE: Try individual county downloaders")
    print("   Some county APIs may still work even if NCTCOG is down")

def try_simple_api_calls():
    """Try some simple, more reliable API endpoints"""
    print("\n🔄 TRYING SIMPLE API APPROACHES")
    print("-" * 40)
    
    output_dir = create_output_directory()
    
    # Try some basic endpoints that are more likely to work
    simple_sources = [
        {
            "name": "Austin Open Data",
            "url": "https://data.austintexas.gov/resource/8u4p-d5da.geojson?$limit=1000",
            "output": "austin_sample_parcels.geojson"
        }
    ]
    
    for source in simple_sources:
        try:
            print(f"📡 Trying: {source['name']}")
            
            headers = {'User-Agent': 'Colosseum-LIHTC-Analyzer/1.0'}
            response = requests.get(source['url'], headers=headers, timeout=60)
            
            if response.status_code == 200:
                print(f"✅ Got {len(response.content)} bytes")
                
                # Try to parse as JSON
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        # Convert array of features to GeoJSON FeatureCollection
                        geojson_data = {
                            "type": "FeatureCollection",
                            "features": data
                        }
                    else:
                        geojson_data = data
                    
                    output_file = os.path.join(output_dir, source['output'])
                    with open(output_file, 'w') as f:
                        json.dump(geojson_data, f, indent=2)
                    
                    print(f"💾 Saved to: {output_file}")
                    
                    if 'features' in geojson_data:
                        print(f"📊 Features: {len(geojson_data['features'])}")
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ JSON parsing failed: {e}")
                    
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 TEXAS PARCEL DATA ACQUISITION - SIMPLIFIED APPROACH")
    print("🚛 When APIs fail, we adapt!")
    print("")
    
    # Try simple API calls first
    api_success = try_simple_api_calls()
    
    # Always show manual instructions
    download_from_manual_search()
    
    if api_success:
        print("🎉 AT LEAST ONE API WORKED!")
        print("Check the output files and proceed with integration testing")
    else:
        print("📋 NO APIs WORKING - MANUAL DOWNLOAD REQUIRED")
        print("Follow the instructions above to get data files")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Get at least ONE metro area working (any will do)")
    print("2. Test with your existing D'Marco environmental mapper")
    print("3. Validate bulk processing speed improvement")
    print("4. Troubleshoot other regions once one is working")
    
    print("\n💡 REMEMBER: We just need ONE working region to prove the concept!")
    print("   Even 1 county is better than API calls for bulk processing")