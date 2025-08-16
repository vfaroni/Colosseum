#!/usr/bin/env python3
"""
Get census tract and poverty data for Fir Tree Park
614 North 4th Street, Shelton, WA 98584
"""

import requests
import json

def get_census_data():
    # Fir Tree coordinates
    lat, lon = 47.2172038, -123.1027976
    
    # Get census tract using Census Geocoder
    url = 'https://geocoding.geo.census.gov/geocoder/geographies/coordinates'
    params = {
        'x': lon,
        'y': lat,
        'benchmark': 'Public_AR_Current',
        'vintage': 'Current_Current',
        'format': 'json'
    }
    
    try:
        print("🏛️ FIR TREE PARK - CENSUS DATA ACQUISITION")
        print("=" * 50)
        print(f"📍 Coordinates: {lat}, {lon}")
        print(f"🏠 Address: 614 North 4th Street, Shelton, WA 98584")
        print()
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'result' in data and 'geographies' in data['result']:
            tract_info = data['result']['geographies']['Census Tracts'][0]
            tract_fips = tract_info['GEOID']
            
            print(f"📊 Census Tract FIPS: {tract_fips}")
            print(f"🗺️ Tract Name: {tract_info.get('NAME', 'N/A')}")
            
            # Extract state and county codes
            state_code = tract_fips[:2]
            county_code = tract_fips[2:5] 
            tract_code = tract_fips[5:]
            
            print(f"📍 State Code: {state_code} (Washington)")
            print(f"🏘️ County Code: {county_code} (Mason County)")
            print(f"🗺️ Tract Code: {tract_code}")
            print()
            
            # Now get ACS poverty data
            print("📈 ACQUIRING ACS POVERTY DATA...")
            acs_url = 'https://api.census.gov/data/2022/acs/acs5'
            acs_params = {
                'get': 'B17001_002E,B17001_001E,NAME',
                'for': f'tract:{tract_code}',
                'in': f'state:{state_code} county:{county_code}'
            }
            
            acs_response = requests.get(acs_url, params=acs_params, timeout=10)
            acs_data = acs_response.json()
            
            if len(acs_data) > 1:
                # Handle null/missing data codes
                poverty_count_raw = acs_data[1][0]
                total_pop_raw = acs_data[1][1]
                tract_name = acs_data[1][2]
                
                poverty_count = int(poverty_count_raw) if poverty_count_raw and poverty_count_raw != '-666666666' else 0
                total_pop = int(total_pop_raw) if total_pop_raw and total_pop_raw != '-666666666' else 0
                
                poverty_rate = (poverty_count / total_pop * 100) if total_pop > 0 else 0
                
                print(f"✅ Tract Full Name: {tract_name}")
                print(f"👥 Total Population: {total_pop:,}")
                print(f"📉 Poverty Count: {poverty_count:,}")
                print(f"📊 Poverty Rate: {poverty_rate:.1f}%")
                print()
                
                # Determine LIHTC eligibility context
                if poverty_rate >= 20:
                    print(f"✅ HIGH POVERTY TRACT: {poverty_rate:.1f}% (Good for LIHTC)")
                elif poverty_rate >= 10:
                    print(f"🟡 MODERATE POVERTY: {poverty_rate:.1f}% (Standard LIHTC)")
                else:
                    print(f"⚠️ LOW POVERTY: {poverty_rate:.1f}% (May need QCT/DDA)")
                
                # Return data for further processing
                return {
                    'tract_fips': tract_fips,
                    'tract_name': tract_name,
                    'poverty_rate': poverty_rate,
                    'poverty_count': poverty_count,
                    'total_population': total_pop,
                    'coordinates': {'lat': lat, 'lon': lon}
                }
                
            else:
                print("❌ No ACS poverty data available")
                return None
                
        else:
            print("❌ No census tract found")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    result = get_census_data()
    if result:
        print(f"\n📋 SUMMARY DATA FOR HTML REPORT:")
        print(f"Tract: {result['tract_fips']}")
        print(f"Poverty Rate: {result['poverty_rate']:.1f}%")
        print(f"Population: {result['total_population']:,}")