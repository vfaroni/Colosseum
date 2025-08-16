#!/usr/bin/env python3
"""
Alternative ZIP Code Lookup Services for Texas DDA Analysis
Tests multiple free services to find working ZIP code geocoding
"""

import requests
import time
import json

def test_zip_lookup_services(lat, lon, city_name):
    """Test multiple ZIP lookup services to find working options"""
    
    print(f"🔍 Testing ZIP lookup for {city_name} ({lat:.4f}, {lon:.4f})")
    print("-" * 50)
    
    results = {}
    
    # Method 1: Nominatim (OpenStreetMap) - Free, no API key needed
    try:
        print("1. Testing Nominatim (OpenStreetMap)...")
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'addressdetails': 1,
            'zoom': 18
        }
        headers = {'User-Agent': 'LIHTC-Analysis/1.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'address' in data and 'postcode' in data['address']:
                zip_code = data['address']['postcode']
                results['nominatim'] = zip_code[:5]  # Get 5-digit ZIP
                print(f"   ✅ Success: {zip_code[:5]}")
            else:
                print("   ❌ No ZIP code in response")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    time.sleep(1)  # Rate limiting
    
    # Method 2: GeoPy with Nominatim (alternative interface)
    try:
        print("2. Testing GeoPy Nominatim...")
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut, GeocoderServiceError
        
        geolocator = Nominatim(user_agent="LIHTC-Analysis")
        location = geolocator.reverse((lat, lon), timeout=10)
        
        if location and location.raw.get('address', {}).get('postcode'):
            zip_code = location.raw['address']['postcode']
            results['geopy_nominatim'] = zip_code[:5]
            print(f"   ✅ Success: {zip_code[:5]}")
        else:
            print("   ❌ No ZIP code found")
            
    except ImportError:
        print("   ⚠️ GeoPy not installed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    time.sleep(1)
    
    # Method 3: MapBox Geocoding (requires free API key but very reliable)
    try:
        print("3. Testing MapBox (would need free API key)...")
        # Placeholder - would need API key
        print("   ⚠️ Requires API key setup")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Method 4: Census Bureau alternative endpoint
    try:
        print("4. Testing Census Bureau alternative...")
        url = "https://geocoding.geo.census.gov/geocoder/locations/coordinates"
        params = {
            'x': lon,
            'y': lat,
            'benchmark': 'Public_AR_Current',
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            matches = data.get('result', {}).get('addressMatches', [])
            if matches:
                address_components = matches[0].get('addressComponents', {})
                zip_code = address_components.get('zip')
                if zip_code:
                    results['census_alt'] = zip_code
                    print(f"   ✅ Success: {zip_code}")
                else:
                    print("   ❌ No ZIP in address components")
            else:
                print("   ❌ No address matches")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    time.sleep(1)
    
    # Method 5: Zippopotam.us (free ZIP info service)
    # Note: This is reverse - we'd need ZIP to get coordinates, not coordinates to get ZIP
    print("5. Zippopotam.us - Not suitable (ZIP->coordinates, not coordinates->ZIP)")
    
    print(f"\n📊 Results for {city_name}:")
    for service, zip_code in results.items():
        print(f"   {service}: {zip_code}")
    
    # Return the most reliable result
    if 'nominatim' in results:
        return results['nominatim']
    elif 'geopy_nominatim' in results:
        return results['geopy_nominatim']
    elif 'census_alt' in results:
        return results['census_alt']
    else:
        return None

def create_working_zip_lookup():
    """Create a working ZIP lookup function for Texas sites"""
    
    def lookup_zip_texas(lat, lon, city="Unknown"):
        """Reliable ZIP lookup using Nominatim"""
        try:
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1,
                'zoom': 18
            }
            headers = {'User-Agent': 'LIHTC-QCT-DDA-Analysis/1.0'}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'address' in data and 'postcode' in data['address']:
                    zip_code = data['address']['postcode']
                    return zip_code[:5]  # Return 5-digit ZIP
            
            return None
        except Exception:
            return None
    
    return lookup_zip_texas

if __name__ == "__main__":
    print("🎯 TESTING ZIP LOOKUP SERVICES FOR TEXAS")
    print("=" * 50)
    
    # Test on some Texas cities from our dataset
    test_locations = [
        (32.7767, -96.7970, 'Dallas'),        # Should be 75201 area
        (29.7604, -95.3698, 'Houston'),       # Should be 77002 area  
        (30.2672, -97.7431, 'Austin'),        # Should be 78701 area
        (29.4241, -98.4936, 'San Antonio'),   # Should be 78205 area
        (32.7555, -97.3308, 'Fort Worth'),    # Should be 76102 area
    ]
    
    print("Testing multiple services on known Texas locations...")
    print()
    
    for lat, lon, city in test_locations:
        zip_result = test_zip_lookup_services(lat, lon, city)
        print(f"Best result for {city}: {zip_result}")
        print()
        time.sleep(2)  # Be nice to free services
    
    print("🎯 CREATING PRODUCTION ZIP LOOKUP FUNCTION...")
    zip_lookup_func = create_working_zip_lookup()
    
    print("Testing production function...")
    for lat, lon, city in test_locations[:2]:  # Test first 2
        zip_code = zip_lookup_func(lat, lon, city)
        print(f"{city}: {zip_code}")
        time.sleep(1)