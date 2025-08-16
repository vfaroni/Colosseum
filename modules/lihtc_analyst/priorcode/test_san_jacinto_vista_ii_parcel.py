#!/usr/bin/env python3
"""
Test San Jacinto Vista II with Parcel Boundary Enhancement
Uses actual parcel corners to calculate distances from parcel edges
"""

from ctcac_parcel_boundary_mapper import analyze_site_with_parcel_boundary

def test_san_jacinto_vista_ii_with_parcel():
    """Test the San Jacinto Vista II project with parcel boundary calculations"""
    
    print("Testing San Jacinto Vista II - Parcel Boundary Enhanced Map")
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
    
    # Calculate parcel dimensions (approximate)
    # North edge length
    north_edge_miles = 0.0867  # Approximate based on coordinates
    # West edge length  
    west_edge_miles = 0.1128   # Approximate based on coordinates
    acres = north_edge_miles * west_edge_miles * 640  # Convert sq miles to acres
    print(f"\nApproximate parcel area: {acres:.2f} acres")
    
    # Analyze the site with parcel boundaries
    map_obj, results = analyze_site_with_parcel_boundary(
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
        # Save the enhanced map
        output_file = 'san_jacinto_vista_ii_parcel_enhanced_map.html'
        map_obj.save(output_file)
        
        print(f"\n✅ Enhanced map saved to: {output_file}")
        print(f"\n📊 CTCAC Score: {results['total_points']}/15 points")
        print("\n🎯 New Features Implemented:")
        print("  • Parcel boundary drawn on map")
        print("  • Distance circles measured from parcel edges")
        print("  • 1/3 mile reference circle added")
        print("  • Amenity distances recalculated from nearest parcel edge")
        print("  • Corner markers (NW, NE, SW, SE) displayed")
        print("  • All existing amenity data preserved")
        
        # Show amenity summary with edge distances
        print("\n📍 Amenities Found (distances from parcel boundary):")
        for category, amenities in results['amenities_found'].items():
            if amenities:
                # Find closest amenity by edge distance
                closest = min(amenities, key=lambda x: x.get('distance_miles', 999))
                edge_dist = closest.get('distance_miles', 0)
                center_dist = closest.get('distance_miles_from_center', 0)
                
                print(f"\n  • {category.replace('_', ' ').title()}: {len(amenities)} found")
                print(f"    - Closest from edge: {edge_dist:.3f} miles")
                print(f"    - (Was {center_dist:.3f} miles from center)")
                
                # Show improvement
                if center_dist > edge_dist:
                    improvement = center_dist - edge_dist
                    print(f"    - ✅ {improvement:.3f} miles closer using parcel boundary!")
        
        print("\n📏 Distance Calculation Method:")
        print("  • Old method: All distances from parcel center point")
        print("  • New method: Distances from nearest parcel boundary")
        print("  • Result: More accurate CTCAC compliance assessment")
        
        return map_obj, results
    else:
        print("\n❌ Error creating enhanced map")
        return None, None

if __name__ == "__main__":
    test_san_jacinto_vista_ii_with_parcel()