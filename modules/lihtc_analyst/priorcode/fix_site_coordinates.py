#!/usr/bin/env python3
"""
Fix Site Coordinates using Google Geocoding API
Get accurate coordinates for all 6 D'Marco sites

Author: Bill Rice, Structured Consultants LLC
Date: June 26, 2025
"""

import requests
import time

def geocode_address(address):
    """Use Google Geocoding API to get accurate coordinates"""
    
    # Free geocoding services (no API key needed)
    # 1. Try Nominatim (OpenStreetMap)
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'us'
    }
    
    try:
        response = requests.get(nominatim_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lng = float(data[0]['lon'])
                return lat, lng, data[0]['display_name']
    except Exception as e:
        print(f"Nominatim failed for {address}: {e}")
    
    return None, None, None

def main():
    sites = [
        '615 N Saginaw Blvd, Saginaw, TX 76179',
        '2002 Mansfield Webb Rd, Mansfield, TX 76002',
        '1051 W Marshall Dr, Grand Prairie, TX 75051',
        '7100 W Camp Wisdom Rd, Dallas, TX 75249',
        '1497 US-67, Cedar Hill, TX 75104',
        '1000 S Joe Wilson Rd, Cedar Hill, TX 75104'
    ]
    
    print("🔍 Geocoding all site addresses for accurate coordinates...")
    
    corrected_coords = []
    
    for address in sites:
        print(f"\n📍 Geocoding: {address}")
        lat, lng, display_name = geocode_address(address)
        
        if lat and lng:
            print(f"   ✅ Found: {lat:.6f}, {lng:.6f}")
            print(f"   📍 Full: {display_name}")
            corrected_coords.append({
                'address': address,
                'lat': lat,
                'lng': lng,
                'display_name': display_name
            })
        else:
            print(f"   ❌ Failed to geocode")
            corrected_coords.append({
                'address': address,
                'lat': None,
                'lng': None,
                'display_name': None
            })
        
        time.sleep(1)  # Rate limiting
    
    print(f"\n📊 Corrected Coordinates:")
    print("=" * 80)
    
    for i, coord in enumerate(corrected_coords):
        if coord['lat']:
            print(f"Site {i+1}: {coord['address']}")
            print(f"   Coordinates: {coord['lat']:.6f}, {coord['lng']:.6f}")
            print(f"   Google Maps: https://www.google.com/maps?q={coord['lat']},{coord['lng']}")
            print()

if __name__ == "__main__":
    main()