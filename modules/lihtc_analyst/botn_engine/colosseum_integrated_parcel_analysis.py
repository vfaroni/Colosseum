#!/usr/bin/env python3

"""
Colosseum Integrated Parcel Analysis System
Combines:
1. Vitor's BOTN CoStar data
2. Bill's parcel corner mapping 
3. CTCAC scoring from Perris model
4. California and national datasets

IMPORTANT: Creates NEW Excel file preserving original CoStar data
"""

import sys
import os
import pandas as pd
import json
from datetime import datetime
import logging
from pathlib import Path

# Add required paths
sys.path.append('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping')
sys.path.append('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/lihtc_analyst/priorcode')

from universal_parcel_mapper import UniversalParcelMapper, ParcelData

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ColosseumIntegratedAnalyzer:
    """Integrated analysis combining BOTN, parcel mapping, and CTCAC scoring"""
    
    def __init__(self):
        self.mapper = UniversalParcelMapper()
        
        # CTCAC distance rules and scoring from Perris model
        self.ctcac_scoring = {
            'transit': {
                'hqta': {'distance': 0.33, 'points': 7},
                'frequent_service': {'distance': [0.33, 0.5], 'points': [6, 5]},
                'basic_transit': {'distance': [0.33, 0.5], 'points': [4, 3]}
            },
            'public_park': {
                'standard': {'distance': [0.5, 0.75], 'points': [3, 2]},
                'rural': {'distance': [1.0, 1.5], 'points': [3, 2]}
            },
            'library': {
                'standard': {'distance': [0.5, 1.0], 'points': [3, 2]},
                'rural': {'distance': [1.0, 2.0], 'points': [3, 2]}
            },
            'grocery': {
                'full_scale': {'standard': [0.5, 1.0, 1.5], 'points': [5, 4, 3]},
                'neighborhood': {'standard': [0.25, 0.5], 'points': [4, 3]}
            },
            'schools': {
                'elementary': {'standard': [0.25, 0.75], 'points': [3, 2]},
                'high': {'standard': [1.0, 1.5], 'points': [3, 2]}
            },
            'medical': {
                'standard': {'distance': [0.5, 1.0], 'points': [3, 2]},
                'rural': {'distance': [1.0, 1.5], 'points': [3, 2]}
            },
            'pharmacy': {
                'standard': {'distance': [0.5, 1.0], 'points': [2, 1]},
                'rural': {'distance': [1.0, 2.0], 'points': [2, 1]}
            }
        }
        
        # Data paths
        self.data_base = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Data_Sets")
        self.ca_parcels_path = self.data_base / "california/CA_Parcels"
        self.transit_data_path = self.data_base / "california/CA_Transit_Data"
        self.schools_path = self.data_base / "california/CA_Public_Schools"
        
    def process_costar_file(self, costar_file_path):
        """Process CoStar Excel file and enhance with parcel and CTCAC data"""
        
        print("🏛️ COLOSSEUM INTEGRATED PARCEL ANALYSIS")
        print("=" * 60)
        print(f"Processing: {costar_file_path}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Progress update 1
        print("📊 [1/6] Reading CoStar Excel file...")
        try:
            # Read CoStar data - preserve original
            costar_df = pd.read_excel(costar_file_path)
            print(f"✅ Loaded {len(costar_df)} sites from CoStar export")
            print(f"   Columns: {', '.join(costar_df.columns[:5])}...")
            print()
        except Exception as e:
            logger.error(f"Failed to read CoStar file: {e}")
            return None
        
        # Progress update 2
        print("🗺️ [2/6] Extracting parcel boundaries for each site...")
        enhanced_data = []
        
        for idx, row in costar_df.iterrows():
            # Try to find lat/lng columns (common variations)
            lat = None
            lng = None
            
            # Check for various column names
            lat_columns = ['Latitude', 'latitude', 'Lat', 'lat', 'LAT', 'Y', 'y']
            lng_columns = ['Longitude', 'longitude', 'Long', 'long', 'LON', 'LONG', 'Lng', 'lng', 'LNG', 'X', 'x']
            
            for col in lat_columns:
                if col in row and pd.notna(row[col]):
                    lat = float(row[col])
                    break
                    
            for col in lng_columns:
                if col in row and pd.notna(row[col]):
                    lng = float(row[col])
                    break
            
            if lat is None or lng is None:
                print(f"⚠️  Site {idx+1}: Missing coordinates, skipping...")
                continue
            
            print(f"🔍 Site {idx+1}/{len(costar_df)}: Processing ({lat:.6f}, {lng:.6f})")
            
            # Get parcel data with boundaries
            try:
                parcel_data = self.mapper.get_parcel_from_coordinates(lat, lng, 'CA')
                
                if parcel_data and parcel_data.boundary_coordinates:
                    corners = parcel_data.boundary_coordinates
                    print(f"   ✅ Found {len(corners)} boundary points")
                    
                    # Calculate corner summary
                    lats = [coord[0] for coord in corners]
                    lngs = [coord[1] for coord in corners]
                    
                    site_data = {
                        'Site_Index': idx,
                        'Original_Lat': lat,
                        'Original_Lng': lng,
                        'APN': parcel_data.apn,
                        'County': parcel_data.county,
                        'Parcel_Area_Acres': parcel_data.property_area_acres,
                        'Owner_Name': parcel_data.owner_name,
                        'Num_Corners': len(corners),
                        'North_Boundary': max(lats),
                        'South_Boundary': min(lats),
                        'East_Boundary': max(lngs),
                        'West_Boundary': min(lngs),
                        'Centroid_Lat': sum(lats) / len(lats),
                        'Centroid_Lng': sum(lngs) / len(lngs),
                        'Corner_Coordinates': json.dumps(corners)  # Store as JSON string
                    }
                    
                    # Add all original CoStar columns
                    for col in costar_df.columns:
                        if col not in site_data:
                            site_data[f'CoStar_{col}'] = row[col]
                    
                    enhanced_data.append(site_data)
                    
                else:
                    print(f"   ❌ No parcel boundaries found")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                
        print()
        
        # Progress update 3
        print("🎯 [3/6] Calculating CTCAC scores...")
        # TODO: Implement CTCAC scoring based on amenity distances
        # This would query transit, schools, parks, etc. datasets
        
        # Progress update 4
        print("📊 [4/6] Creating enhanced Excel output...")
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = costar_file_path.replace('.xlsx', f'_ENHANCED_{timestamp}.xlsx')
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet 1: Original CoStar Data (preserved)
            costar_df.to_excel(writer, sheet_name='Original_CoStar_Data', index=False)
            print("   ✅ Sheet 1: Original CoStar data preserved")
            
            # Sheet 2: Enhanced Site Summary
            if enhanced_data:
                enhanced_df = pd.DataFrame(enhanced_data)
                # Select summary columns for main sheet
                summary_cols = ['Site_Index', 'APN', 'County', 'Parcel_Area_Acres', 
                               'Num_Corners', 'North_Boundary', 'South_Boundary',
                               'East_Boundary', 'West_Boundary', 'Owner_Name']
                # Add CoStar columns
                costar_cols = [col for col in enhanced_df.columns if col.startswith('CoStar_')]
                summary_df = enhanced_df[summary_cols + costar_cols[:5]]  # First 5 CoStar columns
                summary_df.to_excel(writer, sheet_name='Enhanced_Site_Summary', index=False)
                print("   ✅ Sheet 2: Enhanced site summary created")
            
            # Sheet 3: Parcel Corner Details
            if enhanced_data:
                corner_details = []
                for site in enhanced_data:
                    corners = json.loads(site['Corner_Coordinates'])
                    for i, (lat, lng) in enumerate(corners):
                        corner_details.append({
                            'Site_Index': site['Site_Index'],
                            'APN': site['APN'],
                            'Corner_Number': i + 1,
                            'Latitude': lat,
                            'Longitude': lng
                        })
                
                pd.DataFrame(corner_details).to_excel(writer, sheet_name='Parcel_Corner_Coordinates', index=False)
                print("   ✅ Sheet 3: Detailed corner coordinates")
            
            # Sheet 4: CTCAC Scoring (placeholder)
            ctcac_df = pd.DataFrame({
                'Category': ['Transit', 'Parks', 'Schools', 'Grocery', 'Medical'],
                'Points_Available': [7, 3, 3, 5, 3],
                'Status': ['To be implemented'] * 5
            })
            ctcac_df.to_excel(writer, sheet_name='CTCAC_Scoring', index=False)
            print("   ✅ Sheet 4: CTCAC scoring framework")
        
        # Progress update 5
        print("\n🗺️ [5/6] Generating KML files for visualization...")
        kml_count = 0
        for site in enhanced_data[:5]:  # First 5 sites only
            try:
                # Create temporary ParcelData object for KML export
                corners = json.loads(site['Corner_Coordinates'])
                temp_parcel = ParcelData(
                    apn=site['APN'],
                    state='CA',
                    county=site['County'],
                    boundary_coordinates=corners,
                    property_area_acres=site['Parcel_Area_Acres']
                )
                
                kml_file = output_file.replace('.xlsx', f'_Site{site["Site_Index"]}.kml')
                self.mapper.export_parcel_boundaries_kml(temp_parcel, kml_file)
                kml_count += 1
            except:
                pass
        
        print(f"   ✅ Generated {kml_count} KML files for visualization")
        
        # Progress update 6
        print("\n✅ [6/6] Analysis complete!")
        print(f"\n📊 SUMMARY:")
        print(f"   Total sites processed: {len(costar_df)}")
        print(f"   Sites with parcel data: {len(enhanced_data)}")
        print(f"   Output file: {output_file}")
        print(f"   Completion time: {datetime.now().strftime('%H:%M:%S')}")
        
        return output_file, enhanced_data

def main():
    """Main execution function"""
    # Initialize analyzer
    analyzer = ColosseumIntegratedAnalyzer()
    
    # Process the CoStar file
    costar_file = '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport-15.xlsx'
    
    output_file, enhanced_data = analyzer.process_costar_file(costar_file)
    
    if output_file:
        print(f"\n🎉 SUCCESS! Enhanced analysis saved to:")
        print(f"   {output_file}")
        print("\n🚀 Ready for Vitor's BOTN integration!")
    else:
        print("\n❌ Analysis failed. Please check the logs.")

if __name__ == "__main__":
    main()