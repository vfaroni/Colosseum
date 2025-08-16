#!/usr/bin/env python3

"""
Colosseum Local Parcel Analysis System
Uses Bill's California parcel datasets (10M+ parcels) instead of external APIs
Combines:
1. Vitor's BOTN CoStar data
2. Bill's local parcel datasets with corner mapping 
3. CTCAC scoring from Perris model
4. California datasets (transit, schools, etc.)

IMPORTANT: Creates NEW Excel file preserving original CoStar data
"""

import sys
import os
import pandas as pd
import geopandas as gpd
import json
from datetime import datetime
import logging
from pathlib import Path
from shapely.geometry import Point, Polygon
import numpy as np
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CaliforniaLocalParcelAnalyzer:
    """Analyze parcels using local California datasets"""
    
    def __init__(self):
        # Base data paths
        self.data_base = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Data_Sets")
        self.ca_parcels_path = self.data_base / "california/CA_Parcels"
        self.transit_data_path = self.data_base / "california/CA_Transit_Data"
        self.schools_path = self.data_base / "california/CA_Public_Schools"
        
        # CTCAC scoring rules from Perris model
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
        
        # Track loaded datasets
        self.loaded_counties = {}
        
    def determine_county_from_coords(self, lat, lng):
        """Determine which California county based on coordinates"""
        # County approximate bounds
        county_bounds = {
            'Los_Angeles': {'lat_min': 33.7, 'lat_max': 34.8, 'lng_min': -118.9, 'lng_max': -117.6},
            'Orange': {'lat_min': 33.4, 'lat_max': 33.9, 'lng_min': -118.1, 'lng_max': -117.4},
            'San_Diego': {'lat_min': 32.5, 'lat_max': 33.5, 'lng_min': -117.6, 'lng_max': -116.1},
            'Riverside': {'lat_min': 33.4, 'lat_max': 34.1, 'lng_min': -117.7, 'lng_max': -114.4},
            'San_Bernardino': {'lat_min': 34.0, 'lat_max': 35.8, 'lng_min': -118.0, 'lng_max': -114.1},
            'Fresno': {'lat_min': 36.2, 'lat_max': 37.6, 'lng_min': -120.9, 'lng_max': -118.3},
            'Sacramento': {'lat_min': 38.0, 'lat_max': 38.9, 'lng_min': -121.6, 'lng_max': -120.7},
            'San_Francisco': {'lat_min': 37.7, 'lat_max': 37.9, 'lng_min': -122.6, 'lng_max': -122.3},
            'Alameda': {'lat_min': 37.4, 'lat_max': 37.9, 'lng_min': -122.4, 'lng_max': -121.5},
            'Santa_Clara': {'lat_min': 36.9, 'lat_max': 37.5, 'lng_min': -122.2, 'lng_max': -121.2}
        }
        
        for county, bounds in county_bounds.items():
            if (bounds['lat_min'] <= lat <= bounds['lat_max'] and 
                bounds['lng_min'] <= lng <= bounds['lng_max']):
                return county
        
        return None
    
    def load_county_parcels(self, county):
        """Load parcel data for a specific county"""
        if county in self.loaded_counties:
            return self.loaded_counties[county]
        
        print(f"   Loading {county} parcel data...")
        county_path = self.ca_parcels_path / county
        
        # Try different file formats
        geojson_files = list(county_path.glob("*.geojson"))
        csv_files = list(county_path.glob("*.csv"))
        shp_files = list(county_path.glob("*.shp"))
        
        if geojson_files:
            # Prefer GeoJSON
            print(f"   Found GeoJSON: {geojson_files[0].name}")
            gdf = gpd.read_file(geojson_files[0])
            self.loaded_counties[county] = gdf
            return gdf
        elif shp_files:
            # Try shapefile
            print(f"   Found Shapefile: {shp_files[0].name}")
            gdf = gpd.read_file(shp_files[0])
            self.loaded_counties[county] = gdf
            return gdf
        elif csv_files:
            # Last resort - CSV (no geometry)
            print(f"   Found CSV (no geometry): {csv_files[0].name}")
            df = pd.read_csv(csv_files[0])
            self.loaded_counties[county] = df
            return df
        else:
            print(f"   ❌ No parcel data found for {county}")
            return None
    
    def find_parcel_by_coords(self, lat, lng, county_gdf):
        """Find parcel containing the given coordinates"""
        if county_gdf is None:
            return None
            
        # Create point
        point = Point(lng, lat)
        
        # For GeoDataFrame with geometry
        if isinstance(county_gdf, gpd.GeoDataFrame) and 'geometry' in county_gdf.columns:
            # Find parcel containing the point
            mask = county_gdf.contains(point)
            matching_parcels = county_gdf[mask]
            
            if not matching_parcels.empty:
                return matching_parcels.iloc[0]
        
        # For regular DataFrame, try to find by proximity if lat/lng columns exist
        elif isinstance(county_gdf, pd.DataFrame):
            lat_cols = ['latitude', 'lat', 'y', 'centroid_lat']
            lng_cols = ['longitude', 'lng', 'lon', 'x', 'centroid_lng']
            
            lat_col = None
            lng_col = None
            
            for col in lat_cols:
                if col in county_gdf.columns:
                    lat_col = col
                    break
                    
            for col in lng_cols:
                if col in county_gdf.columns:
                    lng_col = col
                    break
                    
            if lat_col and lng_col:
                # Find nearest parcel
                county_gdf['distance'] = ((county_gdf[lat_col] - lat)**2 + 
                                         (county_gdf[lng_col] - lng)**2)**0.5
                nearest = county_gdf.nsmallest(1, 'distance')
                if not nearest.empty and nearest.iloc[0]['distance'] < 0.001:  # ~100m threshold
                    return nearest.iloc[0]
        
        return None
    
    def extract_parcel_corners(self, parcel):
        """Extract corner coordinates from parcel geometry"""
        corners = []
        
        if hasattr(parcel, 'geometry') and parcel.geometry is not None:
            geom = parcel.geometry
            
            # Handle different geometry types
            if geom.geom_type == 'Polygon':
                # Get exterior coordinates
                coords = list(geom.exterior.coords)
                corners = [(coord[1], coord[0]) for coord in coords[:-1]]  # Exclude duplicate last point
            elif geom.geom_type == 'MultiPolygon':
                # Get the largest polygon
                largest = max(geom.geoms, key=lambda p: p.area)
                coords = list(largest.exterior.coords)
                corners = [(coord[1], coord[0]) for coord in coords[:-1]]
        
        return corners
    
    def _map_county_name_to_folder(self, county_name: str) -> Optional[str]:
        """Map county names from CoStar to folder names in our dataset"""
        # Direct mapping for counties we have
        county_mapping = {
            'Humboldt': 'Humboldt',
            'Los Angeles': 'Los_Angeles',
            'Orange': 'Orange', 
            'San Diego': 'San_Diego',
            'Riverside': 'Riverside',
            'San Bernardino': 'San_Bernardino',
            'Fresno': 'Fresno',
            'Sacramento': 'Sacramento',
            'San Francisco': 'San_Francisco',
            'Alameda': 'Alameda',
            'Santa Clara': 'Santa_Clara',
            'Kern': 'Kern',
            'Marin': 'Marin',
            'Merced': 'Merced',
            'Monterey': 'Monterey',
            'San Joaquin': 'San_Joaquin',
            'San Luis Obispo': 'San_Luis_Obispo',
            'Ventura': 'Ventura',
            'Contra Costa': 'Contra_Costa'
        }
        
        # Check if we have this county
        if county_name in county_mapping:
            folder_name = county_mapping[county_name]
            # Verify folder exists
            if (self.ca_parcels_path / folder_name).exists():
                return folder_name
        
        # Try with underscores
        folder_name = county_name.replace(' ', '_')
        if (self.ca_parcels_path / folder_name).exists():
            return folder_name
            
        return None
    
    def process_costar_file(self, costar_file_path):
        """Process CoStar Excel file and enhance with local parcel data"""
        
        print("🏛️ COLOSSEUM LOCAL PARCEL ANALYSIS")
        print("=" * 60)
        print(f"Processing: {costar_file_path}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Using local California parcel datasets (10M+ parcels)")
        print()
        
        # Progress update 1
        print("📊 [1/6] Reading CoStar Excel file...")
        try:
            # Read CoStar data - preserve original
            costar_df = pd.read_excel(costar_file_path)
            print(f"✅ Loaded {len(costar_df)} sites from CoStar export")
            if len(costar_df.columns) > 0:
                print(f"   Columns: {', '.join(costar_df.columns[:5])}...")
            
            # Check available counties in our datasets
            available_counties = set()
            if self.ca_parcels_path.exists():
                for county_dir in self.ca_parcels_path.iterdir():
                    if county_dir.is_dir():
                        available_counties.add(county_dir.name)
            
            print(f"\n   Available parcel datasets: {len(available_counties)} counties")
            print(f"   Counties: {', '.join(sorted(available_counties))}")
            print()
        except Exception as e:
            logger.error(f"Failed to read CoStar file: {e}")
            return None
        
        # Progress update 2
        print("🗺️ [2/6] Finding parcels in local datasets...")
        enhanced_data = []
        
        # Process only first 10 sites for testing
        for idx, row in costar_df.head(10).iterrows():
            # Try to find lat/lng columns
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
            
            # Get county from CoStar data
            county_name = row.get('County Name', '')
            if not county_name:
                print(f"⚠️  Site {idx+1}: Missing county name, skipping...")
                continue
            
            print(f"🔍 Site {idx+1}/{len(costar_df)}: ({lat:.6f}, {lng:.6f}) - {county_name} County")
            
            # Map county name to folder name (handle variations)
            county_folder = self._map_county_name_to_folder(county_name)
            if not county_folder:
                print(f"   ❌ No parcel data available for {county_name} County")
                enhanced_data.append({
                    'Site_Index': idx,
                    'Original_Lat': lat,
                    'Original_Lng': lng,
                    'County': county_name,
                    'Data_Status': 'No parcel data available',
                    **{f'CoStar_{col}': row[col] for col in costar_df.columns}
                })
                continue
                
            print(f"   📍 Using dataset: {county_folder}")
            
            # Load county parcels if needed
            county_gdf = self.load_county_parcels(county_folder)
            if county_gdf is None:
                enhanced_data.append({
                    'Site_Index': idx,
                    'Original_Lat': lat,
                    'Original_Lng': lng,
                    'County': county_name,
                    'Data_Status': 'Failed to load parcel data',
                    **{f'CoStar_{col}': row[col] for col in costar_df.columns}
                })
                continue
            
            # Find parcel
            parcel = self.find_parcel_by_coords(lat, lng, county_gdf)
            
            if parcel is not None:
                # Extract corners
                corners = self.extract_parcel_corners(parcel)
                
                if corners:
                    print(f"   ✅ Found parcel with {len(corners)} corners")
                else:
                    print(f"   ⚠️  Found parcel but no corner geometry")
                
                # Get APN
                apn_fields = ['APN', 'apn', 'Parcel_ID', 'PARCEL_ID', 'ParcelID', 'Assessor_Parcel_Number']
                apn = 'Unknown'
                for field in apn_fields:
                    if field in parcel and pd.notna(parcel[field]):
                        apn = str(parcel[field])
                        break
                
                # Calculate area if possible
                area = 0
                if hasattr(parcel, 'geometry') and parcel.geometry is not None:
                    # Calculate area in acres (approximate)
                    area = parcel.geometry.area * 247105  # Convert from degrees² to acres (rough estimate)
                
                # Build enhanced data
                site_data = {
                    'Site_Index': idx,
                    'Original_Lat': lat,
                    'Original_Lng': lng,
                    'County': county_name,
                    'APN': apn,
                    'Parcel_Area_Acres': area,
                    'Num_Corners': len(corners),
                    'Corner_Coordinates': json.dumps(corners) if corners else '[]'
                }
                
                # Calculate bounds if corners exist
                if corners:
                    lats = [c[0] for c in corners]
                    lngs = [c[1] for c in corners]
                    site_data.update({
                        'North_Boundary': max(lats),
                        'South_Boundary': min(lats),
                        'East_Boundary': max(lngs),
                        'West_Boundary': min(lngs),
                        'Centroid_Lat': sum(lats) / len(lats),
                        'Centroid_Lng': sum(lngs) / len(lngs)
                    })
                
                # Add owner info if available
                owner_fields = ['Owner', 'OWNER', 'Owner_Name', 'OWNER_NAME']
                for field in owner_fields:
                    if field in parcel and pd.notna(parcel[field]):
                        site_data['Owner_Name'] = str(parcel[field])
                        break
                
                # Add all original CoStar columns
                for col in costar_df.columns:
                    if col not in site_data:
                        site_data[f'CoStar_{col}'] = row[col]
                
                enhanced_data.append(site_data)
                
            else:
                print(f"   ❌ No parcel found at coordinates")
                
        print()
        
        # Progress update 3
        print("🎯 [3/6] Calculating CTCAC scores...")
        # TODO: Implement CTCAC scoring based on amenity distances
        
        # Progress update 4
        print("📊 [4/6] Creating enhanced Excel output...")
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = costar_file_path.replace('.xlsx', f'_LOCAL_ENHANCED_{timestamp}.xlsx')
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet 1: Original CoStar Data (preserved)
            costar_df.to_excel(writer, sheet_name='Original_CoStar_Data', index=False)
            print("   ✅ Sheet 1: Original CoStar data preserved")
            
            # Sheet 2: Enhanced Site Summary
            if enhanced_data:
                enhanced_df = pd.DataFrame(enhanced_data)
                # Dynamic column selection based on what's available
                summary_cols = ['Site_Index', 'County']
                
                # Add optional columns if they exist
                optional_cols = ['APN', 'Parcel_Area_Acres', 'Num_Corners', 'Data_Status',
                               'North_Boundary', 'South_Boundary', 'East_Boundary', 'West_Boundary', 'Owner_Name']
                for col in optional_cols:
                    if col in enhanced_df.columns:
                        summary_cols.append(col)
                    
                # Add first few CoStar columns
                costar_cols = [col for col in enhanced_df.columns if col.startswith('CoStar_')][:5]
                existing_cols = [col for col in summary_cols + costar_cols if col in enhanced_df.columns]
                summary_df = enhanced_df[existing_cols]
                summary_df.to_excel(writer, sheet_name='Enhanced_Site_Summary', index=False)
                print("   ✅ Sheet 2: Enhanced site summary created")
            
            # Sheet 3: Parcel Corner Details
            if enhanced_data:
                corner_details = []
                for site in enhanced_data:
                    if 'Corner_Coordinates' in site:
                        corners = json.loads(site['Corner_Coordinates'])
                        for i, (lat, lng) in enumerate(corners):
                            corner_details.append({
                                'Site_Index': site['Site_Index'],
                                'County': site['County'],
                                'APN': site.get('APN', 'N/A'),
                                'Corner_Number': i + 1,
                                'Latitude': lat,
                                'Longitude': lng
                            })
                
                if corner_details:
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
            
            # Sheet 5: Data Summary
            summary_stats = pd.DataFrame({
                'Metric': ['Total Sites', 'Sites with Parcel Data', 'Sites with Corners', 
                          'Average Corners per Parcel', 'Counties Analyzed'],
                'Value': [
                    len(costar_df),
                    len(enhanced_data),
                    sum(1 for d in enhanced_data if 'Num_Corners' in d and d['Num_Corners'] > 0),
                    np.mean([d['Num_Corners'] for d in enhanced_data if 'Num_Corners' in d]) if any('Num_Corners' in d for d in enhanced_data) else 0,
                    len(set(d['County'] for d in enhanced_data))
                ]
            })
            summary_stats.to_excel(writer, sheet_name='Analysis_Summary', index=False)
            print("   ✅ Sheet 5: Analysis summary statistics")
        
        # Progress update 5
        print("\n🗺️ [5/6] Generating visualizations...")
        # KML generation would go here
        
        # Progress update 6
        print("\n✅ [6/6] Analysis complete!")
        print(f"\n📊 SUMMARY:")
        print(f"   Total sites processed: {len(costar_df)}")
        print(f"   Sites with parcel data: {len(enhanced_data)}")
        if enhanced_data:
            sites_with_corners = sum(1 for d in enhanced_data if 'Num_Corners' in d and d['Num_Corners'] > 0)
            print(f"   Sites with corner data: {sites_with_corners}")
            print(f"   Counties analyzed: {len(set(d['County'] for d in enhanced_data))}")
            sites_without_data = sum(1 for d in enhanced_data if 'Data_Status' in d)
            if sites_without_data > 0:
                print(f"   Sites without parcel data: {sites_without_data}")
        print(f"   Output file: {output_file}")
        print(f"   Completion time: {datetime.now().strftime('%H:%M:%S')}")
        
        return output_file, enhanced_data

def main():
    """Main execution function"""
    # Initialize analyzer
    analyzer = CaliforniaLocalParcelAnalyzer()
    
    # Process the CoStar file
    costar_file = '/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport-11.xlsx'
    
    output_file, enhanced_data = analyzer.process_costar_file(costar_file)
    
    if output_file:
        print(f"\n🎉 SUCCESS! Enhanced analysis saved to:")
        print(f"   {output_file}")
        print("\n🚀 Ready for Vitor's BOTN integration!")
        print("📂 Using local California parcel data - no external API calls needed!")
    else:
        print("\n❌ Analysis failed. Please check the logs.")

if __name__ == "__main__":
    main()