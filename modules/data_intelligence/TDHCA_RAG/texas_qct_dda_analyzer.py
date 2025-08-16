#!/usr/bin/env python3
"""
Texas QCT/DDA Analyzer - Fixed version for 375 CoStar sites
"""

import pandas as pd
import requests
import json
import time
from datetime import datetime

class TexasQCTDDAAnalyzer:
    """Working QCT/DDA analyzer specifically for Texas sites"""
    
    def __init__(self):
        self.census_api_key = "06ece0121263282cd9ffd753215b007b8f9a3dfc"
        self.load_data()
    
    def load_data(self):
        """Load HUD QCT and DDA data"""
        base_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
        
        # Load QCT data
        print("Loading QCT data...")
        self.qct_data = pd.read_excel(f"{base_path}/qct_data_2025.xlsx")
        
        # Filter for Texas (state = 48) and QCT designated (qct = 1)
        self.texas_qcts = self.qct_data[(self.qct_data['state'] == 48) & (self.qct_data['qct'] == 1)]
        print(f"✅ Texas QCTs loaded: {len(self.texas_qcts)} tracts")
        
        # Load Metro DDA data
        print("Loading Metro DDA data...")
        self.metro_dda_data = pd.read_excel(f"{base_path}/2025-DDAs-Data-Used-to-Designate.xlsx")
        
        # Filter for Texas ZIP codes (assuming they start with 7)
        self.texas_metro_ddas = self.metro_dda_data[
            self.metro_dda_data['ZCTA5CE20'].astype(str).str.startswith('7')
        ]
        print(f"✅ Texas Metro DDAs loaded: {len(self.texas_metro_ddas)} ZIP areas")
        
        # Load Non-Metro DDA data
        print("Loading Non-Metro DDA data...")
        self.nonmetro_dda_data = pd.read_csv(f"{base_path}/nonmetro_dda_2025.csv")
        
        # Filter for Texas counties (FIPS starting with 48)
        if 'FIPS' in self.nonmetro_dda_data.columns:
            self.texas_nonmetro_ddas = self.nonmetro_dda_data[
                self.nonmetro_dda_data['FIPS'].astype(str).str.startswith('48')
            ]
        else:
            self.texas_nonmetro_ddas = pd.DataFrame()  # Empty if column doesn't exist
        
        print(f"✅ Texas Non-Metro DDAs loaded: {len(self.texas_nonmetro_ddas)} counties")
    
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
                        'state': tract_info.get('STATE', ''),
                        'county': tract_info.get('COUNTY', ''),
                        'tract': tract_info.get('TRACT', '')
                    }
            
            return None
            
        except Exception as e:
            print(f"Census tract lookup error: {e}")
            return None
    
    def check_qct_status(self, tract_geoid):
        """Check if tract is QCT designated"""
        if not tract_geoid:
            return False, "No tract ID"
        
        # Convert tract_geoid to match QCT database format
        if len(tract_geoid) == 11:  # Full GEOID like 48113020402
            state_code = int(tract_geoid[:2])
            county_code = int(tract_geoid[2:5])
            tract_code = float(tract_geoid[5:]) / 100  # Convert to decimal format
            
            # Look up in Texas QCT data
            matching_qcts = self.texas_qcts[
                (self.texas_qcts['state'] == state_code) &
                (self.texas_qcts['county'] == county_code) &
                (abs(self.texas_qcts['tract'] - tract_code) < 0.01)  # Float comparison tolerance
            ]
            
            if len(matching_qcts) > 0:
                return True, "QCT Designated"
            else:
                return False, "Not QCT"
        
        return False, "Invalid tract format"
    
    def check_dda_status(self, zip_code, county_fips=None):
        """Check if ZIP or county is DDA designated"""
        dda_status = {"metro": False, "nonmetro": False, "status": "Not DDA"}
        
        if zip_code:
            # Check Metro DDA (ZIP-based)
            metro_matches = self.texas_metro_ddas[
                self.texas_metro_ddas['ZCTA5CE20'].astype(str) == str(zip_code).zfill(5)
            ]
            if len(metro_matches) > 0:
                dda_status["metro"] = True
                dda_status["status"] = "Metro DDA"
        
        if county_fips:
            # Check Non-Metro DDA (county-based)
            nonmetro_matches = self.texas_nonmetro_ddas[
                self.texas_nonmetro_ddas['FIPS'].astype(str) == str(county_fips)
            ]
            if len(nonmetro_matches) > 0:
                dda_status["nonmetro"] = True
                if dda_status["status"] == "Not DDA":
                    dda_status["status"] = "Non-Metro DDA"
                else:
                    dda_status["status"] = "Metro + Non-Metro DDA"
        
        return dda_status["metro"] or dda_status["nonmetro"], dda_status["status"]
    
    def get_zip_code_simple(self, lat, lon):
        """Simple ZIP code lookup using reverse geocoding"""
        try:
            # Use a free reverse geocoding service
            url = f"https://api.zippopotam.us/us/{lat},{lon}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('post code', None)
        except:
            pass
        
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
                
                # Get ZIP code for DDA check
                zip_code = self.get_zip_code_simple(lat, lon)
                result['zip_code'] = zip_code
                
                # Check DDA status
                county_fips = tract_info['state'] + tract_info['county']
                is_dda, dda_msg = self.check_dda_status(zip_code, county_fips)
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
    
    def analyze_costar_sites(self, sites_file, output_file=None):
        """Analyze all CoStar sites for QCT/DDA status"""
        print(f"🎯 ANALYZING COSTAR SITES FOR QCT/DDA STATUS...")
        
        # Load sites
        df = pd.read_excel(sites_file)
        print(f"✅ Loaded {len(df)} sites")
        
        # Add analysis columns
        analysis_columns = [
            'Census_Tract', 'ZIP_Code', 'QCT_Status', 'DDA_Status',
            'Basis_Boost_Eligible', 'Industry_Classification', 'Analysis_Status'
        ]
        
        for col in analysis_columns:
            df[col] = ''
        
        # Analyze each site
        qct_count = 0
        dda_count = 0
        dual_count = 0
        boost_eligible_count = 0
        
        for idx, row in df.iterrows():
            lat = row['Latitude']
            lon = row['Longitude']
            city = row.get('City', 'Unknown')
            
            result = self.analyze_site(lat, lon, city)
            
            # Populate columns
            df.at[idx, 'Census_Tract'] = result['census_tract'] or ''
            df.at[idx, 'ZIP_Code'] = result['zip_code'] or ''
            df.at[idx, 'QCT_Status'] = result['qct_status']
            df.at[idx, 'DDA_Status'] = result['dda_status']
            df.at[idx, 'Basis_Boost_Eligible'] = 'YES' if result['basis_boost_eligible'] else 'NO'
            df.at[idx, 'Industry_Classification'] = result['industry_classification']
            df.at[idx, 'Analysis_Status'] = result['analysis_status']
            
            # Count results
            if 'QCT' in result['qct_status']:
                qct_count += 1
            if 'DDA' in result['dda_status']:
                dda_count += 1
            if 'QCT + DDA' in result['industry_classification']:
                dual_count += 1
            if result['basis_boost_eligible']:
                boost_eligible_count += 1
            
            print(f"✅ {idx+1}/{len(df)}: {city} - {result['industry_classification']}")
            
            # Rate limiting
            time.sleep(1.2)  # Be nice to Census API
        
        # Summary
        print(f"\\n📊 FINAL QCT/DDA ANALYSIS RESULTS:")
        print(f"🎯 QCT Sites: {qct_count}")
        print(f"🎯 DDA Sites: {dda_count}")
        print(f"🎯 QCT + DDA Sites: {dual_count}")
        print(f"✅ Total Basis Boost Eligible: {boost_eligible_count}")
        print(f"📈 Eligibility Rate: {boost_eligible_count/len(df)*100:.1f}%")
        
        # Save results
        if output_file:
            df.to_excel(output_file, index=False)
            print(f"💾 Results saved: {output_file}")
        
        return df

if __name__ == "__main__":
    analyzer = TexasQCTDDAAnalyzer()
    
    # Test on a known QCT area first
    print("🔍 TESTING ON KNOWN QCT AREA...")
    test_result = analyzer.analyze_site(29.7604, -95.3698, "Houston Downtown")
    print(f"Test result: {test_result}")
    
    # Then run on CoStar sites
    input_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/Analysis_Results/CoStar_375_Phase1_Screening_20250731_160305.xlsx"
    output_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG/D'Marco_Sites/Analysis_Results/CoStar_375_Complete_QCT_DDA_Analysis.xlsx"
    
    results = analyzer.analyze_costar_sites(input_file, output_file)