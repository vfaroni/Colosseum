#!/usr/bin/env python3
"""
Arizona USDA Rural Development Properties Analyzer
Analyzes 5 properties for LIHTC eligibility factors
"""

import json
import requests
import pandas as pd
import geopandas as gpd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime
import time
from pathlib import Path

class ArizonaRuralAnalyzer:
    def __init__(self):
        self.properties = [
            {
                "name": "Mt. Graham",
                "address": "2040 S Twentieth Avenue, Safford, AZ",
                "units": 40,
                "rental_assistance": 36
            },
            {
                "name": "Safford Villa", 
                "address": "106 W 11th Street, Safford, AZ",
                "units": 24,
                "rental_assistance": 24
            },
            {
                "name": "Willcox Villa",
                "address": "201 N. Bisbee Ave, Wilcox, AZ",  
                "units": 24,
                "rental_assistance": 24
            },
            {
                "name": "Cochise Apts",
                "address": "650 W. Union Street, Benson, AZ",
                "units": 24,
                "rental_assistance": 23
            },
            {
                "name": "United Church Village Apts",
                "address": "320 E Placita Naco Cir, Nogales, AZ 85621",
                "units": 48,
                "rental_assistance": 48
            }
        ]
        
        # API Keys
        self.positionstack_key = "41b80ed51d92978904592126d2bb8f7e"
        self.census_key = "06ece0121263282cd9ffd753215b007b8f9a3dfc"
        
        # Data paths
        self.base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets")
        self.qct_dda_path = self.base_path / "federal/HUD_QCT_DDA_Data/HUD_DDA_QCT_2025_Combined.gpkg"
        self.ami_path = self.base_path / "federal/HUD_AMI_Geographic/HUD2025_AMI_Rent_Data_Static.xlsx"
        self.poverty_path = self.base_path / "environmental/Poverty Rate Census Tracts (ACS)/poverty_tracts_AZ_2022.gpkg"
        
        # Results storage
        self.results = []
        
    def geocode_property_free(self, address):
        """Geocode using free Nominatim service first"""
        print(f"  📍 Attempting free geocoding for: {address}")
        
        try:
            geolocator = Nominatim(user_agent="arizona_rural_development_analyzer")
            location = geolocator.geocode(address, timeout=10)
            
            if location:
                print(f"  ✅ Free geocoding successful: {location.latitude}, {location.longitude}")
                return location.latitude, location.longitude
            else:
                print("  ❌ Free geocoding failed, trying PositionStack...")
                return None
                
        except Exception as e:
            print(f"  ❌ Free geocoding error: {e}")
            return None
    
    def geocode_property_positionstack(self, address):
        """Geocode using PositionStack API as fallback"""
        print(f"  📍 Using PositionStack API for: {address}")
        
        try:
            url = "http://api.positionstack.com/v1/forward"
            params = {
                'access_key': self.positionstack_key,
                'query': address,
                'limit': 1,
                'country': 'US',
                'region': 'Arizona'
            }
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                result = data['data'][0]
                lat = result['latitude']
                lon = result['longitude']
                print(f"  ✅ PositionStack success: {lat}, {lon}")
                return lat, lon
            else:
                print(f"  ❌ PositionStack failed: No results")
                return None
                
        except Exception as e:
            print(f"  ❌ PositionStack error: {e}")
            return None
    
    def get_census_tract(self, lat, lon):
        """Get census tract from coordinates"""
        try:
            url = f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
            params = {
                'x': lon,
                'y': lat,
                'benchmark': 'Public_AR_Current',
                'vintage': 'Current_Current',
                'layers': '2020 Census Tracts',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'result' in data and 'geographies' in data['result']:
                tracts = data['result']['geographies'].get('2020 Census Tracts', [])
                if tracts:
                    tract = tracts[0]
                    return {
                        'state_fips': tract['STATE'],
                        'county_fips': tract['COUNTY'],
                        'tract': tract['TRACT'],
                        'geoid': tract['GEOID'],
                        'county_name': tract.get('COUNTY_NAME', 'Unknown'),
                        'state_name': tract.get('STATE_NAME', 'Arizona')
                    }
            return None
            
        except Exception as e:
            print(f"  ❌ Census tract lookup error: {e}")
            return None
    
    def check_qct_dda_status(self, lat, lon):
        """Check if location is in QCT or DDA"""
        try:
            # Load QCT/DDA data
            qct_dda = gpd.read_file(self.qct_dda_path)
            
            # Create point
            from shapely.geometry import Point
            point = gpd.GeoDataFrame([1], geometry=[Point(lon, lat)], crs='EPSG:4326')
            
            # Project to match QCT/DDA CRS
            if qct_dda.crs != point.crs:
                point = point.to_crs(qct_dda.crs)
            
            # Check intersections
            in_qct = False
            in_dda = False
            
            for idx, row in qct_dda.iterrows():
                if point.geometry[0].within(row.geometry):
                    if row.get('QCT_FLAG') == 1 or row.get('is_qct') == 1:
                        in_qct = True
                    if row.get('DDA_FLAG') == 1 or row.get('is_dda') == 1:
                        in_dda = True
            
            return {'is_qct': in_qct, 'is_dda': in_dda}
            
        except Exception as e:
            print(f"  ❌ QCT/DDA check error: {e}")
            return {'is_qct': False, 'is_dda': False}
    
    def get_ami_data(self, county_name):
        """Get HUD AMI data for county"""
        try:
            # Load AMI data
            ami_df = pd.read_excel(self.ami_path, sheet_name='FY2025 AMI')
            
            # Find county
            county_match = ami_df[ami_df['countyname'].str.contains(county_name, case=False, na=False)]
            
            if not county_match.empty:
                row = county_match.iloc[0]
                
                # Calculate 60% AMI rents using correct HUD methodology
                ami_100_4person = row['l50_4']  # 50% of AMI for 4-person household
                ami_100_4person = ami_100_4person * 2  # Convert to 100% AMI
                
                # Get income limits at 60% AMI
                income_1p = row['l50_1'] * 1.2  # 60% AMI for 1 person
                income_2p = row['l50_2'] * 1.2  # 60% AMI for 2 person
                income_3p = row['l50_3'] * 1.2  # 60% AMI for 3 person
                income_4p = row['l50_4'] * 1.2  # 60% AMI for 4 person
                income_5p = row['l50_5'] * 1.2  # 60% AMI for 5 person
                income_6p = row['l50_6'] * 1.2  # 60% AMI for 6 person
                
                # Calculate rents using correct household sizes
                # Studio = 1.0 person
                rent_0br = int((income_1p * 0.30) / 12)
                
                # 1BR = 1.5 persons (interpolate)
                income_1p5 = income_1p + 0.5 * (income_2p - income_1p)
                rent_1br = int((income_1p5 * 0.30) / 12)
                
                # 2BR = 3.0 persons
                rent_2br = int((income_3p * 0.30) / 12)
                
                # 3BR = 4.5 persons (interpolate)
                income_4p5 = income_4p + 0.5 * (income_5p - income_4p)
                rent_3br = int((income_4p5 * 0.30) / 12)
                
                # 4BR = 6.0 persons
                rent_4br = int((income_6p * 0.30) / 12)
                
                return {
                    'ami_100_4person': ami_100_4person,
                    'rent_0br_60': rent_0br,
                    'rent_1br_60': rent_1br,
                    'rent_2br_60': rent_2br,
                    'rent_3br_60': rent_3br,
                    'rent_4br_60': rent_4br,
                    'metro_area': row.get('metro_area_name', 'Non-Metropolitan')
                }
            
            return None
            
        except Exception as e:
            print(f"  ❌ AMI data error: {e}")
            return None
    
    def get_poverty_rate(self, geoid):
        """Get poverty rate for census tract"""
        try:
            # Load poverty data
            poverty_gdf = gpd.read_file(self.poverty_path)
            
            # Find tract
            tract_data = poverty_gdf[poverty_gdf['GEOID'] == geoid]
            
            if not tract_data.empty:
                poverty_rate = tract_data.iloc[0].get('poverty_rate', None)
                return poverty_rate
            
            return None
            
        except Exception as e:
            print(f"  ❌ Poverty data error: {e}")
            return None
    
    def analyze_properties(self):
        """Analyze all properties"""
        print("\n🏢 ARIZONA USDA RURAL DEVELOPMENT PROPERTIES ANALYSIS")
        print("=" * 60)
        
        for prop in self.properties:
            print(f"\n📊 Analyzing: {prop['name']}")
            print(f"   Address: {prop['address']}")
            print(f"   Units: {prop['units']} (RA: {prop['rental_assistance']})")
            
            # Step 1: Geocode
            coords = self.geocode_property_free(prop['address'])
            if not coords:
                coords = self.geocode_property_positionstack(prop['address'])
            
            if coords:
                lat, lon = coords
                prop['latitude'] = lat
                prop['longitude'] = lon
                
                # Step 2: Get census tract
                tract_info = self.get_census_tract(lat, lon)
                if tract_info:
                    prop['census_tract'] = tract_info['tract']
                    prop['geoid'] = tract_info['geoid']
                    prop['county'] = tract_info['county_name']
                    print(f"   Census Tract: {tract_info['geoid']}")
                    print(f"   County: {tract_info['county_name']}")
                
                # Step 3: Check QCT/DDA
                qct_dda = self.check_qct_dda_status(lat, lon)
                prop['is_qct'] = qct_dda['is_qct']
                prop['is_dda'] = qct_dda['is_dda']
                status = []
                if qct_dda['is_qct']:
                    status.append("QCT")
                if qct_dda['is_dda']:
                    status.append("DDA")
                if not status:
                    status.append("Neither")
                print(f"   QCT/DDA Status: {', '.join(status)}")
                
                # Step 4: Get AMI data
                if tract_info:
                    ami_data = self.get_ami_data(tract_info['county_name'])
                    if ami_data:
                        prop['ami_100_4person'] = ami_data['ami_100_4person']
                        prop['rent_1br_60'] = ami_data['rent_1br_60']
                        prop['rent_2br_60'] = ami_data['rent_2br_60']
                        prop['rent_3br_60'] = ami_data['rent_3br_60']
                        prop['rent_4br_60'] = ami_data['rent_4br_60']
                        prop['metro_area'] = ami_data['metro_area']
                        
                        print(f"   4-Person 100% AMI: ${ami_data['ami_100_4person']:,}")
                        print(f"   60% AMI Rents: 1BR=${ami_data['rent_1br_60']}, 2BR=${ami_data['rent_2br_60']}, 3BR=${ami_data['rent_3br_60']}, 4BR=${ami_data['rent_4br_60']}")
                
                # Step 5: Get poverty rate
                if tract_info:
                    poverty_rate = self.get_poverty_rate(tract_info['geoid'])
                    if poverty_rate is not None:
                        prop['poverty_rate'] = poverty_rate
                        print(f"   Poverty Rate: {poverty_rate:.1f}%")
                
                # Add to results
                self.results.append(prop)
                
            else:
                print(f"  ❌ Failed to geocode property")
            
            # Rate limit
            time.sleep(1)
        
        return self.results
    
    def save_results(self):
        """Save results to Excel and JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Convert to DataFrame
        df = pd.DataFrame(self.results)
        
        # Save Excel
        excel_path = f"Arizona_Rural_Development_Analysis_{timestamp}.xlsx"
        df.to_excel(excel_path, index=False)
        print(f"\n✅ Results saved to: {excel_path}")
        
        # Save JSON
        json_path = f"Arizona_Rural_Development_Analysis_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"✅ JSON saved to: {json_path}")
        
        return excel_path, json_path

if __name__ == "__main__":
    analyzer = ArizonaRuralAnalyzer()
    results = analyzer.analyze_properties()
    analyzer.save_results()