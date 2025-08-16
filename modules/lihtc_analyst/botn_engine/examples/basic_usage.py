#!/usr/bin/env python3
"""
Basic Usage Examples for LIHTC Site Scorer

This file demonstrates how to use the LIHTC Site Scorer for common tasks.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.site_analyzer import SiteAnalyzer

def example_single_site_analysis():
    """Example: Analyze a single site"""
    print("=" * 60)
    print("EXAMPLE 1: Single Site Analysis")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = SiteAnalyzer()
    
    # Analyze the Simi Valley site we worked on
    print("Analyzing Simi Valley site...")
    result = analyzer.analyze_site(
        latitude=34.282556,
        longitude=-118.708943,
        state='CA',
        project_type='family'
    )
    
    # Print basic results
    print(f"Site: {result.site_info.latitude}, {result.site_info.longitude}")
    print(f"State: {result.site_info.state}")
    print(f"QCT Qualified: {result.federal_status.get('qct_qualified', 'Unknown')}")
    print(f"Total Points: {result.state_scoring.get('total_points', 'Unknown')}")
    print(f"Recommendation: {result.recommendations.get('overall_recommendation', 'Unknown')}")
    
    return result

def example_batch_analysis():
    """Example: Analyze multiple sites"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Batch Site Analysis")
    print("=" * 60)
    
    analyzer = SiteAnalyzer()
    
    # Define multiple sites
    sites = [
        (34.282556, -118.708943),  # Simi Valley, CA
        (34.0522, -118.2437),     # Los Angeles, CA  
        (37.7749, -122.4194),     # San Francisco, CA
        (30.2672, -97.7431),      # Austin, TX
        (40.7128, -74.0060)       # New York, NY
    ]
    
    print(f"Analyzing {len(sites)} sites...")
    
    # Note: In real usage, this would make actual API calls
    # For this example, we'll simulate the process
    for i, (lat, lon) in enumerate(sites, 1):
        print(f"Site {i}: Analyzing {lat}, {lon}")
        try:
            result = analyzer.analyze_site(lat, lon)
            print(f"  ✅ Analysis completed")
        except Exception as e:
            print(f"  ❌ Analysis failed: {str(e)}")
    
    print("Batch analysis completed!")

def example_export_results():
    """Example: Export analysis results"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Export Analysis Results")
    print("=" * 60)
    
    analyzer = SiteAnalyzer()
    
    # Analyze a site
    result = analyzer.analyze_site(
        latitude=34.282556,
        longitude=-118.708943,
        state='CA'
    )
    
    # Export in different formats
    output_dir = Path("outputs/examples")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # JSON export
        analyzer.export_analysis(
            result, 
            str(output_dir / "simi_valley_analysis.json"), 
            format='json'
        )
        print("✅ JSON export completed")
        
        # Excel export (if implemented)
        analyzer.export_analysis(
            result,
            str(output_dir / "simi_valley_analysis.xlsx"),
            format='excel'
        )
        print("✅ Excel export completed")
        
        # PDF export (if implemented)
        analyzer.export_analysis(
            result,
            str(output_dir / "simi_valley_analysis.pdf"), 
            format='pdf'
        )
        print("✅ PDF export completed")
        
    except Exception as e:
        print(f"❌ Export failed: {str(e)}")

def example_california_specific():
    """Example: California (CTCAC) specific analysis"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: California (CTCAC) Specific Analysis")
    print("=" * 60)
    
    analyzer = SiteAnalyzer()
    
    # Analyze with detailed amenity scoring
    result = analyzer.analyze_site(
        latitude=34.282556,
        longitude=-118.708943,
        state='CA',
        project_type='family',
        include_detailed_amenities=True
    )
    
    print("CTCAC Amenity Scoring:")
    if 'amenities' in result.amenity_analysis:
        for amenity, data in result.amenity_analysis['amenities'].items():
            points = data.get('points', 0)
            distance = data.get('distance', 'Unknown')
            print(f"  {amenity.title()}: {points} points (distance: {distance} mi)")
    
    print(f"\nOpportunity Area Status:")
    opp_status = result.state_scoring.get('opportunity_area_points', 0)
    print(f"  Additional Points: {opp_status}")
    
    print(f"\nFederal Benefits:")
    federal = result.federal_status
    if federal.get('qct_qualified'):
        print("  ✅ QCT Qualified - 30% basis boost available")
    if federal.get('dda_qualified'):
        print("  ✅ DDA Qualified - 30% basis boost available")

def example_different_project_types():
    """Example: Analysis for different project types"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Different Project Types")
    print("=" * 60)
    
    analyzer = SiteAnalyzer()
    
    # Same coordinates, different project types
    lat, lon = 34.282556, -118.708943
    
    project_types = ['family', 'senior', 'special_needs']
    
    for project_type in project_types:
        print(f"\nAnalyzing as {project_type} development:")
        try:
            result = analyzer.analyze_site(
                latitude=lat,
                longitude=lon,
                state='CA',
                project_type=project_type
            )
            
            total_points = result.state_scoring.get('total_points', 'Unknown')
            print(f"  Total Points: {total_points}")
            
            # Project-specific amenities might be different
            if project_type == 'senior':
                print("  Senior-specific amenities considered")
            elif project_type == 'special_needs':
                print("  Special needs facilities considered")
            
        except Exception as e:
            print(f"  ❌ Analysis failed: {str(e)}")

def example_error_handling():
    """Example: Proper error handling"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Error Handling")
    print("=" * 60)
    
    analyzer = SiteAnalyzer()
    
    # Test various error conditions
    test_cases = [
        (91.0, -118.0, "Invalid latitude (>90)"),
        (34.0, 181.0, "Invalid longitude (>180)"),
        (34.0, -118.0, "Valid coordinates")
    ]
    
    for lat, lon, description in test_cases:
        print(f"\nTesting: {description}")
        try:
            result = analyzer.analyze_site(lat, lon)
            print("  ✅ Analysis successful")
        except ValueError as e:
            print(f"  ❌ Validation error: {str(e)}")
        except Exception as e:
            print(f"  ❌ Analysis error: {str(e)}")

def main():
    """Run all examples"""
    print("LIHTC Site Scorer - Usage Examples")
    print("Note: These examples may use mock data in development")
    
    try:
        example_single_site_analysis()
        example_batch_analysis()
        example_export_results()
        example_california_specific()
        example_different_project_types()
        example_error_handling()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("Check the outputs/ directory for exported files")
        print("=" * 60)
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()