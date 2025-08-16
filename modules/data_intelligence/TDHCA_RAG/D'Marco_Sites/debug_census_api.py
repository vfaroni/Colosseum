#!/usr/bin/env python3
"""
Debug Census API Issues
Check what's happening with tract identification
"""

import requests
import json

def test_census_tract_api():
    """Test Census tract API directly"""
    
    print("🧪 DEBUGGING CENSUS TRACT API")
    print("="*50)
    
    # Houston Third Ward coordinates
    lat, lng = 29.7372, -95.3647
    
    # Test the tract identification API (this should work)
    print(f"🎯 Testing tract API for: {lat}, {lng}")
    
    url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
    params = {
        "x": lng,
        "y": lat,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"📊 Tract API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Tract API Response:")
            
            if data.get('result') and data['result'].get('geographies'):
                geogs = data['result']['geographies']
                print(f"   Available geographies: {list(geogs.keys())}")
                
                if 'Census Tracts' in geogs and geogs['Census Tracts']:
                    tract_info = geogs['Census Tracts'][0]
                    print(f"   ✅ Tract found: {tract_info.get('NAME')}")
                    print(f"   State: {tract_info.get('STATE')} ({tract_info.get('BASENAME')})")
                    print(f"   County: {tract_info.get('COUNTY')}")
                    print(f"   Tract: {tract_info.get('TRACT')}")
                    print(f"   GEOID: {tract_info.get('GEOID')}")
                else:
                    print("   ❌ No tract data found")
            else:
                print("   ❌ No geography data in response")
        else:
            print(f"❌ Tract API failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Tract API exception: {e}")
    
    print("\n" + "="*50)
    
    # Test the ZIP code API (this is failing)
    print(f"🎯 Testing ZIP API for: {lat}, {lng}")
    
    url2 = "https://geocoding.geo.census.gov/geocoder/locations/coordinates"
    params2 = {
        "x": lng,
        "y": lat,
        "benchmark": "Public_AR_Current",
        "format": "json"
    }
    
    try:
        response2 = requests.get(url2, params=params2)
        print(f"📊 ZIP API Status: {response2.status_code}")
        
        if response2.status_code == 200:
            data2 = response2.json()
            print("✅ ZIP API Response:")
            print(json.dumps(data2, indent=2)[:500])
        else:
            print(f"❌ ZIP API failed: {response2.status_code}")
            print(f"Response: {response2.text[:200]}")
            
    except Exception as e:
        print(f"❌ ZIP API exception: {e}")

if __name__ == "__main__":
    test_census_tract_api()