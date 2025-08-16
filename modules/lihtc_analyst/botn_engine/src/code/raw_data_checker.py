#!/usr/bin/env python3
"""
Raw Data Checker
Check exactly what's in the dataset for the coordinates
"""

import pandas as pd

def check_raw_data():
    """Check the raw data exactly as it appears"""
    
    lat = 33.5515298
    lng = -117.2078974
    
    print(f"🔍 RAW DATA CHECK FOR: {lat}, {lng}")
    print("=" * 60)
    
    # Load dataset
    dataset_path = "CostarExport_HighResource_BACKUP_20250730_090645.xlsx"
    df = pd.read_excel(dataset_path)
    
    # Find matching site
    matching_site = None
    for idx, row in df.iterrows():
        if (abs(row.get('Latitude', 0) - lat) < 0.0001 and 
            abs(row.get('Longitude', 0) - lng) < 0.0001):
            matching_site = row
            site_index = idx
            break
    
    if matching_site is not None:
        print(f"📍 FOUND SITE AT ROW {site_index}:")
        print(f"   Address: {matching_site.get('Property Address')}")
        
        print(f"\n📊 RAW FLOOD DATA VALUES:")
        sfha = matching_site.get('In SFHA')
        flood_area = matching_site.get('Flood Risk Area')
        flood_zone = matching_site.get('Fema Flood Zone')
        
        print(f"   In SFHA: {repr(sfha)} (type: {type(sfha)})")
        print(f"   Flood Risk Area: {repr(flood_area)} (type: {type(flood_area)})")
        print(f"   Fema Flood Zone: {repr(flood_zone)} (type: {type(flood_zone)})")
        
        print(f"\n🔍 NULL/NaN CHECK:")
        print(f"   In SFHA is null/NaN: {pd.isna(sfha)}")
        print(f"   Flood Risk Area is null/NaN: {pd.isna(flood_area)}")
        print(f"   Fema Flood Zone is null/NaN: {pd.isna(flood_zone)}")
        
        print(f"\n📝 STRING CONVERSION CHECK:")
        sfha_str = str(sfha) if not pd.isna(sfha) else "NULL"
        flood_area_str = str(flood_area) if not pd.isna(flood_area) else "NULL"
        flood_zone_str = str(flood_zone) if not pd.isna(flood_zone) else "NULL"
        
        print(f"   In SFHA as string: '{sfha_str}'")
        print(f"   Flood Risk Area as string: '{flood_area_str}'")
        print(f"   Fema Flood Zone as string: '{flood_zone_str}'")
        
        print(f"\n🎯 CORRECTED ELIMINATION LOGIC:")
        
        # Corrected logic - only eliminate if there's actual flood data
        has_sfha = (not pd.isna(sfha)) and str(sfha).upper() == 'YES'
        has_flood_area = (not pd.isna(flood_area)) and ('High Risk' in str(flood_area))
        has_flood_zone = (not pd.isna(flood_zone)) and any(zone in str(flood_zone).upper() for zone in ['A', 'AE', 'AH', 'AO', 'V', 'VE'])
        
        print(f"   Has SFHA (YES): {has_sfha}")
        print(f"   Has High Risk Area: {has_flood_area}")
        print(f"   Has High Risk Zone (A, AE, V, etc.): {has_flood_zone}")
        
        should_eliminate = has_sfha or has_flood_area or has_flood_zone
        print(f"   Should eliminate: {should_eliminate}")
        
        if not should_eliminate:
            print(f"   ✅ THIS SITE SHOULD BE SAFE!")
        else:
            print(f"   🚨 This site should be eliminated")
        
        # Show some other sites for comparison
        print(f"\n📊 SAMPLE OF OTHER SITES:")
        for i, (_, other_row) in enumerate(df.head(10).iterrows()):
            if pd.notna(other_row.get('Latitude')):
                addr = other_row.get('Property Address', 'Unknown')[:30]
                sfha_val = other_row.get('In SFHA')
                zone_val = other_row.get('Fema Flood Zone')
                print(f"   {i+1}. {addr} - SFHA: {repr(sfha_val)} - Zone: {repr(zone_val)}")
    
    else:
        print("❌ Site not found")

if __name__ == "__main__":
    check_raw_data()