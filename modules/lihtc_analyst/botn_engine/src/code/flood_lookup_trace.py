#!/usr/bin/env python3
"""
Flood Lookup Trace - Show exactly how flood criteria is determined
"""

import sys
from pathlib import Path
import requests

sys.path.append(str(Path(__file__).parent))
from multi_source_flood_analyzer import MultiSourceFloodAnalyzer

def trace_flood_lookup():
    """Trace exactly how flood criteria is determined"""
    
    lat = 33.5515298
    lng = -117.2078974
    
    print(f"🔍 TRACING FLOOD LOOKUP FOR: {lat}, {lng}")
    print("=" * 60)
    
    analyzer = MultiSourceFloodAnalyzer()
    
    # Test each data source individually
    print("📊 TESTING EACH FLOOD DATA SOURCE:")
    
    print("\n1. 🌊 USGS Flood Services:")
    try:
        usgs_result = analyzer._query_usgs_flood_data(lat, lng)
        print(f"   Result: {usgs_result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. 🏛️ FEMA Alternative Endpoints:")
    try:
        fema_result = analyzer._query_fema_alternative(lat, lng)
        print(f"   Result: {fema_result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. 🏢 County GIS Services:")
    try:
        county_result = analyzer._query_county_flood_services(lat, lng)
        print(f"   Result: {county_result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. 🌊 NOAA Coastal Flood:")
    try:
        noaa_result = analyzer._query_noaa_coastal_flood(lat, lng)
        print(f"   Result: {noaa_result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n5. ⛰️ Elevation Modeling:")
    try:
        elevation_result = analyzer._analyze_topographic_flood_risk(lat, lng)
        print(f"   Result: {elevation_result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test with existing data
    print("\n6. 📋 Using Existing Dataset Data:")
    existing_data = {
        'In SFHA': float('nan'),
        'Flood Risk Area': 'Moderate to Low Risk Areas',
        'Fema Flood Zone': 'Area of moderate flood hazard, usually the area between the limits of the 100-year and 500-year floods.'
    }
    
    try:
        existing_result = analyzer._process_existing_flood_data(existing_data, "25071 Adams Ave", lat, lng)
        print(f"   Result: {existing_result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Show what the comprehensive analysis returns
    print("\n🎯 COMPREHENSIVE ANALYSIS RESULT:")
    final_result = analyzer.analyze_flood_risk_comprehensive(lat, lng, existing_data, "25071 Adams Ave")
    
    print(f"   Flood Risk Level: {final_result.get('flood_risk_level')}")
    print(f"   FEMA Flood Zone: {final_result.get('fema_flood_zone')}")
    print(f"   Meets Flood Criteria: {final_result.get('meets_flood_criteria')}")
    print(f"   Data Source: {final_result.get('data_source')}")
    print(f"   Elimination Reason: {final_result.get('elimination_reason')}")
    
    # Also test direct FEMA lookup
    print("\n🏛️ DIRECT FEMA API TEST:")
    fema_url = "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer/28/query"
    params = {
        'where': '1=1',
        'geometry': f'{lng},{lat}',
        'geometryType': 'esriGeometryPoint',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': 'FLD_ZONE,SFHA_TF,ZONE_SUBTY',
        'returnGeometry': 'false',
        'f': 'json'
    }
    
    try:
        response = requests.get(fema_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   FEMA API Response: {data}")
        else:
            print(f"   FEMA API Error: {response.status_code}")
    except Exception as e:
        print(f"   FEMA API Exception: {e}")

if __name__ == "__main__":
    trace_flood_lookup()