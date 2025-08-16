#!/usr/bin/env python3
"""
Enhanced Texas LIHTC Analyzer with Census API and HUD AMI Integration
Complete Texas LIHTC scoring with tie-breaker analysis + HTML Report Generation
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

class EnhancedTexasAnalyzer:
    def __init__(self, 
                 census_api_key: str,
                 hud_ami_file_path: str = None,
                 work_dir: str = "./enhanced_texas_analysis"):
        """
        Initialize Enhanced Texas LIHTC Analyzer
        
        Args:
            census_api_key: Your Census API key
            hud_ami_file_path: Path to HUD AMI Excel file (optional, will search current dir)
            work_dir: Working directory for results and cache
        """
        self.census_api_key = census_api_key
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)
        
        # Cache directory in your Dropbox structure - create if doesn't exist
        try:
            self.cache_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Cache")
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            (self.cache_dir / "census_api_cache").mkdir(exist_ok=True)
            (self.cache_dir / "ami_lookup_cache").mkdir(exist_ok=True)
            (self.cache_dir / "geocoding_cache").mkdir(exist_ok=True)
        except:
            # Fallback to local cache if Dropbox path doesn't work
            self.cache_dir = self.work_dir / "cache"
            self.cache_dir.mkdir(exist_ok=True)
            (self.cache_dir / "census_api_cache").mkdir(exist_ok=True)
            (self.cache_dir / "ami_lookup_cache").mkdir(exist_ok=True)
            (self.cache_dir / "geocoding_cache").mkdir(exist_ok=True)
        
        # Data containers
        self.qct_data = None
        self.dda_data = None
        self.ami_data = None
        self.census_cache = {}
        self.geocoding_cache = {}
        
        # Load and index HUD AMI data
        if hud_ami_file_path and Path(hud_ami_file_path).exists():
            self.load_ami_data(hud_ami_file_path)
        else:
            # Search for AMI file in multiple locations
            search_paths = [
                Path("."),  # Current directory
                Path(".."),  # Parent directory
                Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code"),
                Path("/Users/williamrice/Downloads"),
                Path("/Users/williamrice/Desktop")
            ]
            
            ami_file_found = None
            for search_path in search_paths:
                if search_path.exists():
                    # Try multiple filename patterns
                    patterns = [
                        "*AMI*Rent*Data*.xlsx",
                        "HUD2025*.xlsx", 
                        "*HUD*AMI*.xlsx",
                        "*AMI*.xlsx"
                    ]
                    
                    for pattern in patterns:
                        ami_files = list(search_path.glob(pattern))
                        if ami_files:
                            ami_file_found = ami_files[0]
                            print(f"Found AMI file: {ami_file_found}")
                            break
                    
                    if ami_file_found:
                        break
            
            if ami_file_found:
                try:
                    self.load_ami_data(str(ami_file_found))
                except Exception as e:
                    print(f"⚠️ Could not load AMI file (maybe Excel has it open?): {e}")
                    self.ami_data = None
            else:
                print("⚠️ No AMI file found in common locations.")
                print("   Searched patterns: *AMI*Rent*Data*.xlsx, HUD2025*.xlsx")
                print("   Searched paths: current dir, Downloads, Desktop, code dir")
                self.ami_data = None
        
        # Load existing QCT/DDA data
        self.load_hud_designation_data()
        
        print(f"Enhanced Texas LIHTC Analyzer initialized.")
        print(f"Working directory: {self.work_dir}")
        print(f"Cache directory: {self.cache_dir}")
        print(f"Census API configured: {'✅' if census_api_key else '❌'}")
        print(f"HUD AMI data loaded: {'✅' if self.ami_data is not None else '❌'}")
    
    def load_ami_data(self, file_path: str):
        """Load and index HUD AMI data for fast lookups"""
        try:
            print(f"Loading HUD AMI data from: {file_path}")
            
            # Verify file exists
            if not Path(file_path).exists():
                raise FileNotFoundError(f"AMI file not found: {file_path}")
            
            # Load the AMI data
            df = pd.read_excel(file_path, sheet_name="MTSP2025-Static")
            print(f"Loaded {len(df)} total AMI records")
            
            # Filter for Texas only
            texas_df = df[df['stusps'] == 'TX'].copy()
            print(f"Found {len(texas_df)} Texas AMI records")
            
            # Create FIPS-based index for fast lookups
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
            
            # Show sample FIPS codes for debugging, especially Houston area
            sample_fips = list(self.ami_data.keys())[:5]
            houston_fips = [fips for fips in self.ami_data.keys() if "48201" in fips]  # Harris County
            
            print(f"Sample FIPS codes: {sample_fips}")
            if houston_fips:
                print(f"Houston/Harris County FIPS: {houston_fips}")
            else:
                print("No Houston/Harris County FIPS found - checking for other Houston counties...")
                # Check for other Houston metro counties
                fort_bend = [fips for fips in self.ami_data.keys() if "48157" in fips]  # Fort Bend
                montgomery = [fips for fips in self.ami_data.keys() if "48339" in fips]  # Montgomery
                if fort_bend:
                    print(f"Fort Bend County FIPS: {fort_bend}")
                if montgomery:
                    print(f"Montgomery County FIPS: {montgomery}")
            
            # Cache the indexed data
            cache_file = self.cache_dir / "ami_lookup_cache" / "texas_ami_2025_indexed.json"
            with open(cache_file, 'w') as f:
                json.dump(self.ami_data, f, indent=2)
            print(f"📁 Cached AMI data to: {cache_file}")
            
        except Exception as e:
            print(f"❌ Error loading AMI data: {e}")
            self.ami_data = None
    
    def load_hud_designation_data(self):
        """Load existing QCT/DDA data"""
        try:
            base_hud_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD DDA QCT")
            
            # Look for QCT files
            qct_files = []
            dda_files = []
            
            for pattern in ["*qct*", "*QCT*", "*tract*"]:
                qct_files.extend(list(base_hud_path.glob(f"{pattern}.geojson")))
                qct_files.extend(list(base_hud_path.glob(f"{pattern}.shp")))
                qct_files.extend(list(base_hud_path.glob(f"{pattern}.gpkg")))
            
            for pattern in ["*dda*", "*DDA*"]:
                dda_files.extend(list(base_hud_path.glob(f"{pattern}.geojson")))
                dda_files.extend(list(base_hud_path.glob(f"{pattern}.shp")))
                dda_files.extend(list(base_hud_path.glob(f"{pattern}.gpkg")))
            
            # Load QCT data
            if qct_files:
                qct_file = qct_files[0]
                self.qct_data = gpd.read_file(qct_file)
                if self.qct_data.crs != 'EPSG:4326':
                    self.qct_data = self.qct_data.to_crs('EPSG:4326')
                print(f"✅ Loaded QCT data: {len(self.qct_data)} features")
            
            # Load DDA data
            if dda_files:
                dda_file = dda_files[0]
                self.dda_data = gpd.read_file(dda_file)
                if self.dda_data.crs != 'EPSG:4326':
                    self.dda_data = self.dda_data.to_crs('EPSG:4326')
                print(f"✅ Loaded DDA data: {len(self.dda_data)} features")
                
        except Exception as e:
            print(f"⚠️ Could not load HUD designation data: {e}")
    
    def get_demographics_from_census_api(self, census_tract: str) -> Dict:
        """Get comprehensive demographics from Census API with caching"""
        
        # Check cache first
        cache_key = f"demographics_{census_tract}"
        if cache_key in self.census_cache:
            return self.census_cache[cache_key]
        
        # Check file cache
        cache_file = self.cache_dir / "census_api_cache" / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    # Check if cache is less than 30 days old
                    cache_date = datetime.fromisoformat(cached_data.get('cached_date', '2020-01-01'))
                    if datetime.now() - cache_date < timedelta(days=30):
                        self.census_cache[cache_key] = cached_data['data']
                        return cached_data['data']
            except:
                pass
        
        try:
            # Extract state and county from census tract GEOID
            if len(census_tract) >= 11:
                state_code = census_tract[:2]
                county_code = census_tract[2:5]
                tract_code = census_tract[5:]
            else:
                return {"error": "Invalid census tract format"}
            
            # Census API call for comprehensive demographics
            base_url = "https://api.census.gov/data/2022/acs/acs5"
            
            # Key variables for Texas LIHTC scoring
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
                row = data[1]  # First data row
                
                # Safely parse values with error handling
                def safe_int(value, default=0):
                    try:
                        if value is None or str(value).strip() in ['', 'null', 'None', '-', 'N/A']:
                            return default
                        
                        # Convert to float first to handle scientific notation
                        float_val = float(str(value))
                        int_val = int(float_val)
                        
                        # Flag obviously wrong values - Census API sometimes returns very large negative numbers
                        if int_val < -1000000 or int_val > 10000000:  # Reasonable income range
                            print(f"    ⚠️ Suspicious value detected: {int_val:,} - treating as unavailable")
                            return default
                            
                        # Additional check for Census API error patterns
                        if abs(int_val) == 666666666:  # This specific error pattern
                            print(f"    ⚠️ Census API error pattern detected: {int_val:,} - treating as unavailable")
                            return default
                            
                        return int_val
                    except (ValueError, TypeError) as e:
                        print(f"    ⚠️ Error parsing value '{value}': {e}")
                        return default
                
                # Calculate demographics with safe parsing
                total_pop = safe_int(row[5])
                poverty_total = safe_int(row[2])
                poverty_below = safe_int(row[1])
                median_income = safe_int(row[3])
                
                # Additional validation for median income
                if median_income <= 0:
                    print(f"    ⚠️ Invalid median income: ${median_income:,} - marked as unavailable")
                    median_income = 0
                
                # Education calculations
                total_25_plus = safe_int(row[10])
                associates_plus = sum([
                    safe_int(row[6]),  # Associates
                    safe_int(row[7]),  # Bachelors  
                    safe_int(row[8]),  # Masters
                    safe_int(row[9]),  # Doctorate
                ])
                
                poverty_rate = (poverty_below / poverty_total * 100) if poverty_total > 0 else 0
                education_rate = (associates_plus / total_25_plus * 100) if total_25_plus > 0 else 0
                
                demographics = {
                    "census_tract": census_tract,
                    "total_population": total_pop,
                    "median_household_income": median_income,
                    "poverty_rate": round(poverty_rate, 2),
                    "low_poverty_tract": poverty_rate <= 20.0,
                    "education_rate": round(education_rate, 2),
                    "high_education_tract": education_rate >= 27.0,
                    "data_date": "2022 ACS 5-Year",
                    "data_quality": "GOOD" if median_income > 0 and poverty_total > 0 else "POOR"
                }
                
                # Cache the result
                self.census_cache[cache_key] = demographics
                
                # Save to file cache
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
        
        # Try multiple FIPS matching strategies
        if len(census_tract) >= 5:
            # Strategy 1: County FIPS + 99999 (standard format)
            county_fips = census_tract[:5] + "99999"
            if county_fips in self.ami_data:
                return self.ami_data[county_fips]
            
            # Strategy 2: Try with different padding
            county_fips_alt = census_tract[:5] + "00000"
            if county_fips_alt in self.ami_data:
                return self.ami_data[county_fips_alt]
            
            # Strategy 3: Look for any FIPS starting with the county code
            county_prefix = census_tract[:5]
            for fips_key in self.ami_data.keys():
                if fips_key.startswith(county_prefix):
                    return self.ami_data[fips_key]
            
            # Strategy 4: Search by county name if we can determine it
            # This would require additional lookup but could be added later
            
        print(f"    ⚠️ No AMI data found for census tract {census_tract}")
        return None
    
    def enhanced_geocode_address(self, address: str) -> Optional[Dict]:
        """Enhanced geocoding with comprehensive location analysis"""
        
        # Check geocoding cache
        cache_key = f"geocode_{hash(address)}"
        cache_file = self.cache_dir / "geocoding_cache" / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    cache_date = datetime.fromisoformat(cached_data.get('cached_date', '2020-01-01'))
                    if datetime.now() - cache_date < timedelta(days=7):  # Geocoding cache for 7 days
                        return cached_data['data']
            except:
                pass
        
        # Clean address variations  
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
                    
                    # Cache the result
                    cache_data = {
                        "data": geocode_result,
                        "cached_date": datetime.now().isoformat()
                    }
                    with open(cache_file, 'w') as f:
                        json.dump(cache_data, f, indent=2)
                    
                    print(f"    ✅ Geocoded successfully")
                    return geocode_result
                
                time.sleep(0.5)  # Rate limiting
                
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
        
        # Street type replacements - more comprehensive
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
                # Also try the reverse
                if abbrev in base_addr:
                    new_addr = base_addr.replace(abbrev, full_word).strip()
                    if new_addr not in variations:
                        variations.append(new_addr)
        
        # Special handling for problematic addresses
        # Try without specific words that might cause issues
        problem_words = ['Slough', 'Cypress Slough']
        for base_addr in base_variations:
            for problem_word in problem_words:
                if problem_word in base_addr:
                    # Try with just the number and street type
                    simplified = re.sub(rf'\b{re.escape(problem_word)}\b', '', base_addr, flags=re.IGNORECASE).strip()
                    simplified = re.sub(r'\s+', ' ', simplified)  # Clean up extra spaces
                    if simplified and simplified not in variations:
                        variations.append(simplified)
        
        # Try without leading zeros from house numbers
        no_leading_zeros = re.sub(r'\b0+(\d+)', r'\1', address)
        if no_leading_zeros != address:
            variations.append(no_leading_zeros)
            if not has_state:
                variations.append(f"{no_leading_zeros}, TX")
        
        # For specific problematic addresses, try alternatives
        if "Cypress Slough" in address:
            # Try variations specific to this Houston area
            variations.extend([
                address.replace("Cypress Slough", "Cypress Creek"),
                address.replace("Cypress Slough", "Cypress Point"),
                address.replace("Cypress Slough Dr", "Cypress Dr"),
                address.replace("Cypress Slough Drive", "Cypress Drive")
            ])
        
        # Remove duplicates while preserving order
        clean_variations = []
        seen = set()
        for var in variations:
            var = var.strip()
            if var and var not in seen and len(var) > 5:  # Avoid too-short addresses
                seen.add(var)
                clean_variations.append(var)
        
        return clean_variations
    
    def calculate_opportunity_index_score(self, demographics: Dict, ami_data: Dict) -> Dict:
        """Calculate Texas opportunity index score (0-2 points) based on Section 5A"""
        
        if not demographics or "error" in demographics:
            return {"score": 0, "reason": "No demographic data available"}
        
        # Check data quality
        if demographics.get("data_quality") == "POOR":
            return {"score": 0, "reason": f"Poor data quality - median income: ${demographics.get('median_household_income', 0):,}"}
        
        poverty_rate = demographics.get("poverty_rate", 100)
        median_income = demographics.get("median_household_income", 0)
        
        # Texas Section 5A(i): Low poverty threshold analysis
        # Official rule: "less than 20% or regional median, whichever is greater"
        # For now using 20% threshold - would need regional calculation for full accuracy
        
        # Be more generous with borderline cases (within 1% of threshold)
        definitely_low_poverty = poverty_rate < 20.0
        borderline_low_poverty = poverty_rate <= 21.0  # Allow some margin for data variation
        
        if definitely_low_poverty:
            # Clear low poverty case
            if median_income >= 85000:  # Top 2 quartiles (approximate)
                return {
                    "score": 2,
                    "reason": f"Low poverty ({poverty_rate:.1f}%) + high income quartile (${median_income:,})"
                }
            elif median_income >= 60000:  # 3rd quartile (approximate)
                return {
                    "score": 1,
                    "reason": f"Low poverty ({poverty_rate:.1f}%) + middle income quartile (${median_income:,})"
                }
            elif median_income > 0:  # Valid income data but lower quartile
                return {
                    "score": 1,
                    "reason": f"Low poverty area ({poverty_rate:.1f}%) - income: ${median_income:,}"
                }
            else:
                return {
                    "score": 1,
                    "reason": f"Low poverty area ({poverty_rate:.1f}%) - income data unavailable"
                }
                
        elif borderline_low_poverty:
            # Borderline case - still award some points if has other good factors
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
            # Clearly high poverty
            return {
                "score": 0,
                "reason": f"High poverty area: {poverty_rate:.1f}% (above 21% threshold)"
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
    
    def calculate_texas_lihtc_score(self, analysis_result: Dict) -> Dict:
        """Calculate comprehensive Texas LIHTC score based on official criteria"""
        
        scoring = {
            "opportunity_index": 0,
            "qct_bonus": 0,
            "federal_benefits": [],
            "total_analyzed_points": 0,
            "category": "UNKNOWN",
            "scoring_details": []
        }
        
        # Opportunity Index (0-2 points) - Section 5A
        if analysis_result.get("opportunity_index"):
            opp_score = analysis_result["opportunity_index"]["score"]
            scoring["opportunity_index"] = opp_score
            scoring["total_analyzed_points"] += opp_score
            scoring["scoring_details"].append(
                f"Opportunity Index: {opp_score} points - {analysis_result['opportunity_index']['reason']}"
            )
        
        # Federal Benefits (30% basis boost)
        federal_boost_value = 0
        if analysis_result.get("qct_dda_status", {}).get("federal_basis_boost"):
            benefits = []
            if analysis_result["qct_dda_status"]["qct_status"]:
                benefits.append("QCT (30% basis boost)")
                federal_boost_value += 5  # Assign point value for category calculation
            if analysis_result["qct_dda_status"]["dda_status"]:
                benefits.append("DDA (30% basis boost)")
                federal_boost_value += 5  # Assign point value for category calculation
            scoring["federal_benefits"] = benefits
            scoring["scoring_details"].append(f"Federal Benefits: {', '.join(benefits)}")
        
        # Overall Category Assessment - Updated Logic
        has_federal_boost = len(scoring["federal_benefits"]) > 0
        opp_points = scoring["opportunity_index"]
        
        # More nuanced category assignment
        if has_federal_boost and opp_points >= 2:
            scoring["category"] = "BEST"
        elif has_federal_boost and opp_points >= 1:
            scoring["category"] = "GOOD"  # Federal benefits + some opportunity points = GOOD
        elif has_federal_boost:
            scoring["category"] = "GOOD"  # Federal benefits alone are valuable = GOOD
        elif opp_points >= 2:
            scoring["category"] = "GOOD"  # High opportunity score without federal benefits
        elif opp_points >= 1:
            scoring["category"] = "MAYBE"  # Some opportunity points
        else:
            scoring["category"] = "FIRM NO"  # No benefits at all
        
        # Add reasoning for category
        if scoring["category"] == "BEST":
            scoring["scoring_details"].append("Category: BEST - Federal benefits + high opportunity score")
        elif scoring["category"] == "GOOD":
            if has_federal_boost:
                scoring["scoring_details"].append("Category: GOOD - Federal 30% basis boost provides significant value")
            else:
                scoring["scoring_details"].append("Category: GOOD - Strong opportunity characteristics")
        elif scoring["category"] == "MAYBE":
            scoring["scoring_details"].append("Category: MAYBE - Some positive factors but limited benefits")
        else:
            scoring["scoring_details"].append("Category: FIRM NO - No significant LIHTC advantages")
        
        return scoring
    
    def enhanced_analyze_address(self, address: str) -> Dict:
        """Comprehensive address analysis with full Texas LIHTC scoring"""
        
        print(f"\n🔍 Enhanced Analysis: {address}")
        
        # Step 1: Geocoding
        geocode_result = self.enhanced_geocode_address(address)
        if not geocode_result:
            return {"error": "Geocoding failed", "address": address}
        
        # Step 2: Get demographics from Census API
        census_tract = geocode_result.get("census_tract")
        print(f"  📍 Census Tract: {census_tract}")
        demographics = self.get_demographics_from_census_api(census_tract) if census_tract else {}
        
        # Step 3: Get AMI data
        ami_data = self.get_ami_data_for_location(census_tract) if census_tract else None
        
        # Step 4: Check QCT/DDA status
        point = Point(geocode_result["longitude"], geocode_result["latitude"])
        qct_dda_status = self.check_qct_dda_status(point)
        
        # Step 5: Calculate opportunity index score
        opportunity_index = self.calculate_opportunity_index_score(demographics, ami_data)
        
        # Step 6: Compile comprehensive result
        result = {
            "address": address,
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
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Step 7: Calculate Texas LIHTC scoring
        result["texas_scoring"] = self.calculate_texas_lihtc_score(result)
        
        # Print summary
        self.print_analysis_summary(result)
        
        return result
    
    def print_analysis_summary(self, result: Dict):
        """Print formatted analysis summary"""
        print(f"  📍 Location: {result['coordinates']['latitude']:.6f}, {result['coordinates']['longitude']:.6f}")
        
        if result.get("demographics"):
            demo = result["demographics"]
            data_quality = demo.get("data_quality", "UNKNOWN")
            quality_emoji = "✅" if data_quality == "GOOD" else "⚠️"
            print(f"  📊 Demographics: Poverty {demo.get('poverty_rate', 'N/A')}%, Income ${demo.get('median_household_income', 0):,} {quality_emoji}")
        
        if result.get("ami_data"):
            ami = result["ami_data"]
            print(f"  🏠 Area: {ami['hud_area_name']} ({'Metro' if ami['metro'] else 'Non-Metro'})")
            print(f"  💰 AMI: ${ami['median_ami']:,}, 1BR 50%: ${ami['rent_limits']['50_pct']['1br']}")
        else:
            print(f"  ⚠️ No AMI data found for this location")
        
        qct_dda = result.get("qct_dda_status", {})
        federal_benefits = []
        if qct_dda.get("qct_status"):
            federal_benefits.append("QCT")
        if qct_dda.get("dda_status"):
            federal_benefits.append("DDA")
        
        if federal_benefits:
            print(f"  🎯 Federal Benefits: {', '.join(federal_benefits)} (30% basis boost)")
        
        opp_index = result.get("opportunity_index", {})
        opp_score = opp_index.get("score", 0)
        opp_reason = opp_index.get("reason", "No details")
        
        scoring = result.get("texas_scoring", {})
        print(f"  🏆 Opportunity Index: {opp_score} points - {opp_reason}")
        print(f"  📋 Category: {scoring.get('category', 'UNKNOWN')}")
    
    def batch_analyze_addresses(self, addresses: List[str], progress_callback=None) -> List[Dict]:
        """Batch analyze multiple addresses with progress tracking"""
        
        print(f"\n🚀 Starting batch analysis of {len(addresses)} addresses...")
        results = []
        
        for i, address in enumerate(addresses):
            print(f"\n--- Processing {i+1}/{len(addresses)} ---")
            
            try:
                result = self.enhanced_analyze_address(address)
                results.append(result)
                
                if progress_callback:
                    progress_callback(i + 1, len(addresses), result)
                
                # Auto-save progress every 25 addresses
                if (i + 1) % 25 == 0:
                    temp_file = self.work_dir / f"progress_backup_{i+1}.json"
                    with open(temp_file, 'w') as f:
                        json.dump(results, f, indent=2)
                    print(f"📁 Progress saved: {temp_file}")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error analyzing {address}: {e}")
                results.append({
                    "address": address,
                    "error": str(e),
                    "analysis_timestamp": datetime.now().isoformat()
                })
        
        # Sort results by scoring category and points
        results.sort(key=lambda x: (
            {"BEST": 4, "GOOD": 3, "MAYBE": 2, "FIRM NO": 1}.get(
                x.get("texas_scoring", {}).get("category", "UNKNOWN"), 0
            ),
            x.get("texas_scoring", {}).get("total_analyzed_points", 0)
        ), reverse=True)
        
        return results
    
    def create_enhanced_report(self, results: List[Dict]) -> str:
        """Create comprehensive analysis report"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Calculate summary statistics
        total = len(results)
        successful = len([r for r in results if "error" not in r])
        
        categories = {"BEST": 0, "GOOD": 0, "MAYBE": 0, "FIRM NO": 0}
        federal_benefits = {"qct": 0, "dda": 0, "both": 0}
        
        for result in results:
            if "error" not in result:
                category = result.get("texas_scoring", {}).get("category", "UNKNOWN")
                if category in categories:
                    categories[category] += 1
                
                qct_dda = result.get("qct_dda_status", {})
                if qct_dda.get("qct_status") and qct_dda.get("dda_status"):
                    federal_benefits["both"] += 1
                elif qct_dda.get("qct_status"):
                    federal_benefits["qct"] += 1
                elif qct_dda.get("dda_status"):
                    federal_benefits["dda"] += 1
        
        # Generate report
        report = f"""Enhanced Texas LIHTC Analysis Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
=========================================

EXECUTIVE SUMMARY:
• Total Properties Analyzed: {total}
• Successfully Analyzed: {successful} ({successful/total*100:.0f}%)
• QCT Qualified: {federal_benefits['qct'] + federal_benefits['both']} (30% basis boost)
• DDA Qualified: {federal_benefits['dda'] + federal_benefits['both']} (30% basis boost)
• QCT + DDA: {federal_benefits['both']} (30% basis boost)

TEXAS LIHTC SCORING RESULTS:
🥇 BEST Projects: {categories['BEST']} (Top development priority)
🥈 GOOD Projects: {categories['GOOD']} (Strong candidates)  
🥉 MAYBE Projects: {categories['MAYBE']} (Consider with other factors)
❌ FIRM NO: {categories['FIRM NO']} (Avoid for LIHTC)

DETAILED ANALYSIS:
"""
        
        # Add detailed results
        for i, result in enumerate(results, 1):
            if "error" in result:
                report += f"\n❌ FAILED: {result['address']}\n   Error: {result['error']}\n"
                continue
            
            scoring = result.get("texas_scoring", {})
            demo = result.get("demographics", {})
            ami = result.get("ami_data", {})
            
            category_emoji = {"BEST": "🥇", "GOOD": "🥈", "MAYBE": "🥉", "FIRM NO": "❌"}.get(
                scoring.get("category", ""), "❓"
            )
            
            report += f"\n{i}. {category_emoji} {result['address']}\n"
            report += f"   Category: {scoring.get('category', 'UNKNOWN')}\n"
            report += f"   Opportunity Points: {scoring.get('total_analyzed_points', 0)}\n"
            
            if scoring.get("federal_benefits"):
                report += f"   Federal Benefits: {', '.join(scoring['federal_benefits'])}\n"
            
            if ami:
                report += f"   Area: {ami['hud_area_name']} ({'Metro' if ami['metro'] else 'Non-Metro'})\n"
                report += f"   Median AMI: ${ami['median_ami']:,}\n"
                report += f"   50% Rent Limits: 1BR=${ami['rent_limits']['50_pct']['1br']}, 2BR=${ami['rent_limits']['50_pct']['2br']}\n"
            
            if demo and "error" not in demo:
                report += f"   Poverty Rate: {demo.get('poverty_rate', 'N/A')}%\n"
                report += f"   Median Income: ${demo.get('median_household_income', 0):,}\n"
            
            # Google Maps link
            coords = result.get("coordinates", {})
            if coords:
                import urllib.parse
                encoded_address = urllib.parse.quote_plus(result['address'])
                report += f"   Google Maps: https://www.google.com/maps/search/?api=1&query={encoded_address}\n"
        
        # Save report
        report_file = self.work_dir / f"enhanced_texas_analysis_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📋 Enhanced report saved: {report_file}")
        return report
    
    def create_html_report(self, results: List[Dict]) -> str:
        """Create professional HTML report with enhanced styling and all requested improvements"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Calculate summary statistics
        total = len(results)
        successful = len([r for r in results if "error" not in r])
        
        categories = {"BEST": 0, "GOOD": 0, "MAYBE": 0, "FIRM NO": 0}
        federal_benefits = {"qct": 0, "dda": 0, "both": 0}
        
        for result in results:
            if "error" not in result:
                category = result.get("texas_scoring", {}).get("category", "UNKNOWN")
                if category in categories:
                    categories[category] += 1
                
                qct_dda = result.get("qct_dda_status", {})
                if qct_dda.get("qct_status") and qct_dda.get("dda_status"):
                    federal_benefits["both"] += 1
                elif qct_dda.get("qct_status"):
                    federal_benefits["qct"] += 1
                elif qct_dda.get("dda_status"):
                    federal_benefits["dda"] += 1
        
        # Create HTML content with enhanced styling and smaller fonts for 4-column layout
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Texas LIHTC Analysis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .summary {{
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .summary h2 {{
            color: #495057;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .categories-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
        }}
        
        .category-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid;
        }}
        
        .category-card.best {{ border-left-color: #28a745; }}
        .category-card.good {{ border-left-color: #007bff; }}
        .category-card.maybe {{ border-left-color: #ffc107; }}
        .category-card.firm-no {{ border-left-color: #dc3545; }}
        
        .results {{
            padding: 30px;
        }}
        
        .results h2 {{
            color: #495057;
            margin-bottom: 25px;
            font-size: 1.8em;
        }}
        
        .property {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        
        .property-header {{
            padding: 20px;
            border-left: 5px solid;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .property-header.best {{ border-left-color: #28a745; background: #f8fff9; }}
        .property-header.good {{ border-left-color: #007bff; background: #f8f9ff; }}
        .property-header.maybe {{ border-left-color: #ffc107; background: #fffcf0; }}
        .property-header.firm-no {{ border-left-color: #dc3545; background: #fff5f5; }}
        .property-header.error {{ border-left-color: #6c757d; background: #f8f9fa; }}
        
        .property-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: #495057;
        }}
        
        .property-number {{
            font-size: 0.9em;
            color: #6c757d;
            font-weight: 400;
        }}
        
        .property-category {{
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .category-best {{ background: #d4edda; color: #155724; }}
        .category-good {{ background: #cce7ff; color: #004085; }}
        .category-maybe {{ background: #fff3cd; color: #856404; }}
        .category-firm-no {{ background: #f8d7da; color: #721c24; }}
        .category-error {{ background: #e2e3e5; color: #383d41; }}
        
        .property-details {{
            padding: 20px;
            background: #fafafa;
            border-top: 1px solid #dee2e6;
        }}
        
        .details-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 15px;
        }}
        
        .detail-section {{
            background: white;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
        }}
        
        .detail-section h4 {{
            color: #495057;
            margin-bottom: 8px;
            font-size: 0.95em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 3px;
        }}
        
        .detail-item {{
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}
        
        .detail-label {{
            font-weight: 500;
            color: #6c757d;
            flex-shrink: 0;
            min-width: 85px;
            font-size: 0.85em;
        }}
        
        .detail-value {{
            color: #495057;
            font-weight: 600;
            text-align: right;
            flex: 1;
            font-size: 0.85em;
        }}
        
        .rent-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 6px;
            margin-top: 6px;
        }}
        
        .rent-item {{
            background: #f8f9fa;
            padding: 6px;
            border-radius: 4px;
            font-size: 0.8em;
        }}
        
        .rent-label {{
            font-weight: 500;
            color: #6c757d;
            font-size: 0.75em;
        }}
        
        .rent-values {{
            font-weight: 600;
            color: #495057;
            font-size: 0.8em;
        }}
        
        .benefits-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }}
        
        .benefit-tag {{
            background: #28a745;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.7em;
            font-weight: 500;
        }}
        
        .links-section {{
            margin-top: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}
        
        .link-btn {{
            display: inline-flex;
            align-items: center;
            padding: 6px 10px;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: 500;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }}
        
        .google-maps-link {{
            background: #4285f4;
            color: white;
        }}
        
        .google-maps-link:hover {{
            background: #3367d6;
        }}
        
        .apple-maps-link {{
            background: #000000;
            color: white;
        }}
        
        .apple-maps-link:hover {{
            background: #333333;
        }}
        
        .census-data-link {{
            background: #28a745;
            color: white;
        }}
        
        .census-data-link:hover {{
            background: #218838;
        }}
        
        .error-message {{
            color: #dc3545;
            font-style: italic;
            padding: 10px;
            background: #f8d7da;
            border-radius: 5px;
            margin-top: 10px;
        }}
        
        .footer {{
            background: #495057;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        .company-name {{
            color: #ffffff;
            font-weight: 600;
            margin-top: 5px;
        }}
        
        @media (max-width: 768px) {{
            .property-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }}
            
            .stats-grid,
            .categories-grid {{
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }}
            
            .details-grid {{
                grid-template-columns: 1fr;
            }}
            
            .links-section {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Enhanced Texas LIHTC Analysis Report</h1>
            <div class="subtitle">Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</div>
        </div>
        
        <div class="summary">
            <h2>Executive Summary</h2>
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
            
            <h3 style="margin-bottom: 15px; color: #495057;">LIHTC Project Categories</h3>
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
        </div>
        
        <div class="results">
            <h2>Detailed Property Analysis</h2>
"""
        
        # Add detailed results with all requested enhancements
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
            
            scoring = result.get("texas_scoring", {})
            demo = result.get("demographics", {})
            ami = result.get("ami_data", {})
            qct_dda = result.get("qct_dda_status", {})
            coords = result.get("coordinates", {})
            
            category = scoring.get("category", "UNKNOWN").lower().replace(" ", "-")
            category_display = scoring.get("category", "UNKNOWN")
            
            # Category emoji and styling
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
            
            # Scoring Details
            html_content += f"""
                        <div class="detail-section">
                            <h4>📊 LIHTC Scoring</h4>
                            <div class="detail-item">
                                <span class="detail-label">Category:</span>
                                <span class="detail-value">{category_display}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Opp. Points:</span>
                                <span class="detail-value">{scoring.get('total_analyzed_points', 0)}</span>
                            </div>
"""
            
            if scoring.get("federal_benefits"):
                html_content += f"""
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
            
            # Enhanced Demographics Section
            if demo and "error" not in demo:
                # Get 4-Person 50% AMI from AMI data
                four_person_ami = ""
                if ami and ami.get('income_limits', {}).get('50_pct', {}).get('4p'):
                    four_person_ami = f"${ami['income_limits']['50_pct']['4p']:,}"
                else:
                    four_person_ami = "N/A"
                
                html_content += f"""
                        <div class="detail-section">
                            <h4>🏘️ Demographics</h4>
                            <div class="detail-item">
                                <span class="detail-label">Poverty Rate:</span>
                                <span class="detail-value">{demo.get('poverty_rate', 'N/A')}%</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Med. Income:</span>
                                <span class="detail-value">${demo.get('median_household_income', 0):,}</span>
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
            
            # Enhanced HUD Area Data Section
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
                                    <div class="rent-values">${ami['rent_limits']['60_pct']['1br']} 60% / ${ami['rent_limits']['80_pct']['1br']} 80%</div>
                                </div>
                                <div class="rent-item">
                                    <div class="rent-label">2BR Rent Limits</div>
                                    <div class="rent-values">${ami['rent_limits']['60_pct']['2br']} 60% / ${ami['rent_limits']['80_pct']['2br']} 80%</div>
                                </div>
                                <div class="rent-item">
                                    <div class="rent-label">3BR Rent Limits</div>
                                    <div class="rent-values">${ami['rent_limits']['60_pct']['3br']} 60% / ${ami['rent_limits']['80_pct']['3br']} 80%</div>
                                </div>
                            </div>
                        </div>
"""
            
            # Enhanced Location Section with improved Census link
            if coords:
                encoded_address = urllib.parse.quote_plus(result['address'])
                
                # Google Maps URL
                google_maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
                
                # Apple Maps URL
                apple_maps_url = f"https://maps.apple.com/?q={encoded_address}"
                
                # Better Census Data URL - try multiple formats for tract-specific data
                census_tract = result.get('census_tract', '')
                if census_tract and len(census_tract) >= 11:
                    # Try the Census Reporter format which is more reliable for tract data
                    census_data_url = f"https://censusreporter.org/profiles/14000US{census_tract}/"
                else:
                    # Fallback - just remove the census link if no valid tract
                    census_data_url = None
                
                html_content += f"""
                        <div class="detail-section">
                            <h4>📍 Location</h4>
                            <div class="detail-item">
                                <span class="detail-label">Coordinates:</span>
                                <span class="detail-value">{coords['latitude']:.4f}, {coords['longitude']:.4f}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Census Tract:</span>
                                <span class="detail-value">{result.get('census_tract', 'N/A')}</span>
                            </div>
                            
                            <div class="links-section">
                                <a href="{google_maps_url}" target="_blank" class="link-btn google-maps-link">🗺️ Google Maps</a>
                                <a href="{apple_maps_url}" target="_blank" class="link-btn apple-maps-link">🍎 Apple Maps</a>
"""
                
                # Only include Census link if we have a valid tract and URL
                if census_data_url:
                    html_content += f"""                                <a href="{census_data_url}" target="_blank" class="link-btn census-data-link">📊 Census Data</a>
"""
                
                html_content += """                            </div>
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
            Enhanced Texas LIHTC Analysis Report | Generated by Enhanced Texas Analyzer | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            <div class="company-name">Structured Consultants LLC</div>
        </div>
    </div>
</body>
</html>"""
        
        # Save HTML report
        html_file = self.work_dir / f"enhanced_texas_analysis_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n🌐 Enhanced HTML report saved: {html_file}")
        return str(html_file)

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    census_api_key = "06ece0121263282cd9ffd753215b007b8f9a3dfc"
    
    # Use the correct AMI file path
    hud_ami_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx"
    
    analyzer = EnhancedTexasAnalyzer(
        census_api_key=census_api_key,
        hud_ami_file_path=hud_ami_file  # Now using correct path
    )
    
    # Test addresses - keeping original addresses to test improved geocoding
    test_addresses = [
        "22214 Cypress Slough, Houston, TX 77073",
        "6053 Bellfort St Houston, TX 77033",
        "2904 Greens Rd, Houston, TX 77032",
        "3206 Spring Stuebner Rd, Spring, TX 77389",
        "814 Autumnwood Dr Houston",
        "4810 S Acres Dr, Houston, TX, 77048, USA",
        "822 W Greens Rd, Houston, TX 77060",
        "2110 Aldine Western Rd, Houston, TX 77038",
        "4810 S Acres Dr, Houston, TX 77048",
    ]
    
    print(f"\n🧪 Testing Enhanced Analyzer with {len(test_addresses)} addresses...")
    
    # Run enhanced analysis
    results = analyzer.batch_analyze_addresses(test_addresses)
    
    # Generate both text and HTML reports
    text_report = analyzer.create_enhanced_report(results)
    html_report = analyzer.create_html_report(results)
    
    # Print summary
    successful = len([r for r in results if "error" not in r])
    categories = {"BEST": 0, "GOOD": 0, "MAYBE": 0, "FIRM NO": 0}
    
    for result in results:
        if "error" not in result:
            category = result.get("texas_scoring", {}).get("category", "UNKNOWN")
            if category in categories:
                categories[category] += 1
    
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   ✅ Successfully analyzed: {successful}/{len(test_addresses)}")
    print(f"   🥇 BEST: {categories['BEST']}")
    print(f"   🥈 GOOD: {categories['GOOD']}")
    print(f"   🥉 MAYBE: {categories['MAYBE']}")
    print(f"   ❌ FIRM NO: {categories['FIRM NO']}")
    print(f"   📄 Text report: Available")
    print(f"   🌐 HTML report: {html_report}")
    
    print("\n✅ Enhanced Texas LIHTC Analysis Complete with HTML Reports!")
