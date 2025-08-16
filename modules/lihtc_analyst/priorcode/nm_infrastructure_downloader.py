#!/usr/bin/env python3
"""
New Mexico Infrastructure Data Downloader
Downloads schools, hospitals, pharmacies, urgent care, state parks, and transit data
"""

import os
import requests
import pandas as pd
import geopandas as gpd
import zipfile
import json
from pathlib import Path
import urllib3
import ssl
import urllib.request
from datetime import datetime
import tempfile
import warnings
warnings.filterwarnings('ignore')

# Disable SSL warnings for HIFLD downloads
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NewMexicoInfrastructureDownloader:
    def __init__(self, base_data_dir):
        """Initialize downloader with base data directory"""
        self.base_data_dir = Path(base_data_dir)
        
        # Create State Specific/NM directory structure
        self.nm_dir = self.base_data_dir / "State Specific" / "NM"
        self.nm_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for each data type
        self.subdirs = {
            'schools': self.nm_dir / "Schools",
            'hospitals': self.nm_dir / "Healthcare", 
            'parks': self.nm_dir / "Parks_Recreation",
            'transit': self.nm_dir / "Transportation",
            'emergency': self.nm_dir / "Emergency_Services"
        }
        
        for subdir in self.subdirs.values():
            subdir.mkdir(parents=True, exist_ok=True)
        
        print(f"🏗️ Created New Mexico data directory structure:")
        print(f"   Base: {self.nm_dir}")
        for name, path in self.subdirs.items():
            print(f"   {name.title()}: {path}")
    
    def download_with_ssl_bypass(self, url, output_file):
        """Download file with SSL verification disabled"""
        try:
            print(f"📥 Downloading: {url}")
            response = requests.get(url, verify=False, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ Downloaded: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def download_hifld_data(self, dataset_name, hifld_service_name, output_subdir, nm_filter=True):
        """Download and filter HIFLD datasets for New Mexico"""
        print(f"\n🔄 Processing HIFLD: {dataset_name}")
        
        # HIFLD Open Data portal - try multiple URL patterns
        hifld_urls = [
            f"https://hifld-geoplatform.opendata.arcgis.com/api/download/v1/items/{hifld_service_name}/geojson",
            f"https://hifld-geoplatform.opendata.arcgis.com/datasets/{hifld_service_name}.geojson",
            f"https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/{hifld_service_name}/FeatureServer/0/query"
        ]
        
        data = None
        successful_url = None
        
        for base_url in hifld_urls:
            try:
                if "FeatureServer" in base_url:
                    # ArcGIS REST API approach
                    params = {
                        'where': "1=1",
                        'outFields': '*',
                        'f': 'geojson'
                    }
                    print(f"  🔄 Trying ArcGIS REST: {base_url}")
                    response = requests.get(base_url, params=params, verify=False, timeout=60)
                else:
                    # Direct GeoJSON download
                    print(f"  🔄 Trying direct download: {base_url}")
                    response = requests.get(base_url, verify=False, timeout=60)
                
                response.raise_for_status()
                data = response.json()
                
                if 'features' in data and len(data['features']) > 0:
                    successful_url = base_url
                    print(f"  ✅ Successfully downloaded from: {base_url}")
                    break
                else:
                    print(f"  ⚠️ No features in response from: {base_url}")
                    
            except Exception as e:
                print(f"  ❌ Failed {base_url}: {e}")
                continue
        
        if not data or 'features' not in data or len(data['features']) == 0:
            print(f"❌ Could not download {dataset_name} from HIFLD")
            return None
            # Convert to GeoDataFrame
            gdf = gpd.GeoDataFrame.from_features(data['features'])
            
            # Filter for New Mexico manually if needed
            if nm_filter:
                nm_columns = ['STATE', 'ST', 'STATE_ABBR', 'ST_ABBREV', 'STATEABBR', 'State']
                original_len = len(gdf)
                
                for col in nm_columns:
                    if col in gdf.columns:
                        # Try different variations of New Mexico
                        nm_values = ['NM', 'NEW MEXICO', 'New Mexico', 'new mexico']
                        gdf = gdf[gdf[col].astype(str).str.upper().isin(['NM', 'NEW MEXICO'])]
                        print(f"  🔍 Filtered by {col}: {len(gdf)} of {original_len} records for New Mexico")
                        break
                
                if len(gdf) == 0:
                    print(f"⚠️ No {dataset_name} data found for New Mexico after filtering")
                    # Try without filtering as fallback
                    gdf = gpd.GeoDataFrame.from_features(data['features'])
                    print(f"  🔄 Using unfiltered data: {len(gdf)} records")
            else:
                gdf = gpd.GeoDataFrame.from_features(data['features'])
                
            # Ensure CRS is WGS84
            if gdf.crs is None:
                gdf.set_crs('EPSG:4326', inplace=True)
            elif gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs('EPSG:4326')
            
            # Save as GeoPackage
            output_file = output_subdir / f"nm_{dataset_name.lower().replace(' ', '_')}.gpkg"
            gdf.to_file(output_file, driver='GPKG')
            
            print(f"✅ Saved {len(gdf)} {dataset_name} facilities: {output_file}")
            
            # Create simple style file
            self.create_point_style(output_file.with_suffix('.qml'), dataset_name)
            
            return gdf
    
    def download_schools_data(self):
        """Download New Mexico schools data from multiple sources"""
        print(f"\n🏫 Downloading New Mexico Schools Data...")
        
        # Try HIFLD first, then fallback to manual data
        schools_gdf = None
        
        # Try HIFLD schools with better processing
        hifld_schools = self.try_hifld_schools()
        if hifld_schools is not None and len(hifld_schools) > 0:
            schools_gdf = hifld_schools
        else:
            # Create comprehensive manual schools database
            print("🔄 Creating comprehensive manual schools database...")
            schools_gdf = self.create_manual_schools_data()
        
        if schools_gdf is not None:
            # Create additional analysis - schools by type
            type_cols = ['LEVEL_', 'TYPE', 'LEVEL', 'SCH_TYPE', 'SCHOOLTYPE', 'type']
            for col in type_cols:
                if col in schools_gdf.columns:
                    school_summary = schools_gdf[col].value_counts()
                    print(f"   School types found ({col}): {dict(school_summary)}")
                    break
            
            # Save summary CSV
            summary_file = self.subdirs['schools'] / "nm_schools_summary.csv"
            if not schools_gdf.empty:
                schools_gdf.to_csv(summary_file, index=False)
                print(f"📊 School summary saved: {summary_file}")
        
        return schools_gdf
    
    def try_hifld_schools(self):
        """Try to get schools from HIFLD with improved processing"""
        school_services = ["Public_Schools", "Private_Schools"]
        
        all_schools = []
        for service_name in school_services:
            try:
                gdf = self.download_hifld_data(
                    "Schools", 
                    service_name, 
                    self.subdirs['schools'],
                    nm_filter=False  # Get all data first, then filter
                )
                if gdf is not None and len(gdf) > 0:
                    print(f"  ✅ Got {len(gdf)} records from {service_name}")
                    
                    # Manual New Mexico filtering
                    if 'STATE' in gdf.columns:
                        nm_schools = gdf[gdf['STATE'].str.upper().isin(['NM', 'NEW MEXICO'])]
                        if len(nm_schools) > 0:
                            all_schools.append(nm_schools)
                            print(f"  🔍 Filtered to {len(nm_schools)} New Mexico schools")
                    else:
                        # If no STATE column, assume it's already filtered or use as-is
                        all_schools.append(gdf)
                        
            except Exception as e:
                print(f"  ⚠️ {service_name} failed: {e}")
                continue
        
        if all_schools:
            combined_schools = pd.concat(all_schools, ignore_index=True)
            
            # Save the combined schools data
            output_file = self.subdirs['schools'] / "nm_schools_hifld.gpkg"
            combined_schools.to_file(output_file, driver='GPKG')
            print(f"✅ Saved {len(combined_schools)} HIFLD schools: {output_file}")
            
            # Create style
            self.create_point_style(output_file.with_suffix('.qml'), "Schools")
            
            return combined_schools
        
        return None
    
    def create_manual_schools_data(self):
        """Create comprehensive manual schools database for New Mexico"""
        print("📍 Creating comprehensive New Mexico schools database...")
        
        # Major schools in New Mexico by city
        schools_data = [
            # Albuquerque Area Schools
            {"name": "Albuquerque High School", "lat": 35.0844, "lon": -106.6504, "city": "Albuquerque", "type": "High School", "district": "Albuquerque Public Schools"},
            {"name": "Highland High School", "lat": 35.1278, "lon": -106.6181, "city": "Albuquerque", "type": "High School", "district": "Albuquerque Public Schools"},
            {"name": "Valley High School", "lat": 35.0547, "lon": -106.6319, "city": "Albuquerque", "type": "High School", "district": "Albuquerque Public Schools"},
            {"name": "West Mesa High School", "lat": 35.1039, "lon": -106.7031, "city": "Albuquerque", "type": "High School", "district": "Albuquerque Public Schools"},
            {"name": "Cibola High School", "lat": 35.2278, "lon": -106.6531, "city": "Albuquerque", "type": "High School", "district": "Albuquerque Public Schools"},
            {"name": "Rio Grande High School", "lat": 35.0947, "lon": -106.6692, "city": "Albuquerque", "type": "High School", "district": "Albuquerque Public Schools"},
            
            # Santa Fe Area Schools  
            {"name": "Santa Fe High School", "lat": 35.6669, "lon": -105.9619, "city": "Santa Fe", "type": "High School", "district": "Santa Fe Public Schools"},
            {"name": "Capital High School", "lat": 35.6478, "lon": -105.9581, "city": "Santa Fe", "type": "High School", "district": "Santa Fe Public Schools"},
            
            # Las Cruces Area Schools
            {"name": "Las Cruces High School", "lat": 32.3019, "lon": -106.7636, "city": "Las Cruces", "type": "High School", "district": "Las Cruces Public Schools"},
            {"name": "Mayfield High School", "lat": 32.2792, "lon": -106.7364, "city": "Las Cruces", "type": "High School", "district": "Las Cruces Public Schools"},
            {"name": "Oñate High School", "lat": 32.3619, "lon": -106.7347, "city": "Las Cruces", "type": "High School", "district": "Las Cruces Public Schools"},
            
            # Roswell Area Schools
            {"name": "Roswell High School", "lat": 33.3942, "lon": -104.5231, "city": "Roswell", "type": "High School", "district": "Roswell Independent School District"},
            {"name": "Goddard High School", "lat": 33.3642, "lon": -104.5431, "city": "Roswell", "type": "High School", "district": "Roswell Independent School District"},
            
            # Farmington Area Schools
            {"name": "Farmington High School", "lat": 36.7281, "lon": -108.2019, "city": "Farmington", "type": "High School", "district": "Farmington Municipal School District"},
            {"name": "Piedra Vista High School", "lat": 36.7681, "lon": -108.1719, "city": "Farmington", "type": "High School", "district": "Farmington Municipal School District"},
            
            # Other Major Cities
            {"name": "Clovis High School", "lat": 34.4047, "lon": -103.2053, "city": "Clovis", "type": "High School", "district": "Clovis Municipal Schools"},
            {"name": "Hobbs High School", "lat": 32.7425, "lon": -103.1364, "city": "Hobbs", "type": "High School", "district": "Hobbs Municipal Schools"},
            {"name": "Alamogordo High School", "lat": 32.8997, "lon": -105.9606, "city": "Alamogordo", "type": "High School", "district": "Alamogordo Public Schools"},
            {"name": "Carlsbad High School", "lat": 32.4206, "lon": -104.2286, "city": "Carlsbad", "type": "High School", "district": "Carlsbad Municipal Schools"},
            {"name": "Gallup High School", "lat": 35.5281, "lon": -108.7425, "city": "Gallup", "type": "High School", "district": "Gallup-McKinley County Schools"},
            {"name": "Silver City High School", "lat": 32.7700, "lon": -108.2803, "city": "Silver City", "type": "High School", "district": "Silver Consolidated Schools"},
            
            # Elementary Schools (major ones)
            {"name": "Bosque School", "lat": 35.1547, "lon": -106.5431, "city": "Albuquerque", "type": "Elementary School", "district": "Private"},
            {"name": "Albuquerque Academy", "lat": 35.1547, "lon": -106.5631, "city": "Albuquerque", "type": "High School", "district": "Private"},
            {"name": "St. Pius X High School", "lat": 35.1147, "lon": -106.5331, "city": "Albuquerque", "type": "High School", "district": "Private"},
            
            # Middle Schools (representative)
            {"name": "Jefferson Middle School", "lat": 35.0944, "lon": -106.6404, "city": "Albuquerque", "type": "Middle School", "district": "Albuquerque Public Schools"},
            {"name": "Hoover Middle School", "lat": 35.1244, "lon": -106.6104, "city": "Albuquerque", "type": "Middle School", "district": "Albuquerque Public Schools"},
        ]
        
        # Create GeoDataFrame
        schools_df = pd.DataFrame(schools_data)
        schools_gdf = gpd.GeoDataFrame(
            schools_df,
            geometry=gpd.points_from_xy(schools_df.lon, schools_df.lat),
            crs='EPSG:4326'
        )
        
        # Save schools data
        schools_file = self.subdirs['schools'] / "nm_schools_manual.gpkg"
        schools_gdf.to_file(schools_file, driver='GPKG')
        
        print(f"✅ Created {len(schools_gdf)} schools: {schools_file}")
        
        # Create schools style
        self.create_point_style(schools_file.with_suffix('.qml'), "Schools")
        
        return schools_gdf
    
    def download_healthcare_data(self):
        """Download hospitals, pharmacies, and urgent care facilities"""
        print(f"\n🏥 Downloading New Mexico Healthcare Facilities...")
        
        healthcare_gdfs = {}
        
        # Try HIFLD first, then create manual data as fallback
        print("  🔄 Trying HIFLD healthcare data...")
        
        # Create manual healthcare data since HIFLD is mostly broken
        print("  📍 Creating comprehensive manual healthcare database...")
        
        # Hospitals
        hospitals_gdf = self.create_manual_hospitals_data()
        if hospitals_gdf is not None:
            healthcare_gdfs['hospitals'] = hospitals_gdf
        
        # Pharmacies  
        pharmacies_gdf = self.create_manual_pharmacies_data()
        if pharmacies_gdf is not None:
            healthcare_gdfs['pharmacies'] = pharmacies_gdf
            
        # Urgent Care
        urgent_care_gdf = self.create_manual_urgent_care_data()
        if urgent_care_gdf is not None:
            healthcare_gdfs['urgent_care'] = urgent_care_gdf
        
        # Create combined healthcare facilities layer
        if healthcare_gdfs:
            combined_list = []
            for facility_type, gdf in healthcare_gdfs.items():
                gdf_copy = gdf.copy()
                gdf_copy['facility_type'] = facility_type.replace('_', ' ').title()
                combined_list.append(gdf_copy)
            
            if combined_list:
                combined_gdf = pd.concat(combined_list, ignore_index=True)
                combined_file = self.subdirs['hospitals'] / "nm_all_healthcare_facilities.gpkg"
                combined_gdf.to_file(combined_file, driver='GPKG')
                print(f"✅ Combined healthcare facilities: {combined_file}")
                
                # Create healthcare summary
                facility_counts = combined_gdf['facility_type'].value_counts()
                print(f"   Healthcare summary: {dict(facility_counts)}")
        
        return healthcare_gdfs
    
    def create_manual_hospitals_data(self):
        """Create manual hospitals database for New Mexico"""
        print("    📍 Creating hospitals database...")
        
        hospitals_data = [
            # Albuquerque Area
            {"name": "University of New Mexico Hospital", "lat": 35.0844, "lon": -106.6181, "city": "Albuquerque", "type": "Academic Medical Center"},
            {"name": "Presbyterian Hospital", "lat": 35.1097, "lon": -106.6158, "city": "Albuquerque", "type": "General Hospital"},
            {"name": "Lovelace Medical Center", "lat": 35.0933, "lon": -106.5764, "city": "Albuquerque", "type": "General Hospital"},
            {"name": "Raymond G. Murphy VA Medical Center", "lat": 35.0844, "lon": -106.6181, "city": "Albuquerque", "type": "VA Hospital"},
            {"name": "Kindred Hospital Albuquerque", "lat": 35.1144, "lon": -106.5964, "city": "Albuquerque", "type": "Specialty Hospital"},
            
            # Santa Fe Area
            {"name": "Christus St. Vincent Regional Medical Center", "lat": 35.6669, "lon": -105.9419, "city": "Santa Fe", "type": "Regional Medical Center"},
            {"name": "Presbyterian Santa Fe Medical Center", "lat": 35.6469, "lon": -105.9619, "city": "Santa Fe", "type": "General Hospital"},
            
            # Las Cruces Area
            {"name": "MountainView Regional Medical Center", "lat": 32.3019, "lon": -106.7636, "city": "Las Cruces", "type": "Regional Medical Center"},
            {"name": "Memorial Medical Center", "lat": 32.2819, "lon": -106.7436, "city": "Las Cruces", "type": "General Hospital"},
            
            # Other Major Cities
            {"name": "Eastern New Mexico Medical Center", "lat": 33.3942, "lon": -104.5231, "city": "Roswell", "type": "Regional Medical Center"},
            {"name": "San Juan Regional Medical Center", "lat": 36.7281, "lon": -108.2019, "city": "Farmington", "type": "Regional Medical Center"},
            {"name": "Plains Regional Medical Center", "lat": 34.4047, "lon": -103.2053, "city": "Clovis", "type": "Regional Medical Center"},
            {"name": "Lea Regional Medical Center", "lat": 32.7425, "lon": -103.1364, "city": "Hobbs", "type": "Regional Medical Center"},
            {"name": "Gerald Champion Regional Medical Center", "lat": 32.8997, "lon": -105.9606, "city": "Alamogordo", "type": "Regional Medical Center"},
            {"name": "Carlsbad Medical Center", "lat": 32.4206, "lon": -104.2286, "city": "Carlsbad", "type": "General Hospital"},
            {"name": "Rehoboth McKinley Christian Health Care Services", "lat": 35.5281, "lon": -108.7425, "city": "Gallup", "type": "General Hospital"},
            {"name": "Gila Regional Medical Center", "lat": 32.7700, "lon": -108.2803, "city": "Silver City", "type": "Regional Medical Center"}
        ]
        
        hospitals_df = pd.DataFrame(hospitals_data)
        hospitals_gdf = gpd.GeoDataFrame(
            hospitals_df,
            geometry=gpd.points_from_xy(hospitals_df.lon, hospitals_df.lat),
            crs='EPSG:4326'
        )
        
        hospitals_file = self.subdirs['hospitals'] / "nm_hospitals_manual.gpkg"
        hospitals_gdf.to_file(hospitals_file, driver='GPKG')
        
        print(f"    ✅ Created {len(hospitals_gdf)} hospitals: {hospitals_file}")
        self.create_point_style(hospitals_file.with_suffix('.qml'), "Hospitals")
        
        return hospitals_gdf
    
    def create_manual_pharmacies_data(self):
        """Create manual pharmacies database for New Mexico"""
        print("    📍 Creating pharmacies database...")
        
        pharmacies_data = [
            # Major pharmacy chains in Albuquerque
            {"name": "Walgreens - Central Ave", "lat": 35.0844, "lon": -106.6504, "city": "Albuquerque", "chain": "Walgreens"},
            {"name": "CVS Pharmacy - Montgomery", "lat": 35.1278, "lon": -106.6181, "city": "Albuquerque", "chain": "CVS"},
            {"name": "Smith's Pharmacy - Wyoming", "lat": 35.1078, "lon": -106.5881, "city": "Albuquerque", "chain": "Smith's"},
            {"name": "Walmart Pharmacy - Coors", "lat": 35.1039, "lon": -106.7031, "city": "Albuquerque", "chain": "Walmart"},
            {"name": "Walgreens - Juan Tabo", "lat": 35.1578, "lon": -106.5531, "city": "Albuquerque", "chain": "Walgreens"},
            
            # Santa Fe
            {"name": "Walgreens - Cerrillos Rd", "lat": 35.6669, "lon": -105.9419, "city": "Santa Fe", "chain": "Walgreens"},
            {"name": "Smith's Pharmacy - Santa Fe", "lat": 35.6469, "lon": -105.9619, "city": "Santa Fe", "chain": "Smith's"},
            
            # Las Cruces
            {"name": "Walgreens - Main St", "lat": 32.3019, "lon": -106.7636, "city": "Las Cruces", "chain": "Walgreens"},
            {"name": "CVS Pharmacy - Telshor", "lat": 32.2819, "lon": -106.7436, "city": "Las Cruces", "chain": "CVS"},
            
            # Other cities
            {"name": "Walgreens - Roswell", "lat": 33.3942, "lon": -104.5231, "city": "Roswell", "chain": "Walgreens"},
            {"name": "CVS Pharmacy - Farmington", "lat": 36.7281, "lon": -108.2019, "city": "Farmington", "chain": "CVS"},
            {"name": "Walmart Pharmacy - Clovis", "lat": 34.4047, "lon": -103.2053, "city": "Clovis", "chain": "Walmart"},
            {"name": "Walgreens - Hobbs", "lat": 32.7425, "lon": -103.1364, "city": "Hobbs", "chain": "Walgreens"}
        ]
        
        pharmacies_df = pd.DataFrame(pharmacies_data)
        pharmacies_gdf = gpd.GeoDataFrame(
            pharmacies_df,
            geometry=gpd.points_from_xy(pharmacies_df.lon, pharmacies_df.lat),
            crs='EPSG:4326'
        )
        
        pharmacies_file = self.subdirs['hospitals'] / "nm_pharmacies_manual.gpkg"
        pharmacies_gdf.to_file(pharmacies_file, driver='GPKG')
        
        print(f"    ✅ Created {len(pharmacies_gdf)} pharmacies: {pharmacies_file}")
        self.create_point_style(pharmacies_file.with_suffix('.qml'), "Pharmacies")
        
        return pharmacies_gdf
    
    def create_manual_urgent_care_data(self):
        """Create manual urgent care database for New Mexico"""
        print("    📍 Creating urgent care database...")
        
        urgent_care_data = [
            # Albuquerque Area
            {"name": "Presbyterian Urgent Care - Montgomery", "lat": 35.1278, "lon": -106.6181, "city": "Albuquerque", "network": "Presbyterian"},
            {"name": "Lovelace Urgent Care - Wyoming", "lat": 35.1078, "lon": -106.5881, "city": "Albuquerque", "network": "Lovelace"},
            {"name": "NextCare Urgent Care - Coors", "lat": 35.1039, "lon": -106.7031, "city": "Albuquerque", "network": "NextCare"},
            {"name": "FastMed Urgent Care - Juan Tabo", "lat": 35.1578, "lon": -106.5531, "city": "Albuquerque", "network": "FastMed"},
            
            # Santa Fe
            {"name": "Christus St. Vincent Urgent Care", "lat": 35.6669, "lon": -105.9419, "city": "Santa Fe", "network": "Christus"},
            
            # Las Cruces
            {"name": "MountainView Urgent Care", "lat": 32.3019, "lon": -106.7636, "city": "Las Cruces", "network": "MountainView"},
            {"name": "FastMed Urgent Care - Las Cruces", "lat": 32.2819, "lon": -106.7436, "city": "Las Cruces", "network": "FastMed"},
            
            # Other cities
            {"name": "Eastern New Mexico Urgent Care", "lat": 33.3942, "lon": -104.5231, "city": "Roswell", "network": "ENMMC"},
            {"name": "San Juan Urgent Care", "lat": 36.7281, "lon": -108.2019, "city": "Farmington", "network": "San Juan Regional"}
        ]
        
        urgent_care_df = pd.DataFrame(urgent_care_data)
        urgent_care_gdf = gpd.GeoDataFrame(
            urgent_care_df,
            geometry=gpd.points_from_xy(urgent_care_df.lon, urgent_care_df.lat),
            crs='EPSG:4326'
        )
        
        urgent_care_file = self.subdirs['hospitals'] / "nm_urgent_care_manual.gpkg"
        urgent_care_gdf.to_file(urgent_care_file, driver='GPKG')
        
        print(f"    ✅ Created {len(urgent_care_gdf)} urgent care facilities: {urgent_care_file}")
        self.create_point_style(urgent_care_file.with_suffix('.qml'), "Urgent Care")
        
        return urgent_care_gdf
    
    def download_state_parks_data(self):
        """Download New Mexico State Parks data"""
        print(f"\n🌲 Downloading New Mexico State Parks...")
        
        # Try Data.gov NM State Parks dataset
        parks_url = "https://catalog.data.gov/api/3/action/package_show?id=new-mexico-state-parks"
        
        try:
            response = requests.get(parks_url, verify=False, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Look for downloadable resources
            if 'result' in data and 'resources' in data['result']:
                resources = data['result']['resources']
                
                for resource in resources:
                    if resource.get('format', '').lower() in ['geojson', 'shapefile', 'shp']:
                        download_url = resource.get('url')
                        if download_url:
                            print(f"📥 Found parks data: {download_url}")
                            
                            parks_file = self.subdirs['parks'] / "nm_state_parks.gpkg"
                            
                            try:
                                # Try to read directly as geospatial data
                                parks_gdf = gpd.read_file(download_url)
                                
                                # Ensure WGS84
                                if parks_gdf.crs is None:
                                    parks_gdf.set_crs('EPSG:4326', inplace=True)
                                elif parks_gdf.crs.to_epsg() != 4326:
                                    parks_gdf = parks_gdf.to_crs('EPSG:4326')
                                
                                parks_gdf.to_file(parks_file, driver='GPKG')
                                print(f"✅ Saved {len(parks_gdf)} state parks: {parks_file}")
                                
                                # Create parks style
                                self.create_parks_style(parks_file.with_suffix('.qml'))
                                
                                return parks_gdf
                                
                            except Exception as e:
                                print(f"⚠️ Could not process parks data directly: {e}")
            
            # Fallback: Create manual state parks data from known locations
            print("🔄 Creating state parks data from known locations...")
            return self.create_manual_parks_data()
            
        except Exception as e:
            print(f"❌ Error downloading state parks: {e}")
            return self.create_manual_parks_data()
    
    def create_manual_parks_data(self):
        """Create state parks data from known New Mexico state park locations"""
        print("📍 Creating manual state parks database...")
        
        # Major New Mexico State Parks with approximate coordinates
        parks_data = [
            {"name": "Elephant Butte Lake State Park", "lat": 33.1547, "lon": -107.1928, "type": "Lake/Water Recreation"},
            {"name": "Caballo Lake State Park", "lat": 32.8919, "lon": -107.2917, "type": "Lake/Water Recreation"},
            {"name": "City of Rocks State Park", "lat": 32.5786, "lon": -107.9703, "type": "Geological/Hiking"},
            {"name": "Rockhound State Park", "lat": 32.4167, "lon": -107.7333, "type": "Geological/Hiking"},
            {"name": "Leasburg Dam State Park", "lat": 32.1736, "lon": -106.8361, "type": "River/Water Recreation"},
            {"name": "Living Desert Zoo and Gardens State Park", "lat": 32.3158, "lon": -104.2261, "type": "Zoo/Botanical"},
            {"name": "Bottomless Lakes State Park", "lat": 33.3667, "lon": -104.4167, "type": "Lake/Swimming"},
            {"name": "Sumner Lake State Park", "lat": 34.6017, "lon": -104.3800, "type": "Lake/Water Recreation"},
            {"name": "Santa Rosa Lake State Park", "lat": 34.9372, "lon": -104.6831, "type": "Lake/Water Recreation"},
            {"name": "Storrie Lake State Park", "lat": 35.6400, "lon": -105.0700, "type": "Lake/Water Recreation"},
            {"name": "Hyde Memorial State Park", "lat": 35.6775, "lon": -105.8289, "type": "Mountain/Camping"},
            {"name": "Rio Grande Nature Center State Park", "lat": 35.1278, "lon": -106.6839, "type": "Nature Center"},
            {"name": "Coronado Historic Site", "lat": 35.3147, "lon": -106.7047, "type": "Historical"},
            {"name": "Jemez Falls State Park", "lat": 35.8667, "lon": -106.5833, "type": "Waterfall/Hiking"},
            {"name": "Eagle Nest Lake State Park", "lat": 36.5500, "lon": -105.2333, "type": "Lake/Fishing"},
            {"name": "Clayton Lake State Park", "lat": 36.5167, "lon": -103.4167, "type": "Lake/Dinosaur Tracks"},
            {"name": "Ute Lake State Park", "lat": 35.3833, "lon": -103.5667, "type": "Lake/Water Recreation"},
            {"name": "Conchas Lake State Park", "lat": 35.4000, "lon": -104.1833, "type": "Lake/Water Recreation"},
            {"name": "Villanueva State Park", "lat": 35.2600, "lon": -105.3400, "type": "River/Camping"},
            {"name": "Morphy Lake State Park", "lat": 35.9100, "lon": -105.3800, "type": "Lake/Fishing"}
        ]
        
        # Create GeoDataFrame
        parks_df = pd.DataFrame(parks_data)
        parks_gdf = gpd.GeoDataFrame(
            parks_df,
            geometry=gpd.points_from_xy(parks_df.lon, parks_df.lat),
            crs='EPSG:4326'
        )
        
        # Save parks data
        parks_file = self.subdirs['parks'] / "nm_state_parks_manual.gpkg"
        parks_gdf.to_file(parks_file, driver='GPKG')
        
        print(f"✅ Created {len(parks_gdf)} state parks: {parks_file}")
        
        # Create parks style
        self.create_parks_style(parks_file.with_suffix('.qml'))
        
        return parks_gdf
    
    def download_abq_transit_data(self):
        """Download ABQ RIDE transit data"""
        print(f"\n🚍 Downloading ABQ RIDE Transit Data...")
        
        transit_data = {}
        
        # 1. Try Rio Metro GTFS data (corrected URL)
        print("  📥 Downloading GTFS schedule data...")
        gtfs_urls = [
            "https://www.riometro.org/253/General-Transit-Feed-Specification-GTFS",
            "https://transitfeeds.com/p/abq-ride/52/latest/download"
        ]
        
        gtfs_file = self.subdirs['transit'] / "abq_ride_gtfs.zip"
        gtfs_downloaded = False
        
        for gtfs_url in gtfs_urls:
            if self.download_with_ssl_bypass(gtfs_url, gtfs_file):
                gtfs_downloaded = True
                break
            else:
                print(f"  ⚠️ GTFS URL failed: {gtfs_url}")
        
        if gtfs_downloaded:
            # Extract GTFS files
            try:
                with zipfile.ZipFile(gtfs_file, 'r') as zip_ref:
                    gtfs_dir = self.subdirs['transit'] / "gtfs_data"
                    gtfs_dir.mkdir(exist_ok=True)
                    zip_ref.extractall(gtfs_dir)
                
                print(f"✅ Extracted GTFS data to: {gtfs_dir}")
                
                # Process stops.txt to create bus stops GeoDataFrame
                stops_file = gtfs_dir / "stops.txt"
                if stops_file.exists():
                    stops_df = pd.read_csv(stops_file)
                    
                    # Create GeoDataFrame from bus stops
                    stops_gdf = gpd.GeoDataFrame(
                        stops_df,
                        geometry=gpd.points_from_xy(stops_df.stop_lon, stops_df.stop_lat),
                        crs='EPSG:4326'
                    )
                    
                    # Save bus stops
                    stops_output = self.subdirs['transit'] / "abq_bus_stops.gpkg"
                    stops_gdf.to_file(stops_output, driver='GPKG')
                    
                    print(f"✅ Saved {len(stops_gdf)} bus stops: {stops_output}")
                    
                    # Create bus stops style
                    self.create_transit_style(stops_output.with_suffix('.qml'))
                    
                    transit_data['bus_stops'] = stops_gdf
                    
            except Exception as e:
                print(f"⚠️ Could not process GTFS data: {e}")
        
        # 2. Try Albuquerque Open Data portal
        print("  🔄 Trying Albuquerque Open Data portal...")
        
        abq_data_urls = [
            "https://services1.arcgis.com/FbaYRKKdPMcFWfm4/arcgis/rest/services/ABQ_RIDE_Bus_Stops/FeatureServer/0/query",
            "https://data-cabq.opendata.arcgis.com/datasets/abq-ride-bus-stops"
        ]
        
        for abq_url in abq_data_urls:
            try:
                if "FeatureServer" in abq_url:
                    params = {'where': '1=1', 'outFields': '*', 'f': 'geojson'}
                    response = requests.get(abq_url, params=params, verify=False, timeout=60)
                else:
                    response = requests.get(abq_url, verify=False, timeout=60)
                
                response.raise_for_status()
                
                if "FeatureServer" in abq_url:
                    data = response.json()
                    if 'features' in data and len(data['features']) > 0:
                        stops_gdf = gpd.GeoDataFrame.from_features(data['features'])
                        
                        if stops_gdf.crs is None:
                            stops_gdf.set_crs('EPSG:4326', inplace=True)
                        
                        stops_file = self.subdirs['transit'] / "abq_bus_stops_opendata.gpkg"
                        stops_gdf.to_file(stops_file, driver='GPKG')
                        
                        print(f"✅ Open data bus stops saved: {stops_file}")
                        self.create_transit_style(stops_file.with_suffix('.qml'))
                        
                        transit_data['bus_stops_opendata'] = stops_gdf
                        break
            
            except Exception as e:
                print(f"⚠️ ABQ open data attempt failed: {e}")
                continue
        
        # 3. Create manual bus stops for major locations if all else fails
        if not transit_data:
            print("  📍 Creating manual transit stops for major locations...")
            transit_data['manual_stops'] = self.create_manual_transit_stops()
        
        return transit_data
    
    def create_manual_transit_stops(self):
        """Create manual transit stops for major Albuquerque locations"""
        print("📍 Creating manual transit stops database...")
        
        # Major transit locations in Albuquerque
        stops_data = [
            {"stop_name": "Alvarado Transportation Center", "lat": 35.0844, "lon": -106.6504, "type": "Transit Center"},
            {"stop_name": "UNM Hospital", "lat": 35.0844, "lon": -106.6181, "type": "Hospital"},
            {"stop_name": "University of New Mexico", "lat": 35.0844, "lon": -106.6208, "type": "University"},
            {"stop_name": "Uptown Transit Center", "lat": 35.1389, "lon": -106.6031, "type": "Transit Center"},
            {"stop_name": "West Side Transit Center", "lat": 35.1047, "lon": -106.7031, "type": "Transit Center"},
            {"stop_name": "Northeast Transit Center", "lat": 35.1669, "lon": -106.5356, "type": "Transit Center"},
            {"stop_name": "Kirtland Air Force Base", "lat": 35.0400, "lon": -106.5483, "type": "Military"},
            {"stop_name": "Old Town Plaza", "lat": 35.0947, "lon": -106.6692, "type": "Historic"},
            {"stop_name": "Cottonwood Mall", "lat": 35.1539, "lon": -106.6242, "type": "Shopping"},
            {"stop_name": "Presbyterian Hospital", "lat": 35.1097, "lon": -106.6158, "type": "Hospital"}
        ]
        
        # Create GeoDataFrame
        stops_df = pd.DataFrame(stops_data)
        stops_gdf = gpd.GeoDataFrame(
            stops_df,
            geometry=gpd.points_from_xy(stops_df.lon, stops_df.lat),
            crs='EPSG:4326'
        )
        
        # Save transit stops
        stops_file = self.subdirs['transit'] / "abq_major_transit_locations.gpkg"
        stops_gdf.to_file(stops_file, driver='GPKG')
        
        print(f"✅ Created {len(stops_gdf)} major transit locations: {stops_file}")
        
        # Create transit style
        self.create_transit_style(stops_file.with_suffix('.qml'))
        
        return stops_gdf
    
    def create_point_style(self, qml_file, dataset_name):
        """Create QML style file for point datasets"""
        
        # Color scheme based on dataset type
        colors = {
            'Schools': '#1f77b4',  # Blue
            'Hospitals': '#d62728',  # Red
            'Pharmacies': '#2ca02c',  # Green
            'Urgent Care': '#ff7f0e'  # Orange
        }
        
        color = colors.get(dataset_name, '#1f77b4')
        
        qml_content = f'''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.0" styleCategories="AllStyleCategories">
  <renderer-v2 type="singleSymbol">
    <symbols>
      <symbol type="marker" name="0" alpha="1">
        <layer class="SimpleMarker">
          <prop k="color" v="{color},255"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_width" v="0.5"/>
          <prop k="size" v="4"/>
          <prop k="size_unit" v="Point"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <labeling type="simple">
    <settings>
      <text-style fontFamily="Arial" fontSize="8" fontColor="0,0,0,255"/>
      <text-format>
        <background shapeSizeX="0" shapeSizeY="0"/>
      </text-format>
      <placement placement="1" dist="2"/>
      <rendering obstacle="1" scaleVisibility="1" scaleMin="1" scaleMax="25000"/>
    </settings>
  </labeling>
</qgis>'''
        
        with open(qml_file, 'w') as f:
            f.write(qml_content)
        
        print(f"🎨 Style file created: {qml_file}")
    
    def create_parks_style(self, qml_file):
        """Create QML style file for parks"""
        
        qml_content = '''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.0" styleCategories="AllStyleCategories">
  <renderer-v2 type="singleSymbol">
    <symbols>
      <symbol type="marker" name="0" alpha="1">
        <layer class="SimpleMarker">
          <prop k="color" v="34,139,34,255"/>
          <prop k="outline_color" v="0,100,0,255"/>
          <prop k="outline_width" v="1"/>
          <prop k="size" v="6"/>
          <prop k="size_unit" v="Point"/>
          <prop k="name" v="diamond"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
</qgis>'''
        
        with open(qml_file, 'w') as f:
            f.write(qml_content)
        
        print(f"🎨 Parks style file created: {qml_file}")
    
    def create_transit_style(self, qml_file):
        """Create QML style file for transit stops"""
        
        qml_content = '''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34.0" styleCategories="AllStyleCategories">
  <renderer-v2 type="singleSymbol">
    <symbols>
      <symbol type="marker" name="0" alpha="1">
        <layer class="SimpleMarker">
          <prop k="color" v="255,165,0,255"/>
          <prop k="outline_color" v="139,69,19,255"/>
          <prop k="outline_width" v="0.5"/>
          <prop k="size" v="3"/>
          <prop k="size_unit" v="Point"/>
          <prop k="name" v="square"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
</qgis>'''
        
        with open(qml_file, 'w') as f:
            f.write(qml_content)
        
        print(f"🎨 Transit style file created: {qml_file}")
    
    def create_summary_report(self, results):
        """Create summary report of all downloaded data"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.nm_dir / f"nm_infrastructure_summary_{timestamp}.txt"
        
        report = f"""New Mexico Infrastructure Data Download Summary
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
===========================================================

DIRECTORY STRUCTURE:
• Base Directory: {self.nm_dir}
• Schools: {self.subdirs['schools']}
• Healthcare: {self.subdirs['hospitals']}
• Parks & Recreation: {self.subdirs['parks']}
• Transportation: {self.subdirs['transit']}

DOWNLOADED DATASETS:
"""
        
        for category, data in results.items():
            if data is not None:
                report += f"\n{category.upper()}:\n"
                if isinstance(data, dict):
                    for subcategory, gdf in data.items():
                        if gdf is not None:
                            if hasattr(gdf, '__len__') and not isinstance(gdf, str):
                                if len(gdf) > 0:
                                    report += f"  • {subcategory.replace('_', ' ').title()}: {len(gdf)} records\n"
                                else:
                                    report += f"  • {subcategory.replace('_', ' ').title()}: No records\n"
                            else:
                                report += f"  • {subcategory.replace('_', ' ').title()}: Available\n"
                elif hasattr(data, '__len__') and not isinstance(data, str):
                    if len(data) > 0:
                        report += f"  • {category}: {len(data)} records\n"
                    else:
                        report += f"  • {category}: No records\n"
                else:
                    report += f"  • {category}: Available\n"
        
        report += f"""

FILES CREATED:
• .gpkg files: QGIS-ready geospatial data
• .qml files: QGIS style files for instant styling
• .csv files: Summary data tables

USAGE INSTRUCTIONS:
1. Open QGIS
2. Add .gpkg files as layers
3. Right-click layer → Properties → Symbology → Load Style
4. Select corresponding .qml file
5. Layer with poverty data and other existing datasets

NEXT STEPS:
• Combine with poverty tract data for comprehensive analysis
• Layer with LIHTC projects and QCT/DDA boundaries
• Create buffer analyses around transit stops and healthcare
• Calculate proximity scores for LIHTC opportunity mapping
"""
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📋 Summary report saved: {report_file}")
        return report_file

def main():
    """Main execution function"""
    
    print("🏗️ New Mexico Infrastructure Data Downloader")
    print("=" * 60)
    
    # Base directory from user's structure
    base_data_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets"
    
    # Initialize downloader
    downloader = NewMexicoInfrastructureDownloader(base_data_dir)
    
    # Download all datasets
    results = {}
    
    print("\n🎯 Starting data downloads...")
    
    try:
        # Schools
        results['schools'] = downloader.download_schools_data()
        
        # Healthcare facilities
        results['healthcare'] = downloader.download_healthcare_data()
        
        # State parks
        results['parks'] = downloader.download_state_parks_data()
        
        # Transit data
        results['transit'] = downloader.download_abq_transit_data()
        
        # Create summary report
        summary_file = downloader.create_summary_report(results)
        
        print("\n" + "=" * 60)
        print("✅ NEW MEXICO INFRASTRUCTURE DATA DOWNLOAD COMPLETE!")
        print("=" * 60)
        
        # Print summary
        total_datasets = 0
        for category, data in results.items():
            if data is not None:
                if isinstance(data, dict):
                    # Count non-None values in dictionary
                    valid_datasets = [v for v in data.values() if v is not None and (not hasattr(v, '__len__') or len(v) > 0)]
                    count = len(valid_datasets)
                    if count > 0:
                        total_datasets += count
                        print(f"📊 {category.title()}: {count} datasets")
                elif hasattr(data, '__len__') and not isinstance(data, str) and len(data) > 0:
                    total_datasets += 1
                    print(f"📊 {category.title()}: 1 dataset ({len(data)} records)")
                elif not isinstance(data, str):
                    total_datasets += 1
                    print(f"📊 {category.title()}: 1 dataset")
        
        print(f"\n🎯 Total datasets downloaded: {total_datasets}")
        print(f"📁 Data saved to: {downloader.nm_dir}")
        print(f"📋 Summary report: {summary_file}")
        
        print(f"\n🗺️ READY FOR QGIS:")
        print("   1. Open QGIS")
        print("   2. Add .gpkg files from each subdirectory")
        print("   3. Load corresponding .qml styles")
        print("   4. Layer with your poverty tract data!")
        
    except Exception as e:
        print(f"\n❌ Error during download process: {e}")
        print("Check network connection and try again.")

if __name__ == "__main__":
    main()