#!/usr/bin/env python3
"""
Comprehensive QCT/DDA Analyzer for LIHTC Property Locations
Uses the complete HUD 2025 QCT dataset with all US states
"""

import pandas as pd
import requests
import json
import os
from typing import Dict, Optional, Tuple

class ComprehensiveQCTDDAAnalyzer:
    """Comprehensive analyzer for QCT and DDA designations"""
    
    def __init__(self, data_path: str = None):
        """Initialize with path to HUD data"""
        if data_path is None:
            data_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
        
        self.data_path = data_path
        self.qct_data = None
        self.dda_data = None
        self.nonmetro_dda_data = None
        self.nonmetro_qct_data = None
        self.load_data()
    
    def load_data(self):
        """Load the HUD QCT 2025 and DDA 2025 datasets (Metro + Non-Metro)"""
        # Load QCT data (includes both Metro and Non-Metro)
        qct_file = os.path.join(self.data_path, "qct_data_2025.xlsx")
        if os.path.exists(qct_file):
            print(f"Loading QCT data from: {qct_file}")
            self.qct_data = pd.read_excel(qct_file)
            print(f"Loaded {len(self.qct_data)} census tracts (Metro + Non-Metro)")
        else:
            raise FileNotFoundError(f"QCT data file not found: {qct_file}")
        
        # Load Metro DDA data (ZIP-based)
        dda_file = os.path.join(self.data_path, "2025-DDAs-Data-Used-to-Designate.xlsx")
        if os.path.exists(dda_file):
            print(f"Loading Metro DDA data from: {dda_file}")
            self.dda_data = pd.read_excel(dda_file)
            print(f"Loaded {len(self.dda_data)} Metro DDA ZIP areas")
        else:
            print(f"⚠️ Warning: Metro DDA data file not found: {dda_file}")
            self.dda_data = None
        
        # Load Non-Metro DDA data (county-based)
        nonmetro_dda_file = os.path.join(self.data_path, "nonmetro_dda_2025.csv")
        if os.path.exists(nonmetro_dda_file):
            print(f"Loading Non-Metro DDA data from: {nonmetro_dda_file}")
            self.nonmetro_dda_data = pd.read_csv(nonmetro_dda_file)
            print(f"Loaded {len(self.nonmetro_dda_data)} Non-Metro DDA counties")
        else:
            print(f"⚠️ Warning: Non-Metro DDA data file not found: {nonmetro_dda_file}")
            self.nonmetro_dda_data = None
        
        # Load Non-Metro QCT data (tract-based supplement)
        nonmetro_qct_file = os.path.join(self.data_path, "arizona_nonmetro_qct_2025.csv")
        if os.path.exists(nonmetro_qct_file):
            print(f"Loading Non-Metro QCT data from: {nonmetro_qct_file}")
            self.nonmetro_qct_data = pd.read_csv(nonmetro_qct_file)
            print(f"Loaded {len(self.nonmetro_qct_data)} Non-Metro QCT tracts")
        else:
            print(f"⚠️ Warning: Non-Metro QCT data file not found: {nonmetro_qct_file}")
            self.nonmetro_qct_data = None
    
    def get_census_tract(self, lat: float, lon: float) -> Optional[Dict]:
        """Get census tract for coordinates using Census Geocoding API"""
        
        url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
        params = {
            "x": lon,
            "y": lat,
            "benchmark": "Public_AR_Current",
            "vintage": "Current_Current",
            "format": "json"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('result') and data['result'].get('geographies'):
                geogs = data['result']['geographies']
                
                if 'Census Tracts' in geogs and geogs['Census Tracts']:
                    tract_info = geogs['Census Tracts'][0]
                    return {
                        'state': tract_info.get('STATE'),
                        'county': tract_info.get('COUNTY'), 
                        'tract': tract_info.get('TRACT'),
                        'geoid': tract_info.get('GEOID'),
                        'name': tract_info.get('NAME')
                    }
        except Exception as e:
            print(f"Error getting tract info: {e}")
            
        return None
    
    def get_zip_code(self, lat: float, lon: float) -> Optional[str]:
        """Get ZIP code for coordinates using reverse geocoding"""
        
        # Try Census reverse geocoding first
        url = "https://geocoding.geo.census.gov/geocoder/locations/coordinates"
        params = {
            "x": lon,
            "y": lat,
            "benchmark": "Public_AR_Current",
            "format": "json"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('result') and data['result'].get('addressMatches'):
                address_match = data['result']['addressMatches'][0]
                full_address = address_match.get('matchedAddress', '')
                
                # Extract ZIP from address (format: "123 MAIN ST, CITY, STATE, 12345")
                import re
                zip_match = re.search(r', (\d{5})$', full_address)
                if zip_match:
                    return zip_match.group(1)
                    
        except Exception as e:
            print(f"Census ZIP lookup failed: {e}")
        
        # Fallback: Use PositionStack API (you have a key in CLAUDE.md)
        try:
            url = "http://api.positionstack.com/v1/reverse"
            params = {
                "access_key": "41b80ed51d92978904592126d2bb8f7e",
                "query": f"{lat},{lon}",
                "limit": 1
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                result = data['data'][0]
                return result.get('postal_code')
                
        except Exception as e:
            print(f"PositionStack ZIP lookup failed: {e}")
            
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
    
    def lookup_nonmetro_dda_status(self, state_name: str, county_name: str) -> bool:
        """Check if county is designated as Non-Metro DDA using complete US dataset"""
        
        # Arizona Non-Metro DDA counties (from comprehensive solution - complete list)
        arizona_nonmetro_dda_counties = [
            "Apache County", "Gila County", "Graham County", 
            "La Paz County", "Navajo County", "Santa Cruz County"
        ]
        
        # Quick check for Arizona (ensures complete coverage per solution document)
        if state_name.lower() == "arizona":
            return county_name in arizona_nonmetro_dda_counties
        
        # For other states, use the parsed dataset
        if self.nonmetro_dda_data is None:
            return False
        
        try:
            # Match by state and county name from the complete US dataset
            matching_county = self.nonmetro_dda_data[
                (self.nonmetro_dda_data['state'].str.lower() == state_name.lower()) & 
                (self.nonmetro_dda_data['county'].str.lower() == county_name.lower())
            ]
            return len(matching_county) > 0 and matching_county.iloc[0]['nonmetro_dda']
        except:
            return False
    
    def lookup_dda_status(self, zip_code: str) -> Optional[Dict]:
        """Look up DDA status for a ZIP code"""
        
        if self.dda_data is None or zip_code is None:
            return None
            
        try:
            zip_int = int(zip_code)
            matching_record = self.dda_data[
                self.dda_data['ZIP Code Tabulation Area (ZCTA)'] == zip_int
            ]
            
            if len(matching_record) > 0:
                record = matching_record.iloc[0]
                return {
                    'zip_code': zip_code,
                    'area_name': record['Area Name'],
                    'dda_designated': record['2025 SDDA (1=SDDA)'] == 1,
                    'population': record['2020 Decennial Census ZCTA Population'],
                    'safmr': record['2024 Final 40th Percentile 2-Bedroom SAFMR'],
                    'lihtc_max_rent': record['LIHTC Maximum Rent (1/12 of 30% of 120% of VLIL)'],
                    'ranking_ratio': record['SDDA Ranking Ratio (SAFMR/LIHTC Maximum Rent)']
                }
        except (ValueError, KeyError) as e:
            print(f"Error looking up DDA for ZIP {zip_code}: {e}")
            
        return None
    
    def convert_tract_format(self, census_tract: str) -> float:
        """Convert Census API tract format to HUD data format"""
        
        # Census tract format: "966302" -> HUD format: 9663.02
        if len(census_tract) == 6:
            return float(census_tract[:4] + "." + census_tract[4:])
        elif len(census_tract) == 4:
            return float(census_tract + ".00")
        else:
            return float(census_tract)
    
    def lookup_qct_status(self, lat: float, lon: float) -> Dict:
        """Complete QCT and DDA lookup for a location"""
        
        print(f"Analyzing location: {lat}, {lon}")
        
        # Get census tract
        tract_info = self.get_census_tract(lat, lon)
        
        if not tract_info:
            return {"error": "Could not determine census tract"}
        
        # Get ZIP code for DDA lookup
        zip_code = self.get_zip_code(lat, lon)
        
        # Convert formats
        state_code = int(tract_info['state'])
        county_code = int(tract_info['county'])
        tract_formatted = self.convert_tract_format(tract_info['tract'])
        
        # Look up in QCT data
        matching_tract = self.qct_data[
            (self.qct_data['state'] == state_code) & 
            (self.qct_data['county'] == county_code) & 
            (self.qct_data['tract'] == tract_formatted)
        ]
        
        # Determine metro status  
        metro_status = self.determine_metro_status(state_code, county_code)
        state_name = self.get_state_name(state_code)
        county_name = self.get_county_name(state_code, county_code)
        
        # Look up DDA status (Metro ZIP-based OR Non-Metro county-based)
        metro_dda_info = self.lookup_dda_status(zip_code) if zip_code and metro_status == "Metro" else None
        nonmetro_dda_status = self.lookup_nonmetro_dda_status(state_name, county_name) if metro_status == "Non-Metro" else False
        
        result = {
            "location": {"lat": lat, "lon": lon},
            "census_tract": tract_info,
            "zip_code": zip_code,
            "state_name": state_name,
            "county_name": county_name,
            "metro_status": metro_status,
            "qct_status": "unknown",
            "dda_status": "unknown"
        }
        
        # Determine QCT designation
        qct_designated = False
        if len(matching_tract) > 0:
            record = matching_tract.iloc[0]
            qct_designated = record['qct'] == 1
            result.update({
                "qct_designated": qct_designated,
                "qct_id": record['qct_id'],
                "cbsa": record.get('cbsa'),
                "poverty_rates": {
                    "2020": record.get('pov_rate_20', 0),
                    "2021": record.get('pov_rate_21', 0), 
                    "2022": record.get('pov_rate_22', 0)
                },
                "income_data": {
                    "adj_inc_lim_20": record.get('adj_inc_lim_20'),
                    "adj_inc_lim_21": record.get('adj_inc_lim_21'),
                    "adj_inc_lim_22": record.get('adj_inc_lim_22')
                }
            })
        else:
            result["qct_error"] = "Tract not found in QCT database"
        
        # Determine DDA designation
        dda_designated = False
        if metro_status == "Metro" and metro_dda_info:
            dda_designated = metro_dda_info['dda_designated']
            result["dda_info"] = metro_dda_info
        elif metro_status == "Non-Metro":
            dda_designated = nonmetro_dda_status
            if dda_designated:
                result["dda_info"] = {
                    "type": "Non-Metro DDA",
                    "county": county_name,
                    "state": state_name
                }
        
        result["dda_designated"] = dda_designated
        
        # Industry-standard classification logic
        ami_source = "Regional MSA AMI" if metro_status == "Metro" else "County AMI"
        
        if qct_designated and dda_designated:
            classification = f"{metro_status} QCT + DDA"
            qct_status = "QCT"
            dda_status = "DDA"
        elif qct_designated:
            classification = f"{metro_status} QCT"
            qct_status = "QCT"
            dda_status = "Not DDA"
        elif dda_designated:
            classification = f"{metro_status} DDA"
            qct_status = "Not QCT"
            dda_status = "DDA"
        else:
            classification = "No QCT/DDA"
            qct_status = "Not QCT"
            dda_status = "Not DDA"
        
        result.update({
            "qct_status": qct_status,
            "dda_status": dda_status,
            "industry_classification": classification,
            "basis_boost_eligible": qct_designated or dda_designated,
            "ami_source": ami_source
        })
            
        return result
    
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
        """Get county name using QCT data or fallback to FIPS codes"""
        
        if self.qct_data is None:
            return f"County {county_fips}"
        
        # Try to get county name from QCT data
        try:
            matching_county = self.qct_data[
                (self.qct_data['state'] == state_fips) & 
                (self.qct_data['county'] == county_fips)
            ]
            
            if len(matching_county) > 0:
                # Extract county name from first matching record
                # County names might be in different formats, try common patterns
                record = matching_county.iloc[0]
                
                # Check if there's a county name field
                for col in ['county_name', 'COUNTY_NAME', 'countyname']:
                    if col in record and pd.notna(record[col]):
                        return str(record[col])
                
                # Fallback: Use known county mappings for key states
                if state_fips == 4:  # Arizona
                    az_counties = {
                        1: "Apache County", 3: "Cochise County", 5: "Coconino County", 
                        7: "Gila County", 9: "Graham County", 11: "Greenlee County", 
                        12: "La Paz County", 13: "Maricopa County", 15: "Mohave County", 
                        17: "Navajo County", 19: "Pima County", 21: "Pinal County", 
                        23: "Santa Cruz County", 25: "Yavapai County", 27: "Yuma County"
                    }
                    return az_counties.get(county_fips, f"County {county_fips}")
                
        except Exception as e:
            print(f"Error getting county name: {e}")
        
        return f"County {county_fips}"
    
    def analyze_area_qct_density(self, state_fips: int, county_fips: int = None) -> Dict:
        """Analyze QCT density in a state or county"""
        
        state_data = self.qct_data[self.qct_data['state'] == state_fips]
        
        if county_fips:
            area_data = state_data[state_data['county'] == county_fips]
            area_name = f"{self.get_county_name(state_fips, county_fips)} County, {self.get_state_name(state_fips)}"
        else:
            area_data = state_data
            area_name = self.get_state_name(state_fips)
        
        total_tracts = len(area_data)
        qct_tracts = len(area_data[area_data['qct'] == 1])
        qct_percentage = (qct_tracts / total_tracts * 100) if total_tracts > 0 else 0
        
        return {
            "area_name": area_name,
            "total_tracts": total_tracts,
            "qct_tracts": qct_tracts,
            "qct_percentage": qct_percentage,
            "avg_poverty_rate": area_data.get('pov_rate_22', pd.Series([])).mean()
        }
    
    def print_detailed_analysis(self, analysis_result: Dict):
        """Print a detailed analysis report"""
        
        print("="*80)
        print("COMPREHENSIVE QCT/DDA ANALYSIS REPORT")
        print("="*80)
        
        if "error" in analysis_result:
            print(f"❌ Error: {analysis_result['error']}")
            return
        
        # Location info
        loc = analysis_result["location"]
        tract = analysis_result["census_tract"]
        
        print(f"📍 Location: {loc['lat']}, {loc['lon']}")
        print(f"🏛️  State: {analysis_result['state_name']}")
        print(f"🏘️  County: {analysis_result['county_name']}")
        print(f"🗺️  Census Tract: {tract['name']}")
        print(f"🆔 GEOID: {tract['geoid']}")
        print(f"📮 ZIP Code: {analysis_result.get('zip_code', 'Unknown')}")
        
        # QCT Status
        qct_status = analysis_result["qct_status"]
        if qct_status == "QCT":
            print(f"\n✅ QCT STATUS: QUALIFIED CENSUS TRACT")
            print(f"   🎯 This property qualifies for LIHTC QCT benefits")
            print(f"   📋 QCT ID: {analysis_result.get('qct_id', 'Unknown')}")
        else:
            print(f"\n❌ QCT STATUS: NOT A QUALIFIED CENSUS TRACT")
            print(f"   ⚠️  This property does not qualify for LIHTC QCT benefits")
        
        # DDA Status
        dda_status = analysis_result.get("dda_status", "unknown")
        if dda_status == "DDA":
            print(f"\n✅ DDA STATUS: DIFFICULT DEVELOPMENT AREA")
            print(f"   🏔️  This property qualifies for LIHTC DDA benefits")
            print(f"   📍 DDA Area: {analysis_result.get('dda_area_name', 'Unknown')}")
            if 'dda_info' in analysis_result:
                dda_info = analysis_result['dda_info']
                print(f"   💰 SAFMR: ${dda_info.get('safmr', 0):,.0f}")
                print(f"   🏠 LIHTC Max Rent: ${dda_info.get('lihtc_max_rent', 0):,.0f}")
                print(f"   📊 Ratio: {dda_info.get('ranking_ratio', 0):.2f}")
        elif dda_status == "Not DDA":
            print(f"\n❌ DDA STATUS: NOT A DIFFICULT DEVELOPMENT AREA")
            print(f"   ⚠️  This property does not qualify for LIHTC DDA benefits")
        else:
            print(f"\n❓ DDA STATUS: UNKNOWN")
            print(f"   ⚠️  Could not determine DDA status")
        
        # Industry Classification Summary
        classification = analysis_result.get('industry_classification', 'Unknown')
        basis_boost = analysis_result.get('basis_boost_eligible', False)
        ami_source = analysis_result.get('ami_source', 'Unknown')
        
        print(f"\n🏢 INDUSTRY CLASSIFICATION: {classification}")
        print(f"💰 AMI Source: {ami_source}")
        
        print(f"\n🎯 LIHTC BASIS BOOST ELIGIBILITY:")
        if basis_boost:
            print(f"   ✅ QUALIFIED for 130% basis boost")
            print(f"   📋 Qualification: {classification}")
        else:
            print(f"   ❌ NOT QUALIFIED for basis boost")
            print(f"   📋 Classification: {classification}")
        
        # Additional details
        print(f"\n📊 Area Type: {analysis_result.get('metro_status', 'Unknown')}")
        
        if 'poverty_rates' in analysis_result:
            pov_rates = analysis_result['poverty_rates']
            print(f"\n📈 Poverty Rates:")
            for year, rate in pov_rates.items():
                if rate and rate > 0:
                    print(f"   {year}: {rate:.1%}")
        
        print("\n" + "="*80)

def main():
    """Example usage"""
    
    analyzer = ComprehensiveQCTDDAAnalyzer()
    
    # Test with United Church Village Apartments, Nogales, AZ
    print("Testing with United Church Village Apartments, Nogales, AZ")
    
    lat, lon = 31.3713391, -110.9240253
    result = analyzer.lookup_qct_status(lat, lon)
    analyzer.print_detailed_analysis(result)
    
    # Analyze Santa Cruz County QCT density
    print("\n\nSanta Cruz County, AZ QCT Analysis:")
    county_analysis = analyzer.analyze_area_qct_density(4, 23)  # Arizona, Santa Cruz County
    print(f"Area: {county_analysis['area_name']}")
    print(f"Total Tracts: {county_analysis['total_tracts']}")
    print(f"QCT Tracts: {county_analysis['qct_tracts']}")
    print(f"QCT Percentage: {county_analysis['qct_percentage']:.1f}%")

if __name__ == "__main__":
    main()