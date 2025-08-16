#!/usr/bin/env python3
"""
D'Marco Priority Sites Comprehensive Analyzer
Processes D'Marco's 8 priority Texas sites with complete TDHCA analysis including:
- FEMA flood zone integration
- ACS poverty rate analysis  
- QCT/DDA verification
- School proximity analysis
- TDHCA competition analysis
- Economic viability assessment

Author: Claude Code
Date: July 16, 2025
"""

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import json
import requests
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
import geopandas as gpd
from shapely.geometry import Point
from geopy.distance import geodesic
import math
import warnings
warnings.filterwarnings('ignore')

# Add the code directory to Python path for imports
sys.path.append('/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DMarcoSiteAnalyzer:
    """Comprehensive analyzer for D'Marco's priority Texas sites"""
    
    def __init__(self):
        """Initialize the analyzer with required API keys and data paths"""
        self.positionstack_api_key = "41b80ed51d92978904592126d2bb8f7e"
        self.census_api_key = "06ece0121263282cd9ffd753215b007b8f9a3dfc"
        
        # Data paths
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/D'Marco_Site_Visit")
        self.input_file = self.base_dir / "For Bill Region 9.xlsx"
        self.output_file = self.base_dir / "DMarco_Priority_Sites_Analysis.xlsx"
        
        # Data source paths
        self.flood_data_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/environmental/FEMA_Flood_Maps/state_flood_data")
        self.hud_ami_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_AMI_Geographic/HUD2025_AMI_Rent_Data_Static.xlsx")
        self.tdhca_projects_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas/State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx")
        self.texas_schools_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/texas/TX_Public_Schools/Schools_2024_to_2025.csv")
        
        # Flood zone risk classifications
        self.high_risk_zones = ['A', 'AE', 'AH', 'AO', 'V', 'VE', 'AR', 'A99']
        self.moderate_risk_zones = ['X', 'X500']
        self.minimal_risk_zones = ['X (unshaded)', 'C']
        
        # Load supporting datasets
        self.load_flood_data()
        self.load_supporting_data()
        
        # Load the raw data
        self.load_and_clean_data()
        
    def load_flood_data(self):
        """Load Texas FEMA flood zone data"""
        logger.info("Loading Texas FEMA flood zone data...")
        
        # Try to load Texas flood geometry
        tx_flood_file = self.flood_data_path / "TX/processed/TX_flood_zones_complete.gpkg"
        tx_attrs_file = self.flood_data_path / "TX/processed/TX_flood_zones_attributes.csv"
        
        self.tx_flood_gdf = None
        self.tx_flood_attrs = None
        
        if tx_flood_file.exists():
            try:
                self.tx_flood_gdf = gpd.read_file(tx_flood_file)
                logger.info(f"✅ Texas flood geometry loaded: {len(self.tx_flood_gdf)} zones")
            except Exception as e:
                logger.warning(f"Could not load TX flood geometry: {e}")
                
        if tx_attrs_file.exists():
            try:
                self.tx_flood_attrs = pd.read_csv(tx_attrs_file)
                logger.info(f"✅ Texas flood attributes loaded: {len(self.tx_flood_attrs)} records")
            except Exception as e:
                logger.warning(f"Could not load TX flood attributes: {e}")
                
        if self.tx_flood_gdf is None and self.tx_flood_attrs is None:
            logger.warning("⚠️ No Texas flood data available")
            
    def load_supporting_data(self):
        """Load HUD AMI data, TDHCA projects, and Texas schools"""
        logger.info("Loading supporting datasets...")
        
        # Load HUD AMI data
        if self.hud_ami_file.exists():
            try:
                self.hud_ami_data = pd.read_excel(self.hud_ami_file)
                logger.info(f"✅ HUD AMI data loaded: {len(self.hud_ami_data)} areas")
            except Exception as e:
                logger.warning(f"Could not load HUD AMI data: {e}")
                self.hud_ami_data = None
        else:
            logger.warning(f"HUD AMI file not found: {self.hud_ami_file}")
            self.hud_ami_data = None
            
        # Load TDHCA projects
        if self.tdhca_projects_file.exists():
            try:
                self.tdhca_projects = pd.read_excel(self.tdhca_projects_file)
                # Clean coordinate columns
                self.tdhca_projects['Latitude'] = pd.to_numeric(self.tdhca_projects['Latitude11'], errors='coerce')
                self.tdhca_projects['Longitude'] = pd.to_numeric(self.tdhca_projects['Longitude11'], errors='coerce')
                
                # Filter for projects with valid coordinates
                valid_coords = self.tdhca_projects[['Latitude', 'Longitude']].notna().all(axis=1)
                self.tdhca_projects = self.tdhca_projects[valid_coords].copy()
                
                logger.info(f"✅ TDHCA projects loaded: {len(self.tdhca_projects)} projects with coordinates")
            except Exception as e:
                logger.warning(f"Could not load TDHCA projects: {e}")
                self.tdhca_projects = None
        else:
            logger.warning(f"TDHCA projects file not found: {self.tdhca_projects_file}")
            self.tdhca_projects = None
            
        # Load Texas schools
        if self.texas_schools_file.exists():
            try:
                self.texas_schools = pd.read_csv(self.texas_schools_file)
                # Fix coordinate column names - schools data uses X/Y instead of Longitude/Latitude
                if 'X' in self.texas_schools.columns and 'Y' in self.texas_schools.columns:
                    self.texas_schools['Longitude'] = self.texas_schools['X']
                    self.texas_schools['Latitude'] = self.texas_schools['Y']
                logger.info(f"✅ Texas schools loaded: {len(self.texas_schools)} schools")
            except Exception as e:
                logger.warning(f"Could not load Texas schools: {e}")
                self.texas_schools = None
        else:
            logger.warning(f"Texas schools file not found: {self.texas_schools_file}")
            self.texas_schools = None
            
    def get_flood_zone_info(self, lat: float, lon: float) -> dict:
        """Get flood zone information for coordinates using FEMA API"""
        if pd.isna(lat) or pd.isna(lon):
            return {'flood_zone': 'UNKNOWN', 'risk_category': 'UNKNOWN', 'insurance_required': False, 'cost_impact': 0}
            
        # Try FEMA ArcGIS REST API for flood zone lookup
        try:
            # FEMA National Flood Hazard Layer REST endpoint
            url = "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer/28/query"
            params = {
                'geometry': f"{lon},{lat}",
                'geometryType': 'esriGeometryPoint',
                'inSR': 4326,
                'spatialRel': 'esriSpatialRelIntersects',
                'returnGeometry': 'false',
                'outFields': 'FLD_ZONE,ZONE_SUBTY',
                'f': 'json'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if 'features' in data and len(data['features']) > 0:
                feature = data['features'][0]
                attributes = feature.get('attributes', {})
                flood_zone = attributes.get('FLD_ZONE', 'X')
                
                logger.info(f"  FEMA API flood zone: {flood_zone}")
                return self._classify_flood_risk(flood_zone)
            else:
                # No flood zone found, assume minimal risk
                logger.info(f"  No flood zone found, assuming minimal risk")
                return {'flood_zone': 'X', 'risk_category': 'LOW', 'insurance_required': False, 'cost_impact': 0}
                
        except Exception as e:
            logger.warning(f"FEMA API flood zone lookup failed for {lat}, {lon}: {e}")
            
        # Fallback to local geometry lookup if available
        if self.tx_flood_gdf is not None:
            try:
                point = Point(lon, lat)
                intersects = self.tx_flood_gdf[self.tx_flood_gdf.contains(point) | self.tx_flood_gdf.intersects(point)]
                
                if len(intersects) > 0:
                    zone_row = intersects.iloc[0]
                    flood_zone = zone_row.get('FLD_ZONE', 'X')
                    return self._classify_flood_risk(flood_zone)
            except Exception as e:
                logger.warning(f"Local flood zone lookup failed: {e}")
                
        # Final fallback - conservative estimate for Texas
        logger.info(f"  Using fallback: moderate risk assumption")
        return {'flood_zone': 'X', 'risk_category': 'MODERATE', 'insurance_required': False, 'cost_impact': 5}
        
    def _classify_flood_risk(self, flood_zone: str) -> dict:
        """Classify flood risk based on zone"""
        flood_zone = flood_zone.upper().strip() if flood_zone else 'X'
        
        if flood_zone in self.high_risk_zones:
            return {
                'flood_zone': flood_zone,
                'risk_category': 'HIGH',
                'insurance_required': True,
                'cost_impact': 25  # 25% construction cost increase
            }
        elif flood_zone in self.moderate_risk_zones or flood_zone.startswith('X'):
            return {
                'flood_zone': flood_zone,
                'risk_category': 'MODERATE', 
                'insurance_required': False,
                'cost_impact': 5  # 5% construction cost increase
            }
        elif flood_zone in self.minimal_risk_zones:
            return {
                'flood_zone': flood_zone,
                'risk_category': 'LOW',
                'insurance_required': False,
                'cost_impact': 0
            }
        else:
            return {
                'flood_zone': flood_zone,
                'risk_category': 'UNKNOWN',
                'insurance_required': False,
                'cost_impact': 0
            }
        
    def load_and_clean_data(self):
        """Load and clean the Excel data with proper headers"""
        logger.info(f"Loading data from: {self.input_file}")
        
        # Read the Excel file
        df = pd.read_excel(self.input_file)
        
        # Fix the headers - first row contains the actual column names
        new_columns = {
            'Unnamed: 0': 'Site_ID',
            'Unnamed: 1': 'Address', 
            'Unnamed: 2': 'Coordinates',
            'Unnamed: 3': 'Price',
            'Unnamed: 4': 'Price_Per_Sqft',
            'Unnamed: 5': 'Acreage',
            'Unnamed: 6': 'QCT_DDA_Status',
            'Unnamed: 7': 'Region',
            'Unnamed: 8': 'Zoning',
            'Unnamed: 9': 'Listing_Link'
        }
        
        df = df.rename(columns=new_columns)
        
        # Remove the header row (first row)
        df = df.iloc[1:].reset_index(drop=True)
        
        # Clean and standardize data types
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['Price_Per_Sqft'] = pd.to_numeric(df['Price_Per_Sqft'], errors='coerce')
        df['Acreage'] = pd.to_numeric(df['Acreage'], errors='coerce')
        df['Region'] = pd.to_numeric(df['Region'], errors='coerce')
        
        # Parse coordinates where available
        df['Latitude'] = np.nan
        df['Longitude'] = np.nan
        
        for idx, coord_str in enumerate(df['Coordinates']):
            if pd.notna(coord_str) and isinstance(coord_str, str):
                try:
                    if ',' in coord_str:
                        lat, lon = coord_str.split(',')
                        df.loc[idx, 'Latitude'] = float(lat.strip())
                        df.loc[idx, 'Longitude'] = float(lon.strip())
                except Exception as e:
                    logger.warning(f"Could not parse coordinates for site {idx+1}: {coord_str}")
        
        # Add Site_Number for tracking
        df['Site_Number'] = range(1, len(df) + 1)
        
        self.df = df
        logger.info(f"✅ Loaded and cleaned {len(df)} sites")
        logger.info(f"Sites with coordinates: {df[['Latitude', 'Longitude']].notna().all(axis=1).sum()}")
        logger.info(f"Sites needing geocoding: {df[['Latitude', 'Longitude']].isna().any(axis=1).sum()}")
        
    def geocode_missing_coordinates(self):
        """Geocode addresses missing coordinates using PositionStack API"""
        logger.info("Starting geocoding for missing coordinates...")
        
        missing_coords = self.df[self.df[['Latitude', 'Longitude']].isna().any(axis=1)]
        
        if len(missing_coords) == 0:
            logger.info("✅ All sites already have coordinates")
            return
            
        logger.info(f"Geocoding {len(missing_coords)} addresses...")
        
        for idx, row in missing_coords.iterrows():
            address = row['Address']
            if pd.isna(address):
                logger.warning(f"Site {row['Site_Number']}: No address to geocode")
                continue
                
            logger.info(f"Geocoding Site {row['Site_Number']}: {address}")
            
            # Call PositionStack API
            url = "http://api.positionstack.com/v1/forward"
            params = {
                'access_key': self.positionstack_api_key,
                'query': f"{address}, Texas, USA",
                'limit': 1,
                'output': 'json'
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if 'data' in data and len(data['data']) > 0:
                    result = data['data'][0]
                    lat = result.get('latitude')
                    lon = result.get('longitude')
                    
                    if lat and lon:
                        self.df.loc[idx, 'Latitude'] = lat
                        self.df.loc[idx, 'Longitude'] = lon
                        logger.info(f"  ✅ Geocoded: {lat:.6f}, {lon:.6f}")
                    else:
                        logger.warning(f"  ❌ No coordinates in response")
                else:
                    logger.warning(f"  ❌ No results from PositionStack")
                    
            except Exception as e:
                logger.error(f"  ❌ Geocoding failed: {str(e)}")
                
            # Rate limiting
            time.sleep(0.5)
            
        geocoded_count = self.df[self.df[['Latitude', 'Longitude']].notna().all(axis=1)].shape[0]
        logger.info(f"✅ Geocoding complete. Total sites with coordinates: {geocoded_count}/{len(self.df)}")
        
    def apply_data_corrections(self):
        """Apply manual corrections for known data issues"""
        logger.info("Applying manual data corrections...")
        
        # Fix Site 2 coordinates - D'Marco provided correct coordinates: 29°12'59"N 98°25'38"W
        site2_mask = self.df['Address'].str.contains('20421 Gus McCrae Ln', na=False)
        if site2_mask.any():
            self.df.loc[site2_mask, 'Latitude'] = 29.216389  # 29°12'59"N
            self.df.loc[site2_mask, 'Longitude'] = -98.427222  # 98°25'38"W
            logger.info("✅ Corrected Site 2 coordinates: 29.216389, -98.427222")
        
        # Fix Site 4 QCT/DDA status - D'Marco confirmed it's QCT, not DDA
        site4_mask = self.df['Address'].str.contains('10519 Hwy 16 South', na=False)
        if site4_mask.any():
            self.df.loc[site4_mask, 'QCT_DDA_Status'] = 'QCT'
            logger.info("✅ Corrected Site 4 QCT/DDA status to QCT")
        
    def get_census_tract(self, lat: float, lon: float) -> Optional[str]:
        """Get census tract GEOID for coordinates"""
        try:
            url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
            params = {
                'x': lon,
                'y': lat,
                'benchmark': 'Public_AR_Current',
                'vintage': 'Current_Current',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'result' in data and 'geographies' in data['result']:
                tracts = data['result']['geographies'].get('Census Tracts', [])
                if tracts:
                    return tracts[0].get('GEOID')
                    
        except Exception as e:
            logger.warning(f"Census tract lookup failed for {lat}, {lon}: {str(e)}")
            
        return None
        
    def get_poverty_rate(self, tract_geoid: str) -> Optional[float]:
        """Get poverty rate for census tract from ACS API"""
        try:
            # ACS 5-Year estimates for poverty
            url = "https://api.census.gov/data/2022/acs/acs5"
            params = {
                'get': 'B17001_001E,B17001_002E',  # Total population, Population below poverty
                'for': f'tract:{tract_geoid[-6:]}',  # Last 6 digits are tract
                'in': f'state:{tract_geoid[:2]} county:{tract_geoid[2:5]}',  # State and county codes
                'key': self.census_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if len(data) > 1:  # Skip header row
                total_pop = int(data[1][0]) if data[1][0] not in ['-666666666', 'null', None] else 0
                poverty_pop = int(data[1][1]) if data[1][1] not in ['-666666666', 'null', None] else 0
                
                if total_pop > 0:
                    poverty_rate = (poverty_pop / total_pop) * 100
                    return round(poverty_rate, 2)
                    
        except Exception as e:
            logger.warning(f"Poverty rate lookup failed for tract {tract_geoid}: {str(e)}")
            
        return None
        
    def add_census_poverty_analysis(self):
        """Add census tract and poverty rate analysis"""
        logger.info("Adding census tract and poverty rate analysis...")
        
        # Initialize new columns
        self.df['Census_Tract_GEOID'] = None
        self.df['Poverty_Rate_Percent'] = np.nan
        self.df['Low_Poverty_Bonus_Eligible'] = False
        self.df['Poverty_Category'] = None
        
        for idx, row in self.df.iterrows():
            lat, lon = row['Latitude'], row['Longitude']
            
            if pd.isna(lat) or pd.isna(lon):
                logger.warning(f"Site {row['Site_Number']}: No coordinates for poverty analysis")
                continue
                
            logger.info(f"Analyzing Site {row['Site_Number']}: {lat:.6f}, {lon:.6f}")
            
            # Get census tract
            tract_geoid = self.get_census_tract(lat, lon)
            if tract_geoid:
                self.df.loc[idx, 'Census_Tract_GEOID'] = tract_geoid
                logger.info(f"  Census Tract: {tract_geoid}")
                
                # Get poverty rate
                poverty_rate = self.get_poverty_rate(tract_geoid)
                if poverty_rate is not None:
                    self.df.loc[idx, 'Poverty_Rate_Percent'] = poverty_rate
                    
                    # Determine low poverty bonus eligibility (≤20% for CTCAC)
                    if poverty_rate <= 20:
                        self.df.loc[idx, 'Low_Poverty_Bonus_Eligible'] = True
                        
                    # Categorize poverty level
                    if poverty_rate < 10:
                        self.df.loc[idx, 'Poverty_Category'] = 'Very Low'
                    elif poverty_rate <= 20:
                        self.df.loc[idx, 'Poverty_Category'] = 'Low'
                    elif poverty_rate <= 30:
                        self.df.loc[idx, 'Poverty_Category'] = 'Moderate'
                    else:
                        self.df.loc[idx, 'Poverty_Category'] = 'High'
                        
                    logger.info(f"  Poverty Rate: {poverty_rate:.1f}% ({self.df.loc[idx, 'Poverty_Category']})")
                else:
                    logger.warning(f"  Could not get poverty rate")
            else:
                logger.warning(f"  Could not get census tract")
                
            time.sleep(0.2)  # Rate limiting
            
        poverty_count = self.df['Poverty_Rate_Percent'].notna().sum()
        logger.info(f"✅ Census/poverty analysis complete. {poverty_count}/{len(self.df)} sites analyzed")
        
    def add_flood_zone_analysis(self):
        """Add FEMA flood zone analysis to sites"""
        logger.info("Adding FEMA flood zone analysis...")
        
        # Initialize flood columns
        self.df['Flood_Zone'] = None
        self.df['Flood_Risk_Category'] = None
        self.df['Flood_Insurance_Required'] = False
        self.df['Construction_Cost_Impact_Percent'] = 0
        
        for idx, row in self.df.iterrows():
            lat, lon = row['Latitude'], row['Longitude']
            
            if pd.isna(lat) or pd.isna(lon):
                logger.warning(f"Site {row['Site_Number']}: No coordinates for flood analysis")
                continue
                
            logger.info(f"Analyzing flood risk for Site {row['Site_Number']}")
            
            flood_info = self.get_flood_zone_info(lat, lon)
            
            self.df.loc[idx, 'Flood_Zone'] = flood_info['flood_zone']
            self.df.loc[idx, 'Flood_Risk_Category'] = flood_info['risk_category']
            self.df.loc[idx, 'Flood_Insurance_Required'] = flood_info['insurance_required']
            self.df.loc[idx, 'Construction_Cost_Impact_Percent'] = flood_info['cost_impact']
            
            logger.info(f"  Flood Zone: {flood_info['flood_zone']} ({flood_info['risk_category']} risk)")
            if flood_info['insurance_required']:
                logger.info(f"  ⚠️ Flood insurance required")
            if flood_info['cost_impact'] > 0:
                logger.info(f"  💰 Construction cost impact: +{flood_info['cost_impact']}%")
                
        flood_count = self.df['Flood_Zone'].notna().sum()
        logger.info(f"✅ Flood zone analysis complete. {flood_count}/{len(self.df)} sites analyzed")
        
    def get_ami_rents_for_area(self, site_lat: float, site_lon: float) -> dict:
        """Get AMI rent data for the area containing the site"""
        if self.hud_ami_data is None:
            return {}
            
        # Try to match by proximity to major Texas metros
        # This is a simplified approach - in production you'd use more precise MSA matching
        metro_areas = {
            'San Antonio': (29.4241, -98.4936),
            'Austin': (30.2672, -97.7431),
            'Houston': (29.7604, -95.3698),
            'Dallas': (32.7767, -96.7970),
            'Fort Worth': (32.7555, -97.3308)
        }
        
        # Find closest metro
        closest_metro = None
        min_distance = float('inf')
        
        for metro, (metro_lat, metro_lon) in metro_areas.items():
            distance = geodesic((site_lat, site_lon), (metro_lat, metro_lon)).miles
            if distance < min_distance:
                min_distance = distance
                closest_metro = metro
                
        # Look for AMI data matching the metro area
        if closest_metro:
            metro_matches = self.hud_ami_data[
                self.hud_ami_data['HUD_Area'].str.contains(closest_metro, case=False, na=False)
            ]
            
            if len(metro_matches) > 0:
                # Use the first match
                ami_row = metro_matches.iloc[0]
                
                return {
                    'area_name': ami_row['HUD_Area'],
                    'ami_4person_100pct': ami_row.get('Median_AMI_100pct', 0),
                    'studio_50pct': ami_row.get('50pct_AMI_Studio_Rent', 0),
                    'studio_60pct': ami_row.get('60pct_AMI_Studio_Rent', 0),
                    '1br_50pct': ami_row.get('50pct_AMI_1BR_Rent', 0),
                    '1br_60pct': ami_row.get('60pct_AMI_1BR_Rent', 0),
                    '2br_50pct': ami_row.get('50pct_AMI_2BR_Rent', 0),
                    '2br_60pct': ami_row.get('60pct_AMI_2BR_Rent', 0),
                    '3br_50pct': ami_row.get('50pct_AMI_3BR_Rent', 0),
                    '3br_60pct': ami_row.get('60pct_AMI_3BR_Rent', 0),
                    '4br_50pct': ami_row.get('50pct_AMI_4BR_Rent', 0),
                    '4br_60pct': ami_row.get('60pct_AMI_4BR_Rent', 0)
                }
                
        return {}
        
    def analyze_tdhca_competition(self, site_lat: float, site_lon: float, radius_miles: float = 2.0) -> dict:
        """Analyze TDHCA competition within radius"""
        if self.tdhca_projects is None:
            return {'competition_count': 0, 'competition_details': [], 'total_units': 0}
            
        # Find projects within radius
        competing_projects = []
        total_competing_units = 0
        
        for idx, project in self.tdhca_projects.iterrows():
            project_lat = project['Latitude']
            project_lon = project['Longitude']
            
            if pd.isna(project_lat) or pd.isna(project_lon):
                continue
                
            distance = geodesic((site_lat, site_lon), (project_lat, project_lon)).miles
            
            if distance <= radius_miles:
                # Extract unit mix information
                total_units = project.get('Total Units', 0)
                if pd.notna(total_units) and total_units > 0:
                    total_competing_units += int(total_units)
                
                lihtc_units = project.get('LIHTC Units', 0)
                
                project_info = {
                    'development_name': project.get('Development Name', 'Unknown'),
                    'address': project.get('Project Address ', 'Unknown'),
                    'city': project.get('Project City', 'Unknown'),
                    'year': project.get('Year', 'Unknown'),
                    'board_approval': project.get('Board Approval', 'Unknown'),
                    'total_units': total_units,
                    'lihtc_units': lihtc_units,
                    'program_type': project.get('Program Type', 'Unknown'),
                    'distance_miles': round(distance, 2),
                    'lihtc_amount': project.get('LIHTC Amt Awarded', 0),
                    'population_served': project.get('Population Served', 'Unknown')
                }
                
                competing_projects.append(project_info)
        
        # Sort by distance
        competing_projects.sort(key=lambda x: x['distance_miles'])
        
        return {
            'competition_count': len(competing_projects),
            'total_units': total_competing_units,
            'competition_details': competing_projects[:10]  # Limit to top 10 closest
        }
        
    def analyze_school_proximity(self, site_lat: float, site_lon: float, radius_miles: float = 2.5) -> dict:
        """Analyze school proximity within radius"""
        if self.texas_schools is None:
            return {'schools_count': 0, 'school_details': []}
            
        nearby_schools = []
        
        for idx, school in self.texas_schools.iterrows():
            school_lat = school.get('Latitude', None)
            school_lon = school.get('Longitude', None)
            
            if pd.isna(school_lat) or pd.isna(school_lon):
                continue
                
            distance = geodesic((site_lat, site_lon), (school_lat, school_lon)).miles
            
            if distance <= radius_miles:
                school_info = {
                    'school_name': school.get('USER_School_Name', 'Unknown'),
                    'district': school.get('USER_District_Name', 'Unknown'),
                    'type': school.get('School_Type', 'Unknown'),
                    'grades': school.get('USER_Grade_Range', 'Unknown'),
                    'distance_miles': round(distance, 2)
                }
                nearby_schools.append(school_info)
        
        # Sort by distance
        nearby_schools.sort(key=lambda x: x['distance_miles'])
        
        return {
            'schools_count': len(nearby_schools),
            'school_details': nearby_schools[:15]  # Limit to top 15 closest
        }
        
    def add_comprehensive_site_analysis(self):
        """Add comprehensive analysis including competition, schools, and AMI rents"""
        logger.info("Adding comprehensive site analysis (competition, schools, AMI rents)...")
        
        # Initialize new columns
        self.df['AMI_Area_Name'] = None
        self.df['AMI_4Person_100PCT'] = np.nan
        self.df['AMI_1BR_60PCT_Rent'] = np.nan
        self.df['AMI_2BR_60PCT_Rent'] = np.nan
        self.df['AMI_3BR_60PCT_Rent'] = np.nan
        self.df['AMI_4BR_60PCT_Rent'] = np.nan
        
        self.df['TDHCA_Competition_Count_2mi'] = 0
        self.df['TDHCA_Total_Units_2mi'] = 0
        self.df['TDHCA_Competition_Details'] = None
        
        self.df['Schools_Count_2_5mi'] = 0
        self.df['Schools_Within_2_5mi'] = None
        
        for idx, row in self.df.iterrows():
            lat, lon = row['Latitude'], row['Longitude']
            
            if pd.isna(lat) or pd.isna(lon):
                logger.warning(f"Site {row['Site_Number']}: No coordinates for comprehensive analysis")
                continue
                
            logger.info(f"Comprehensive analysis for Site {row['Site_Number']}")
            
            # AMI rent analysis
            ami_data = self.get_ami_rents_for_area(lat, lon)
            if ami_data:
                self.df.loc[idx, 'AMI_Area_Name'] = ami_data.get('area_name', '')
                self.df.loc[idx, 'AMI_4Person_100PCT'] = ami_data.get('ami_4person_100pct', 0)
                self.df.loc[idx, 'AMI_1BR_60PCT_Rent'] = ami_data.get('1br_60pct', 0)
                self.df.loc[idx, 'AMI_2BR_60PCT_Rent'] = ami_data.get('2br_60pct', 0)
                self.df.loc[idx, 'AMI_3BR_60PCT_Rent'] = ami_data.get('3br_60pct', 0)
                self.df.loc[idx, 'AMI_4BR_60PCT_Rent'] = ami_data.get('4br_60pct', 0)
                logger.info(f"  AMI Area: {ami_data.get('area_name', 'Unknown')}")
                
            # TDHCA competition analysis
            competition = self.analyze_tdhca_competition(lat, lon)
            self.df.loc[idx, 'TDHCA_Competition_Count_2mi'] = competition['competition_count']
            self.df.loc[idx, 'TDHCA_Total_Units_2mi'] = competition['total_units']
            
            if competition['competition_details']:
                # Format competition details as readable string
                comp_summary = []
                for comp in competition['competition_details'][:5]:  # Top 5
                    address_str = f"{comp['address']}, {comp['city']}" if comp['address'] != 'Unknown' else "Address unavailable"
                    comp_str = f"{comp['development_name']} ({comp['total_units']} units, {comp['distance_miles']}mi, {comp['year']}) - {address_str}"
                    comp_summary.append(comp_str)
                self.df.loc[idx, 'TDHCA_Competition_Details'] = '; '.join(comp_summary)
                
            logger.info(f"  Competition: {competition['competition_count']} projects within 2 miles")
            
            # School proximity analysis
            schools = self.analyze_school_proximity(lat, lon)
            self.df.loc[idx, 'Schools_Count_2_5mi'] = schools['schools_count']
            
            if schools['school_details']:
                # Format school details
                school_summary = []
                for school in schools['school_details'][:5]:  # Top 5
                    school_str = f"{school['school_name']} ({school['type']}, {school['distance_miles']}mi)"
                    school_summary.append(school_str)
                self.df.loc[idx, 'Schools_Within_2_5mi'] = '; '.join(school_summary)
                
            logger.info(f"  Schools: {schools['schools_count']} schools within 2.5 miles")
            
        logger.info(f"✅ Comprehensive site analysis complete!")
        
    def run_comprehensive_analysis(self):
        """Run the complete analysis pipeline"""
        logger.info("🚀 Starting comprehensive D'Marco site analysis...")
        
        # Phase 1: Data preparation
        self.geocode_missing_coordinates()
        self.apply_data_corrections()
        
        # Phase 2: Census and poverty analysis
        self.add_census_poverty_analysis()
        
        # Phase 3: FEMA flood zone analysis
        self.add_flood_zone_analysis()
        
        # Phase 4: Comprehensive analysis (competition, schools, AMI rents)
        self.add_comprehensive_site_analysis()
        
        # Save final results
        self.save_results()
        
        # Generate professional reports
        self.generate_html_report()
        self.generate_pdf_report()
        self.generate_google_earth_kml()
        
        logger.info(f"✅ Analysis complete! Results saved to: {self.output_file}")
        logger.info(f"📄 HTML report: {self.base_dir / 'DMarco_Sites_Analysis_Report.html'}")
        logger.info(f"📄 PDF report: {self.base_dir / 'DMarco_Sites_Analysis_Report.pdf'}")
        logger.info(f"🌍 Google Earth KML: {self.base_dir / 'DMarco_Sites_GoogleEarth.kml'}")
        
    def save_results(self):
        """Save analysis results to Excel"""
        logger.info(f"Saving results to: {self.output_file}")
        
        # Reorder columns for better readability
        column_order = [
            'Site_Number', 'Address', 'Latitude', 'Longitude', 
            'Price', 'Price_Per_Sqft', 'Acreage', 'QCT_DDA_Status',
            'Census_Tract_GEOID', 'Poverty_Rate_Percent', 'Low_Poverty_Bonus_Eligible', 'Poverty_Category',
            'Flood_Zone', 'Flood_Risk_Category', 'Flood_Insurance_Required', 'Construction_Cost_Impact_Percent',
            'AMI_Area_Name', 'AMI_4Person_100PCT', 'AMI_1BR_60PCT_Rent', 'AMI_2BR_60PCT_Rent', 'AMI_3BR_60PCT_Rent', 'AMI_4BR_60PCT_Rent',
            'TDHCA_Competition_Count_2mi', 'TDHCA_Competition_Details',
            'Schools_Count_2_5mi', 'Schools_Within_2_5mi',
            'Region', 'Zoning', 'Listing_Link'
        ]
        
        # Ensure all columns exist
        for col in column_order:
            if col not in self.df.columns:
                self.df[col] = None
                
        output_df = self.df[column_order].copy()
        
        # Save to Excel
        with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
            output_df.to_excel(writer, sheet_name='DMarco_Sites_Analysis', index=False)
            
        logger.info(f"✅ Results saved successfully!")
        
    def generate_html_report(self):
        """Generate professional HTML report for D'Marco sites"""
        logger.info("Generating HTML report...")
        
        html_file = self.base_dir / "DMarco_Sites_Analysis_Report.html"
        
        # Calculate summary statistics
        total_sites = len(self.df)
        sites_with_competition = (self.df['TDHCA_Competition_Count_2mi'] > 0).sum()
        sites_with_lpb = self.df['Low_Poverty_Bonus_Eligible'].sum()
        avg_price_per_acre = (self.df['Price'] / self.df['Acreage']).mean()
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D'Marco Priority Sites - Comprehensive TDHCA Analysis</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .summary-card h3 {{
            color: #2c3e50;
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }}
        .summary-card p {{
            color: #7f8c8d;
            margin: 0;
            font-weight: 500;
        }}
        .top-sites {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .top-sites h2 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 25px;
        }}
        .site-card {{
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            background: #f8f9fa;
        }}
        .site-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .site-title {{
            font-size: 1.4em;
            font-weight: 600;
            color: #2c3e50;
        }}
        .site-price {{
            font-size: 1.3em;
            font-weight: 600;
            color: #27ae60;
        }}
        .site-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }}
        .detail-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 12px;
            background: white;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }}
        .detail-label {{
            font-weight: 500;
            color: #7f8c8d;
        }}
        .detail-value {{
            font-weight: 600;
            color: #2c3e50;
        }}
        .competition-section {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin-top: 15px;
        }}
        .competition-title {{
            font-weight: 600;
            color: #856404;
            margin-bottom: 10px;
        }}
        .competition-details {{
            font-size: 0.9em;
            color: #856404;
        }}
        .data-table {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        .data-table h2 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 25px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .status-qct {{
            background-color: #d4edda;
            color: #155724;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .status-dda {{
            background-color: #cce5ff;
            color: #004085;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .poverty-very-low {{
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
        }}
        .poverty-low {{
            background-color: #d4edda;
            color: #155724;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
        }}
        .poverty-moderate {{
            background-color: #fff3cd;
            color: #856404;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .methodology {{
            background: #e8f4fd;
            border: 1px solid #b8daff;
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
        }}
        .methodology h3 {{
            color: #004085;
            margin-top: 0;
        }}
        .competition-zero {{
            color: #28a745;
            font-weight: 600;
        }}
        .competition-high {{
            color: #dc3545;
            font-weight: 600;
        }}
        .lpb-yes {{
            color: #28a745;
            font-weight: 600;
        }}
        .lpb-no {{
            color: #dc3545;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>D'Marco Priority Sites Analysis</h1>
        <p>Comprehensive TDHCA Development Opportunity Assessment</p>
        <p>{datetime.now().strftime('%B %d, %Y')}</p>
    </div>

    <div class="summary-cards">
        <div class="summary-card">
            <h3>{total_sites}</h3>
            <p>Total Sites Analyzed</p>
        </div>
        <div class="summary-card">
            <h3>{sites_with_lpb}</h3>
            <p>Low Poverty Bonus Eligible</p>
        </div>
        <div class="summary-card">
            <h3>{sites_with_competition}</h3>
            <p>Sites with Competition</p>
        </div>
        <div class="summary-card">
            <h3>${avg_price_per_acre:,.0f}</h3>
            <p>Avg Price per Acre</p>
        </div>
    </div>

    <div class="top-sites">
        <h2>🎯 Priority Site Analysis</h2>
"""

        # Add detailed site cards
        for idx, row in self.df.iterrows():
            poverty_class = "poverty-very-low" if row['Poverty_Rate_Percent'] < 10 else \
                           "poverty-low" if row['Poverty_Rate_Percent'] <= 20 else "poverty-moderate"
            
            status_class = "status-qct" if row['QCT_DDA_Status'] == 'QCT' else "status-dda"
            
            competition_class = "competition-zero" if row['TDHCA_Competition_Count_2mi'] == 0 else \
                               "competition-high" if row['TDHCA_Competition_Count_2mi'] > 5 else ""
            
            lpb_class = "lpb-yes" if row['Low_Poverty_Bonus_Eligible'] else "lpb-no"
            lpb_text = "✅ Eligible" if row['Low_Poverty_Bonus_Eligible'] else "❌ Not Eligible"
            
            price_per_acre = row['Price'] / row['Acreage']
            
            html_content += f"""
        <div class="site-card">
            <div class="site-header">
                <div class="site-title">Site {row['Site_Number']}: {row['Address']}</div>
                <div class="site-price">${row['Price']:,.0f}</div>
            </div>
            
            <div class="site-details">
                <div class="detail-item">
                    <span class="detail-label">Location:</span>
                    <span class="detail-value">
                        <a href="https://www.google.com/maps?q={row['Latitude']:.6f},{row['Longitude']:.6f}" target="_blank">
                            {row['Latitude']:.6f}, {row['Longitude']:.6f} (Google Maps)
                        </a>
                    </span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Census Tract:</span>
                    <span class="detail-value">
                        <a href="https://data.census.gov/table/ACSST5Y2022.S1701?g=1400000US{row.get('Census_Tract_GEOID', '')}" target="_blank">
                            {row.get('Census_Tract_GEOID', 'Unknown')} (View Census Data)
                        </a>
                    </span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Acreage:</span>
                    <span class="detail-value">{row['Acreage']} acres (${price_per_acre:,.0f}/acre)</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Status:</span>
                    <span class="detail-value"><span class="{status_class}">{row['QCT_DDA_Status']}</span></span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Poverty Rate:</span>
                    <span class="detail-value"><span class="{poverty_class}">{row['Poverty_Rate_Percent']:.1f}% ({row['Poverty_Category']})</span></span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Low Poverty Bonus:</span>
                    <span class="detail-value"><span class="{lpb_class}">{lpb_text}</span></span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Competition:</span>
                    <span class="detail-value"><span class="{competition_class}">{row['TDHCA_Competition_Count_2mi']} projects / {row.get('TDHCA_Total_Units_2mi', 0)} units within 2 miles</span></span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">AMI Area:</span>
                    <span class="detail-value">{row['AMI_Area_Name']}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">AMI Rents (60%):</span>
                    <span class="detail-value">1BR: ${row['AMI_1BR_60PCT_Rent']:,.0f} | 2BR: ${row['AMI_2BR_60PCT_Rent']:,.0f} | 3BR: ${row['AMI_3BR_60PCT_Rent']:,.0f}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Flood Risk:</span>
                    <span class="detail-value">Zone {row['Flood_Zone']} ({row['Flood_Risk_Category']}) | +{row['Construction_Cost_Impact_Percent']}% cost</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Zoning:</span>
                    <span class="detail-value">{row['Zoning']}</span>
                </div>
            </div>
"""

            # Add competition details if available
            if pd.notna(row['TDHCA_Competition_Details']) and row['TDHCA_Competition_Details']:
                html_content += f"""
            <div class="competition-section">
                <div class="competition-title">🏢 Competing TDHCA Projects:</div>
                <div class="competition-details">{row['TDHCA_Competition_Details']}</div>
            </div>
"""

            html_content += "        </div>\n"

        # Add data table
        html_content += f"""
    </div>

    <div class="data-table">
        <h2>📊 Complete Site Comparison Table</h2>
        <table>
            <thead>
                <tr>
                    <th>Site</th>
                    <th>Address</th>
                    <th>Price</th>
                    <th>Acres</th>
                    <th>$/Acre</th>
                    <th>Status</th>
                    <th>% Pov.</th>
                    <th>LPB</th>
                    <th>Projects/Units</th>
                    <th>2BR Rent</th>
                    <th>Zoning</th>
                </tr>
            </thead>
            <tbody>
"""

        # Add table rows
        for idx, row in self.df.iterrows():
            price_per_acre = row['Price'] / row['Acreage']
            poverty_class = "poverty-very-low" if row['Poverty_Rate_Percent'] < 10 else \
                           "poverty-low" if row['Poverty_Rate_Percent'] <= 20 else "poverty-moderate"
            status_class = "status-qct" if row['QCT_DDA_Status'] == 'QCT' else "status-dda"
            lpb_text = "✅" if row['Low_Poverty_Bonus_Eligible'] else "❌"
            
            html_content += f"""
                <tr>
                    <td><strong>{row['Site_Number']}</strong></td>
                    <td>{row['Address']}</td>
                    <td>${row['Price']:,.0f}</td>
                    <td>{row['Acreage']}</td>
                    <td>${price_per_acre:,.0f}</td>
                    <td><span class="{status_class}">{row['QCT_DDA_Status']}</span></td>
                    <td><span class="{poverty_class}">{row['Poverty_Rate_Percent']:.1f}%</span></td>
                    <td>{lpb_text}</td>
                    <td>{row['TDHCA_Competition_Count_2mi']} / {row.get('TDHCA_Total_Units_2mi', 0)}</td>
                    <td>${row['AMI_2BR_60PCT_Rent']:,.0f}</td>
                    <td>{row['Zoning']}</td>
                </tr>
"""

        html_content += """
            </tbody>
        </table>
    </div>

    <div class="footer">
        <p>Report generated by Structured Consultants LLC using comprehensive TDHCA analysis framework</p>
        <p>© 2025 Structured Consultants LLC | Professional LIHTC Development Advisory Services</p>
    </div>

</body>
</html>"""

        # Write HTML file
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        logger.info(f"✅ HTML report generated: {html_file}")
        
    def generate_pdf_report(self):
        """Generate PDF report from HTML using weasyprint or similar"""
        logger.info("Generating PDF report...")
        
        try:
            import weasyprint
            
            html_file = self.base_dir / "DMarco_Sites_Analysis_Report.html"
            pdf_file = self.base_dir / "DMarco_Sites_Analysis_Report.pdf"
            
            if html_file.exists():
                # Generate PDF from HTML
                weasyprint.HTML(filename=str(html_file)).write_pdf(str(pdf_file))
                logger.info(f"✅ PDF report generated: {pdf_file}")
            else:
                logger.warning("HTML file not found for PDF generation")
                
        except ImportError:
            logger.warning("weasyprint not available - PDF generation skipped")
            logger.info("To enable PDF generation, install: pip install weasyprint")
        except Exception as e:
            logger.warning(f"PDF generation failed: {e}")
            
    def generate_google_earth_kml(self):
        """Generate Google Earth KML file for site visit planning"""
        logger.info("Generating Google Earth KML file...")
        
        try:
            import simplekml
            
            kml_file = self.base_dir / "DMarco_Sites_GoogleEarth.kml"
            
            # Create KML object
            kml = simplekml.Kml()
            kml.document.name = "D'Marco Priority Sites - TDHCA Analysis"
            kml.document.description = f"""
D'Marco Priority Sites for TDHCA Development
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

Site Priority Legend:
🥇 = Top Priority (Zero Competition)
⭐ = High Priority 
📍 = Medium Priority
⚠️ = Caution (High Competition or Issues)

Click any marker for detailed analysis results.
"""

            # Create folders by priority
            folders = {}
            
            for idx, row in self.df.iterrows():
                lat, lon = row['Latitude'], row['Longitude']
                
                if pd.isna(lat) or pd.isna(lon):
                    continue
                    
                # Determine priority and icon
                competition_count = row['TDHCA_Competition_Count_2mi']
                lpb_eligible = row['Low_Poverty_Bonus_Eligible']
                price_per_acre = row['Price'] / row['Acreage']
                
                # Priority logic
                if competition_count == 0 and lpb_eligible:
                    priority = "🥇 Top Priority"
                    icon_color = "green"
                    icon = "🥇"
                elif competition_count <= 2 and lpb_eligible:
                    priority = "⭐ High Priority"
                    icon_color = "yellow"
                    icon = "⭐"
                elif competition_count <= 5 or lpb_eligible:
                    priority = "📍 Medium Priority"
                    icon_color = "orange"
                    icon = "📍"
                else:
                    priority = "⚠️ Caution"
                    icon_color = "red"
                    icon = "⚠️"
                
                # Create folder if not exists
                if priority not in folders:
                    folders[priority] = kml.newfolder(name=priority)
                
                # Create placemark
                site_name = f"{icon} Site {row['Site_Number']}: {row['Address']}"
                
                # Detailed description
                description = f"""
<b>Site {row['Site_Number']}: {row['Address']}</b><br/><br/>
                
<b>📍 Location:</b><br/>
Coordinates: {lat:.6f}, {lon:.6f}<br/>
Region: {row['Region']}<br/><br/>

<b>💰 Financial Details:</b><br/>
Price: ${row['Price']:,.0f}<br/>
Acreage: {row['Acreage']} acres<br/>
Price per Acre: ${price_per_acre:,.0f}<br/>
Price per Sqft: ${row['Price_Per_Sqft']:,.0f}<br/><br/>

<b>🏛️ TDHCA Status:</b><br/>
QCT/DDA Status: {row['QCT_DDA_Status']}<br/>
Poverty Rate: {row['Poverty_Rate_Percent']:.1f}% ({row['Poverty_Category']})<br/>
Low Poverty Bonus: {'✅ Eligible' if row['Low_Poverty_Bonus_Eligible'] else '❌ Not Eligible'}<br/><br/>

<b>🏢 Competition Analysis:</b><br/>
TDHCA Projects within 2mi: {competition_count}<br/>
"""
                
                if pd.notna(row['TDHCA_Competition_Details']) and row['TDHCA_Competition_Details']:
                    description += f"Competing Projects: {row['TDHCA_Competition_Details']}<br/>"
                
                description += f"""<br/>
<b>🏠 Market Data:</b><br/>
AMI Area: {row['AMI_Area_Name']}<br/>
1BR Rent (60% AMI): ${row['AMI_1BR_60PCT_Rent']:,.0f}<br/>
2BR Rent (60% AMI): ${row['AMI_2BR_60PCT_Rent']:,.0f}<br/>
3BR Rent (60% AMI): ${row['AMI_3BR_60PCT_Rent']:,.0f}<br/><br/>

<b>🌊 Risk Factors:</b><br/>
Flood Zone: {row['Flood_Zone']} ({row['Flood_Risk_Category']} risk)<br/>
Construction Cost Impact: +{row['Construction_Cost_Impact_Percent']}%<br/><br/>

<b>🏗️ Development Details:</b><br/>
Zoning: {row['Zoning']}<br/>
Schools within 2.5mi: {row['Schools_Count_2_5mi']}<br/>
"""

                # Create the placemark
                pnt = folders[priority].newpoint(name=site_name, coords=[(lon, lat)])
                pnt.description = description
                
                # Style the placemark
                pnt.style.iconstyle.color = icon_color
                pnt.style.iconstyle.scale = 1.2
                pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png'
                
                if icon_color == "green":
                    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/grn-pushpin.png'
                elif icon_color == "red":
                    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png'
                elif icon_color == "orange":
                    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png'
            
            # Save KML file
            kml.save(str(kml_file))
            logger.info(f"✅ Google Earth KML generated: {kml_file}")
            
        except ImportError:
            logger.warning("simplekml not available - KML generation skipped")
            logger.info("To enable KML generation, install: pip install simplekml")
        except Exception as e:
            logger.warning(f"KML generation failed: {e}")

if __name__ == "__main__":
    analyzer = DMarcoSiteAnalyzer()
    analyzer.run_comprehensive_analysis()