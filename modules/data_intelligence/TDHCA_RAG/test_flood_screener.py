#!/usr/bin/env python3
"""
Test FEMA flood screener on first 5 sites
"""

import pandas as pd
import requests
import time
from pathlib import Path

def test_flood_api():
    """Test FEMA API on known Texas coordinates"""
    
    # Test coordinates in Texas  
    test_sites = [
        {"lat": 32.7767, "lng": -96.7970, "name": "Dallas, TX"},
        {"lat": 29.7604, "lng": -95.3698, "name": "Houston, TX"},
        {"lat": 30.2672, "lng": -97.7431, "name": "Austin, TX"},
    ]
    
    for site in test_sites:
        lat, lng, name = site["lat"], site["lng"], site["name"]
        print(f"\n🏠 Testing: {name} ({lat}, {lng})")
        
        try:
            base_url = "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer"
            identify_url = f"{base_url}/identify"
            
            params = {
                'geometry': f'{lng},{lat}',
                'geometryType': 'esriGeometryPoint',
                'sr': '4326',
                'layers': 'all:28',
                'tolerance': '0',
                'mapExtent': f'{lng-0.01},{lat-0.01},{lng+0.01},{lat+0.01}',
                'imageDisplay': '400,400,96',
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            response = requests.get(identify_url, params=params, timeout=15)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response keys: {list(data.keys())}")
                
                if 'results' in data:
                    print(f"   Results count: {len(data['results'])}")
                    if data['results']:
                        result = data['results'][0]
                        attrs = result.get('attributes', {})
                        zone = attrs.get('FLD_ZONE', attrs.get('ZONE', 'Not found'))
                        print(f"   ✅ Flood Zone: {zone}")
                    else:
                        print(f"   ⚠️ No results - likely Zone X (low risk)")
                else:
                    print(f"   ❌ No results key in response")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)

def check_master_file():
    """Check first few rows of MASTER file"""
    master_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/Analysis_Results/MASTER_155_BoostEligible_Sites_20250731_223500.xlsx")
    
    df = pd.read_excel(master_file)
    print(f"MASTER file: {len(df)} sites loaded")
    print("\nFirst 3 sites coordinates:")
    
    for idx in range(min(3, len(df))):
        row = df.iloc[idx]
        lat = row['Latitude']
        lng = row['Longitude'] 
        address = row['Address']
        print(f"Site {idx}: {address[:30]}... ({lat}, {lng})")

if __name__ == "__main__":
    print("🧪 TESTING FEMA FLOOD API")
    print("=" * 50)
    
    print("\n1. Testing FEMA API on known coordinates:")
    test_flood_api()
    
    print("\n\n2. Checking MASTER file coordinates:")
    check_master_file()