#!/usr/bin/env python3

"""
Extract Actual Parcel Corner Coordinates for D'Marco Sites
Shows real LAT/LONG boundary points for property-edge analysis
"""

import sys
import os
import pandas as pd
import json
from datetime import datetime

# Add the parcel mapping module to path
sys.path.append('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping')

from universal_parcel_mapper import UniversalParcelMapper, ParcelData

def extract_boundary_coordinates_for_dmarco_sites():
    """Extract and display actual parcel corner coordinates for successful D'Marco sites"""
    
    print("🗺️ D'MARCO PARCEL CORNER COORDINATES EXTRACTION")
    print("=" * 60)
    print(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Successful D'Marco sites from our analysis
    successful_sites = [
        {
            'site_id': 'DMarco_Top25_09_Boerne_Ralph_Fair_Rd',
            'lat': 29.6859485,
            'lng': -98.6325156,
            'state': 'TX',
            'address': 'Ralph Fair Rd., Boerne, TX',
            'expected_boundary_points': 19
        },
        {
            'site_id': 'DMarco_Top25_13_San_Antonio_20623_Stone_Oak_Park',
            'lat': 29.6495764,
            'lng': -98.464094,
            'state': 'TX', 
            'address': '20623 Stone Oak Parkway, San Antonio, TX',
            'expected_boundary_points': 41
        }
    ]
    
    # Initialize Universal Parcel Mapper
    mapper = UniversalParcelMapper()
    
    parcel_corner_data = {}
    
    for site in successful_sites:
        print(f"🏢 EXTRACTING PARCEL CORNERS: {site['site_id']}")
        print(f"📍 Location: {site['address']}")
        print(f"🎯 Coordinates: {site['lat']:.6f}, {site['lng']:.6f}")
        print()
        
        # Get parcel data with boundary coordinates
        parcel_data = mapper.get_parcel_from_coordinates(site['lat'], site['lng'], site['state'])
        
        if parcel_data and parcel_data.boundary_coordinates:
            boundary_coords = parcel_data.boundary_coordinates
            
            print(f"✅ SUCCESS: Found {len(boundary_coords)} boundary coordinates")
            print(f"🏛️ APN: {parcel_data.apn}")
            print(f"🏗️ County: {parcel_data.county}")
            print(f"📐 Calculated Area: {parcel_data.property_area_acres:.2f} acres")
            print()
            
            print("🗺️ PARCEL CORNER COORDINATES:")
            print("-" * 40)
            
            # Display boundary coordinates
            for i, (lat, lng) in enumerate(boundary_coords[:10]):  # Show first 10 points
                print(f"   Corner {i+1:2d}: {lat:.8f}, {lng:.8f}")
            
            if len(boundary_coords) > 10:
                print(f"   ... and {len(boundary_coords) - 10} more boundary points")
            
            print()
            
            # Calculate property dimensions for analysis
            if len(boundary_coords) >= 4:
                lats = [coord[0] for coord in boundary_coords]
                lngs = [coord[1] for coord in boundary_coords]
                
                lat_range = max(lats) - min(lats)
                lng_range = max(lngs) - min(lngs)
                
                # Approximate dimensions (not geodesically correct, but good estimate)
                lat_distance_ft = lat_range * 364000  # Approximate feet per degree latitude
                lng_distance_ft = lng_range * 288200  # Approximate feet per degree longitude at Texas latitude
                
                print(f"📏 PROPERTY DIMENSIONS ANALYSIS:")
                print(f"   Latitude Range: {lat_range:.6f}° ({lat_distance_ft:.0f} feet)")
                print(f"   Longitude Range: {lng_range:.6f}° ({lng_distance_ft:.0f} feet)")
                print(f"   Approximate Shape: {lat_distance_ft:.0f}' x {lng_distance_ft:.0f}'")
                print()
            
            # Store detailed corner data
            parcel_corner_data[site['site_id']] = {
                'site_info': site,
                'parcel_data': {
                    'apn': parcel_data.apn,
                    'county': parcel_data.county,
                    'state': parcel_data.state,
                    'area_acres': parcel_data.property_area_acres,
                    'owner_name': parcel_data.owner_name,
                    'data_source': parcel_data.data_source
                },
                'boundary_coordinates': boundary_coords,
                'corner_analysis': {
                    'total_corners': len(boundary_coords),
                    'north_boundary': max(lat for lat, lng in boundary_coords),
                    'south_boundary': min(lat for lat, lng in boundary_coords),
                    'east_boundary': max(lng for lat, lng in boundary_coords),
                    'west_boundary': min(lng for lat, lng in boundary_coords),
                    'property_centroid': (sum(lat for lat, lng in boundary_coords) / len(boundary_coords),
                                        sum(lng for lat, lng in boundary_coords) / len(boundary_coords))
                }
            }
            
            # Create KML for visualization
            kml_file = f'/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping/DMarco_{site["site_id"]}_Parcel_Boundaries.kml'
            mapper.export_parcel_boundaries_kml(parcel_data, kml_file)
            print(f"🗺️ KML exported: {kml_file}")
            print()
            
        else:
            print(f"❌ No boundary data available for {site['site_id']}")
            print()
        
        print("-" * 60)
        print()
    
    # Export detailed corner coordinate analysis
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # JSON export with full coordinate data
    json_file = f'/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping/DMarco_Parcel_Corner_Coordinates_{timestamp}.json'
    
    corner_analysis = {
        'extraction_metadata': {
            'extraction_date': datetime.now().isoformat(),
            'total_sites_analyzed': len(successful_sites),
            'sites_with_boundary_data': len(parcel_corner_data),
            'total_boundary_points_extracted': sum(len(data['boundary_coordinates']) for data in parcel_corner_data.values())
        },
        'business_applications': {
            'environmental_screening': 'Property-edge distance calculations for contamination risk assessment',
            'transit_compliance': 'Precise TDHCA measurements from parcel boundaries to transit stops',
            'setback_analysis': 'Building placement and zoning compliance verification',
            'utility_planning': 'Infrastructure routing and easement analysis',
            'due_diligence': 'Professional-grade property boundary verification'
        },
        'parcel_corner_data': parcel_corner_data
    }
    
    with open(json_file, 'w') as f:
        json.dump(corner_analysis, f, indent=2)
    
    print(f"📁 Detailed corner coordinates exported to: {json_file}")
    
    # Excel export with corner coordinates
    excel_file = f'/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping/DMarco_Parcel_Corner_Analysis_{timestamp}.xlsx'
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = []
        corner_sheets_data = {}
        
        for site_id, data in parcel_corner_data.items():
            summary_data.append({
                'Site_ID': site_id,
                'Address': data['site_info']['address'],
                'APN': data['parcel_data']['apn'],
                'County': data['parcel_data']['county'],
                'Area_Acres': data['parcel_data']['area_acres'],
                'Owner': data['parcel_data']['owner_name'],
                'Total_Corners': data['corner_analysis']['total_corners'],
                'North_Boundary': data['corner_analysis']['north_boundary'],
                'South_Boundary': data['corner_analysis']['south_boundary'],
                'East_Boundary': data['corner_analysis']['east_boundary'],
                'West_Boundary': data['corner_analysis']['west_boundary'],
                'Centroid_Lat': data['corner_analysis']['property_centroid'][0],
                'Centroid_Lng': data['corner_analysis']['property_centroid'][1]
            })
            
            # Create corner coordinates sheet for each site
            corner_coords_data = []
            for i, (lat, lng) in enumerate(data['boundary_coordinates']):
                corner_coords_data.append({
                    'Corner_Number': i + 1,
                    'Latitude': lat,
                    'Longitude': lng,
                    'Decimal_Degrees': f"{lat:.8f}, {lng:.8f}"
                })
            
            # Clean sheet name for Excel
            sheet_name = site_id.replace('DMarco_Top25_', '').replace('_', ' ')[:30]
            corner_sheets_data[sheet_name] = pd.DataFrame(corner_coords_data)
        
        # Write summary
        if summary_data:
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Parcel_Summary', index=False)
        
        # Write individual corner coordinate sheets
        for sheet_name, df in corner_sheets_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"📁 Corner analysis Excel exported to: {excel_file}")
    print()
    
    print("🎯 PARCEL CORNER EXTRACTION SUMMARY")
    print("-" * 45)
    print(f"D'Marco Sites Analyzed: {len(successful_sites)}")
    print(f"Sites with Boundary Data: {len(parcel_corner_data)}")
    if parcel_corner_data:
        total_corners = sum(len(data['boundary_coordinates']) for data in parcel_corner_data.values())
        print(f"Total Corner Coordinates: {total_corners}")
        print(f"Average Corners per Property: {total_corners / len(parcel_corner_data):.1f}")
    print()
    
    print("✅ ENHANCED ANALYSIS CAPABILITIES UNLOCKED:")
    print("   🌍 Property-edge environmental screening")
    print("   🚌 Precise transit compliance measurements")
    print("   🏗️ Professional setback and zoning analysis")
    print("   📏 Accurate property dimension calculations")
    print("   🗺️ Google Earth visualization (KML files)")
    print()
    
    print("🚀 READY FOR VITOR BOTN INTEGRATION")
    print("   Phase 6.5: Parcel boundary enhancement")
    print("   Enhanced environmental analysis with property edges")
    print("   Precise TDHCA transit measurements from boundaries")
    print()
    
    return parcel_corner_data, json_file, excel_file

if __name__ == "__main__":
    print("🎯 Starting D'Marco Parcel Corner Coordinate Extraction")
    print()
    
    # Extract actual corner coordinates
    corner_data, json_file, excel_file = extract_boundary_coordinates_for_dmarco_sites()
    
    print(f"🎖️ CORNER COORDINATE EXTRACTION COMPLETE")
    print(f"📊 Analysis Spreadsheet: {excel_file}")
    print(f"🔧 Technical Data: {json_file}")
    print("\n✅ Ready for integration with Vitor's BOTN system!")