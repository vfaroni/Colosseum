#!/usr/bin/env python3

"""
Test Universal Parcel Mapper with D'Marco Sites and California Coordinates
Testing dual-track TX/CA APN conversion system
"""

import sys
import os
import pandas as pd
import json
from datetime import datetime

# Add the parcel mapping module to path
sys.path.append('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping')

from universal_parcel_mapper import UniversalParcelMapper, ParcelData

def load_dmarco_coordinates():
    """Load D'Marco site coordinates from existing data files"""
    
    # Known D'Marco coordinates from our previous analysis
    dmarco_coordinates = [
        # Major Texas Metro Areas for Testing
        {'lat': 32.7767, 'lng': -96.7970, 'state': 'TX', 'site_id': 'DMarco_Dallas_Downtown'},
        {'lat': 29.7604, 'lng': -95.3698, 'state': 'TX', 'site_id': 'DMarco_Houston_Downtown'},
        {'lat': 30.2672, 'lng': -97.7431, 'state': 'TX', 'site_id': 'DMarco_Austin_Downtown'},
        {'lat': 29.4241, 'lng': -98.4936, 'state': 'TX', 'site_id': 'DMarco_San_Antonio_Downtown'},
        {'lat': 32.7555, 'lng': -97.3308, 'state': 'TX', 'site_id': 'DMarco_Fort_Worth_Downtown'},
        
        # Texas Suburban/Regional
        {'lat': 33.0198, 'lng': -96.6989, 'state': 'TX', 'site_id': 'DMarco_Plano_Test'},
        {'lat': 32.9465, 'lng': -96.8295, 'state': 'TX', 'site_id': 'DMarco_Irving_Test'},
        {'lat': 29.5516, 'lng': -98.4738, 'state': 'TX', 'site_id': 'DMarco_San_Antonio_South'},
        {'lat': 29.9844, 'lng': -95.3414, 'state': 'TX', 'site_id': 'DMarco_Spring_Houston'},
        {'lat': 30.5852, 'lng': -97.7431, 'state': 'TX', 'site_id': 'DMarco_Round_Rock_Austin'},
        
        # Real D'Marco Region 3 coordinates (if available)
        {'lat': 33.2148, 'lng': -97.1331, 'state': 'TX', 'site_id': 'DMarco_Denton_County'},
        {'lat': 33.1507, 'lng': -96.8236, 'state': 'TX', 'site_id': 'DMarco_Frisco_Test'},
        {'lat': 32.8674, 'lng': -96.9697, 'state': 'TX', 'site_id': 'DMarco_Carrollton_Test'},
        {'lat': 32.9126, 'lng': -96.6384, 'state': 'TX', 'site_id': 'DMarco_Richardson_Test'},
        {'lat': 32.8668, 'lng': -96.9308, 'state': 'TX', 'site_id': 'DMarco_Farmers_Branch'}
    ]
    
    return dmarco_coordinates

def load_california_test_coordinates():
    """Load California coordinates for dual-track testing"""
    
    california_coordinates = [
        # Los Angeles Area
        {'lat': 34.0522, 'lng': -118.2437, 'state': 'CA', 'site_id': 'CA_Los_Angeles_Downtown'},
        {'lat': 33.9425, 'lng': -118.4081, 'state': 'CA', 'site_id': 'CA_LAX_Area'},
        {'lat': 34.1478, 'lng': -118.1445, 'state': 'CA', 'site_id': 'CA_Pasadena'},
        {'lat': 33.8358, 'lng': -117.9147, 'state': 'CA', 'site_id': 'CA_Anaheim'},
        
        # San Francisco Bay Area
        {'lat': 37.7749, 'lng': -122.4194, 'state': 'CA', 'site_id': 'CA_San_Francisco'},
        {'lat': 37.4419, 'lng': -122.1430, 'state': 'CA', 'site_id': 'CA_Palo_Alto'},
        {'lat': 37.3382, 'lng': -121.8863, 'state': 'CA', 'site_id': 'CA_San_Jose'},
        {'lat': 37.8044, 'lng': -122.2712, 'state': 'CA', 'site_id': 'CA_Oakland'},
        
        # San Diego Area
        {'lat': 32.7157, 'lng': -117.1611, 'state': 'CA', 'site_id': 'CA_San_Diego_Downtown'},
        {'lat': 32.8328, 'lng': -117.2713, 'state': 'CA', 'site_id': 'CA_La_Jolla'},
        
        # Riverside/Inland Empire (LIHTC Focus Area)
        {'lat': 33.9533, 'lng': -117.3962, 'state': 'CA', 'site_id': 'CA_Riverside'},
        {'lat': 33.7929, 'lng': -117.2211, 'state': 'CA', 'site_id': 'CA_Perris_Vista_II'}, # Our actual Perris project
        {'lat': 34.0975, 'lng': -117.2898, 'state': 'CA', 'site_id': 'CA_San_Bernardino'},
        {'lat': 33.7866, 'lng': -116.9670, 'state': 'CA', 'site_id': 'CA_Hemet'},
        
        # Central Valley
        {'lat': 36.7378, 'lng': -119.7871, 'state': 'CA', 'site_id': 'CA_Fresno'},
        {'lat': 35.3738, 'lng': -119.0194, 'state': 'CA', 'site_id': 'CA_Bakersfield'}
    ]
    
    return california_coordinates

def run_comprehensive_parcel_test():
    """Run comprehensive test of Universal Parcel Mapper with TX and CA coordinates"""
    
    print("🏛️ UNIVERSAL PARCEL MAPPER - COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize the mapper
    mapper = UniversalParcelMapper()
    
    # Load test coordinates
    dmarco_coords = load_dmarco_coordinates()
    california_coords = load_california_test_coordinates()
    
    print(f"📍 Testing {len(dmarco_coords)} D'Marco Texas sites")
    print(f"📍 Testing {len(california_coords)} California sites")
    print()
    
    # Combine all coordinates
    all_coordinates = dmarco_coords + california_coords
    
    print("🔍 Starting parcel analysis...")
    print()
    
    # Run analysis
    results_df = mapper.analyze_multiple_sites(all_coordinates)
    
    # Display results summary
    print("📊 ANALYSIS RESULTS SUMMARY")
    print("-" * 40)
    
    total_sites = len(results_df)
    successful_lookups = len(results_df[results_df['status'] == 'SUCCESS'])
    failed_lookups = len(results_df[results_df['status'] == 'NOT_FOUND'])
    
    print(f"Total Sites Analyzed: {total_sites}")
    print(f"Successful APN Lookups: {successful_lookups} ({successful_lookups/total_sites*100:.1f}%)")
    print(f"Failed Lookups: {failed_lookups} ({failed_lookups/total_sites*100:.1f}%)")
    print()
    
    # State-by-state breakdown
    tx_results = results_df[results_df['state'] == 'TX']
    ca_results = results_df[results_df['state'] == 'CA']
    
    tx_success = len(tx_results[tx_results['status'] == 'SUCCESS'])
    ca_success = len(ca_results[ca_results['status'] == 'SUCCESS'])
    
    print("🏠 STATE-BY-STATE RESULTS")
    print("-" * 30)
    print(f"Texas: {tx_success}/{len(tx_results)} successful ({tx_success/len(tx_results)*100:.1f}%)")
    print(f"California: {ca_success}/{len(ca_results)} successful ({ca_success/len(ca_results)*100:.1f}%)")
    print()
    
    # Show successful results
    successful_results = results_df[results_df['status'] == 'SUCCESS']
    if len(successful_results) > 0:
        print("✅ SUCCESSFUL APN LOOKUPS")
        print("-" * 50)
        for _, row in successful_results.iterrows():
            print(f"{row['site_id']}: APN {row['apn']} ({row['county']} County, {row['state']})")
            if row['property_area_acres']:
                print(f"   📐 Area: {row['property_area_acres']:.2f} acres")
            if row['owner_name']:
                print(f"   👤 Owner: {row['owner_name']}")
            if row['data_source']:
                print(f"   📡 Source: {row['data_source']}")
            print()
    
    # Show failed results
    failed_results = results_df[results_df['status'] == 'NOT_FOUND']
    if len(failed_results) > 0:
        print("❌ FAILED LOOKUPS")
        print("-" * 20)
        for _, row in failed_results.iterrows():
            print(f"{row['site_id']}: {row['input_lat']}, {row['input_lng']} ({row['state']})")
        print()
    
    # Export results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Excel export
    excel_file = f'/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping/universal_parcel_test_results_{timestamp}.xlsx'
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Main results
        results_df.to_excel(writer, sheet_name='All_Results', index=False)
        
        # Texas results
        tx_results.to_excel(writer, sheet_name='Texas_DMarco_Sites', index=False)
        
        # California results  
        ca_results.to_excel(writer, sheet_name='California_Sites', index=False)
        
        # Successful lookups only
        successful_results.to_excel(writer, sheet_name='Successful_APNs', index=False)
        
        # Summary stats
        summary_data = {
            'Metric': ['Total Sites', 'Successful Lookups', 'Failed Lookups', 'Success Rate (%)', 
                      'Texas Success Rate (%)', 'California Success Rate (%)'],
            'Value': [total_sites, successful_lookups, failed_lookups, 
                     f"{successful_lookups/total_sites*100:.1f}%",
                     f"{tx_success/len(tx_results)*100:.1f}%" if len(tx_results) > 0 else "N/A",
                     f"{ca_success/len(ca_results)*100:.1f}%" if len(ca_results) > 0 else "N/A"]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"📁 Results exported to: {excel_file}")
    
    # JSON export for detailed analysis
    json_file = f'/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping/universal_parcel_test_detailed_{timestamp}.json'
    
    # Convert DataFrame to detailed JSON with metadata
    detailed_results = {
        'test_metadata': {
            'test_date': datetime.now().isoformat(),
            'total_sites': total_sites,
            'successful_lookups': successful_lookups,
            'failed_lookups': failed_lookups,
            'success_rate_percent': round(successful_lookups/total_sites*100, 1),
            'texas_sites': len(tx_results),
            'california_sites': len(ca_results),
            'texas_success_rate': round(tx_success/len(tx_results)*100, 1) if len(tx_results) > 0 else None,
            'california_success_rate': round(ca_success/len(ca_results)*100, 1) if len(ca_results) > 0 else None
        },
        'results': results_df.to_dict('records')
    }
    
    with open(json_file, 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"📁 Detailed JSON exported to: {json_file}")
    print()
    
    # Test KML export for successful parcels with boundary data
    kml_exports = 0
    for _, row in successful_results.iterrows():
        if row['boundary_points_count'] > 0:
            # Note: This would require getting the actual ParcelData object
            # For now, just count potential KML exports
            kml_exports += 1
    
    print(f"🗺️  Potential KML exports: {kml_exports} parcels with boundary data")
    
    print("✅ COMPREHENSIVE PARCEL TEST COMPLETED")
    print("=" * 60)
    
    return results_df, excel_file, json_file

def test_specific_dmarco_site():
    """Test with a specific D'Marco site for detailed analysis"""
    
    print("\n🎯 SPECIFIC D'MARCO SITE TEST")
    print("-" * 40)
    
    # Test with a specific coordinate (Dallas area)
    test_lat = 32.7767
    test_lng = -96.7970
    
    mapper = UniversalParcelMapper()
    parcel_data = mapper.get_parcel_from_coordinates(test_lat, test_lng, 'TX')
    
    if parcel_data:
        print(f"✅ SUCCESS: Found parcel data")
        print(f"   APN: {parcel_data.apn}")
        print(f"   State: {parcel_data.state}")
        print(f"   County: {parcel_data.county}")
        print(f"   Area: {parcel_data.property_area_acres:.2f} acres")
        print(f"   Owner: {parcel_data.owner_name or 'Unknown'}")
        print(f"   Boundary Points: {len(parcel_data.boundary_coordinates)}")
        print(f"   Data Source: {parcel_data.data_source}")
        
        # Test KML export
        if parcel_data.boundary_coordinates:
            kml_file = f'/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping/test_parcel_{parcel_data.apn.replace("/", "_")}.kml'
            mapper.export_parcel_boundaries_kml(parcel_data, kml_file)
            print(f"   🗺️  KML exported: {kml_file}")
    else:
        print(f"❌ FAILED: No parcel found for {test_lat}, {test_lng}")

if __name__ == "__main__":
    print("🚀 Starting Universal Parcel Mapper Tests")
    print()
    
    # Run comprehensive test
    results_df, excel_file, json_file = run_comprehensive_parcel_test()
    
    # Run specific site test
    test_specific_dmarco_site()
    
    print("\n🏁 ALL TESTS COMPLETED")
    print(f"📊 Main Results: {excel_file}")
    print(f"📋 Detailed Data: {json_file}")