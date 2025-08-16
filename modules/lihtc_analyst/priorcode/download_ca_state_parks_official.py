#!/usr/bin/env python3
"""
California State Parks Official Dataset Downloader
Downloads official CA state park boundaries and converts to point locations for CTCAC amenity analysis.

Data Source: California Department of Parks and Recreation
URL: https://data.ca.gov/dataset/park-boundaries
"""

import requests
import pandas as pd
import geopandas as gpd
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class CAStateParksDownloader:
    def __init__(self, data_path=None):
        if data_path is None:
            self.data_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets")
        else:
            self.data_path = Path(data_path)
        
        self.parks_dir = self.data_path / "CA_Public_Parks"
        self.parks_dir.mkdir(exist_ok=True)
        
        # Official CA state parks data URLs
        self.csv_url = "https://gis.data.cnra.ca.gov/api/download/v1/items/0fea4fa1db734794bdb3b5410bb3eed9/csv?layers=0"
        self.geojson_url = "https://gis.data.cnra.ca.gov/api/download/v1/items/0fea4fa1db734794bdb3b5410bb3eed9/geojson?layers=0"
        
    def download_state_parks_boundaries(self):
        """Download official CA state parks boundary data"""
        print("Downloading official California state parks boundaries...")
        
        # First try CSV approach (simpler, more reliable)
        try:
            print(f"Trying CSV download from: {self.csv_url}")
            
            response = requests.get(self.csv_url, timeout=120)
            response.raise_for_status()
            
            # Check if we got actual CSV data
            if response.headers.get('content-type', '').startswith('text/csv') or 'csv' in response.headers.get('content-disposition', ''):
                # Save and read CSV
                csv_file = self.parks_dir / "temp_state_parks.csv"
                with open(csv_file, 'wb') as f:
                    f.write(response.content)
                
                # Read CSV and check for coordinate columns
                df = pd.read_csv(csv_file)
                print(f"Downloaded CSV with {len(df)} parks")
                print(f"Columns available: {list(df.columns)}")
                
                # Convert to GeoDataFrame if we have coordinates
                if 'Latitude' in df.columns and 'Longitude' in df.columns:
                    gdf = gpd.GeoDataFrame(
                        df,
                        geometry=gpd.points_from_xy(df.Longitude, df.Latitude),
                        crs='EPSG:4326'
                    )
                    csv_file.unlink()  # Clean up temp file
                    return gdf
                else:
                    print("CSV doesn't contain coordinate columns")
                    csv_file.unlink()  # Clean up temp file
                    
        except Exception as e:
            print(f"CSV download failed: {e}")
        
        # Fallback to GeoJSON approach
        try:
            print(f"Trying GeoJSON download from: {self.geojson_url}")
            
            # Download the GeoJSON data
            response = requests.get(self.geojson_url, timeout=120)
            response.raise_for_status()
            
            # Load as GeoDataFrame
            gdf = gpd.read_file(self.geojson_url)
            
            print(f"Downloaded {len(gdf)} state park boundaries")
            print(f"Columns available: {list(gdf.columns)}")
            
            return gdf
            
        except Exception as e:
            print(f"GeoJSON download also failed: {e}")
            return None
    
    def convert_boundaries_to_points(self, gdf):
        """Convert park boundary polygons to point locations (centroids)"""
        if gdf is None or gdf.empty:
            return pd.DataFrame()
        
        print("Converting park boundaries to point locations...")
        
        # Ensure we're in a projected CRS for accurate centroid calculation
        if gdf.crs != 'EPSG:4326':
            # Convert to WGS84 if not already
            gdf = gdf.to_crs('EPSG:4326')
        
        # Calculate centroids
        gdf['centroid'] = gdf.geometry.centroid
        
        # Extract point coordinates
        gdf['latitude'] = gdf['centroid'].y
        gdf['longitude'] = gdf['centroid'].x
        
        # Create standardized parks DataFrame
        parks_data = []
        
        for idx, row in gdf.iterrows():
            # Extract park information
            park_name = row.get('UNIT_NAME', row.get('name', 'State Park'))
            subtype = row.get('SUBTYPE', row.get('subtype', 'state_park'))
            
            # Skip if no valid coordinates
            if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                continue
            
            park_info = {
                'name': park_name,
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'park_type': 'state_park',
                'subtype': subtype,
                'amenity_type': 'state_park',
                'amenity_category': 'public_park',
                'access': 'public',
                'operator': 'CA State Parks',
                'data_source': 'CA_DPR_Official'
            }
            
            # Add additional fields if available
            for field in ['UNIT_ID', 'ACRES', 'DISTRICT', 'REGION']:
                if field in row and pd.notna(row[field]):
                    park_info[field.lower()] = row[field]
            
            parks_data.append(park_info)
        
        result_df = pd.DataFrame(parks_data)
        print(f"Converted {len(result_df)} state parks to point locations")
        
        return result_df
    
    def merge_with_existing_parks(self, state_parks_df):
        """Merge state parks with existing curated parks dataset"""
        print("Merging with existing parks dataset...")
        
        # Load existing parks
        existing_file = self.parks_dir / "CA_Public_Parks.csv"
        if existing_file.exists():
            existing_df = pd.read_csv(existing_file)
            print(f"Found {len(existing_df)} existing parks")
        else:
            print("No existing parks dataset found - using state parks only")
            return state_parks_df
        
        # Combine datasets
        combined_data = []
        
        # Add existing parks (prioritize curated major parks)
        for idx, row in existing_df.iterrows():
            park_info = row.to_dict()
            if 'data_source' not in park_info:
                park_info['data_source'] = 'Curated_Major_Parks'
            combined_data.append(park_info)
        
        # Add state parks (check for duplicates by proximity)
        for idx, row in state_parks_df.iterrows():
            state_park = row.to_dict()
            
            # Check if this state park is close to any existing park (within 0.5 miles)
            is_duplicate = False
            for existing_park in combined_data:
                if 'latitude' in existing_park and 'longitude' in existing_park:
                    distance = self.haversine_distance(
                        state_park['latitude'], state_park['longitude'],
                        existing_park['latitude'], existing_park['longitude']
                    )
                    if distance <= 0.5:  # Within 0.5 miles
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                combined_data.append(state_park)
        
        combined_df = pd.DataFrame(combined_data)
        print(f"Combined dataset: {len(combined_df)} total parks")
        print(f"- Existing curated: {len(existing_df)}")
        print(f"- New state parks: {len(combined_df) - len(existing_df)}")
        
        return combined_df
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 3959  # Earth's radius in miles
        
        return c * r
    
    def save_enhanced_parks_data(self, df):
        """Save enhanced parks dataset"""
        if df.empty:
            print("No data to save")
            return
        
        # Save as CSV (replace existing)
        csv_file = self.parks_dir / "CA_Public_Parks_Enhanced.csv"
        df.to_csv(csv_file, index=False)
        print(f"Enhanced CSV saved to: {csv_file}")
        
        # Also update the main parks file
        main_csv_file = self.parks_dir / "CA_Public_Parks.csv"
        df.to_csv(main_csv_file, index=False)
        print(f"Main parks file updated: {main_csv_file}")
        
        # Save as GeoJSON
        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df.longitude, df.latitude),
            crs='EPSG:4326'
        )
        geojson_file = self.parks_dir / "CA_Public_Parks_Enhanced.geojson"
        gdf.to_file(geojson_file, driver='GeoJSON')
        print(f"Enhanced GeoJSON saved to: {geojson_file}")
        
        # Create enhanced summary
        summary = {
            'total_parks': len(df),
            'data_sources': df['data_source'].value_counts().to_dict() if 'data_source' in df.columns else {},
            'park_types': df['park_type'].value_counts().to_dict() if 'park_type' in df.columns else {},
            'regions_covered': df['region'].value_counts().to_dict() if 'region' in df.columns else {},
            'districts_covered': df['district'].value_counts().to_dict() if 'district' in df.columns else {}
        }
        
        summary_file = self.parks_dir / "CA_Public_Parks_Enhanced_Summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Enhanced summary saved to: {summary_file}")
        
        print(f"\n=== ENHANCED PARKS DATA COMPLETE ===")
        print(f"Total parks: {len(df)}")
        if 'data_source' in df.columns:
            print("Data sources:")
            print(df['data_source'].value_counts())
        if 'park_type' in df.columns:
            print("Park types:")
            print(df['park_type'].value_counts())
    
    def create_enhanced_parks_dataset(self):
        """Create enhanced parks dataset with official state parks data"""
        print("=== CALIFORNIA PARKS ENHANCEMENT WITH OFFICIAL STATE DATA ===")
        
        # Step 1: Download official state parks boundaries
        state_parks_gdf = self.download_state_parks_boundaries()
        
        if state_parks_gdf is None:
            print("Failed to download state parks data")
            return pd.DataFrame()
        
        # Step 2: Convert boundaries to points
        state_parks_df = self.convert_boundaries_to_points(state_parks_gdf)
        
        if state_parks_df.empty:
            print("Failed to convert state parks to points")
            return pd.DataFrame()
        
        # Step 3: Merge with existing curated parks
        enhanced_df = self.merge_with_existing_parks(state_parks_df)
        
        # Step 4: Save enhanced dataset
        self.save_enhanced_parks_data(enhanced_df)
        
        return enhanced_df

def main():
    """Main execution function"""
    downloader = CAStateParksDownloader()
    result_df = downloader.create_enhanced_parks_dataset()
    
    if not result_df.empty:
        print(f"\n=== SUCCESS ===")
        print(f"Enhanced parks dataset created!")
        print(f"Ready for CTCAC amenity analysis with official state parks data")
        
        # Show sample data
        print(f"\nSample enhanced parks:")
        for i, row in result_df.head(5).iterrows():
            source = row.get('data_source', 'unknown')
            park_type = row.get('park_type', 'unknown')
            print(f"{row['name']} ({park_type}) - Source: {source}")
            print(f"  Coordinates: {row['latitude']:.4f}, {row['longitude']:.4f}")
    else:
        print("Failed to create enhanced parks dataset")

if __name__ == "__main__":
    main()