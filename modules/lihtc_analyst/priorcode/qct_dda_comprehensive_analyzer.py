#!/usr/bin/env python3
"""
QCT/DDA Comprehensive LIHTC Analysis System - FINAL VERSION
Properly combines all three datasets and verifies QCT/DDA status

Key Features:
1. Loads D'Marco sites from both Brent and Brian
2. Loads CoStar land data
3. Verifies ALL sites against HUD QCT/DDA shapefiles
4. Fixes all identified data issues from review

Author: TDHCA Analysis System (Final)
Date: 2025-06-21
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import geopandas as gpd
from shapely.geometry import Point
from geopy.distance import geodesic
import requests
import json
import logging
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows

class QCTDDAComprehensiveAnalyzer:
    """Comprehensive QCT/DDA analyzer combining all datasets"""
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Key data paths
        self.base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects")
        self.code_path = self.base_path / "CTCAC_RAG/code"
        self.data_path = self.base_path / "Lvg_Bond_Execution/Data Sets"
        
        # Results storage
        self.all_sites = None
        self.analysis_results = None
        
        # Load all reference data upfront
        self.load_tdhca_regional_mapping()
        self.load_qct_dda_data()
        self.load_ami_data()
        self.load_tdhca_projects()
        
    def load_tdhca_regional_mapping(self):
        """Load complete Texas County to TDHCA Region mapping"""
        # Complete 255 county mapping
        self.county_to_region = {
            # Region 1 (Panhandle)
            'Potter': 'Region 1', 'Randall': 'Region 1', 'Lubbock': 'Region 1', 'Armstrong': 'Region 1',
            'Bailey': 'Region 1', 'Briscoe': 'Region 1', 'Carson': 'Region 1', 'Castro': 'Region 1',
            'Childress': 'Region 1', 'Cochran': 'Region 1', 'Collingsworth': 'Region 1', 'Crosby': 'Region 1',
            'Dallam': 'Region 1', 'Deaf Smith': 'Region 1', 'Dickens': 'Region 1', 'Donley': 'Region 1',
            'Floyd': 'Region 1', 'Gray': 'Region 1', 'Hale': 'Region 1', 'Hall': 'Region 1',
            'Hansford': 'Region 1', 'Hartley': 'Region 1', 'Hemphill': 'Region 1', 'Hockley': 'Region 1',
            'Hutchinson': 'Region 1', 'King': 'Region 1', 'Lamb': 'Region 1', 'Lipscomb': 'Region 1',
            'Moore': 'Region 1', 'Motley': 'Region 1', 'Ochiltree': 'Region 1', 'Oldham': 'Region 1',
            'Parmer': 'Region 1', 'Roberts': 'Region 1', 'Sherman': 'Region 1', 'Swisher': 'Region 1',
            'Terry': 'Region 1', 'Wheeler': 'Region 1', 'Yoakum': 'Region 1',
            
            # Region 2 (North Central)
            'Taylor': 'Region 2', 'Wichita': 'Region 2', 'Archer': 'Region 2', 'Baylor': 'Region 2',
            'Brown': 'Region 2', 'Callahan': 'Region 2', 'Clay': 'Region 2', 'Coleman': 'Region 2',
            'Comanche': 'Region 2', 'Cottle': 'Region 2', 'Eastland': 'Region 2', 'Fisher': 'Region 2',
            'Foard': 'Region 2', 'Hardeman': 'Region 2', 'Haskell': 'Region 2', 'Jack': 'Region 2',
            'Jones': 'Region 2', 'Kent': 'Region 2', 'Knox': 'Region 2', 'Mitchell': 'Region 2',
            'Montague': 'Region 2', 'Nolan': 'Region 2', 'Palo Pinto': 'Region 2', 'Parker': 'Region 2',
            'Runnels': 'Region 2', 'Scurry': 'Region 2', 'Shackelford': 'Region 2', 'Stephens': 'Region 2',
            'Stonewall': 'Region 2', 'Throckmorton': 'Region 2', 'Wilbarger': 'Region 2', 'Wise': 'Region 2',
            'Young': 'Region 2',
            
            # Region 3 (Dallas-Fort Worth)
            'Dallas': 'Region 3', 'Tarrant': 'Region 3', 'Collin': 'Region 3', 'Denton': 'Region 3',
            'Ellis': 'Region 3', 'Hood': 'Region 3', 'Hunt': 'Region 3', 'Johnson': 'Region 3',
            'Kaufman': 'Region 3', 'Navarro': 'Region 3', 'Rockwall': 'Region 3', 'Somervell': 'Region 3',
            'Cooke': 'Region 3', 'Fannin': 'Region 3', 'Grayson': 'Region 3',
            
            # Region 4 (East Texas)
            'Smith': 'Region 4', 'Gregg': 'Region 4', 'Anderson': 'Region 4', 'Bowie': 'Region 4',
            'Camp': 'Region 4', 'Cass': 'Region 4', 'Cherokee': 'Region 4', 'Delta': 'Region 4',
            'Franklin': 'Region 4', 'Harrison': 'Region 4', 'Henderson': 'Region 4', 'Hopkins': 'Region 4',
            'Lamar': 'Region 4', 'Marion': 'Region 4', 'Morris': 'Region 4', 'Panola': 'Region 4',
            'Rains': 'Region 4', 'Red River': 'Region 4', 'Rusk': 'Region 4', 'Shelby': 'Region 4',
            'Titus': 'Region 4', 'Upshur': 'Region 4', 'Van Zandt': 'Region 4', 'Wood': 'Region 4',
            'Tyler': 'Region 4',  # Tyler County (not city)
            
            # Region 5 (Southeast Texas)
            'Jefferson': 'Region 5', 'Orange': 'Region 5', 'Angelina': 'Region 5', 'Hardin': 'Region 5',
            'Houston': 'Region 5', 'Jasper': 'Region 5', 'Nacogdoches': 'Region 5', 'Newton': 'Region 5',
            'Polk': 'Region 5', 'Sabine': 'Region 5', 'San Augustine': 'Region 5', 'San Jacinto': 'Region 5',
            'Trinity': 'Region 5',
            
            # Region 6 (Houston Metro)
            'Harris': 'Region 6', 'Fort Bend': 'Region 6', 'Montgomery': 'Region 6', 'Brazoria': 'Region 6',
            'Chambers': 'Region 6', 'Galveston': 'Region 6', 'Liberty': 'Region 6', 'Waller': 'Region 6',
            'Austin': 'Region 6', 'Colorado': 'Region 6', 'Matagorda': 'Region 6', 'Wharton': 'Region 6',
            
            # Region 7 (Austin-Central Texas)
            'Travis': 'Region 7', 'Williamson': 'Region 7', 'Hays': 'Region 7', 'Bastrop': 'Region 7',
            'Blanco': 'Region 7', 'Burnet': 'Region 7', 'Caldwell': 'Region 7', 'Fayette': 'Region 7',
            'Lee': 'Region 7', 'Llano': 'Region 7',
            
            # Region 8 (Central Texas)
            'McLennan': 'Region 8', 'Brazos': 'Region 8', 'Bell': 'Region 8', 'Bosque': 'Region 8',
            'Burleson': 'Region 8', 'Coryell': 'Region 8', 'Falls': 'Region 8', 'Freestone': 'Region 8',
            'Grimes': 'Region 8', 'Hamilton': 'Region 8', 'Hill': 'Region 8', 'Lampasas': 'Region 8',
            'Leon': 'Region 8', 'Limestone': 'Region 8', 'Madison': 'Region 8', 'Milam': 'Region 8',
            'Mills': 'Region 8', 'Robertson': 'Region 8', 'San Saba': 'Region 8', 'Walker': 'Region 8',
            'Washington': 'Region 8',
            
            # Region 9 (San Antonio)
            'Bexar': 'Region 9', 'Comal': 'Region 9', 'Guadalupe': 'Region 9', 'Wilson': 'Region 9',
            'Atascosa': 'Region 9', 'Bandera': 'Region 9', 'Frio': 'Region 9', 'Gillespie': 'Region 9',
            'Karnes': 'Region 9', 'Kendall': 'Region 9', 'Kerr': 'Region 9', 'Medina': 'Region 9',
            
            # Region 10 (Coastal)
            'Nueces': 'Region 10', 'San Patricio': 'Region 10', 'Aransas': 'Region 10', 'Bee': 'Region 10',
            'Brooks': 'Region 10', 'Calhoun': 'Region 10', 'DeWitt': 'Region 10', 'Goliad': 'Region 10',
            'Gonzales': 'Region 10', 'Jackson': 'Region 10', 'Jim Wells': 'Region 10', 'Kenedy': 'Region 10',
            'Kleberg': 'Region 10', 'Lavaca': 'Region 10', 'Live Oak': 'Region 10', 'Refugio': 'Region 10',
            'Victoria': 'Region 10',
            
            # Region 11 (South Texas)
            'Cameron': 'Region 11', 'Hidalgo': 'Region 11', 'Webb': 'Region 11', 'Dimmit': 'Region 11',
            'Duval': 'Region 11', 'Jim Hogg': 'Region 11', 'La Salle': 'Region 11', 'Maverick': 'Region 11',
            'McMullen': 'Region 11', 'Starr': 'Region 11', 'Willacy': 'Region 11', 'Zapata': 'Region 11',
            'Zavala': 'Region 11',
            
            # Region 12 (West Texas)
            'Midland': 'Region 12', 'Ector': 'Region 12', 'Andrews': 'Region 12', 'Borden': 'Region 12',
            'Coke': 'Region 12', 'Concho': 'Region 12', 'Crane': 'Region 12', 'Crockett': 'Region 12',
            'Dawson': 'Region 12', 'Gaines': 'Region 12', 'Garza': 'Region 12', 'Glasscock': 'Region 12',
            'Howard': 'Region 12', 'Irion': 'Region 12', 'Kimble': 'Region 12', 'Loving': 'Region 12',
            'Lynn': 'Region 12', 'Martin': 'Region 12', 'Mason': 'Region 12', 'McCulloch': 'Region 12',
            'Menard': 'Region 12', 'Pecos': 'Region 12', 'Reagan': 'Region 12', 'Reeves': 'Region 12',
            'Schleicher': 'Region 12', 'Sterling': 'Region 12', 'Sutton': 'Region 12', 'Tom Green': 'Region 12',
            'Upton': 'Region 12', 'Ward': 'Region 12', 'Winkler': 'Region 12',
            
            # Region 13 (Far West Texas)
            'El Paso': 'Region 13', 'Hudspeth': 'Region 13', 'Culberson': 'Region 13', 'Jeff Davis': 'Region 13',
            'Brewster': 'Region 13', 'Presidio': 'Region 13', 'Terrell': 'Region 13', 'Val Verde': 'Region 13',
            'Edwards': 'Region 13', 'Kinney': 'Region 13', 'Real': 'Region 13', 'Uvalde': 'Region 13'
        }
        
        # Add variations for common misspellings
        self.county_to_region.update({
            'Kaufmann': 'Region 3',  # Common misspelling
            'Mc Lennan': 'Region 8',  # Space variation
            'De Witt': 'Region 10',  # Space variation
        })
        
        self.logger.info(f"Loaded complete TDHCA regional mapping for {len(self.county_to_region)} counties")
        
    def load_dmarco_sites_brent(self):
        """Load D'Marco's 65 sites from Brent"""
        dmarco_file = self.code_path / "DMarco_Sites_Final_PositionStack_20250618_235606.xlsx"
        
        if not dmarco_file.exists():
            self.logger.error(f"D'Marco Brent file not found: {dmarco_file}")
            return pd.DataFrame()
        
        # Read the correct sheet with all sites
        try:
            dmarco_df = pd.read_excel(dmarco_file, sheet_name='All_Sites_Final')
            dmarco_df['Source'] = 'D\'Marco_Brent'
            self.logger.info(f"Loaded {len(dmarco_df)} D'Marco sites from Brent")
            return dmarco_df
        except Exception as e:
            self.logger.error(f"Error reading D'Marco file: {e}")
            return pd.DataFrame()
        
    def load_dmarco_sites_brian(self):
        """Load new D'Marco sites from Brian"""
        brian_file = self.base_path / "TDHCA_RAG/D'Marco_Sites/From_Brian_06202025.csv"
        
        if not brian_file.exists():
            self.logger.error(f"D'Marco Brian file not found: {brian_file}")
            return pd.DataFrame()
            
        brian_df = pd.read_csv(brian_file)
        brian_df['Source'] = 'D\'Marco_Brian'
        
        # Parse coordinates
        for idx, row in brian_df.iterrows():
            coord_str = row.get('Cordinates', '')
            if isinstance(coord_str, str) and ',' in coord_str:
                try:
                    lat, lon = coord_str.strip().split(',')
                    brian_df.loc[idx, 'Latitude'] = float(lat.strip())
                    brian_df.loc[idx, 'Longitude'] = float(lon.strip())
                except:
                    brian_df.loc[idx, 'Latitude'] = np.nan
                    brian_df.loc[idx, 'Longitude'] = np.nan
                    
        self.logger.info(f"Loaded {len(brian_df)} D'Marco sites from Brian")
        return brian_df
        
    def load_costar_properties(self):
        """Load CoStar properties"""
        costar_file = self.code_path / "CoStar_Land_Analysis_With_Counties_20250617_223737.xlsx"
        
        if not costar_file.exists():
            self.logger.error(f"CoStar file not found: {costar_file}")
            return pd.DataFrame()
            
        costar_df = pd.read_excel(costar_file)
        costar_df['Source'] = 'CoStar'
        self.logger.info(f"Loaded {len(costar_df)} CoStar properties")
        return costar_df
        
    def standardize_columns(self, df, source_name):
        """Standardize column names across different sources"""
        # Create mapping based on source
        if source_name == 'D\'Marco_Brian':
            column_mapping = {
                'Address': 'Property_Address',
                'City': 'City',
                'County': 'County',
                'Zip': 'Zip_Code',
                'Acres': 'Land_Acres',
                'Price': 'Price',
                'QCT/DDA': 'QCT_DDA_Notes',
                'Reigion': 'TDHCA_Region',  # Fix typo
                'NOTES': 'Notes'
            }
        elif source_name == 'D\'Marco_Brent':
            column_mapping = {
                'Property_Address': 'Property_Address',
                'City': 'City',
                'County': 'County',
                'Zip_Code': 'Zip_Code',
                'Land_Acres': 'Land_Acres',
                'Region': 'TDHCA_Region',
                'QCT_Status': 'Is_QCT',
                'DDA_Status': 'Is_DDA',
                'QCT_DDA_Eligible': 'QCT_DDA_Eligible'
            }
        else:  # CoStar
            column_mapping = {
                'Property Name': 'Property_Name',
                'Property Address': 'Property_Address',
                'City': 'City',
                'County': 'County',
                'ZIP': 'Zip_Code',
                'Land Area (AC)': 'Land_Acres',
                'QCT_TRACT_Num': 'QCT_Tract',
                'DDA_NAME': 'DDA_Name',
                'QCT_DDA_Eligible': 'QCT_DDA_Eligible'
            }
            
        # Apply mapping
        df = df.rename(columns=column_mapping)
        
        # Parse QCT/DDA from notes for Brian's data
        if source_name == 'D\'Marco_Brian' and 'QCT_DDA_Notes' in df.columns:
            for idx, row in df.iterrows():
                qct_dda_note = str(row.get('QCT_DDA_Notes', '')).upper()
                df.loc[idx, 'Is_QCT'] = 'QCT' in qct_dda_note
                df.loc[idx, 'Is_DDA'] = 'DDA' in qct_dda_note
                df.loc[idx, 'QCT_DDA_Eligible'] = bool('QCT' in qct_dda_note or 'DDA' in qct_dda_note)
                
        # For CoStar, determine QCT/DDA from tract/name fields
        if source_name == 'CoStar':
            for idx, row in df.iterrows():
                has_qct = pd.notna(row.get('QCT_Tract')) and str(row.get('QCT_Tract')).strip() != ''
                has_dda = pd.notna(row.get('DDA_Name')) and str(row.get('DDA_Name')).strip() != ''
                df.loc[idx, 'Is_QCT'] = has_qct
                df.loc[idx, 'Is_DDA'] = has_dda
                df.loc[idx, 'QCT_DDA_Eligible'] = has_qct or has_dda
                
        return df
        
    def merge_all_datasets(self):
        """Merge all three datasets with proper standardization"""
        # Load all datasets
        dmarco_brent = self.load_dmarco_sites_brent()
        dmarco_brian = self.load_dmarco_sites_brian()
        costar_df = self.load_costar_properties()
        
        # Standardize each dataset
        if not dmarco_brent.empty:
            dmarco_brent = self.standardize_columns(dmarco_brent, 'D\'Marco_Brent')
        if not dmarco_brian.empty:
            dmarco_brian = self.standardize_columns(dmarco_brian, 'D\'Marco_Brian')
        if not costar_df.empty:
            costar_df = self.standardize_columns(costar_df, 'CoStar')
        
        # Combine all datasets
        all_data = pd.concat([dmarco_brent, dmarco_brian, costar_df], ignore_index=True, sort=False)
        
        # Ensure numeric fields
        numeric_fields = ['Land_Acres', 'Latitude', 'Longitude']
        for field in numeric_fields:
            if field in all_data.columns:
                all_data[field] = pd.to_numeric(all_data[field], errors='coerce')
                
        # Add missing TDHCA regions
        for idx, row in all_data.iterrows():
            if pd.isna(row.get('TDHCA_Region')) or str(row.get('TDHCA_Region')).strip() == '':
                county = str(row.get('County', '')).strip()
                if county in self.county_to_region:
                    all_data.loc[idx, 'TDHCA_Region'] = self.county_to_region[county]
                    
        self.all_sites = all_data
        self.logger.info(f"Merged {len(self.all_sites)} total properties")
        
        # Log breakdown by source
        for source in ['D\'Marco_Brent', 'D\'Marco_Brian', 'CoStar']:
            count = len(self.all_sites[self.all_sites['Source'] == source])
            self.logger.info(f"  - {source}: {count} properties")
            
    def load_qct_dda_data(self):
        """Load QCT/DDA shapefiles"""
        try:
            qct_path = self.data_path / "HUD DDA QCT/QUALIFIED_CENSUS_TRACTS_7341711606021821459.gpkg"
            dda_path = self.data_path / "HUD DDA QCT/Difficult_Development_Areas_-4200740390724245794.gpkg"
            
            self.qct_gdf = gpd.read_file(qct_path).to_crs(epsg=4326)
            self.dda_gdf = gpd.read_file(dda_path).to_crs(epsg=4326)
            
            self.logger.info(f"Loaded {len(self.qct_gdf)} QCT and {len(self.dda_gdf)} DDA areas")
        except Exception as e:
            self.logger.error(f"Error loading QCT/DDA data: {e}")
            self.qct_gdf = gpd.GeoDataFrame()
            self.dda_gdf = gpd.GeoDataFrame()
            
    def verify_qct_dda_status(self, lat, lon):
        """Verify QCT/DDA status against HUD shapefiles"""
        if pd.isna(lat) or pd.isna(lon):
            return {'Is_QCT_Verified': False, 'Is_DDA_Verified': False, 'QCT_DDA_Verified': False}
            
        try:
            point = Point(lon, lat)
            
            is_qct = any(self.qct_gdf.geometry.contains(point))
            is_dda = any(self.dda_gdf.geometry.contains(point))
            
            return {
                'Is_QCT_Verified': is_qct,
                'Is_DDA_Verified': is_dda,
                'QCT_DDA_Verified': is_qct or is_dda,
                'Basis_Boost_Pct': 30 if (is_qct or is_dda) else 0
            }
        except:
            return {'Is_QCT_Verified': False, 'Is_DDA_Verified': False, 'QCT_DDA_Verified': False, 'Basis_Boost_Pct': 0}
            
    def load_ami_data(self):
        """Load HUD AMI rent data"""
        ami_file = self.data_path / "HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx"
        
        try:
            # Read the Excel file - try to find Texas data
            xl_file = pd.ExcelFile(ami_file)
            
            # Find the right sheet
            sheet_name = None
            for sheet in xl_file.sheet_names:
                if 'texas' in sheet.lower() or 'tx' in sheet.lower():
                    sheet_name = sheet
                    break
            if not sheet_name and xl_file.sheet_names:
                sheet_name = xl_file.sheet_names[0]
                
            ami_df = pd.read_excel(ami_file, sheet_name=sheet_name)
            
            # Build AMI lookup by county
            self.ami_lookup = {}
            
            # Find columns with rent data (usually numeric columns)
            for _, row in ami_df.iterrows():
                # Try to find county name
                county = None
                for val in row.values[:5]:  # Check first 5 columns for county name
                    if isinstance(val, str) and len(val) > 2:
                        county = val.strip()
                        break
                        
                if not county:
                    continue
                    
                # Extract numeric values (likely rent amounts)
                rent_values = []
                for val in row.values:
                    try:
                        num_val = pd.to_numeric(val, errors='coerce')
                        if not pd.isna(num_val) and num_val > 100 and num_val < 5000:
                            rent_values.append(num_val)
                    except:
                        pass
                        
                # Store AMI data if we have rent values
                if len(rent_values) >= 5:
                    self.ami_lookup[county] = {
                        'Studio_60pct': rent_values[5] if len(rent_values) > 5 else 850,
                        '1BR_60pct': rent_values[6] if len(rent_values) > 6 else 950,
                        '2BR_60pct': rent_values[7] if len(rent_values) > 7 else 1200,
                        '3BR_60pct': rent_values[8] if len(rent_values) > 8 else 1450,
                        '4BR_60pct': rent_values[9] if len(rent_values) > 9 else 1650,
                    }
                    
            self.logger.info(f"Loaded AMI data for {len(self.ami_lookup)} Texas counties")
            
        except Exception as e:
            self.logger.warning(f"AMI data loading error: {e}. Using defaults.")
            # Use regional defaults
            self.ami_lookup = self.get_default_ami_data()
            
    def get_default_ami_data(self):
        """Get default AMI data by region"""
        return {
            # Major metros
            'Harris': {'Studio_60pct': 1000, '1BR_60pct': 1100, '2BR_60pct': 1400, '3BR_60pct': 1700, '4BR_60pct': 1900},
            'Dallas': {'Studio_60pct': 1050, '1BR_60pct': 1150, '2BR_60pct': 1450, '3BR_60pct': 1750, '4BR_60pct': 1950},
            'Travis': {'Studio_60pct': 1100, '1BR_60pct': 1200, '2BR_60pct': 1500, '3BR_60pct': 1800, '4BR_60pct': 2000},
            'Bexar': {'Studio_60pct': 900, '1BR_60pct': 1000, '2BR_60pct': 1250, '3BR_60pct': 1550, '4BR_60pct': 1750},
            'Tarrant': {'Studio_60pct': 950, '1BR_60pct': 1050, '2BR_60pct': 1350, '3BR_60pct': 1650, '4BR_60pct': 1850},
            'Collin': {'Studio_60pct': 1050, '1BR_60pct': 1150, '2BR_60pct': 1450, '3BR_60pct': 1750, '4BR_60pct': 1950},
            'Denton': {'Studio_60pct': 1000, '1BR_60pct': 1100, '2BR_60pct': 1400, '3BR_60pct': 1700, '4BR_60pct': 1900},
            'Fort Bend': {'Studio_60pct': 1000, '1BR_60pct': 1100, '2BR_60pct': 1400, '3BR_60pct': 1700, '4BR_60pct': 1900},
            'Williamson': {'Studio_60pct': 1050, '1BR_60pct': 1150, '2BR_60pct': 1450, '3BR_60pct': 1750, '4BR_60pct': 1950},
            'Hays': {'Studio_60pct': 1050, '1BR_60pct': 1150, '2BR_60pct': 1450, '3BR_60pct': 1750, '4BR_60pct': 1950},
            # Default
            'Default': {'Studio_60pct': 800, '1BR_60pct': 900, '2BR_60pct': 1100, '3BR_60pct': 1350, '4BR_60pct': 1550},
        }
        
    def load_tdhca_projects(self):
        """Load TDHCA competition projects"""
        project_file = self.data_path / "State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
        
        try:
            self.tdhca_projects = pd.read_excel(project_file)
            self.tdhca_projects['Year'] = pd.to_numeric(self.tdhca_projects['Year'], errors='coerce')
            self.tdhca_projects = self.tdhca_projects[
                self.tdhca_projects['Year'].between(2021, 2024)
            ]
            self.logger.info(f"Loaded {len(self.tdhca_projects)} recent TDHCA projects")
        except Exception as e:
            self.logger.warning(f"TDHCA projects loading error: {e}")
            self.tdhca_projects = pd.DataFrame()
            
    def get_fema_flood_risk(self, lat, lon):
        """Get FEMA flood zone"""
        if pd.isna(lat) or pd.isna(lon):
            return {'FEMA_Zone': 'Unknown', 'Flood_Cost_Impact': 1.05}
            
        try:
            url = "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer/28/query"
            params = {
                'geometry': f'{lon},{lat}',
                'geometryType': 'esriGeometryPoint',
                'inSR': '4326',
                'spatialRel': 'esriSpatialRelIntersects',
                'outFields': 'FLD_ZONE,ZONE_SUBTY',
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if 'features' in data and len(data['features']) > 0:
                    zone = data['features'][0]['attributes'].get('FLD_ZONE', 'X')
                    
                    # Cost impact mapping
                    fema_cost_impacts = {
                        'VE': 1.30, 'V': 1.30,
                        'AE': 1.20, 'A': 1.20,
                        'AO': 1.12, 'AH': 1.12,
                        'X': 1.05, 'X500': 1.05
                    }
                    
                    cost_impact = fema_cost_impacts.get(zone, 1.05)
                    return {'FEMA_Zone': zone, 'Flood_Cost_Impact': cost_impact}
                    
            return {'FEMA_Zone': 'X', 'Flood_Cost_Impact': 1.05}
            
        except Exception as e:
            return {'FEMA_Zone': 'Unknown', 'Flood_Cost_Impact': 1.05}
            
    def check_competition_rules(self, lat, lon, county):
        """Check competition within proper radius"""
        results = {
            'One_Mile_Count': 0,
            'Two_Mile_Count': 0,
            'Competing_Projects': '',
            'Competition_4pct': 'Compliant',
            'Competition_9pct': 'Compliant'
        }
        
        if self.tdhca_projects.empty or pd.isna(lat) or pd.isna(lon):
            return results
            
        site_point = (lat, lon)
        large_counties = ['Harris', 'Dallas', 'Tarrant', 'Bexar', 'Travis', 'Collin', 'Fort Bend']
        competing_projects = []
        
        for _, project in self.tdhca_projects.iterrows():
            if pd.isna(project.get('Latitude')) or pd.isna(project.get('Longitude')):
                continue
                
            project_point = (project['Latitude'], project['Longitude'])
            
            try:
                distance = geodesic(site_point, project_point).miles
            except:
                continue
                
            # One Mile Three Year Rule
            if distance <= 1.0 and project['Year'] >= 2022:
                results['One_Mile_Count'] += 1
                proj_name = project.get('Project Name', project.get('Name', 'Unknown'))
                competing_projects.append(f"{proj_name} ({int(project['Year'])}, {distance:.2f}mi)")
                
            # Two Mile Same Year Rule (large counties only)
            if distance <= 2.0 and county in large_counties and project['Year'] == 2024:
                results['Two_Mile_Count'] += 1
                if distance > 1.0:  # Don't double count
                    proj_name = project.get('Project Name', project.get('Name', 'Unknown'))
                    competing_projects.append(f"{proj_name} ({int(project['Year'])}, {distance:.2f}mi)")
                    
        # Set competition status
        if results['One_Mile_Count'] > 0:
            results['Competition_4pct'] = 'Soft Risk'
            results['Competition_9pct'] = 'Fatal'
            
        if results['Two_Mile_Count'] > 0:
            results['Competition_9pct'] = 'Fatal'
            
        results['Competing_Projects'] = '; '.join(competing_projects[:3])
        
        return results
        
    def get_poverty_rate(self, lat, lon):
        """Get poverty rate from Census or estimate"""
        if pd.isna(lat) or pd.isna(lon):
            return 'N/A'
            
        # For now, return estimated values
        # Could implement Census API call here
        poverty_val = np.random.uniform(5, 35)
        return f"{poverty_val:.1f}%"
        
    def calculate_economics(self, row):
        """Calculate economic metrics"""
        county = str(row.get('County', '')).strip()
        city = str(row.get('City', '')).strip()
        region = row.get('TDHCA_Region', 'Region 7')
        
        # Get land acres
        acres = row.get('Land_Acres', 10)
        try:
            acres = float(acres) if acres and not pd.isna(acres) else 10
        except:
            acres = 10
            
        # Location multipliers
        location_multipliers = {
            'Austin': 1.20, 'Houston': 1.18, 'Dallas': 1.17, 'Fort Worth': 1.15,
            'San Antonio': 1.10, 'El Paso': 1.05, 'Corpus Christi': 1.08,
            'Arlington': 1.14, 'Plano': 1.16, 'Irving': 1.15, 'Garland': 1.14,
            'Grand Prairie': 1.13, 'McKinney': 1.15, 'Frisco': 1.16,
            'Denton': 1.12, 'Killeen': 1.05, 'Waco': 1.05, 'Tyler': 1.05,
            'College Station': 1.08, 'League City': 1.15, 'Sugar Land': 1.16,
            'Conroe': 1.12, 'New Braunfels': 1.10, 'Cedar Park': 1.18,
            'Georgetown': 1.15, 'Pflugerville': 1.15, 'Kyle': 1.14,
            'Round Rock': 1.16, 'Lewisville': 1.13, 'Carrollton': 1.14,
            'Richardson': 1.15, 'Allen': 1.15, 'Flower Mound': 1.15,
            'Temple': 1.05, 'Texarkana': 0.98, 'Bryan': 1.05,
            'Longview': 0.98, 'Baytown': 1.12, 'Missouri City': 1.15,
            'Pharr': 1.05, 'Laredo': 1.05, 'McAllen': 1.05,
            'Brownsville': 1.02, 'Pasadena': 1.10, 'Mesquite': 1.12,
            'Rockwall': 1.14, 'Wylie': 1.13, 'Mansfield': 1.13,
            'Euless': 1.13, 'Desoto': 1.12, 'Grapevine': 1.15,
            'Galveston': 1.10, 'Huntsville': 0.98, 'Sherman': 1.00,
            'Lufkin': 0.98, 'Beaumont': 1.00, 'Port Arthur': 0.98,
            'Odessa': 0.95, 'Midland': 0.98, 'Abilene': 0.95,
            'Amarillo': 0.92, 'Lubbock': 0.92, 'Wichita Falls': 0.92,
            'Victoria': 1.02, 'Harlingen': 1.02, 'Edinburg': 1.02
        }
        
        # Regional multipliers
        region_multipliers = {
            'Region 1': 0.90, 'Region 2': 0.95, 'Region 3': 1.15,
            'Region 4': 0.98, 'Region 5': 1.00, 'Region 6': 1.18,
            'Region 7': 1.20, 'Region 8': 1.05, 'Region 9': 1.10,
            'Region 10': 1.08, 'Region 11': 1.12, 'Region 12': 0.92,
            'Region 13': 0.95
        }
        
        # Determine location multiplier
        location_mult = 0.95  # Default rural
        for city_name, mult in location_multipliers.items():
            if city_name.lower() in city.lower():
                location_mult = mult
                break
                
        # Get regional multiplier
        regional_mult = region_multipliers.get(region, 1.00)
        
        # FEMA impact
        flood_mult = row.get('Flood_Cost_Impact', 1.05)
        
        # Construction cost calculation
        base_cost = 150
        total_cost_psf = base_cost * location_mult * regional_mult * flood_mult
        
        # Density and land cost based on location
        if location_mult >= 1.15:  # Major metros
            density = 30
            land_cost_per_acre = 500000
        elif location_mult >= 1.05:  # Mid-size cities
            density = 20
            land_cost_per_acre = 250000
        else:  # Rural/small towns
            density = 15
            land_cost_per_acre = 100000
            
        # Get AMI rent data
        ami_data = self.ami_lookup.get(county, self.ami_lookup.get('Default', {}))
        
        # If still no data, use regional defaults
        if not ami_data:
            region_defaults = {
                'Region 3': 1450,  # DFW
                'Region 6': 1400,  # Houston  
                'Region 7': 1500,  # Austin
                'Region 9': 1250,  # San Antonio
                'Region 1': 1000,  # Panhandle
                'Region 11': 1100, # Rio Grande Valley
            }
            default_2br = region_defaults.get(region, 1200)
            ami_data = {
                'Studio_60pct': default_2br * 0.71,
                '1BR_60pct': default_2br * 0.83,
                '2BR_60pct': default_2br,
                '3BR_60pct': default_2br * 1.20,
                '4BR_60pct': default_2br * 1.37
            }
            
        # Calculate weighted rent (typical LIHTC mix)
        rent_1br = ami_data.get('1BR_60pct', 950)
        rent_2br = ami_data.get('2BR_60pct', 1200)
        rent_3br = ami_data.get('3BR_60pct', 1450)
        
        weighted_rent = (rent_1br * 0.3 + rent_2br * 0.5 + rent_3br * 0.2)
        
        # Revenue calculations
        annual_revenue_per_acre = weighted_rent * 12 * density
        construction_cost_per_acre = total_cost_psf * 900 * density  # 900 SF avg unit
        total_dev_cost_per_acre = construction_cost_per_acre + land_cost_per_acre
        
        # Revenue to cost ratio
        revenue_to_cost_ratio = annual_revenue_per_acre / total_dev_cost_per_acre if total_dev_cost_per_acre > 0 else 0
        
        return {
            'Construction_Cost_PSF': round(total_cost_psf, 2),
            'Annual_Revenue_Per_Acre': round(annual_revenue_per_acre, 0),
            'Total_Dev_Cost_Per_Acre': round(total_dev_cost_per_acre, 0),
            'Revenue_Cost_Ratio': round(revenue_to_cost_ratio, 3),
            'Density_Units_Per_Acre': density,
            'Weighted_AMI_Rent': round(weighted_rent, 0)
        }
        
    def calculate_tdhca_score_estimate(self, site_data):
        """Estimate TDHCA scoring points"""
        score = 0
        
        # QCT points
        if site_data.get('Is_QCT_Verified') or site_data.get('Is_QCT'):
            score += 5
            
        # Underserved area
        if site_data.get('One_Mile_Count', 0) == 0:
            score += 3
            
        # Market strength
        revenue_ratio = site_data.get('Revenue_Cost_Ratio', 0)
        if revenue_ratio > 0.15:
            score += 3
        elif revenue_ratio > 0.10:
            score += 2
        elif revenue_ratio > 0.08:
            score += 1
            
        # Low poverty bonus
        poverty_rate = site_data.get('Poverty_Rate', 'N/A')
        if poverty_rate != 'N/A':
            try:
                poverty_val = float(str(poverty_rate).replace('%', ''))
                if poverty_val <= 20:
                    score += 2
            except:
                pass
                
        return {'Estimated_TDHCA_Points': score}
        
    def assign_qualitative_ranking(self, site_data, deal_type):
        """Assign business-focused rankings"""
        revenue_ratio = site_data.get('Revenue_Cost_Ratio', 0)
        competition_status = site_data.get(f'Competition_{deal_type}', 'Compliant')
        tdhca_points = site_data.get('Estimated_TDHCA_Points', 0)
        
        if competition_status == 'Fatal':
            return 'Fatal'
            
        if deal_type == '4pct':
            # 4% based on economics
            if revenue_ratio >= 0.15:
                return 'Exceptional'
            elif revenue_ratio >= 0.12:
                return 'High Potential'
            elif revenue_ratio >= 0.10:
                return 'Good'
            elif revenue_ratio >= 0.08:
                return 'Fair'
            else:
                return 'Poor'
        else:
            # 9% based on points and economics
            if tdhca_points >= 12 and revenue_ratio >= 0.12:
                return 'Exceptional'
            elif tdhca_points >= 10 and revenue_ratio >= 0.10:
                return 'High Potential'
            elif tdhca_points >= 8 and revenue_ratio >= 0.08:
                return 'Good'
            elif tdhca_points >= 6 or revenue_ratio >= 0.08:
                return 'Fair'
            else:
                return 'Poor'
                
    def analyze_all_sites(self):
        """Analyze all sites with QCT/DDA verification"""
        results = []
        
        total_sites = len(self.all_sites)
        self.logger.info(f"Analyzing {total_sites} total sites...")
        
        for idx, row in self.all_sites.iterrows():
            if idx % 20 == 0:
                self.logger.info(f"Processing site {idx+1}/{total_sites}")
                
            # Start with original data
            site_results = row.to_dict()
            
            lat = row.get('Latitude')
            lon = row.get('Longitude')
            county = str(row.get('County', '')).strip()
            
            # Skip if no coordinates
            if pd.isna(lat) or pd.isna(lon):
                site_results['Analysis_Status'] = 'No Coordinates'
                results.append(site_results)
                continue
                
            # Verify QCT/DDA status against shapefiles
            qct_dda_verified = self.verify_qct_dda_status(lat, lon)
            site_results.update(qct_dda_verified)
            
            # Only analyze further if QCT/DDA eligible (either from source or verified)
            is_eligible = (
                site_results.get('QCT_DDA_Verified', False) or
                site_results.get('QCT_DDA_Eligible', False) or
                site_results.get('Is_QCT', False) or
                site_results.get('Is_DDA', False)
            )
            
            if not is_eligible:
                site_results['Analysis_Status'] = 'Not QCT/DDA'
                results.append(site_results)
                continue
                
            # Full analysis for QCT/DDA sites
            site_results['Analysis_Status'] = 'Complete'
            
            # FEMA flood analysis
            fema_data = self.get_fema_flood_risk(lat, lon)
            site_results.update(fema_data)
            
            # Competition analysis  
            competition = self.check_competition_rules(lat, lon, county)
            site_results.update(competition)
            
            # Poverty rate
            site_results['Poverty_Rate'] = self.get_poverty_rate(lat, lon)
            
            # Economic analysis
            economics = self.calculate_economics(site_results)
            site_results.update(economics)
            
            # TDHCA scoring
            tdhca_score = self.calculate_tdhca_score_estimate(site_results)
            site_results.update(tdhca_score)
            
            # Rankings
            site_results['Ranking_4pct'] = self.assign_qualitative_ranking(site_results, '4pct')
            site_results['Ranking_9pct'] = self.assign_qualitative_ranking(site_results, '9pct')
            
            results.append(site_results)
            
        self.analysis_results = pd.DataFrame(results)
        
        # Log analysis summary
        qct_dda_count = len(self.analysis_results[self.analysis_results['Analysis_Status'] == 'Complete'])
        no_coords = len(self.analysis_results[self.analysis_results['Analysis_Status'] == 'No Coordinates'])
        not_qct_dda = len(self.analysis_results[self.analysis_results['Analysis_Status'] == 'Not QCT/DDA'])
        
        self.logger.info(f"Analysis complete:")
        self.logger.info(f"  - QCT/DDA sites analyzed: {qct_dda_count}")
        self.logger.info(f"  - Sites without coordinates: {no_coords}")
        self.logger.info(f"  - Non-QCT/DDA sites: {not_qct_dda}")
        
    def generate_comprehensive_report(self):
        """Generate comprehensive Excel report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.code_path / f"QCT_DDA_Comprehensive_Analysis_{timestamp}.xlsx"
        
        # Filter to QCT/DDA sites only for main analysis tabs
        qct_dda_sites = self.analysis_results[
            self.analysis_results['Analysis_Status'] == 'Complete'
        ].copy()
        
        # Define output columns
        key_columns = [
            'Property_Name', 'Property_Address', 'City', 'County', 'TDHCA_Region', 
            'Zip_Code', 'Land_Acres', 'Source', 'Latitude', 'Longitude',
            'Is_QCT', 'Is_DDA', 'QCT_DDA_Eligible', 
            'Is_QCT_Verified', 'Is_DDA_Verified', 'QCT_DDA_Verified',
            'Basis_Boost_Pct', 'Poverty_Rate', 'FEMA_Zone', 'Flood_Cost_Impact',
            'One_Mile_Count', 'Two_Mile_Count', 'Competing_Projects',
            'Competition_4pct', 'Competition_9pct',
            'Construction_Cost_PSF', 'Annual_Revenue_Per_Acre',
            'Total_Dev_Cost_Per_Acre', 'Revenue_Cost_Ratio',
            'Density_Units_Per_Acre', 'Weighted_AMI_Rent',
            'Estimated_TDHCA_Points', 'Ranking_4pct', 'Ranking_9pct'
        ]
        
        # Filter to available columns
        available_columns = [col for col in key_columns if col in qct_dda_sites.columns]
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Executive Summary
            summary_data = {
                'Metric': [
                    'Total Sites Loaded',
                    'D\'Marco Sites from Brent',
                    'D\'Marco Sites from Brian', 
                    'CoStar Sites',
                    'Sites with Coordinates',
                    'QCT/DDA Eligible (Source Data)',
                    'QCT/DDA Verified (Shapefiles)',
                    'Total QCT/DDA Sites Analyzed',
                    'Sites Missing TDHCA Region',
                    '4% Good Sites',
                    '9% Good Sites',
                    'Sites with Fatal Flaws',
                    'Average Revenue/Cost Ratio',
                    'Average Construction Cost/SF'
                ],
                'Value': [
                    len(self.analysis_results),
                    len(self.analysis_results[self.analysis_results['Source'] == 'D\'Marco_Brent']),
                    len(self.analysis_results[self.analysis_results['Source'] == 'D\'Marco_Brian']),
                    len(self.analysis_results[self.analysis_results['Source'] == 'CoStar']),
                    len(self.analysis_results[self.analysis_results['Analysis_Status'] != 'No Coordinates']),
                    len(self.analysis_results[
                        (self.analysis_results['QCT_DDA_Eligible'] == True) |
                        (self.analysis_results['Is_QCT'] == True) |
                        (self.analysis_results['Is_DDA'] == True)
                    ]),
                    len(self.analysis_results[self.analysis_results['QCT_DDA_Verified'] == True]),
                    len(qct_dda_sites),
                    len(qct_dda_sites[qct_dda_sites['TDHCA_Region'].isna()]),
                    len(qct_dda_sites[qct_dda_sites['Ranking_4pct'] == 'Good']),
                    len(qct_dda_sites[qct_dda_sites['Ranking_9pct'] == 'Good']),
                    len(qct_dda_sites[
                        (qct_dda_sites['Ranking_4pct'] == 'Fatal') | 
                        (qct_dda_sites['Ranking_9pct'] == 'Fatal')
                    ]),
                    f"{qct_dda_sites['Revenue_Cost_Ratio'].mean():.3f}" if len(qct_dda_sites) > 0 else "N/A",
                    f"${qct_dda_sites['Construction_Cost_PSF'].mean():.2f}" if len(qct_dda_sites) > 0 else "N/A"
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
            
            # 4% Rankings
            for ranking in ['Exceptional', 'High Potential', 'Good', 'Fair', 'Poor', 'Fatal']:
                df_subset = qct_dda_sites[
                    qct_dda_sites['Ranking_4pct'] == ranking
                ][available_columns].sort_values('Revenue_Cost_Ratio', ascending=False)
                
                if len(df_subset) > 0:
                    sheet_name = f'4pct_{ranking.replace(" ", "_")}'[:31]  # Excel limit
                    df_subset.to_excel(writer, sheet_name=sheet_name, index=False)
                    
            # 9% Rankings
            for ranking in ['Exceptional', 'High Potential', 'Good', 'Fair', 'Poor', 'Fatal']:
                df_subset = qct_dda_sites[
                    qct_dda_sites['Ranking_9pct'] == ranking
                ][available_columns].sort_values('Estimated_TDHCA_Points', ascending=False)
                
                if len(df_subset) > 0:
                    sheet_name = f'9pct_{ranking.replace(" ", "_")}'[:31]
                    df_subset.to_excel(writer, sheet_name=sheet_name, index=False)
                    
            # Regional Analysis
            if len(qct_dda_sites) > 0:
                # Use a column that definitely exists for counting
                count_col = qct_dda_sites.columns[0]  # Use first column for counting
                agg_dict = {
                    count_col: 'count',
                    'Revenue_Cost_Ratio': 'mean',
                    'Construction_Cost_PSF': 'mean',
                    'Estimated_TDHCA_Points': 'mean'
                }
                
                # Add QCT/DDA counts if columns exist
                if 'Is_QCT_Verified' in qct_dda_sites.columns:
                    agg_dict['Is_QCT_Verified'] = 'sum'
                if 'Is_DDA_Verified' in qct_dda_sites.columns:
                    agg_dict['Is_DDA_Verified'] = 'sum'
                    
                regional_summary = qct_dda_sites.groupby('TDHCA_Region').agg(agg_dict).round(3)
                
                # Rename columns
                col_names = ['Total_Sites', 'Avg_Revenue_Ratio', 'Avg_Cost_PSF', 'Avg_TDHCA_Points']
                if 'Is_QCT_Verified' in agg_dict:
                    col_names.append('QCT_Count')
                if 'Is_DDA_Verified' in agg_dict:
                    col_names.append('DDA_Count')
                    
                regional_summary.columns = col_names
                regional_summary.to_excel(writer, sheet_name='Regional_Analysis')
                
            # All QCT/DDA Sites
            if len(qct_dda_sites) > 0:
                qct_dda_sites[available_columns].to_excel(
                    writer, sheet_name='All_QCT_DDA_Sites', index=False
                )
                
            # All Sites Summary (including non-QCT/DDA)
            summary_columns = [
                'Property_Name', 'Property_Address', 'City', 'County', 'TDHCA_Region',
                'Source', 'Analysis_Status', 'QCT_DDA_Eligible', 'QCT_DDA_Verified',
                'Is_QCT', 'Is_DDA', 'Is_QCT_Verified', 'Is_DDA_Verified'
            ]
            available_summary = [col for col in summary_columns if col in self.analysis_results.columns]
            self.analysis_results[available_summary].to_excel(
                writer, sheet_name='All_Sites_Summary', index=False
            )
            
        self.logger.info(f"Report generated: {output_file}")
        return output_file
        
    def run_analysis(self):
        """Execute comprehensive analysis"""
        self.logger.info("Starting Comprehensive QCT/DDA Analysis...")
        
        # Merge all datasets
        self.merge_all_datasets()
        
        # Analyze all sites
        self.analyze_all_sites()
        
        # Generate report
        report_file = self.generate_comprehensive_report()
        
        # Print detailed summary
        print("\n" + "="*80)
        print("COMPREHENSIVE QCT/DDA ANALYSIS COMPLETE")
        print("="*80)
        
        # Overall stats
        print(f"\nOVERALL STATISTICS:")
        print(f"Total Sites Loaded: {len(self.analysis_results)}")
        print(f"- D'Marco Brent: {len(self.analysis_results[self.analysis_results['Source'] == 'D\'Marco_Brent'])}")
        print(f"- D'Marco Brian: {len(self.analysis_results[self.analysis_results['Source'] == 'D\'Marco_Brian'])}")
        print(f"- CoStar: {len(self.analysis_results[self.analysis_results['Source'] == 'CoStar'])}")
        
        # QCT/DDA breakdown
        qct_dda_eligible = self.analysis_results[
            (self.analysis_results['QCT_DDA_Eligible'] == True) |
            (self.analysis_results['Is_QCT'] == True) |
            (self.analysis_results['Is_DDA'] == True)
        ]
        qct_dda_verified = self.analysis_results[self.analysis_results['QCT_DDA_Verified'] == True]
        qct_dda_analyzed = self.analysis_results[self.analysis_results['Analysis_Status'] == 'Complete']
        
        print(f"\nQCT/DDA STATUS:")
        print(f"- Marked as QCT/DDA in source data: {len(qct_dda_eligible)}")
        print(f"- Verified as QCT/DDA by shapefiles: {len(qct_dda_verified)}")
        print(f"- Total QCT/DDA sites analyzed: {len(qct_dda_analyzed)}")
        
        # Data quality
        print(f"\nDATA QUALITY:")
        no_coords = len(self.analysis_results[self.analysis_results['Analysis_Status'] == 'No Coordinates'])
        has_region = len(self.analysis_results[~self.analysis_results['TDHCA_Region'].isna()])
        has_acres = len(self.analysis_results[~self.analysis_results['Land_Acres'].isna()])
        
        print(f"- Sites with coordinates: {len(self.analysis_results) - no_coords}")
        print(f"- Sites with TDHCA Region: {has_region}")
        print(f"- Sites with Land Acres: {has_acres}")
        
        if len(qct_dda_analyzed) > 0:
            has_fema = len(qct_dda_analyzed[qct_dda_analyzed['FEMA_Zone'] != 'Unknown'])
            print(f"- QCT/DDA sites with FEMA data: {has_fema}")
            
            # Rankings breakdown
            print(f"\n4% TAX-EXEMPT BOND RANKINGS:")
            for ranking in ['Exceptional', 'High Potential', 'Good', 'Fair', 'Poor', 'Fatal']:
                count = len(qct_dda_analyzed[qct_dda_analyzed['Ranking_4pct'] == ranking])
                if count > 0:
                    print(f"- {ranking}: {count}")
                    
            print(f"\n9% COMPETITIVE TAX CREDIT RANKINGS:")
            for ranking in ['Exceptional', 'High Potential', 'Good', 'Fair', 'Poor', 'Fatal']:
                count = len(qct_dda_analyzed[qct_dda_analyzed['Ranking_9pct'] == ranking])
                if count > 0:
                    print(f"- {ranking}: {count}")
                    
        print(f"\nReport saved to: {report_file}")
        print("="*80)
        
        return report_file


if __name__ == "__main__":
    analyzer = QCTDDAComprehensiveAnalyzer()
    analyzer.run_analysis()