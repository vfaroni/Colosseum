#!/usr/bin/env python3
"""
Coordinate Checker
Analyze specific coordinates: 33.5515298, -117.2078974
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from multi_source_fire_analyzer import MultiSourceFireAnalyzer
from multi_source_flood_analyzer import MultiSourceFloodAnalyzer

def check_specific_coordinates():
    """Check the specific coordinates provided by user"""
    
    lat = 33.5515298
    lng = -117.2078974
    
    print(f"🔍 ANALYZING COORDINATES: {lat}, {lng}")
    print("=" * 50)
    
    # Find this site in the dataset
    dataset_path = "CostarExport_HighResource_BACKUP_20250730_090645.xlsx"
    df = pd.read_excel(dataset_path)
    
    # Find matching site
    matching_site = None
    for _, row in df.iterrows():
        if (abs(row.get('Latitude', 0) - lat) < 0.0001 and 
            abs(row.get('Longitude', 0) - lng) < 0.0001):
            matching_site = row
            break
    
    if matching_site is not None:
        print(f"📍 FOUND MATCHING SITE:")
        print(f"   Address: {matching_site.get('Property Address', 'Unknown')}")
        print(f"   Coordinates: {matching_site.get('Latitude')}, {matching_site.get('Longitude')}")
        
        print(f"\n🌊 FLOOD DATA IN DATASET:")
        print(f"   In SFHA: '{matching_site.get('In SFHA', 'N/A')}'")
        print(f"   Flood Risk Area: '{matching_site.get('Flood Risk Area', 'N/A')}'")
        print(f"   FEMA Flood Zone: '{matching_site.get('Fema Flood Zone', 'N/A')}'")
        
        # Check what our elimination logic would do
        sfha_status = str(matching_site.get('In SFHA', '')).upper()
        flood_risk_area = str(matching_site.get('Flood Risk Area', ''))
        fema_flood_zone = str(matching_site.get('Fema Flood Zone', ''))
        
        print(f"\n🔍 ELIMINATION LOGIC CHECK:")
        print(f"   SFHA status upper: '{sfha_status}'")
        print(f"   Has 'YES' SFHA: {sfha_status == 'YES'}")
        print(f"   Flood risk area: '{flood_risk_area}'")
        print(f"   Has 'Risk' in area: {'Risk' in flood_risk_area}")
        print(f"   FEMA flood zone: '{fema_flood_zone}'")
        
        # Check flood indicators
        flood_indicators = ['A', 'AE', 'AH', 'AO', 'AR', 'A99', 'V', 'VE', 'B', 'C', 'X', 'D', 'SFHA']
        zone_matches = [indicator for indicator in flood_indicators if indicator in fema_flood_zone.upper()]
        print(f"   Zone indicators found: {zone_matches}")
        
        has_sfha = sfha_status == 'YES'
        has_flood_zone = any(indicator in fema_flood_zone.upper() for indicator in flood_indicators)
        has_flood_area = 'Risk' in flood_risk_area
        
        should_eliminate = has_sfha or has_flood_zone or has_flood_area
        
        print(f"\n🎯 ELIMINATION DECISION:")
        print(f"   Should eliminate: {should_eliminate}")
        if should_eliminate:
            reasons = []
            if has_sfha:
                reasons.append(f"SFHA: {sfha_status}")
            if has_flood_zone:
                reasons.append(f"Zone: {fema_flood_zone}")
            if has_flood_area:
                reasons.append(f"Area: {flood_risk_area}")
            print(f"   Reasons: {'; '.join(reasons)}")
        else:
            print(f"   This site would be SAFE!")
        
    else:
        print("❌ No matching site found in dataset")
    
    # Also test with our analyzers
    print(f"\n🔥 FIRE ANALYSIS:")
    fire_analyzer = MultiSourceFireAnalyzer()
    fire_result = fire_analyzer.analyze_fire_risk_comprehensive(lat, lng, "Test Site")
    print(f"   Fire hazard: {fire_result.get('hazard_class', 'Unknown')}")
    print(f"   Data source: {fire_result.get('data_source', 'Unknown')}")
    print(f"   Meets criteria: {fire_result.get('meets_criteria', 'Unknown')}")
    
    print(f"\n🌊 FLOOD ANALYSIS:")
    flood_analyzer = MultiSourceFloodAnalyzer()
    existing_flood = {}
    if matching_site is not None:
        existing_flood = {
            'In SFHA': matching_site.get('In SFHA'),
            'Flood Risk Area': matching_site.get('Flood Risk Area'),
            'Fema Flood Zone': matching_site.get('Fema Flood Zone')
        }
    
    flood_result = flood_analyzer.analyze_flood_risk_comprehensive(lat, lng, existing_flood, "Test Site")
    print(f"   Flood risk: {flood_result.get('flood_risk_level', 'Unknown')}")
    print(f"   FEMA zone: {flood_result.get('fema_flood_zone', 'Unknown')}")
    print(f"   Meets criteria: {flood_result.get('meets_flood_criteria', 'Unknown')}")
    print(f"   Data source: {flood_result.get('data_source', 'Unknown')}")

if __name__ == "__main__":
    check_specific_coordinates()