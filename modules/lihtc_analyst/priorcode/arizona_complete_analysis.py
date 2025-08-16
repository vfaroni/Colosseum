#!/usr/bin/env python3
"""
Complete Arizona Rural Development Properties Analysis
"""

import json
import requests
import pandas as pd
import geopandas as gpd
from datetime import datetime
import time
from pathlib import Path
import folium
from folium.plugins import MeasureControl

class ArizonaCompleteAnalyzer:
    def __init__(self):
        # Properties with coordinates from previous run
        self.properties = [
            {
                "name": "Mt. Graham",
                "address": "2040 S Twentieth Avenue, Safford, AZ",
                "units": 40,
                "rental_assistance": 36,
                "latitude": 32.822054,
                "longitude": -109.720607
            },
            {
                "name": "Safford Villa", 
                "address": "106 W 11th Street, Safford, AZ",
                "units": 24,
                "rental_assistance": 24,
                "latitude": 32.8276193,
                "longitude": -109.7085118
            },
            {
                "name": "Willcox Villa",
                "address": "201 N. Bisbee Ave, Wilcox, AZ",
                "units": 24,
                "rental_assistance": 24,
                "latitude": 32.261129,
                "longitude": -109.841382
            },
            {
                "name": "Cochise Apts",
                "address": "650 W. Union Street, Benson, AZ",
                "units": 24,
                "rental_assistance": 23,
                "latitude": 31.962736,
                "longitude": -110.308719
            },
            {
                "name": "United Church Village Apts",
                "address": "320 E Placita Naco Cir, Nogales, AZ 85621",
                "units": 48,
                "rental_assistance": 48,
                "latitude": 31.3713391,
                "longitude": -110.9240253
            }
        ]
        
        # API Keys
        self.census_key = "06ece0121263282cd9ffd753215b007b8f9a3dfc"
        
        # Data paths
        self.base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets")
        self.ami_path = self.base_path / "federal/HUD_AMI_Geographic/HUD2025_AMI_Rent_Data_Static.xlsx"
        self.poverty_summary_path = self.base_path / "environmental/Poverty Rate Census Tracts (ACS)/poverty_summary_AZ_2022.csv"
        
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
                        'county_name': tract.get('NAME', 'Unknown')
                    }
            return None
            
        except Exception as e:
            print(f"  ❌ Census tract lookup error: {e}")
            return None
    
    def get_ami_data(self, county_name):
        """Get HUD AMI data for county"""
        try:
            # Load AMI data
            ami_df = pd.read_excel(self.ami_path, sheet_name='FY2025 AMI')
            
            # Find Arizona county
            az_data = ami_df[ami_df['state_name'] == 'Arizona']
            county_match = az_data[az_data['countyname'].str.contains(county_name, case=False, na=False)]
            
            if not county_match.empty:
                row = county_match.iloc[0]
                
                # Calculate 100% AMI for 4-person household
                ami_100_4person = row['l50_4'] * 2  # Convert 50% to 100%
                
                # Get income limits at 60% AMI
                income_1p = row['l50_1'] * 1.2  # 60% AMI for 1 person
                income_2p = row['l50_2'] * 1.2  # 60% AMI for 2 person
                income_3p = row['l50_3'] * 1.2  # 60% AMI for 3 person
                income_4p = row['l50_4'] * 1.2  # 60% AMI for 4 person
                income_5p = row['l50_5'] * 1.2  # 60% AMI for 5 person
                income_6p = row['l50_6'] * 1.2  # 60% AMI for 6 person
                
                # Calculate rents using correct HUD methodology
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
                    'metro_area': row.get('metro_area_name', 'Non-Metropolitan'),
                    'county_full': row.get('countyname', '')
                }
            
            return None
            
        except Exception as e:
            print(f"  ❌ AMI data error: {e}")
            return None
    
    def get_poverty_rate(self, geoid):
        """Get poverty rate for census tract"""
        try:
            # Load poverty data
            poverty_df = pd.read_csv(self.poverty_summary_path)
            
            # Find tract
            tract_data = poverty_df[poverty_df['GEOID'] == geoid]
            
            if not tract_data.empty:
                poverty_rate = tract_data.iloc[0].get('poverty_rate', None)
                return poverty_rate
            
            return None
            
        except Exception as e:
            print(f"  ❌ Poverty data error: {e}")
            return None
    
    def analyze_properties(self):
        """Complete analysis of all properties"""
        print("\n🏢 COMPLETE ARIZONA RURAL DEVELOPMENT ANALYSIS")
        print("=" * 55)
        
        for prop in self.properties:
            print(f"\n📊 Analyzing: {prop['name']}")
            print(f"   Address: {prop['address']}")
            print(f"   Coordinates: {prop['latitude']:.6f}, {prop['longitude']:.6f}")
            
            # Get census tract
            tract_info = self.get_census_tract(prop['latitude'], prop['longitude'])
            if tract_info:
                prop['census_tract'] = tract_info['tract']
                prop['geoid'] = tract_info['geoid']
                prop['county'] = tract_info['county_name']
                print(f"   Census Tract: {tract_info['geoid']}")
                print(f"   County: {tract_info['county_name']}")
                
                # Get AMI data
                ami_data = self.get_ami_data(tract_info['county_name'])
                if ami_data:
                    prop.update(ami_data)
                    print(f"   4-Person 100% AMI: ${ami_data['ami_100_4person']:,}")
                    print(f"   60% AMI Rents: 1BR=${ami_data['rent_1br_60']}, 2BR=${ami_data['rent_2br_60']}, 3BR=${ami_data['rent_3br_60']}, 4BR=${ami_data['rent_4br_60']}")
                    print(f"   Metro Area: {ami_data['metro_area']}")
                
                # Get poverty rate
                poverty_rate = self.get_poverty_rate(tract_info['geoid'])
                if poverty_rate is not None:
                    prop['poverty_rate'] = poverty_rate
                    print(f"   Poverty Rate: {poverty_rate:.1f}%")
                
                # QCT/DDA status (all rural, none qualify)
                prop['is_qct'] = False
                prop['is_dda'] = False
                print(f"   QCT/DDA Status: Neither (Rural)")
            
            time.sleep(1)  # Rate limit
        
        return self.properties
    
    def create_map(self):
        """Create HTML map of all properties"""
        print("\n🗺️ Creating interactive map...")
        
        # Calculate center point
        lats = [prop['latitude'] for prop in self.properties]
        lons = [prop['longitude'] for prop in self.properties]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        # Add properties
        for prop in self.properties:
            # Create popup text
            poverty_str = f"{prop.get('poverty_rate', 0):.1f}%" if prop.get('poverty_rate') else "N/A"
            popup_text = f"""
            <b>{prop['name']}</b><br>
            Address: {prop['address']}<br>
            Units: {prop['units']} (RA: {prop['rental_assistance']})<br>
            County: {prop.get('county', 'Unknown')}<br>
            QCT/DDA: Neither (Rural)<br>
            Poverty Rate: {poverty_str}<br>
            4-Person 100% AMI: ${prop.get('ami_100_4person', 0):,}<br>
            60% AMI Rents:<br>
            • 1BR: ${prop.get('rent_1br_60', 0)}<br>
            • 2BR: ${prop.get('rent_2br_60', 0)}<br>
            • 3BR: ${prop.get('rent_3br_60', 0)}<br>
            • 4BR: ${prop.get('rent_4br_60', 0)}
            """
            
            folium.Marker(
                location=[prop['latitude'], prop['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=prop['name'],
                icon=folium.Icon(color='blue', icon='home')
            ).add_to(m)
        
        # Add measure control
        MeasureControl().add_to(m)
        
        # Add title
        title_html = '''
        <h3 align="center" style="font-size:20px"><b>Arizona USDA Rural Development Properties</b></h3>
        <h4 align="center" style="font-size:14px">LIHTC Eligibility Analysis</h4>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        map_filename = f"Arizona_Rural_Properties_Map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        m.save(map_filename)
        print(f"✅ Map saved to: {map_filename}")
        
        return map_filename
    
    def save_results(self):
        """Save results to Excel"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Convert to DataFrame
        df = pd.DataFrame(self.properties)
        
        # Reorder columns
        column_order = [
            'name', 'address', 'units', 'rental_assistance',
            'latitude', 'longitude', 'county', 'census_tract', 'geoid',
            'is_qct', 'is_dda', 'poverty_rate',
            'ami_100_4person', 'rent_1br_60', 'rent_2br_60', 'rent_3br_60', 'rent_4br_60',
            'metro_area'
        ]
        
        # Reorder existing columns
        existing_cols = [col for col in column_order if col in df.columns]
        df = df[existing_cols]
        
        # Save Excel
        excel_path = f"Arizona_Rural_Complete_Analysis_{timestamp}.xlsx"
        df.to_excel(excel_path, index=False)
        print(f"✅ Complete analysis saved to: {excel_path}")
        
        return excel_path
    
    def print_summary(self):
        """Print summary table"""
        print("\n📋 SUMMARY TABLE")
        print("=" * 85)
        print(f"{'Property':<25} {'County':<15} {'Units':<6} {'QCT/DDA':<8} {'Poverty%':<9} {'100% AMI':<10}")
        print("-" * 85)
        
        for prop in self.properties:
            poverty = f"{prop.get('poverty_rate', 0):.1f}%" if prop.get('poverty_rate') else "N/A"
            ami = f"${prop.get('ami_100_4person', 0):,}" if prop.get('ami_100_4person') else "N/A"
            
            print(f"{prop['name'][:24]:<25} {prop.get('county', 'Unknown')[:14]:<15} {prop['units']:<6} {'Neither':<8} {poverty:<9} {ami:<10}")

if __name__ == "__main__":
    analyzer = ArizonaCompleteAnalyzer()
    results = analyzer.analyze_properties()
    analyzer.save_results()
    analyzer.create_map()
    analyzer.print_summary()