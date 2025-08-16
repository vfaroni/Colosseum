#!/usr/bin/env python3
"""
ENHANCED TDHCA ACCURATE Texas LIHTC Analyzer
Now captures rich AMI data and competing project details
"""

import os
import sys
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import time
import re
import math
from datetime import datetime, timedelta
import urllib.parse
from geopy.distance import geodesic

class TDHCAAccurateAnalyzer:
    def __init__(self, 
                 census_api_key: str,
                 positionstack_api_key: str = None,
                 hud_ami_file_path: str = None,
                 tdhca_project_file_path: str = None,
                 work_dir: str = None):
        """
        Initialize TDHCA Accurate Analyzer with correct distance rules
        """
        self.census_api_key = census_api_key
        self.positionstack_api_key = positionstack_api_key
        
        # Use code directory if no work_dir specified
        if work_dir is None:
            work_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code"
        
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)
        
        # Cache directory setup
        self.cache_dir = self.work_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Data containers
        self.qct_data = None
        self.dda_data = None
        self.ami_data = None
        self.tdhca_data = None
        
        # Load data files
        if hud_ami_file_path and Path(hud_ami_file_path).exists():
            self.load_ami_data(hud_ami_file_path)
            
        if tdhca_project_file_path and Path(tdhca_project_file_path).exists():
            self.load_tdhca_data(tdhca_project_file_path)
            
        # Load QCT/DDA data
        self.load_hud_designation_data()
        
        print(f"TDHCA Accurate Analyzer initialized")
        print(f"✅ Census API configured")
        print(f"✅ PositionStack API: {'configured' if positionstack_api_key else 'not configured'}")
        print(f"✅ TDHCA data: {len(self.tdhca_data) if self.tdhca_data is not None else 0} projects")
        print(f"✅ AMI data: {len(self.ami_data) if self.ami_data is not None else 0} areas")

    def load_ami_data(self, file_path: str):
        """Load HUD AMI data with ENHANCED rent limits capture"""
        try:
            print(f"Loading HUD AMI data from: {file_path}")
            df = pd.read_excel(file_path, sheet_name="MTSP2025-Static")
            texas_df = df[df['stusps'] == 'TX'].copy()
            
            self.ami_data = {}
            for _, row in texas_df.iterrows():
                fips = str(row['fips'])
                # ENHANCED: Capture ALL rent limits and income limits
                self.ami_data[fips] = {
                    'hud_area_name': row['hud_area_name'],
                    'county_name': row['County_Name'],
                    'metro': row['metro'] == 1,
                    'median_ami': row['median2025'],
                    # Income limits for different household sizes
                    'income_limits': {
                        '50_pct': {
                            '1p': row['lim50_25p1'], 
                            '2p': row['lim50_25p2'], 
                            '3p': row['lim50_25p3'], 
                            '4p': row['lim50_25p4']
                        }
                    },
                    # ENHANCED: Capture ALL rent limit percentages
                    'rent_limits': {
                        '50_pct': {
                            'studio': row['Studio 50%'], 
                            '1br': row['1BR 50%'],
                            '2br': row['2BR 50%'], 
                            '3br': row['3BR 50%'], 
                            '4br': row['4BR 50%']
                        },
                        '60_pct': {
                            'studio': row['Studio 60%'], 
                            '1br': row['1BR 60%'],
                            '2br': row['2BR 60%'], 
                            '3br': row['3BR 60%'], 
                            '4br': row['4BR 60%']
                        },
                        '70_pct': {
                            'studio': row['Studio 70%'], 
                            '1br': row['1BR 70%'],
                            '2br': row['2BR 70%'], 
                            '3br': row['3BR 70%'], 
                            '4br': row['4BR 70%']
                        },
                        '80_pct': {
                            'studio': row['Studio 80%'], 
                            '1br': row['1BR 80%'],
                            '2br': row['2BR 80%'], 
                            '3br': row['3BR 80%'], 
                            '4br': row['4BR 80%']
                        }
                    }
                }
            print(f"✅ Loaded AMI data for {len(self.ami_data)} Texas areas")
        except Exception as e:
            print(f"❌ Error loading AMI data: {e}")
            self.ami_data = None

    def load_tdhca_data(self, file_path: str):
        """Load TDHCA project data"""
        try:
            print(f"Loading TDHCA project data from: {file_path}")
            df = pd.read_excel(file_path)
            
            # Clean data
            df['Population Served'] = df['Population Served'].fillna('General').str.strip()
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
            df['Latitude11'] = pd.to_numeric(df['Latitude11'], errors='coerce')
            df['Longitude11'] = pd.to_numeric(df['Longitude11'], errors='coerce')
            df['Total Units'] = pd.to_numeric(df['Total Units'], errors='coerce')
            
            # Fix census tract format
            if 'CT 2020' in df.columns:
                df['CT 2020'] = pd.to_numeric(df['CT 2020'], errors='coerce').fillna(0).astype(int).astype(str)
            
            self.tdhca_data = df
            print(f"✅ Loaded {len(self.tdhca_data)} TDHCA projects")
            
            # Get county info
            if 'County' in df.columns:
                county_counts = df['County'].value_counts()
                print(f"   Major counties: {', '.join(county_counts.head(5).index.tolist())}")
                
        except Exception as e:
            print(f"❌ Error loading TDHCA data: {e}")
            self.tdhca_data = None

    def load_hud_designation_data(self):
        """Load QCT/DDA data"""
        try:
            base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD DDA QCT")
            
            qct_file = base_path / "QUALIFIED_CENSUS_TRACTS_7341711606021821459.gpkg"
            if qct_file.exists():
                self.qct_data = gpd.read_file(qct_file)
                if self.qct_data.crs != 'EPSG:4326':
                    self.qct_data = self.qct_data.to_crs('EPSG:4326')
                print(f"✅ Loaded QCT data: {len(self.qct_data)} features")
            
            dda_file = base_path / "Difficult_Development_Areas_-4200740390724245794.gpkg"
            if dda_file.exists():
                self.dda_data = gpd.read_file(dda_file)
                if self.dda_data.crs != 'EPSG:4326':
                    self.dda_data = self.dda_data.to_crs('EPSG:4326')
                print(f"✅ Loaded DDA data: {len(self.dda_data)} features")
                
        except Exception as e:
            print(f"⚠️ Error loading HUD designation data: {e}")

    def geocode_with_positionstack(self, address: str) -> Optional[Dict]:
        """Geocode using PositionStack API"""
        if not self.positionstack_api_key:
            return None
            
        try:
            url = "http://api.positionstack.com/v1/forward"
            params = {
                'access_key': self.positionstack_api_key,
                'query': address,
                'limit': 1,
                'country': 'US',
                'region': 'Texas'
            }
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                result = data['data'][0]
                return {
                    'latitude': result['latitude'],
                    'longitude': result['longitude'],
                    'confidence': result.get('confidence', 0)
                }
        except:
            pass
        
        return None

    def geocode_with_census(self, address: str) -> Optional[Dict]:
        """Fallback geocoding with Census API"""
        try:
            url = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
            params = {
                'address': address,
                'benchmark': 'Public_AR_Current',
                'vintage': 'Current_Current',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if data.get('result', {}).get('addressMatches'):
                match = data['result']['addressMatches'][0]
                coords = match['coordinates']
                
                census_tract = None
                if 'geographies' in match:
                    tracts = match['geographies'].get('Census Tracts', [])
                    if tracts:
                        census_tract = tracts[0].get('GEOID')
                
                return {
                    'latitude': coords['y'],
                    'longitude': coords['x'],
                    'census_tract': census_tract,
                    'confidence': 1.0
                }
        except:
            pass
            
        return None

    def get_census_tract_from_coords(self, lat: float, lon: float) -> Optional[str]:
        """Get census tract from coordinates"""
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
            data = response.json()
            
            if data.get('result', {}).get('geographies'):
                tracts = data['result']['geographies'].get('Census Tracts', [])
                if tracts:
                    return tracts[0].get('GEOID')
        except:
            pass
            
        return None

    def get_demographics(self, census_tract: str) -> Dict:
        """Get demographics from Census API - ENHANCED to include total population"""
        if not census_tract or len(census_tract) < 11:
            return {}
            
        try:
            state_code = census_tract[:2]
            county_code = census_tract[2:5]
            tract_code = census_tract[5:]
            
            base_url = "https://api.census.gov/data/2022/acs/acs5"
            variables = [
                "B17001_002E",  # Poverty - below poverty
                "B17001_001E",  # Poverty - total
                "B19013_001E",  # Median household income
                "B01003_001E",  # Total population
            ]
            
            params = {
                'get': ','.join(['NAME'] + variables),
                'for': f'tract:{tract_code}',
                'in': f'state:{state_code} county:{county_code}',
                'key': self.census_api_key
            }
            
            response = requests.get(base_url, params=params, timeout=15)
            data = response.json()
            
            if len(data) > 1:
                row = data[1]
                
                poverty_total = int(row[2]) if row[2] else 0
                poverty_below = int(row[1]) if row[1] else 0
                
                return {
                    'total_population': int(row[4]) if row[4] else 0,
                    'median_income': int(row[3]) if row[3] else 0,
                    'poverty_rate': round((poverty_below / poverty_total * 100), 1) if poverty_total > 0 else 0,
                    'low_poverty': (poverty_below / poverty_total * 100) < 20 if poverty_total > 0 else False
                }
        except:
            pass
            
        return {}

    def get_county_population(self, county_name: str) -> int:
        """Get county population for distance rules"""
        # Major Texas counties with >1M population
        large_counties = {
            'Harris': 4731145,    # Houston
            'Dallas': 2613539,    # Dallas
            'Tarrant': 2110640,   # Fort Worth
            'Bexar': 2009324,     # San Antonio
            'Travis': 1290188,    # Austin
            'Collin': 1064465     # Plano/McKinney
        }
        
        for county, pop in large_counties.items():
            if county.lower() in county_name.lower():
                return pop
                
        return 500000  # Default for smaller counties

    def check_one_mile_three_year_rule(self, point: Point, target_population: str, current_year: int = 2026) -> Dict:
        """
        ENHANCED: Return full project details, not just count
        Check TDHCA One Mile Three Year Rule (applies to BOTH 4% and 9%)
        """
        if self.tdhca_data is None:
            return {'compliant': True, 'competing_projects': [], 'message': 'No TDHCA data available'}
        
        target_coords = (point.y, point.x)
        competing_projects = []
        
        # Look for projects within 1 mile from prior 3 years
        for _, project in self.tdhca_data.iterrows():
            # Check year (must be within prior 3 years)
            year = project.get('Year')
            if pd.isna(year) or year < (current_year - 3):
                continue
                
            # Check population served
            if project.get('Population Served', 'General') != target_population:
                continue
                
            # Check distance
            lat = project.get('Latitude11')
            lon = project.get('Longitude11')
            if pd.isna(lat) or pd.isna(lon):
                continue
                
            try:
                distance = geodesic(target_coords, (lat, lon)).miles
                if distance <= 1.0:
                    # ENHANCED: Capture full project details
                    competing_projects.append({
                        'name': project.get('Development Name', 'Unknown'),
                        'year': int(year),
                        'year_display': f"'{str(int(year))[-2:]}",  # '24 format
                        'distance': round(distance, 2),
                        'units': int(project.get('Total Units', 0)),
                        'city': project.get('Project City', 'Unknown'),
                        'coordinates': (lat, lon)
                    })
            except:
                continue
        
        # Sort by distance
        competing_projects.sort(key=lambda x: x['distance'])
        
        compliant = len(competing_projects) == 0
        
        return {
            'compliant': compliant,
            'competing_projects': competing_projects,
            'message': f"{'PASS' if compliant else 'FAIL'}: {len(competing_projects)} competing {target_population} projects within 1 mile from prior 3 years"
        }

    def check_two_mile_same_year_rule(self, point: Point, county_name: str, current_year: int = 2026) -> Dict:
        """
        Check 9% ONLY: Two Mile Same Year Rule for counties >1M population
        """
        county_pop = self.get_county_population(county_name)
        
        if county_pop <= 1000000:
            return {'applicable': False, 'compliant': True, 'message': 'County population <1M, rule not applicable'}
        
        if self.tdhca_data is None:
            return {'applicable': True, 'compliant': True, 'message': 'No TDHCA data to check'}
        
        target_coords = (point.y, point.x)
        same_year_projects = []
        
        # Look for projects awarded in current year within 2 miles
        for _, project in self.tdhca_data.iterrows():
            if project.get('Year') != current_year:
                continue
                
            lat = project.get('Latitude11')
            lon = project.get('Longitude11')
            if pd.isna(lat) or pd.isna(lon):
                continue
                
            try:
                distance = geodesic(target_coords, (lat, lon)).miles
                if distance <= 2.0:
                    same_year_projects.append({
                        'name': project.get('Development Name', 'Unknown'),
                        'distance': round(distance, 2)
                    })
            except:
                continue
        
        compliant = len(same_year_projects) == 0
        
        return {
            'applicable': True,
            'compliant': compliant,
            'competing_projects': same_year_projects,
            'message': f"Large county (pop {county_pop:,}) - {'PASS' if compliant else 'FAIL'}: {len(same_year_projects)} projects within 2 miles same year"
        }

    def check_census_tract_concentration(self, census_tract: str) -> Dict:
        """Check if census tract has >20% HTC units (needs resolution for new construction)"""
        # This would require detailed household data - simplified version
        return {
            'concentration_check': 'Unable to verify - recommend checking with local planning',
            'resolution_needed': True
        }

    def get_ami_data_for_location(self, census_tract: str) -> Optional[Dict]:
        """Get AMI data for a census tract"""
        if not self.ami_data or not census_tract:
            return None
        
        # Try exact match first
        if len(census_tract) >= 5:
            county_fips = census_tract[:5] + "99999"
            if county_fips in self.ami_data:
                return self.ami_data[county_fips]
            
            # Try alternative format
            county_fips_alt = census_tract[:5] + "00000"
            if county_fips_alt in self.ami_data:
                return self.ami_data[county_fips_alt]
            
            # Search for any matching county
            county_prefix = census_tract[:5]
            for fips_key in self.ami_data.keys():
                if fips_key.startswith(county_prefix):
                    return self.ami_data[fips_key]
        
        return None

    def calculate_opportunity_index_distances(self, point: Point, urban: bool = True) -> Dict:
        """
        Calculate 9% Opportunity Index scoring based on distances to amenities
        Note: This is simplified - full implementation would need amenity databases
        """
        # Placeholder - would need actual amenity location data
        return {
            'scoring_potential': 'Requires amenity location data',
            'urban': urban,
            'distances_required': {
                'park': '0.5 miles' if urban else '4 miles',
                'grocery': '2 miles' if urban else '5 miles',
                'pharmacy': '2 miles' if urban else '5 miles',
                'childcare': '3 miles' if urban else '5 miles',
                'health': '4 miles' if urban else '5 miles',
                'library': '5 miles' if urban else '5 miles',
                'college': '6 miles' if urban else '15 miles'
            }
        }

    def score_4pct_deal(self, analysis: Dict) -> Dict:
        """
        Score 4% Tax-Exempt Bond Deal
        Focus on compliance with distance rules and local support requirements
        """
        score = {
            'category': 'UNKNOWN',
            'compliance_items': [],
            'action_items': [],
            'fatal_flaws': []
        }
        
        # Check One Mile Three Year Rule (critical for 4%)
        one_mile = analysis.get('one_mile_three_year', {})
        if one_mile.get('compliant'):
            score['compliance_items'].append('✅ Meets 1-mile/3-year rule')
        else:
            score['fatal_flaws'].append('❌ Fails 1-mile/3-year rule')
            competing = len(one_mile.get('competing_projects', []))
            score['fatal_flaws'].append(f'   {competing} competing projects within 1 mile')
        
        # Check QCT/DDA status for 30% basis boost
        if analysis.get('qct_status') or analysis.get('dda_status'):
            benefits = []
            if analysis.get('qct_status'):
                benefits.append('QCT')
            if analysis.get('dda_status'):
                benefits.append('DDA')
            score['compliance_items'].append(f'✅ Federal basis boost: {", ".join(benefits)} (30%)')
        
        # Check demographics
        demographics = analysis.get('demographics', {})
        if demographics.get('low_poverty'):
            score['compliance_items'].append(f'✅ Low poverty area ({demographics.get("poverty_rate", 0)}%)')
        
        # Required resolutions
        score['action_items'].append('📋 Need resolution of no objection from local government')
        score['action_items'].append('📋 Need public hearings by municipality/county')
        
        # Determine category
        if score['fatal_flaws']:
            score['category'] = 'FATAL FLAW'
        elif len(score['compliance_items']) >= 2:
            score['category'] = 'VIABLE'
        else:
            score['category'] = 'MARGINAL'
        
        return score

    def score_9pct_deal(self, analysis: Dict) -> Dict:
        """
        Score 9% Competitive HTC Deal
        More complex scoring with multiple factors
        """
        score = {
            'category': 'UNKNOWN',
            'points_estimate': 0,
            'strengths': [],
            'weaknesses': [],
            'fatal_flaws': []
        }
        
        # Check One Mile Three Year Rule
        one_mile = analysis.get('one_mile_three_year', {})
        if not one_mile.get('compliant'):
            score['fatal_flaws'].append('❌ Fails 1-mile/3-year rule')
        
        # Check Two Mile Same Year Rule (if applicable)
        two_mile = analysis.get('two_mile_same_year', {})
        if two_mile.get('applicable') and not two_mile.get('compliant'):
            score['fatal_flaws'].append('❌ Fails 2-mile same year rule')
        
        # Check underserved area potential
        tdhca_same_tract = analysis.get('tdhca_same_tract_score', 0)
        if tdhca_same_tract >= 4:
            score['strengths'].append(f'✅ Strong underserved area score: {tdhca_same_tract}/5 points')
            score['points_estimate'] += tdhca_same_tract
        elif tdhca_same_tract >= 3:
            score['strengths'].append(f'📊 Moderate underserved area score: {tdhca_same_tract}/5 points')
            score['points_estimate'] += tdhca_same_tract
        else:
            score['weaknesses'].append(f'❌ Weak underserved area score: {tdhca_same_tract}/5 points')
        
        # Check QCT/DDA
        if analysis.get('qct_status') or analysis.get('dda_status'):
            score['strengths'].append('✅ 30% basis boost (QCT/DDA)')
        
        # Determine category
        if score['fatal_flaws']:
            score['category'] = 'FATAL FLAW'
        elif score['points_estimate'] >= 4:
            score['category'] = 'COMPETITIVE'
        elif score['points_estimate'] >= 3:
            score['category'] = 'POSSIBLE'
        else:
            score['category'] = 'WEAK'
        
        return score

    def analyze_site(self, address: str, lat: float = None, lon: float = None) -> Dict:
        """ENHANCED: Comprehensive site analysis with rich data capture"""
        
        print(f"\n🏗️ Analyzing: {address}")
        
        # Get coordinates if not provided
        if lat is None or lon is None:
            # Try PositionStack first
            geo_result = self.geocode_with_positionstack(address)
            if not geo_result:
                # Fallback to Census
                geo_result = self.geocode_with_census(address)
            
            if not geo_result:
                return {'error': 'Geocoding failed', 'address': address}
            
            lat = geo_result['latitude']
            lon = geo_result['longitude']
        
        point = Point(lon, lat)
        
        # Get census tract
        census_tract = self.get_census_tract_from_coords(lat, lon)
        
        # Get demographics (includes total population)
        demographics = self.get_demographics(census_tract) if census_tract else {}
        
        # ENHANCED: Get AMI data
        ami_data = self.get_ami_data_for_location(census_tract)
        
        # Check QCT/DDA status
        qct_status = False
        dda_status = False
        
        try:
            if self.qct_data is not None:
                qct_intersects = self.qct_data[self.qct_data.contains(point)]
                qct_status = len(qct_intersects) > 0
        except:
            qct_status = False
        
        try:
            if self.dda_data is not None:
                dda_intersects = self.dda_data[self.dda_data.contains(point)]
                dda_status = len(dda_intersects) > 0
        except:
            dda_status = False
        
        # Determine county
        county_name = "Unknown"
        if census_tract and len(census_tract) >= 5:
            county_fips = census_tract[2:5]
            county_map = {
                '201': 'Harris',
                '113': 'Dallas',
                '439': 'Tarrant',
                '029': 'Bexar',
                '453': 'Travis'
            }
            county_name = county_map.get(county_fips, 'Other')
        
        # Run TDHCA compliance checks
        target_population = 'General'
        
        one_mile_check = self.check_one_mile_three_year_rule(point, target_population)
        two_mile_check = self.check_two_mile_same_year_rule(point, county_name)
        
        # Calculate TDHCA same tract score
        tdhca_score = self.calculate_tdhca_same_tract_score(census_tract, target_population)
        
        # Compile analysis
        analysis = {
            'address': address,
            'coordinates': {'latitude': lat, 'longitude': lon},
            'census_tract': census_tract,
            'county': county_name,
            'demographics': demographics,
            'ami_data': ami_data,  # ENHANCED: Full AMI data included
            'qct_status': qct_status,
            'dda_status': dda_status,
            'one_mile_three_year': one_mile_check,  # Now includes full project details
            'two_mile_same_year': two_mile_check,
            'tdhca_same_tract_score': tdhca_score
        }
        
        # Score for both deal types
        analysis['score_4pct'] = self.score_4pct_deal(analysis)
        analysis['score_9pct'] = self.score_9pct_deal(analysis)
        
        return analysis

    def calculate_tdhca_same_tract_score(self, census_tract: str, target_population: str = 'General') -> int:
        """Calculate underserved area score based on same census tract"""
        if self.tdhca_data is None or len(self.tdhca_data) == 0 or not census_tract:
            return 5  # Assume no projects if no data
            
        # Find projects in same tract
        same_tract = self.tdhca_data[
            (self.tdhca_data['CT 2020'].astype(str) == str(census_tract)) &
            (self.tdhca_data['Population Served'] == target_population)
        ]
        
        if len(same_tract) == 0:
            return 5  # No competing projects
            
        # Get most recent year
        recent_year = same_tract['Year'].max()
        if pd.isna(recent_year):
            return 5
            
        years_since = 2026 - recent_year
        
        if years_since >= 20:
            return 5
        elif years_since >= 15:
            return 4
        elif years_since >= 10:
            return 3
        else:
            return 0

    def process_costar_data(self, costar_file: str, address_column: str = 'Address') -> pd.DataFrame:
        """ENHANCED: Process CoStar data with rich data capture"""
        
        print(f"\n📊 Processing CoStar data from: {costar_file}")
        df = pd.read_excel(costar_file)
        print(f"   Loaded {len(df)} properties")
        
        # Initialize result columns - ENHANCED with new fields
        result_columns = [
            # Basic location data
            'Latitude', 'Longitude', 'Census_Tract', 'County',
            # QCT/DDA status
            'QCT_Status', 'DDA_Status',
            # Demographics
            'Poverty_Rate', 'Median_Income', 'Total_Population',
            # AMI Data
            'HUD_Area_Name', 'Metro_Status', 'Median_AMI', 
            '4P_50pct_Income',  # 4-person 50% AMI income limit
            # Rent Limits (selected key ones for display)
            'Rent_1BR_60pct', 'Rent_2BR_60pct', 'Rent_3BR_60pct',
            'Rent_1BR_80pct', 'Rent_2BR_80pct', 'Rent_3BR_80pct',
            # 4% Deal Scoring
            '4pct_Category', '4pct_One_Mile_Compliant', '4pct_Action_Items',
            # 9% Deal Scoring
            '9pct_Category', '9pct_Points_Est', '9pct_Fatal_Flaws',
            # Competition Data
            'One_Mile_Competitors', 'Nearest_Competitor_Name', 'Nearest_Competitor_Distance',
            'Nearest_Competitor_Year', 'Nearest_Competitor_Units',
            # Regulatory scoring
            'TDHCA_Same_Tract_Score'
        ]
        
        for col in result_columns:
            df[col] = None
        
        # Process each property
        for idx, row in df.iterrows():
            address = row[address_column]
            print(f"\n{idx + 1}/{len(df)}: {address}")
            
            try:
                # Run analysis
                analysis = self.analyze_site(address)
                
                if 'error' not in analysis:
                    # Basic data
                    df.at[idx, 'Latitude'] = analysis['coordinates']['latitude']
                    df.at[idx, 'Longitude'] = analysis['coordinates']['longitude']
                    df.at[idx, 'Census_Tract'] = analysis.get('census_tract', '')
                    df.at[idx, 'County'] = analysis.get('county', '')
                    
                    # QCT/DDA
                    df.at[idx, 'QCT_Status'] = analysis.get('qct_status', False)
                    df.at[idx, 'DDA_Status'] = analysis.get('dda_status', False)
                    
                    # Demographics (ENHANCED with total population)
                    demo = analysis.get('demographics', {})
                    df.at[idx, 'Poverty_Rate'] = demo.get('poverty_rate')
                    df.at[idx, 'Median_Income'] = demo.get('median_income')
                    df.at[idx, 'Total_Population'] = demo.get('total_population')
                    
                    # AMI Data (ENHANCED)
                    ami = analysis.get('ami_data', {})
                    if ami:
                        df.at[idx, 'HUD_Area_Name'] = ami.get('hud_area_name', '')
                        df.at[idx, 'Metro_Status'] = 'Metro' if ami.get('metro') else 'Non-Metro'
                        df.at[idx, 'Median_AMI'] = ami.get('median_ami')
                        df.at[idx, '4P_50pct_Income'] = ami.get('income_limits', {}).get('50_pct', {}).get('4p')
                        
                        # Rent limits
                        rent_60 = ami.get('rent_limits', {}).get('60_pct', {})
                        rent_80 = ami.get('rent_limits', {}).get('80_pct', {})
                        df.at[idx, 'Rent_1BR_60pct'] = rent_60.get('1br')
                        df.at[idx, 'Rent_2BR_60pct'] = rent_60.get('2br')
                        df.at[idx, 'Rent_3BR_60pct'] = rent_60.get('3br')
                        df.at[idx, 'Rent_1BR_80pct'] = rent_80.get('1br')
                        df.at[idx, 'Rent_2BR_80pct'] = rent_80.get('2br')
                        df.at[idx, 'Rent_3BR_80pct'] = rent_80.get('3br')
                    
                    # 4% scoring
                    score_4p = analysis.get('score_4pct', {})
                    df.at[idx, '4pct_Category'] = score_4p.get('category', 'UNKNOWN')
                    df.at[idx, '4pct_One_Mile_Compliant'] = analysis.get('one_mile_three_year', {}).get('compliant', False)
                    df.at[idx, '4pct_Action_Items'] = '; '.join(score_4p.get('action_items', []))
                    
                    # 9% scoring
                    score_9p = analysis.get('score_9pct', {})
                    df.at[idx, '9pct_Category'] = score_9p.get('category', 'UNKNOWN')
                    df.at[idx, '9pct_Points_Est'] = score_9p.get('points_estimate', 0)
                    df.at[idx, '9pct_Fatal_Flaws'] = '; '.join(score_9p.get('fatal_flaws', []))
                    
                    # Competition data (ENHANCED with details)
                    one_mile = analysis.get('one_mile_three_year', {})
                    competitors = one_mile.get('competing_projects', [])
                    df.at[idx, 'One_Mile_Competitors'] = len(competitors)
                    
                    if competitors:
                        # Get nearest competitor details
                        nearest = competitors[0]  # Already sorted by distance
                        df.at[idx, 'Nearest_Competitor_Name'] = nearest.get('name', 'Unknown')
                        df.at[idx, 'Nearest_Competitor_Distance'] = nearest.get('distance', 0)
                        df.at[idx, 'Nearest_Competitor_Year'] = nearest.get('year', 0)
                        df.at[idx, 'Nearest_Competitor_Units'] = nearest.get('units', 0)
                    
                    df.at[idx, 'TDHCA_Same_Tract_Score'] = analysis.get('tdhca_same_tract_score', 0)
                    
                else:
                    df.at[idx, '4pct_Category'] = 'ERROR'
                    df.at[idx, '9pct_Category'] = 'ERROR'
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                df.at[idx, '4pct_Category'] = 'ERROR'
                df.at[idx, '9pct_Category'] = 'ERROR'
            
            # Pause to avoid rate limits
            time.sleep(0.5)
        
        return df

    def save_results(self, df: pd.DataFrame, base_filename: str):
        """ENHANCED: Save results with rich data to Excel"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.work_dir / f"{base_filename}_TDHCA_Analysis_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # All data
            df.to_excel(writer, sheet_name='All_Properties', index=False)
            
            # 4% deals - sorted by category
            df_4p = df.copy()
            category_order = {'VIABLE': 1, 'MARGINAL': 2, 'FATAL FLAW': 3, 'ERROR': 4}
            df_4p['sort_order'] = df_4p['4pct_Category'].map(category_order).fillna(5)
            df_4p = df_4p.sort_values(['sort_order', '4pct_One_Mile_Compliant', 'QCT_Status'], 
                                     ascending=[True, False, False])
            df_4p.drop('sort_order', axis=1).to_excel(writer, sheet_name='4pct_Ranked', index=False)
            
            # 9% deals - sorted by category and points
            df_9p = df.copy()
            category_order = {'COMPETITIVE': 1, 'POSSIBLE': 2, 'WEAK': 3, 'FATAL FLAW': 4, 'ERROR': 5}
            df_9p['sort_order'] = df_9p['9pct_Category'].map(category_order).fillna(6)
            df_9p = df_9p.sort_values(['sort_order', '9pct_Points_Est', 'TDHCA_Same_Tract_Score'], 
                                     ascending=[True, False, False])
            df_9p.drop('sort_order', axis=1).to_excel(writer, sheet_name='9pct_Ranked', index=False)
            
            # Summary stats
            summary_data = {
                'Metric': [
                    'Total Properties',
                    '4% Viable', '4% Marginal', '4% Fatal Flaw',
                    '9% Competitive', '9% Possible', '9% Weak', '9% Fatal Flaw',
                    'Properties in QCT', 'Properties in DDA', 'Properties with Either QCT/DDA',
                    'Low Poverty (<20%)', 'One Mile Rule Compliant',
                    'Properties with AMI Data', 'Metro Area Properties'
                ],
                'Count': [
                    len(df),
                    len(df[df['4pct_Category'] == 'VIABLE']),
                    len(df[df['4pct_Category'] == 'MARGINAL']),
                    len(df[df['4pct_Category'] == 'FATAL FLAW']),
                    len(df[df['9pct_Category'] == 'COMPETITIVE']),
                    len(df[df['9pct_Category'] == 'POSSIBLE']),
                    len(df[df['9pct_Category'] == 'WEAK']),
                    len(df[df['9pct_Category'] == 'FATAL FLAW']),
                    len(df[df['QCT_Status'] == True]),
                    len(df[df['DDA_Status'] == True]),
                    len(df[(df['QCT_Status'] == True) | (df['DDA_Status'] == True)]),
                    len(df[df['Poverty_Rate'] < 20]),
                    len(df[df['4pct_One_Mile_Compliant'] == True]),
                    len(df[df['HUD_Area_Name'].notna()]),
                    len(df[df['Metro_Status'] == 'Metro'])
                ]
            }
            
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"\n✅ Results saved to: {output_file}")
        return output_file


def main():
    """Main execution function"""
    
    # Configuration
    CENSUS_API_KEY = "06ece0121263282cd9ffd753215b007b8f9a3dfc"
    POSITIONSTACK_API_KEY = "41b80ed51d92978904592126d2bb8f7e"
    
    # File paths
    base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets")
    
    HUD_AMI_FILE = base_path / "HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx"
    TDHCA_PROJECT_FILE = base_path / "State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
    
    # CoStar file to analyze - Full path
    COSTAR_FILE = base_path / "Costar/TX/CS_Land_TX_1_10ac_05312025_RANKED_4p_9p.xlsx"
    
    # Initialize analyzer
    print("=" * 70)
    print("ENHANCED TDHCA ACCURATE ANALYSIS - With Rich Data Capture")
    print("=" * 70)
    
    analyzer = TDHCAAccurateAnalyzer(
        census_api_key=CENSUS_API_KEY,
        positionstack_api_key=POSITIONSTACK_API_KEY,
        hud_ami_file_path=str(HUD_AMI_FILE),
        tdhca_project_file_path=str(TDHCA_PROJECT_FILE)
        # work_dir will default to code directory
    )
    
    # Load CoStar data
    if not COSTAR_FILE.exists():
        print(f"\n❌ ERROR: CoStar file not found: {COSTAR_FILE}")
        print(f"Please ensure the file exists at the specified path.")
        return
    
    print(f"\n📊 Loading CoStar data from: {COSTAR_FILE}")
    full_df = pd.read_excel(str(COSTAR_FILE))
    
    # Find address column
    address_cols = [col for col in full_df.columns if 'address' in col.lower()]
    if address_cols:
        address_column = address_cols[0]
        print(f"✅ Using address column: {address_column}")
    else:
        print("❌ No address column found!")
        print(f"Available columns: {list(full_df.columns)}")
        return
    
    # Full run - analyze all properties
    print(f"\n🚀 FULL RUN: Processing all {len(full_df)} properties...")
    print("This may take 15-20 minutes depending on geocoding speed...")
    print("Progress updates will appear every 10 properties.\n")
    
    # Start timer
    import time
    start_time = time.time()
    
    # Process full dataset
    results_df = analyzer.process_costar_data(str(COSTAR_FILE), address_column=address_column)
    
    # Calculate total time
    end_time = time.time()
    total_minutes = (end_time - start_time) / 60
    print(f"\n⏱️ Total processing time: {total_minutes:.1f} minutes")
    
    # Save results
    output_file = analyzer.save_results(results_df, 'Enhanced_CoStar_TX_Land')
    
    # Print summary of new data captured
    print("\n📊 ENHANCED DATA CAPTURE SUMMARY:")
    print(f"✅ Processed {len(results_df)} properties")
    
    # Check what enhanced data we captured
    ami_captured = results_df['HUD_Area_Name'].notna().sum()
    print(f"✅ AMI data captured: {ami_captured} properties")
    
    competitor_details = results_df['Nearest_Competitor_Name'].notna().sum()
    print(f"✅ Competitor details captured: {competitor_details} properties")
    
    population_data = results_df['Total_Population'].notna().sum()
    print(f"✅ Population data captured: {population_data} properties")
    
    # Show sample of enhanced data
    if ami_captured > 0:
        sample = results_df[results_df['HUD_Area_Name'].notna()].iloc[0]
        print(f"\n📋 Sample Enhanced Data for: {sample['Address']}")
        print(f"   HUD Area: {sample['HUD_Area_Name']}")
        print(f"   Metro Status: {sample['Metro_Status']}")
        print(f"   Median AMI: ${sample['Median_AMI']:,}")
        print(f"   4-Person 50% Income: ${sample['4P_50pct_Income']:,}")
        print(f"   1BR Rent @ 60%: ${sample['Rent_1BR_60pct']:,}")
        print(f"   2BR Rent @ 60%: ${sample['Rent_2BR_60pct']:,}")
    
    print(f"\n✅ Enhanced results saved to: {output_file}")
    print("\n🎯 Next step: Update HTML reporter to use this rich data!")


if __name__ == "__main__":
    main()