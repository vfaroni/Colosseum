#!/usr/bin/env python3
"""
Complete CTCAC Amenity Analysis Tool

Command-line interface for comprehensive CTCAC amenity scoring analysis
with all application categories included.

Usage Examples:
    # Basic analysis
    python3 complete_amenity_analysis.py "1000 N St, Sacramento, CA"
    python3 complete_amenity_analysis.py 38.7584 -121.2942
    
    # Family development with 25%+ 3BR units (qualifying development)
    python3 complete_amenity_analysis.py 38.7584 -121.2942 --family --qualifying
    
    # Rural senior development
    python3 complete_amenity_analysis.py 38.7584 -121.2942 --rural --senior
    
    # New construction large family in high resource area
    python3 complete_amenity_analysis.py 38.7584 -121.2942 --family --qualifying --new-construction --large-family --opportunity-area high
    
    # High density transit-oriented development
    python3 complete_amenity_analysis.py 38.7584 -121.2942 --family --qualifying --density 30
"""

import sys
import argparse
from ctcac_amenity_mapper_complete import CTCACAmenityMapperComplete, analyze_complete_site_by_address, analyze_complete_site_by_coordinates

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Complete CTCAC Amenity Analysis Tool - All Application Categories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "1000 N St, Sacramento, CA"
  %(prog)s 38.7584 -121.2942 --family --qualifying
  %(prog)s 38.7584 -121.2942 --rural --senior
  %(prog)s 38.7584 -121.2942 --family --qualifying --new-construction --large-family --opportunity-area high
        """
    )
    
    # Location input (required)
    parser.add_argument('location', nargs='+', 
                       help='Address (quoted string) or coordinates (lat lng)')
    
    # Project characteristics
    parser.add_argument('--rural', action='store_true',
                       help='Rural set-aside project (extends distance requirements)')
    
    parser.add_argument('--project-type', choices=['family', 'senior', 'special_needs'], 
                       default='family',
                       help='Project type (default: family)')
    
    # Legacy shortcuts for project types
    parser.add_argument('--family', action='store_const', dest='project_type', const='family',
                       help='Family housing project (default)')
    parser.add_argument('--senior', action='store_const', dest='project_type', const='senior',
                       help='Senior housing project')
    parser.add_argument('--special-needs', action='store_const', dest='project_type', const='special_needs',
                       help='Special needs housing project')
    
    # Development characteristics
    parser.add_argument('--qualifying', action='store_true',
                       help='Qualifying development (25%+ 3BR units for family housing)')
    
    parser.add_argument('--new-construction', action='store_true',
                       help='New construction project (required for opportunity area points)')
    
    parser.add_argument('--large-family', action='store_true',
                       help='Large family housing type (required for opportunity area points)')
    
    parser.add_argument('--density', type=float,
                       help='Units per acre (affects transit scoring if >25)')
    
    parser.add_argument('--opportunity-area', choices=['highest', 'high', 'moderate', 'low'],
                       help='CTCAC/HCD Opportunity Area designation')
    
    # Output options
    parser.add_argument('--output', '-o', default='complete_amenity_analysis_map.html',
                       help='Output HTML map filename (default: complete_amenity_analysis_map.html)')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output with detailed amenity lists')
    
    return parser.parse_args()

def print_comprehensive_results(results, args):
    """Print comprehensive analysis results"""
    print(f"\nCTCAC COMPLETE AMENITY SCORING ANALYSIS")
    print(f"{'=' * 60}")
    print(f"Total CTCAC Points: {results['total_points']}/{results['max_possible_points']}")
    print(f"Project Type: {results['project_type'].title()}")
    print(f"Rural Classification: {'Yes' if results['is_rural'] else 'No'}")
    print(f"Qualifying Development: {'Yes' if results.get('qualifying_development', False) else 'No'}")
    
    if args.density:
        print(f"Density: {args.density} units/acre")
    if args.opportunity_area:
        print(f"Opportunity Area: {args.opportunity_area.title()}")
    
    print(f"\nCOMPLETE SCORING BREAKDOWN:")
    print(f"{'-' * 40}")
    
    # Group scoring by implementation status
    implemented_categories = []
    placeholder_categories = []
    project_categories = []
    
    for category, scores in results['scoring_summary'].items():
        if isinstance(scores, dict):
            if 'note' in scores and ('placeholder' in scores['note'] or 'not available' in scores['note']):
                placeholder_categories.append((category, scores))
            elif 'note' in scores and 'Project amenity' in scores['note']:
                project_categories.append((category, scores))
            else:
                implemented_categories.append((category, scores))
        else:
            implemented_categories.append((category, scores))
    
    # Show implemented categories first
    if implemented_categories:
        print("IMPLEMENTED AMENITIES:")
        for category, scores in implemented_categories:
            if isinstance(scores, dict) and 'points' in scores:
                distance = scores.get('closest_distance')
                dist_str = f" (closest: {distance:.2f} mi)" if distance else ""
                print(f"  {category.replace('_', ' ').title()}: {scores['points']} points{dist_str}")
            elif category == 'schools':
                # Special handling for schools
                total_pts = sum([v for v in scores.values() if isinstance(v, (int, float))])
                print(f"  Schools: {total_pts} points total")
                for subcat, pts in scores.items():
                    if isinstance(pts, (int, float)) and pts > 0:
                        print(f"    • {subcat.replace('_', ' ').title()}: {pts} points")
            elif category == 'opportunity_area':
                points = scores.get('points', 0)
                status = scores.get('status', 'not_applicable')
                print(f"  Opportunity Area: {points} points ({status.replace('_', ' ').title()})")
    
    # Show placeholder categories
    if placeholder_categories:
        print(f"\nNOT YET IMPLEMENTED (Placeholders):")
        for category, scores in placeholder_categories:
            print(f"  {category.replace('_', ' ').title()}: {scores['points']} points - {scores.get('note', '')}")
    
    # Show project-specific categories
    if project_categories:
        print(f"\nPROJECT-SPECIFIC AMENITIES:")
        for category, scores in project_categories:
            print(f"  {category.replace('_', ' ').title()}: {scores['points']} points - {scores.get('note', '')}")
    
    # Show amenities found if verbose
    if args.verbose:
        print(f"\nAMENITIES FOUND (Verbose Mode):")
        print(f"{'-' * 40}")
        
        for category, amenities in results['amenities_found'].items():
            if amenities:
                print(f"\n{category.replace('_', ' ').title()} ({len(amenities)} found):")
                # Show closest 10 amenities
                sorted_amenities = sorted(amenities, key=lambda x: x.get('distance_miles', 999))[:10]
                for amenity in sorted_amenities:
                    name = amenity.get('name', 'Unknown')
                    distance = amenity.get('distance_miles', 0)
                    amenity_type = amenity.get('amenity_type', '')
                    print(f"  • {name} ({amenity_type}): {distance:.2f} miles")
                
                if len(amenities) > 10:
                    print(f"  ... and {len(amenities) - 10} more")
    else:
        # Show summary counts
        print(f"\nAMENITY SUMMARY:")
        print(f"{'-' * 40}")
        for category, amenities in results['amenities_found'].items():
            if amenities:
                closest_distance = min(a.get('distance_miles', 999) for a in amenities)
                print(f"{category.replace('_', ' ').title()}: {len(amenities)} found (closest: {closest_distance:.2f} mi)")

def main():
    args = parse_arguments()
    
    print("CTCAC Complete Amenity Analysis Tool")
    print("===================================")
    
    # Parse location input
    if len(args.location) == 1:
        # Address provided
        address = args.location[0]
        
        print(f"Analyzing address: {address}")
        print_analysis_params(args)
        print("=" * 60)
        
        map_obj, results = analyze_complete_site_by_address(
            address, 
            is_rural=args.rural,
            project_type=args.project_type,
            qualifying_development=args.qualifying,
            new_construction=args.new_construction,
            large_family=args.large_family,
            opportunity_area_status=args.opportunity_area
        )
        
    elif len(args.location) == 2:
        # Coordinates provided
        try:
            lat = float(args.location[0])
            lng = float(args.location[1])
            site_name = f"Site at {lat:.6f}, {lng:.6f}"
            
            print(f"Analyzing coordinates: {lat}, {lng}")
            print_analysis_params(args)
            print("=" * 60)
            
            map_obj, results = analyze_complete_site_by_coordinates(
                lat, lng, site_name,
                is_rural=args.rural,
                project_type=args.project_type,
                qualifying_development=args.qualifying,
                new_construction=args.new_construction,
                large_family=args.large_family,
                opportunity_area_status=args.opportunity_area
            )
            
        except ValueError:
            print("Error: Invalid coordinates provided")
            sys.exit(1)
    else:
        print("Error: Invalid location format")
        print("Provide either: 'Address' or lat lng")
        sys.exit(1)
    
    if map_obj is None:
        print("Analysis failed")
        sys.exit(1)
    
    # Save map
    map_obj.save(args.output)
    
    # Print results
    print_comprehensive_results(results, args)
    
    print(f"\nInteractive map saved to: {args.output}")
    print("Open this file in a web browser to view the complete amenity analysis.")
    
    # Show missing data recommendations
    print(f"\nDATA EXPANSION RECOMMENDATIONS:")
    print(f"{'-' * 40}")
    print("To achieve full 15-point potential, add these datasets:")
    print("• Transit data (GTFS feeds) - up to 7 points")
    print("• Public parks/recreation data - up to 3 points")  
    print("• Grocery store/supermarket data - up to 5 points")
    print("• Geocoded medical facilities - up to 3 points")
    print("• High-speed internet commitment - up to 3 points (rural)")

def print_analysis_params(args):
    """Print analysis parameters"""
    print(f"Project type: {args.project_type}")
    print(f"Rural status: {args.rural}")
    print(f"Qualifying development: {args.qualifying}")
    if args.new_construction:
        print(f"New construction: Yes")
    if args.large_family:
        print(f"Large family housing: Yes")
    if args.density:
        print(f"Density: {args.density} units/acre")
    if args.opportunity_area:
        print(f"Opportunity area: {args.opportunity_area}")

if __name__ == "__main__":
    main()