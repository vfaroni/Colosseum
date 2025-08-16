#!/usr/bin/env python3
"""
Fixed QCT/DDA Analyzer - Loads both Excel tabs properly
"""

import pandas as pd
import requests
import json
import time
from datetime import datetime
import sys
sys.path.append('/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code')

class FixedQCTDDAAnalyzer:
    """Fixed QCT/DDA analyzer that loads both Excel tabs"""
    
    def __init__(self):
        self.load_qct_data()
        self.load_dda_data()
    
    def load_qct_data(self):
        """Load QCT data from both Excel tabs"""
        qct_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data/qct_data_2025.xlsx"
        
        print("Loading QCT data from both tabs...")
        
        # Load both tabs
        tab1 = pd.read_excel(qct_file, sheet_name='AL-MO')  # States 1-29
        tab2 = pd.read_excel(qct_file, sheet_name='MT-WY')  # States 30-72 (includes Texas 48)
        
        # Combine both tabs
        self.qct_data = pd.concat([tab1, tab2], ignore_index=True)
        
        print(f"✅ Combined QCT data loaded: {len(self.qct_data)} total tracts")
        
        # Verify Texas data
        texas_data = self.qct_data[self.qct_data['state'] == 48]
        texas_qcts = texas_data[texas_data['qct'] == 1]
        print(f"✅ Texas verification: {len(texas_data)} total tracts, {len(texas_qcts)} QCT designated")
    
    def load_dda_data(self):
        """Load DDA data"""
        base_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
        
        # Load Metro DDA data
        self.metro_dda_data = pd.read_excel(f"{base_path}/2025-DDAs-Data-Used-to-Designate.xlsx")
        print(f"✅ Metro DDA data loaded: {len(self.metro_dda_data)} ZIP areas")
        
        # Load Non-Metro DDA data
        try:
            self.nonmetro_dda_data = pd.read_csv(f"{base_path}/nonmetro_dda_2025.csv")
            print(f"✅ Non-Metro DDA data loaded: {len(self.nonmetro_dda_data)} counties")
        except:
            self.nonmetro_dda_data = pd.DataFrame()
            print("⚠️ Non-Metro DDA data not found")
    
    def get_census_tract(self, lat, lon):
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
            
            if response.status_code == 200:
                data = response.json()
                if data.get('result', {}).get('geographies', {}).get('Census Tracts'):
                    tract_info = data['result']['geographies']['Census Tracts'][0]
                    return {
                        'geoid': tract_info.get('GEOID', ''),
                        'state_fips': tract_info.get('STATE', ''),
                        'county_fips': tract_info.get('COUNTY', ''),
                        'tract_code': tract_info.get('TRACT', '')
                    }
            
            return None
            
        except Exception as e:
            print(f"Census tract lookup error: {e}")
            return None
    
    def check_qct_status(self, tract_geoid):
        """Check if tract is QCT designated using proper tract matching"""
        if not tract_geoid or len(tract_geoid) != 11:
            return False, "Invalid tract ID"
        
        # Parse tract GEOID (format: SSCCCTTTTTT)
        state_fips = int(tract_geoid[:2])
        county_fips = int(tract_geoid[2:5])
        tract_number = float(tract_geoid[5:]) / 100  # Convert to decimal
        
        # Look up in QCT database
        matching_tracts = self.qct_data[
            (self.qct_data['state'] == state_fips) &
            (self.qct_data['county'] == county_fips) &
            (abs(self.qct_data['tract'] - tract_number) < 0.01)
        ]
        
        if len(matching_tracts) > 0:
            tract_record = matching_tracts.iloc[0]
            if tract_record['qct'] == 1:
                return True, "QCT Designated"
            else:
                return False, "Not QCT"
        
        return False, "Tract not found in database"
    
    def check_dda_status(self, zip_code):
        """Check if ZIP is DDA designated"""
        if not zip_code:
            return False, "No ZIP code"
        
        # Check Metro DDA using correct column name
        zip_str = str(zip_code).zfill(5)
        zip_col = 'ZIP Code Tabulation Area (ZCTA)'  # Correct column name from earlier check
        
        if zip_col in self.metro_dda_data.columns:
            matching_ddas = self.metro_dda_data[
                self.metro_dda_data[zip_col].astype(str) == zip_str
            ]
            
            if len(matching_ddas) > 0:
                dda_record = matching_ddas.iloc[0]
                # Check if designated as DDA (column: '2025 SDDA (1=SDDA)')
                if '2025 SDDA (1=SDDA)' in dda_record and dda_record['2025 SDDA (1=SDDA)'] == 1:
                    return True, "Metro DDA"
        
        return False, "Not DDA"
    
    def get_zip_from_address(self, lat, lon):
        """Get ZIP code using alternative method"""
        try:
            # Try reverse geocoding with different service
            import requests
            url = f"https://geocoding.geo.census.gov/geocoder/locations/coordinates"
            params = {
                'x': lon,
                'y': lat,
                'benchmark': 'Public_AR_Current',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('result', {}).get('addressMatches'):
                    address_info = data['result']['addressMatches'][0]
                    return address_info.get('addressComponents', {}).get('zip', None)
            
            return None
            
        except:
            return None
    
    def analyze_site(self, lat, lon, city="Unknown"):
        """Complete QCT/DDA analysis for a single site"""
        result = {
            'lat': lat,
            'lon': lon,
            'city': city,
            'census_tract': None,
            'zip_code': None,
            'qct_status': 'Not QCT',
            'dda_status': 'Not DDA',
            'basis_boost_eligible': False,
            'industry_classification': 'No QCT/DDA',
            'analysis_status': 'Success'
        }
        
        try:
            # Get census tract
            tract_info = self.get_census_tract(lat, lon)
            if tract_info:
                result['census_tract'] = tract_info['geoid']
                
                # Check QCT status
                is_qct, qct_msg = self.check_qct_status(tract_info['geoid'])
                result['qct_status'] = qct_msg
                
                # Get ZIP code
                zip_code = self.get_zip_from_address(lat, lon)
                result['zip_code'] = zip_code
                
                # Check DDA status
                is_dda, dda_msg = self.check_dda_status(zip_code)
                result['dda_status'] = dda_msg
                
                # Determine final status
                if is_qct and is_dda:
                    result['industry_classification'] = 'QCT + DDA'
                    result['basis_boost_eligible'] = True
                elif is_qct:
                    result['industry_classification'] = 'QCT Only'
                    result['basis_boost_eligible'] = True
                elif is_dda:
                    result['industry_classification'] = 'DDA Only'  
                    result['basis_boost_eligible'] = True
                
            else:
                result['analysis_status'] = 'Census tract lookup failed'
        
        except Exception as e:
            result['analysis_status'] = f'Error: {str(e)[:100]}'
        
        return result

if __name__ == "__main__":
    print("🔍 TESTING FIXED QCT/DDA ANALYZER...")
    
    analyzer = FixedQCTDDAAnalyzer()
    
    # Test on known Texas QCT areas
    test_locations = [
        (29.7604, -95.3698, 'Houston Downtown'),     # Should be QCT
        (32.7767, -96.7970, 'Dallas Downtown'),      # Should be QCT  
        (29.4241, -98.4936, 'San Antonio Downtown'), # Should be QCT
        (33.0271742, -97.131181, 'Flower Mound'),    # Suburban - likely not QCT
    ]
    
    print("\\n📊 TESTING KNOWN AREAS:")
    for lat, lon, name in test_locations:
        result = analyzer.analyze_site(lat, lon, name)
        print(f"{name}: {result['industry_classification']} - Boost: {result['basis_boost_eligible']}")
        print(f"  Tract: {result['census_tract']}, Status: {result['analysis_status']}")