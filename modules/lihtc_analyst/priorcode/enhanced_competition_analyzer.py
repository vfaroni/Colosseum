#!/usr/bin/env python3
"""
Enhanced Texas LIHTC Analyzer with Market Saturation & Competition Analysis
Complete integration with existing analyzer - adds TDHCA-compliant distance analysis
"""

import os
import sys
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import requests
from pathlib import Path
import tempfile
from typing import Dict, List, Tuple, Optional, Union
import time
import re
import math
from datetime import datetime, timedelta
import urllib.parse
from geopy.distance import geodesic
import numpy as np

class EnhancedTexasAnalyzer:
    def __init__(self, 
                 census_api_key: str,
                 hud_ami_file_path: str = None,
                 work_dir: str = "./enhanced_texas_analysis"):
        """
        Initialize Enhanced Texas LIHTC Analyzer with Competition Analysis
        """
        self.census_api_key = census_api_key
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)
        
        # Cache directory setup
        try:
            self.cache_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Cache")
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            (self.cache_dir / "census_api_cache").mkdir(exist_ok=True)
            (self.cache_dir / "ami_lookup_cache").mkdir(exist_ok=True)
            (self.cache_dir / "geocoding_cache").mkdir(exist_ok=True)
            (self.cache_dir / "competition_cache").mkdir(exist_ok=True)
        except:
            self.cache_dir = self.work_dir / "cache"
            self.cache_dir.mkdir(exist_ok=True)
            (self.cache_dir / "census_api_cache").mkdir(exist_ok=True)
            (self.cache_dir / "ami_lookup_cache").mkdir(exist_ok=True)
            (self.cache_dir / "geocoding_cache").mkdir(exist_ok=True)
            (self.cache_dir / "competition_cache").mkdir(exist_ok=True)
        
        # Data containers
        self.qct_data = None
        self.dda_data = None
        self.ami_data = None
        self.lihtc_data = None
        self.census_cache = {}
        self.geocoding_cache = {}
        self.competition_cache = {}
        
        # Load all data
        if hud_ami_file_path and Path(hud_ami_file_path).exists():
            self.load_ami_data(hud_ami_file_path)
        else:
            self.search_and_load_ami_data()
        
        self.load_hud_designation_data()
        
        print(f"Enhanced Texas LIHTC Analyzer with Competition Analysis initialized.")
        print(f"Working directory: {self.work_dir}")
        print(f"Cache directory: {self.cache_dir}")
        print(f"Census API configured: {'✅' if census_api_key else '❌'}")
        print(f"HUD AMI data loaded: {'✅' if self.ami_data is not None else '❌'}")
        print(f"LIHTC projects loaded: {'✅' if self.lihtc_data is not None else '❌'}")

    def search_and_load_ami_data(self):
        """Search for AMI file in multiple locations"""
        search_paths = [
            Path("."),
            Path(".."),
            Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code"),
            Path("/Users/williamrice/Downloads"),
            Path("/Users/williamrice/Desktop")
        ]
        
        patterns = ["*AMI*Rent*Data*.xlsx", "HUD2025*.xlsx", "*HUD*AMI*.xlsx", "*AMI*.xlsx"]
        
        for search_path in search_paths:
            if search_path.exists():
                for pattern in patterns:
                    ami_files = list(search_path.glob(pattern))
                    if ami_files:
                        try:
                            self.load_ami_data(str(ami_files[0]))
                            return
                        except Exception as e:
                            print(f"⚠️ Could not load AMI file: {e}")
                            continue
        
        print("⚠️ No AMI file found")
        self.ami_data = None

    def load_ami_data(self, file_path: str):
        """Load and index HUD AMI data for fast lookups"""
        try:
            df = pd.read_excel(file_path, sheet_name="MTSP2025-Static")
            texas_df = df[df['stusps'] == 'TX'].copy()
            
            self.ami_data = {}
            for _, row in texas_df.iterrows():
                fips = str(row['fips'])
                self.ami_data[fips] = {
                    'hud_area_name': row['hud_area_name'],
                    'county_name': row['County_Name'],
                    'metro': row['metro'] == 1,
                    'median_ami': row['median2025'],
                    'income_limits': {
                        '50_pct': {'1p': row['lim50_25p1'], '2p': row['lim50_25p2'], '3p': row['lim50_25p3'], '4p': row['lim50_25p4']}
                    },
                    'rent_limits': {
                        '50_pct': {'studio': row['Studio 50%'], '1br': row['1BR 50%'], '2br': row['2BR 50%'], '3br': row['3BR 50%'], '4br': row['4BR 50%']},
                        '60_pct': {'studio': row['Studio 60%'], '1br': row['1BR 60%'], '2br': row['2BR 60%'], '3br': row['3BR 60%'], '4br': row['4BR 60%']},
                        '70_pct': {'studio': row['Studio 70%'], '1br': row['1BR 70%'], '2br': row['2BR 70%'], '3br': row['3BR 70%'], '4br': row['4BR 70%']},
                        '80_pct': {'studio': row['Studio 80%'], '1br': row['1BR 80%'], '2br': row['2BR 80%'], '3br': row['3BR 80%'], '4br': row['4BR 80%']}
                    }
                }
            print(f"✅ Loaded AMI data for {len(self.ami_data)} Texas areas")
        except Exception as e:
            print(f"❌ Error loading AMI data: {e}")
            self.ami_data = None

    def load_hud_designation_data(self):
        """Load QCT/DDA and LIHTC project data"""
        try:
            base_hud_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD DDA QCT")
            lihtc_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD LIHTC List")
            
            # Load QCT data
            qct_file = base_hud_path / "QUALIFIED_CENSUS_TRACTS_7341711606021821459.gpkg"
            if qct_file.exists():
                self.qct_data = gpd.read_file(qct_file)
                if self.qct_data.crs != 'EPSG:4326':
                    self.qct_data = self.qct_data.to_crs('EPSG:4326')
                print(f"✅ Loaded QCT data: {len(self.qct_data)} features")
            
            # Load DDA data
            dda_file = base_hud_path / "Difficult_Development_Areas_-4200740390724245794.gpkg"
            if dda_file.exists():
                self.dda_data = gpd.read_file(dda_file)
                if self.dda_data.crs != 'EPSG:4326':
                    self.dda_data = self.dda_data.to_crs('EPSG:4326')
                print(f"✅ Loaded DDA data: {len(self.dda_data)} features")
            
            # Load LIHTC projects data
            lihtc_file = lihtc_path / "LIHTC_-4037276073095513651.gpkg"
            if lihtc_file.exists():
                self.lihtc_data = gpd.read_file(lihtc_file)
                if self.lihtc_data.crs != 'EPSG:4326':
                    self.lihtc_data = self.lihtc_data.to_crs('EPSG:4326')
                
                # Filter for Texas and prepare for competition analysis
                state_columns = ['STATE', 'state', 'State']
                for col in state_columns:
                    if col in self.lihtc_data.columns:
                        self.lihtc_data = self.lihtc_data[self.lihtc_data[col] == 'TX'].copy()
                        break
                
                print(f"✅ Loaded Texas LIHTC data: {len(self.lihtc_data)} projects")
                self.prepare_lihtc_data_for_analysis()
            
        except Exception as e:
            print(f"⚠️ Error loading HUD designation data: {e}")

    def prepare_lihtc_data_for_analysis(self):
        """Prepare LIHTC data for competition analysis"""
        if self.lihtc_data is None:
            return
        
        # Clean and standardize key fields for competition analysis
        required_fields = ['TOTAL_UNITS', 'YEAR_PLACED_IN_SERVICE', 'PROJECT_NAME', 'CITY']
        
        for field in required_fields:
            if field not in self.lihtc_data.columns:
                # Try alternative field names
                alt_names = {
                    'TOTAL_UNITS': ['total_units', 'Total_Units', 'UNITS', 'units'],
                    'YEAR_PLACED_IN_SERVICE': ['year_placed', 'placed_in_service', 'YEAR', 'year'],
                    'PROJECT_NAME': ['project_name', 'name', 'NAME', 'Project_Name'],
                    'CITY': ['city', 'City', 'CITY_NAME', 'city_name']
                }
                
                for alt_name in alt_names.get(field, []):
                    if alt_name in self.lihtc_data.columns:
                        self.lihtc_data[field] = self.lihtc_data[alt_name]
                        break
                else:
                    # Create default values if field not found
                    if field == 'TOTAL_UNITS':
                        self.lihtc_data[field] = 50
                    elif field == 'YEAR_PLACED_IN_SERVICE':
                        self.lihtc_data[field] = 2020
                    else:
                        self.lihtc_data[field] = 'Unknown'
        
        print(f"✅ Prepared LIHTC data for competition analysis")

    def determine_market_radius(self, point: Point, demographics: Dict = None) -> float:
        """Determine appropriate market radius based on TDHCA guidelines"""
        
        # Major Texas metro areas (approximate bounding boxes)
        major_metros = {
            'Houston': {'lat_range': (29.5, 30.1), 'lon_range': (-95.8, -95.0)},
            'Dallas': {'lat_range': (32.6, 33.0), 'lon_range': (-97.0, -96.5)},
            'Austin': {'lat_range': (30.1, 30.5), 'lon_range': (-98.0, -97.5)},
            'San Antonio': {'lat_range': (29.2, 29.7), 'lon_range': (-98.8, -98.2)},
            'Fort Worth': {'lat_range': (32.6, 32.9), 'lon_range': (-97.5, -97.1)}
        }
        
        lat, lon = point.y, point.x
        
        # Check if in major metro area
        for metro, bounds in major_metros.items():
            if (bounds['lat_range'][0] <= lat <= bounds['lat_range'][1] and 
                bounds['lon_range'][0] <= lon <= bounds['lon_range'][1]):
                
                if metro in ['Houston', 'Dallas', 'Austin']:
                    return 2.0  # Dense urban
                else:
                    return 3.0  # Other metros
        
        # Use demographics to determine suburban vs rural
        if demographics:
            population = demographics.get('total_population', 0)
            if population > 5000:
                return 4.0  # Suburban
            else:
                return 8.0  # Rural
        
        return 4.0  # Default suburban

    def get_nearby_lihtc_projects(self, target_point: Point, radius_miles: float) -> List[Dict]:
        """Find LIHTC projects within specified radius"""
        if self.lihtc_data is None:
            return []
        
        nearby_projects = []
        target_coords = (target_point.y, target_point.x)
        
        for idx, project in self.lihtc_data.iterrows():
            try:
                # Get project coordinates
                if hasattr(project.geometry, 'coords'):
                    project_coords = list(project.geometry.coords)[0]
                elif hasattr(project.geometry, 'x') and hasattr(project.geometry, 'y'):
                    project_coords = (project.geometry.y, project.geometry.x)
                else:
                    continue
                
                # Calculate distance
                distance_miles = geodesic(target_coords, project_coords).miles
                
                if distance_miles <= radius_miles:
                    project_info = {
                        'distance': round(distance_miles, 2),
                        'project_name': project.get('PROJECT_NAME', 'Unknown'),
                        'total_units': int(project.get('TOTAL_UNITS', 0)),
                        'year_placed': int(project.get('YEAR_PLACED_IN_SERVICE', 0)),
                        'city': project.get('CITY', 'Unknown'),
                        'coordinates': project_coords
                    }
                    nearby_projects.append(project_info)
                    
            except Exception as e:
                continue
        
        # Sort by distance
        nearby_projects.sort(key=lambda x: x['distance'])
        return nearby_projects

    def calculate_market_saturation_score(self, nearby_projects: List[Dict], demographics: Dict) -> Dict:
        """Calculate market saturation based on LIHTC industry standards"""
        
        if not nearby_projects or not demographics:
            return {
                'saturation_level': 'UNKNOWN',
                'saturation_score': 0,
                'total_competing_units': 0,
                'qualified_households_estimate': 0,
                'units_per_100_households': 0
            }
        
        # Calculate total competing units
        total_units = sum(project['total_units'] for project in nearby_projects)
        
        # Estimate income-qualified households
        total_population = demographics.get('total_population', 0)
        households_estimate = total_population / 2.5
        qualified_households = households_estimate * 0.30
        
        # Calculate saturation ratio
        if qualified_households > 0:
            units_per_100 = (total_units / qualified_households) * 100
        else:
            units_per_100 = 0
        
        # Determine saturation level
        if units_per_100 < 15:
            level = 'LOW'
            score = 3
        elif units_per_100 < 30:
            level = 'MEDIUM'
            score = 2
        elif units_per_100 < 50:
            level = 'HIGH'
            score = 1
        else:
            level = 'OVERSATURATED'
            score = 0
        
        return {
            'saturation_level': level,
            'saturation_score': score,
            'total_competing_units': total_units,
            'qualified_households_estimate': int(qualified_households),
            'units_per_100_households': round(units_per_100, 1)
        }

    def analyze_project_timeline(self, nearby_projects: List[Dict]) -> Dict:
        """Analyze development timeline and pipeline"""
        if not nearby_projects:
            return {'recent_development': False, 'pipeline_risk': 'LOW'}
        
        current_year = datetime.now().year
        recent_projects = [p for p in nearby_projects if p['year_placed'] >= current_year - 3]
        
        pipeline_risk = 'LOW'
        if len(recent_projects) >= 3:
            pipeline_risk = 'HIGH'
        elif len(recent_projects) >= 2:
            pipeline_risk = 'MEDIUM'
        
        return {
            'recent_development': len(recent_projects) > 0,
            'recent_projects_count': len(recent_projects),
            'pipeline_risk': pipeline_risk,
            'newest_project_year': max([p['year_placed'] for p in nearby_projects]) if nearby_projects else 0
        }

    def analyze_lihtc_competition(self, point: Point, demographics: Dict) -> Dict:
        """Comprehensive LIHTC competition analysis"""
        
        # Determine appropriate search radius
        radius = self.determine_market_radius(point, demographics)
        
        # Get nearby projects
        nearby_projects = self.get_nearby_lihtc_projects(point, radius)
        
        # Calculate market saturation
        saturation = self.calculate_market_saturation_score(nearby_projects, demographics)
        
        # Analyze development timeline
        timeline = self.analyze_project_timeline(nearby_projects)
        
        # Calculate competition score (0-3 points for TDHCA scoring)
        competition_score = 0
        
        if saturation['saturation_level'] == 'LOW':
            competition_score = 3
        elif saturation['saturation_level'] == 'MEDIUM':
            competition_score = 2
        elif saturation['saturation_level'] == 'HIGH':
            competition_score = 1
        
        # Adjust for recent development pipeline risk
        if timeline['pipeline_risk'] == 'HIGH':
            competition_score = max(0, competition_score - 1)
        
        return {
            'search_radius_miles': radius,
            'projects_within_radius': len(nearby_projects),
            'nearest_project': nearby_projects[0] if nearby_projects else None,
            'saturation_analysis': saturation,
            'timeline_analysis': timeline,
            'competition_score': competition_score,
            'market_recommendation': self.get_market_recommendation(competition_score, saturation['saturation_level'])
        }

    def get_market_recommendation(self, competition_score: int, saturation_level: str) -> str:
        """Generate market recommendation based on competition analysis"""
        
        if competition_score >= 3 and saturation_level == 'LOW':
            return "EXCELLENT - Low competition, strong market opportunity"
        elif competition_score >= 2:
            return "GOOD - Moderate competition, viable market"
        elif competition_score == 1:
            return "CAUTION - High competition, careful site selection needed"
        else:
            return "AVOID - Oversaturated market, high development risk"

    # Include key methods from original analyzer
    def enhanced_geocode_address(self, address: str) -> Optional[Dict]:
        """Enhanced geocoding with comprehensive location analysis"""
        
        # Simplified geocoding for this example - you'd include full implementation
        try:
            url = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
            params = {
                'address': address,
                'benchmark': 'Public_AR_Current',
                'vintage': 'Current_Current',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('result', {}).get('addressMatches'):
                match = data['result']['addressMatches'][0]
                coords = match['coordinates']
                matched_address = match.get('matchedAddress', address)
                
                census_tract = None
                if 'geographies' in match:
                    tracts = match['geographies'].get('Census Tracts', [])
                    if tracts:
                        census_tract = tracts[0].get('GEOID')
                
                return {
                    "address": address,
                    "matched_address": matched_address,
                    "longitude": coords['x'],
                    "latitude": coords['y'],
                    "census_tract": census_tract,
                    "geocoding_success": True
                }
            
        except Exception as e:
            print(f"❌ Geocoding failed: {e}")
        
        return None

    def get_demographics_from_census_api(self, census_tract: str) -> Dict:
        """Get comprehensive demographics from Census API"""
        
        if not census_tract or len(census_tract) < 11:
            return {"error": "Invalid census tract format"}
        
        try:
            state_code = census_tract[:2]
            county_code = census_tract[2:5]
            tract_code = census_tract[5:]
            
            base_url = "https://api.census.gov/data/2022/acs/acs5"
            
            variables = [
                "B17001_002E",  # Poverty - Income below poverty level
                "B17001_001E",  # Poverty - Total for whom poverty determined  
                "B19013_001E",  # Median household income
                "B25044_001E",  # Total occupied housing units
                "B01003_001E",  # Total population
            ]
            
            params = {
                'get': ','.join(['NAME'] + variables),
                'for': f'tract:{tract_code}',
                'in': f'state:{state_code} county:{county_code}',
                'key': self.census_api_key
            }
            
            response = requests.get(base_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) > 1:
                row = data[1]
                
                def safe_int(value, default=0):
                    try:
                        return int(float(str(value))) if value not in [None, '', 'null', 'None', '-'] else default
                    except:
                        return default
                
                total_pop = safe_int(row[5])
                poverty_total = safe_int(row[2])
                poverty_below = safe_int(row[1])
                median_income = safe_int(row[3])
                
                poverty_rate = (poverty_below / poverty_total * 100) if poverty_total > 0 else 0
                
                return {
                    "census_tract": census_tract,
                    "total_population": total_pop,
                    "median_household_income": median_income,
                    "poverty_rate": round(poverty_rate, 2),
                    "low_poverty_tract": poverty_rate <= 20.0,
                    "data_date": "2022 ACS 5-Year",
                    "data_quality": "GOOD" if median_income > 0 and poverty_total > 0 else "POOR"
                }
            
        except Exception as e:
            print(f"❌ Census API error for tract {census_tract}: {e}")
            return {"error": str(e)}
        
        return {"error": "No data returned from Census API"}

    def get_ami_data_for_location(self, census_tract: str) -> Optional[Dict]:
        """Get AMI data for a census tract"""
        if not self.ami_data or not census_tract:
            return None
        
        if len(census_tract) >= 5:
            county_fips = census_tract[:5] + "99999"
            if county_fips in self.ami_data:
                return self.ami_data[county_fips]
            
            # Try alternative matching
            county_prefix = census_tract[:5]
            for fips_key in self.ami_data.keys():
                if fips_key.startswith(county_prefix):
                    return self.ami_data[fips_key]
        
        return None

    def check_qct_dda_status(self, point: Point) -> Dict:
        """Check QCT and DDA status for federal benefits"""
        status = {
            "qct_status": False,
            "dda_status": False,
            "federal_basis_boost": False,
            "qct_details": {},
            "dda_details": {}
        }
        
        try:
            # Check QCT status
            if self.qct_data is not None:
                qct_intersects = self.qct_data[self.qct_data.contains(point)]
                if not qct_intersects.empty:
                    status["qct_status"] = True
                    status["federal_basis_boost"] = True
            
            # Check DDA status
            if self.dda_data is not None:
                dda_intersects = self.dda_data[self.dda_data.contains(point)]
                if not dda_intersects.empty:
                    status["dda_status"] = True
                    status["federal_basis_boost"] = True
        
        except Exception as e:
            print(f"⚠️ Error checking QCT/DDA status: {e}")
        
        return status

    def calculate_opportunity_index_score(self, demographics: Dict, ami_data: Dict) -> Dict:
        """Calculate Texas opportunity index score (0-2 points)"""
        
        if not demographics or "error" in demographics:
            return {"score": 0, "reason": "No demographic data available"}
        
        if demographics.get("data_quality") == "POOR":
            return {"score": 0, "reason": "Poor data quality"}
        
        poverty_rate = demographics.get("poverty_rate", 100)
        median_income = demographics.get("median_household_income", 0)
        
        if poverty_rate < 20.0:
            if median_income >= 85000:
                return {"score": 2, "reason": f"Low poverty ({poverty_rate:.1f}%) + high income (${median_income:,})"}
            elif median_income >= 60000:
                return {"score": 1, "reason": f"Low poverty ({poverty_rate:.1f}%) + moderate income (${median_income:,})"}
            else:
                return {"score": 1, "reason": f"Low poverty area ({poverty_rate:.1f}%)"}
        else:
            return {"score": 0, "reason": f"High poverty area: {poverty_rate:.1f}%"}

    def enhanced_analyze_address(self, address: str) -> Dict:
        """Enhanced address analysis with competition analysis"""
        
        print(f"\n🔍 Enhanced Analysis with Competition: {address}")
        
        # Geocoding
        geocode_result = self.enhanced_geocode_address(address)
        if not geocode_result:
            return {"error": "Geocoding failed", "address": address}
        
        # Get additional data
        census_tract = geocode_result.get("census_tract")
        demographics = self.get_demographics_from_census_api(census_tract) if census_tract else {}
        ami_data = self.get_ami_data_for_location(census_tract) if census_tract else None
        
        point = Point(geocode_result["longitude"], geocode_result["latitude"])
        qct_dda_status = self.check_qct_dda_status(point)
        opportunity_index = self.calculate_opportunity_index_score(demographics, ami_data)
        
        # NEW: Competition analysis
        competition_analysis = self.analyze_lihtc_competition(point, demographics)
        
        result = {
            "address": address,
            "matched_address": geocode_result["matched_address"],
            "coordinates": {"latitude": geocode_result["latitude"], "longitude": geocode_result["longitude"]},
            "census_tract": census_tract,
            "demographics": demographics,
            "ami_data": ami_data,
            "qct_dda_status": qct_dda_status,
            "opportunity_index": opportunity_index,
            "competition_analysis": competition_analysis,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Enhanced scoring with competition
        result["texas_scoring"] = self.calculate_enhanced_texas_lihtc_score(result)
        
        self.print_enhanced_analysis_summary(result)
        return result

    def calculate_enhanced_texas_lihtc_score(self, analysis_result: Dict) -> Dict:
        """Enhanced scoring with competition analysis"""
        
        scoring = {
            "opportunity_index": 0,
            "competition_score": 0,
            "federal_benefits": [],
            "total_analyzed_points": 0,
            "category": "UNKNOWN",
            "scoring_details": []
        }
        
        # Opportunity Index (0-2 points)
        if analysis_result.get("opportunity_index"):
            opp_score = analysis_result["opportunity_index"]["score"]
            scoring["opportunity_index"] = opp_score
            scoring["total_analyzed_points"] += opp_score
            scoring["scoring_details"].append(f"Opportunity Index: {opp_score} points")
        
        # Competition Score (0-3 points) - NEW
        if analysis_result.get("competition_analysis"):
            comp_score = analysis_result["competition_analysis"]["competition_score"]
            scoring["competition_score"] = comp_score
            scoring["total_analyzed_points"] += comp_score
            
            saturation = analysis_result["competition_analysis"]["saturation_analysis"]["saturation_level"]
            scoring["scoring_details"].append(f"Competition Score: {comp_score} points (Market: {saturation})")
        
        # Federal Benefits
        if analysis_result.get("qct_dda_status", {}).get("federal_basis_boost"):
            benefits = []
            if analysis_result["qct_dda_status"]["qct_status"]:
                benefits.append("QCT (30% basis boost)")
            if analysis_result["qct_dda_status"]["dda_status"]:
                benefits.append("DDA (30% basis boost)")
            scoring["federal_benefits"] = benefits
        
        # Enhanced Category Logic
        has_federal_boost = len(scoring["federal_benefits"]) > 0
        total_points = scoring["total_analyzed_points"]
        comp_score = scoring["competition_score"]
        
        if has_federal_boost and total_points >= 4 and comp_score >= 2:
            scoring["category"] = "BEST"
        elif has_federal_boost and total_points >= 3:
            scoring["category"] = "GOOD"
        elif comp_score >= 3 and total_points >= 3:
            scoring["category"] = "GOOD"
        elif total_points >= 2 and comp_score >= 2:
            scoring["category"] = "MAYBE"
        elif comp_score == 0:
            scoring["category"] = "FIRM NO"
        else:
            scoring["category"] = "FIRM NO"
        
        return scoring

    def print_enhanced_analysis_summary(self, result: Dict):
        """Print enhanced summary with competition analysis"""
        
        print(f"  📍 Location: {result['coordinates']['latitude']:.6f}, {result['coordinates']['longitude']:.6f}")
        
        # Demographics
        if result.get("demographics"):
            demo = result["demographics"]
            print(f"  📊 Demographics: Poverty {demo.get('poverty_rate', 'N/A')}%, Income ${demo.get('median_household_income', 0):,}")
        
        # Competition Analysis - NEW
        if result.get("competition_analysis"):
            comp = result["competition_analysis"]
            print(f"  🎯 Market Analysis:")
            print(f"    • Search Radius: {comp['search_radius_miles']} miles")
            print(f"    • Competing Projects: {comp['projects_within_radius']}")
            print(f"    • Market Saturation: {comp['saturation_analysis']['saturation_level']}")
            
            if comp['nearest_project']:
                nearest = comp['nearest_project']
                print(f"    • Nearest Project: {nearest['distance']} miles ({nearest['total_units']} units)")
        
        # Scoring
        scoring = result.get("texas_scoring", {})
        print(f"  🏆 Total Score: {scoring.get('total_analyzed_points', 0)} points")
        print(f"  📋 Category: {scoring.get('category', 'UNKNOWN')}")

    def batch_analyze_addresses_with_competition(self, addresses: List[str]) -> List[Dict]:
        """Batch analyze addresses with enhanced competition analysis"""
        
        print(f"\n🚀 Starting enhanced batch analysis with competition scoring...")
        results = []
        
        for i, address in enumerate(addresses):
            print(f"\n--- Processing {i+1}/{len(addresses)} ---")
            
            try:
                result = self.enhanced_analyze_address(address)
                results.append(result)
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error analyzing {address}: {e}")
                results.append({"address": address, "error": str(e), "analysis_timestamp": datetime.now().isoformat()})
        
        # Sort by total scoring points and category
        results.sort(key=lambda x: (
            {"BEST": 4, "GOOD": 3, "MAYBE": 2, "FIRM NO": 1}.get(x.get("texas_scoring", {}).get("category", "UNKNOWN"), 0),
            x.get("texas_scoring", {}).get("total_analyzed_points", 0)
        ), reverse=True)
        
        return results

# Test the enhanced analyzer
if __name__ == "__main__":
    census_api_key = "06ece0121263282cd9ffd753215b007b8f9a3dfc"
    hud_ami_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx"
    
    analyzer = EnhancedTexasAnalyzer(
        census_api_key=census_api_key,
        hud_ami_file_path=hud_ami_file
    )
    
    # Test with Houston area addresses
    test_addresses = [
        "22214 Cypress Slough, Houston, TX 77073",
        "6053 Bellfort St Houston, TX 77033",
        "2904 Greens Rd, Houston, TX 77032"
    ]
    
    results = analyzer.batch_analyze_addresses_with_competition(test_addresses)
    
    print(f"\n📊 ENHANCED ANALYSIS COMPLETE:")
    for i, result in enumerate(results, 1):
        if "error" not in result:
            comp = result.get("competition_analysis", {})
            scoring = result.get("texas_scoring", {})
            print(f"{i}. {result['address']}")
            print(f"   Category: {scoring.get('category', 'UNKNOWN')}")
            print(f"   Total Points: {scoring.get('total_analyzed_points', 0)}")
            print(f"   Competition: {comp.get('saturation_analysis', {}).get('saturation_level', 'Unknown')}")
            print(f"   Market Rec: {comp.get('market_recommendation', 'N/A')}")
