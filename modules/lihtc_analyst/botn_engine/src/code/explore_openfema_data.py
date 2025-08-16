#!/usr/bin/env python3
"""
Explore what data is actually in OpenFEMA endpoints
"""

import requests
import json

def explore_openfema_data():
    """Explore the structure of OpenFEMA flood data"""
    
    print("🔍 EXPLORING OPENFEMA FLOOD DATA STRUCTURE")
    print("=" * 50)
    
    base_url = "https://www.fema.gov/api/open"
    
    # Working endpoints from previous test
    working_endpoints = [
        "/v2/FimaNfipClaims",
        "/v2/FimaNfipPolicies", 
        "/v1/NfipCommunityStatusBook"
    ]
    
    for endpoint in working_endpoints:
        print(f"\n📊 Exploring: {endpoint}")
        
        try:
            # Get a sample record to see structure
            response = requests.get(f"{base_url}{endpoint}?$top=1", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Get the first record
                data_key = list(data.keys())[0]
                records = data[data_key]
                
                if records and len(records) > 0:
                    sample_record = records[0]
                    
                    print(f"   📋 Sample record fields:")
                    for key, value in sample_record.items():
                        # Truncate long values
                        display_value = str(value)[:50]
                        if len(str(value)) > 50:
                            display_value += "..."
                        print(f"      {key}: {display_value}")
                    
                    # Look for geographic fields
                    geo_fields = [k for k in sample_record.keys() if any(geo_term in k.lower() for geo_term in ['geo', 'lat', 'lon', 'coord', 'state', 'county', 'zip', 'city', 'address'])]
                    if geo_fields:
                        print(f"   📍 Geographic fields found: {geo_fields}")
                    else:
                        print(f"   ❌ No obvious geographic fields")
                        
                else:
                    print(f"   ❌ No records found")
                    
        except Exception as e:
            print(f"   ❌ Error exploring {endpoint}: {e}")
    
    # Try to find any coordinate-based queries
    print(f"\n🌍 Testing coordinate-based queries on NFIP data:")
    
    lat = 33.5515298
    lng = -117.2078974
    
    # Try different location-based filters
    location_queries = [
        f"state eq 'CA'",
        f"countyCode eq '065'",  # Riverside County FIPS code
        f"zipcode eq '92570'"     # Approximate zip for that area
    ]
    
    for query in location_queries:
        print(f"\n   🔍 Testing query: {query}")
        try:
            encoded_query = requests.utils.quote(query)
            url = f"{base_url}/v2/FimaNfipClaims?$filter={encoded_query}&$top=1"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                claims = data.get('FimaNfipClaims', [])
                print(f"      ✅ Query works - found {len(claims)} records")
                
                if claims:
                    claim = claims[0]
                    relevant_fields = {k: v for k, v in claim.items() if any(term in k.lower() for term in ['state', 'county', 'zip', 'lat', 'lon', 'geo'])}
                    print(f"      📍 Location data: {relevant_fields}")
            else:
                print(f"      ❌ Query failed: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Query error: {e}")

if __name__ == "__main__":
    explore_openfema_data()