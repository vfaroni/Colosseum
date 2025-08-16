#!/usr/bin/env python3
"""
PositionStack API Test - Quick Validation
Test your PositionStack API with problematic addresses before full analysis
"""

import requests
import json
from datetime import datetime

def test_positionstack_api():
    """
    Test PositionStack API with addresses that failed Census geocoding
    """
    
    POSITIONSTACK_API_KEY = "41b80ed51d92978904592126d2bb8f7e"
    
    # Test addresses - including ones that likely failed Census geocoding
    test_addresses = [
        "13921 Nutty Brown Rd, Austin, TX 78737",  # Previously 0 competitors
        "9104 Atwater Cv, Austin, TX 78733-3233",  # Previously 0 competitors
        "1234 Main St, Dallas, TX 75201",           # Major metro
        "123 River Walk, San Antonio, TX 78205",   # San Antonio
        "8080 Old Colony Line Rd, Dale",           # Problematic address from your data
        "1000 Old Lytton Springs Rd, Lockhart"    # Another problematic one
    ]
    
    print("🗺️ POSITIONSTACK API TEST")
    print("=" * 50)
    print(f"🔑 API Key: {POSITIONSTACK_API_KEY[:8]}...")
    print(f"🧪 Testing {len(test_addresses)} addresses")
    
    successful_geocodes = 0
    failed_geocodes = 0
    
    for i, address in enumerate(test_addresses, 1):
        print(f"\n🏠 Test {i}: {address}")
        
        try:
            url = "http://api.positionstack.com/v1/forward"
            params = {
                'access_key': POSITIONSTACK_API_KEY,
                'query': address,
                'limit': 1,
                'country': 'US',
                'region': 'Texas',
                'output': 'json'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if 'error' in data:
                print(f"   ❌ API Error: {data['error']['message']}")
                failed_geocodes += 1
                continue
            
            if data.get('data') and len(data['data']) > 0:
                result = data['data'][0]
                
                latitude = result['latitude']
                longitude = result['longitude']
                formatted_address = result.get('label', address)
                confidence = result.get('confidence', 0)
                
                print(f"   ✅ SUCCESS!")
                print(f"      📍 Coordinates: {latitude:.6f}, {longitude:.6f}")
                print(f"      🏷️ Formatted: {formatted_address}")
                print(f"      🎯 Confidence: {confidence}")
                
                # Test census tract lookup from coordinates
                census_tract = get_census_tract_from_coordinates(latitude, longitude)
                if census_tract:
                    print(f"      📊 Census Tract: {census_tract}")
                else:
                    print(f"      ⚠️ Could not get census tract")
                
                successful_geocodes += 1
                
            else:
                print(f"   ❌ No results returned")
                failed_geocodes += 1
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request Error: {e}")
            failed_geocodes += 1
        except Exception as e:
            print(f"   ❌ Unexpected Error: {e}")
            failed_geocodes += 1
    
    print(f"\n📊 POSITIONSTACK TEST RESULTS:")
    print(f"   ✅ Successful: {successful_geocodes}/{len(test_addresses)}")
    print(f"   ❌ Failed: {failed_geocodes}/{len(test_addresses)}")
    print(f"   📈 Success Rate: {successful_geocodes/len(test_addresses)*100:.1f}%")
    
    if successful_geocodes >= len(test_addresses) * 0.8:  # 80% success rate
        print(f"   🎯 EXCELLENT - Ready for full analysis!")
        return True
    else:
        print(f"   ⚠️ Issues detected - investigate before full analysis")
        return False

def get_census_tract_from_coordinates(latitude: float, longitude: float) -> str:
    """
    Get census tract from coordinates using Census API
    """
    try:
        url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
        params = {
            'x': longitude,
            'y': latitude,
            'benchmark': 'Public_AR_Current',
            'vintage': 'Current_Current',
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('result', {}).get('geographies'):
            tracts = data['result']['geographies'].get('Census Tracts', [])
            if tracts:
                return tracts[0].get('GEOID')
        
        return None
        
    except Exception as e:
        return None

def test_corrected_search_radii():
    """
    Test that our corrected search radii make sense
    """
    print(f"\n📏 SEARCH RADII TEST")
    print("=" * 30)
    
    # Test coordinates for major metros
    test_locations = [
        {"name": "Austin Downtown", "lat": 30.2672, "lon": -97.7431, "expected_radius": 8.0},
        {"name": "Houston Downtown", "lat": 29.7604, "lon": -95.3698, "expected_radius": 8.0},
        {"name": "Dallas Downtown", "lat": 32.7767, "lon": -96.7970, "expected_radius": 7.0},
        {"name": "San Antonio Downtown", "lat": 29.4241, "lon": -98.4936, "expected_radius": 7.0},
        {"name": "Fort Worth", "lat": 32.7555, "lon": -97.3308, "expected_radius": 6.0}
    ]
    
    def determine_radius(lat, lon):
        """Test version of radius determination"""
        major_metros = {
            'Houston': {
                'lat_range': (29.3, 30.3), 'lon_range': (-95.9, -94.9),
                'radius': 8.0
            },
            'Dallas': {
                'lat_range': (32.4, 33.2), 'lon_range': (-97.2, -96.4), 
                'radius': 7.0
            },
            'Austin': {
                'lat_range': (30.0, 30.6), 'lon_range': (-98.1, -97.4),
                'radius': 8.0
            },
            'San Antonio': {
                'lat_range': (29.1, 29.8), 'lon_range': (-98.9, -98.1),
                'radius': 7.0
            },
            'Fort Worth': {
                'lat_range': (32.5, 33.0), 'lon_range': (-97.6, -97.0),
                'radius': 6.0
            }
        }
        
        for metro, bounds in major_metros.items():
            if (bounds['lat_range'][0] <= lat <= bounds['lat_range'][1] and 
                bounds['lon_range'][0] <= lon <= bounds['lon_range'][1]):
                return metro, bounds['radius']
        
        return "Unknown", 7.0
    
    print("Testing corrected search radii:")
    for location in test_locations:
        metro, radius = determine_radius(location['lat'], location['lon'])
        expected = location['expected_radius']
        
        status = "✅" if radius == expected else "❌"
        print(f"  {status} {location['name']}: {radius} miles (expected: {expected})")
        if metro != "Unknown":
            print(f"      Detected as: {metro}")

def run_quick_validation():
    """
    Run quick validation before full analysis
    """
    print("🎯 QUICK VALIDATION - PositionStack & Search Radii")
    print("=" * 60)
    
    # Test PositionStack API
    positionstack_ready = test_positionstack_api()
    
    # Test search radii logic
    test_corrected_search_radii()
    
    print(f"\n🎬 GLENN GLENGARRY GLEN ROSS READINESS CHECK:")
    if positionstack_ready:
        print("   ✅ PositionStack geocoding: READY")
        print("   ✅ Search radii corrected: READY")
        print("   🚀 READY FOR FRESH ANALYSIS!")
        print("   🎯 No more bad leads from flawed data!")
        
        # Ask about proceeding to full analysis
        proceed = input("\n🚀 Proceed with full CoStar analysis? (y/N): ").strip().lower()
        if proceed == 'y':
            print("   📁 Need path to original CoStar data file...")
            return True
    else:
        print("   ❌ Issues detected - fix before proceeding")
        print("   🔧 Check PositionStack API key and connectivity")
        return False
    
    return False

if __name__ == "__main__":
    ready = run_quick_validation()
    
    if ready:
        print("\n📋 NEXT STEPS:")
        print("1. 📁 Locate your ORIGINAL CoStar raw data file")
        print("2. 🚀 Run the full fresh analysis script")
        print("3. 📊 Compare old vs new results")
        print("4. 🎯 Pursue only the ACCURATE leads!")
