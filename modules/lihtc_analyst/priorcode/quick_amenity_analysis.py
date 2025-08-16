#!/usr/bin/env python3
"""
Quick CTCAC Amenity Analysis Tool

Simple command-line interface for analyzing CTCAC amenity scoring
for a specific address or coordinates.

Usage:
    python3 quick_amenity_analysis.py "123 Main St, Sacramento, CA"
    python3 quick_amenity_analysis.py 38.7584 -121.2942
"""

import sys
from ctcac_amenity_mapper import CTCACAmenityMapper, analyze_site_by_address, analyze_site_by_coordinates

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  By address: python3 quick_amenity_analysis.py '123 Main St, Sacramento, CA'")
        print("  By coordinates: python3 quick_amenity_analysis.py 38.7584 -121.2942")
        print("  With options: python3 quick_amenity_analysis.py 38.7584 -121.2942 --rural --senior")
        return
    
    # Parse arguments
    is_rural = '--rural' in sys.argv
    project_type = 'family'  # default
    
    if '--senior' in sys.argv:
        project_type = 'senior'
    elif '--special' in sys.argv:
        project_type = 'special_needs'
    
    # Determine if input is address or coordinates
    if len(sys.argv) >= 3 and sys.argv[1].replace('.', '').replace('-', '').isdigit():
        # Coordinates provided
        try:
            lat = float(sys.argv[1])
            lng = float(sys.argv[2])
            site_name = f"Site at {lat:.6f}, {lng:.6f}"
            
            print(f"Analyzing coordinates: {lat}, {lng}")
            print(f"Project type: {project_type}")
            print(f"Rural status: {is_rural}")
            print("=" * 50)
            
            map_obj, results = analyze_site_by_coordinates(lat, lng, site_name, is_rural, project_type)
            
        except ValueError:
            print("Invalid coordinates provided")
            return
    else:
        # Address provided
        address = sys.argv[1]
        
        print(f"Analyzing address: {address}")
        print(f"Project type: {project_type}")
        print(f"Rural status: {is_rural}")
        print("=" * 50)
        
        map_obj, results = analyze_site_by_address(address, is_rural, project_type)
    
    if map_obj is None:
        print("Analysis failed")
        return
    
    # Save map
    output_file = "amenity_analysis_map.html"
    map_obj.save(output_file)
    
    # Print detailed results
    print(f"\nCTCAC AMENITY SCORING ANALYSIS")
    print(f"{'=' * 50}")
    print(f"Total CTCAC Points: {results['total_points']}")
    print(f"Project Type: {results['project_type'].title()}")
    print(f"Rural Classification: {'Yes' if results['is_rural'] else 'No'}")
    
    print(f"\nDETAILED SCORING:")
    print(f"{'-' * 30}")
    
    for category, scores in results['scoring_summary'].items():
        if isinstance(scores, dict):
            if 'points' in scores:
                distance = scores.get('closest_distance')
                dist_str = f" (closest: {distance:.2f} mi)" if distance else ""
                print(f"{category.title()}: {scores['points']} points{dist_str}")
            else:
                # Schools scoring (has sub-categories)
                total_pts = sum(scores.values())
                print(f"{category.title()}: {total_pts} points total")
                for subcat, pts in scores.items():
                    if pts > 0:
                        print(f"  - {subcat.title()}: {pts} points")
    
    print(f"\nAMENITIES FOUND:")
    print(f"{'-' * 30}")
    
    for category, amenities in results['amenities_found'].items():
        if amenities:
            print(f"\n{category.title()} ({len(amenities)} found):")
            # Show closest 5 amenities
            sorted_amenities = sorted(amenities, key=lambda x: x.get('distance_miles', 999))[:5]
            for amenity in sorted_amenities:
                name = amenity.get('name', amenity.get('School Name', 'Unknown'))
                distance = amenity.get('distance_miles', 0)
                print(f"  - {name}: {distance:.2f} miles")
            
            if len(amenities) > 5:
                print(f"  ... and {len(amenities) - 5} more")
    
    print(f"\nMap saved to: {output_file}")
    print("Open this file in a web browser to view the interactive map.")

if __name__ == "__main__":
    main()