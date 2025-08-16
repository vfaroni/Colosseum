#!/usr/bin/env python3
"""
Test San Jacinto Vista II with all CTCAC mapping fixes
"""

from ctcac_amenity_mapper_complete import analyze_complete_site_by_address

def test_san_jacinto_vista_ii():
    """Test the San Jacinto Vista II project with all fixes"""
    
    print("Testing San Jacinto Vista II - CTCAC Compliant Map")
    print("=" * 60)
    
    # Project details
    project_name = "San Jacinto Vista II"
    project_address = "202 E. Jarvis St., Perris, CA 92570"
    
    # Analyze the site
    map_obj, results = analyze_complete_site_by_address(
        address=project_address,
        is_rural=False,
        project_type='at_risk',  # At-Risk project type
        qualifying_development=True,
        new_construction=False,  # At-Risk is existing
        large_family=True,
        site_name=project_name,
        project_address=project_address
    )
    
    if map_obj and results:
        # Save the map
        output_file = 'san_jacinto_vista_ii_ctcac_map.html'
        map_obj.save(output_file)
        
        print(f"\n✅ Map saved to: {output_file}")
        print(f"\n📊 CTCAC Score: {results['total_points']}/15 points")
        print("\n🎯 Key Features Implemented:")
        print("  • Distance scale on map")
        print("  • Distance markers on scoring circles")
        print("  • Project name and address displayed")
        print("  • Coordinates shown")
        print("  • 'Use Rural Dist?' instead of 'Rural'")
        print("  • Project type: At-Risk")
        print("  • Internet removed from legend")
        print("  • Better spacing between icon and text")
        print("  • Duplicate transit stops removed")
        
        # Show amenity summary
        print("\n📍 Amenities Found (within CTCAC distances):")
        for category, amenities in results['amenities_found'].items():
            if amenities:
                print(f"  • {category.replace('_', ' ').title()}: {len(amenities)} found")

if __name__ == "__main__":
    test_san_jacinto_vista_ii()