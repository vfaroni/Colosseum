#!/usr/bin/env python3
"""
Texas HFC Distressed Property Analysis System
Analyzes HFC properties facing distress due to HB 21 retroactive tax liability
Integrates 50%, 60%, 80% AMI rent analysis with Census demographic data
"""

import pandas as pd
import requests
import json
import time
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HFCPropertyAnalyzer:
    def __init__(self):
        # Data paths from CLAUDE.md
        self.hud_ami_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx"
        self.output_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Workforce_Housing/TX WFH/HFC_Project"
        self.cache_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Cache"
        
        # Census API key from CLAUDE.md
        self.census_api_key = "06ece0121263282cd9ffd753215b007b8f9a3dfc"
        
        # Create output directories
        Path(f"{self.output_path}/analysis_outputs").mkdir(parents=True, exist_ok=True)
        Path(f"{self.output_path}/census_data").mkdir(parents=True, exist_ok=True)
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        
        self.properties_df = None
        self.hud_ami_data = None
        
    def load_property_data(self):
        """Load HFC distressed properties data"""
        try:
            properties_path = f"{self.output_path}/data/hfc_distressed_properties.csv"
            self.properties_df = pd.read_csv(properties_path)
            logger.info(f"Loaded {len(self.properties_df)} properties")
            return True
        except Exception as e:
            logger.error(f"Error loading property data: {e}")
            return False
    
    def load_hud_ami_data(self):
        """Load HUD AMI rent data for Texas counties"""
        try:
            self.hud_ami_data = pd.read_excel(self.hud_ami_path)
            logger.info(f"Loaded HUD AMI data with {len(self.hud_ami_data)} records")
            
            # Filter to Texas data only
            self.hud_ami_data = self.hud_ami_data[self.hud_ami_data['stusps'] == 'TX'].copy()
            
            # Clean county names - remove "County" suffix
            self.hud_ami_data['County'] = self.hud_ami_data['County_Name'].str.replace(' County', '').str.strip()
            
            # Filter for target counties in our analysis
            target_counties = ['Harris', 'Tarrant', 'Johnson', 'Hood', 'Wise', 'Parker']
            texas_ami = self.hud_ami_data[self.hud_ami_data['County'].isin(target_counties)].copy()
            logger.info(f"Found AMI data for {len(texas_ami)} target counties: {texas_ami['County'].unique()}")
            
            return texas_ami
        except Exception as e:
            logger.error(f"Error loading HUD AMI data: {e}")
            return None
    
    def get_ami_rents_for_county(self, county_name):
        """Get 50%, 60%, 80% AMI rents for a specific county"""
        try:
            county_data = self.hud_ami_data[self.hud_ami_data['County'].str.contains(county_name, na=False, case=False)]
            
            if county_data.empty:
                logger.warning(f"No AMI data found for {county_name} County")
                return None
            
            # Extract rent data for different AMI levels and unit types using correct column names
            row = county_data.iloc[0] if len(county_data) > 0 else None
            
            ami_rents = {
                'county': county_name,
                '50_ami_studio': row['Studio 50%'] if row is not None and 'Studio 50%' in county_data.columns else 0,
                '50_ami_1br': row['1BR 50%'] if row is not None and '1BR 50%' in county_data.columns else 0,
                '50_ami_2br': row['2BR 50%'] if row is not None and '2BR 50%' in county_data.columns else 0,
                '50_ami_3br': row['3BR 50%'] if row is not None and '3BR 50%' in county_data.columns else 0,
                '60_ami_studio': row['Studio 60%'] if row is not None and 'Studio 60%' in county_data.columns else 0,
                '60_ami_1br': row['1BR 60%'] if row is not None and '1BR 60%' in county_data.columns else 0,
                '60_ami_2br': row['2BR 60%'] if row is not None and '2BR 60%' in county_data.columns else 0,
                '60_ami_3br': row['3BR 60%'] if row is not None and '3BR 60%' in county_data.columns else 0,
                # Calculate 80% AMI (derived from 60% AMI * 1.33)
                '80_ami_studio': (row['Studio 60%'] * 1.33) if row is not None and 'Studio 60%' in county_data.columns else 0,
                '80_ami_1br': (row['1BR 60%'] * 1.33) if row is not None and '1BR 60%' in county_data.columns else 0,
                '80_ami_2br': (row['2BR 60%'] * 1.33) if row is not None and '2BR 60%' in county_data.columns else 0,
                '80_ami_3br': (row['3BR 60%'] * 1.33) if row is not None and '3BR 60%' in county_data.columns else 0,
            }
            
            return ami_rents
        except Exception as e:
            logger.error(f"Error getting AMI rents for {county_name}: {e}")
            return None
    
    def geocode_address(self, address, city, state="TX"):
        """Geocode address using Census Geocoding API"""
        try:
            # Check cache first
            cache_key = f"{address}_{city}_{state}".replace(" ", "_").replace(",", "")
            cache_file = f"{self.cache_dir}/geocode_{cache_key}.json"
            
            if Path(cache_file).exists():
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    if cached_data.get('lat') and cached_data.get('lng'):
                        return cached_data['lat'], cached_data['lng']
            
            # Census Geocoding API
            full_address = f"{address}, {city}, {state}"
            url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
            params = {
                'address': full_address,
                'benchmark': 'Public_AR_Current',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('result', {}).get('addressMatches'):
                    match = data['result']['addressMatches'][0]
                    lat = match['coordinates']['y']
                    lng = match['coordinates']['x']
                    
                    # Cache the result
                    cache_data = {'lat': lat, 'lng': lng, 'address': full_address}
                    with open(cache_file, 'w') as f:
                        json.dump(cache_data, f)
                    
                    return lat, lng
            
            logger.warning(f"Geocoding failed for {full_address}")
            return None, None
            
        except Exception as e:
            logger.error(f"Error geocoding {address}, {city}: {e}")
            return None, None
    
    def get_census_tract(self, lat, lng):
        """Get census tract for coordinates using FCC API"""
        try:
            if not lat or not lng:
                return None
            
            # Cache key
            cache_key = f"tract_{lat:.6f}_{lng:.6f}".replace(".", "_")
            cache_file = f"{self.cache_dir}/census_tract_{cache_key}.json"
            
            if Path(cache_file).exists():
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    return cached_data.get('tract')
            
            # FCC Area API for census tract
            url = "https://geo.fcc.gov/api/census/area"
            params = {
                'lat': lat,
                'lon': lng,
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('results') and len(data['results']) > 0:
                    tract = data['results'][0].get('block_fips', '')[:11]  # First 11 digits = tract
                    
                    # Cache the result
                    cache_data = {'tract': tract, 'lat': lat, 'lng': lng}
                    with open(cache_file, 'w') as f:
                        json.dump(cache_data, f)
                    
                    return tract
            
            logger.warning(f"Census tract lookup failed for {lat}, {lng}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting census tract for {lat}, {lng}: {e}")
            return None
    
    def get_census_poverty_data(self, tract_fips):
        """Get poverty rate for census tract using ACS API"""
        try:
            if not tract_fips or len(tract_fips) != 11:
                return None
            
            # Cache key
            cache_file = f"{self.cache_dir}/poverty_{tract_fips}.json"
            
            if Path(cache_file).exists():
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    return cached_data.get('poverty_rate')
            
            # Parse FIPS components
            state_fips = tract_fips[:2]  # First 2 digits
            county_fips = tract_fips[2:5]  # Next 3 digits  
            tract_code = tract_fips[5:11]  # Last 6 digits
            
            # ACS API for poverty data
            url = "https://api.census.gov/data/2022/acs/acs5"
            params = {
                'get': 'S1701_C03_001E',  # Poverty rate
                'for': f'tract:{tract_code}',
                'in': f'state:{state_fips} county:{county_fips}',
                'key': self.census_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:  # Header + data row
                    poverty_rate = float(data[1][0]) if data[1][0] and data[1][0] != '-' else None
                    
                    # Cache the result
                    cache_data = {'poverty_rate': poverty_rate, 'tract_fips': tract_fips}
                    with open(cache_file, 'w') as f:
                        json.dump(cache_data, f)
                    
                    return poverty_rate
            
            logger.warning(f"Poverty data lookup failed for tract {tract_fips}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting poverty data for tract {tract_fips}: {e}")
            return None
    
    def get_census_demographics(self, tract_fips):
        """Get additional demographic data for census tract"""
        try:
            if not tract_fips or len(tract_fips) != 11:
                return {}
            
            # Cache key
            cache_file = f"{self.cache_dir}/demographics_{tract_fips}.json"
            
            if Path(cache_file).exists():
                with open(cache_file, 'r') as f:
                    return json.load(f)
            
            # Parse FIPS components
            state_fips = tract_fips[:2]
            county_fips = tract_fips[2:5]
            tract_code = tract_fips[5:11]
            
            # ACS API for demographic data
            url = "https://api.census.gov/data/2022/acs/acs5"
            params = {
                'get': 'B25003_001E,B25003_002E,B25003_003E,B19013_001E,B08301_010E,B08301_021E,B25064_001E',  
                # Total housing, owner-occupied, renter-occupied, median income, public transit, work from home, median rent
                'for': f'tract:{tract_code}',
                'in': f'state:{state_fips} county:{county_fips}',
                'key': self.census_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:
                    row = data[1]
                    demographics = {
                        'total_housing_units': int(row[0]) if row[0] and row[0] != '-' else 0,
                        'owner_occupied': int(row[1]) if row[1] and row[1] != '-' else 0,
                        'renter_occupied': int(row[2]) if row[2] and row[2] != '-' else 0,
                        'median_household_income': int(row[3]) if row[3] and row[3] != '-' else 0,
                        'public_transit_commuters': int(row[4]) if row[4] and row[4] != '-' else 0,
                        'work_from_home': int(row[5]) if row[5] and row[5] != '-' else 0,
                        'median_rent': int(row[6]) if row[6] and row[6] != '-' else 0,
                        'tract_fips': tract_fips
                    }
                    
                    # Cache the result
                    with open(cache_file, 'w') as f:
                        json.dump(demographics, f)
                    
                    return demographics
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting demographics for tract {tract_fips}: {e}")
            return {}
    
    def analyze_properties(self):
        """Main analysis function"""
        if not self.load_property_data():
            logger.error("Failed to load property data")
            return
        
        # Load HUD AMI data
        ami_data = self.load_hud_ami_data()
        if ami_data is None:
            logger.error("Failed to load HUD AMI data")
            return
        
        # Analysis results list
        analysis_results = []
        
        for idx, property_row in self.properties_df.iterrows():
            logger.info(f"Analyzing property: {property_row['Property_Name']}")
            
            result = {
                'property_name': property_row['Property_Name'],
                'address': property_row['Address'],
                'city': property_row['City'],
                'county': property_row['County'],
                'units': property_row['Units'],
                'current_rent_range': property_row['Current_Rent_Range'],
                'hb21_risk_level': property_row['HB21_Risk_Level'],
                'conversion_priority': property_row['Conversion_Priority']
            }
            
            # Get AMI rents for county
            ami_rents = self.get_ami_rents_for_county(property_row['County'])
            if ami_rents:
                result.update(ami_rents)
            
            # Geocode address
            if pd.notna(property_row['Address']) and property_row['Address'] != 'TBD':
                lat, lng = self.geocode_address(property_row['Address'], property_row['City'])
                result['latitude'] = lat
                result['longitude'] = lng
                
                # Get census tract and poverty data
                if lat and lng:
                    tract_fips = self.get_census_tract(lat, lng)
                    result['census_tract'] = tract_fips
                    
                    if tract_fips:
                        poverty_rate = self.get_census_poverty_data(tract_fips)
                        result['poverty_rate'] = poverty_rate
                        
                        demographics = self.get_census_demographics(tract_fips)
                        result.update(demographics)
                        
                        # LIHTC eligibility flags
                        result['lihtc_low_poverty_bonus'] = poverty_rate <= 20.0 if poverty_rate else False
            
            analysis_results.append(result)
            
            # Rate limiting
            time.sleep(1)
        
        # Convert to DataFrame and save
        results_df = pd.DataFrame(analysis_results)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{self.output_path}/analysis_outputs/HFC_Property_Analysis_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            results_df.to_excel(writer, sheet_name='Property_Analysis', index=False)
            
            # Create AMI comparison sheet
            ami_comparison = self.create_ami_comparison(results_df)
            ami_comparison.to_excel(writer, sheet_name='AMI_Rent_Analysis', index=False)
            
            # Create summary sheet
            summary = self.create_summary_analysis(results_df)
            summary.to_excel(writer, sheet_name='Executive_Summary', index=False)
        
        logger.info(f"Analysis complete. Results saved to: {output_file}")
        return results_df
    
    def create_ami_comparison(self, results_df):
        """Create AMI rent comparison analysis"""
        ami_comparison = []
        
        for _, row in results_df.iterrows():
            if pd.notna(row.get('60_ami_2br', 0)) and row.get('60_ami_2br', 0) > 0:
                # Parse current rent range to get midpoint
                rent_range = str(row.get('current_rent_range', ''))
                current_rent_mid = self.parse_rent_midpoint(rent_range)
                
                comparison = {
                    'property_name': row['property_name'],
                    'county': row['county'],
                    'current_rent_midpoint': current_rent_mid,
                    '50_ami_2br_rent': row.get('50_ami_2br', 0),
                    '60_ami_2br_rent': row.get('60_ami_2br', 0),
                    '80_ami_2br_rent': row.get('80_ami_2br', 0),
                    'gap_to_60_ami': current_rent_mid - row.get('60_ami_2br', 0) if current_rent_mid else 0,
                    'gap_to_80_ami': current_rent_mid - row.get('80_ami_2br', 0) if current_rent_mid else 0,
                    'feasible_50_ami': current_rent_mid <= row.get('50_ami_2br', 0) if current_rent_mid else False,
                    'feasible_60_ami': current_rent_mid <= row.get('60_ami_2br', 0) if current_rent_mid else False,
                    'feasible_80_ami': current_rent_mid <= row.get('80_ami_2br', 0) if current_rent_mid else False,
                }
                
                ami_comparison.append(comparison)
        
        return pd.DataFrame(ami_comparison)
    
    def parse_rent_midpoint(self, rent_range_str):
        """Parse rent range string to get midpoint"""
        try:
            # Remove $ and , and split on -
            cleaned = rent_range_str.replace('$', '').replace(',', '')
            if '-' in cleaned:
                parts = cleaned.split('-')
                if len(parts) == 2:
                    low = float(parts[0])
                    high = float(parts[1])
                    return (low + high) / 2
            return None
        except:
            return None
    
    def create_summary_analysis(self, results_df):
        """Create executive summary analysis"""
        summary_data = []
        
        # Overall portfolio summary
        total_properties = len(results_df)
        total_units = results_df['units'].sum()
        high_risk_properties = len(results_df[results_df['hb21_risk_level'] == 'HIGH'])
        
        summary_data.append({
            'metric': 'Total Properties',
            'value': total_properties,
            'notes': 'Properties identified in HFC distressed portfolio'
        })
        
        summary_data.append({
            'metric': 'Total Units',
            'value': total_units,
            'notes': 'Combined unit count across all properties'
        })
        
        summary_data.append({
            'metric': 'High Risk Properties',
            'value': high_risk_properties,
            'notes': 'Properties with HIGH HB21 tax liability risk'
        })
        
        # Counties represented
        counties = results_df['county'].unique()
        summary_data.append({
            'metric': 'Counties Represented',
            'value': len(counties),
            'notes': ', '.join(counties)
        })
        
        # LIHTC eligibility
        low_poverty_eligible = len(results_df[results_df.get('lihtc_low_poverty_bonus', False) == True])
        summary_data.append({
            'metric': 'Low Poverty Bonus Eligible',
            'value': low_poverty_eligible,
            'notes': 'Properties in census tracts with ≤20% poverty rate'
        })
        
        return pd.DataFrame(summary_data)

def main():
    """Main execution function"""
    analyzer = HFCPropertyAnalyzer()
    results = analyzer.analyze_properties()
    
    if results is not None:
        print(f"\nAnalysis completed successfully!")
        print(f"Analyzed {len(results)} properties")
        print(f"Results saved to: {analyzer.output_path}/analysis_outputs/")
    else:
        print("Analysis failed. Check logs for details.")

if __name__ == "__main__":
    main()