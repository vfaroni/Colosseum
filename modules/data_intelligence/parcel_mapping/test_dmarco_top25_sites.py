#!/usr/bin/env python3

"""
Test Universal Parcel Mapper with D'Marco Top 25 Investment-Ready Sites
Extract real coordinates and attempt APN/parcel boundary extraction
"""

import sys
import os
import pandas as pd
import json
from datetime import datetime

# Add the parcel mapping module to path
sys.path.append('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping')

from universal_parcel_mapper import UniversalParcelMapper, ParcelData

def load_dmarco_top25_sites():
    """Load D'Marco Top 25 Investment-Ready sites from the Excel file sent at 12:20 AM"""
    
    file_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/Sent_to_D'Marco/ENHANCED_CENSUS_ANALYSIS_20250801_235158._Sentxlsx.xlsx"
    
    try:
        # Read the Top 25 sheet
        df = pd.read_excel(file_path, sheet_name='Top_25_Investment_Ready')
        
        print(f"📊 Loaded {len(df)} D'Marco Top 25 Investment-Ready Sites")
        print(f"📍 Available columns: {list(df.columns)}")
        print()
        
        # Extract coordinates and create test list
        dmarco_coordinates = []
        
        for index, row in df.iterrows():
            # Create site identifier
            address = str(row.get('Address', f'Site_{index+1}')).strip()
            city = str(row.get('City', 'Unknown')).strip()
            site_id = f"DMarco_Top25_{index+1:02d}_{city.replace(' ', '_')}_{address[:20].replace(' ', '_').replace(',', '')}"
            
            coord_data = {
                'lat': float(row['Latitude']),
                'lng': float(row['Longitude']),
                'state': 'TX',  # All D'Marco sites are Texas
                'site_id': site_id,
                'original_address': address,
                'city': city,
                'acres': row.get('Acres_Calculated', row.get('Calculated_Acres', 0)),
                'population': row.get('Census_Total_Population', 0)
            }
            
            dmarco_coordinates.append(coord_data)
        
        return dmarco_coordinates
        
    except Exception as e:
        print(f"❌ Error loading D'Marco sites: {str(e)}")
        return []

def test_dmarco_sites_for_parcel_boundaries():
    """Test D'Marco Top 25 sites with Universal Parcel Mapper to extract APN and boundary coordinates"""
    
    print("🏛️ D'MARCO TOP 25 SITES - PARCEL BOUNDARY EXTRACTION TEST")
    print("=" * 70)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load D'Marco sites
    dmarco_sites = load_dmarco_top25_sites()
    
    if not dmarco_sites:
        print("❌ Failed to load D'Marco sites")
        return None, None, None
    
    print(f"🎯 Testing {len(dmarco_sites)} D'Marco Top 25 Investment-Ready sites")
    print("🔍 Attempting real APN lookup and parcel boundary extraction...")
    print()
    
    # Initialize Universal Parcel Mapper
    mapper = UniversalParcelMapper()
    
    # Test all sites
    results_df = mapper.analyze_multiple_sites(dmarco_sites)
    
    # Analysis results
    total_sites = len(results_df)
    successful_lookups = len(results_df[results_df['status'] == 'SUCCESS'])
    failed_lookups = len(results_df[results_df['status'] == 'NOT_FOUND'])
    
    print("📊 D'MARCO TOP 25 PARCEL ANALYSIS RESULTS")
    print("-" * 50)
    print(f"Total D'Marco Sites: {total_sites}")
    print(f"Successful APN Lookups: {successful_lookups} ({successful_lookups/total_sites*100:.1f}%)")
    print(f"Failed Lookups: {failed_lookups} ({failed_lookups/total_sites*100:.1f}%)")
    print()
    
    # Show successful results with boundary data
    successful_results = results_df[results_df['status'] == 'SUCCESS']
    boundary_available = len(successful_results[successful_results['boundary_points_count'] > 0])
    
    if len(successful_results) > 0:
        print("✅ SUCCESSFUL D'MARCO APN LOOKUPS")
        print("-" * 40)
        for _, row in successful_results.iterrows():
            print(f"🏢 {row['site_id']}")
            print(f"   📍 Location: {row['input_lat']:.6f}, {row['input_lng']:.6f}")
            print(f"   🏛️ APN: {row['apn']} ({row['county']} County)")
            if row['property_area_acres']:
                print(f"   📐 Area: {row['property_area_acres']:.2f} acres")
            if row['owner_name']:
                print(f"   👤 Owner: {row['owner_name']}")
            if row['boundary_points_count'] > 0:
                print(f"   🗺️ Boundary Points: {row['boundary_points_count']} coordinates AVAILABLE")
            else:
                print(f"   🗺️ Boundary Points: No boundary data available")
            print(f"   📡 Source: {row['data_source']}")
            print()
    
    print(f"🗺️ PARCEL BOUNDARY DATA AVAILABILITY")
    print("-" * 40)
    print(f"Properties with Boundary Coordinates: {boundary_available}/{successful_lookups}")
    if successful_lookups > 0:
        print(f"Boundary Data Success Rate: {boundary_available/successful_lookups*100:.1f}%")
    print()
    
    # Show failed results
    failed_results = results_df[results_df['status'] == 'NOT_FOUND']
    if len(failed_results) > 0:
        print("❌ FAILED D'MARCO LOOKUPS")
        print("-" * 30)
        for _, row in failed_results.iterrows():
            print(f"{row['site_id']}: {row['input_lat']:.6f}, {row['input_lng']:.6f}")
        print()
    
    # Export results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Excel export with detailed analysis
    excel_file = f'/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping/DMarco_Top25_Parcel_Analysis_{timestamp}.xlsx'
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Main results with original D'Marco data merged
        enhanced_results = results_df.copy()
        
        # Add original D'Marco data
        for i, site_data in enumerate(dmarco_sites):
            if i < len(enhanced_results):
                enhanced_results.loc[i, 'original_address'] = site_data.get('original_address', '')
                enhanced_results.loc[i, 'dmarco_city'] = site_data.get('city', '')
                enhanced_results.loc[i, 'dmarco_acres'] = site_data.get('acres', 0)
                enhanced_results.loc[i, 'census_population'] = site_data.get('population', 0)
        
        enhanced_results.to_excel(writer, sheet_name='DMarco_Top25_Parcel_Results', index=False)
        
        # Successful APNs with boundary data
        if len(successful_results) > 0:
            successful_results.to_excel(writer, sheet_name='Successful_APNs', index=False)
        
        # Sites with boundary coordinates
        boundary_sites = successful_results[successful_results['boundary_points_count'] > 0]
        if len(boundary_sites) > 0:
            boundary_sites.to_excel(writer, sheet_name='Sites_with_Boundaries', index=False)
        
        # Summary statistics
        summary_data = {
            'Metric': [
                'Total D\'Marco Top 25 Sites',
                'Successful APN Lookups',
                'Failed Lookups', 
                'APN Success Rate (%)',
                'Sites with Boundary Data',
                'Boundary Data Success Rate (%)',
                'Ready for Enhanced Analysis'
            ],
            'Value': [
                total_sites,
                successful_lookups,
                failed_lookups,
                f"{successful_lookups/total_sites*100:.1f}%",
                boundary_available,
                f"{boundary_available/successful_lookups*100:.1f}%" if successful_lookups > 0 else "0%",
                boundary_available
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Analysis_Summary', index=False)
    
    print(f"📁 D'Marco parcel analysis exported to: {excel_file}")
    
    # JSON export for technical integration
    json_file = f'/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping/DMarco_Top25_Parcel_Technical_{timestamp}.json'
    
    detailed_analysis = {
        'dmarco_analysis_metadata': {
            'analysis_date': datetime.now().isoformat(),
            'source_file': 'ENHANCED_CENSUS_ANALYSIS_20250801_235158._Sentxlsx.xlsx',
            'sheet_analyzed': 'Top_25_Investment_Ready',
            'total_dmarco_sites': total_sites,
            'successful_apn_lookups': successful_lookups,
            'failed_lookups': failed_lookups,
            'apn_success_rate_percent': round(successful_lookups/total_sites*100, 1),
            'boundary_data_available': boundary_available,
            'boundary_success_rate_percent': round(boundary_available/successful_lookups*100, 1) if successful_lookups > 0 else 0
        },
        'integration_capabilities': {
            'vitor_botn_integration': 'Ready for Phase 6.5 parcel boundary enhancement',
            'environmental_analysis': f'{boundary_available} sites ready for property-edge contamination screening',
            'transit_compliance': f'{boundary_available} sites ready for precise TDHCA transit measurements',
            'lihtc_due_diligence': f'{successful_lookups} sites with official APN identification'
        },
        'dmarco_parcel_results': enhanced_results.to_dict('records') if 'enhanced_results' in locals() else results_df.to_dict('records')
    }
    
    with open(json_file, 'w') as f:
        json.dump(detailed_analysis, f, indent=2)
    
    print(f"📁 Technical analysis exported to: {json_file}")
    print()
    
    # Show examples of parcel corner coordinates if available
    if boundary_available > 0:
        print("🗺️ SAMPLE PARCEL CORNER COORDINATES")
        print("-" * 40)
        sample_count = 0
        for _, row in boundary_sites.iterrows():
            if sample_count < 3:  # Show first 3 examples
                print(f"📍 {row['site_id']} (APN: {row['apn']})")
                print(f"   Boundary Points: {row['boundary_points_count']} coordinates")
                print(f"   Note: Full coordinates available in technical system")
                print()
                sample_count += 1
    
    print("✅ D'MARCO TOP 25 PARCEL BOUNDARY EXTRACTION COMPLETE")
    print("=" * 70)
    
    return results_df, excel_file, json_file

if __name__ == "__main__":
    print("🚀 Starting D'Marco Top 25 Parcel Boundary Test")
    print()
    
    # Run comprehensive D'Marco test
    results_df, excel_file, json_file = test_dmarco_sites_for_parcel_boundaries()
    
    if results_df is not None:
        print(f"\n🎖️ D'MARCO ANALYSIS COMPLETE")
        print(f"📊 Results Spreadsheet: {excel_file}")
        print(f"🔧 Technical Data: {json_file}")
        print("\nReady for integration with Vitor's BOTN system Phase 6.5!")
    else:
        print("\n❌ D'Marco analysis failed - check data files")