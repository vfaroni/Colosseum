#!/usr/bin/env python3
"""
FIXED Enhanced Texas LIHTC Analyzer - Competition Data Fixed & Scoring Systems Separated
Key Fixes:
1. Uses TDHCA data for competition analysis (solves 0 projects issue)
2. Separates 9% LIHTC vs 4% Bond scoring systems
3. Adds deal_type parameter for appropriate analysis
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

try:
    from geopy.distance import geodesic
except ImportError:
    print("⚠️ geopy not installed. Install with: pip install geopy")
    def geodesic(coord1, coord2):
        import math
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        lat_diff = lat2 - lat1
        lon_diff = lon2 - lon1
        distance_km = ((lat_diff * 111.32) ** 2 + (lon_diff * 111.32 * math.cos(math.radians(lat1))) ** 2) ** 0.5
        class Distance:
            def __init__(self, km):
                self.km = km
                self.miles = km * 0.621371
        return Distance(distance_km)

class FixedTexasAnalyzer:
    def __init__(self, 
                 census_api_key: str,
                 hud_ami_file_path: str = None,
                 tdhca_project_file_path: str = None,
                 work_dir: str = "./fixed_texas_analysis"):
        """
        Initialize FIXED Texas LIHTC Analyzer with proper competition data and separated scoring
        
        Args:
            census_api_key: Your Census API key
            hud_ami_file_path: Path to HUD AMI Excel file
            tdhca_project_file_path: Path to TDHCA project list Excel file
            work_dir: Working directory for results and cache
        """
        self.census_api_key = census_api_key
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)
        
        # Search paths for files
        search_paths = [
            Path("."),
            Path(".."),
            Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code"),
            Path("/Users/williamrice/Downloads"),
            Path("/Users/williamrice/Desktop")
        ]
        
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
        self.tdhca_data = None
        self.census_cache = {}
        self.geocoding_cache = {}
        self.competition_cache = {}
        
        # Load HUD AMI data
        if hud_ami_file_path and Path(hud_ami_file_path).exists():
            self.load_ami_data(hud_ami_file_path)
        else:
            ami_file_found = self._search_for_file(search_paths, [
                "*AMI*Rent*Data*.xlsx", "HUD2025*.xlsx", "*HUD*AMI*.xlsx", "*AMI*.xlsx"
            ])
            if ami_file_found:
                try:
                    self.load_ami_data(str(ami_file_found))
                except Exception as e:
                    print(f"⚠️ Could not load AMI file: {e}")
                    self.ami_data = None
            else:
                print("⚠️ No AMI file found")
                self.ami_data = None

        # Load TDHCA project data (FIXED: This is our competition data source!)
        if tdhca_project_file_path and Path(tdhca_project_file_path).exists():
            self.load_tdhca_data(tdhca_project_file_path)
        else:
            tdhca_file_found = self._search_for_file(search_paths, [
                "*TDHCA*Project*List*.xlsx", "*TX_TDHCA*.xlsx", "*TDHCA*.xlsx"
            ])
            if tdhca_file_found:
                try:
                    self.load_tdhca_data(str(tdhca_file_found))
                except Exception as e:
                    print(f"⚠️ Could not load TDHCA file: {e}")
                    self.tdhca_data = None
            else:
                print("⚠️ No TDHCA project file found")
                self.tdhca_data = None
        
        # Load HUD designation data (QCT/DDA)
        self.load_hud_designation_data()
        
        print(f"FIXED Texas LIHTC Analyzer initialized.")
        print(f"Working directory: {self.work_dir}")
        print(f"Cache directory: {self.cache_dir}")
        print(f"Census API configured: {'✅' if census_api_key else '❌'}")
        print(f"HUD AMI data loaded: {'✅' if self.ami_data is not None else '❌'}")
        print(f"TDHCA project data loaded: {'✅' if self.tdhca_data is not None else '❌'}")
        if self.tdhca_data is not None:
            print(f"   → Total TDHCA projects: {len(self.tdhca_data):,}")
            houston_projects = len(self.tdhca_data[self.tdhca_data['Project City'].str.contains('Houston', case=False, na=False)])
            print(f"   → Houston area projects: {houston_projects:,}")

    def _search_for_file(self, search_paths: List[Path], patterns: List[str]) -> Optional[Path]:
        """Helper method to search for files with multiple patterns"""
        for search_path in search_paths:
            if search_path.exists():
                for pattern in patterns:
                    files = list(search_path.glob(pattern))
                    if files:
                        print(f"Found file: {files[0]}")
                        return files[0]
        return None

    def load_ami_data(self, file_path: str):
        """Load and index HUD AMI data for fast lookups"""
        try:
            print(f"Loading HUD AMI data from: {file_path}")
            
            if not Path(file_path).exists():
                raise FileNotFoundError(f"AMI file not found: {file_path}")
            
            df = pd.read_excel(file_path, sheet_name="MTSP2025-Static")
            print(f"Loaded {len(df)} total AMI records")
            
            texas_df = df[df['stusps'] == 'TX'].copy()
            print(f"Found {len(texas_df)} Texas AMI records")
            
            self.ami_data = {}
            for _, row in texas_df.iterrows():
                fips = str(row['fips'])
                self.ami_data[fips] = {
                    'hud_area_name': row['hud_area_name'],
                    'county_name': row['County_Name'],
                    'metro': row['metro'] == 1,
                    'median_ami': row['median2025'],
                    'income_limits': {
                        '50_pct': {
                            '1p': row['lim50_25p1'], '2p': row['lim50_25p2'], 
                            '3p': row['lim50_25p3'], '4p': row['lim50_25p4']
                        }
                    },
                    'rent_limits': {
                        '50_pct': {
                            'studio': row['Studio 50%'], '1br': row['1BR 50%'],
                            '2br': row['2BR 50%'], '3br': row['3BR 50%'], '4br': row['4BR 50%']
                        },
                        '60_pct': {
                            'studio': row['Studio 60%'], '1br': row['1BR 60%'],
                            '2br': row['2BR 60%'], '3br': row['3BR 60%'], '4br': row['4BR 60%']
                        },
                        '70_pct': {
                            'studio': row['Studio 70%'], '1br': row['1BR 70%'],
                            '2br': row['2BR 70%'], '3br': row['3BR 70%'], '4br': row['4BR 70%']
                        },
                        '80_pct': {
                            'studio': row['Studio 80%'], '1br': row['1BR 80%'],
                            '2br': row['2BR 80%'], '3br': row['3BR 80%'], '4br': row['4BR 80%']
                        }
                    }
                }
            
            print(f"✅ Loaded AMI data for {len(self.ami_data)} Texas areas")
            
        except Exception as e:
            print(f"❌ Error loading AMI data: {e}")
            self.ami_data = None

    def load_tdhca_data(self, file_path: str):
        """Load and process TDHCA project list (FIXED: This is our LIHTC competition dataset!)"""
        try:
            print(f"Loading TDHCA/LIHTC project data from: {file_path}")
            
            if not Path(file_path).exists():
                raise FileNotFoundError(f"TDHCA file not found: {file_path}")
            
            df = pd.read_excel(file_path)
            print(f"Loaded {len(df)} total TDHCA/LIHTC records")
            
            df_clean = df.copy()
            
            # Clean and standardize column names
            if 'Population Served' in df_clean.columns:
                df_clean['Population Served'] = df_clean['Population Served'].fillna('General').str.strip()
                df_clean['Population Served'] = df_clean['Population Served'].replace('General ', 'General')
            
            if 'CT 2020' in df_clean.columns:
                df_clean['CT 2020'] = df_clean['CT 2020'].astype(str).str.strip()
            
            if 'Year' in df_clean.columns:
                df_clean['Year'] = pd.to_numeric(df_clean['Year'], errors='coerce')
                
            # FIXED: Clean coordinate data for competition analysis
            if 'Latitude11' in df_clean.columns:
                df_clean['Latitude11'] = pd.to_numeric(df_clean['Latitude11'], errors='coerce')
            if 'Longitude11' in df_clean.columns:
                df_clean['Longitude11'] = pd.to_numeric(df_clean['Longitude11'], errors='coerce')
                
            # FIXED: Convert census tract to integer format (remove .0 decimals)
            if 'CT 2020' in df_clean.columns:
                df_clean['CT 2020'] = pd.to_numeric(df_clean['CT 2020'], errors='coerce').fillna(0).astype(int).astype(str)
                print(f"✅ Fixed census tract format (removed decimals)")
            
            self.tdhca_data = df_clean
            print(f"✅ Loaded TDHCA data with {len(self.tdhca_data)} projects")            

            # Show statistics
            if 'Population Served' in self.tdhca_data.columns:
                pop_counts = self.tdhca_data['Population Served'].value_counts()
                print(f"Population Served breakdown:")
                for pop_type, count in pop_counts.head(5).items():
                    print(f"  {pop_type}: {count} projects")
            
            # FIXED: Show competition data statistics
            houston_projects = self.tdhca_data[self.tdhca_data['Project City'].str.contains('Houston', case=False, na=False)]
            print(f"Houston area projects: {len(houston_projects)}")
            
            with_coords = houston_projects.dropna(subset=['Latitude11', 'Longitude11'])
            print(f"Houston projects with coordinates: {len(with_coords)}")
            
        except Exception as e:
            print(f"❌ Error loading TDHCA data: {e}")
            self.tdhca_data = None

    def load_hud_designation_data(self):
        """Load QCT/DDA data for federal benefits analysis"""
        try:
            base_hud_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD DDA QCT")
            
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
                
        except Exception as e:
            print(f"⚠️ Error loading HUD designation data: {e}")

    def get_demographics_from_census_api(self, census_tract: str) -> Dict:
        """Get comprehensive demographics from Census API with enhanced error handling"""
        
        cache_key = f"demographics_{census_tract}"
        if cache_key in self.census_cache:
            return self.census_cache[cache_key]
        
        cache_file = self.cache_dir / "census_api_cache" / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    cache_date = datetime.fromisoformat(cached_data.get('cached_date', '2020-01-01'))
                    if datetime.now() - cache_date < timedelta(days=30):
                        self.census_cache[cache_key] = cached_data['data']
                        return cached_data['data']
            except:
                pass
        
        try:
            if len(census_tract) >= 11:
                state_code = census_tract[:2]
                county_code = census_tract[2:5]
                tract_code = census_tract[5:]
            else:
                return {"error": "Invalid census tract format"}
            
            base_url = "https://api.census.gov/data/2022/acs/acs5"
            
            variables = [
                "B17001_002E",  # Poverty - Income below poverty level
                "B17001_001E",  # Poverty - Total for whom poverty determined  
                "B19013_001E",  # Median household income
                "B25044_001E",  # Total occupied housing units
                "B01003_001E",  # Total population
                "B15003_022E",  # Associates degree
                "B15003_023E",  # Bachelors degree  
                "B15003_024E",  # Masters degree
                "B15003_025E",  # Doctorate degree
                "B15003_001E",  # Total 25+ population
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
                        if value is None or str(value).strip() in ['', 'null', 'None', '-', 'N/A']:
                            return default
                        
                        str_val = str(value).strip()
                        
                        if ('-666' in str_val or '666666666' in str_val or 
                            str_val.startswith('-666') or str_val == '-666666666' or
                            abs(float(str_val)) > 100000000):
                            print(f"    ⚠️ Census API error pattern detected: '{str_val}' - treating as unavailable")
                            return default
                        
                        float_val = float(str_val)
                        int_val = int(float_val)
                        
                        if int_val < 0 or int_val > 500000:
                            print(f"    ⚠️ Census API unreasonable value: {int_val:,} - treating as unavailable")
                            return default
                            
                        return int_val
                    except (ValueError, TypeError) as e:
                        print(f"    ⚠️ Error parsing value '{value}': {e}")
                        return default
                
                total_pop = safe_int(row[5])
                poverty_total = safe_int(row[2])
                poverty_below = safe_int(row[1])
                median_income = safe_int(row[3])
                
                if median_income <= 0:
                    print(f"    ⚠️ Invalid median income after processing: ${median_income:,} - marked as unavailable")
                    median_income = 0
                
                total_25_plus = safe_int(row[10])
                associates_plus = sum([
                    safe_int(row[6]), safe_int(row[7]), safe_int(row[8]), safe_int(row[9])
                ])
                
                poverty_rate = (poverty_below / poverty_total * 100) if poverty_total > 0 else 0
                education_rate = (associates_plus / total_25_plus * 100) if total_25_plus > 0 else 0
                
                demographics = {
                    "census_tract": census_tract,
                    "total_population": total_pop,
                    "median_household_income": median_income,
                    "poverty_rate": round(poverty_rate, 2),
                    "low_poverty_tract": poverty_rate < 20.0,
                    "borderline_poverty": 19.0 <= poverty_rate <= 21.0,
                    "education_rate": round(education_rate, 2),
                    "high_education_tract": education_rate >= 27.0,
                    "data_date": "2022 ACS 5-Year",
                    "data_quality": "GOOD" if median_income > 0 and poverty_total > 0 else "POOR"
                }
                
                self.census_cache[cache_key] = demographics
                
                cache_data = {
                    "data": demographics,
                    "cached_date": datetime.now().isoformat()
                }
                with open(cache_file, 'w') as f:
                    json.dump(cache_data, f, indent=2)
                
                return demographics
            
        except Exception as e:
            print(f"❌ Census API error for tract {census_tract}: {e}")
            return {"error": str(e)}
        
        return {"error": "No data returned from Census API"}

    def get_ami_data_for_location(self, census_tract: str) -> Optional[Dict]:
        """Get AMI data for a census tract with improved matching"""
        if not self.ami_data or not census_tract:
            return None
        
        if len(census_tract) >= 5:
            county_fips = census_tract[:5] + "99999"
            if county_fips in self.ami_data:
                return self.ami_data[county_fips]
            
            county_fips_alt = census_tract[:5] + "00000"
            if county_fips_alt in self.ami_data:
                return self.ami_data[county_fips_alt]
            
            county_prefix = census_tract[:5]
            for fips_key in self.ami_data.keys():
                if fips_key.startswith(county_prefix):
                    return self.ami_data[fips_key]
        
        print(f"    ⚠️ No AMI data found for census tract {census_tract}")
        return None

    def enhanced_geocode_address(self, address: str) -> Optional[Dict]:
        """Enhanced geocoding with comprehensive location analysis"""
        
        cache_key = f"geocode_{hash(address)}"
        cache_file = self.cache_dir / "geocoding_cache" / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    cache_date = datetime.fromisoformat(cached_data.get('cached_date', '2020-01-01'))
                    if datetime.now() - cache_date < timedelta(days=7):
                        return cached_data['data']
            except:
                pass
        
        address_variations = self.clean_address(address)
        
        for i, addr_variant in enumerate(address_variations):
            try:
                print(f"    Geocoding attempt {i+1}: {addr_variant}")
                
                url = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
                params = {
                    'address': addr_variant,
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
                    matched_address = match.get('matchedAddress', addr_variant)
                    
                    census_tract = None
                    if 'geographies' in match:
                        tracts = match['geographies'].get('Census Tracts', [])
                        if tracts:
                            census_tract = tracts[0].get('GEOID')
                    
                    geocode_result = {
                        "address": address,
                        "matched_address": matched_address,
                        "longitude": coords['x'],
                        "latitude": coords['y'],
                        "census_tract": census_tract,
                        "geocoding_success": True
                    }
                    
                    cache_data = {
                        "data": geocode_result,
                        "cached_date": datetime.now().isoformat()
                    }
                    with open(cache_file, 'w') as f:
                        json.dump(cache_data, f, indent=2)
                    
                    print(f"    ✅ Geocoded successfully")
                    return geocode_result
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    ❌ Attempt {i+1} failed: {e}")
                continue
        
        print(f"    ❌ All geocoding attempts failed")
        return None

    def clean_address(self, address: str) -> List[str]:
        """Create comprehensive address variations for better geocoding"""
        address = address.strip()
        variations = [address]
        
        # Add TX if missing
        has_state = ', TX' in address.upper() or ' TX ' in address.upper()
        if not has_state:
            variations.append(f"{address}, TX")
            variations.append(f"{address}, Texas")
        
        # Remove apartment/unit numbers
        no_apt = re.sub(r'(apt\.?|apartment|unit|#|suite|ste\.?)\s*\w*', '', address, flags=re.IGNORECASE).strip()
        if no_apt != address and no_apt:
            variations.append(no_apt)
            if not has_state:
                variations.append(f"{no_apt}, TX")
        
        # Street type replacements
        street_types = [
            ('Drive', 'Dr'), ('Street', 'St'), ('Avenue', 'Ave'),
            ('Boulevard', 'Blvd'), ('Road', 'Rd'), ('Lane', 'Ln'),
            ('Court', 'Ct'), ('Place', 'Pl'), ('Circle', 'Cir'),
            ('Parkway', 'Pkwy'), ('Trail', 'Trl')
        ]
        
        base_variations = variations.copy()
        for full_word, abbrev in street_types:
            for base_addr in base_variations:
                if full_word in base_addr:
                    new_addr = base_addr.replace(full_word, abbrev).strip()
                    if new_addr not in variations:
                        variations.append(new_addr)
                if abbrev in base_addr:
                    new_addr = base_addr.replace(abbrev, full_word).strip()
                    if new_addr not in variations:
                        variations.append(new_addr)
        
        # Remove duplicates while preserving order
        clean_variations = []
        seen = set()
        for var in variations:
            var = var.strip()
            if var and var not in seen and len(var) > 5:
                seen.add(var)
                clean_variations.append(var)
        
        return clean_variations

    def calculate_opportunity_index_score(self, demographics: Dict, ami_data: Dict) -> Dict:
        """Calculate opportunity index score for 4% bond deals"""
        
        if not demographics or "error" in demographics:
            return {"score": 0, "reason": "No demographic data available"}
        
        if demographics.get("data_quality") == "POOR":
            return {"score": 0, "reason": f"Poor data quality - median income: ${demographics.get('median_household_income', 0):,}"}
        
        poverty_rate = demographics.get("poverty_rate", 100)
        median_income = demographics.get("median_household_income", 0)
        
        if poverty_rate < 20.0:  # Low poverty area
            if median_income >= 85000:
                return {
                    "score": 2,
                    "reason": f"Low poverty ({poverty_rate:.1f}%) + high income quartile (${median_income:,})"
                }
            elif median_income >= 60000:
                return {
                    "score": 2,
                    "reason": f"Low poverty ({poverty_rate:.1f}%) + middle income quartile (${median_income:,})"
                }
            elif median_income > 0:
                return {
                    "score": 1,
                    "reason": f"Low poverty area ({poverty_rate:.1f}%) - income: ${median_income:,}"
                }
            else:
                return {
                    "score": 1,
                    "reason": f"Low poverty area ({poverty_rate:.1f}%) - income data unavailable"
                }
        
        elif 19.0 <= poverty_rate <= 21.0:  # Borderline cases
            if median_income >= 60000:
                return {
                    "score": 1,
                    "reason": f"Borderline low poverty ({poverty_rate:.1f}%) + decent income (${median_income:,})"
                }
            elif median_income > 0:
                return {
                    "score": 0,
                    "reason": f"Borderline poverty ({poverty_rate:.1f}%) + lower income (${median_income:,})"
                }
            else:
                return {
                    "score": 0,
                    "reason": f"Borderline poverty ({poverty_rate:.1f}%) + income data unavailable"
                }
        else:
            return {
                "score": 0,
                "reason": f"High poverty area: {poverty_rate:.1f}% (above 20% threshold)"
            }

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
                    qct_row = qct_intersects.iloc[0]
                    status["qct_details"] = {
                        "geoid": qct_row.get('GEOID', 'N/A'),
                        "name": qct_row.get('NAME', 'N/A')
                    }
            
            # Check DDA status
            if self.dda_data is not None:
                dda_intersects = self.dda_data[self.dda_data.contains(point)]
                if not dda_intersects.empty:
                    status["dda_status"] = True
                    status["federal_basis_boost"] = True
                    dda_row = dda_intersects.iloc[0]
                    status["dda_details"] = {
                        "zcta5": dda_row.get('ZCTA5', 'N/A'),
                        "dda_type": dda_row.get('DDA_TYPE', 'N/A'),
                        "dda_name": dda_row.get('DDA_NAME', 'N/A')
                    }
        
        except Exception as e:
            print(f"⚠️ Error checking QCT/DDA status: {e}")
        
        return status

    def determine_market_radius(self, point: Point, demographics: Dict = None) -> float:
        """Determine appropriate market radius based on location"""
        
        major_metros = {
            'Houston': {'lat_range': (29.5, 30.1), 'lon_range': (-95.8, -95.0)},
            'Dallas': {'lat_range': (32.6, 33.0), 'lon_range': (-97.0, -96.5)},
            'Austin': {'lat_range': (30.1, 30.5), 'lon_range': (-98.0, -97.5)},
            'San Antonio': {'lat_range': (29.2, 29.7), 'lon_range': (-98.8, -98.2)},
            'Fort Worth': {'lat_range': (32.6, 32.9), 'lon_range': (-97.5, -97.1)}
        }
        
        lat, lon = point.y, point.x
        
        for metro, bounds in major_metros.items():
            if (bounds['lat_range'][0] <= lat <= bounds['lat_range'][1] and 
                bounds['lon_range'][0] <= lon <= bounds['lon_range'][1]):
                
                if metro in ['Houston', 'Dallas', 'Austin']:
                    return 2.0  # Dense urban
                else:
                    return 3.0  # Other metros
        
        if demographics:
            population = demographics.get('total_population', 0)
            if population > 5000:
                return 4.0  # Suburban
            else:
                return 8.0  # Rural
        
        return 4.0  # Default suburban

    def get_nearby_lihtc_projects(self, target_point: Point, radius_miles: float) -> List[Dict]:
        """FIXED: Find LIHTC projects using TDHCA data with correct column names"""
        
        if self.tdhca_data is None:
            print(f"    ⚠️ No TDHCA data available for competition analysis")
            return []
        
        nearby_projects = []
        target_coords = (target_point.y, target_point.x)
        
        total_projects_checked = 0
        valid_geometry_count = 0
        
        # FIXED: Use correct TDHCA column names
        for idx, project in self.tdhca_data.iterrows():
            total_projects_checked += 1
            try:
                # FIXED: Use Latitude11 and Longitude11 columns
                lat = project.get('Latitude11')
                lon = project.get('Longitude11')
                
                if pd.isna(lat) or pd.isna(lon):
                    continue
                
                project_coords = (float(lat), float(lon))
                valid_geometry_count += 1
                
                try:
                    distance_miles = geodesic(target_coords, project_coords).miles
                    
                    if distance_miles <= radius_miles:
                        # FIXED: Use correct column names
                        project_name = str(project.get('Development Name', 'Unknown')).strip()
                        if project_name in ['Unknown', 'nan', 'None', '']:
                            project_name = 'Unknown'
                        
                        total_units = 0
                        if pd.notna(project.get('Total Units')):
                            try:
                                total_units = int(float(project.get('Total Units', 0)))
                            except (ValueError, TypeError):
                                total_units = 0
                        
                        year_placed = 0
                        year_display = "N/A"
                        if pd.notna(project.get('Year')):
                            try:
                                full_year = int(float(project.get('Year', 0)))
                                if 1950 <= full_year <= 2030:
                                    year_placed = full_year
                                    year_display = f"'{str(full_year)[-2:]}"
                            except (ValueError, TypeError):
                                pass
                        
                        project_info = {
                            'distance': round(distance_miles, 2),
                            'project_name': project_name,
                            'total_units': total_units,
                            'year_placed': year_placed,
                            'year_display': year_display,
                            'city': str(project.get('Project City', 'Unknown')).strip(),
                            'coordinates': project_coords
                        }
                        nearby_projects.append(project_info)
                except Exception as distance_error:
                    continue
                        
            except Exception as e:
                continue
        
        print(f"    📊 Competition Analysis:")
        print(f"       • Total TDHCA projects checked: {total_projects_checked:,}")
        print(f"       • Projects with valid coordinates: {valid_geometry_count:,}")
        print(f"       • Projects within {radius_miles} miles: {len(nearby_projects)}")
        
        nearby_projects.sort(key=lambda x: x['distance'])
        return nearby_projects

    def calculate_market_saturation_score(self, nearby_projects: List[Dict], demographics: Dict) -> Dict:
        """
        FIXED: Calculate market saturation for 4% bond deals with correct logic for zero competition
        """
    
        # FIXED: Handle zero competition case properly - this should be EXCELLENT!
        if not nearby_projects:
            if not demographics:
                return {
                    'saturation_level': 'UNKNOWN',
                    'saturation_score': 0,
                    'total_competing_units': 0,
                    'qualified_households_estimate': 0,
                    'units_per_100_households': 0
                }
            else:
                # FIXED: Zero competing projects = BEST case scenario!
                total_population = demographics.get('total_population', 0)
                households_estimate = total_population / 2.5
                qualified_households = households_estimate * 0.30
                
                return {
                    'saturation_level': 'EXCELLENT',  # Changed from UNKNOWN
                    'saturation_score': 3,            # Changed from 0 to maximum!
                    'total_competing_units': 0,
                    'qualified_households_estimate': int(qualified_households),
                    'units_per_100_households': 0     # 0 units = perfect score
                }
        
        # Continue with existing logic for when there ARE competing projects
        if not demographics:
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
        
        # FIXED: Determine saturation level and score with correct logic
        if units_per_100 < 15:
            level = 'LOW'
            score = 3  # Excellent opportunity
        elif units_per_100 < 30:
            level = 'MEDIUM'
            score = 2  # Good opportunity
        elif units_per_100 < 50:
            level = 'HIGH'
            score = 1  # Some competition
        else:
            level = 'OVERSATURATED'
            score = 0  # Avoid development
        
        return {
            'saturation_level': level,
            'saturation_score': score,
            'total_competing_units': total_units,
            'qualified_households_estimate': int(qualified_households),
            'units_per_100_households': round(units_per_100, 1)}

    def analyze_project_timeline(self, nearby_projects: List[Dict]) -> Dict:
        """Analyze development timeline and pipeline risk"""
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
        """Comprehensive LIHTC competition analysis for 4% bond deals"""
        
        radius = self.determine_market_radius(point, demographics)
        nearby_projects = self.get_nearby_lihtc_projects(point, radius)
        saturation = self.calculate_market_saturation_score(nearby_projects, demographics)
        timeline = self.analyze_project_timeline(nearby_projects)
        
        competition_score = saturation['saturation_score']
        
        if timeline['pipeline_risk'] == 'HIGH':
            competition_score = max(0, competition_score - 1)
        
        return {
            'search_radius_miles': radius,
            'projects_within_radius': len(nearby_projects),
            'nearby_projects': nearby_projects,
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

    # REPLACE the calculate_tdhca_same_tract_score method in _d.py with this enhanced debug version

    def calculate_tdhca_same_tract_score(self, census_tract: str, target_population: str = 'General', base_year: int = 2026) -> Dict:
        """Calculate TDHCA Criteria 1: Same census tract scoring with ENHANCED DEBUGGING"""
        
        if self.tdhca_data is None:
            return {
                "score": 0,
                "reason": "TDHCA data not available",
                "detail": "Cannot perform regulatory scoring",
                "competing_projects": [],
                "borderline": None
            }
        
        # ENHANCED DEBUGGING - Let's see what's happening
        print(f"    🔍 TDHCA DEBUG for tract {census_tract}:")
        print(f"       • Target population: {target_population}")
        print(f"       • Total TDHCA records: {len(self.tdhca_data)}")
        
        # DEBUG: Check census tract column and sample values
        print(f"       • Census tract column name: 'CT 2020'")
        if 'CT 2020' in self.tdhca_data.columns:
            sample_tracts = self.tdhca_data['CT 2020'].dropna().astype(str).head(10).tolist()
            print(f"       • Sample census tracts in data: {sample_tracts}")
            print(f"       • Looking for tract: '{census_tract}' (type: {type(census_tract)})")
            
            # Check for exact matches
            exact_matches = self.tdhca_data[self.tdhca_data['CT 2020'].astype(str) == str(census_tract)]
            print(f"       • Exact matches for {census_tract}: {len(exact_matches)}")
            
            # Check for partial matches (maybe formatting issue)
            if len(exact_matches) == 0:
                # Try without leading zeros
                tract_no_leading = census_tract.lstrip('0')
                partial_matches = self.tdhca_data[self.tdhca_data['CT 2020'].astype(str).str.contains(tract_no_leading, na=False)]
                print(f"       • Partial matches (no leading zeros): {len(partial_matches)}")
                
                # Try as numeric comparison
                try:
                    tract_numeric = float(census_tract)
                    numeric_matches = self.tdhca_data[pd.to_numeric(self.tdhca_data['CT 2020'], errors='coerce') == tract_numeric]
                    print(f"       • Numeric matches: {len(numeric_matches)}")
                except:
                    print(f"       • Could not convert tract to numeric")
        else:
            print(f"       • ERROR: 'CT 2020' column not found!")
            print(f"       • Available columns: {list(self.tdhca_data.columns)}")
            return {
                "score": 0,
                "reason": "Census tract column not found",
                "detail": "CT 2020 column missing from TDHCA data",
                "competing_projects": [],
                "borderline": None
            }
        
        # Continue with existing logic but with matches found
        same_tract_projects = self.tdhca_data[
            (self.tdhca_data['CT 2020'].astype(str) == str(census_tract)) &
            (self.tdhca_data['Population Served'] == target_population)
        ].copy()
        
        print(f"       • {target_population} population projects in tract: {len(same_tract_projects)}")
        
        if len(same_tract_projects) == 0:
            # Check what populations ARE available in this tract
            all_tract_projects = self.tdhca_data[self.tdhca_data['CT 2020'].astype(str) == str(census_tract)]
            if len(all_tract_projects) > 0:
                available_pops = all_tract_projects['Population Served'].value_counts()
                print(f"       • Available populations in tract: {dict(available_pops)}")
            
            return {
                "score": 5,
                "reason": "No competing projects in census tract",
                "detail": f"Clean slate - no {target_population} projects in tract {census_tract}",
                "competing_projects": [],
                "borderline": None
            }
        
        # Rest of the existing logic...
        same_tract_projects = same_tract_projects[same_tract_projects['Year'].notna()].copy()
        
        if len(same_tract_projects) == 0:
            return {
                "score": 5,
                "reason": "No competing projects with valid years",
                "detail": f"Projects found but no valid year data",
                "competing_projects": [],
                "borderline": None
            }
        
        # Continue with existing scoring logic...
        same_tract_projects['years_since'] = base_year - same_tract_projects['Year']
        most_recent_year = int(same_tract_projects['Year'].max())
        years_since_recent = base_year - most_recent_year
        
        print(f"       • Most recent project: {most_recent_year} ({years_since_recent} years ago)")
        
        # Build competing projects list
        competing_projects = []
        for _, project in same_tract_projects.iterrows():
            competing_projects.append({
                'name': project.get('Development Name', 'Unknown'),
                'year': int(project['Year']) if pd.notna(project['Year']) else 0,
                'units': int(project.get('Total Units', 0)) if pd.notna(project.get('Total Units', 0)) else 0,
                'years_ago': int(base_year - project['Year']) if pd.notna(project['Year']) else 0
            })
        
        competing_projects.sort(key=lambda x: x['year'], reverse=True)
        
        # Scoring logic (same as before)
        if years_since_recent >= 20:
            score = 5
            reason = f"Most recent project: {most_recent_year} ({years_since_recent} years ago)"
            detail = f"All projects 20+ years old"
        elif years_since_recent >= 15:
            score = 4
            reason = f"Most recent project: {most_recent_year} ({years_since_recent} years ago)" 
            detail = f"{len(same_tract_projects)} competing projects (15-19 years old)"
        elif years_since_recent >= 10:
            score = 3
            reason = f"Most recent project: {most_recent_year} ({years_since_recent} years ago)"
            detail = f"{len(same_tract_projects)} competing projects (10-14 years old)"
        else:
            score = 0
            reason = f"Recent competing project: {most_recent_year} ({years_since_recent} years ago)"
            detail = f"Recent competition in tract"
        
        print(f"       • TDHCA Score: {score}/5 points - {reason}")
        
        return {
            "score": score,
            "reason": reason,
            "detail": detail,
            "competing_projects": competing_projects,
            "borderline": None
        }

    def detect_target_population(self, project_description: str = "", development_name: str = "") -> str:
        """Detect likely target population based on project information"""
        
        text_to_analyze = f"{project_description} {development_name}".lower()
        
        elderly_keywords = ['senior', 'elderly', 'age', 'retirement', 'assisted', '55+', '62+', 'active adult']
        
        for keyword in elderly_keywords:
            if keyword in text_to_analyze:
                return 'Elderly'
        
        return 'General'

    def calculate_bond_deal_score(self, analysis_result: Dict) -> Dict:
        """4% Bond Deal Scoring (0-5 points: 0-2 opportunity + 0-3 competition)"""
        
        scoring = {
            "opportunity_score": 0,
            "competition_score": 0,
            "total_points": 0,
            "federal_benefits": [],
            "category": "UNKNOWN",
            "scoring_details": []
        }
        
        # Opportunity Index (0-2 points)
        if analysis_result.get("opportunity_index"):
            opp_score = analysis_result["opportunity_index"]["score"]
            scoring["opportunity_score"] = opp_score
            scoring["total_points"] += opp_score
            scoring["scoring_details"].append(f"Opportunity Index: {opp_score}/2 points - {analysis_result['opportunity_index']['reason']}")
        
        # Competition Score (0-3 points)
        if analysis_result.get("competition_analysis"):
            comp_score = analysis_result["competition_analysis"]["competition_score"]
            scoring["competition_score"] = comp_score
            scoring["total_points"] += comp_score
            
            saturation = analysis_result["competition_analysis"]["saturation_analysis"]["saturation_level"]
            scoring["scoring_details"].append(f"Competition Score: {comp_score}/3 points (Market: {saturation})")
        
        # Federal Benefits (30% basis boost)
        if analysis_result.get("qct_dda_status", {}).get("federal_basis_boost"):
            benefits = []
            if analysis_result["qct_dda_status"]["qct_status"]:
                benefits.append("QCT (30% basis boost)")
            if analysis_result["qct_dda_status"]["dda_status"]:
                benefits.append("DDA (30% basis boost)")
            scoring["federal_benefits"] = benefits
            scoring["scoring_details"].append(f"Federal Benefits: {', '.join(benefits)}")
        
        # Category Logic for 4% Bond Deals
        has_federal_boost = len(scoring["federal_benefits"]) > 0
        total_points = scoring["total_points"]
        comp_score = scoring["competition_score"]
        opp_score = scoring["opportunity_score"]
        
        if has_federal_boost and total_points >= 4:
            scoring["category"] = "BEST"
        elif has_federal_boost and total_points >= 3:
            scoring["category"] = "GOOD"
        elif total_points >= 4:
            scoring["category"] = "GOOD"
        elif has_federal_boost and total_points >= 2:
            scoring["category"] = "GOOD"
        elif comp_score == 0:  # Oversaturated market
            scoring["category"] = "FIRM NO"
        elif total_points >= 3:
            scoring["category"] = "MAYBE"
        elif total_points >= 2 and opp_score >= 1:
            scoring["category"] = "MAYBE"
        else:
            scoring["category"] = "FIRM NO"

        # ENHANCEMENT: Promote borderline poverty cases from FIRM NO to MAYBE
        if scoring["category"] == "FIRM NO":
            # Check if this was a borderline poverty case (19-21%)
            demographics = analysis_result.get("demographics", {})
            if demographics and "error" not in demographics:
                poverty_rate = demographics.get("poverty_rate", 100)
                
                # If borderline poverty (19.0-21.0%), promote to MAYBE with potential note
                if 19.0 <= poverty_rate <= 21.0:
                    scoring["category"] = "MAYBE"
                    
                    # Calculate potential scoring if verified as low poverty
                    potential_opportunity = 2  # Would get full opportunity points
                    current_competition = scoring.get("competition_score", 0)
                    potential_total = potential_opportunity + current_competition
                    
                    # Add potential upside note
                    potential_note = f"Borderline poverty ({poverty_rate:.1f}%) - Potential if HUD verifies <20%: {potential_total}/5 points"
                    scoring["scoring_details"].append(potential_note)

        return scoring

    def calculate_nine_percent_score(self, analysis_result: Dict) -> Dict:
        """9% LIHTC Deal Scoring (0-5 TDHCA regulatory points + federal benefits)"""
        
        scoring = {
            "tdhca_same_tract_score": 0,
            "total_tdhca_points": 0,
            "federal_benefits": [],
            "category": "UNKNOWN", 
            "scoring_details": []
        }
        
        # TDHCA Same Tract Score (0-5 points)
        if analysis_result.get("tdhca_same_tract"):
            tdhca_score = analysis_result["tdhca_same_tract"]["score"]
            scoring["tdhca_same_tract_score"] = tdhca_score
            scoring["total_tdhca_points"] += tdhca_score
            
            tdhca_detail = analysis_result["tdhca_same_tract"]["detail"]
            borderline = analysis_result["tdhca_same_tract"].get("borderline")
            
            detail_text = f"TDHCA Same Tract: {tdhca_score}/5 points - {tdhca_detail}"
            if borderline:
                detail_text += f" ({borderline})"
                
            scoring["scoring_details"].append(detail_text)
        
        # Federal Benefits (30% basis boost)
        if analysis_result.get("qct_dda_status", {}).get("federal_basis_boost"):
            benefits = []
            if analysis_result["qct_dda_status"]["qct_status"]:
                benefits.append("QCT (30% basis boost)")
            if analysis_result["qct_dda_status"]["dda_status"]:
                benefits.append("DDA (30% basis boost)")
            scoring["federal_benefits"] = benefits
            scoring["scoring_details"].append(f"Federal Benefits: {', '.join(benefits)}")
        
        # Category Logic for 9% LIHTC Deals
        has_federal_boost = len(scoring["federal_benefits"]) > 0
        tdhca_points = scoring["total_tdhca_points"]
        
        if tdhca_points >= 5:
            scoring["category"] = "BEST"
        elif tdhca_points >= 4 and has_federal_boost:
            scoring["category"] = "BEST"
        elif tdhca_points >= 4:
            scoring["category"] = "GOOD"
        elif tdhca_points >= 3 and has_federal_boost:
            scoring["category"] = "GOOD"
        elif tdhca_points >= 3:
            scoring["category"] = "MAYBE"
        elif has_federal_boost and tdhca_points >= 1:
            scoring["category"] = "MAYBE"
        else:
            scoring["category"] = "FIRM NO"
        
        return scoring

    def comprehensive_analyze_address(self, address: str, deal_type: str = "4% Bond") -> Dict:
        """
        FIXED comprehensive address analysis with separated scoring systems
        
        Args:
            address: Property address to analyze
            deal_type: "4% Bond" or "9% LIHTC" - determines scoring system used
        """
        
        # START TIMING
        start_time = time.time()
        print(f"\n🔍 FIXED Analysis ({deal_type}): {address}")
        
        # Step 1: Geocoding
        geocode_result = self.enhanced_geocode_address(address)
        if not geocode_result:
            return {"error": "Geocoding failed", "address": address, "deal_type": deal_type}
        
        # Step 2: Get demographics from Census API
        census_tract = geocode_result.get("census_tract")
        print(f"  📍 Census Tract: {census_tract}")
        demographics = self.get_demographics_from_census_api(census_tract) if census_tract else {}
        
        # Step 3: Get AMI data
        ami_data = self.get_ami_data_for_location(census_tract) if census_tract else None
        
        # Step 4: Check QCT/DDA status
        point = Point(geocode_result["longitude"], geocode_result["latitude"])
        qct_dda_status = self.check_qct_dda_status(point)
        
        # Step 5: Always do TDHCA analysis (for both deal types, useful reference)
        target_population = self.detect_target_population("", address)
        tdhca_same_tract = self.calculate_tdhca_same_tract_score(census_tract, target_population)
        
        # Step 6: Always do competition analysis (for both deal types)
        competition_analysis = self.analyze_lihtc_competition(point, demographics)
        
        # Step 7: Always calculate opportunity index (for both deal types)
        opportunity_index = self.calculate_opportunity_index_score(demographics, ami_data)
        
        # Step 8: Compile result
        result = {
            "address": address,
            "deal_type": deal_type,
            "matched_address": geocode_result["matched_address"],
            "coordinates": {
                "latitude": geocode_result["latitude"],
                "longitude": geocode_result["longitude"]
            },
            "census_tract": census_tract,
            "demographics": demographics,
            "ami_data": ami_data,
            "qct_dda_status": qct_dda_status,
            "opportunity_index": opportunity_index,
            "competition_analysis": competition_analysis,
            "tdhca_same_tract": tdhca_same_tract,
            "target_population": target_population,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Step 9: Calculate appropriate scoring based on deal type
        if deal_type == "9% LIHTC":
            result["scoring"] = self.calculate_nine_percent_score(result)
        else:  # Default to 4% Bond
            result["scoring"] = self.calculate_bond_deal_score(result)
        
        # END TIMING AND DISPLAY
        end_time = time.time()
        analysis_duration = end_time - start_time
        result["analysis_duration_seconds"] = round(analysis_duration, 2)
        
        # Enhanced timing display
        print(f"  ⏱️ Analysis completed in {analysis_duration:.2f} seconds")
        if analysis_duration > 10:
            print(f"     ⚠️ Slow analysis - consider checking Census API response time")
        elif analysis_duration < 3:
            print(f"     ✅ Fast analysis - good performance")
        
        # Print summary
        self.print_analysis_summary(result)
        
        return result

    def print_analysis_summary(self, result: Dict):
        """Print formatted analysis summary with deal-type specific scoring"""
        
        deal_type = result.get('deal_type', '4% Bond')
        print(f"  📍 Location: {result['coordinates']['latitude']:.6f}, {result['coordinates']['longitude']:.6f}")
        
        # Demographics with poverty indicators
        if result.get("demographics"):
            demo = result["demographics"]
            data_quality = demo.get("data_quality", "UNKNOWN")
            quality_emoji = "✅" if data_quality == "GOOD" else "⚠️"
            
            poverty_rate = demo.get('poverty_rate', 100)
            if poverty_rate < 20.0:
                poverty_indicator = "✅ LOW POVERTY"
            elif 19.0 <= poverty_rate <= 21.0:
                poverty_indicator = "⚠️ BORDERLINE"
            else:
                poverty_indicator = "❌ HIGH POVERTY"
            
            median_income = demo.get('median_household_income', 0)
            if median_income > 0:
                income_display = f"Income ${median_income:,}"
            else:
                income_display = "Income: Unavailable"
            
            print(f"  📊 Demographics: Poverty {poverty_rate}% {poverty_indicator}, {income_display} {quality_emoji}")
        
        # AMI data
        if result.get("ami_data"):
            ami = result["ami_data"]
            print(f"  🏠 Area: {ami['hud_area_name']} ({'Metro' if ami['metro'] else 'Non-Metro'})")
            print(f"  💰 AMI: ${ami['median_ami']:,}, 1BR 50%: ${ami['rent_limits']['50_pct']['1br']}")
        else:
            print(f"  ⚠️ No AMI data found for this location")

        # Competition Analysis (always shown for reference)
        if result.get("competition_analysis"):
            comp = result["competition_analysis"]
            print(f"  🎯 Market Analysis:")
            print(f"    • Search Radius: {comp['search_radius_miles']} miles")
            print(f"    • Competing Projects: {comp['projects_within_radius']}")
            print(f"    • Market Saturation: {comp['saturation_analysis']['saturation_level']}")
            
            if comp['nearest_project']:
                nearest = comp['nearest_project']
                name_display = nearest['project_name'] if nearest['project_name'] != 'Unknown' else 'Unnamed project'
                units_display = f"{nearest['total_units']} units" if nearest['total_units'] > 0 else "units unknown"
                year_display = f", {nearest['year_display']}" if nearest.get('year_display', 'N/A') != 'N/A' else ""
                
                print(f"    • Nearest Project: {nearest['distance']} miles - {name_display} ({units_display}{year_display})")

        # TDHCA Regulatory Scoring (always shown for reference)
        if result.get("tdhca_same_tract"):
            tdhca = result["tdhca_same_tract"]
            print(f"  🏛️ TDHCA Same Tract: {tdhca['score']}/5 points - {tdhca.get('detail', 'No details')}")
            if tdhca.get("borderline"):
                print(f"    ⏰ Timing Note: {tdhca.get('borderline')}")
        
        # Federal benefits
        qct_dda = result.get("qct_dda_status", {})
        federal_benefits = []
        if qct_dda.get("qct_status"):
            federal_benefits.append("QCT")
        if qct_dda.get("dda_status"):
            federal_benefits.append("DDA")
        
        if federal_benefits:
            print(f"  🎯 Federal Benefits: {', '.join(federal_benefits)} (30% basis boost)")
        
        # Deal-specific scoring display
        scoring = result.get("scoring", {})
        if deal_type == "9% LIHTC":
            print(f"  🏆 9% LIHTC Scoring:")
            print(f"    • TDHCA Same Tract: {scoring.get('tdhca_same_tract_score', 0)}/5 points")
            print(f"    • Category: {scoring.get('category', 'UNKNOWN')}")
        else:
            print(f"  🏆 4% Bond Deal Scoring:")
            print(f"    • Opportunity: {scoring.get('opportunity_score', 0)}/2 points")
            print(f"    • Competition: {scoring.get('competition_score', 0)}/3 points")
            print(f"    • Total: {scoring.get('total_points', 0)}/5 points")
            print(f"    • Category: {scoring.get('category', 'UNKNOWN')}")

    def batch_analyze_addresses(self, addresses: List[str], deal_type: str = "4% Bond", progress_callback=None) -> List[Dict]:
        """Batch analyze multiple addresses with enhanced performance tracking"""
    
        batch_start_time = time.time()
        print(f"\n🚀 Starting FIXED batch analysis of {len(addresses)} addresses ({deal_type})...")
        results = []
        total_analysis_time = 0
        
        for i, address in enumerate(addresses):
            print(f"\n--- Processing {i+1}/{len(addresses)} ---")
            
            try:
                result = self.comprehensive_analyze_address(address, deal_type)
                results.append(result)
                
                # Track cumulative analysis time
                if "analysis_duration_seconds" in result:
                    total_analysis_time += result["analysis_duration_seconds"]
                    print(f"     🔍 Added {result['analysis_duration_seconds']}s, total now: {total_analysis_time}s")                
                    
                # Enhanced progress reporting
                avg_time_per_property = total_analysis_time / (i + 1) if i > 0 else 0
                remaining_properties = len(addresses) - (i + 1)
                estimated_remaining_time = avg_time_per_property * remaining_properties
                
                print(f"  📊 Progress: {i+1}/{len(addresses)} complete")
                print(f"  ⏱️ Avg time per property: {avg_time_per_property:.1f}s")
                if remaining_properties > 0:
                    print(f"  🔮 Estimated time remaining: {estimated_remaining_time:.0f}s ({estimated_remaining_time/60:.1f} min)")
                
                if progress_callback:
                    progress_callback(i + 1, len(addresses), result)
                
                if (i + 1) % 25 == 0:
                    temp_file = self.work_dir / f"progress_backup_{deal_type.replace('%', 'pct').replace(' ', '_')}_{i+1}.json"
                    with open(temp_file, 'w') as f:
                        json.dump(results, f, indent=2)
                    print(f"📁 Progress saved: {temp_file}")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error analyzing {address}: {e}")
                results.append({
                    "address": address,
                    "deal_type": deal_type,
                    "error": str(e),
                    "analysis_timestamp": datetime.now().isoformat()
            })
        
        # FINAL BATCH SUMMARY
        batch_end_time = time.time()
        total_batch_time = batch_end_time - batch_start_time
        successful = len([r for r in results if "error" not in r])
        
        print(f"\n🎯 BATCH ANALYSIS COMPLETE!")
        print(f"   ⏱️ Total time: {total_batch_time:.1f}s ({total_batch_time/60:.1f} min)")
        print(f"   📊 Properties analyzed: {successful}")
        if successful > 0:
            print(f"   🚄 Average per property: {total_analysis_time/successful:.1f}s")
            timing_data = [r.get('analysis_duration_seconds', 0) for r in results if 'error' not in r and r.get('analysis_duration_seconds', 0) > 0]
            if timing_data:
                print(f"   🏆 Fastest property: {min(timing_data):.1f}s")
                print(f"   🐌 Slowest property: {max(timing_data):.1f}s")
        
        # Sort results by scoring category and points
        if deal_type == "9% LIHTC":
            results.sort(key=lambda x: (
                {"BEST": 4, "GOOD": 3, "MAYBE": 2, "FIRM NO": 1}.get(
                    x.get("scoring", {}).get("category", "UNKNOWN"), 0
                ),
                x.get("scoring", {}).get("total_tdhca_points", 0)
            ), reverse=True)
        else:
            results.sort(key=lambda x: (
                {"BEST": 4, "GOOD": 3, "MAYBE": 2, "FIRM NO": 1}.get(
                    x.get("scoring", {}).get("category", "UNKNOWN"), 0
                ),
                x.get("scoring", {}).get("total_points", 0)
            ), reverse=True)
        
        return results

    def create_fixed_html_report(self, results: List[Dict], deal_type: str = "4% Bond") -> str:
        """
        ENHANCED FIXED: Create rich HTML report with working competition data + comprehensive data sections
    
        Merges:
        - Working TDHCA competition data from fixed version
        - Rich data presentation from original enhanced version  
        - Deal-type specific emphasis for 9% LIHTC vs 4% Bond
        """
    
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        deal_type_safe = deal_type.replace('%', 'pct').replace(' ', '_')
        
        # Calculate summary statistics
        total = len(results)
        successful = len([r for r in results if "error" not in r])
        
        categories = {"BEST": 0, "GOOD": 0, "MAYBE": 0, "FIRM NO": 0}
        federal_benefits = {"qct": 0, "dda": 0, "both": 0}
        
        # Deal-specific statistics
        if deal_type == "9% LIHTC":
            tdhca_scores = {"5pts": 0, "4pts": 0, "3pts": 0, "0pts": 0}
        else:
            bond_scores = {"5pts": 0, "4pts": 0, "3pts": 0, "0-2pts": 0}
        
        for result in results:
            if "error" not in result:
                category = result.get("scoring", {}).get("category", "UNKNOWN")
                if category in categories:
                    categories[category] += 1
                
                qct_dda = result.get("qct_dda_status", {})
                if qct_dda.get("qct_status") and qct_dda.get("dda_status"):
                    federal_benefits["both"] += 1
                elif qct_dda.get("qct_status"):
                    federal_benefits["qct"] += 1
                elif qct_dda.get("dda_status"):
                    federal_benefits["dda"] += 1
                
                if deal_type == "9% LIHTC":
                    tdhca_score = result.get("scoring", {}).get("tdhca_same_tract_score", 0)
                    if tdhca_score >= 5:
                        tdhca_scores["5pts"] += 1
                    elif tdhca_score >= 4:
                        tdhca_scores["4pts"] += 1
                    elif tdhca_score >= 3:
                        tdhca_scores["3pts"] += 1
                    else:
                        tdhca_scores["0pts"] += 1
                else:
                    bond_score = result.get("scoring", {}).get("total_points", 0)
                    if bond_score >= 5:
                        bond_scores["5pts"] += 1
                    elif bond_score >= 4:
                        bond_scores["4pts"] += 1
                    elif bond_score >= 3:
                        bond_scores["3pts"] += 1
                    else:
                        bond_scores["0-2pts"] += 1
    
        # Generate comprehensive HTML content
        html_content = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enhanced Texas LIHTC Analysis Report - {deal_type}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6; color: #333; background: #f8f9fa; padding: 20px;
            }}
            
            .container {{ max-width: 1200px; margin: 0 auto; background: white; box-shadow: 0 0 20px rgba(0,0,0,0.1); border-radius: 10px; overflow: hidden; }}
            
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
            .header h1 {{ font-size: 2.5em; margin-bottom: 10px; font-weight: 700; }}
            .header .subtitle {{ font-size: 1.1em; opacity: 0.9; }}
            
            .summary {{ padding: 30px; background: #f8f9fa; border-bottom: 1px solid #dee2e6; }}
            .summary h2 {{ color: #495057; margin-bottom: 20px; font-size: 1.8em; }}
            
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
            .stat-number {{ font-size: 2.5em; font-weight: bold; color: #667eea; margin-bottom: 5px; }}
            .stat-label {{ color: #6c757d; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }}
            
            .categories-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 30px; }}
            .category-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid; }}
            .category-card.best {{ border-left-color: #28a745; }}
            .category-card.good {{ border-left-color: #007bff; }}
            .category-card.maybe {{ border-left-color: #ffc107; }}
            .category-card.firm-no {{ border-left-color: #dc3545; }}
            
            .scoring-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 30px; }}
            .scoring-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #6f42c1; }}
            
            .results {{ padding: 30px; }}
            .results h2 {{ color: #495057; margin-bottom: 25px; font-size: 1.8em; }}
            
            .property {{ background: white; border: 1px solid #dee2e6; border-radius: 8px; margin-bottom: 20px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
            
            .property-header {{ padding: 20px; border-left: 5px solid; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }}
            .property-header.best {{ border-left-color: #28a745; background: #f8fff9; }}
            .property-header.good {{ border-left-color: #007bff; background: #f8f9ff; }}
            .property-header.maybe {{ border-left-color: #ffc107; background: #fffcf0; }}
            .property-header.firm-no {{ border-left-color: #dc3545; background: #fff5f5; }}
            .property-header.error {{ border-left-color: #6c757d; background: #f8f9fa; }}
            
            .property-title {{ font-size: 1.3em; font-weight: 600; color: #495057; }}
            .property-number {{ font-size: 0.9em; color: #6c757d; font-weight: 400; }}
            
            .property-category {{ padding: 8px 16px; border-radius: 20px; font-size: 0.9em; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
            .category-best {{ background: #d4edda; color: #155724; }}
            .category-good {{ background: #cce7ff; color: #004085; }}
            .category-maybe {{ background: #fff3cd; color: #856404; }}
            .category-firm-no {{ background: #f8d7da; color: #721c24; }}
            .category-error {{ background: #e2e3e5; color: #383d41; }}
            
            .property-details {{ padding: 20px; background: #fafafa; border-top: 1px solid #dee2e6; }}
            .details-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 15px; }}
            
            .detail-section {{ background: white; padding: 12px; border-radius: 6px; border: 1px solid #e9ecef; }}
            .detail-section h4 {{ color: #495057; margin-bottom: 8px; font-size: 0.95em; border-bottom: 2px solid #667eea; padding-bottom: 3px; }}
            
            .detail-item {{ margin-bottom: 6px; display: flex; justify-content: space-between; align-items: flex-start; }}
            .detail-label {{ font-weight: 500; color: #6c757d; flex-shrink: 0; min-width: 85px; font-size: 0.85em; }}
            .detail-value {{ color: #495057; font-weight: 600; text-align: right; flex: 1; font-size: 0.85em; }}
            
            .poverty-indicator {{ padding: 2px 6px; border-radius: 12px; font-size: 0.7em; font-weight: 600; margin-left: 5px; }}
            .poverty-low {{ background: #d4edda; color: #155724; }}
            .poverty-borderline {{ background: #fff3cd; color: #856404; }}
            .poverty-high {{ background: #f8d7da; color: #721c24; }}
            
            .projects-list {{ 
                margin-top: 8px; 
                max-height: 120px; 
                overflow-y: auto; 
                border: 1px solid #e9ecef; 
                border-radius: 4px; 
                background: #f8f9fa; 
                position: relative; 
            }}

            /* Add scroll indicator when content overflows */
            .projects-list::after {{
                content: "⬇ Scroll for more projects";
                position: sticky;
                bottom: 0;
                left: 0;
                right: 0;
                background: linear-gradient(transparent, rgba(248, 249, 250, 0.9));
                text-align: center;
                font-size: 0.65em;
                color: #6c757d;
                padding: 2px 4px;
                font-style: italic;
                display: none;
            }}

            /* Show scroll indicator when there's overflow */
            .projects-list[data-has-overflow="true"]::after {{
                display: block;
            }}

            .projects-list .project-item:last-child {{
                margin-bottom: 20px;
            }}

            .project-item:hover {{
                background-color: rgba(102, 126, 234, 0.1);
            }}
            .project-item {{ padding: 4px 8px; border-bottom: 1px solid #e9ecef; font-size: 0.75em; }}
            .project-name {{ font-weight: 500; color: #495057; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-bottom: 2px; }}
            .project-details {{ color: #6c757d; font-size: 0.85em; }}
            
            .rent-grid {{ display: grid; grid-template-columns: 1fr; gap: 6px; margin-top: 6px; }}
            .rent-item {{ background: #f8f9fa; padding: 6px; border-radius: 4px; font-size: 0.8em; }}
            .rent-label {{ font-weight: 500; color: #6c757d; font-size: 0.75em; }}
            .rent-values {{ font-weight: 600; color: #495057; font-size: 0.8em; }}
            
            .benefits-list {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }}
            .benefit-tag {{ background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.7em; font-weight: 500; }}
            
            .links-section {{ margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; }}
            .link-btn {{ display: inline-flex; align-items: center; padding: 6px 10px; text-decoration: none; border-radius: 4px; font-size: 0.75em; font-weight: 500; transition: all 0.3s; border: none; cursor: pointer; }}
            .google-maps-link {{ background: #4285f4; color: white; }}
            .google-maps-link:hover {{ background: #3367d6; }}
            .apple-maps-link {{ background: #000000; color: white; }}
            .apple-maps-link:hover {{ background: #333333; }}
            .census-data-link {{ background: #28a745; color: white; }}
            .census-data-link:hover {{ background: #218838; }}
            .hud-poverty-link {{ background: #dc3545; color: white; }}
            .hud-poverty-link:hover {{ background: #c82333; }}
            
            .error-message {{ color: #dc3545; font-style: italic; padding: 10px; background: #f8d7da; border-radius: 5px; margin-top: 10px; }}
            
            .footer {{ background: #495057; color: white; text-align: center; padding: 20px; font-size: 0.9em; }}
            .company-name {{ color: #ffffff; font-weight: 600; margin-top: 5px; }}
            
            @media (max-width: 768px) {{
                .property-header {{ flex-direction: column; align-items: flex-start; gap: 10px; }}
                .stats-grid, .categories-grid {{ grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }}
                .details-grid {{ grid-template-columns: 1fr; }}
                .links-section {{ flex-direction: column; }}
            }}
            
            @media print {{
                /* Hide scroll indicators when printing */
                .projects-list::after {{
                    display: none !important;
                }}
                
                /* Show all project content when printing */
                .projects-list {{
                    max-height: none !important;
                    overflow: visible !important;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Enhanced Texas LIHTC Analysis Report</h1>
                <div class="subtitle">{deal_type} Deals - Rich Data + Working Competition Analysis - Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</div>
            </div>
            
            <div class="summary">
                <h2>Executive Summary - {deal_type} Analysis</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{total}</div>
                        <div class="stat-label">Total Properties</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{successful}</div>
                        <div class="stat-label">Successfully Analyzed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{federal_benefits['qct'] + federal_benefits['both']}</div>
                        <div class="stat-label">QCT Qualified</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{federal_benefits['dda'] + federal_benefits['both']}</div>
                        <div class="stat-label">DDA Qualified</div>
                    </div>
                </div>
                
                <h3 style="margin-bottom: 15px; color: #495057;">Project Categories</h3>
                <div class="categories-grid">
                    <div class="category-card best">
                        <div style="font-size: 1.8em; font-weight: bold; color: #28a745;">🥇 {categories['BEST']}</div>
                        <div style="font-size: 0.9em; color: #6c757d;">BEST Projects</div>
                    </div>
                    <div class="category-card good">
                        <div style="font-size: 1.8em; font-weight: bold; color: #007bff;">🥈 {categories['GOOD']}</div>
                        <div style="font-size: 0.9em; color: #6c757d;">GOOD Projects</div>
                    </div>
                    <div class="category-card maybe">
                        <div style="font-size: 1.8em; font-weight: bold; color: #ffc107;">🥉 {categories['MAYBE']}</div>
                        <div style="font-size: 0.9em; color: #6c757d;">MAYBE Projects</div>
                    </div>
                    <div class="category-card firm-no">
                        <div style="font-size: 1.8em; font-weight: bold; color: #dc3545;">❌ {categories['FIRM NO']}</div>
                        <div style="font-size: 0.9em; color: #6c757d;">FIRM NO</div>
                    </div>
                </div>
    """

        # Add deal-specific scoring section
        if deal_type == "9% LIHTC":
            html_content += f"""
                <h3 style="margin-bottom: 15px; color: #495057;">TDHCA Regulatory Scoring (Same Census Tract)</h3>
                <div class="scoring-grid">
                    <div class="scoring-card">
                        <div style="font-size: 1.5em; font-weight: bold; color: #6f42c1;">🎯 {tdhca_scores['5pts']}</div>
                        <div style="font-size: 0.8em; color: #6c757d;">5 Points</div>
                    </div>
                    <div class="scoring-card">
                        <div style="font-size: 1.5em; font-weight: bold; color: #6f42c1;">🎯 {tdhca_scores['4pts']}</div>
                        <div style="font-size: 0.8em; color: #6c757d;">4 Points</div>
                    </div>
                    <div class="scoring-card">
                        <div style="font-size: 1.5em; font-weight: bold; color: #6f42c1;">🎯 {tdhca_scores['3pts']}</div>
                        <div style="font-size: 0.8em; color: #6c757d;">3 Points</div>
                    </div>
                    <div class="scoring-card">
                        <div style="font-size: 1.5em; font-weight: bold; color: #6f42c1;">🎯 {tdhca_scores['0pts']}</div>
                        <div style="font-size: 0.8em; color: #6c757d;">0 Points</div>
                    </div>
                </div>
    """
        else:
            html_content += f"""
                <h3 style="margin-bottom: 15px; color: #495057;">4% Bond Deal Scoring (Opportunity + Competition)</h3>
                <div class="scoring-grid">
                    <div class="scoring-card">
                        <div style="font-size: 1.5em; font-weight: bold; color: #6f42c1;">🎯 {bond_scores['5pts']}</div>
                        <div style="font-size: 0.8em; color: #6c757d;">5 Points</div>
                    </div>
                    <div class="scoring-card">
                        <div style="font-size: 1.5em; font-weight: bold; color: #6f42c1;">🎯 {bond_scores['4pts']}</div>
                        <div style="font-size: 0.8em; color: #6c757d;">4 Points</div>
                    </div>
                    <div class="scoring-card">
                        <div style="font-size: 1.5em; font-weight: bold; color: #6f42c1;">🎯 {bond_scores['3pts']}</div>
                        <div style="font-size: 0.8em; color: #6c757d;">3 Points</div>
                    </div>
                    <div class="scoring-card">
                        <div style="font-size: 1.5em; font-weight: bold; color: #6f42c1;">🎯 {bond_scores['0-2pts']}</div>
                        <div style="font-size: 0.8em; color: #6c757d;">0-2 Points</div>
                    </div>
                </div>
    """

        html_content += """
            </div>
            
            <div class="results">
                <h2>Detailed Property Analysis</h2>
    """

        # Add detailed property results with ALL comprehensive data sections
        for i, result in enumerate(results, 1):
            if "error" in result:
                html_content += f"""
                <div class="property">
                    <div class="property-header error">
                        <div class="property-title">❌ {result['address']} <span class="property-number">({i} of {total})</span></div>
                        <div class="property-category category-error">FAILED</div>
                    </div>
                    <div class="property-details">
                        <div class="error-message">Error: {result['error']}</div>
                    </div>
                </div>
    """
                continue
            
            # Extract all data for property
            scoring = result.get("scoring", {})
            demo = result.get("demographics", {})
            ami = result.get("ami_data", {})
            qct_dda = result.get("qct_dda_status", {})
            coords = result.get("coordinates", {})
            comp_analysis = result.get("competition_analysis", {})
            
            category = scoring.get("category", "UNKNOWN").lower().replace(" ", "-")
            category_display = scoring.get("category", "UNKNOWN")
            
            category_info = {
                "best": {"emoji": "🥇", "class": "best"},
                "good": {"emoji": "🥈", "class": "good"},
                "maybe": {"emoji": "🥉", "class": "maybe"},
                "firm-no": {"emoji": "❌", "class": "firm-no"}
            }
            
            cat_info = category_info.get(category, {"emoji": "❓", "class": "error"})
            
            html_content += f"""
                <div class="property">
                    <div class="property-header {cat_info['class']}">
                        <div class="property-title">{cat_info['emoji']} {result['address']} <span class="property-number">({i} of {total})</span></div>
                        <div class="property-category category-{cat_info['class']}">{category_display}</div>
                    </div>
                    <div class="property-details">
                        <div class="details-grid">
    """
            
            # Deal-specific scoring section with enhanced details
            if deal_type == "9% LIHTC":
                html_content += f"""
                            <div class="detail-section">
                                <h4>🏛️ 9% LIHTC Scoring</h4>
                                <div class="detail-item">
                                    <span class="detail-label">Category:</span>
                                    <span class="detail-value">{category_display}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">TDHCA Same Tract:</span>
                                    <span class="detail-value">{scoring.get('tdhca_same_tract_score', 0)}/5</span>
                                </div>
    """
                
                # Add TDHCA details if available
                if result.get("tdhca_same_tract"):
                    tdhca = result["tdhca_same_tract"]
                    competing_projects = tdhca.get("competing_projects", [])
                    if competing_projects:
                        html_content += f"""
                                <div class="detail-item">
                                    <span class="detail-label">Same Tract Projects:</span>
                                    <span class="detail-value">{len(competing_projects)}</span>
                                </div>
    """
                        if tdhca.get("borderline"):
                            html_content += f"""
                                <div class="detail-item">
                                    <span class="detail-label">Timing Note:</span>
                                    <span class="detail-value" style="font-size: 0.7em;">{tdhca['borderline']}</span>
                                </div>
    """
            else:
                html_content += f"""
                            <div class="detail-section">
                                <h4>🏠 4% Bond Deal Scoring</h4>
                                <div class="detail-item">
                                    <span class="detail-label">Category:</span>
                                    <span class="detail-value">{category_display}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Total Points:</span>
                                    <span class="detail-value">{scoring.get('total_points', 0)}/5</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Opportunity:</span>
                                    <span class="detail-value">{scoring.get('opportunity_score', 0)}/2</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Competition:</span>
                                    <span class="detail-value">{scoring.get('competition_score', 0)}/3</span>
                                </div>
    """
            
            # Add federal benefits if present
            if scoring.get("federal_benefits"):
                html_content += """
                                <div class="detail-item">
                                    <span class="detail-label">Fed. Benefits:</span>
                                </div>
                                <div class="benefits-list">
    """
                for benefit in scoring["federal_benefits"]:
                    html_content += f'<span class="benefit-tag">{benefit}</span>'
                html_content += """
                                </div>
    """
            
            html_content += """
                            </div>
    """
            
            # ENHANCED: Market Analysis Section with Rich Competition Data (Working TDHCA data!)
            if comp_analysis:
                html_content += f"""
                            <div class="detail-section">
                                <h4>🎯 Market Analysis (ENHANCED!)</h4>
                                <div class="detail-item">
                                    <span class="detail-label">Radius:</span>
                                    <span class="detail-value">{comp_analysis['search_radius_miles']} mi</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Competing:</span>
                                    <span class="detail-value">{comp_analysis['projects_within_radius']} projects</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Saturation:</span>
                                    <span class="detail-value">{comp_analysis['saturation_analysis']['saturation_level']}</span>
                                </div>
    """
                
                if comp_analysis.get('nearest_project'):
                    nearest = comp_analysis['nearest_project']
                    html_content += f"""
                                <div class="detail-item">
                                    <span class="detail-label">Nearest:</span>
                                    <span class="detail-value">{nearest['distance']} mi</span>
                                </div>
    """
                
                # ENHANCED: Show comprehensive nearby projects list (working TDHCA data!)
                nearby_projects = comp_analysis.get('nearby_projects', [])
                if nearby_projects:
                    display_projects = nearby_projects[:8]  # Show more projects
                    html_content += """
                                <div class="detail-item" style="margin-bottom: 8px;">
                                    <span class="detail-label">Nearby Projects:</span>
                                </div>
                                <div class="projects-list">
    """
                    for project in display_projects:
                        project_name = project.get('project_name', 'Unknown')[:35]  # Truncate for display
                        total_units = project.get('total_units', 0)
                        distance = project.get('distance', 0)
                        year_display = project.get('year_display', '')
                        
                        unit_text = f"{total_units} units" if total_units > 0 else "units unknown"
                        year_text = f", {year_display}" if year_display and year_display != "N/A" else ""
                        
                        html_content += f"""
                                    <div class="project-item">
                                        <div class="project-name" title="{project.get('project_name', 'Unknown')}">{project_name}</div>
                                        <div class="project-details">{unit_text}, {distance} mi{year_text}</div>
                                    </div>
    """
                    
                    if len(nearby_projects) > 8:
                        html_content += f"""
                                    <div class="project-item" style="font-style: italic; color: #6c757d;">
                                        <span>... and {len(nearby_projects) - 8} more projects</span>
                                    </div>
    """
                    
                    html_content += """
                                </div>
    """
                
                html_content += """
                            </div>
    """
            
                # Enhanced Demographics Section with Borderline Poverty Alert
                if demo and "error" not in demo:
                # Get 4-Person 50% AMI from AMI data
                    four_person_ami = "N/A"
                if ami and ami.get('income_limits', {}).get('50_pct', {}).get('4p'):
                    four_person_ami = f"${ami['income_limits']['50_pct']['4p']:,}"
    
                    # Define income_display
                    median_income = demo.get('median_household_income', 0)
                    income_display = f"${median_income:,}" if median_income > 0 else "Unavailable"
                    
                # Enhanced poverty indicator logic with potential scoring
                poverty_rate = demo.get('poverty_rate', 100)
                if poverty_rate < 20.0:
                    poverty_class = "poverty-low"
                    poverty_text = "✅ LOW"
                    potential_message = ""
                elif 19.0 <= poverty_rate <= 21.0:
                    poverty_class = "poverty-borderline" 
                    poverty_text = "⚠️ BORDERLINE"
                    
                    # Calculate potential scoring if verified as low poverty
                    current_opportunity = scoring.get('opportunity_score', 0)
                    potential_opportunity = 2  # Would get full opportunity points
                    potential_total = potential_opportunity + scoring.get('competition_score', 0)
                    
                    potential_message = f'''
                            <div class="detail-item" style="background: #fff3cd; padding: 8px; border-radius: 4px; margin-top: 8px;">
                                <span class="detail-label" style="color: #856404; font-weight: bold;">🎯 POTENTIAL:</span>
                                <span class="detail-value" style="color: #856404; font-size: 0.8em;">
                                    If HUD verifies &lt;20%: {potential_total}/5 points
                                </span>
                            </div>'''
                else:
                    poverty_class = "poverty-high"
                    poverty_text = "❌ HIGH"
                    potential_message = ""
                
                html_content += f"""
                        <div class="detail-section">
                            <h4>🏘️ Demographics</h4>
                            <div class="detail-item">
                                <span class="detail-label">Poverty Rate:</span>
                                <span class="detail-value">
                                    {poverty_rate}%
                                    <span class="poverty-indicator {poverty_class}">{poverty_text}</span>
                                </span>
                            </div>
                            {potential_message}
                            <div class="detail-item">
                                <span class="detail-label">Med. Income:</span>
                                <span class="detail-value">{income_display}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Pop. (Tract):</span>
                                <span class="detail-value">{demo.get('total_population', 'N/A'):,}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">4P 50% AMI:</span>
                                <span class="detail-value">{four_person_ami}</span>
                            </div>
                        </div>
    """
            
            # RESTORED: Enhanced HUD Area Data Section with Rent Limits Grid
            if ami:
                html_content += f"""
                            <div class="detail-section">
                                <h4>🏠 HUD Area Data</h4>
                                <div class="detail-item">
                                    <span class="detail-label">Area:</span>
                                    <span class="detail-value" style="font-size: 0.75em;">{ami['hud_area_name']}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Type:</span>
                                    <span class="detail-value">{'Metro' if ami['metro'] else 'Non-Metro'}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Med. AMI:</span>
                                    <span class="detail-value">${ami['median_ami']:,}</span>
                                </div>
                                
                                <div class="rent-grid">
                                    <div class="rent-item">
                                        <div class="rent-label">1BR Rent Limits</div>
                                        <div class="rent-values">${ami['rent_limits']['60_pct']['1br']:,} @ 60% / ${ami['rent_limits']['80_pct']['1br']:,} @ 80%</div>
                                    </div>
                                    <div class="rent-item">
                                        <div class="rent-label">2BR Rent Limits</div>
                                        <div class="rent-values">${ami['rent_limits']['60_pct']['2br']:,} @ 60% / ${ami['rent_limits']['80_pct']['2br']:,} @ 80%</div>
                                    </div>
                                    <div class="rent-item">
                                        <div class="rent-label">3BR Rent Limits</div>
                                        <div class="rent-values">${ami['rent_limits']['60_pct']['3br']:,} @ 60% / ${ami['rent_limits']['80_pct']['3br']:,} @ 80%</div>
                                    </div>
                                </div>
                            </div>
    """
            
            # RESTORED: Location Section with Navigation Links
            if coords:
                encoded_address = urllib.parse.quote_plus(result['address'])
                
                google_maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
                apple_maps_url = f"https://maps.apple.com/?q={encoded_address}"
                
                census_tract = result.get('census_tract', '')
                census_data_url = None
                if census_tract and len(census_tract) >= 11:
                    census_data_url = f"https://censusreporter.org/profiles/14000US{census_tract}/"
                
                hud_poverty_url = "https://www.huduser.gov/portal/maps/hcv/home.html"
                
                html_content += f"""
                            <div class="detail-section">
                                <h4>📍 Location</h4>
                                <div class="detail-item">
                                    <span class="detail-label">Coordinates:</span>
                                    <span class="detail-value">{coords['latitude']:.4f}, {coords['longitude']:.4f}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Census Tract:</span>
                                    <span class="detail-value">{census_tract}</span>
                                </div>
                                
                                <div class="links-section">
                                    <a href="{google_maps_url}" target="_blank" class="link-btn google-maps-link">🗺️ Google Maps</a>
                                    <a href="{apple_maps_url}" target="_blank" class="link-btn apple-maps-link">🍎 Apple Maps</a>
    """
                
                if census_data_url:
                    html_content += f"""                                <a href="{census_data_url}" target="_blank" class="link-btn census-data-link">📊 Census Data</a>
    """
                
                html_content += f"""                                <a href="{hud_poverty_url}" target="_blank" class="link-btn hud-poverty-link">🏘️ HUD Poverty Map</a>
                                </div>
                            </div>
    """
            
            html_content += """
                        </div>
                    </div>
                </div>
    """
        
        html_content += f"""
            </div>
            
            <div class="footer">
                Enhanced Texas LIHTC Analysis Report - {deal_type} | Rich Data + Working Competition Analysis | Generated by Enhanced Fixed Texas Analyzer | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                <div class="company-name">Structured Consultants LLC</div>
            </div>
        </div>
        
        <script>
        // Detect overflow in project lists and show scroll indicators
        document.addEventListener('DOMContentLoaded', function() {{
            const projectsLists = document.querySelectorAll('.projects-list');
            
            projectsLists.forEach(function(list) {{
                // Check if content overflows
                if (list.scrollHeight > list.clientHeight) {{
                    list.setAttribute('data-has-overflow', 'true');
                    
                    // Hide indicator when scrolled to bottom
                    list.addEventListener('scroll', function() {{
                        if (list.scrollTop + list.clientHeight >= list.scrollHeight - 5) {{
                            list.setAttribute('data-has-overflow', 'false');
                        }} else {{
                            list.setAttribute('data-has-overflow', 'true');
                        }}
                    }});
                }}
            }});
        }});
        </script>

    </body>
    </html>"""
        
        # Save enhanced HTML report
        html_file = self.work_dir / f"enhanced_fixed_texas_analysis_{deal_type_safe}_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n🌐 ENHANCED FIXED HTML report saved: {html_file}")
        return str(html_file)


# Example usage with FIXED functionality
if __name__ == "__main__":
    # Initialize FIXED analyzer
    census_api_key = "06ece0121263282cd9ffd753215b007b8f9a3dfc"
    
    # File paths
    hud_ami_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx"
    tdhca_project_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
    
    analyzer = FixedTexasAnalyzer(
        census_api_key=census_api_key,
        hud_ami_file_path=hud_ami_file,
        tdhca_project_file_path=tdhca_project_file
    )
    
    # Test addresses
    test_addresses = [
        "6053 Bellfort St Houston, TX 77033",
        "2904 Greens Rd, Houston, TX 77032",
        "3206 Spring Stuebner Rd, Spring, TX 77389",
        "814 Autumnwood Dr Houston",
        "4810 S Acres Dr, Houston, TX, 77048, USA",
        "822 W Greens Rd, Houston, TX 77060",
        "2110 Aldine Western Rd, Houston, TX 77038",
        "4810 S Acres Dr, Houston, TX 77048",
    ]
    
    print(f"\n🧪 Testing FIXED Enhanced Analyzer with separated scoring systems...")
    
    # Test both deal types
    for deal_type in ["4% Bond", "9% LIHTC"]:
        print(f"\n{'='*60}")
        print(f"TESTING {deal_type} DEALS")
        print(f"{'='*60}")
        
        # Run FIXED analysis
        results = analyzer.batch_analyze_addresses(test_addresses, deal_type=deal_type)
        
        # Generate FIXED HTML report
        html_report = analyzer.create_fixed_html_report(results, deal_type=deal_type)
        
        # Print FIXED summary
        successful = len([r for r in results if "error" not in r])
        categories = {"BEST": 0, "GOOD": 0, "MAYBE": 0, "FIRM NO": 0}
        
        for result in results:
            if "error" not in result:
                category = result.get("scoring", {}).get("category", "UNKNOWN")
                if category in categories:
                    categories[category] += 1
        
        print(f"\n📊 {deal_type} SUMMARY:")
        print(f"   ✅ Successfully analyzed: {successful}/{len(test_addresses)}")
        print(f"   🥇 BEST: {categories['BEST']}")
        print(f"   🥈 GOOD: {categories['GOOD']}")
        print(f"   🥉 MAYBE: {categories['MAYBE']}")
        print(f"   ❌ FIRM NO: {categories['FIRM NO']}")
        print(f"   🌐 FIXED HTML report: {html_report}")
    
    print("\n✅ FIXED Enhanced Texas LIHTC Analysis Complete!")
    print("🔧 Key Fixes Applied:")
    print("   • Competition data now uses TDHCA dataset (364 Houston projects)")
    print("   • Scoring systems separated: 9% LIHTC vs 4% Bond deals")
    print("   • Fixed column name mapping for TDHCA data")
    print("   • Added deal_type parameter for appropriate analysis")
    print("   • Competition analysis now working with real project data")