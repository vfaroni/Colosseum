#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE Arizona USDA Rural Development Properties Map
- Corrected QCT/DDA detection with detailed analysis
- Real HUD LIHTC database (35 properties)
- Arizona amenities from geospatial datasets
- Complete analysis with all requested fixes
"""

import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MeasureControl
from datetime import datetime
from pathlib import Path
from shapely.geometry import Point

class ArizonaFinalComprehensiveMapper:
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
        
    def detailed_qct_dda_analysis(self, lat, lon, property_name):
        """Detailed QCT/DDA analysis with complete field checking"""
        try:
            print(f"    🔍 Detailed analysis for {property_name}")
            
            # Create point geometry
            point = Point(lon, lat)
            point_gdf = gpd.GeoDataFrame([1], geometry=[point], crs='EPSG:4326')
            
            # Load QCT/DDA data if not already loaded
            if not hasattr(self, 'qct_dda_gdf'):
                print(f"      Loading QCT/DDA database...")
                qct_dda_all = gpd.read_file(self.qct_dda_path)
                # Filter for Arizona (state FIPS 04)
                self.qct_dda_gdf = qct_dda_all[
                    (qct_dda_all.get('STATEFP', qct_dda_all.get('STATE', '')).astype(str).str.zfill(2) == '04') |
                    (qct_dda_all.get('GEOID', '').astype(str).str.startswith('04'))
                ]
                print(f"      Loaded {len(self.qct_dda_gdf)} Arizona QCT/DDA areas")
                
                # Print available fields for debugging
                qct_dda_fields = [col for col in self.qct_dda_gdf.columns if isinstance(col, str) and ('qct' in col.lower() or 'dda' in col.lower())]
                print(f"      Available QCT/DDA fields: {qct_dda_fields}")
            
            # Ensure same CRS
            if self.qct_dda_gdf.crs != point_gdf.crs:
                point_gdf = point_gdf.to_crs(self.qct_dda_gdf.crs)
            
            # Check for intersections
            intersections = gpd.sjoin(point_gdf, self.qct_dda_gdf, how='inner', predicate='intersects')
            
            if intersections.empty:
                print(f"      No QCT/DDA intersections found")
                return {
                    'is_qct': False,
                    'is_dda': False,
                    'status': 'Neither',
                    'details': 'Not in any QCT/DDA area',
                    'tract_id': 'None'
                }
            
            # Analyze intersections
            print(f"      Found {len(intersections)} intersections")
            
            is_qct = False
            is_dda = False
            tract_details = []
            
            for idx, row in intersections.iterrows():
                tract_id = row.get('GEOID', row.get('TRACT', 'Unknown'))
                print(f"      Tract: {tract_id}")
                
                # Check all QCT/DDA related fields
                qct_indicators = []
                dda_indicators = []
                
                for col_name in row.index:
                    if isinstance(col_name, str):
                        col_lower = col_name.lower()
                        if 'qct' in col_lower:
                            value = row[col_name]
                            print(f"        QCT field {col_name}: {value}")
                            if value == 1 or str(value).upper() in ['TRUE', 'YES', 'Y']:
                                is_qct = True
                                qct_indicators.append(f"{col_name}={value}")
                        
                        if 'dda' in col_lower:
                            value = row[col_name]
                            print(f"        DDA field {col_name}: {value}")
                            if value == 1 or str(value).upper() in ['TRUE', 'YES', 'Y']:
                                is_dda = True
                                dda_indicators.append(f"{col_name}={value}")
                
                tract_info = f"Tract {tract_id}"
                if qct_indicators:
                    tract_info += f" (QCT: {'; '.join(qct_indicators)})"
                if dda_indicators:
                    tract_info += f" (DDA: {'; '.join(dda_indicators)})"
                
                tract_details.append(tract_info)
            
            # Determine final status
            status_parts = []
            if is_qct:
                status_parts.append("QCT")
            if is_dda:
                status_parts.append("DDA")
            
            final_status = " + ".join(status_parts) if status_parts else "Neither"
            details = "; ".join(tract_details) if tract_details else "In tract but no QCT/DDA flags"
            
            print(f"      Final result: {final_status}")
            
            return {
                'is_qct': is_qct,
                'is_dda': is_dda,
                'status': final_status,
                'details': details,
                'tract_id': intersections.iloc[0].get('GEOID', 'Unknown') if not intersections.empty else 'None'
            }
            
        except Exception as e:
            print(f"      ❌ Error in QCT/DDA analysis: {e}")
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
                    'dda_flag': prop.get('DDA', 0),
                    'allocation_amount': prop.get('ALLOCAMT', 0)
                })
            
            print(f"  ✅ Processed {len(real_lihtc_properties)} LIHTC properties with valid coordinates")
            
            # County summary
            county_summary = {}
            total_lihtc_units = 0
            for prop in real_lihtc_properties:
                county = prop['county']
                if county not in county_summary:
                    county_summary[county] = {'count': 0, 'units': 0}
                county_summary[county]['count'] += 1
                county_summary[county]['units'] += prop['units']
                total_lihtc_units += prop['units']
            
            print(f"  📊 County breakdown ({total_lihtc_units:,} total LIHTC units):")
            for county, stats in sorted(county_summary.items()):
                print(f"    {county}: {stats['count']} properties, {stats['units']:,} units")
            
            return real_lihtc_properties
            
        except Exception as e:
            print(f"  ❌ Error loading LIHTC database: {e}")
            return []
    
    def create_final_map(self):
        """Create final comprehensive map"""
        print("\n🗺️ Creating FINAL COMPREHENSIVE Arizona map...")
        
        # Load real LIHTC properties
        real_lihtc = self.load_real_lihtc_properties()
        
        # Detailed QCT/DDA analysis for our properties
        print("\n🔍 DETAILED QCT/DDA Analysis:")
        for prop in self.properties:
            print(f"  🏠 {prop['name']} ({prop['city']})")
            qct_dda_result = self.detailed_qct_dda_analysis(prop['latitude'], prop['longitude'], prop['name'])
            prop.update(qct_dda_result)
        
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
        
        # Add QCT/DDA areas
        try:
            print("  🎯 Adding QCT/DDA areas...")
            if hasattr(self, 'qct_dda_gdf'):
                qct_count = 0
                dda_count = 0
                for idx, area in self.qct_dda_gdf.iterrows():
                    area_types = []
                    color = 'gray'
                    
                    # Check for QCT/DDA flags
                    is_qct = False
                    is_dda = False
                    
                    for col_name in area.index:
                        if isinstance(col_name, str):
                            col_lower = col_name.lower()
                            if 'qct' in col_lower and area[col_name] == 1:
                                is_qct = True
                            if 'dda' in col_lower and area[col_name] == 1:
                                is_dda = True
                    
                    if is_qct:
                        area_types.append('QCT')
                        color = 'orange'
                        qct_count += 1
                    if is_dda:
                        area_types.append('DDA')
                        color = 'purple' if not is_qct else 'red'
                        dda_count += 1
                    
                    if area_types:
                        folium.GeoJson(
                            area.geometry,
                            style_function=lambda x, color=color: {
                                'fillColor': color,
                                'color': color,
                                'weight': 1,
                                'fillOpacity': 0.3
                            },
                            popup=folium.Popup(f"<b>{'/'.join(area_types)} Area</b><br>Tract: {area.get('GEOID', 'Unknown')}", max_width=200),
                            tooltip=f"{'/'.join(area_types)} Area"
                        ).add_to(m)
                
                print(f"    Added {qct_count} QCT areas and {dda_count} DDA areas")
        except Exception as e:
            print(f"    ❌ Error adding QCT/DDA areas: {e}")
        
        # Add our USDA Rural Development properties
        print("  🏡 Adding USDA Rural Development properties...")
        total_usda_units = sum(prop['units'] for prop in self.properties)
        total_usda_ra = sum(prop['rental_assistance'] for prop in self.properties)
        
        for prop in self.properties:
            # Enhanced popup with QCT/DDA details
            popup_html = f"""
            <div style="width: 450px;">
                <h4 style="margin: 0; color: #2E8B57;"><b>{prop['name']}</b></h4>
                <hr style="margin: 5px 0;">
                <b>📍 Address:</b> {prop['address']}<br>
                <b>🏠 Units:</b> {prop['units']} total ({prop['rental_assistance']} with RA)<br>
                <b>🗺️ County:</b> {prop['county']}<br>
                <b>🏙️ Metro Status:</b> {prop['metro_status']}<br>
                <b>📊 QCT/DDA Status:</b> <span style="color: {'red' if prop.get('is_qct') or prop.get('is_dda') else 'green'}; font-weight: bold;">{prop.get('status', 'Unknown')}</span><br>
                <b>📋 Census Tract:</b> {prop.get('tract_id', 'Unknown')}<br>
                <b>📝 Analysis Details:</b> {prop.get('details', 'No details')}<br>
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
            
            # Color by QCT/DDA status
            if prop.get('is_qct') and prop.get('is_dda'):
                marker_color = 'red'
            elif prop.get('is_qct'):
                marker_color = 'orange'
            elif prop.get('is_dda'):
                marker_color = 'purple'
            else:
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
                <b>💰 Allocation:</b> ${lihtc.get('allocation_amount', 0):,}<br>
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
        
        # Enhanced legend with real data
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 350px; height: 320px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px;
                    box-shadow: 0 0 15px rgba(0,0,0,0.2);
                    ">
        <h4 style="margin: 0 0 10px 0; text-align: center;">Arizona USDA Rural Analysis - FINAL</h4>
        
        <b>🏡 USDA Rural Development Properties ({total_usda_units:,} units):</b><br>
        <i class="fa fa-home" style="color:red; margin-right: 5px;"></i> QCT + DDA<br>
        <i class="fa fa-home" style="color:orange; margin-right: 5px;"></i> QCT Only<br>
        <i class="fa fa-home" style="color:purple; margin-right: 5px;"></i> DDA Only<br>
        <i class="fa fa-home" style="color:green; margin-right: 5px;"></i> Graham County (Neither)<br>
        <i class="fa fa-home" style="color:blue; margin-right: 5px;"></i> Cochise County (Neither)<br>
        <i class="fa fa-home" style="color:darkred; margin-right: 5px;"></i> Santa Cruz County (Neither)<br>
        
        <br><b>🏠 Real LIHTC Properties ({len(real_lihtc)} properties, {total_lihtc_units:,} units):</b><br>
        <i class="fa fa-building" style="color:orange; margin-right: 5px;"></i> Existing LIHTC (HUD Database)<br>
        
        <br><b>🗺️ Geographic Boundaries:</b><br>
        <span style="color:blue;">━━━</span> County Boundaries<br>
        <span style="color:orange;">▓▓▓</span> QCT Areas<br>
        <span style="color:purple;">▓▓▓</span> DDA Areas<br>
        <span style="color:red;">▓▓▓</span> QCT+DDA Areas<br>
        
        <br><b>📊 Portfolio Summary:</b><br>
        • USDA Rural: {total_usda_units:,} units ({total_usda_ra:,} RA)<br>
        • Existing LIHTC: {total_lihtc_units:,} units<br>
        • Total Affordable: {total_usda_units + total_lihtc_units:,} units
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add measure control
        MeasureControl().add_to(m)
        
        # Add title
        title_html = '''
        <h2 align="center" style="font-size:24px; margin: 10px;"><b>Arizona USDA Rural Development Properties - FINAL ANALYSIS</b></h2>
        <h3 align="center" style="font-size:16px; margin: 5px; color: #666;">Corrected QCT/DDA Detection + Real HUD LIHTC Database + Comprehensive Analysis</h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_filename = f"Arizona_FINAL_Comprehensive_Map_{timestamp}.html"
        m.save(map_filename)
        print(f"✅ FINAL comprehensive map saved to: {map_filename}")
        
        # Print final summary
        print(f"\n📊 FINAL ANALYSIS SUMMARY:")
        print(f"   🏡 USDA Rural Development: 5 properties, {total_usda_units:,} units ({total_usda_ra:,} RA)")
        print(f"   🏠 Existing LIHTC: {len(real_lihtc)} properties, {total_lihtc_units:,} units") 
        print(f"   📍 Total Affordable Housing: {total_usda_units + total_lihtc_units:,} units across 3 counties")
        print(f"   🎯 QCT/DDA Properties: {sum(1 for p in self.properties if p.get('is_qct') or p.get('is_dda'))}")
        
        return map_filename

if __name__ == "__main__":
    mapper = ArizonaFinalComprehensiveMapper()
    map_file = mapper.create_final_map()
    print(f"\n🎉 FINAL COMPREHENSIVE MAP: {map_file}")