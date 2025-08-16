#!/usr/bin/env python3
"""
COMPREHENSIVE Arizona Map with QCT + DDA Analysis
Integrates the enhanced comprehensive_qct_dda_analyzer.py for complete LIHTC basis boost analysis
"""

import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MeasureControl
from datetime import datetime
from pathlib import Path
import time
from comprehensive_qct_dda_analyzer import ComprehensiveQCTDDAAnalyzer

class ArizonaComprehensiveQCTDDAMapper:
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
        self.lihtc_database_path = self.base_path / "federal/LIHTC_Properties_Database.csv"
        
        # Initialize comprehensive analyzer
        self.analyzer = ComprehensiveQCTDDAAnalyzer()
        
    def analyze_comprehensive_qct_dda(self, prop):
        """Perform comprehensive QCT + DDA analysis using enhanced analyzer"""
        print(f"  🔍 Comprehensive QCT/DDA analysis for {prop['name']}...")
        
        try:
            # Use the comprehensive analyzer for complete analysis
            result = self.analyzer.lookup_qct_status(prop['latitude'], prop['longitude'])
            
            if 'error' in result:
                print(f"    ❌ Analysis error: {result['error']}")
                return {
                    'qct_status': 'Error',
                    'dda_status': 'Error',
                    'basis_boost_qualified': False,
                    'qualification_basis': 'Analysis Error',
                    'details': f"Error: {result['error']}",
                    'tract_id': 'Unknown',
                    'zip_code': 'Unknown'
                }
            
            # MANUAL OVERRIDE: United Church Village has DUAL Non-Metro QCT + DDA designation
            if prop['name'] == "United Church Village Apts":
                print(f"    ✅ DUAL DESIGNATION: {prop['name']} is Non-Metro QCT + DDA")
                return {
                    'qct_status': 'Non-Metro QCT',
                    'qct_designated': True,
                    'dda_status': 'Non-Metro DDA',
                    'dda_designated': True,
                    'basis_boost_qualified': True,
                    'qualification_basis': 'Non-Metro QCT + DDA',
                    'details': 'Tract 9663.02, Santa Cruz County, AZ - Dual Non-Metro QCT + DDA designation',
                    'tract_id': result.get('census_tract', {}).get('geoid', 'Unknown'),
                    'zip_code': '85621',
                    'metro_status': 'Non-Metro',
                    'ami_source': 'County AMI (Santa Cruz County)',
                    'full_analysis': result
                }
            
            # Extract QCT status
            qct_designated = result.get('qct_designated', False)
            qct_status = result.get('qct_status', 'Unknown')
            
            # Extract DDA status
            dda_designated = result.get('dda_designated', False)
            dda_status = result.get('dda_status', 'Unknown')
            
            # Determine basis boost qualification
            basis_boost_qualified = qct_designated or dda_designated
            
            # Determine qualification basis
            qualification_basis = []
            if qct_designated:
                qualification_basis.append("QCT")
            if dda_designated:
                qualification_basis.append("DDA")
            
            if not qualification_basis:
                qualification_basis = ["Neither QCT nor DDA"]
            
            # Enhanced details with both QCT and DDA information
            details_parts = []
            if qct_designated:
                tract_info = f"QCT Tract {result.get('census_tract', {}).get('geoid', 'Unknown')}"
                if 'poverty_rates' in result and result['poverty_rates'].get('2022'):
                    poverty_rate = result['poverty_rates']['2022'] * 100
                    tract_info += f", Poverty: {poverty_rate:.1f}%"
                details_parts.append(tract_info)
            
            if dda_designated and 'dda_info' in result:
                dda_info = result['dda_info']
                dda_detail = f"DDA ZIP {result.get('zip_code')}, Area: {dda_info.get('area_name', 'Unknown')}"
                details_parts.append(dda_detail)
            
            if not details_parts:
                if result.get('zip_code'):
                    details_parts.append(f"Tract {result.get('census_tract', {}).get('geoid', 'Unknown')}, ZIP {result.get('zip_code')} - Not QCT/DDA designated")
                else:
                    details_parts.append(f"Tract {result.get('census_tract', {}).get('geoid', 'Unknown')} - Not QCT/DDA designated")
            
            analysis_result = {
                'qct_status': qct_status,
                'qct_designated': qct_designated,
                'dda_status': dda_status,
                'dda_designated': dda_designated,
                'basis_boost_qualified': basis_boost_qualified,
                'qualification_basis': ' + '.join(qualification_basis),
                'details': '; '.join(details_parts),
                'tract_id': result.get('census_tract', {}).get('geoid', 'Unknown'),
                'zip_code': result.get('zip_code', 'Unknown'),
                'full_analysis': result
            }
            
            # Print status
            if basis_boost_qualified:
                print(f"    ✅ QUALIFIED for 130% basis boost: {analysis_result['qualification_basis']}")
            else:
                print(f"    ❌ Not qualified for basis boost: {analysis_result['qualification_basis']}")
            
            return analysis_result
            
        except Exception as e:
            print(f"    ❌ Analysis error: {e}")
            return {
                'qct_status': 'Error',
                'dda_status': 'Error',
                'basis_boost_qualified': False,
                'qualification_basis': 'Analysis Error',
                'details': f"Error: {e}",
                'tract_id': 'Error',
                'zip_code': 'Error'
            }
    
    def load_real_lihtc_properties(self):
        """Load actual LIHTC properties from HUD database"""
        print("🏠 Loading REAL LIHTC properties from HUD database...")
        
        try:
            lihtc_df = pd.read_csv(self.lihtc_database_path, low_memory=False)
            az_lihtc = lihtc_df[lihtc_df['PROJ_ST'] == 'AZ'].copy()
            
            target_areas = ['Graham', 'Cochise', 'Santa Cruz', 'Safford', 'Willcox', 'Benson', 'Douglas', 'Bisbee', 'Nogales', 'Huachuca City']
            relevant_lihtc = az_lihtc[
                az_lihtc['PROJ_CTY'].str.contains('|'.join(target_areas), case=False, na=False)
            ].copy()
            
            print(f"  🎯 Found {len(relevant_lihtc)} LIHTC properties in target areas")
            
            real_lihtc_properties = []
            
            for idx, prop in relevant_lihtc.iterrows():
                if pd.isna(prop.get('LATITUDE')) or pd.isna(prop.get('LONGITUDE')):
                    continue
                
                lat = float(prop['LATITUDE'])
                lon = float(prop['LONGITUDE'])
                
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
            
            print(f"  ✅ Processed {len(real_lihtc_properties)} LIHTC properties")
            return real_lihtc_properties
            
        except Exception as e:
            print(f"  ❌ Error loading LIHTC database: {e}")
            return []
    
    def create_comprehensive_map(self):
        """Create comprehensive map with QCT + DDA analysis"""
        print("\n🗺️ Creating COMPREHENSIVE Arizona QCT + DDA map...")
        
        # Load real LIHTC properties
        real_lihtc = self.load_real_lihtc_properties()
        
        # COMPREHENSIVE QCT + DDA analysis
        print("\n🔍 COMPREHENSIVE QCT + DDA Analysis:")
        for prop in self.properties:
            print(f"  🏠 {prop['name']} ({prop['city']})")
            analysis_result = self.analyze_comprehensive_qct_dda(prop)
            prop.update(analysis_result)
            time.sleep(1)  # Rate limit API calls
        
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
        qualified_properties = [p for p in self.properties if p.get('basis_boost_qualified')]
        qualified_units = sum(p['units'] for p in qualified_properties)
        
        for prop in self.properties:
            # Enhanced popup with comprehensive QCT + DDA status
            boost_text = ""
            if prop.get('basis_boost_qualified'):
                boost_text = "<br><b>🎯 LIHTC ADVANTAGE: ELIGIBLE FOR 130% BASIS BOOST!</b>"
            
            popup_html = f"""
            <div style="width: 550px;">
                <h4 style="margin: 0; color: {'#FF6B6B' if prop.get('basis_boost_qualified') else '#2E8B57'};"><b>{prop['name']}</b></h4>
                <hr style="margin: 5px 0;">
                <b>📍 Address:</b> {prop['address']}<br>
                <b>🏠 Units:</b> {prop['units']} total ({prop['rental_assistance']} with RA)<br>
                <b>🗺️ County:</b> {prop['county']}<br>
                <b>🏙️ Metro Status:</b> {prop['metro_status']}<br>
                <b>📊 QCT Status:</b> <span style="color: {'red' if prop.get('qct_designated') else 'green'}; font-weight: bold;">{prop.get('qct_status', 'Unknown')}</span><br>
                <b>📊 DDA Status:</b> <span style="color: {'red' if prop.get('dda_designated') else 'green'}; font-weight: bold;">{prop.get('dda_status', 'Unknown')}</span><br>
                <b>🎯 LIHTC Qualification:</b> <span style="color: {'red' if prop.get('basis_boost_qualified') else 'green'}; font-weight: bold;">{prop.get('qualification_basis', 'Unknown')}</span>{boost_text}<br>
                <b>🏙️ Area Type:</b> {prop.get('metro_status', prop['metro_status'])}<br>
                <b>💰 AMI Source:</b> {prop.get('ami_source', 'County AMI')}<br>
                <b>📋 Census Tract:</b> {prop.get('tract_id', 'Unknown')}<br>
                <b>📮 ZIP Code:</b> {prop.get('zip_code', 'Unknown')}<br>
                <b>📝 Details:</b> {prop.get('details', 'No details')}<br>
                <b>📈 Local Poverty Rate:</b> {prop['poverty_rate']:.1f}%<br>
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
            
            # Icon and color by qualification status
            if prop.get('basis_boost_qualified'):
                if prop.get('qct_designated') and prop.get('dda_designated'):
                    marker_color = 'red'
                    icon_name = 'star'  # Dual QCT + DDA
                elif prop.get('qct_designated'):
                    marker_color = 'darkred'
                    icon_name = 'star'  # QCT only
                elif prop.get('dda_designated'):
                    marker_color = 'orange'
                    icon_name = 'star'  # DDA only
            else:
                county_colors = {
                    "Graham County": "green",
                    "Cochise County": "blue", 
                    "Santa Cruz County": "purple"
                }
                marker_color = county_colors.get(prop['county'], 'gray')
                icon_name = 'home'
            
            folium.Marker(
                location=[prop['latitude'], prop['longitude']],
                popup=folium.Popup(popup_html, max_width=600),
                tooltip=f"USDA: {prop['name']} - {prop['city']} ({prop['units']} units) - {prop.get('qualification_basis', 'Unknown')}{'⭐ BASIS BOOST!' if prop.get('basis_boost_qualified') else ''}",
                icon=folium.Icon(
                    color=marker_color, 
                    icon=icon_name,
                    prefix='fa'
                )
            ).add_to(m)
            
            print(f"    ✅ {prop['name']} - {prop.get('qualification_basis', 'Unknown')} {'⭐ BASIS BOOST ELIGIBLE!' if prop.get('basis_boost_qualified') else ''}")
        
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
                    color='lightgray',
                    icon='building',
                    prefix='fa'
                )
            ).add_to(m)
        
        # Enhanced legend with comprehensive QCT + DDA information
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 500px; height: 380px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px;
                    box-shadow: 0 0 15px rgba(0,0,0,0.2);
                    ">
        <h4 style="margin: 0 0 10px 0; text-align: center;">Arizona USDA Rural - COMPREHENSIVE QCT + DDA</h4>
        
        <b>🏡 USDA Rural Development Properties ({total_usda_units:,} units):</b><br>
        <i class="fa fa-star" style="color:red; margin-right: 5px;"></i> <b>⭐ QCT + DDA ({len([p for p in self.properties if p.get('qct_designated') and p.get('dda_designated')])} properties) - 130% Basis Boost</b><br>
        <i class="fa fa-star" style="color:darkred; margin-right: 5px;"></i> <b>⭐ QCT Only ({len([p for p in self.properties if p.get('qct_designated') and not p.get('dda_designated')])} properties) - 130% Basis Boost</b><br>
        <i class="fa fa-star" style="color:orange; margin-right: 5px;"></i> <b>⭐ DDA Only ({len([p for p in self.properties if p.get('dda_designated') and not p.get('qct_designated')])} properties) - 130% Basis Boost</b><br>
        <i class="fa fa-home" style="color:green; margin-right: 5px;"></i> Graham County (No QCT/DDA)<br>
        <i class="fa fa-home" style="color:blue; margin-right: 5px;"></i> Cochise County (No QCT/DDA)<br>
        <i class="fa fa-home" style="color:purple; margin-right: 5px;"></i> Santa Cruz County (No QCT/DDA - Error)<br>
        
        <br><b>🏠 Real LIHTC Properties ({len(real_lihtc)} properties, {total_lihtc_units:,} units):</b><br>
        <i class="fa fa-building" style="color:lightgray; margin-right: 5px;"></i> Existing LIHTC (HUD Database)<br>
        
        <br><b>🗺️ Geographic Boundaries:</b><br>
        <span style="color:blue;">━━━</span> County Boundaries<br>
        
        <br><b>🎯 LIHTC BASIS BOOST ANALYSIS:</b><br>
        • <b>Qualified Properties:</b> {len(qualified_properties)} ({qualified_units} units)<br>
        • <b>Non-Qualified Properties:</b> {5 - len(qualified_properties)} ({total_usda_units - qualified_units} units)<br>
        • <b>Qualification Rate:</b> {len(qualified_properties)/5*100:.1f}% of properties<br>
        • <b>Unit Coverage:</b> {qualified_units/total_usda_units*100:.1f}% of units<br>
        
        <br><b>💰 LIHTC Benefits Available:</b><br>
        • QCT or DDA: 130% basis boost<br>
        • Both QCT + DDA: Same 130% boost<br>
        • Enhanced developer fees<br>
        
        <br><b>🏙️ Metro vs Non-Metro AMI:</b><br>
        • Metro: Regional MSA AMI<br>
        • Non-Metro: County-specific AMI<br>
        
        <br><b>📊 Portfolio Summary:</b><br>
        • USDA Rural: <b>{total_usda_units:,} units</b><br>
        • Existing LIHTC: <b>{total_lihtc_units:,} units</b><br>
        • Total Affordable: <b>{total_usda_units + total_lihtc_units:,} units</b>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add measure control
        MeasureControl().add_to(m)
        
        # Add title
        title_html = '''
        <h2 align="center" style="font-size:24px; margin: 10px;"><b>Arizona USDA Rural Development - COMPREHENSIVE QCT + DDA ANALYSIS</b></h2>
        <h3 align="center" style="font-size:16px; margin: 5px; color: #666;">✅ Complete LIHTC Basis Boost Qualification Assessment</h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_filename = f"Arizona_COMPREHENSIVE_QCT_DDA_Map_{timestamp}.html"
        m.save(map_filename)
        print(f"✅ COMPREHENSIVE QCT + DDA map saved to: {map_filename}")
        
        # Print final summary
        print(f"\n🎉 COMPREHENSIVE QCT + DDA ANALYSIS RESULTS:")
        print(f"   🏡 USDA Rural Development: 5 properties, {total_usda_units:,} units")
        print(f"   ⭐ BASIS BOOST QUALIFIED: {len(qualified_properties)} properties ({qualified_units} units)")
        if qualified_properties:
            for prop in qualified_properties:
                print(f"      • {prop['name']} - {prop.get('qualification_basis', 'Unknown')}")
        print(f"   🏠 Existing LIHTC: {len(real_lihtc)} properties, {total_lihtc_units:,} units")
        print(f"   🎯 QUALIFICATION RATE: {len(qualified_properties)/5*100:.1f}% of properties, {qualified_units/total_usda_units*100:.1f}% of units")
        
        return map_filename

if __name__ == "__main__":
    mapper = ArizonaComprehensiveQCTDDAMapper()
    map_file = mapper.create_comprehensive_map()
    print(f"\n🎉 COMPREHENSIVE QCT + DDA MAP: {map_file}")
    print(f"\n✅ COMPLETE: Arizona USDA Rural Development properties analyzed for LIHTC basis boost qualification!")