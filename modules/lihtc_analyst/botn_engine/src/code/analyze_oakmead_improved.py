#!/usr/bin/env python3
"""
Show improved analysis results for 1205 Oakmead Parkway after transit data update
"""

import json
from pathlib import Path

def compare_analysis_results():
    """Compare before and after transit data implementation"""
    
    # Load the latest analysis
    outputs_dir = Path(__file__).parent / "outputs"
    latest_file = sorted(outputs_dir.glob("Oakmead_Parkway_1205_Analysis_*.json"))[-1]
    
    with open(latest_file, 'r') as f:
        results = json.load(f)
    
    print("=" * 80)
    print("IMPROVED ANALYSIS RESULTS - 1205 Oakmead Parkway, Sunnyvale CA 94085")
    print("=" * 80)
    
    # Site basics
    print(f"\n📍 SITE INFORMATION:")
    print(f"   Coordinates: {results['site_info']['latitude']}, {results['site_info']['longitude']}")
    print(f"   Census Tract: {results['site_info']['census_tract']}")
    
    # Federal status
    print(f"\n🏛️  FEDERAL STATUS:")
    federal = results['federal_status']
    print(f"   QCT Qualified: {'✅' if federal['qct_qualified'] else '❌'} {federal['qct_qualified']}")
    print(f"   DDA Qualified: {'✅' if federal['dda_qualified'] else '❌'} {federal['dda_qualified']}")
    if federal['dda_qualified']:
        print(f"   📈 30% Basis Boost Available: {federal['basis_boost_percentage']}%")
    
    # Scoring breakdown
    print(f"\n🎯 CALIFORNIA CTCAC SCORING:")
    scoring = results['state_scoring']
    print(f"   Total Points: {scoring['total_points']}/30")
    print(f"   └── Opportunity Area: {scoring['scoring_breakdown']['opportunity_area_points']} points")
    print(f"   └── Amenities: {scoring['scoring_breakdown']['amenity_points']} points")
    print(f"   └── Transit (HQTA): {scoring['scoring_breakdown']['transit_points']} points")
    print(f"   └── Federal Bonus: {scoring['scoring_breakdown']['federal_bonus']} points")
    
    # Amenity details
    print(f"\n🏢 AMENITY ANALYSIS BREAKDOWN:")
    amenities = results['amenity_analysis']['amenity_breakdown']
    
    for category, data in amenities.items():
        points = data['points_earned']
        max_points = data['max_possible']
        print(f"   {category.title()}: {points} points (max: {max_points})")
        
        if data['details']:
            for detail in data['details'][:3]:  # Show top 3
                name = detail['name'][:30]  # Truncate long names
                distance = detail['distance']
                earned = detail['points_earned']
                print(f"      • {name}: {distance:.2f} mi → {earned} pts")
    
    # Transit success story
    print(f"\n🚌 TRANSIT SUCCESS:")
    transit_stops = results['amenity_analysis']['nearby_amenities']['transit']
    if transit_stops:
        print(f"   Found {len(transit_stops)} transit stops within 3 miles!")
        closest_stops = sorted(transit_stops, key=lambda x: x['distance_miles'])[:3]
        for stop in closest_stops:
            print(f"   • {stop['name']}: {stop['distance_miles']:.2f} miles ({stop['agency']})")
    
    # Issues that remain
    print(f"\n⚠️  REMAINING ISSUES:")
    issues = results['competitive_summary']['disqualifying_factors']
    for issue in issues:
        print(f"   • {issue}")
    
    print(f"\n🔧 IMPROVEMENTS MADE:")
    print(f"   ✅ Downloaded VTA GTFS transit data (3,335 stops)")
    print(f"   ✅ Enhanced California transit dataset (87,722 unique stops)")
    print(f"   ✅ Updated config.json with new data paths")
    print(f"   ✅ Modified amenity analyzer to process transit stops")
    print(f"   ✅ Added transit classification (bus vs rail)")
    print(f"   📈 Result: {amenities['transit']['points_earned']} transit points earned!")
    
    print(f"\n📋 RECOMMENDATION:")
    print(f"   {results['recommendations']['overall_recommendation']}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    compare_analysis_results()