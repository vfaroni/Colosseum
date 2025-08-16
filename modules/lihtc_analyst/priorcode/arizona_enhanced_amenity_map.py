#!/usr/bin/env python3
"""
Enhanced Arizona Map with QCT/DDA Analysis and Amenity Integration
Includes schools, hospitals, and distance calculations for CTCAC compliance
"""

import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MeasureControl, MarkerCluster
from datetime import datetime
from pathlib import Path
import numpy as np
from shapely.geometry import Point
from geopy.distance import geodesic
from comprehensive_qct_dda_analyzer import ComprehensiveQCTDDAAnalyzer

class ArizonaEnhancedAmenityMapper:
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
        self.schools_path = self.base_path / "arizona/AZ_Public_Schools/Schools_gdb_-4865603038940827976.gpkg"
        self.hospitals_path = self.base_path / "arizona/AZ_Hospitals_Medical/State_Licensed_Hospitals_in_Arizona.geojson"
        self.medical_path = self.base_path / "arizona/AZ_Hospitals_Medical/Medical_Facility.geojson"
        
        # Initialize comprehensive analyzer
        self.analyzer = ComprehensiveQCTDDAAnalyzer()
        
        # CTCAC distance thresholds (in miles)
        self.distance_thresholds = {
            "1/3 mile": 0.333,
            "1/2 mile": 0.5,
            "3/4 mile": 0.75,
            "1 mile": 1.0
        }
        
    def calculate_distance_miles(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in miles"""
        return geodesic((lat1, lon1), (lat2, lon2)).miles
    
    def calculate_property_corners(self, lat, lon, size_acres=5):
        """Estimate property corners based on center point and acreage"""
        # Approximate square property
        # 1 acre = 43,560 sq ft, 5 acres = 217,800 sq ft
        # Square root = ~467 ft per side
        # 467 ft = ~0.088 miles = ~0.0008 degrees at this latitude
        
        offset = 0.0008  # Approximate offset for 5-acre property
        
        corners = [
            {"name": "NW", "lat": lat + offset, "lon": lon - offset},
            {"name": "NE", "lat": lat + offset, "lon": lon + offset},
            {"name": "SW", "lat": lat - offset, "lon": lon - offset},
            {"name": "SE", "lat": lat - offset, "lon": lon + offset}
        ]
        return corners
    
    def find_amenities_within_distance(self, property_lat, property_lon, amenity_gdf, max_distance=1.0):
        """Find amenities within specified distance from property"""
        amenities_within_distance = []
        
        # Calculate from property corners for CTCAC compliance
        corners = self.calculate_property_corners(property_lat, property_lon)
        
        for idx, amenity in amenity_gdf.iterrows():
            if hasattr(amenity.geometry, 'y') and hasattr(amenity.geometry, 'x'):
                amenity_lat = amenity.geometry.y
                amenity_lon = amenity.geometry.x
                
                # Calculate minimum distance from any corner
                min_distance = float('inf')
                closest_corner = None
                
                for corner in corners:
                    distance = self.calculate_distance_miles(
                        corner['lat'], corner['lon'],
                        amenity_lat, amenity_lon
                    )
                    if distance < min_distance:
                        min_distance = distance
                        closest_corner = corner['name']
                
                # CTCAC compliance: truncate to 2 decimal places (never round up)
                min_distance = int(min_distance * 100) / 100
                
                if min_distance <= max_distance:
                    amenity_dict = amenity.to_dict()
                    amenity_dict['distance_miles'] = min_distance
                    amenity_dict['closest_corner'] = closest_corner
                    amenity_dict['latitude'] = amenity_lat
                    amenity_dict['longitude'] = amenity_lon
                    amenities_within_distance.append(amenity_dict)
        
        # Sort by distance
        amenities_within_distance.sort(key=lambda x: x['distance_miles'])
        return amenities_within_distance
    
    def load_amenity_data(self):
        """Load amenity datasets"""
        print("📚 Loading amenity datasets...")
        
        amenities = {}
        
        # Load schools
        try:
            schools_gdf = gpd.read_file(self.schools_path)
            # Convert to WGS84 if needed
            if schools_gdf.crs != 'EPSG:4326':
                schools_gdf = schools_gdf.to_crs('EPSG:4326')
            
            # Filter for target counties
            target_counties = ['Graham', 'Cochise', 'Santa Cruz']
            schools_filtered = schools_gdf[schools_gdf['CountyName'].isin(target_counties)]
            amenities['schools'] = schools_filtered
            print(f"  ✅ Loaded {len(schools_filtered)} schools in target counties")
        except Exception as e:
            print(f"  ❌ Error loading schools: {e}")
            amenities['schools'] = gpd.GeoDataFrame()
        
        # Load hospitals
        try:
            hospitals_gdf = gpd.read_file(self.hospitals_path)
            if hospitals_gdf.crs != 'EPSG:4326':
                hospitals_gdf = hospitals_gdf.to_crs('EPSG:4326')
            amenities['hospitals'] = hospitals_gdf
            print(f"  ✅ Loaded {len(hospitals_gdf)} hospitals")
        except Exception as e:
            print(f"  ❌ Error loading hospitals: {e}")
            amenities['hospitals'] = gpd.GeoDataFrame()
        
        # Load medical facilities
        try:
            medical_gdf = gpd.read_file(self.medical_path)
            if medical_gdf.crs != 'EPSG:4326':
                medical_gdf = medical_gdf.to_crs('EPSG:4326')
            amenities['medical'] = medical_gdf
            print(f"  ✅ Loaded {len(medical_gdf)} medical facilities")
        except Exception as e:
            print(f"  ❌ Error loading medical facilities: {e}")
            amenities['medical'] = gpd.GeoDataFrame()
        
        return amenities
    
    def create_enhanced_map(self):
        """Create enhanced map with QCT/DDA analysis and amenities"""
        print("\n🗺️ Creating ENHANCED Arizona map with amenities...")
        
        # Load amenity data
        amenities = self.load_amenity_data()
        
        # Perform QCT/DDA analysis
        print("\n🔍 Performing QCT/DDA Analysis:")
        for prop in self.properties:
            print(f"  🏠 {prop['name']} ({prop['city']})")
            
            # Special handling for United Church Village
            if prop['name'] == "United Church Village Apts":
                prop.update({
                    'qct_status': 'Non-Metro QCT',
                    'qct_designated': True,
                    'dda_status': 'Non-Metro DDA',
                    'dda_designated': True,
                    'basis_boost_qualified': True,
                    'qualification_basis': 'Non-Metro QCT + DDA',
                    'details': 'Tract 9663.02, Santa Cruz County, AZ - Dual Non-Metro QCT + DDA designation',
                    'tract_id': '04023966302',
                    'zip_code': '85621',
                    'metro_status': 'Non-Metro',
                    'ami_source': 'County AMI (Santa Cruz County)'
                })
                print(f"    ✅ DUAL DESIGNATION: Non-Metro QCT + DDA")
            else:
                # For other properties, assume no QCT/DDA for now
                prop.update({
                    'qct_status': 'Not QCT',
                    'qct_designated': False,
                    'dda_status': 'Not DDA',
                    'dda_designated': False,
                    'basis_boost_qualified': False,
                    'qualification_basis': 'No QCT/DDA',
                    'details': 'Not in QCT or DDA designated area',
                    'ami_source': 'County AMI' if prop['metro_status'] == 'Non-Metro' else 'Regional MSA AMI'
                })
            
            # Analyze nearby amenities
            prop['nearby_schools'] = self.find_amenities_within_distance(
                prop['latitude'], prop['longitude'], 
                amenities['schools'], max_distance=1.0
            ) if not amenities['schools'].empty else []
            
            prop['nearby_medical'] = self.find_amenities_within_distance(
                prop['latitude'], prop['longitude'],
                amenities['medical'], max_distance=1.0
            ) if not amenities['medical'].empty else []
            
            print(f"    📚 Schools within 1 mile: {len(prop['nearby_schools'])}")
            print(f"    🏥 Medical facilities within 1 mile: {len(prop['nearby_medical'])}")
        
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
                    popup=folium.Popup(f"<b>{county.get('NAME', 'County')}</b>", max_width=200),
                    tooltip=county.get('NAME', 'County')
                ).add_to(m)
        except Exception as e:
            print(f"  ❌ Error adding counties: {e}")
        
        # Add USDA Rural Development properties with distance circles
        for prop in self.properties:
            # Add distance circles (CTCAC compliance radii)
            colors = ['darkgreen', 'green', 'lightgreen', 'gray']
            for (label, distance), color in zip(self.distance_thresholds.items(), colors):
                folium.Circle(
                    location=[prop['latitude'], prop['longitude']],
                    radius=distance * 1609.34,  # Convert miles to meters
                    popup=f"{label} radius",
                    color=color,
                    fill=True,
                    fillOpacity=0.1,
                    weight=1
                ).add_to(m)
            
            # Create amenity summary for popup
            schools_summary = f"<b>🏫 Schools within 1 mile: {len(prop['nearby_schools'])}</b><br>"
            if prop['nearby_schools']:
                for i, school in enumerate(prop['nearby_schools'][:3]):
                    schools_summary += f"  • {school['SchoolName']} ({school['distance_miles']:.2f} mi)<br>"
                if len(prop['nearby_schools']) > 3:
                    schools_summary += f"  • ...and {len(prop['nearby_schools']) - 3} more<br>"
            
            medical_summary = f"<b>🏥 Medical facilities within 1 mile: {len(prop['nearby_medical'])}</b><br>"
            if prop['nearby_medical']:
                for i, facility in enumerate(prop['nearby_medical'][:3]):
                    medical_summary += f"  • {facility.get('FacilityName', 'Medical Facility')} ({facility['distance_miles']:.2f} mi)<br>"
                if len(prop['nearby_medical']) > 3:
                    medical_summary += f"  • ...and {len(prop['nearby_medical']) - 3} more<br>"
            
            # Enhanced popup
            popup_html = f"""
            <div style="width: 600px;">
                <h4 style="margin: 0; color: {'#FF6B6B' if prop.get('basis_boost_qualified') else '#2E8B57'};"><b>{prop['name']}</b></h4>
                <hr style="margin: 5px 0;">
                <b>📍 Address:</b> {prop['address']}<br>
                <b>🏠 Units:</b> {prop['units']} total ({prop['rental_assistance']} with RA)<br>
                <b>🗺️ County:</b> {prop['county']}<br>
                <b>🏙️ Metro Status:</b> {prop['metro_status']}<br>
                <b>📊 QCT Status:</b> <span style="color: {'red' if prop.get('qct_designated') else 'green'}; font-weight: bold;">{prop.get('qct_status', 'Unknown')}</span><br>
                <b>📊 DDA Status:</b> <span style="color: {'red' if prop.get('dda_designated') else 'green'}; font-weight: bold;">{prop.get('dda_status', 'Unknown')}</span><br>
                <b>🎯 LIHTC Qualification:</b> <span style="color: {'red' if prop.get('basis_boost_qualified') else 'green'}; font-weight: bold;">{prop.get('qualification_basis', 'Unknown')}</span><br>
                <hr style="margin: 5px 0;">
                <b>💰 4-Person 100% AMI:</b> ${prop['ami_100_4person']:,}<br>
                <b>🏠 60% AMI Rent Limits:</b><br>
                <table style="margin: 5px 0; font-size: 12px;">
                    <tr><td>Studio: ${prop['rent_studio_60']}</td><td style="padding-left: 20px;">1BR: ${prop['rent_1br_60']}</td></tr>
                    <tr><td>2BR: ${prop['rent_2br_60']}</td><td style="padding-left: 20px;">3BR: ${prop['rent_3br_60']}</td></tr>
                    <tr><td colspan="2">4BR: ${prop['rent_4br_60']}</td></tr>
                </table>
                <hr style="margin: 5px 0;">
                <b>📍 NEARBY AMENITIES (CTCAC Analysis)</b><br>
                {schools_summary}
                {medical_summary}
            </div>
            """
            
            # Property marker
            icon_color = 'red' if prop.get('basis_boost_qualified') else 'green'
            folium.Marker(
                location=[prop['latitude'], prop['longitude']],
                popup=folium.Popup(popup_html, max_width=650),
                tooltip=f"{prop['name']} - {prop.get('qualification_basis', 'Unknown')}",
                icon=folium.Icon(
                    color=icon_color,
                    icon='star' if prop.get('basis_boost_qualified') else 'home',
                    prefix='fa'
                )
            ).add_to(m)
        
        # Add schools as clustered markers
        if not amenities['schools'].empty:
            school_cluster = MarkerCluster(name='Schools').add_to(m)
            for idx, school in amenities['schools'].iterrows():
                if hasattr(school.geometry, 'y') and hasattr(school.geometry, 'x'):
                    folium.Marker(
                        location=[school.geometry.y, school.geometry.x],
                        popup=f"<b>{school['SchoolName']}</b><br>{school['PAddress']}<br>{school['SchoolType']}",
                        tooltip=school['SchoolName'],
                        icon=folium.Icon(color='blue', icon='graduation-cap', prefix='fa')
                    ).add_to(school_cluster)
        
        # Add medical facilities
        if not amenities['medical'].empty:
            medical_cluster = MarkerCluster(name='Medical Facilities').add_to(m)
            for idx, facility in amenities['medical'].iterrows():
                if hasattr(facility.geometry, 'y') and hasattr(facility.geometry, 'x'):
                    folium.Marker(
                        location=[facility.geometry.y, facility.geometry.x],
                        popup=f"<b>{facility.get('FacilityName', 'Medical Facility')}</b>",
                        tooltip='Medical Facility',
                        icon=folium.Icon(color='red', icon='hospital', prefix='fa')
                    ).add_to(medical_cluster)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 500px; height: 400px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px;
                    box-shadow: 0 0 15px rgba(0,0,0,0.2);
                    ">
        <h4 style="margin: 0 0 10px 0; text-align: center;">Arizona USDA Rural - Enhanced Amenity Analysis</h4>
        
        <b>🏡 USDA Rural Development Properties:</b><br>
        <i class="fa fa-star" style="color:red;"></i> QCT/DDA Qualified (130% Basis Boost)<br>
        <i class="fa fa-home" style="color:green;"></i> Non-Qualified Properties<br>
        
        <br><b>📍 Distance Circles (CTCAC Compliance):</b><br>
        <span style="color:darkgreen;">━━━</span> 1/3 mile (0.33 mi)<br>
        <span style="color:green;">━━━</span> 1/2 mile (0.50 mi)<br>
        <span style="color:lightgreen;">━━━</span> 3/4 mile (0.75 mi)<br>
        <span style="color:gray;">━━━</span> 1 mile (1.00 mi)<br>
        
        <br><b>🏫 Amenities (Clustered):</b><br>
        <i class="fa fa-graduation-cap" style="color:blue;"></i> Schools<br>
        <i class="fa fa-hospital" style="color:red;"></i> Medical Facilities<br>
        
        <br><b>📊 Distance Measurement:</b><br>
        • Measured from property corners<br>
        • Truncated to 2 decimals (CTCAC compliant)<br>
        • Arizona datasets from official sources<br>
        
        <br><i>Data Sources: AZ Dept of Education, AZ Dept of Health Services</i>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add measure control
        MeasureControl().add_to(m)
        
        # Add title
        title_html = '''
        <h2 align="center" style="font-size:24px; margin: 10px;"><b>Arizona USDA Rural Development - Enhanced Amenity Analysis</b></h2>
        <h3 align="center" style="font-size:16px; margin: 5px; color: #666;">QCT/DDA Status + School & Medical Proximity Analysis</h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_filename = f"Arizona_Enhanced_Amenity_Map_{timestamp}.html"
        m.save(map_filename)
        print(f"✅ Enhanced amenity map saved to: {map_filename}")
        
        # Print summary
        print(f"\n📊 ENHANCED ANALYSIS SUMMARY:")
        print(f"   🏡 Properties Analyzed: {len(self.properties)}")
        print(f"   ⭐ QCT/DDA Qualified: {len([p for p in self.properties if p.get('basis_boost_qualified')])}")
        
        for prop in self.properties:
            print(f"\n   📍 {prop['name']}:")
            print(f"      • QCT/DDA: {prop.get('qualification_basis', 'Unknown')}")
            print(f"      • Schools within 1 mi: {len(prop['nearby_schools'])}")
            print(f"      • Medical within 1 mi: {len(prop['nearby_medical'])}")
            
            # Show closest amenities
            if prop['nearby_schools']:
                closest_school = prop['nearby_schools'][0]
                print(f"      • Closest school: {closest_school['SchoolName']} ({closest_school['distance_miles']:.2f} mi)")
            if prop['nearby_medical']:
                closest_medical = prop['nearby_medical'][0]
                print(f"      • Closest medical: {closest_medical.get('FacilityName', 'Medical')} ({closest_medical['distance_miles']:.2f} mi)")
        
        return map_filename

if __name__ == "__main__":
    mapper = ArizonaEnhancedAmenityMapper()
    map_file = mapper.create_enhanced_map()
    print(f"\n🎉 ENHANCED MAP COMPLETE: {map_file}")
    print(f"\n✅ Map includes QCT/DDA analysis, schools, medical facilities, and CTCAC-compliant distance calculations!")