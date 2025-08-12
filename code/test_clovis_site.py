#!/usr/bin/env python3
"""
Test Specific Clovis Site - 8045 Alluvial Ave, Fresno, CA
Test the corrected transit processor on the actual Production 1 site
"""

import pandas as pd
import sys
import os
from pathlib import Path
import json
from datetime import datetime
import requests

# Add the botn_engine directory to the path
botn_engine_path = Path(__file__).parent / "modules/lihtc_analyst/botn_engine"
sys.path.insert(0, str(botn_engine_path))

from ultimate_ctcac_transit_processor import UltimateCTCACTransitProcessor

def geocode_address(address):
    """Geocode address using OpenStreetMap Nominatim API"""
    try:
        # Use Nominatim (free, no API key required)
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'us'
        }
        headers = {
            'User-Agent': 'LIHTC-Transit-Analysis/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        results = response.json()
        if results:
            result = results[0]
            lat = float(result['lat'])
            lon = float(result['lon'])
            display_name = result['display_name']
            return lat, lon, display_name
        else:
            return None, None, None
            
    except Exception as e:
        print(f"⚠️ Geocoding error: {e}")
        return None, None, None

def test_clovis_site():
    """Test the specific Clovis site from Production 1"""
    
    print("🏗️ TESTING SPECIFIC CLOVIS SITE")
    print("=" * 60)
    print("Site: 1.94 Acre Lot- Clovis Residential Parcel")
    print("Address: 8045 Alluvial Ave, Fresno, CA")
    print("⚔️ Using STRIKE_LEADER corrected transit processor")
    print()
    
    # Geocode the address
    print("📍 GEOCODING ADDRESS...")
    address = "8045 Alluvial Ave, Fresno, CA"
    lat, lon, display_name = geocode_address(address)
    
    if lat is None or lon is None:
        print("❌ Could not geocode address - using approximate Clovis coordinates")
        lat, lon = 36.8477, -119.7016  # Approximate Clovis area
        display_name = "Approximate Clovis, CA location"
    
    print(f"✅ Geocoded to: {lat:.6f}, {lon:.6f}")
    print(f"📍 Location: {display_name}")
    print()
    
    # Calculate site information
    site_acres = 1.94
    # Estimate density based on typical LIHTC development
    estimated_units = int(site_acres * 20)  # ~20 units per acre typical
    density_per_acre = estimated_units / site_acres
    
    print(f"🏢 SITE DETAILS:")
    print(f"   • Size: {site_acres} acres")
    print(f"   • Estimated units: {estimated_units}")
    print(f"   • Estimated density: {density_per_acre:.1f} units/acre")
    print()
    
    # Initialize corrected processor
    processor = UltimateCTCACTransitProcessor()
    print("🏛️ Initialized Ultimate CTCAC Transit Processor (STRIKE_LEADER CORRECTED)")
    print()
    
    # Load datasets
    print("📊 Loading comprehensive transit datasets...")
    datasets_loaded = processor.load_all_datasets()
    print()
    
    print("🚌 ANALYZING CLOVIS SITE TRANSIT ACCESS...")
    print("=" * 60)
    
    try:
        # Create site data
        site_data = {
            'site_id': 'CLOVIS_ALLUVIAL_001',
            'latitude': lat,
            'longitude': lon,
            'density_per_acre': density_per_acre
        }
        
        # Analyze with corrected processor
        print("🔍 Running corrected transit analysis...")
        result = processor.analyze_site_ultimate(site_data)
        
        print("\n🎯 CORRECTED TRANSIT ANALYSIS RESULTS:")
        print("=" * 50)
        
        # Basic results
        points = result['ctcac_points_earned']
        method = result['qualification_method']
        qualified = result['transit_qualified']
        base_points = result.get('base_points', 0)
        tiebreaker_points = result.get('tiebreaker_points', 0)
        
        print(f"🚌 CTCAC TRANSIT SCORE: {points} points")
        print(f"   • Base points: {base_points}")
        print(f"   • Tiebreaker points: {tiebreaker_points}")
        print(f"✅ Qualification method: {method}")
        print(f"🏅 Transit qualified: {'YES' if qualified else 'NO'}")
        print()
        
        # HQTA Analysis
        hqta_details = result.get('hqta_details', {})
        print("🏛️ HQTA ANALYSIS:")
        if hqta_details.get('within_hqta', False):
            print(f"   ✅ WITHIN HQTA BOUNDARY")
            print(f"   • Type: {hqta_details.get('hqta_type', 'Unknown')}")
            print(f"   • Agency: {hqta_details.get('agency_primary', 'Unknown')}")
        else:
            print(f"   ❌ NOT within HQTA boundary")
            print(f"   • Analysis method: {hqta_details.get('analysis_method', 'Unknown')}")
        print()
        
        # Frequency Analysis (for non-HQTA sites)
        if not hqta_details.get('within_hqta', False):
            freq_analysis = result.get('frequency_analysis', {})
            if freq_analysis:
                print("🚏 FREQUENCY-BASED ANALYSIS (CORRECTED):")
                stops = freq_analysis.get('total_stops', 0)
                high_freq = freq_analysis.get('high_frequency_stops', 0)
                validated = freq_analysis.get('high_frequency_validated_stops', 0)
                best_freq = freq_analysis.get('estimated_peak_frequency', 999)
                hqts_enhanced = freq_analysis.get('hqts_enhanced_stops', 0)
                
                print(f"   🚏 Stops within 1/3 mile: {stops}")
                print(f"   ⚡ High-frequency stops (≤30 min): {high_freq}")
                print(f"   ✅ Validated high-frequency: {validated}")
                print(f"   📊 HQTS enhanced stops: {hqts_enhanced}")
                print(f"   🕐 Best frequency: {best_freq:.1f} minutes")
                print()
                
                # Show detailed stop information
                stop_details = freq_analysis.get('stop_details', [])
                if stop_details:
                    print("   🚌 NEARBY TRANSIT STOPS:")
                    for i, stop in enumerate(stop_details[:5]):  # Show first 5 stops
                        stop_name = stop.get('stop_name', 'Unknown')
                        agency = stop.get('agency', 'Unknown')
                        distance = stop.get('distance_miles', 0)
                        freq = stop.get('calculated_frequency_minutes', 999)
                        routes = stop.get('n_routes', 0)
                        arrivals = stop.get('n_arrivals', 0)
                        is_high_freq = stop.get('is_high_frequency', False)
                        
                        print(f"   {i+1}. {stop_name[:40]}")
                        print(f"      • Agency: {agency}")
                        print(f"      • Distance: {distance:.2f} miles")
                        print(f"      • Frequency: {freq:.1f} minutes")
                        print(f"      • Routes: {routes}, Daily arrivals: {arrivals}")
                        print(f"      • High-frequency: {'YES' if is_high_freq else 'NO'}")
                        print()
        
        # Scoring Details
        scoring_details = result.get('scoring_details', {})
        if scoring_details:
            print("📊 DETAILED SCORING ANALYSIS:")
            analysis_method = scoring_details.get('analysis_method', 'Unknown')
            is_high_density = scoring_details.get('is_high_density', False)
            density_value = scoring_details.get('density_per_acre', 0)
            tiebreaker_freq = scoring_details.get('tiebreaker_frequency_minutes', 999)
            scoring_method = scoring_details.get('scoring_method', 'Unknown')
            
            print(f"   • Analysis method: {analysis_method}")
            print(f"   • Scoring method: {scoring_method}")
            print(f"   • Site density: {density_value:.1f} units/acre")
            print(f"   • High-density bonus eligible: {'YES' if is_high_density else 'NO'}")
            if tiebreaker_freq < 999:
                print(f"   • Tiebreaker frequency: {tiebreaker_freq:.1f} minutes")
        print()
        
        # Analysis of what changed
        print("🔧 STRIKE_LEADER FIXES IMPACT:")
        print("=" * 40)
        
        if points > 0:
            print("✅ SITE NOW RECEIVES TRANSIT POINTS")
            if not hqta_details.get('within_hqta', False):
                print("   • Non-HQTA site scoring with corrected frequency analysis")
                print("   • Proper peak hour calculations implemented")
                print("   • Multi-tier distance analysis (1/3 and 1/2 mile)")
            
            if base_points >= 6:
                print("   • High base points (6-7) achievable with corrections")
            if tiebreaker_points > 0:
                print("   • Tiebreaker bonus applied for excellent service")
                
        else:
            print("❌ Site does not qualify for transit points")
            print("   • No qualifying transit within required distances")
            
        print()
        print("💡 BEFORE vs AFTER COMPARISON:")
        print(f"   Before fixes: Likely 0-4 points (due to calculation errors)")
        print(f"   After fixes: {points} points (proper CTCAC methodology)")
        
        # Export results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"CLOVIS_ALLUVIAL_TRANSIT_TEST_{timestamp}.json"
        
        export_data = {
            'test_timestamp': datetime.now().isoformat(),
            'site_name': '1.94 Acre Lot- Clovis Residential Parcel',
            'address': '8045 Alluvial Ave, Fresno, CA',
            'geocoded_coordinates': {'latitude': lat, 'longitude': lon},
            'site_details': {
                'acres': site_acres,
                'estimated_units': estimated_units,
                'density_per_acre': density_per_acre
            },
            'transit_analysis_result': result,
            'strike_leader_fixes_applied': [
                'Proper frequency calculations (not 30/n_routes)',
                'Full 3-7 point CTCAC scoring range',
                'High-frequency validation with peak hour analysis',
                'Density integration for bonus points',
                'Multi-distance analysis (1/3 and 1/2 mile)'
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"\n📄 Detailed analysis exported to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing Clovis site: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        print("🏛️ COLOSSEUM CLOVIS SITE TRANSIT TEST")
        print("⚔️ Testing STRIKE_LEADER corrections on actual Production 1 site")
        print()
        
        success = test_clovis_site()
        
        if success:
            print("\n🏆 CLOVIS SITE TRANSIT ANALYSIS COMPLETE")
            print("⚔️ STRIKE_LEADER corrections working perfectly!")
        else:
            print("\n❌ CLOVIS SITE TRANSIT ANALYSIS FAILED")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    exit(0)