#!/usr/bin/env python3
"""
Test Enhanced CTCAC Amenity Mapping System
Demonstrates improved symbols, legends, and numbered markers
"""

from ctcac_amenity_mapper_complete import CTCACAmenityMapperComplete

def test_enhanced_mapping():
    """Test the enhanced mapping system with detailed legend and numbered markers"""
    
    print("🏆 Testing Enhanced CTCAC Amenity Mapping System")
    print("=" * 60)
    
    # Initialize mapper
    mapper = CTCACAmenityMapperComplete()
    
    # Test site: Perris, CA (family development)
    test_sites = [
        {
            'name': 'Perris Family Development',
            'lat': 33.792954,
            'lng': -117.221031,
            'project_type': 'family',
            'qualifying_development': True,
            'new_construction': True,
            'large_family': True,
            'filename': 'enhanced_perris_family_map.html'
        },
        {
            'name': 'Sacramento Urban Site',
            'lat': 38.7584,
            'lng': -121.2942,
            'project_type': 'family',
            'qualifying_development': True,
            'new_construction': False,
            'large_family': False,
            'filename': 'enhanced_sacramento_urban_map.html'
        }
    ]
    
    for site in test_sites:
        print(f"\n🎯 Analyzing: {site['name']}")
        print(f"   Coordinates: {site['lat']:.6f}, {site['lng']:.6f}")
        print(f"   Type: {site['project_type'].title()}")
        
        # Create enhanced map
        map_obj, results = mapper.create_complete_amenity_map(
            site['lat'], site['lng'],
            site_name=site['name'],
            is_rural=False,
            project_type=site['project_type'],
            qualifying_development=site['qualifying_development'],
            new_construction=site['new_construction'],
            large_family=site['large_family']
        )
        
        # Save enhanced map
        map_obj.save(site['filename'])
        
        print(f"   ✅ Total Score: {results['total_points']}/15 CTCAC Points")
        print(f"   📍 Map saved: {site['filename']}")
        
        # Show amenity counts by category
        amenity_counts = {}
        for category, amenities in results['amenities_found'].items():
            if amenities:
                amenity_counts[category] = len(amenities)
        
        if amenity_counts:
            print("   📊 Amenities Found:")
            for category, count in amenity_counts.items():
                print(f"      • {category.replace('_', ' ').title()}: {count}")
    
    print(f"\n🎉 Enhanced Mapping Features Demonstrated:")
    print("   ✅ Numbered markers (#1, #2, etc.) for easy identification")
    print("   ✅ Category-specific symbols and colors")
    print("   ✅ Detailed legend with [Amenity]-[Name] ([distance])")
    print("   ✅ Professional styling and tooltips")
    print("   ✅ Enhanced popup information")
    print("   ✅ Scrollable legend for large datasets")
    print("   ✅ Visual distinction between amenity types")
    
    print(f"\n📋 Map Format: [Amenity]-[Name] ([distance to 1 decimal place])")
    print("   Example: #1 School-Palms Elementary (0.3 mi)")
    print("   Example: #2 Medical-Riverside Medical Center (1.2 mi)")

if __name__ == "__main__":
    test_enhanced_mapping()