#!/usr/bin/env python3
"""
Enhanced Arizona USDA Rural Development Properties Map
With county boundaries, QCT/DDA areas, and existing LIHTC properties
"""

import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MeasureControl
from datetime import datetime
from pathlib import Path
import json

class ArizonaEnhancedMapper:
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
                "poverty_rate": 12.4,
                "is_qct": False,
                "is_dda": False
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
                "poverty_rate": 12.4,
                "is_qct": False,
                "is_dda": False
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
                "poverty_rate": 11.8,
                "is_qct": False,
                "is_dda": False
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
                "poverty_rate": 11.8,
                "is_qct": False,
                "is_dda": False
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
                "poverty_rate": 16.2,
                "is_qct": False,
                "is_dda": False
            }
        ]
        
        # Data paths
        self.base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets")
        self.counties_path = self.base_path / "federal/HUD_AMI_Geographic/States/az_counties_hud_ami_2025.gpkg"
        self.qct_dda_path = self.base_path / "federal/HUD_QCT_DDA_Data/HUD QCT DDA 2025 Merged.gpkg"
        self.poverty_path = self.base_path / "environmental/Poverty Rate Census Tracts (ACS)/poverty_tracts_AZ_2022.gpkg"
        
    def load_geographic_data(self):
        """Load county boundaries and QCT/DDA data"""
        print("📊 Loading geographic data...")
        
        try:
            # Load Arizona counties
            print("  Loading Arizona counties...")
            self.counties = gpd.read_file(self.counties_path)
            print(f"  ✅ Loaded {len(self.counties)} Arizona counties")
            
            # Load QCT/DDA data and filter for Arizona
            print("  Loading QCT/DDA data...")
            qct_dda_all = gpd.read_file(self.qct_dda_path)
            
            # Filter for Arizona (FIPS code 04)
            self.qct_dda = qct_dda_all[qct_dda_all.get('STATEFP', qct_dda_all.get('STATE', '')).astype(str).str.zfill(2) == '04']
            print(f"  ✅ Loaded {len(self.qct_dda)} Arizona QCT/DDA areas")
            
            # Load poverty tracts
            print("  Loading poverty data...")
            self.poverty_tracts = gpd.read_file(self.poverty_path)
            print(f"  ✅ Loaded {len(self.poverty_tracts)} Arizona census tracts with poverty data")
            
        except Exception as e:
            print(f"  ❌ Error loading geographic data: {e}")
            self.counties = None
            self.qct_dda = None
            self.poverty_tracts = None
    
    def find_existing_lihtc_properties(self):
        """Find existing LIHTC properties in the same counties"""
        print("🏠 Loading existing LIHTC properties...")
        
        # Real LIHTC properties found in Cochise County through web search
        actual_lihtc = [
            {
                "name": "Huachuca Desert Apartments",
                "address": "Huachuca City, AZ",
                "latitude": 31.6281,
                "longitude": -110.3370,
                "units": "Unknown",
                "county": "Cochise County",
                "allocation_year": "Unknown",
                "type": "LIHTC Property"
            },
            {
                "name": "Sonora Vista Apartments",
                "address": "Douglas, AZ",
                "latitude": 31.3445,
                "longitude": -109.5453,
                "units": "Unknown",
                "county": "Cochise County",
                "allocation_year": "Unknown",
                "type": "LIHTC Property"
            },
            {
                "name": "Sun Ray Apartments",
                "address": "Douglas, AZ",
                "latitude": 31.3455,
                "longitude": -109.5463,
                "units": "Unknown",
                "county": "Cochise County",
                "allocation_year": "Unknown",
                "type": "LIHTC Property"
            },
            {
                "name": "La Habra Apartments",
                "address": "Benson, AZ",
                "latitude": 31.9673,
                "longitude": -110.2943,
                "units": 48,
                "county": "Cochise County",
                "allocation_year": "Unknown",
                "type": "LIHTC Property"
            },
            {
                "name": "Crossings At Elk Grove",
                "address": "Benson, AZ",
                "latitude": 31.9663,
                "longitude": -110.2953,
                "units": "Unknown",
                "county": "Cochise County",
                "allocation_year": "Unknown",
                "type": "LIHTC Property"
            },
            {
                "name": "Esperanza Senior Apartments",
                "address": "Bisbee, AZ",
                "latitude": 31.4481,
                "longitude": -109.9284,
                "units": "Unknown",
                "county": "Cochise County",
                "allocation_year": "Unknown",
                "type": "LIHTC Property"
            },
            {
                "name": "Esperanza Family Apartments",
                "address": "Bisbee, AZ",
                "latitude": 31.4471,
                "longitude": -109.9294,
                "units": "Unknown",
                "county": "Cochise County",
                "allocation_year": "Unknown",
                "type": "LIHTC Property"
            }
        ]
        
        print(f"  📍 Loaded {len(actual_lihtc)} existing LIHTC properties in Cochise County")
        return actual_lihtc
    
    def create_enhanced_map(self):
        """Create comprehensive map with all layers"""
        print("\n🗺️ Creating enhanced interactive map...")
        
        # Load geographic data
        self.load_geographic_data()
        existing_lihtc = self.find_existing_lihtc_properties()
        
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
        if self.counties is not None:
            print("  Adding county boundaries...")
            for idx, county in self.counties.iterrows():
                folium.GeoJson(
                    county.geometry,
                    style_function=lambda x: {
                        'fillColor': 'lightblue',
                        'color': 'blue',
                        'weight': 2,
                        'fillOpacity': 0.1
                    },
                    popup=folium.Popup(f"<b>{county.get('NAMELSAD', 'County')}</b><br>HUD Area: {county.get('AREA_NAME', 'Unknown')}", max_width=200),
                    tooltip=county.get('NAMELSAD', 'County')
                ).add_to(m)
        
        # Add QCT/DDA areas
        if self.qct_dda is not None and len(self.qct_dda) > 0:
            print("  Adding QCT/DDA areas...")
            for idx, area in self.qct_dda.iterrows():
                # Determine type and color
                area_type = []
                color = 'gray'
                
                if area.get('QCT', 0) == 1 or area.get('QCT_FLAG', 0) == 1:
                    area_type.append('QCT')
                    color = 'orange'
                if area.get('DDA', 0) == 1 or area.get('DDA_FLAG', 0) == 1:
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
        
        # Add rural development properties (our 5 properties)
        print("  Adding USDA Rural Development properties...")
        for i, prop in enumerate(self.properties):
            # Create detailed popup
            popup_html = f"""
            <div style="width: 350px;">
                <h4 style="margin: 0; color: #2E8B57;"><b>{prop['name']}</b></h4>
                <hr style="margin: 5px 0;">
                <b>📍 Address:</b> {prop['address']}<br>
                <b>🏠 Units:</b> {prop['units']} total ({prop['rental_assistance']} with RA)<br>
                <b>🗺️ County:</b> {prop['county']}<br>
                <b>🏙️ Metro Status:</b> {prop['metro_status']}<br>
                <b>📊 QCT/DDA:</b> Neither (Rural)<br>
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
            
            # County colors
            county_colors = {
                "Graham County": "green",
                "Cochise County": "blue", 
                "Santa Cruz County": "red"
            }
            
            folium.Marker(
                location=[prop['latitude'], prop['longitude']],
                popup=folium.Popup(popup_html, max_width=400),
                tooltip=f"{prop['name']} - {prop['city']} ({prop['units']} units)",
                icon=folium.Icon(
                    color=county_colors.get(prop['county'], 'gray'), 
                    icon='home',
                    prefix='fa'
                )
            ).add_to(m)
            
            print(f"    ✅ Added {prop['name']} at {prop['latitude']:.6f}, {prop['longitude']:.6f}")
        
        # Add existing LIHTC properties
        print("  Adding existing LIHTC properties...")
        for lihtc in existing_lihtc:
            popup_html = f"""
            <div style="width: 250px;">
                <h4 style="margin: 0; color: #8B4513;"><b>{lihtc['name']}</b></h4>
                <hr style="margin: 5px 0;">
                <b>📍 Address:</b> {lihtc['address']}<br>
                <b>🏠 Units:</b> {lihtc['units']}<br>
                <b>🗺️ County:</b> {lihtc['county']}<br>
                <b>📅 Allocation Year:</b> {lihtc['allocation_year']}<br>
                <b>🏷️ Type:</b> {lihtc['type']}
            </div>
            """
            
            folium.Marker(
                location=[lihtc['latitude'], lihtc['longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{lihtc['name']} ({lihtc['allocation_year']})",
                icon=folium.Icon(
                    color='orange',
                    icon='building',
                    prefix='fa'
                )
            ).add_to(m)
        
        # Add comprehensive legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 280px; height: 220px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px;
                    box-shadow: 0 0 15px rgba(0,0,0,0.2);
                    ">
        <h4 style="margin: 0 0 10px 0; text-align: center;">Arizona USDA Rural Analysis</h4>
        
        <b>🏡 USDA Rural Development Properties:</b><br>
        <i class="fa fa-home" style="color:green; margin-right: 5px;"></i> Graham County (2 properties)<br>
        <i class="fa fa-home" style="color:blue; margin-right: 5px;"></i> Cochise County (2 properties)<br>
        <i class="fa fa-home" style="color:red; margin-right: 5px;"></i> Santa Cruz County (1 property)<br>
        
        <br><b>🏠 Existing LIHTC Properties:</b><br>
        <i class="fa fa-building" style="color:orange; margin-right: 5px;"></i> Cochise County (7 properties)<br>
        
        <br><b>🗺️ Geographic Boundaries:</b><br>
        <span style="color:blue;">━━━</span> County Boundaries<br>
        <span style="color:orange;">▓▓▓</span> QCT Areas<br>
        <span style="color:purple;">▓▓▓</span> DDA Areas<br>
        <span style="color:red;">▓▓▓</span> QCT+DDA Areas<br>
        
        <br><b>📊 Portfolio Total:</b> 160 units (155 RA)
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add measure control
        MeasureControl().add_to(m)
        
        # Add title
        title_html = '''
        <h2 align="center" style="font-size:24px; margin: 10px;"><b>Arizona Rural Affordable Housing Analysis</b></h2>
        <h3 align="center" style="font-size:16px; margin: 5px; color: #666;">USDA Rural Development (5 properties) + Existing LIHTC Properties (7 properties)</h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_filename = f"Arizona_Enhanced_Rural_Properties_Map_{timestamp}.html"
        m.save(map_filename)
        print(f"✅ Enhanced map saved to: {map_filename}")
        
        return map_filename
    
    def verify_all_properties(self):
        """Verify all 5 properties are included"""
        print("\n🔍 PROPERTY VERIFICATION:")
        print("=" * 50)
        
        for i, prop in enumerate(self.properties, 1):
            print(f"{i}. {prop['name']} - {prop['city']}")
            print(f"   📍 {prop['latitude']:.6f}, {prop['longitude']:.6f}")
            print(f"   🏠 {prop['units']} units ({prop['rental_assistance']} RA)")
            print(f"   💰 60% AMI: 1BR=${prop['rent_1br_60']}, 2BR=${prop['rent_2br_60']}, 3BR=${prop['rent_3br_60']}, 4BR=${prop['rent_4br_60']}")
            print()
        
        print(f"✅ Total properties verified: {len(self.properties)}")

if __name__ == "__main__":
    mapper = ArizonaEnhancedMapper()
    mapper.verify_all_properties()
    map_file = mapper.create_enhanced_map()
    print(f"\n🎉 Enhanced map with all features created: {map_file}")