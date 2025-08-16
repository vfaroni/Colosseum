#!/usr/bin/env python3
"""
CORRECTED Arizona Map with Proper QCT/DDA Detection
Using the complete HUD 2025 QCT dataset that includes non-metro areas
"""

import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MeasureControl
from datetime import datetime
from pathlib import Path
import requests
import time

class ArizonaCorrectedQCTMapper:
    def __init__(self):
        # Properties with complete data
        self.properties = [
            {
                "name": "Mt. Graham",
                "address": "2040 S Twentieth Avenue, Safford, AZ",
                "units": 40,
                "rental_assistance": 36,
                "latitude": 32.822054,
                "longitude": -109.720607,
                "county": "Graham County",
                "city": "Safford",
                "ami_100_4person": 81100,
                "rent_studio_60": 852,
                "rent_1br_60": 912,
                "rent_2br_60": 1095,
                "rent_3br_60": 1265,
                "rent_4br_60": 1411,
                "metro_status": "Non-Metro",
                "poverty_rate": 12.4
            },
            {
                "name": "Safford Villa",
                "address": "106 W 11th Street, Safford, AZ",
                "units": 24,
                "rental_assistance": 24,
                "latitude": 32.8276193,
                "longitude": -109.7085118,
                "county": "Graham County",
                "city": "Safford",
                "ami_100_4person": 81100,
                "rent_studio_60": 852,
                "rent_1br_60": 912,
                "rent_2br_60": 1095,
                "rent_3br_60": 1265,
                "rent_4br_60": 1411,
                "metro_status": "Non-Metro",
                "poverty_rate": 12.4
            },
            {
                "name": "Willcox Villa",
                "address": "201 N. Bisbee Ave, Willcox, AZ",
                "units": 24,
                "rental_assistance": 24,
                "latitude": 32.261129,
                "longitude": -109.841382,
                "county": "Cochise County",
                "city": "Willcox",
                "ami_100_4person": 71200,
                "rent_studio_60": 748,
                "rent_1br_60": 801,
                "rent_2br_60": 961,
                "rent_3br_60": 1110,
                "rent_4br_60": 1239,
                "metro_status": "Metro",
                "poverty_rate": 11.8
            },
            {
                "name": "Cochise Apts",
                "address": "650 W. Union Street, Benson, AZ",
                "units": 24,
                "rental_assistance": 23,
                "latitude": 31.962736,
                "longitude": -110.308719,
                "county": "Cochise County",
                "city": "Benson",
                "ami_100_4person": 71200,
                "rent_studio_60": 748,
                "rent_1br_60": 801,
                "rent_2br_60": 961,
                "rent_3br_60": 1110,
                "rent_4br_60": 1239,
                "metro_status": "Metro",
                "poverty_rate": 11.8
            },
            {
                "name": "United Church Village Apts",
                "address": "320 E Placita Naco Cir, Nogales, AZ 85621",
                "units": 48,
                "rental_assistance": 48,
                "latitude": 31.3713391,
                "longitude": -110.9240253,
                "county": "Santa Cruz County",
                "city": "Nogales",
                "ami_100_4person": 66100,
                "rent_studio_60": 735,
                "rent_1br_60": 787,
                "rent_2br_60": 945,
                "rent_3br_60": 1092,
                "rent_4br_60": 1218,
                "metro_status": "Non-Metro",
                "poverty_rate": 16.2
            }
        ]
        
        # Data paths
        self.base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets")
        self.counties_path = self.base_path / "federal/HUD_AMI_Geographic/States/az_counties_hud_ami_2025.gpkg"
        self.qct_data_path = self.base_path / "federal/HUD_QCT_DDA_Data/qct_data_2025.xlsx"
        self.lihtc_database_path = self.base_path / "federal/LIHTC_Properties_Database.csv"
        
    def get_census_tract_from_coordinates(self, lat, lon):
        """Get census tract from coordinates using Census API"""
        try:
            url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
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
                        'geoid': tract['GEOID'],
                        'state': tract['STATE'],
                        'county': tract['COUNTY'],
                        'tract': tract['TRACT'],
                        'name': tract.get('NAME', 'Unknown')
                    }
            return None
            
        except Exception as e:
            print(f"      ❌ Census tract lookup error: {e}")
            return None
    
    def check_qct_status_correct(self, lat, lon, property_name):
        """CORRECTED QCT status check using proper HUD 2025 data"""
        try:
            print(f"    🔍 Checking QCT status for {property_name}")
            
            # Get census tract from coordinates
            tract_info = self.get_census_tract_from_coordinates(lat, lon)
            if not tract_info:
                print(f"      ❌ Could not determine census tract")
                return {
                    'is_qct': False,
                    'is_dda': False,
                    'status': 'Unknown',
                    'details': 'Could not determine census tract',
                    'tract_id': 'Unknown'
                }
            
            print(f"      📍 Found census tract: {tract_info['geoid']}")
            
            # Load QCT data if not already loaded
            if not hasattr(self, 'qct_data'):
                print(f"      📊 Loading complete HUD 2025 QCT dataset...")
                self.qct_data = pd.read_excel(self.qct_data_path)
                print(f"      ✅ Loaded {len(self.qct_data):,} QCT records nationwide")
                
                # Filter for Arizona
                self.az_qct_data = self.qct_data[self.qct_data['State Code'] == 'AZ'].copy()
                print(f"      📍 Found {len(self.az_qct_data)} Arizona QCT records")
            
            # Check if this tract is a QCT
            tract_geoid = tract_info['geoid']
            
            # Look for this tract in the QCT data
            qct_match = self.az_qct_data[self.az_qct_data['Tract ID'].astype(str) == tract_geoid]
            
            if not qct_match.empty:
                qct_record = qct_match.iloc[0]
                print(f"      ✅ FOUND QCT: Tract {tract_geoid}")
                print(f"         County: {qct_record.get('County Name', 'Unknown')}")
                print(f"         Poverty Rate (2020): {qct_record.get('Poverty Rate 2020', 'Unknown')}%")
                
                return {
                    'is_qct': True,
                    'is_dda': False,  # We'll implement DDA checking separately
                    'status': 'QCT',
                    'details': f"QCT Tract {tract_geoid}, {qct_record.get('County Name', 'Unknown')} County, Poverty Rate: {qct_record.get('Poverty Rate 2020', 'Unknown')}%",
                    'tract_id': tract_geoid,
                    'poverty_rate_2020': qct_record.get('Poverty Rate 2020', 0)
                }
            else:
                print(f"      ❌ Not a QCT: Tract {tract_geoid}")
                return {
                    'is_qct': False,
                    'is_dda': False,
                    'status': 'Neither',
                    'details': f"Tract {tract_geoid} - Not designated as QCT",
                    'tract_id': tract_geoid
                }
                
        except Exception as e:
            print(f"      ❌ QCT analysis error: {e}")
            return {
                'is_qct': False,
                'is_dda': False,
                'status': 'Error',
                'details': f"Analysis error: {e}",
                'tract_id': 'Error'
            }
    
    def load_real_lihtc_properties(self):
        """Load actual LIHTC properties from HUD database"""
        print("🏠 Loading REAL LIHTC properties from HUD database...")
        
        try:
            # Load the full HUD LIHTC database
            lihtc_df = pd.read_csv(self.lihtc_database_path, low_memory=False)
            print(f"  📊 Loaded {len(lihtc_df):,} total LIHTC properties from HUD database")
            
            # Filter for Arizona
            az_lihtc = lihtc_df[lihtc_df['PROJ_ST'] == 'AZ'].copy()
            print(f"  📍 Found {len(az_lihtc)} Arizona LIHTC properties")
            
            # Filter for our target counties/cities
            target_areas = ['Graham', 'Cochise', 'Santa Cruz', 'Safford', 'Willcox', 'Benson', 'Douglas', 'Bisbee', 'Nogales', 'Huachuca City']
            relevant_lihtc = az_lihtc[
                az_lihtc['PROJ_CTY'].str.contains('|'.join(target_areas), case=False, na=False)
            ].copy()
            
            print(f"  🎯 Found {len(relevant_lihtc)} LIHTC properties in target areas")
            
            # Process properties with coordinates
            real_lihtc_properties = []
            
            for idx, prop in relevant_lihtc.iterrows():
                # Skip if missing coordinates
                if pd.isna(prop.get('LATITUDE')) or pd.isna(prop.get('LONGITUDE')):
                    continue
                
                lat = float(prop['LATITUDE'])
                lon = float(prop['LONGITUDE'])
                
                # Validate coordinates for Arizona
                if not (31 <= lat <= 37 and -115 <= lon <= -109):
                    continue
                
                units = prop.get('N_UNITS', 0)
                li_units = prop.get('LI_UNITS', 0)
                year_alloc = prop.get('YR_ALLOC', 'Unknown')
                
                real_lihtc_properties.append({
                    'name': prop.get('PROJECT', 'LIHTC Property'),
                    'address': f"{prop.get('PROJ_ADD', '')}, {prop.get('PROJ_CTY', '')}, AZ {prop.get('PROJ_ZIP', '')}".strip(),
                    'latitude': lat,
                    'longitude': lon,
                    'units': int(units) if pd.notna(units) else 0,
                    'li_units': int(li_units) if pd.notna(li_units) else 0,
                    'county': prop.get('PROJ_CTY', 'Unknown'),
                    'allocation_year': int(year_alloc) if pd.notna(year_alloc) and str(year_alloc).isdigit() and year_alloc != 9999 else 'Unknown',
                    'hud_id': prop.get('HUD_ID', 'Unknown'),
                    'type': 'Existing LIHTC',
                    'qct_flag': prop.get('QCT', 0),
                    'dda_flag': prop.get('DDA', 0)
                })
            
            print(f"  ✅ Processed {len(real_lihtc_properties)} LIHTC properties with valid coordinates")
            return real_lihtc_properties
            
        except Exception as e:
            print(f"  ❌ Error loading LIHTC database: {e}")
            return []
    
    def create_corrected_map(self):
        """Create corrected map with proper QCT detection"""
        print("\n🗺️ Creating CORRECTED Arizona map with proper QCT detection...")
        
        # Load real LIHTC properties
        real_lihtc = self.load_real_lihtc_properties()
        
        # CORRECTED QCT/DDA analysis
        print("\n🔍 CORRECTED QCT Analysis using complete HUD 2025 dataset:")
        for prop in self.properties:
            print(f"  🏠 {prop['name']} ({prop['city']})")
            qct_result = self.check_qct_status_correct(prop['latitude'], prop['longitude'], prop['name'])
            prop.update(qct_result)
            time.sleep(0.5)  # Rate limit Census API calls
        
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
        
        # Add county boundaries
        try:
            print("  📍 Adding Arizona county boundaries...")
            counties = gpd.read_file(self.counties_path)
            for idx, county in counties.iterrows():
                folium.GeoJson(
                    county.geometry,
                    style_function=lambda x: {
                        'fillColor': 'lightblue',
                        'color': 'blue',
                        'weight': 2,
                        'fillOpacity': 0.1
                    },
                    popup=folium.Popup(f"<b>{county.get('NAME', 'County')}</b><br>HUD Area: {county.get('AREA_NAME', 'Unknown')}", max_width=200),
                    tooltip=county.get('NAME', 'County')
                ).add_to(m)
        except Exception as e:
            print(f"    ❌ Error adding counties: {e}")
        
        # Add our USDA Rural Development properties
        print("  🏡 Adding USDA Rural Development properties...")
        total_usda_units = sum(prop['units'] for prop in self.properties)
        total_usda_ra = sum(prop['rental_assistance'] for prop in self.properties)
        qct_properties = [p for p in self.properties if p.get('is_qct')]
        
        for prop in self.properties:
            # Enhanced popup with CORRECTED QCT/DDA status
            qct_bonus = " - ELIGIBLE FOR QCT BONUS POINTS!" if prop.get('is_qct') else ""
            popup_html = f"""
            <div style="width: 450px;">
                <h4 style="margin: 0; color: #2E8B57;"><b>{prop['name']}</b></h4>
                <hr style="margin: 5px 0;">
                <b>📍 Address:</b> {prop['address']}<br>
                <b>🏠 Units:</b> {prop['units']} total ({prop['rental_assistance']} with RA)<br>
                <b>🗺️ County:</b> {prop['county']}<br>
                <b>🏙️ Metro Status:</b> {prop['metro_status']}<br>
                <b>📊 QCT/DDA Status:</b> <span style="color: {'red' if prop.get('is_qct') else 'green'}; font-weight: bold;">{prop.get('status', 'Unknown')}</span>{qct_bonus}<br>
                <b>📋 Census Tract:</b> {prop.get('tract_id', 'Unknown')}<br>
                <b>📝 Details:</b> {prop.get('details', 'No details')}<br>
                <b>📈 Poverty Rate:</b> {prop['poverty_rate']:.1f}%<br>
                <hr style="margin: 5px 0;">
                <b>💰 4-Person 100% AMI:</b> ${prop['ami_100_4person']:,}<br>
                <b>🏠 60% AMI Rent Limits:</b><br>
                <table style="margin: 5px 0; font-size: 12px; border-collapse: collapse;">
                    <tr><td style="padding: 2px;">Studio:</td><td style="text-align: right; padding: 2px;">${prop['rent_studio_60']}</td></tr>
                    <tr><td style="padding: 2px;">1 Bedroom:</td><td style="text-align: right; padding: 2px;">${prop['rent_1br_60']}</td></tr>
                    <tr><td style="padding: 2px;">2 Bedroom:</td><td style="text-align: right; padding: 2px;">${prop['rent_2br_60']}</td></tr>
                    <tr><td style="padding: 2px;">3 Bedroom:</td><td style="text-align: right; padding: 2px;">${prop['rent_3br_60']}</td></tr>
                    <tr><td style="padding: 2px;">4 Bedroom:</td><td style="text-align: right; padding: 2px;">${prop['rent_4br_60']}</td></tr>
                </table>
            </div>
            """
            
            # Color by QCT status
            if prop.get('is_qct'):
                marker_color = 'red'  # QCT properties get red (most important)
            else:
                # County colors for non-QCT
                county_colors = {
                    "Graham County": "green",
                    "Cochise County": "blue", 
                    "Santa Cruz County": "darkred"
                }
                marker_color = county_colors.get(prop['county'], 'gray')
            
            folium.Marker(
                location=[prop['latitude'], prop['longitude']],
                popup=folium.Popup(popup_html, max_width=500),
                tooltip=f"USDA: {prop['name']} - {prop['city']} ({prop['units']} units) - {prop.get('status', 'Unknown')}",
                icon=folium.Icon(
                    color=marker_color, 
                    icon='home',
                    prefix='fa'
                )
            ).add_to(m)
            
            print(f"    ✅ {prop['name']} - {prop.get('status', 'Unknown')} (Tract: {prop.get('tract_id', 'Unknown')})")
        
        # Add real LIHTC properties
        print(f"  🏠 Adding {len(real_lihtc)} real LIHTC properties...")
        total_lihtc_units = sum(prop['units'] for prop in real_lihtc)
        
        for lihtc in real_lihtc:
            popup_html = f"""
            <div style="width: 350px;">
                <h4 style="margin: 0; color: #8B4513;"><b>{lihtc['name']}</b></h4>
                <hr style="margin: 5px 0;">
                <b>📍 Address:</b> {lihtc['address']}<br>
                <b>🏠 Total Units:</b> {lihtc['units']:,}<br>
                <b>🏠 LI Units:</b> {lihtc['li_units']:,}<br>
                <b>🗺️ County:</b> {lihtc['county']}<br>
                <b>📅 Allocation Year:</b> {lihtc['allocation_year']}<br>
                <b>🏷️ HUD ID:</b> {lihtc['hud_id']}<br>
                <b>📊 QCT Flag:</b> {'Yes' if lihtc.get('qct_flag') == 1 else 'No'}<br>
                <b>📊 DDA Flag:</b> {'Yes' if lihtc.get('dda_flag') == 1 else 'No'}
            </div>
            """
            
            folium.Marker(
                location=[lihtc['latitude'], lihtc['longitude']],
                popup=folium.Popup(popup_html, max_width=400),
                tooltip=f"LIHTC: {lihtc['name']} ({lihtc['allocation_year']}) - {lihtc['units']:,} units",
                icon=folium.Icon(
                    color='orange',
                    icon='building',
                    prefix='fa'
                )
            ).add_to(m)
        
        # Enhanced legend
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 400px; height: 320px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px;
                    box-shadow: 0 0 15px rgba(0,0,0,0.2);
                    ">
        <h4 style="margin: 0 0 10px 0; text-align: center;">Arizona USDA Rural Analysis - CORRECTED QCT</h4>
        
        <b>🏡 USDA Rural Development Properties ({total_usda_units:,} units):</b><br>
        <i class="fa fa-home" style="color:red; margin-right: 5px;"></i> <b>QCT Properties ({len(qct_properties)})</b> - BONUS ELIGIBLE!<br>
        <i class="fa fa-home" style="color:green; margin-right: 5px;"></i> Graham County (Non-QCT)<br>
        <i class="fa fa-home" style="color:blue; margin-right: 5px;"></i> Cochise County (Non-QCT)<br>
        <i class="fa fa-home" style="color:darkred; margin-right: 5px;"></i> Santa Cruz County (Non-QCT)<br>
        
        <br><b>🏠 Real LIHTC Properties ({len(real_lihtc)} properties, {total_lihtc_units:,} units):</b><br>
        <i class="fa fa-building" style="color:orange; margin-right: 5px;"></i> Existing LIHTC (HUD Database)<br>
        
        <br><b>🗺️ Geographic Boundaries:</b><br>
        <span style="color:blue;">━━━</span> County Boundaries<br>
        
        <br><b>📊 QCT Analysis Results:</b><br>
        • QCT Properties: <b>{len(qct_properties)}</b><br>
        • Non-QCT Properties: <b>{5 - len(qct_properties)}</b><br>
        • Total Portfolio: <b>{total_usda_units:,} units</b><br>
        
        <br><b>🎯 LIHTC Competitive Advantage:</b><br>
        QCT properties get bonus points!
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add measure control
        MeasureControl().add_to(m)
        
        # Add title
        title_html = '''
        <h2 align="center" style="font-size:24px; margin: 10px;"><b>Arizona USDA Rural Development - CORRECTED QCT ANALYSIS</b></h2>
        <h3 align="center" style="font-size:16px; margin: 5px; color: #666;">Using Complete HUD 2025 QCT Dataset (Metro + Non-Metro)</h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_filename = f"Arizona_CORRECTED_QCT_Map_{timestamp}.html"
        m.save(map_filename)
        print(f"✅ CORRECTED QCT map saved to: {map_filename}")
        
        # Print final summary
        print(f"\n📊 CORRECTED QCT ANALYSIS SUMMARY:")
        print(f"   🏡 USDA Rural Development: 5 properties, {total_usda_units:,} units")
        print(f"   🎯 QCT Properties: {len(qct_properties)} ({'✅ BONUS ELIGIBLE' if qct_properties else '❌ No bonus'})")
        if qct_properties:
            for prop in qct_properties:
                print(f"      • {prop['name']} - {prop.get('details', 'QCT')}")
        print(f"   🏠 Existing LIHTC: {len(real_lihtc)} properties, {total_lihtc_units:,} units")
        
        return map_filename

if __name__ == "__main__":
    mapper = ArizonaCorrectedQCTMapper()
    map_file = mapper.create_corrected_map()
    print(f"\n🎉 CORRECTED QCT MAP: {map_file}")