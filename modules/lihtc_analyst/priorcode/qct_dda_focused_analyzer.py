#!/usr/bin/env python3
"""
QCT/DDA Focused LIHTC Analysis System
Focus on 30% basis boost sites only with qualitative rankings

Combines D'Marco 65 sites + CoStar 406 properties
Separate 4% and 9% analysis paths with expert corrections applied

Rankings: Exceptional → High Potential → Good → Fair → Poor → Fatal

Author: TDHCA Analysis System (Expert Corrected)
Date: 2025-06-20
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

class QCTDDAFocusedAnalyzer:
    """QCT/DDA Focused analyzer with qualitative rankings"""
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Key data paths
        self.base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects")
        self.code_path = self.base_path / "CTCAC_RAG/code"
        self.data_path = self.base_path / "Lvg_Bond_Execution/Data Sets"
        
        # Results storage
        self.merged_data = None
        self.qct_dda_sites = None
        self.analysis_results_4pct = None
        self.analysis_results_9pct = None
        
        # Load TDHCA Regional mapping
        self.load_tdhca_regional_mapping()
        
    def load_tdhca_regional_mapping(self):
        """Load Texas County to TDHCA Region mapping"""
        try:
            # Try D'Marco's analysis file first
            dmarco_file = self.code_path / "DMarco_Sites_Final_PositionStack_20250618_235606.xlsx"
            if dmarco_file.exists():
                df = pd.read_excel(dmarco_file, sheet_name='All_Sites_Final')
                # Extract county-region mapping
                county_region = df.dropna(subset=['County', 'Region']).drop_duplicates(['County'])
                self.county_to_region = dict(zip(county_region['County'], county_region['Region']))
                
            # Supplement with official TDHCA source for complete mapping
            tdhca_file = self.data_path / "State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
            if tdhca_file.exists():
                tdhca_df = pd.read_excel(tdhca_file)
                if 'County' in tdhca_df.columns and 'Region' in tdhca_df.columns:
                    tdhca_mapping = tdhca_df.dropna(subset=['County', 'Region']).drop_duplicates(['County'])
                    tdhca_dict = dict(zip(tdhca_mapping['County'], tdhca_mapping['Region']))
                    # Merge with D'Marco data
                    self.county_to_region.update(tdhca_dict)
                    
            self.logger.info(f"Loaded TDHCA regional mapping for {len(self.county_to_region)} counties")
            
        except Exception as e:
            self.logger.warning(f"Could not load regional mapping: {e}")
            # Default mapping for major counties
            self.county_to_region = {
                'Harris': 'Region 6', 'Dallas': 'Region 3', 'Tarrant': 'Region 3',
                'Bexar': 'Region 9', 'Travis': 'Region 7', 'Collin': 'Region 3',
                'Denton': 'Region 3', 'Fort Bend': 'Region 6', 'El Paso': 'Region 13'
            }
            
    def load_dmarco_sites(self):
        """Load D'Marco's 65 sites"""
        dmarco_file = self.code_path / "DMarco_Sites_Final_PositionStack_20250618_235606.xlsx"
        
        if not dmarco_file.exists():
            self.logger.error(f"D'Marco file not found: {dmarco_file}")
            return pd.DataFrame()
            
        dmarco_df = pd.read_excel(dmarco_file, sheet_name='All_Sites_Final')
        dmarco_df['Source'] = 'D\'Marco'
        self.logger.info(f"Loaded {len(dmarco_df)} D'Marco sites")
        return dmarco_df
        
    def load_costar_properties(self):
        """Load CoStar 406 properties"""
        # Try multiple possible CoStar file locations
        costar_files = [
            self.code_path / "FIXED_POSITIONSTACK_RESULTS/FIXED_Enhanced_CoStar_4pct_Bond_20250601_235030.xlsx",
            self.code_path / "CoStar_Land_Analysis_With_Counties_20250617_223737.xlsx"
        ]
        
        costar_df = pd.DataFrame()
        for file_path in costar_files:
            if file_path.exists():
                costar_df = pd.read_excel(file_path)
                costar_df['Source'] = 'CoStar'
                self.logger.info(f"Loaded {len(costar_df)} CoStar properties from {file_path.name}")
                break
                
        return costar_df
        
    def merge_and_standardize(self, dmarco_df, costar_df):
        """Merge and standardize datasets"""
        # Standardize column names
        column_mapping = {
            'MailingName': 'Property_Name', 'property_name': 'Property_Name',
            'Address': 'Street_Address', 'address': 'Street_Address',
            'City': 'City', 'city': 'City',
            'County': 'County', 'county': 'County',
            'Zip': 'Zip_Code', 'zip': 'Zip_Code',
            'Acres': 'Land_Acres', 'acres': 'Land_Acres',
            'Region': 'TDHCA_Region', 'region': 'TDHCA_Region',
            'Latitude': 'Latitude', 'lat': 'Latitude', 'latitude': 'Latitude',
            'Longitude': 'Longitude', 'lng': 'Longitude', 'lon': 'Longitude', 'longitude': 'Longitude',
            'QCT_Status': 'Is_QCT', 'qct_status': 'Is_QCT',
            'DDA_Status': 'Is_DDA', 'dda_status': 'Is_DDA',
            'QCT_DDA_Eligible': 'QCT_DDA_Eligible'
        }
        
        # Apply mappings
        dmarco_df = dmarco_df.rename(columns=column_mapping)
        costar_df = costar_df.rename(columns=column_mapping)
        
        # Merge datasets
        all_data = pd.concat([dmarco_df, costar_df], ignore_index=True, sort=False)
        
        # Add TDHCA Region for properties missing it
        for idx, row in all_data.iterrows():
            if pd.isna(row.get('TDHCA_Region')) and not pd.isna(row.get('County')):
                county = str(row['County']).strip()
                if county in self.county_to_region:
                    all_data.loc[idx, 'TDHCA_Region'] = self.county_to_region[county]
                    
        self.logger.info(f"Merged dataset contains {len(all_data)} total properties")
        return all_data
        
    def load_qct_dda_data(self):
        """Load QCT/DDA shapefiles"""
        qct_path = self.data_path / "HUD DDA QCT/QUALIFIED_CENSUS_TRACTS_7341711606021821459.gpkg"
        dda_path = self.data_path / "HUD DDA QCT/Difficult_Development_Areas_-4200740390724245794.gpkg"
        
        self.qct_gdf = gpd.read_file(qct_path).to_crs(epsg=4326)
        self.dda_gdf = gpd.read_file(dda_path).to_crs(epsg=4326)
        
        self.logger.info(f"Loaded {len(self.qct_gdf)} QCT and {len(self.dda_gdf)} DDA areas")
        
    def check_qct_dda_status(self, lat, lon):
        """Check QCT/DDA status for coordinates"""
        point = Point(lon, lat)
        
        is_qct = any(self.qct_gdf.geometry.contains(point))
        is_dda = any(self.dda_gdf.geometry.contains(point))
        eligible = is_qct or is_dda
        
        return {
            'Is_QCT': is_qct,
            'Is_DDA': is_dda,
            'QCT_DDA_Eligible': eligible,
            'Basis_Boost_Pct': 30 if eligible else 0
        }
        
    def load_ami_data(self):
        """Load HUD AMI rent data"""
        ami_file = self.data_path / "HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx"
        
        try:
            ami_df = pd.read_excel(ami_file, sheet_name='Texas')
            
            self.ami_lookup = {}
            col_names = ami_df.columns.tolist()
            
            for _, row in ami_df.iterrows():
                county = str(row.iloc[1]).strip() if len(row) > 1 else None
                if not county or county == 'nan':
                    continue
                    
                # Extract rent data from last 20 columns
                rent_cols_start = len(col_names) - 20
                
                rent_data = {
                    # 50% AMI rents
                    'Studio_50pct': row.iloc[rent_cols_start] if rent_cols_start < len(row) else 700,
                    '1BR_50pct': row.iloc[rent_cols_start + 1] if rent_cols_start + 1 < len(row) else 800,
                    '2BR_50pct': row.iloc[rent_cols_start + 2] if rent_cols_start + 2 < len(row) else 1000,
                    '3BR_50pct': row.iloc[rent_cols_start + 3] if rent_cols_start + 3 < len(row) else 1200,
                    '4BR_50pct': row.iloc[rent_cols_start + 4] if rent_cols_start + 4 < len(row) else 1400,
                    
                    # 60% AMI rents
                    'Studio_60pct': row.iloc[rent_cols_start + 5] if rent_cols_start + 5 < len(row) else 850,
                    '1BR_60pct': row.iloc[rent_cols_start + 6] if rent_cols_start + 6 < len(row) else 950,
                    '2BR_60pct': row.iloc[rent_cols_start + 7] if rent_cols_start + 7 < len(row) else 1200,
                    '3BR_60pct': row.iloc[rent_cols_start + 8] if rent_cols_start + 8 < len(row) else 1450,
                    '4BR_60pct': row.iloc[rent_cols_start + 9] if rent_cols_start + 9 < len(row) else 1650,
                    
                    # 70% AMI rents
                    'Studio_70pct': row.iloc[rent_cols_start + 10] if rent_cols_start + 10 < len(row) else 1000,
                    '1BR_70pct': row.iloc[rent_cols_start + 11] if rent_cols_start + 11 < len(row) else 1100,
                    '2BR_70pct': row.iloc[rent_cols_start + 12] if rent_cols_start + 12 < len(row) else 1400,
                    '3BR_70pct': row.iloc[rent_cols_start + 13] if rent_cols_start + 13 < len(row) else 1700,
                    '4BR_70pct': row.iloc[rent_cols_start + 14] if rent_cols_start + 14 < len(row) else 1900,
                    
                    # 80% AMI rents
                    'Studio_80pct': row.iloc[rent_cols_start + 15] if rent_cols_start + 15 < len(row) else 1150,
                    '1BR_80pct': row.iloc[rent_cols_start + 16] if rent_cols_start + 16 < len(row) else 1250,
                    '2BR_80pct': row.iloc[rent_cols_start + 17] if rent_cols_start + 17 < len(row) else 1600,
                    '3BR_80pct': row.iloc[rent_cols_start + 18] if rent_cols_start + 18 < len(row) else 1950,
                    '4BR_80pct': row.iloc[rent_cols_start + 19] if rent_cols_start + 19 < len(row) else 2200,
                    
                    'MSA_Name': row.iloc[2] if len(row) > 2 else 'Non-Metro'
                }
                
                self.ami_lookup[county] = rent_data
                
            self.logger.info(f"Loaded AMI data for {len(self.ami_lookup)} Texas counties")
            
        except Exception as e:
            self.logger.warning(f"AMI data loading error: {e}")
            self.ami_lookup = {}
            
    def load_tdhca_projects(self):
        """Load TDHCA competition projects"""
        project_file = self.data_path / "State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
        
        try:
            self.tdhca_projects = pd.read_excel(project_file)
            # Filter for recent competition years
            self.tdhca_projects['Year'] = pd.to_numeric(self.tdhca_projects['Year'], errors='coerce')
            self.tdhca_projects = self.tdhca_projects[
                self.tdhca_projects['Year'].between(2021, 2024)
            ]
            self.logger.info(f"Loaded {len(self.tdhca_projects)} TDHCA projects for competition analysis")
        except Exception as e:
            self.logger.warning(f"TDHCA projects loading error: {e}")
            self.tdhca_projects = pd.DataFrame()
            
    def get_fema_flood_risk(self, lat, lon):
        """Get FEMA flood zone"""
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
            data = response.json()
            
            if 'features' in data and len(data['features']) > 0:
                zone = data['features'][0]['attributes'].get('FLD_ZONE', 'X')
                
                # FEMA cost impact
                if zone in ['VE', 'V']:
                    cost_impact = 1.30
                elif zone in ['AE', 'A']:
                    cost_impact = 1.20
                elif zone in ['AO', 'AH']:
                    cost_impact = 1.12
                elif zone == 'X':
                    cost_impact = 1.05
                else:
                    cost_impact = 1.05
                    
                return {'FEMA_Zone': zone, 'Flood_Cost_Impact': cost_impact}
            else:
                return {'FEMA_Zone': 'X', 'Flood_Cost_Impact': 1.05}
                
        except Exception as e:
            return {'FEMA_Zone': 'Unknown', 'Flood_Cost_Impact': 1.05}
            
    def check_competition_rules(self, lat, lon, county):
        """Check One Mile and Two Mile competition rules"""
        results = {
            'One_Mile_Count': 0,
            'Two_Mile_Count': 0,
            'Competition_4pct': 'Compliant',
            'Competition_9pct': 'Compliant'
        }
        
        if self.tdhca_projects.empty:
            return results
            
        site_point = (lat, lon)
        large_counties = ['Harris', 'Dallas', 'Tarrant', 'Bexar', 'Travis']
        
        for _, project in self.tdhca_projects.iterrows():
            if pd.isna(project.get('Latitude')) or pd.isna(project.get('Longitude')):
                continue
                
            project_point = (project['Latitude'], project['Longitude'])
            distance = geodesic(site_point, project_point).miles
            
            # One Mile Three Year Rule
            if distance <= 1.0 and project['Year'] >= 2022:
                results['One_Mile_Count'] += 1
                
            # Two Mile Same Year Rule (9% family new construction in large counties)
            if (county in large_counties and distance <= 2.0 and 
                project['Year'] == 2024):
                results['Two_Mile_Count'] += 1
                
        # Determine competition status
        if results['One_Mile_Count'] > 0:
            results['Competition_4pct'] = 'Soft Risk'  # Flag but not fatal
            results['Competition_9pct'] = 'Fatal'      # Hard elimination
            
        if results['Two_Mile_Count'] > 0:
            results['Competition_9pct'] = 'Fatal'      # Hard elimination for 9%
            
        return results
        
    def calculate_economics(self, row):
        """Calculate revenue/cost economics for land quality"""
        county = row.get('County', '')
        city = row.get('City', '')
        region = row.get('TDHCA_Region', 'Region 5')
        acres = row.get('Land_Acres', 10)
        
        # Location-based construction costs (from production files)
        location_multipliers = {
            'Austin': 1.20, 'Houston': 1.18, 'Dallas': 1.17, 'Fort Worth': 1.15,
            'San Antonio': 1.10, 'El Paso': 1.05, 'Corpus Christi': 1.08
        }
        
        # Regional multipliers by TDHCA region
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
        
        # Apply regional multiplier
        regional_mult = region_multipliers.get(region, 1.00)
        
        # FEMA flood impact
        flood_mult = row.get('Flood_Cost_Impact', 1.05)
        
        # Total construction cost per SF
        base_cost = 150
        total_cost_psf = base_cost * location_mult * regional_mult * flood_mult
        
        # Density based on location type
        if location_mult >= 1.15:  # Big cities
            density = 30
            land_cost_per_acre = 500000
        elif location_mult >= 1.05:  # Mid cities
            density = 20
            land_cost_per_acre = 250000
        else:  # Rural/small
            density = 15
            land_cost_per_acre = 100000
            
        # AMI rent data
        ami_data = self.ami_lookup.get(county, {})
        rent_2br_60 = ami_data.get('2BR_60pct', 1200)
        rent_1br_60 = ami_data.get('1BR_60pct', 1000)
        rent_3br_60 = ami_data.get('3BR_60pct', 1400)
        
        # Weighted average rent (typical LIHTC mix)
        weighted_rent = (rent_1br_60 * 0.3 + rent_2br_60 * 0.5 + rent_3br_60 * 0.2)
        
        # Revenue calculations
        annual_revenue_per_acre = weighted_rent * 12 * density
        construction_cost_per_acre = total_cost_psf * 900 * density  # 900 SF avg unit
        total_dev_cost_per_acre = construction_cost_per_acre + land_cost_per_acre
        
        # Return metrics
        revenue_to_cost_ratio = annual_revenue_per_acre / total_dev_cost_per_acre
        
        return {
            'Construction_Cost_PSF': round(total_cost_psf, 2),
            'Annual_Revenue_Per_Acre': round(annual_revenue_per_acre, 0),
            'Total_Dev_Cost_Per_Acre': round(total_dev_cost_per_acre, 0),
            'Revenue_Cost_Ratio': round(revenue_to_cost_ratio, 3),
            'Density_Units_Per_Acre': density,
            'Weighted_AMI_Rent': round(weighted_rent, 0)
        }
        
    def calculate_tdhca_score_estimate(self, row):
        """Estimate TDHCA 9% scoring potential"""
        score = 0
        
        # Opportunity Index (7 points) - based on poverty rate
        # Simplified: assume QCT areas get some points
        if row.get('Is_QCT'):
            score += 5  # Estimated points for low-income area
            
        # Underserved Area (0-5 points) - years since last award
        # Simplified: give points if not heavily competed
        if row.get('One_Mile_Count', 0) == 0:
            score += 3  # No recent competition
            
        # Market factors (estimated)
        revenue_ratio = row.get('Revenue_Cost_Ratio', 0)
        if revenue_ratio > 0.15:
            score += 3  # Strong market
        elif revenue_ratio > 0.10:
            score += 2  # Good market
        elif revenue_ratio > 0.08:
            score += 1  # Fair market
            
        # NOTE: Missing major categories:
        # - Local Government Resolution (17 points)
        # - Lender Feasibility Letter (26 points)  
        # - Other QAP categories (~115 points)
        
        return {
            'Estimated_TDHCA_Points': score,
            'Max_Possible_Estimated': 15,  # Only scoring what we can estimate
            'Missing_Major_Categories': 'Local Gov (17), Lender (26), Others (~115)'
        }
        
    def assign_qualitative_ranking(self, row, deal_type):
        """Assign qualitative ranking based on deal type"""
        
        # Check for fatal flaws first
        competition_status = row.get(f'Competition_{deal_type}', 'Compliant')
        if competition_status == 'Fatal':
            return 'Fatal'
            
        # Economic metrics
        revenue_ratio = row.get('Revenue_Cost_Ratio', 0)
        
        if deal_type == '4pct':
            # 4% deals: Economics primary, TDHCA secondary
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
                
        elif deal_type == '9pct':
            # 9% deals: TDHCA points primary, economics secondary (discounted)
            tdhca_points = row.get('Estimated_TDHCA_Points', 0)
            
            # Combined assessment (TDHCA weighted higher)
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
                
        return 'Fair'
        
    def analyze_qct_dda_sites(self):
        """Run analysis on QCT/DDA sites only"""
        # Load all data sources
        self.load_qct_dda_data()
        self.load_ami_data()
        self.load_tdhca_projects()
        
        # Filter for QCT/DDA sites only
        total_sites = len(self.qct_dda_sites)
        results = []
        
        for idx, row in self.qct_dda_sites.iterrows():
            if idx % 25 == 0:
                self.logger.info(f"Processing QCT/DDA site {idx+1}/{total_sites}")
                
            site_results = row.to_dict()
            
            # Skip if no coordinates
            if pd.isna(row.get('Latitude')) or pd.isna(row.get('Longitude')):
                continue
                
            lat = row['Latitude']
            lon = row['Longitude']
            county = row.get('County', '')
            
            # Verify QCT/DDA status if not already set
            if pd.isna(row.get('QCT_DDA_Eligible')):
                qct_dda = self.check_qct_dda_status(lat, lon)
                site_results.update(qct_dda)
                # Skip if not actually QCT/DDA
                if not qct_dda['QCT_DDA_Eligible']:
                    continue
            elif not row.get('QCT_DDA_Eligible'):
                continue  # Skip non-QCT/DDA sites
                
            # FEMA flood analysis
            fema_data = self.get_fema_flood_risk(lat, lon)
            site_results.update(fema_data)
            
            # Competition analysis
            competition = self.check_competition_rules(lat, lon, county)
            site_results.update(competition)
            
            # Economic analysis
            economics = self.calculate_economics(site_results)
            site_results.update(economics)
            
            # TDHCA scoring estimate
            tdhca_score = self.calculate_tdhca_score_estimate(site_results)
            site_results.update(tdhca_score)
            
            # Qualitative rankings
            site_results['Ranking_4pct'] = self.assign_qualitative_ranking(site_results, '4pct')
            site_results['Ranking_9pct'] = self.assign_qualitative_ranking(site_results, '9pct')
            
            results.append(site_results)
            
        self.analysis_results = pd.DataFrame(results)
        self.logger.info(f"Analysis complete for {len(self.analysis_results)} QCT/DDA sites")
        
        # Separate results by deal type
        self.analysis_results_4pct = self.analysis_results.copy()
        self.analysis_results_9pct = self.analysis_results.copy()
        
    def generate_comprehensive_report(self):
        """Generate Excel report with qualitative rankings"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.code_path / f"QCT_DDA_Focused_Analysis_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Executive Summary
            summary_data = {
                'Metric': [
                    'Total QCT/DDA Sites Analyzed',
                    'D\'Marco Sites (QCT/DDA)',
                    'CoStar Sites (QCT/DDA)',
                    '4% Exceptional Sites',
                    '4% High Potential Sites',
                    '4% Good Sites',
                    '9% Exceptional Sites',
                    '9% High Potential Sites',
                    '9% Good Sites',
                    'Sites with Fatal Flaws',
                    'Average Revenue/Cost Ratio',
                    'Average Construction Cost/SF'
                ],
                'Value': [
                    len(self.analysis_results),
                    len(self.analysis_results[self.analysis_results['Source'] == 'D\'Marco']),
                    len(self.analysis_results[self.analysis_results['Source'] == 'CoStar']),
                    len(self.analysis_results[self.analysis_results['Ranking_4pct'] == 'Exceptional']),
                    len(self.analysis_results[self.analysis_results['Ranking_4pct'] == 'High Potential']),
                    len(self.analysis_results[self.analysis_results['Ranking_4pct'] == 'Good']),
                    len(self.analysis_results[self.analysis_results['Ranking_9pct'] == 'Exceptional']),
                    len(self.analysis_results[self.analysis_results['Ranking_9pct'] == 'High Potential']),
                    len(self.analysis_results[self.analysis_results['Ranking_9pct'] == 'Good']),
                    len(self.analysis_results[
                        (self.analysis_results['Ranking_4pct'] == 'Fatal') | 
                        (self.analysis_results['Ranking_9pct'] == 'Fatal')
                    ]),
                    f"{self.analysis_results['Revenue_Cost_Ratio'].mean():.3f}",
                    f"${self.analysis_results['Construction_Cost_PSF'].mean():.2f}"
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
            
            # 4% Deal Rankings
            pct_4_rankings = ['Exceptional', 'High Potential', 'Good', 'Fair', 'Poor', 'Fatal']
            for ranking in pct_4_rankings:
                df_subset = self.analysis_results[
                    self.analysis_results['Ranking_4pct'] == ranking
                ].sort_values('Revenue_Cost_Ratio', ascending=False)
                
                if len(df_subset) > 0:
                    sheet_name = f'4pct_{ranking.replace(" ", "_")}'
                    df_subset.to_excel(writer, sheet_name=sheet_name, index=False)
                    
            # 9% Deal Rankings  
            pct_9_rankings = ['Exceptional', 'High Potential', 'Good', 'Fair', 'Poor', 'Fatal']
            for ranking in pct_9_rankings:
                df_subset = self.analysis_results[
                    self.analysis_results['Ranking_9pct'] == ranking
                ].sort_values('Estimated_TDHCA_Points', ascending=False)
                
                if len(df_subset) > 0:
                    sheet_name = f'9pct_{ranking.replace(" ", "_")}'
                    df_subset.to_excel(writer, sheet_name=sheet_name, index=False)
                    
            # Regional Analysis
            regional_summary = self.analysis_results.groupby('TDHCA_Region').agg({
                'Property_Name': 'count',
                'Revenue_Cost_Ratio': 'mean',
                'Construction_Cost_PSF': 'mean',
                'Estimated_TDHCA_Points': 'mean'
            }).round(3)
            regional_summary.columns = ['Total_Sites', 'Avg_Revenue_Ratio', 'Avg_Cost_PSF', 'Avg_TDHCA_Points']
            regional_summary.to_excel(writer, sheet_name='Regional_Analysis')
            
            # All QCT/DDA Sites
            self.analysis_results.to_excel(writer, sheet_name='All_QCT_DDA_Sites', index=False)
            
        self.logger.info(f"Report generated: {output_file}")
        return output_file
        
    def run_analysis(self):
        """Execute the complete QCT/DDA focused analysis"""
        self.logger.info("Starting QCT/DDA Focused Analysis...")
        
        # Load datasets
        dmarco_df = self.load_dmarco_sites()
        costar_df = self.load_costar_properties()
        
        # Merge and standardize
        self.merged_data = self.merge_and_standardize(dmarco_df, costar_df)
        
        # Filter for QCT/DDA sites only
        # First, identify QCT/DDA sites from existing data
        qct_dda_filter = (
            (self.merged_data.get('QCT_DDA_Eligible') == True) |
            (self.merged_data.get('Is_QCT') == True) |
            (self.merged_data.get('Is_DDA') == True)
        )
        
        self.qct_dda_sites = self.merged_data[qct_dda_filter].copy()
        
        if len(self.qct_dda_sites) == 0:
            # If no pre-identified QCT/DDA sites, check all sites
            self.logger.info("No pre-identified QCT/DDA sites found. Checking all sites...")
            self.qct_dda_sites = self.merged_data.copy()
            
        self.logger.info(f"Focusing analysis on {len(self.qct_dda_sites)} potential QCT/DDA sites")
        
        # Run comprehensive analysis
        self.analyze_qct_dda_sites()
        
        # Generate report
        report_file = self.generate_comprehensive_report()
        
        # Print summary
        print("\n" + "="*80)
        print("QCT/DDA FOCUSED ANALYSIS COMPLETE")
        print("="*80)
        print(f"\nQCT/DDA Sites Analyzed: {len(self.analysis_results)}")
        print(f"- D'Marco Sites: {len(self.analysis_results[self.analysis_results['Source'] == 'D\'Marco'])}")
        print(f"- CoStar Sites: {len(self.analysis_results[self.analysis_results['Source'] == 'CoStar'])}")
        
        print(f"\n4% TAX-EXEMPT BOND OPPORTUNITIES:")
        print(f"- Exceptional: {len(self.analysis_results[self.analysis_results['Ranking_4pct'] == 'Exceptional'])}")
        print(f"- High Potential: {len(self.analysis_results[self.analysis_results['Ranking_4pct'] == 'High Potential'])}")
        print(f"- Good: {len(self.analysis_results[self.analysis_results['Ranking_4pct'] == 'Good'])}")
        
        print(f"\n9% COMPETITIVE TAX CREDIT OPPORTUNITIES:")
        print(f"- Exceptional: {len(self.analysis_results[self.analysis_results['Ranking_9pct'] == 'Exceptional'])}")
        print(f"- High Potential: {len(self.analysis_results[self.analysis_results['Ranking_9pct'] == 'High Potential'])}")
        print(f"- Good: {len(self.analysis_results[self.analysis_results['Ranking_9pct'] == 'Good'])}")
        
        fatal_sites = len(self.analysis_results[
            (self.analysis_results['Ranking_4pct'] == 'Fatal') | 
            (self.analysis_results['Ranking_9pct'] == 'Fatal')
        ])
        print(f"\nSites with Fatal Flaws: {fatal_sites}")
        
        print(f"\nReport saved to: {report_file}")
        print("\nRANKING CRITERIA:")
        print("4% Deals: Revenue/Cost Ratio Primary, TDHCA Considerations Secondary")
        print("9% Deals: TDHCA Points Primary, Revenue/Cost Secondary (Discounted)")
        print("Focus: Only QCT/DDA sites (30% basis boost) for time investment efficiency")
        print("="*80)
        
        return report_file


if __name__ == "__main__":
    analyzer = QCTDDAFocusedAnalyzer()
    analyzer.run_analysis()