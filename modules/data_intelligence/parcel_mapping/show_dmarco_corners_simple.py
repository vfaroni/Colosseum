#!/usr/bin/env python3

"""
Simple extraction of D'Marco parcel corner coordinates
Shows real boundary points without KML export
"""

import sys
import os
import pandas as pd
import json
from datetime import datetime

# Add the parcel mapping module to path
sys.path.append('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping')

from universal_parcel_mapper import UniversalParcelMapper, ParcelData

def show_dmarco_corner_coordinates():
    """Show actual parcel corner coordinates for successful D'Marco sites"""
    
    print("🗺️ D'MARCO PARCEL CORNER COORDINATES")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Successful D'Marco sites 
    sites = [
        {
            'name': 'Boerne Ralph Fair Road',
            'lat': 29.6859485,
            'lng': -98.6325156,
            'address': 'Ralph Fair Rd., Boerne, TX'
        },
        {
            'name': 'San Antonio Stone Oak Park',
            'lat': 29.6495764,
            'lng': -98.464094,
            'address': '20623 Stone Oak Parkway, San Antonio, TX'
        }
    ]
    
    mapper = UniversalParcelMapper()
    
    for site in sites:
        print(f"🏢 {site['name'].upper()}")
        print(f"📍 {site['address']}")
        print(f"🎯 {site['lat']:.6f}, {site['lng']:.6f}")
        print()
        
        parcel_data = mapper.get_parcel_from_coordinates(site['lat'], site['lng'], 'TX')
        
        if parcel_data and parcel_data.boundary_coordinates:
            coords = parcel_data.boundary_coordinates
            
            print(f"✅ FOUND {len(coords)} BOUNDARY COORDINATES")
            print(f"🏛️ APN: {parcel_data.apn}")
            print(f"📐 Area: {parcel_data.property_area_acres:.2f} acres")
            print()
            
            print("🗺️ PARCEL CORNER COORDINATES:")
            for i, (lat, lng) in enumerate(coords):
                print(f"   {i+1:2d}. {lat:.8f}, {lng:.8f}")
            
            print()
            
            # Property dimensions
            lats = [coord[0] for coord in coords]
            lngs = [coord[1] for coord in coords]
            
            print(f"📏 PROPERTY BOUNDARIES:")
            print(f"   North: {max(lats):.8f}")
            print(f"   South: {min(lats):.8f}")
            print(f"   East:  {max(lngs):.8f}")
            print(f"   West:  {min(lngs):.8f}")
            
        else:
            print("❌ No boundary data found")
        
        print()
        print("-" * 50)
        print()

if __name__ == "__main__":
    show_dmarco_corner_coordinates()