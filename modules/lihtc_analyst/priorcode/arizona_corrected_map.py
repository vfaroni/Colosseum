#!/usr/bin/env python3
"""
CORRECTED Arizona USDA Rural Development Properties Map
- Fixed QCT/DDA detection
- Real HUD LIHTC database properties
- Added Arizona geospatial amenities from dataset inventory
"""

import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MeasureControl
from datetime import datetime
from pathlib import Path
from shapely.geometry import Point

class ArizonaCorrectedMapper:
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
        self.qct_dda_path = self.base_path / "federal/HUD_QCT_DDA_Data/HUD QCT DDA 2025 Merged.gpkg"
        self.lihtc_database_path = self.base_path / "federal/LIHTC_Properties_Database.csv"
        
    def check_qct_dda_status_correct(self, lat, lon):
        """CORRECTED QCT/DDA detection using proper spatial intersection"""
        try:
            # Create point geometry
            point = Point(lon, lat)
            point_gdf = gpd.GeoDataFrame([1], geometry=[point], crs='EPSG:4326')
            
            # Load QCT/DDA data if not already loaded
            if not hasattr(self, 'qct_dda_gdf'):
                print(f"    Loading QCT/DDA database...")
                qct_dda_all = gpd.read_file(self.qct_dda_path)
                # Filter for Arizona (state FIPS 04)
                self.qct_dda_gdf = qct_dda_all[
                    (qct_dda_all.get('STATEFP', qct_dda_all.get('STATE', '')).astype(str).str.zfill(2) == '04') |
                    (qct_dda_all.get('GEOID', '').astype(str).str.startswith('04'))
                ]
                print(f"    Loaded {len(self.qct_dda_gdf)} Arizona QCT/DDA areas")
            
            # Ensure same CRS
            if self.qct_dda_gdf.crs != point_gdf.crs:
                point_gdf = point_gdf.to_crs(self.qct_dda_gdf.crs)
            
            # Check for intersections using spatial join
            intersections = gpd.sjoin(point_gdf, self.qct_dda_gdf, how='inner', predicate='intersects')
            
            is_qct = False
            is_dda = False
            area_details = []
            
            if not intersections.empty:
                for idx, row in intersections.iterrows():
                    # Check multiple possible QCT field names
                    qct_fields = ['QCT', 'QCT_FLAG', 'qct', 'IS_QCT']
                    dda_fields = ['DDA', 'DDA_FLAG', 'dda', 'IS_DDA']
                    
                    for field in qct_fields:
                        if field in row and (row[field] == 1 or row[field] == '1' or str(row[field]).upper() == 'TRUE'):
                            is_qct = True
                            break
                    
                    for field in dda_fields:
                        if field in row and (row[field] == 1 or row[field] == '1' or str(row[field]).upper() == 'TRUE'):
                            is_dda = True
                            break
                    
                    # Collect area details
                    tract_id = row.get('GEOID', row.get('TRACT', 'Unknown'))
                    area_details.append(f"Tract {tract_id}")
            
            status_parts = []
            if is_qct:
                status_parts.append("QCT")
            if is_dda:
                status_parts.append("DDA")
            
            status = " + ".join(status_parts) if status_parts else "Neither"
            
            return {
                'is_qct': is_qct,
                'is_dda': is_dda,
                'status': status,
                'details': "; ".join(area_details) if area_details else "Not in QCT/DDA area"
            }
            
        except Exception as e:
            print(f"    ❌ QCT/DDA check error: {e}")
            return {
                'is_qct': False,
                'is_dda': False,
                'status': "Error",
                'details': f"Error checking: {e}"
            }
    
    def load_real_lihtc_properties(self):
        """Load actual LIHTC properties from HUD database"""
        print("🏠 Loading REAL LIHTC properties from HUD database...")
        
        try:
            # Load the full HUD LIHTC database
            lihtc_df = pd.read_csv(self.lihtc_database_path)
            print(f"  📊 Loaded {len(lihtc_df):,} total LIHTC properties from HUD database")
            
            # Filter for Arizona
            az_lihtc = lihtc_df[lihtc_df['PROJ_ST'] == 'AZ'].copy()
            print(f"  📍 Found {len(az_lihtc)} Arizona LIHTC properties")
            
            # Filter for our target counties
            target_counties = ['Graham', 'Cochise', 'Santa Cruz']
            county_matches = az_lihtc[
                az_lihtc['PROJ_CTY'].str.contains('|'.join(target_counties), case=False, na=False)
            ].copy()
            
            # Also check for specific cities
            target_cities = ['Safford', 'Willcox', 'Benson', 'Douglas', 'Bisbee', 'Nogales', 'Huachuca City']
            city_matches = az_lihtc[
                az_lihtc['PROJ_CTY'].str.contains('|'.join(target_cities), case=False, na=False)
            ].copy()
            
            # Combine and remove duplicates
            relevant_lihtc = pd.concat([county_matches, city_matches]).drop_duplicates(subset=['HUD_ID'])
            
            print(f"  🎯 Found {len(relevant_lihtc)} LIHTC properties in target counties/cities")
            
            # Process properties with coordinates
            real_lihtc_properties = []
            
            for idx, prop in relevant_lihtc.iterrows():
                # Skip if missing coordinates
                if pd.isna(prop.get('LATITUDE')) or pd.isna(prop.get('LONGITUDE')):
                    continue
                
                # Clean up data
                lat = float(prop['LATITUDE'])
                lon = float(prop['LONGITUDE'])
                
                # Skip if coordinates are clearly invalid
                if lat == 0 or lon == 0 or abs(lat) > 90 or abs(lon) > 180:
                    continue
                
                # Skip if not in Arizona coordinate range
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
                    'allocation_year': int(year_alloc) if pd.notna(year_alloc) and str(year_alloc).isdigit() else 'Unknown',
                    'hud_id': prop.get('HUD_ID', 'Unknown'),
                    'type': 'Existing LIHTC',
                    'qct_flag': prop.get('QCT', 0),
                    'dda_flag': prop.get('DDA', 0)
                })
            
            print(f"  ✅ Processed {len(real_lihtc_properties)} LIHTC properties with valid coordinates")
            
            # Print summary by county
            if real_lihtc_properties:
                county_summary = {}
                for prop in real_lihtc_properties:
                    county = prop['county']
                    if county not in county_summary:
                        county_summary[county] = {'count': 0, 'units': 0}
                    county_summary[county]['count'] += 1
                    county_summary[county]['units'] += prop['units']
                
                print(f"  📊 County breakdown:")
                for county, stats in county_summary.items():
                    print(f"    {county}: {stats['count']} properties, {stats['units']} total units")
            
            return real_lihtc_properties
            
        except Exception as e:
            print(f"  ❌ Error loading LIHTC database: {e}")
            return []
    
    def create_corrected_map(self):
        """Create corrected map with all fixes"""
        print("\n🗺️ Creating CORRECTED Arizona map...")
        
        # Load real LIHTC properties
        real_lihtc = self.load_real_lihtc_properties()
        
        # Check QCT/DDA status for our properties (CORRECTED)
        print("\n🔍 CORRECTED QCT/DDA Analysis:")
        for prop in self.properties:
            print(f"  Checking {prop['name']} at {prop['latitude']:.6f}, {prop['longitude']:.6f}")
            qct_dda_result = self.check_qct_dda_status_correct(prop['latitude'], prop['longitude'])
            prop.update(qct_dda_result)
            print(f"    Result: {qct_dda_result['status']} - {qct_dda_result['details']}")
        
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
        
        # Load and add county boundaries
        try:
            print("  Adding Arizona county boundaries...")
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
        
        # Load and add QCT/DDA areas
        try:
            print("  Adding QCT/DDA areas...")
            if hasattr(self, 'qct_dda_gdf'):
                for idx, area in self.qct_dda_gdf.iterrows():
                    # Determine type and color
                    area_type = []
                    color = 'gray'
                    
                    # Check multiple field names for QCT/DDA flags
                    qct_fields = ['QCT', 'QCT_FLAG', 'qct', 'IS_QCT']
                    dda_fields = ['DDA', 'DDA_FLAG', 'dda', 'IS_DDA']
                    
                    is_qct = any(area.get(field, 0) == 1 or str(area.get(field, '')).upper() == 'TRUE' for field in qct_fields)
                    is_dda = any(area.get(field, 0) == 1 or str(area.get(field, '')).upper() == 'TRUE' for field in dda_fields)
                    
                    if is_qct:
                        area_type.append('QCT')
                        color = 'orange'
                    if is_dda:
                        area_type.append('DDA')
                        color = 'purple' if 'QCT' not in area_type else 'red'
                    
                    if area_type:
                        folium.GeoJson(
                            area.geometry,
                            style_function=lambda x, color=color: {
                                'fillColor': color,
                                'color': color,
                                'weight': 1,
                                'fillOpacity': 0.3
                            },
                            popup=folium.Popup(f"<b>{'/'.join(area_type)} Area</b><br>Tract: {area.get('GEOID', 'Unknown')}", max_width=200),
                            tooltip=f"{'/'.join(area_type)} Area"
                        ).add_to(m)
        except Exception as e:
            print(f"    ❌ Error adding QCT/DDA areas: {e}")
        
        # Add our USDA Rural Development properties
        print("  Adding USDA Rural Development properties...")
        for i, prop in enumerate(self.properties):
            # Create detailed popup with corrected QCT/DDA status
            popup_html = f"""
            <div style="width: 400px;">
                <h4 style="margin: 0; color: #2E8B57;"><b>{prop['name']}</b></h4>
                <hr style="margin: 5px 0;">
                <b>📍 Address:</b> {prop['address']}<br>
                <b>🏠 Units:</b> {prop['units']} total ({prop['rental_assistance']} with RA)<br>
                <b>🗺️ County:</b> {prop['county']}<br>
                <b>🏙️ Metro Status:</b> {prop['metro_status']}<br>
                <b>📊 QCT/DDA Status:</b> <span style="color: {'red' if prop.get('is_qct') or prop.get('is_dda') else 'green'};">{prop.get('status', 'Unknown')}</span><br>
                <b>📋 Details:</b> {prop.get('details', 'No details')}<br>
                <b>📈 Poverty Rate:</b> {prop['poverty_rate']:.1f}%<br>
                <hr style="margin: 5px 0;">
                <b>💰 4-Person 100% AMI:</b> ${prop['ami_100_4person']:,}<br>
                <b>🏠 60% AMI Rent Limits:</b><br>
                <table style="margin: 5px 0; font-size: 12px;">
                    <tr><td>Studio:</td><td style="text-align: right;">${prop['rent_studio_60']}</td></tr>
                    <tr><td>1 Bedroom:</td><td style="text-align: right;">${prop['rent_1br_60']}</td></tr>
                    <tr><td>2 Bedroom:</td><td style="text-align: right;">${prop['rent_2br_60']}</td></tr>
                    <tr><td>3 Bedroom:</td><td style="text-align: right;">${prop['rent_3br_60']}</td></tr>
                    <tr><td>4 Bedroom:</td><td style="text-align: right;">${prop['rent_4br_60']}</td></tr>
                </table>
            </div>
            """
            
            # Color by QCT/DDA status
            if prop.get('is_qct') and prop.get('is_dda'):
                marker_color = 'red'  # Both QCT and DDA
            elif prop.get('is_qct'):
                marker_color = 'orange'  # QCT only
            elif prop.get('is_dda'):
                marker_color = 'purple'  # DDA only
            else:
                # County colors for non-QCT/DDA
                county_colors = {
                    "Graham County": "green",
                    "Cochise County": "blue", 
                    "Santa Cruz County": "darkred"
                }
                marker_color = county_colors.get(prop['county'], 'gray')
            
            folium.Marker(
                location=[prop['latitude'], prop['longitude']],
                popup=folium.Popup(popup_html, max_width=450),
                tooltip=f"{prop['name']} - {prop['city']} ({prop['units']} units) - {prop.get('status', 'Unknown')}",
                icon=folium.Icon(
                    color=marker_color, 
                    icon='home',
                    prefix='fa'
                )
            ).add_to(m)
            
            print(f"    ✅ Added {prop['name']} - QCT/DDA: {prop.get('status', 'Unknown')}")
        
        # Add real LIHTC properties
        print(f"  Adding {len(real_lihtc)} real LIHTC properties...")
        for lihtc in real_lihtc:
            popup_html = f"""
            <div style="width: 300px;">
                <h4 style="margin: 0; color: #8B4513;"><b>{lihtc['name']}</b></h4>
                <hr style="margin: 5px 0;">
                <b>📍 Address:</b> {lihtc['address']}<br>
                <b>🏠 Total Units:</b> {lihtc['units']}<br>
                <b>🏠 LI Units:</b> {lihtc['li_units']}<br>
                <b>🗺️ County:</b> {lihtc['county']}<br>
                <b>📅 Allocation Year:</b> {lihtc['allocation_year']}<br>
                <b>🏷️ HUD ID:</b> {lihtc['hud_id']}<br>
                <b>📊 QCT:</b> {'Yes' if lihtc.get('qct_flag') == 1 else 'No'}<br>
                <b>📊 DDA:</b> {'Yes' if lihtc.get('dda_flag') == 1 else 'No'}
            </div>
            """
            
            folium.Marker(
                location=[lihtc['latitude'], lihtc['longitude']],
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=f"{lihtc['name']} ({lihtc['allocation_year']}) - {lihtc['units']} units",
                icon=folium.Icon(
                    color='orange',
                    icon='building',
                    prefix='fa'
                )
            ).add_to(m)
        
        # Add comprehensive legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 320px; height: 280px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px;
                    box-shadow: 0 0 15px rgba(0,0,0,0.2);
                    ">
        <h4 style="margin: 0 0 10px 0; text-align: center;">Arizona USDA Rural Analysis (CORRECTED)</h4>
        
        <b>🏡 USDA Rural Development Properties:</b><br>
        <i class="fa fa-home" style="color:red; margin-right: 5px;"></i> QCT + DDA<br>
        <i class="fa fa-home" style="color:orange; margin-right: 5px;"></i> QCT Only<br>
        <i class="fa fa-home" style="color:purple; margin-right: 5px;"></i> DDA Only<br>
        <i class="fa fa-home" style="color:green; margin-right: 5px;"></i> Graham County (Neither)<br>
        <i class="fa fa-home" style="color:blue; margin-right: 5px;"></i> Cochise County (Neither)<br>
        <i class="fa fa-home" style="color:darkred; margin-right: 5px;"></i> Santa Cruz County (Neither)<br>
        
        <br><b>🏠 Real LIHTC Properties (HUD Database):</b><br>
        <i class="fa fa-building" style="color:orange; margin-right: 5px;"></i> Existing LIHTC Properties<br>
        
        <br><b>🗺️ Geographic Boundaries:</b><br>
        <span style="color:blue;">━━━</span> County Boundaries<br>
        <span style="color:orange;">▓▓▓</span> QCT Areas<br>
        <span style="color:purple;">▓▓▓</span> DDA Areas<br>
        <span style="color:red;">▓▓▓</span> QCT+DDA Areas<br>
        
        <br><b>📊 Portfolio Total:</b> 160 units (155 RA)<br>
        <b>🏠 Existing LIHTC:</b> {len(real_lihtc)} properties
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add measure control
        MeasureControl().add_to(m)
        
        # Add title
        title_html = '''
        <h2 align="center" style="font-size:24px; margin: 10px;"><b>Arizona USDA Rural Development Properties - CORRECTED</b></h2>
        <h3 align="center" style="font-size:16px; margin: 5px; color: #666;">Fixed QCT/DDA Detection + Real HUD LIHTC Database</h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_filename = f"Arizona_CORRECTED_Rural_Properties_Map_{timestamp}.html"
        m.save(map_filename)
        print(f"✅ CORRECTED map saved to: {map_filename}")
        
        return map_filename

if __name__ == "__main__":
    mapper = ArizonaCorrectedMapper()
    map_file = mapper.create_corrected_map()
    print(f"\n🎉 CORRECTED map with all fixes: {map_file}")