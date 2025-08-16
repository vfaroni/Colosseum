#!/usr/bin/env python3
"""
Extract county name from coordinates for Census Bureau links
Demonstrates how to programmatically get county name from coordinates
"""

import requests

def get_county_from_coordinates(lat, lon):
    """Get county information from coordinates using Census Geocoder API"""
    try:
        url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
        params = {
            'x': lon,
            'y': lat,
            'benchmark': 'Public_AR_Current',
            'vintage': 'Current_Current',
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'result' in data and 'geographies' in data['result']:
            # Extract county information
            county_info = data['result']['geographies']['Counties'][0]
            county_name = county_info.get('NAME', '')
            county_fips = county_info.get('COUNTY', '')
            state_fips = county_info.get('STATE', '')
            
            # Create Census Bureau county profile URL
            # Format: https://data.census.gov/profile/{CountyName}?g=050XX00US{StateFIPS}{CountyFIPS}
            census_url = f"https://data.census.gov/profile/{county_name}?g=050XX00US{state_fips}{county_fips}"
            
            return {
                'county_name': county_name,
                'county_fips': county_fips,
                'state_fips': state_fips,
                'census_profile_url': census_url,
                'full_fips': f"{state_fips}{county_fips}"
            }
        else:
            return None
            
    except Exception as e:
        print(f"Error getting county information: {e}")
        return None

def demonstrate_fir_tree():
    """Demonstrate with Fir Tree Park coordinates"""
    print("🏛️ COUNTY EXTRACTION DEMO - Fir Tree Park")
    print("=" * 50)
    
    # Fir Tree coordinates
    lat, lon = 47.2172038, -123.1027976
    
    print(f"📍 Coordinates: {lat}, {lon}")
    print(f"🏠 Address: 614 North 4th Street, Shelton, WA 98584")
    print()
    
    county_info = get_county_from_coordinates(lat, lon)
    
    if county_info:
        print(f"✅ County Found: {county_info['county_name']}")
        print(f"📊 County FIPS: {county_info['county_fips']}")
        print(f"📍 State FIPS: {county_info['state_fips']}")
        print(f"🔗 Full FIPS: {county_info['full_fips']}")
        print()
        print(f"🌐 Census Profile URL:")
        print(f"   {county_info['census_profile_url']}")
        print()
        
        # Show how this would be used in HTML
        print("💻 HTML Implementation:")
        print(f'<a href="{county_info["census_profile_url"]}" target="_blank">')
        print(f'   📊 {county_info["county_name"]} County Profile')
        print('</a>')
        
    else:
        print("❌ Could not extract county information")

if __name__ == "__main__":
    demonstrate_fir_tree()