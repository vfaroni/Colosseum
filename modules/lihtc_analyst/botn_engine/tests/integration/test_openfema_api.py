#!/usr/bin/env python3
"""
Test OpenFEMA API for flood zone lookups
"""

import requests
import json

def test_openfema_flood_data():
    """Test OpenFEMA API for flood-related data"""
    
    lat = 33.5515298
    lng = -117.2078974
    
    print(f"🏛️ TESTING OPENFEMA API FOR FLOOD DATA")
    print(f"Coordinates: {lat}, {lng}")
    print("=" * 50)
    
    base_url = "https://www.fema.gov/api/open"
    
    # Test different flood-related endpoints
    endpoints_to_test = [
        "/v2/FimaNfipClaims",
        "/v2/FimaNfipPolicies", 
        "/v1/NfipCommunityStatusBook",
        "/v1/FemaRegions"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            # Test basic endpoint first
            response = requests.get(f"{base_url}{endpoint}?$top=1", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Endpoint works - got {len(data.get('FemaWebDisasterSummaries', data.get('FimaNfipClaims', data.get('FimaNfipPolicies', data.get('NfipCommunityStatusBook', data.get('FemaRegions', []))))))} records")
                
                # Check if it has geospatial fields
                if data and len(data) > 0:
                    first_record = list(data.values())[0]
                    if isinstance(first_record, list) and len(first_record) > 0:
                        sample_record = first_record[0]
                        geo_fields = [k for k in sample_record.keys() if 'geo' in k.lower() or 'lat' in k.lower() or 'lon' in k.lower() or 'coord' in k.lower()]
                        print(f"   📍 Potential geo fields: {geo_fields}")
                
            else:
                print(f"   ❌ Error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test geospatial query on FemaRegions (known to work)
    print(f"\n🌍 Testing geospatial query on FemaRegions:")
    try:
        # Point query using our coordinates
        geo_query = f"geo.intersects(regionGeometry,geography'POINT({lng} {lat})')"
        encoded_query = requests.utils.quote(geo_query)
        
        url = f"{base_url}/v1/FemaRegions?$filter={encoded_query}"
        print(f"   Query URL: {url}")
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Geospatial query works!")
            print(f"   📊 Found {len(data.get('FemaRegions', []))} regions")
            
            if data.get('FemaRegions'):
                region = data['FemaRegions'][0]
                print(f"   🏛️ FEMA Region: {region.get('regionNumber', 'Unknown')}")
                print(f"   📍 Region Name: {region.get('regionName', 'Unknown')}")
        else:
            print(f"   ❌ Geospatial query failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Geospatial query exception: {e}")
    
    # Try to find flood zone specific data
    print(f"\n🌊 Looking for flood zone data:")
    try:
        # Check if there are any flood zone related endpoints
        # This is exploratory - we don't know the exact endpoint names
        possible_flood_endpoints = [
            "/v1/FloodZones",
            "/v1/NfhlData", 
            "/v1/FloodHazard",
            "/v2/FloodMaps"
        ]
        
        for endpoint in possible_flood_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}?$top=1", timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ Found working endpoint: {endpoint}")
                elif response.status_code == 404:
                    print(f"   ❌ Not found: {endpoint}")
                else:
                    print(f"   ⚠️  {endpoint}: Status {response.status_code}")
            except:
                print(f"   ❌ Failed: {endpoint}")
                
    except Exception as e:
        print(f"   Exception in flood zone search: {e}")

if __name__ == "__main__":
    test_openfema_flood_data()