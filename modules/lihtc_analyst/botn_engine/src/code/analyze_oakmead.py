#!/usr/bin/env python3
"""
Analyze site at 1205 Oakmead Parkway, Sunnyvale CA 94085
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.site_analyzer import SiteAnalyzer

# Geocoding using standard service (or we can use known coordinates for Sunnyvale)
# Sunnyvale is in Santa Clara County, coordinates approximately:
# Based on Sunnyvale's general location
OAKMEAD_LAT = 37.3897
OAKMEAD_LON = -121.9927

def analyze_oakmead_site():
    """Analyze the Oakmead Parkway site"""
    print("=" * 80)
    print("LIHTC Site Analysis: 1205 Oakmead Parkway, Sunnyvale CA 94085")
    print("=" * 80)
    
    # Initialize analyzer
    analyzer = SiteAnalyzer()
    
    # Analyze the site
    print(f"\nAnalyzing site at coordinates: {OAKMEAD_LAT}, {OAKMEAD_LON}")
    print("Analysis in progress...")
    
    try:
        result = analyzer.analyze_site(
            latitude=OAKMEAD_LAT,
            longitude=OAKMEAD_LON,
            state='CA',
            project_type='family',
            include_detailed_amenities=True
        )
        
        # Display results
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        
        # Site Information
        print("\nSITE INFORMATION:")
        print(f"  Address: 1205 Oakmead Parkway, Sunnyvale CA 94085")
        print(f"  Coordinates: {result.site_info.latitude}, {result.site_info.longitude}")
        print(f"  State: {result.site_info.state}")
        print(f"  Project Type: family")
        
        # Federal Status
        print("\nFEDERAL STATUS:")
        federal = result.federal_status
        print(f"  QCT Qualified: {federal.get('qct_qualified', 'Unknown')}")
        print(f"  DDA Qualified: {federal.get('dda_qualified', 'Unknown')}")
        if federal.get('qct_qualified') or federal.get('dda_qualified'):
            print("  ✅ Eligible for 30% basis boost")
        
        # State Scoring
        print("\nCALIFORNIA (CTCAC) SCORING:")
        scoring = result.state_scoring
        print(f"  Total Points: {scoring.get('total_points', 'Unknown')}")
        print(f"  Opportunity Area Points: {scoring.get('opportunity_area_points', 0)}")
        print(f"  Transit (HQTA) Points: {scoring.get('hqta_points', 0)}")
        print(f"  Federal Bonus Points: {scoring.get('federal_bonus_points', 0)}")
        
        # Amenity Analysis
        print("\nAMENITY ANALYSIS:")
        if 'amenities' in result.amenity_analysis:
            amenities = result.amenity_analysis['amenities']
            total_amenity_points = 0
            for amenity_type, data in amenities.items():
                points = data.get('points', 0)
                distance = data.get('distance', 'Unknown')
                count = data.get('count', 0)
                total_amenity_points += points
                if points > 0:
                    print(f"  {amenity_type.replace('_', ' ').title()}: {points} points")
                    print(f"    - Distance: {distance} miles")
                    print(f"    - Count: {count}")
            print(f"  Total Amenity Points: {total_amenity_points}")
        
        # Recommendations
        print("\nRECOMMENDATIONS:")
        recommendations = result.recommendations
        print(f"  Overall: {recommendations.get('overall_recommendation', 'Unknown')}")
        if 'strengths' in recommendations:
            print("  Strengths:")
            for strength in recommendations['strengths']:
                print(f"    - {strength}")
        if 'weaknesses' in recommendations:
            print("  Weaknesses:")
            for weakness in recommendations['weaknesses']:
                print(f"    - {weakness}")
        
        # Export results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"outputs/Oakmead_Parkway_1205_Analysis_{timestamp}.json"
        
        print(f"\nExporting detailed results to: {output_path}")
        analyzer.export_analysis(result, output_path, format='json')
        
        print("\n" + "=" * 80)
        print("Analysis completed successfully!")
        print("=" * 80)
        
        return result
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    analyze_oakmead_site()