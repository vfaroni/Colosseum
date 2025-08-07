#!/usr/bin/env python3
"""
Verify Bryson Cottages Location
Double-check the geocoding and provide detailed location information
"""

import requests
import time

def reverse_geocode(lat, lon):
    """Reverse geocode coordinates to get detailed location info"""
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'LIHTC-Location-Verification/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        return result
        
    except Exception as e:
        print(f"⚠️ Reverse geocoding error: {e}")
        return None

def forward_geocode(address):
    """Forward geocode to verify the address search"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 3,
            'countrycodes': 'us',
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'LIHTC-Location-Verification/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        results = response.json()
        return results
        
    except Exception as e:
        print(f"⚠️ Forward geocoding error: {e}")
        return None

def verify_bryson_cottages():
    """Verify the Bryson Cottages location and provide detailed information"""
    
    print("🏗️ BRYSON COTTAGES LOCATION VERIFICATION")
    print("=" * 50)
    
    # Coordinates from the analysis
    lat = 38.382446
    lon = -120.802992
    address = "140 Bryson Drive"
    
    print(f"📍 Coordinates from analysis: {lat}, {lon}")
    print(f"🏠 Address searched: {address}")
    print()
    
    # Reverse geocode to see where these coordinates actually point
    print("🔍 REVERSE GEOCODING (What's at these coordinates?)...")
    reverse_result = reverse_geocode(lat, lon)
    
    if reverse_result:
        display_name = reverse_result.get('display_name', 'Unknown')
        address_parts = reverse_result.get('address', {})
        
        print(f"✅ Location found: {display_name}")
        print()
        print("📍 Address Breakdown:")
        
        # Extract key address components
        house_number = address_parts.get('house_number', '')
        road = address_parts.get('road', '')
        city = address_parts.get('city', address_parts.get('town', address_parts.get('village', '')))
        county = address_parts.get('county', '')
        state = address_parts.get('state', '')
        postcode = address_parts.get('postcode', '')
        
        if house_number:
            print(f"   🏠 House Number: {house_number}")
        if road:
            print(f"   🛣️ Road: {road}")
        if city:
            print(f"   🏘️ City/Town: {city}")
        if county:
            print(f"   🗺️ County: {county}")
        if state:
            print(f"   📍 State: {state}")
        if postcode:
            print(f"   📮 ZIP Code: {postcode}")
        
    else:
        print("❌ Could not reverse geocode coordinates")
    
    print()
    
    # Forward geocode variations to see all possibilities
    print("🔍 FORWARD GEOCODING (Alternative searches)...")
    
    search_variations = [
        "140 Bryson Drive",
        "140 Bryson Drive, CA",
        "140 Bryson Dr, California",
        "Bryson Drive, California",
        "Bryson Cottages, California"
    ]
    
    for i, search in enumerate(search_variations):
        print(f"\n{i+1}. Searching: '{search}'")
        results = forward_geocode(search)
        
        if results:
            print(f"   Found {len(results)} results:")
            for j, result in enumerate(results):
                result_lat = float(result['lat'])
                result_lon = float(result['lon'])
                result_name = result['display_name']
                
                # Calculate distance from original coordinates
                lat_diff = abs(result_lat - lat)
                lon_diff = abs(result_lon - lon)
                approx_distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 69  # Rough miles
                
                print(f"   {j+1}. {result_lat:.6f}, {result_lon:.6f}")
                print(f"      📍 {result_name}")
                print(f"      📏 ~{approx_distance:.1f} miles from original")
                
                # Check if this is significantly different
                if approx_distance > 10:
                    print(f"      ⚠️ SIGNIFICANTLY DIFFERENT LOCATION!")
        else:
            print(f"   ❌ No results found")
        
        time.sleep(1)  # Rate limiting
    
    # Analysis
    print(f"\n" + "=" * 50)
    print("📊 LOCATION ANALYSIS")
    print("=" * 50)
    
    if reverse_result:
        address_parts = reverse_result.get('address', {})
        city = address_parts.get('city', address_parts.get('town', address_parts.get('village', 'Unknown')))
        county = address_parts.get('county', 'Unknown County')
        state = address_parts.get('state', 'Unknown State')
        
        print(f"🎯 The coordinates {lat}, {lon} point to:")
        print(f"   📍 Location: {city}, {county}, {state}")
        
        # Check if this makes sense for LIHTC development
        if state == "California":
            print(f"   ✅ Location is in California (good for CTCAC)")
        else:
            print(f"   ⚠️ Location is NOT in California (concerning for CTCAC analysis)")
        
        # Check if it's in a reasonable area for development
        if 'forest' in display_name.lower() or 'wilderness' in display_name.lower():
            print(f"   ⚠️ Location appears to be in wilderness/forest area")
        elif 'lake' in display_name.lower():
            print(f"   ⚠️ Location appears to be near water body")
        else:
            print(f"   ✅ Location appears to be in developed area")
    
    # Transit analysis context
    print(f"\n🚌 TRANSIT CONTEXT:")
    print(f"   The original analysis found transit nearby with 6 CTCAC points")
    print(f"   This suggests the location has legitimate transit access")
    print(f"   BUT the coordinates should be verified for accuracy")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"   1. 🔍 Verify the actual address of 'Bryson Cottages 12-Lot Subdivision'")
    print(f"   2. 📍 Double-check if 140 Bryson Drive is the correct address")
    print(f"   3. 🗺️ Cross-reference with property records or listing details")
    print(f"   4. 🚌 If address is wrong, re-run transit analysis with correct coordinates")

if __name__ == "__main__":
    try:
        verify_bryson_cottages()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()