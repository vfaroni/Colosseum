#!/usr/bin/env python3
"""
Comprehensive Texas QCT/DDA Analyzer - All 4 HUD Datasets
Uses proper industry-standard logic for Metro QCT, Non-Metro QCT, Metro DDA, Non-Metro DDA

Based on CLAUDE.md notes:
- Metro QCT (7,519 tracts): Census tract-based, metro areas only
- Non-Metro QCT (983 tracts): Census tract-based, non-metro areas only  
- Metro DDA (2,612 ZIPs): ZIP code-based, metro areas only
- Non-Metro DDA (105 counties): County-based, non-metro areas only

Correct methodology for LIHTC analysis with proper AMI source assignment
"""

import pandas as pd
import requests
import json
import os
from typing import Dict, Optional, Tuple

class ComprehensiveTexasQCTDDAAnalyzer:
    """Complete Texas QCT/DDA analyzer using all 4 HUD datasets"""
    
    def __init__(self, data_path: str = None):
        """Initialize with path to HUD data"""
        if data_path is None:
            data_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
        
        self.data_path = data_path
        
        # All 4 datasets as per CLAUDE.md
        self.metro_qct_data = None      # Census tract-based
        self.nonmetro_qct_data = None   # Census tract-based
        self.metro_dda_data = None      # ZIP code-based
        self.nonmetro_dda_data = None   # County-based
        
        self.load_all_four_datasets()
    
    def load_all_four_datasets(self):
        """Load all 4 HUD QCT/DDA datasets with proper industry logic"""
        
        print("Loading all 4 HUD QCT/DDA datasets...")
        
        # 1. Metro QCT (7,519 tracts) - Census tract-based
        try:
            metro_qct_file = os.path.join(self.data_path, "qct_data_2025.xlsx")
            if os.path.exists(metro_qct_file):
                print(f"Loading Metro QCT data from: {metro_qct_file}")
                self.metro_qct_data = pd.read_excel(metro_qct_file)
                # Filter to just Metro areas (exclude Non-Metro)
                if 'Metro_Area' in self.metro_qct_data.columns:
                    self.metro_qct_data = self.metro_qct_data[
                        self.metro_qct_data['Metro_Area'] == 'Metro'
                    ].copy()
                print(f"Loaded {len(self.metro_qct_data)} Metro QCT census tracts")
            else:
                print(f"❌ Metro QCT file not found: {metro_qct_file}")
        except Exception as e:
            print(f"❌ Error loading Metro QCT data: {e}")
        
        # 2. Non-Metro QCT (983 tracts) - Census tract-based
        try:
            nonmetro_qct_file = os.path.join(self.data_path, "QCT2025.csv")
            if os.path.exists(nonmetro_qct_file):
                print(f"Loading Non-Metro QCT data from: {nonmetro_qct_file}")
                self.nonmetro_qct_data = pd.read_csv(nonmetro_qct_file)
                # Filter to just Non-Metro areas
                if 'METRO_NONMET_IND' in self.nonmetro_qct_data.columns:
                    self.nonmetro_qct_data = self.nonmetro_qct_data[
                        self.nonmetro_qct_data['METRO_NONMET_IND'] == 'N'
                    ].copy()
                print(f"Loaded {len(self.nonmetro_qct_data)} Non-Metro QCT census tracts")
            else:
                print(f"❌ Non-Metro QCT file not found: {nonmetro_qct_file}")
        except Exception as e:
            print(f"❌ Error loading Non-Metro QCT data: {e}")
        
        # 3. Metro DDA (2,612 ZIPs) - ZIP code-based  
        try:
            metro_dda_file = os.path.join(self.data_path, "2025-DDAs-Data-Used-to-Designate.xlsx")
            if os.path.exists(metro_dda_file):
                print(f"Loading Metro DDA data from: {metro_dda_file}")
                self.metro_dda_data = pd.read_excel(metro_dda_file)
                print(f"Loaded {len(self.metro_dda_data)} Metro DDA ZIP areas")
            else:
                print(f"❌ Metro DDA file not found: {metro_dda_file}")
        except Exception as e:
            print(f"❌ Error loading Metro DDA data: {e}")
        
        # 4. Non-Metro DDA (105 counties) - County-based
        try:
            nonmetro_dda_file = os.path.join(self.data_path, "nonmetro_dda_2025.csv")
            if os.path.exists(nonmetro_dda_file):
                print(f"Loading Non-Metro DDA data from: {nonmetro_dda_file}")
                self.nonmetro_dda_data = pd.read_csv(nonmetro_dda_file)
                print(f"Loaded {len(self.nonmetro_dda_data)} Non-Metro DDA counties")
            else:
                print(f"❌ Non-Metro DDA file not found: {nonmetro_dda_file}")
        except Exception as e:
            print(f"❌ Error loading Non-Metro DDA data: {e}")
    
    def get_census_tract_and_zip(self, lat: float, lon: float) -> Dict:
        """Get both census tract and ZIP code for coordinates"""
        
        result = {
            'census_tract': None,
            'zip_code': None,
            'county': None,
            'state': None
        }
        
        # Get census tract using Census Geocoding API
        try:
            url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
            params = {
                "x": lon,
                "y": lat,
                "benchmark": "Public_AR_Current",
                "vintage": "Current_Current",
                "format": "json"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('result') and data['result'].get('geographies'):
                geogs = data['result']['geographies']
                
                # Extract census tract
                if 'Census Tracts' in geogs and geogs['Census Tracts']:
                    tract_info = geogs['Census Tracts'][0]
                    result['census_tract'] = tract_info.get('GEOID')
                    result['county'] = tract_info.get('COUNTY')
                    result['state'] = tract_info.get('STATE')
                
                # Extract ZIP code from ZCTA
                if 'Zip Code Tabulation Areas' in geogs and geogs['Zip Code Tabulation Areas']:
                    zcta_info = geogs['Zip Code Tabulation Areas'][0]
                    result['zip_code'] = zcta_info.get('ZCTA5')
        
        except Exception as e:
            print(f"Census API error for {lat}, {lon}: {e}")
        
        # Fallback: Use PositionStack API for ZIP if Census failed
        if not result['zip_code']:
            try:
                url = "http://api.positionstack.com/v1/reverse"
                params = {
                    "access_key": "41b80ed51d92978904592126d2bb8f7e",
                    "query": f"{lat},{lon}",
                    "limit": 1
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data.get('data') and len(data['data']) > 0:
                    location = data['data'][0]
                    result['zip_code'] = location.get('postal_code')
                    if not result['county']:
                        result['county'] = location.get('county')
                        
            except Exception as e:
                print(f"PositionStack API error for {lat}, {lon}: {e}")
        
        return result

    def analyze_qct_status(self, census_tract: str, county: str, state: str = "48") -> Dict:
        """Analyze QCT status using both Metro and Non-Metro datasets"""
        
        result = {
            'is_qct': False,
            'qct_type': None,
            'ami_source': None,
            'poverty_rate': None,
            'income_limit': None
        }
        
        if not census_tract:
            return result
        
        # Check combined QCT dataset (includes both Metro and Non-Metro)
        if self.metro_qct_data is not None:
            # Use tract_id column which appears to be the full FIPS code
            metro_match = self.metro_qct_data[
                (self.metro_qct_data['tract_id'].astype(str) == str(census_tract)) &
                (self.metro_qct_data['qct'] == 1)  # Only QCT tracts
            ]
            
            if len(metro_match) > 0:
                match = metro_match.iloc[0]
                # Determine if Metro or Non-Metro based on 'metro' column
                is_metro = match.get('metro', 0) == 1
                
                result.update({
                    'is_qct': True,
                    'qct_type': 'Metro QCT' if is_metro else 'Non-Metro QCT',
                    'ami_source': 'Metro AMI' if is_metro else 'Non-Metro AMI',
                    'poverty_rate': match.get('pov_rate_22', match.get('pov_rate_21', 0)),
                    'income_limit': match.get('adj_inc_lim_22', match.get('adj_inc_lim_21', 0))
                })
                return result
        
        # Check Non-Metro QCT CSV as backup (tract-based)
        if self.nonmetro_qct_data is not None:
            nonmetro_match = self.nonmetro_qct_data[
                self.nonmetro_qct_data['fips'].astype(str) == str(census_tract)
            ]
            
            if len(nonmetro_match) > 0:
                result.update({
                    'is_qct': True,
                    'qct_type': 'Non-Metro QCT',
                    'ami_source': 'Non-Metro AMI',
                    'poverty_rate': None,  # Not available in this dataset
                    'income_limit': None   # Not available in this dataset
                })
                return result
        
        return result

    def analyze_dda_status(self, zip_code: str, county: str, state: str = "TX") -> Dict:
        """Analyze DDA status using both Metro and Non-Metro datasets"""
        
        result = {
            'is_dda': False,
            'dda_type': None,
            'ami_source': None,
            'safmr': None,
            'lihtc_rent': None
        }
        
        # Check Metro DDA first (ZIP-based)
        if zip_code and self.metro_dda_data is not None:
            metro_match = self.metro_dda_data[
                (self.metro_dda_data['ZIP Code Tabulation Area (ZCTA)'].astype(str) == str(zip_code).zfill(5)) &
                (self.metro_dda_data['2025 SDDA (1=SDDA)'] == 1)  # Only actual DDAs
            ]
            
            if len(metro_match) > 0:
                match = metro_match.iloc[0]
                result.update({
                    'is_dda': True,
                    'dda_type': 'Metro DDA',
                    'ami_source': 'Metro AMI',
                    'safmr': match.get('2024 Final 40th Percentile 2-Bedroom SAFMR', 0),
                    'lihtc_rent': match.get('LIHTC Maximum Rent (1/12 of 30% of 120% of VLIL)', 0)
                })
                return result
        
        # Check Non-Metro DDA (county-based)
        if county and self.nonmetro_dda_data is not None:
            # Clean county name for matching
            county_clean = county.replace(' County', '').strip().upper()
            
            nonmetro_match = self.nonmetro_dda_data[
                (self.nonmetro_dda_data['state'].str.upper() == 'TEXAS') &
                (self.nonmetro_dda_data['county'].str.replace(' County', '').str.strip().str.upper() == county_clean) &
                (self.nonmetro_dda_data['nonmetro_dda'] == True)
            ]
            
            if len(nonmetro_match) > 0:
                result.update({
                    'is_dda': True,
                    'dda_type': 'Non-Metro DDA',
                    'ami_source': 'Non-Metro AMI',
                    'safmr': None,  # Not available in county-based data
                    'lihtc_rent': None   # Not available in county-based data
                })
                return result
        
        return result

    def comprehensive_analysis(self, lat: float, lon: float) -> Dict:
        """Complete QCT/DDA analysis using all 4 HUD datasets"""
        
        # Get location information
        location = self.get_census_tract_and_zip(lat, lon)
        
        # Analyze QCT status
        qct_analysis = self.analyze_qct_status(
            location['census_tract'],
            location['county'],
            location['state']
        )
        
        # Analyze DDA status  
        dda_analysis = self.analyze_dda_status(
            location['zip_code'],
            location['county']
        )
        
        # Determine overall LIHTC eligibility and AMI source
        is_qct = qct_analysis['is_qct']
        is_dda = dda_analysis['is_dda']
        basis_boost_eligible = is_qct or is_dda
        
        # Determine AMI source (industry-standard logic)
        if is_qct and is_dda:
            # Dual designation - use QCT's AMI source for consistency
            ami_source = qct_analysis['ami_source']
            status = f"{qct_analysis['qct_type']} + {dda_analysis['dda_type']}"
        elif is_qct:
            ami_source = qct_analysis['ami_source']
            status = qct_analysis['qct_type']
        elif is_dda:
            ami_source = dda_analysis['ami_source']
            status = dda_analysis['dda_type']
        else:
            ami_source = self._determine_default_ami_source(location['county'])
            status = "Not QCT/DDA"
        
        return {
            # Location data
            'latitude': lat,
            'longitude': lon,
            'census_tract': location['census_tract'],
            'zip_code': location['zip_code'],
            'county': location['county'],
            'state': location['state'],
            
            # QCT analysis
            'qct_status': 'QCT' if is_qct else 'Not QCT',
            'qct_type': qct_analysis['qct_type'],
            'poverty_rate': qct_analysis.get('poverty_rate'),
            
            # DDA analysis
            'dda_status': 'DDA' if is_dda else 'Not DDA',
            'dda_type': dda_analysis['dda_type'],
            'safmr': dda_analysis.get('safmr'),
            'lihtc_rent': dda_analysis.get('lihtc_rent'),
            
            # LIHTC determination
            'lihtc_eligible': basis_boost_eligible,
            'status_combined': status,
            'ami_source': ami_source,
            
            # Summary
            'analysis_method': 'All 4 HUD Datasets',
            'datasets_used': 'Metro QCT + Non-Metro QCT + Metro DDA + Non-Metro DDA'
        }

    def _determine_default_ami_source(self, county: str) -> str:
        """Determine default AMI source for non-QCT/DDA locations"""
        # This would typically be based on MSA/HUD Metro Area definitions
        # For now, use simple heuristic - major counties are Metro
        major_metro_counties = {
            'Harris', 'Dallas', 'Tarrant', 'Bexar', 'Travis', 'Collin',
            'Denton', 'Fort Bend', 'Williamson', 'Montgomery'
        }
        
        if county and any(metro in county for metro in major_metro_counties):
            return 'Metro AMI'
        else:
            return 'Non-Metro AMI'

    def analyze_texas_sites(self, sites_df: pd.DataFrame) -> pd.DataFrame:
        """Analyze multiple Texas sites using comprehensive QCT/DDA analysis"""
        
        results = []
        
        for idx, site in sites_df.iterrows():
            if idx % 10 == 0:
                print(f"Analyzing site {idx+1}/{len(sites_df)}")
            
            # Get coordinates
            lat = site.get('Corrected_Latitude', site.get('Latitude'))
            lon = site.get('Corrected_Longitude', site.get('Longitude'))
            
            if pd.isna(lat) or pd.isna(lon):
                # Skip sites without coordinates
                result = {
                    'original_index': site.get('original_index', idx),
                    'address': site.get('Address', site.get('site_address', 'Unknown')),
                    'error': 'No coordinates available'
                }
            else:
                try:
                    result = self.comprehensive_analysis(lat, lon)
                    result.update({
                        'original_index': site.get('original_index', idx),
                        'address': site.get('Address', site.get('site_address', 'Unknown'))
                    })
                except Exception as e:
                    result = {
                        'original_index': site.get('original_index', idx),
                        'address': site.get('Address', site.get('site_address', 'Unknown')),
                        'error': str(e)
                    }
            
            results.append(result)
        
        return pd.DataFrame(results)

def main():
    """Test the analyzer with Texas coordinates"""
    
    print("🚀 COMPREHENSIVE TEXAS QCT/DDA ANALYZER TEST")
    print("=" * 60)
    
    analyzer = ComprehensiveTexasQCTDDAAnalyzer()
    
    # Test Tyler site specifically
    tyler_lat, tyler_lon = 32.319885, -95.329824
    
    print(f"\n🎯 TESTING TYLER SITE: {tyler_lat}, {tyler_lon}")
    result = analyzer.comprehensive_analysis(tyler_lat, tyler_lon)
    
    print(f"📊 TYLER ANALYSIS RESULTS:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    # Test a few more Texas locations
    test_sites = [
        {"name": "Houston", "lat": 29.7604, "lon": -95.3698},
        {"name": "Dallas", "lat": 32.7767, "lon": -96.7970},
        {"name": "Austin", "lat": 30.2672, "lon": -97.7431},
        {"name": "Rural East Texas", "lat": 32.0, "lon": -94.5}
    ]
    
    print(f"\n📋 TESTING ADDITIONAL TEXAS LOCATIONS:")
    for site in test_sites:
        print(f"\n🏠 {site['name']}: {site['lat']}, {site['lon']}")
        result = analyzer.comprehensive_analysis(site['lat'], site['lon'])
        print(f"  Status: {result['status_combined']}")
        print(f"  AMI Source: {result['ami_source']}")
        print(f"  Basis Boost: {result['lihtc_eligible']}")

if __name__ == "__main__":
    main()