#!/usr/bin/env python3
"""
Test San Jacinto Vista II with Complete Custom Data
Uses actual parcel corners plus custom parks and pharmacies
"""

from ctcac_san_jacinto_custom_mapper import analyze_san_jacinto_with_custom_data

def test_san_jacinto_vista_ii_complete():
    """Test the San Jacinto Vista II project with complete custom data"""
    
    print("Testing San Jacinto Vista II - Complete Custom Data Map")
    print("=" * 60)
    
    # Project details
    project_name = "San Jacinto Vista II"
    project_address = "202 E. Jarvis St., Perris, CA 92570"
    
    # Parcel corner coordinates (from Google Maps)
    parcel_corners = {
        'nw': (33.79377, -117.22184),  # Northwest corner
        'ne': (33.79376, -117.22050),  # Northeast corner  
        'sw': (33.79213, -117.22173),  # Southwest corner
        'se': (33.79211, -117.22048)   # Southeast corner
    }
    
    print("\nParcel Corner Coordinates:")
    for corner, coords in parcel_corners.items():
        print(f"  {corner.upper()}: {coords[0]:.6f}, {coords[1]:.6f}")
    
    print("\nCustom Data Included:")
    print("  Parks (4): SkyDive Baseball Park, Bob Long Park, Panther Park, Metz Park")
    print("  Pharmacies (4): Walmart Pharmacy, Nuevo Pharmacy, Rite Aid, Smart Care & Pharmacy")
    
    # Analyze the site with custom data
    map_obj, results = analyze_san_jacinto_with_custom_data(
        parcel_corners=parcel_corners,
        address=project_address,
        is_rural=False,
        project_type='at_risk',  # At-Risk project type
        qualifying_development=True,
        new_construction=False,  # At-Risk is existing
        large_family=True,
        site_name=project_name
    )
    
    if map_obj and results:
        # Save the complete map
        output_file = 'san_jacinto_vista_ii_complete_custom_map.html'
        map_obj.save(output_file)
        
        print(f"\n✅ Complete custom map saved to: {output_file}")
        print(f"\n📊 CTCAC Score: {results['total_points']}/15 points")
        print("\n🎯 Complete Features:")
        print("  • Parcel boundary with corner markers")
        print("  • Distance circles: 0.25, 1/3, 0.5, 1.0 mile from parcel edges")
        print("  • Custom parks data (4 parks)")
        print("  • Custom pharmacy data (4 pharmacies)")
        print("  • All existing amenity data preserved")
        print("  • Distances from nearest parcel boundary")
        
        # Show complete amenity summary
        print("\n📍 Complete Amenities Found (distances from parcel boundary):")
        for category, amenities in results['amenities_found'].items():
            if amenities:
                # Find closest amenity by edge distance
                closest = min(amenities, key=lambda x: x.get('distance_miles', 999))
                edge_dist = closest.get('distance_miles', 0)
                closest_name = closest.get('name', 'Unknown')
                
                print(f"\n  • {category.replace('_', ' ').title()}: {len(amenities)} found")
                print(f"    - Closest: {closest_name} at {edge_dist:.3f} miles")
                
                # Show all amenities for parks and pharmacies
                if category in ['public_parks', 'pharmacies'] and len(amenities) <= 6:
                    for amenity in sorted(amenities, key=lambda x: x.get('distance_miles', 999)):
                        name = amenity.get('name', 'Unknown')
                        dist = amenity.get('distance_miles', 0)
                        print(f"      - {name}: {dist:.3f} miles")
        
        # Calculate potential scoring improvements
        park_points = results.get('parks_score', {}).get('points', 0)
        pharmacy_points = results.get('pharmacy_score', {}).get('points', 0)
        
        print(f"\n📈 Custom Data Impact:")
        print(f"  • Parks Score: {park_points} points (was 0)")
        print(f"  • Pharmacy Score: {pharmacy_points} points (was 0)")
        
        if park_points > 0 or pharmacy_points > 0:
            print(f"  • ✅ Total improvement: +{park_points + pharmacy_points} points!")
        
        return map_obj, results
    else:
        print("\n❌ Error creating complete custom map")
        return None, None

if __name__ == "__main__":
    test_san_jacinto_vista_ii_complete()