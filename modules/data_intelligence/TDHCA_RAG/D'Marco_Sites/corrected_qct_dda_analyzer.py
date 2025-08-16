#!/usr/bin/env python3
"""
CORRECTED QCT/DDA Analyzer - Reads from proper Excel tabs
Fixed to read Texas data from MT-WY tab (state codes 30-72)
"""

import pandas as pd
import requests
import json
import os
from typing import Dict, Optional, Tuple

class CorrectedQCTDDAAnalyzer:
    """Corrected QCT/DDA analyzer reading from proper Excel tabs"""
    
    def __init__(self, data_path: str = None):
        """Initialize with path to HUD data"""
        if data_path is None:
            data_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
        
        self.data_path = data_path
        self.qct_data = None
        self.dda_data = None
        self.nonmetro_dda_data = None
        self.load_all_data()
    
    def load_all_data(self):
        """Load ALL QCT and DDA data from proper sources"""
        
        print("Loading corrected QCT/DDA data from proper tabs...")
        
        # 1. Load QCT Data from BOTH Excel tabs (AL-MO + MT-WY)
        qct_file = os.path.join(self.data_path, "qct_data_2025.xlsx")
        if os.path.exists(qct_file):
            print(f"Loading QCT data from: {qct_file}")
            
            # Read both tabs and combine
            tab1 = pd.read_excel(qct_file, sheet_name="AL-MO")
            tab2 = pd.read_excel(qct_file, sheet_name="MT-WY")  # Texas is here!
            
            self.qct_data = pd.concat([tab1, tab2], ignore_index=True)
            print(f"✅ Loaded {len(self.qct_data)} total QCT records from both tabs")
            
            # Verify Texas data
            texas_count = (self.qct_data['state'] == 48).sum()
            harris_count = ((self.qct_data['state'] == 48) & (self.qct_data['county'] == 201)).sum()
            print(f"✅ Texas records: {texas_count}")
            print(f"✅ Harris County tracts: {harris_count}")
            
        else:
            raise FileNotFoundError(f"QCT data file not found: {qct_file}")
        
        # 2. Load Metro DDA data (ZIP-based)
        dda_file = os.path.join(self.data_path, "2025-DDAs-Data-Used-to-Designate.xlsx")
        if os.path.exists(dda_file):
            print(f"Loading Metro DDA data from: {dda_file}")
            self.dda_data = pd.read_excel(dda_file)
            print(f"✅ Loaded {len(self.dda_data)} Metro DDA ZIP areas")
        else:
            print(f"⚠️ Warning: Metro DDA data file not found: {dda_file}")
            self.dda_data = None
        
        # 3. Load Non-Metro DDA data (county-based)
        nonmetro_dda_file = os.path.join(self.data_path, "nonmetro_dda_2025.csv")
        if os.path.exists(nonmetro_dda_file):
            print(f"Loading Non-Metro DDA data from: {nonmetro_dda_file}")
            self.nonmetro_dda_data = pd.read_csv(nonmetro_dda_file)
            print(f"✅ Loaded {len(self.nonmetro_dda_data)} Non-Metro DDA counties")
        else:
            print(f"⚠️ Warning: Non-Metro DDA data file not found: {nonmetro_dda_file}")
            self.nonmetro_dda_data = None
    
    def get_census_tract_and_zip(self, lat: float, lon: float) -> Optional[Dict]:
        """Get census tract AND ZIP code using working geographies endpoint"""
        
        url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
        params = {
            "x": lon,
            "y": lat,
            "benchmark": "Public_AR_Current",
            "vintage": "Current_Current", 
            "format": "json",
            "layers": "all"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            result = {"tract_info": None, "zip_code": None}
            
            if data.get('result') and data['result'].get('geographies'):
                geogs = data['result']['geographies']
                
                # Extract tract information
                if 'Census Tracts' in geogs and geogs['Census Tracts']:
                    tract_info = geogs['Census Tracts'][0]
                    result["tract_info"] = {
                        'state': tract_info.get('STATE'),
                        'county': tract_info.get('COUNTY'), 
                        'tract': tract_info.get('TRACT'),
                        'geoid': tract_info.get('GEOID'),
                        'name': tract_info.get('NAME')
                    }
                
                # Extract ZIP code information
                if '2020 Census ZIP Code Tabulation Areas' in geogs and geogs['2020 Census ZIP Code Tabulation Areas']:
                    zip_info = geogs['2020 Census ZIP Code Tabulation Areas'][0]
                    result["zip_code"] = zip_info.get('ZCTA5')
                    
            return result if result["tract_info"] else None
            
        except Exception as e:
            print(f"Error getting tract/ZIP info: {e}")
            return None
    
    def determine_metro_status(self, state_code: int, county_code: int) -> str:
        """Determine if location is Metro or Non-Metro based on QCT data"""
        
        if self.qct_data is None:
            return "Unknown"
        
        # Check metro status from QCT data
        matching_records = self.qct_data[
            (self.qct_data['state'] == state_code) & 
            (self.qct_data['county'] == county_code)
        ]
        
        if len(matching_records) > 0:
            # Use the metro field (1 = Metro, 0 = Non-Metro)
            metro_status = matching_records.iloc[0].get('metro', 0)
            return "Metro" if metro_status == 1 else "Non-Metro"
        
        return "Unknown"
    
    def lookup_dda_status(self, zip_code: str, metro_status: str) -> Optional[Dict]:
        """Look up DDA status - Metro (ZIP-based) or Non-Metro (county-based)"""
        
        if metro_status == "Metro" and self.dda_data is not None and zip_code:
            # Metro DDA lookup (ZIP-based)
            try:
                zip_int = int(zip_code)
                matching_record = self.dda_data[
                    self.dda_data['ZIP Code Tabulation Area (ZCTA)'] == zip_int
                ]
                
                if len(matching_record) > 0:
                    record = matching_record.iloc[0]
                    return {
                        'type': 'Metro DDA',
                        'zip_code': zip_code,
                        'area_name': record['Area Name'],
                        'dda_designated': record['2025 SDDA (1=SDDA)'] == 1,
                        'population': record['2020 Decennial Census ZCTA Population'],
                        'safmr': record['2024 Final 40th Percentile 2-Bedroom SAFMR'],
                        'lihtc_max_rent': record['LIHTC Maximum Rent (1/12 of 30% of 120% of VLIL)'],
                        'ranking_ratio': record['SDDA Ranking Ratio (SAFMR/LIHTC Maximum Rent)']
                    }
            except (ValueError, KeyError) as e:
                print(f"Error looking up Metro DDA for ZIP {zip_code}: {e}")
                
        elif metro_status == "Non-Metro" and self.nonmetro_dda_data is not None:
            # Non-Metro DDA lookup (county-based) - would need county name
            # For now, return basic structure
            return {
                'type': 'Non-Metro DDA',
                'dda_designated': False,  # Would need proper county lookup
                'note': 'Non-Metro DDA lookup requires county name matching'
            }
            
        return None
    
    def convert_tract_format(self, census_tract: str) -> float:
        """Convert Census API tract format to HUD data format"""
        
        # Census tract format: "312300" -> HUD format: 3123.00
        if len(census_tract) == 6:
            return float(census_tract[:4] + "." + census_tract[4:])
        elif len(census_tract) == 4:
            return float(census_tract + ".00")
        else:
            return float(census_tract)
    
    def lookup_qct_status(self, lat: float, lon: float) -> Dict:
        """Complete QCT and DDA lookup for a location - CORRECTED VERSION"""
        
        print(f"🔍 Analyzing location: {lat}, {lon}")
        
        # Get census tract AND ZIP code
        location_data = self.get_census_tract_and_zip(lat, lon)
        
        if not location_data or not location_data.get("tract_info"):
            return {"error": "Could not determine census tract"}
        
        tract_info = location_data["tract_info"]
        zip_code = location_data["zip_code"]
        
        print(f"✅ Found tract: {tract_info.get('name')}, ZIP: {zip_code}")
        
        # Convert formats
        state_code = int(tract_info['state'])
        county_code = int(tract_info['county'])
        tract_formatted = self.convert_tract_format(tract_info['tract'])
        
        print(f"🔍 Looking for: State={state_code}, County={county_code}, Tract={tract_formatted}")
        
        # Look up in QCT data (NOW INCLUDES TEXAS!)
        matching_tract = self.qct_data[
            (self.qct_data['state'] == state_code) & 
            (self.qct_data['county'] == county_code) & 
            (self.qct_data['tract'] == tract_formatted)
        ]
        
        # Determine metro status  
        metro_status = self.determine_metro_status(state_code, county_code)
        state_name = self.get_state_name(state_code)
        county_name = self.get_county_name(state_code, county_code)
        
        print(f"📍 Location: {state_name}, {county_name} ({metro_status})")
        
        # Determine QCT designation
        qct_designated = False
        qct_status = "NOT_QCT"
        if len(matching_tract) > 0:
            record = matching_tract.iloc[0]
            qct_designated = record['qct'] == 1
            qct_status = "QCT" if qct_designated else "NOT_QCT"
            print(f"🎯 QCT Status: {qct_status} (found in database)")
        else:
            print("⚠️ Tract not found in QCT database")
        
        # Look up DDA status
        dda_info = self.lookup_dda_status(zip_code, metro_status)
        dda_designated = False
        dda_status = "NOT_DDA"
        
        if dda_info and dda_info.get('dda_designated'):
            dda_designated = True
            dda_status = "DDA"
            print(f"🏔️ DDA Status: {dda_status} ({dda_info.get('type', 'Unknown type')})")
        else:
            print(f"🏔️ DDA Status: {dda_status}")
        
        # Calculate basis boost eligibility
        basis_boost_eligible = qct_designated or dda_designated
        print(f"💰 Basis Boost Eligible: {'YES' if basis_boost_eligible else 'NO'}")
        
        # Create industry-standard classification
        if qct_designated and dda_designated:
            classification = f"{metro_status} QCT + DDA"
        elif qct_designated:
            classification = f"{metro_status} QCT"
        elif dda_designated:
            classification = f"{metro_status} DDA"
        else:
            classification = "No QCT/DDA"
        
        # Return in format expected by D'Marco analyzer
        return {
            'qct_designation': qct_status,
            'dda_designation': dda_status,
            'basis_boost_eligible': basis_boost_eligible,
            'census_tract': tract_info.get('name'),
            'county': county_name,
            'state': state_name,
            'zip_code': zip_code,
            'metro_status': metro_status,
            'industry_classification': classification,
            'ami_source': "Regional MSA AMI" if metro_status == "Metro" else "County AMI",
            'dda_info': dda_info
        }
    
    def get_state_name(self, state_fips: int) -> str:
        """Get state name from FIPS code"""
        
        states = {
            1: "Alabama", 2: "Alaska", 4: "Arizona", 5: "Arkansas", 6: "California",
            8: "Colorado", 9: "Connecticut", 10: "Delaware", 11: "District of Columbia",
            12: "Florida", 13: "Georgia", 15: "Hawaii", 16: "Idaho", 17: "Illinois",
            18: "Indiana", 19: "Iowa", 20: "Kansas", 21: "Kentucky", 22: "Louisiana",
            23: "Maine", 24: "Maryland", 25: "Massachusetts", 26: "Michigan", 27: "Minnesota",
            28: "Mississippi", 29: "Missouri", 30: "Montana", 31: "Nebraska", 32: "Nevada",
            33: "New Hampshire", 34: "New Jersey", 35: "New Mexico", 36: "New York",
            37: "North Carolina", 38: "North Dakota", 39: "Ohio", 40: "Oklahoma",
            41: "Oregon", 42: "Pennsylvania", 44: "Rhode Island", 45: "South Carolina",
            46: "South Dakota", 47: "Tennessee", 48: "Texas", 49: "Utah", 50: "Vermont",
            51: "Virginia", 53: "Washington", 54: "West Virginia", 55: "Wisconsin",
            56: "Wyoming", 72: "Puerto Rico"
        }
        return states.get(state_fips, f"Unknown({state_fips})")
    
    def get_county_name(self, state_fips: int, county_fips: int) -> str:
        """Get county name - Key Texas counties for LIHTC"""
        
        if state_fips == 48:  # Texas
            tx_counties = {
                113: "Dallas County", 157: "Fort Bend County", 201: "Harris County",
                439: "Tarrant County", 453: "Travis County", 29: "Bexar County",
                85: "Collin County", 121: "Denton County", 167: "Galveston County",
                339: "Montgomery County", 209: "Hays County", 491: "Williamson County"
            }
            return tx_counties.get(county_fips, f"County {county_fips}")
        
        return f"County {county_fips}"

def main():
    """Test the corrected analyzer"""
    
    print("🧪 TESTING CORRECTED QCT/DDA ANALYZER")
    print("="*60)
    
    analyzer = CorrectedQCTDDAAnalyzer()
    
    # Test with Houston Third Ward (known QCT area)
    lat, lng = 29.7372, -95.3647
    result = analyzer.lookup_qct_status(lat, lng)
    
    print("\n🎯 FINAL RESULT:")
    print(f"QCT: {result.get('qct_designation')}")
    print(f"DDA: {result.get('dda_designation')}")
    print(f"Basis Boost: {result.get('basis_boost_eligible')}")
    print(f"County: {result.get('county')}")
    print(f"ZIP: {result.get('zip_code')}")
    print(f"Classification: {result.get('industry_classification')}")

if __name__ == "__main__":
    main()