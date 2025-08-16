#!/usr/bin/env python3
"""
Test different ZIP API endpoints and formats
"""

import requests
import json

def test_zip_api_variations():
    """Test different ZIP API formats"""
    
    lat, lng = 29.7372, -95.3647
    print(f"🧪 TESTING ZIP API VARIATIONS for {lat}, {lng}")
    print("="*60)
    
    # Try different endpoint variations
    endpoints = [
        {
            "name": "Current (failing)",
            "url": "https://geocoding.geo.census.gov/geocoder/locations/coordinates",
            "params": {"x": lng, "y": lat, "benchmark": "Public_AR_Current", "format": "json"}
        },
        {
            "name": "Different benchmark",
            "url": "https://geocoding.geo.census.gov/geocoder/locations/coordinates", 
            "params": {"x": lng, "y": lat, "benchmark": "4", "format": "json"}
        },
        {
            "name": "Alternative endpoint",
            "url": "https://geocoding.geo.census.gov/geocoder/geographies/coordinates",
            "params": {"x": lng, "y": lat, "benchmark": "Public_AR_Current", "vintage": "Current_Current", "format": "json", "layers": "all"}
        },
        {
            "name": "Reverse geocode",
            "url": "https://geocoding.geo.census.gov/geocoder/address/coordinates",
            "params": {"x": lng, "y": lat, "format": "json"}
        }
    ]
    
    for i, endpoint in enumerate(endpoints, 1):
        print(f"\n🎯 TEST {i}: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")
        print(f"Params: {endpoint['params']}")
        
        try:
            response = requests.get(endpoint['url'], params=endpoint['params'])
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS!")
                
                # Look for ZIP code in various places
                if 'result' in data:
                    result = data['result']
                    
                    # Check addressMatches
                    if 'addressMatches' in result and result['addressMatches']:
                        address = result['addressMatches'][0].get('matchedAddress', '')
                        print(f"   Address: {address}")
                        
                        # Extract ZIP from address
                        import re
                        zip_match = re.search(r', (\d{5})', address)
                        if zip_match:
                            print(f"   ✅ ZIP found: {zip_match.group(1)}")
                    
                    # Check geographies for ZIP codes
                    if 'geographies' in result:
                        geogs = result['geographies']
                        for geo_type, geo_list in geogs.items():
                            if 'zip' in geo_type.lower() or 'postal' in geo_type.lower():
                                print(f"   ✅ ZIP geography: {geo_type}")
                                if geo_list:
                                    print(f"   ZIP data: {geo_list[0]}")
                
                # Show first 300 chars of response
                print(f"Response preview: {json.dumps(data, indent=2)[:300]}...")
                
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    test_zip_api_variations()