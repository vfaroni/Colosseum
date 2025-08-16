#!/usr/bin/env python3
"""
Texas Infrastructure Data Processing Script
Processes downloaded infrastructure datasets for Texas affordable housing analysis.

Cleans, filters, geocodes, and organizes datasets for proximity analysis.
Author: Claude Code
Date: July 2025
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import requests
import time
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas")
CENSUS_API_KEY = "06ece0121263282cd9ffd753215b007b8f9a3dfc"

class TexasInfrastructureProcessor:
    """Process and clean Texas infrastructure datasets."""
    
    def __init__(self):
        self.processed_files = []
        
    def geocode_address(self, address, city=None, state="TX"):
        """Geocode address using Census Geocoder API."""
        if pd.isna(address) or address == "":
            return None, None
            
        # Construct full address
        full_address = f"{address}, {city}, {state}" if city else f"{address}, {state}"
        
        # Census Geocoder API
        url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
        params = {
            'address': full_address,
            'benchmark': 'Public_AR_Current',
            'format': 'json'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('result', {}).get('addressMatches'):
                match = data['result']['addressMatches'][0]
                coords = match['coordinates']
                return coords['x'], coords['y']  # longitude, latitude
                
        except Exception as e:
            logger.warning(f"Geocoding failed for {address}: {e}")
            
        return None, None
    
    def process_hospitals_thcic(self):
        """Process THCIC hospital data (manual download required)."""
        input_file = BASE_DIR / "Healthcare" / "TX_hospitals_THCIC_2025.csv"
        
        if not input_file.exists():
            logger.warning(f"Hospital file not found: {input_file}")
            return
            
        try:
            df = pd.read_csv(input_file)
            logger.info(f"Processing {len(df)} hospitals from THCIC")
            
            # Standardize column names (adjust based on actual THCIC format)
            df_clean = df.copy()
            if 'latitude' not in df_clean.columns and 'longitude' not in df_clean.columns:
                # Geocode addresses if coordinates missing
                logger.info("Geocoding hospital addresses...")
                
                coords = []
                for idx, row in df_clean.iterrows():
                    if idx % 10 == 0:
                        logger.info(f"Geocoded {idx}/{len(df_clean)} hospitals")
                    
                    address = row.get('address', '')
                    city = row.get('city', '')
                    lon, lat = self.geocode_address(address, city)
                    coords.append({'longitude': lon, 'latitude': lat})
                    
                    time.sleep(0.1)  # Rate limiting
                
                coords_df = pd.DataFrame(coords)
                df_clean = pd.concat([df_clean, coords_df], axis=1)
            
            # Remove rows without coordinates
            df_clean = df_clean.dropna(subset=['latitude', 'longitude'])
            
            # Save processed file
            output_file = BASE_DIR / "Healthcare" / "TX_hospitals_processed_2025.csv"
            df_clean.to_csv(output_file, index=False)
            
            # Create GeoJSON
            if len(df_clean) > 0:
                gdf = gpd.GeoDataFrame(
                    df_clean, 
                    geometry=gpd.points_from_xy(df_clean.longitude, df_clean.latitude),
                    crs='EPSG:4326'
                )
                geojson_file = BASE_DIR / "Healthcare" / "TX_hospitals_processed_2025.geojson"
                gdf.to_file(geojson_file, driver='GeoJSON')
                
                logger.info(f"Processed {len(df_clean)} hospitals: {output_file}")
                self.processed_files.append(str(output_file))
            
        except Exception as e:
            logger.error(f"Failed to process hospitals: {e}")
    
    def process_libraries_imls(self):
        """Process IMLS library data."""
        input_file = BASE_DIR / "Libraries" / "TX_public_libraries_IMLS_2022.csv"
        
        if not input_file.exists():
            logger.warning(f"Libraries file not found: {input_file}")
            return
            
        try:
            df = pd.read_csv(input_file)
            logger.info(f"Processing {len(df)} libraries from IMLS")
            
            # Clean and geocode if needed
            df_clean = df.copy()
            
            # Geocode addresses if coordinates missing
            if 'latitude' not in df.columns or 'longitude' not in df.columns:
                logger.info("Geocoding library addresses...")
                
                coords = []
                for idx, row in df_clean.iterrows():
                    if idx % 10 == 0:
                        logger.info(f"Geocoded {idx}/{len(df_clean)} libraries")
                    
                    address = f"{row.get('ADDRESS', '')} {row.get('ADDRESS2', '')}"
                    city = row.get('CITY', '')
                    lon, lat = self.geocode_address(address.strip(), city)
                    coords.append({'longitude': lon, 'latitude': lat})
                    
                    time.sleep(0.1)
                
                coords_df = pd.DataFrame(coords)
                df_clean = pd.concat([df_clean, coords_df], axis=1)
            
            # Remove libraries without coordinates
            df_clean = df_clean.dropna(subset=['latitude', 'longitude'])
            
            # Create GeoJSON
            if len(df_clean) > 0:
                gdf = gpd.GeoDataFrame(
                    df_clean,
                    geometry=gpd.points_from_xy(df_clean.longitude, df_clean.latitude),
                    crs='EPSG:4326'
                )
                
                output_file = BASE_DIR / "Libraries" / "TX_libraries_processed_2025.geojson"
                gdf.to_file(output_file, driver='GeoJSON')
                
                logger.info(f"Processed {len(df_clean)} libraries: {output_file}")
                self.processed_files.append(str(output_file))
            
        except Exception as e:
            logger.error(f"Failed to process libraries: {e}")
    
    def validate_city_boundaries(self):
        """Validate and optimize city boundaries data."""
        boundaries_dir = BASE_DIR / "City_Boundaries"
        geojson_file = boundaries_dir / "TX_cities_2024.geojson"
        
        if geojson_file.exists():
            try:
                gdf = gpd.read_file(geojson_file)
                logger.info(f"Loaded {len(gdf)} Texas cities/places")
                
                # Basic validation
                total_area = gdf.geometry.area.sum()
                logger.info(f"Total area covered: {total_area:.2f} square degrees")
                
                # Create simplified version for faster proximity analysis
                gdf_simplified = gdf.copy()
                gdf_simplified['geometry'] = gdf_simplified.geometry.simplify(0.001)
                
                simplified_file = boundaries_dir / "TX_cities_simplified_2025.geojson"
                gdf_simplified.to_file(simplified_file, driver='GeoJSON')
                
                logger.info(f"Created simplified boundaries: {simplified_file}")
                self.processed_files.append(str(simplified_file))
                
            except Exception as e:
                logger.error(f"Failed to process city boundaries: {e}")
    
    def create_proximity_datasets(self):
        """Create optimized datasets for proximity analysis."""
        logger.info("Creating proximity analysis datasets...")
        
        # Combine all point datasets
        datasets = []
        
        # Schools (already available)
        schools_file = BASE_DIR / "TX_Public_Schools" / "Schools_2024_to_2025.geojson"
        if schools_file.exists():
            schools_gdf = gpd.read_file(schools_file)
            schools_gdf['amenity_type'] = 'school'
            schools_gdf['name'] = schools_gdf.get('SchoolName', schools_gdf.get('School_Name', ''))
            datasets.append(schools_gdf[['name', 'amenity_type', 'geometry']])
        
        # Hospitals
        hospitals_file = BASE_DIR / "Healthcare" / "TX_hospitals_processed_2025.geojson"
        if hospitals_file.exists():
            hospitals_gdf = gpd.read_file(hospitals_file)
            hospitals_gdf['amenity_type'] = 'hospital'
            hospitals_gdf['name'] = hospitals_gdf.get('hospital_name', hospitals_gdf.get('name', ''))
            datasets.append(hospitals_gdf[['name', 'amenity_type', 'geometry']])
        
        # Libraries
        libraries_file = BASE_DIR / "Libraries" / "TX_libraries_processed_2025.geojson"
        if libraries_file.exists():
            libraries_gdf = gpd.read_file(libraries_file)
            libraries_gdf['amenity_type'] = 'library'
            libraries_gdf['name'] = libraries_gdf.get('LIBNAME', libraries_gdf.get('name', ''))
            datasets.append(libraries_gdf[['name', 'amenity_type', 'geometry']])
        
        if datasets:
            # Combine all amenities
            combined_gdf = gpd.GeoDataFrame(pd.concat(datasets, ignore_index=True))
            
            output_file = BASE_DIR / "TX_combined_amenities_2025.geojson"
            combined_gdf.to_file(output_file, driver='GeoJSON')
            
            logger.info(f"Created combined amenities dataset: {output_file}")
            logger.info(f"Total amenities: {len(combined_gdf)}")
            logger.info(f"By type: {combined_gdf['amenity_type'].value_counts().to_dict()}")
            
            self.processed_files.append(str(output_file))
    
    def create_dataset_index(self):
        """Create master index of all processed datasets."""
        index_data = []
        
        # Scan all directories for processed files
        for subdir in ['Healthcare', 'Libraries', 'City_Boundaries', 'Water_Sewer_Infrastructure', 'Electric_Utilities']:
            dir_path = BASE_DIR / subdir
            if dir_path.exists():
                for file_path in dir_path.rglob('*'):
                    if file_path.is_file() and file_path.suffix in ['.csv', '.geojson', '.gpkg', '.shp']:
                        try:
                            file_size = file_path.stat().st_size
                            modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                            
                            # Try to get record count
                            record_count = None
                            if file_path.suffix == '.csv':
                                df = pd.read_csv(file_path, nrows=1)
                                record_count = len(pd.read_csv(file_path))
                            elif file_path.suffix in ['.geojson', '.gpkg']:
                                gdf = gpd.read_file(file_path, rows=1)
                                record_count = len(gpd.read_file(file_path))
                            
                            index_data.append({
                                'dataset_name': file_path.stem,
                                'file_path': str(file_path.relative_to(BASE_DIR)),
                                'format': file_path.suffix[1:],
                                'category': subdir,
                                'file_size_bytes': file_size,
                                'record_count': record_count,
                                'last_modified': modified_time.isoformat(),
                                'description': self._get_dataset_description(file_path.name)
                            })
                            
                        except Exception as e:
                            logger.warning(f"Could not index {file_path}: {e}")
        
        # Create index DataFrame
        index_df = pd.DataFrame(index_data)
        index_file = BASE_DIR / "TX_infrastructure_datasets_index.csv"
        index_df.to_csv(index_file, index=False)
        
        logger.info(f"Created dataset index: {index_file}")
        logger.info(f"Indexed {len(index_df)} datasets")
        
        return index_file
    
    def _get_dataset_description(self, filename):
        """Get description for dataset based on filename."""
        descriptions = {
            'TX_hospitals_processed_2025': 'Texas hospitals with coordinates (THCIC)',
            'TX_libraries_processed_2025': 'Texas public libraries (IMLS)',
            'TX_cities_2024': 'Texas incorporated places (Census TIGER)',
            'TX_cities_simplified_2025': 'Simplified Texas city boundaries for analysis',
            'TX_electric_service_territories_HIFLD_2025': 'Electric utility service areas (HIFLD)',
            'TX_combined_amenities_2025': 'Combined schools, hospitals, libraries for proximity analysis'
        }
        
        for key, desc in descriptions.items():
            if key in filename:
                return desc
        
        return 'Texas infrastructure dataset'
    
    def run_processing(self):
        """Run complete processing pipeline."""
        logger.info("Starting Texas Infrastructure Data Processing")
        
        # Process individual datasets
        self.process_hospitals_thcic()
        self.process_libraries_imls()
        self.validate_city_boundaries()
        
        # Create combined datasets
        self.create_proximity_datasets()
        
        # Create master index
        index_file = self.create_dataset_index()
        
        logger.info("Processing complete!")
        logger.info(f"Processed files: {len(self.processed_files)}")
        logger.info(f"Master index: {index_file}")

def main():
    processor = TexasInfrastructureProcessor()
    processor.run_processing()

if __name__ == "__main__":
    main()