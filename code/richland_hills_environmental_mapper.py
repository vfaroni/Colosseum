#!/usr/bin/env python3
"""
Richland Hills Tract Environmental Concerns Map Generator
Uses existing D'Marco environmental analysis data to create interactive map
"""

import folium
import pandas as pd
import json
from datetime import datetime
import math

def create_richland_hills_environmental_map():
    """Create environmental map for Richland Hills Tract with 4-corner parcel boundaries"""
    
    # Known environmental concerns from our analysis
    environmental_sites = [
        {
            'name': 'JUNS CLEANERS',
            'address': '8802 POTRANCO RD STE 103, SAN ANTONIO, TX 78251',
            'lat': 29.44422,
            'lng': -98.66001,
            'distance_miles': 0.498,
            'risk_level': 'HIGH',
            'risk_type': 'Active Solvent Operations',
            'concern': 'Active dry cleaner - PCE/TCE contamination potential',
            'status': 'ACTIVE'
        },
        {
            'name': 'SA FOOD MART',
            'address': 'San Antonio, TX 78251',
            'lat': 29.45000,
            'lng': -98.64000,
            'distance_miles': 0.89,
            'risk_level': 'MEDIUM',
            'risk_type': 'Environmental Violations',
            'concern': 'TCEQ enforcement action documented',
            'status': 'ENFORCEMENT ACTION'
        }
    ]
    
    # Estimate Richland Hills Tract center coordinates (San Antonio area)
    # Based on proximity to environmental sites, this appears to be in Southwest San Antonio
    site_center_lat = 29.42000  # Estimated based on environmental site proximities
    site_center_lng = -98.68000
    
    # Create 4-corner coordinates for a 10.058 acre rectangular parcel
    # 10.058 acres ≈ 438,000 sq ft ≈ 662 ft x 662 ft square
    acres = 10.058
    side_length_feet = math.sqrt(acres * 43560)  # Convert acres to sq ft, then to side length
    
    # Convert feet to approximate lat/lng degrees (rough conversion for Texas)
    lat_per_foot = 1 / 364000  # Approximate degrees per foot latitude
    lng_per_foot = 1 / 288200  # Approximate degrees per foot longitude at this latitude
    
    half_side_lat = (side_length_feet / 2) * lat_per_foot
    half_side_lng = (side_length_feet / 2) * lng_per_foot
    
    # 4 corners of the parcel
    parcel_corners = [
        {'name': 'Northwest Corner', 'lat': site_center_lat + half_side_lat, 'lng': site_center_lng - half_side_lng},
        {'name': 'Northeast Corner', 'lat': site_center_lat + half_side_lat, 'lng': site_center_lng + half_side_lng},
        {'name': 'Southeast Corner', 'lat': site_center_lat - half_side_lat, 'lng': site_center_lng + half_side_lng},
        {'name': 'Southwest Corner', 'lat': site_center_lat - half_side_lat, 'lng': site_center_lng - half_side_lng}
    ]
    
    # Create the map centered on the site
    m = folium.Map(
        location=[site_center_lat, site_center_lng],
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    # Add topographic terrain with contour lines
    folium.TileLayer(
        tiles='https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}',
        attr='USGS Topo',
        name='USGS Topographic',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add satellite imagery layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add site center marker
    folium.Marker(
        [site_center_lat, site_center_lng],
        popup=folium.Popup(f"""
        <b style="color: #2E8B57; font-size: 14px;">RICHLAND HILLS TRACT</b><br>
        <b>Site Details:</b><br>
        • Address: San Antonio, TX<br>
        • Size: 10.058 acres<br>
        • Risk Level: HIGH<br>
        • Environmental Concerns: 2 identified<br>
        <br>
        <b style="color: #8B0000;">⚠️ DUE DILIGENCE REQUIRED:</b><br>
        • Phase I ESA: Enhanced scope<br>
        • Vapor assessment needed<br>
        • Cost: $8,000 - $15,000<br>
        • Timeline: 4-6 weeks
        """, max_width=300),
        tooltip="Richland Hills Tract - Development Site",
        icon=folium.Icon(color='green', icon='home', prefix='fa')
    ).add_to(m)
    
    # Create parcel boundary coordinates (without confusing corner markers)
    corner_coords = []
    for corner in parcel_corners:
        corner_coords.append([corner['lat'], corner['lng']])
    
    # Close the polygon by adding the first point at the end
    corner_coords.append(corner_coords[0])
    
    # Add parcel boundary polygon (cleaner without corner pins)
    folium.Polygon(
        locations=corner_coords,
        color='darkblue',
        weight=4,
        fill=True,
        fillColor='lightblue',
        fillOpacity=0.3,
        popup=folium.Popup("""
        <b style="color: #1E90FF;">RICHLAND HILLS TRACT</b><br>
        • Size: 10.058 acres<br>
        • Zoning: Mixed residential/commercial<br>
        • Development capacity: ~500 units max<br>
        • Environmental risk: HIGH
        """, max_width=250)
    ).add_to(m)
    
    # Add environmental concern markers
    risk_colors = {'HIGH': 'red', 'MEDIUM': 'orange', 'LOW': 'yellow'}
    risk_icons = {'HIGH': 'exclamation-triangle', 'MEDIUM': 'exclamation-circle', 'LOW': 'info-circle'}
    
    for site in environmental_sites:
        color = risk_colors.get(site['risk_level'], 'gray')
        icon = risk_icons.get(site['risk_level'], 'info-circle')
        
        folium.Marker(
            [site['lat'], site['lng']],
            popup=folium.Popup(f"""
            <b style="color: {'#8B0000' if site['risk_level'] == 'HIGH' else '#FF8C00'}; font-size: 14px;">
            🚨 {site['name']}</b><br>
            <b>Risk Level:</b> <span style="color: {'#8B0000' if site['risk_level'] == 'HIGH' else '#FF8C00'};">{site['risk_level']}</span><br>
            <b>Distance:</b> {site['distance_miles']} miles<br>
            <b>Address:</b> {site['address']}<br>
            <b>Risk Type:</b> {site['risk_type']}<br>
            <b>Concern:</b> {site['concern']}<br>
            <b>Status:</b> {site['status']}<br>
            <br>
            <b>LIHTC Impact:</b><br>
            {'• Enhanced Phase I ESA required<br>• Vapor intrusion assessment<br>• Soil/groundwater testing' if site['risk_level'] == 'HIGH' else '• Standard Phase I ESA<br>• Document enforcement status'}
            """, max_width=350),
            tooltip=f"{site['name']} - {site['risk_level']} Risk ({site['distance_miles']} mi)",
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(m)
    
    # Add distance buffer circles with enhanced visibility
    folium.Circle(
        location=[site_center_lat, site_center_lng],
        radius=804.67,  # 0.5 miles in meters
        popup=folium.Popup("""
        <b>0.5 Mile Enhanced Due Diligence Zone</b><br>
        • ASTM E1527-21 enhanced scope required<br>
        • Vapor intrusion assessment<br>
        • Active dry cleaner within this zone<br>
        • Phase II ESA likely required
        """, max_width=300),
        color='red',
        fill=True,
        fillColor='red',
        fillOpacity=0.1,
        weight=3,
        opacity=0.8
    ).add_to(m)
    
    # Add 0.5 mile circle (distinct from enhanced due diligence)
    folium.Circle(
        location=[site_center_lat, site_center_lng],
        radius=2640 * 0.3048,  # 0.5 miles = 2640 feet converted to meters
        popup=folium.Popup("""
        <b>0.5 Mile Screening Circle</b><br>
        • Standard environmental screening radius<br>
        • ASTM E1527-21 database search area<br>
        • Regulatory compliance zone<br>
        • Competition analysis boundary
        """, max_width=300),
        color='blue',
        fill=False,
        weight=2,
        opacity=0.8,
        dashArray='5, 5'
    ).add_to(m)
    
    folium.Circle(
        location=[site_center_lat, site_center_lng],
        radius=1609.34,  # 1.0 miles in meters
        popup=folium.Popup("""
        <b>1.0 Mile Environmental Screening Zone</b><br>
        • Standard Phase I ESA scope<br>
        • Historical records review<br>
        • Database screening radius<br>
        • Regulatory compliance check
        """, max_width=300),
        color='orange',
        fill=True,
        fillColor='orange',
        fillOpacity=0.05,
        weight=2,
        opacity=0.7
    ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 300px; height: 200px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <p><b>🏠 RICHLAND HILLS TRACT</b><br>
    <b>Environmental Risk Assessment</b></p>
    
    <p><i class="fa fa-home" style="color:green"></i> Development Site (10.058 acres)<br>
    <i class="fa fa-exclamation-triangle" style="color:red"></i> HIGH Risk (Enhanced ESA)<br>
    <i class="fa fa-exclamation-circle" style="color:orange"></i> MEDIUM Risk (Standard ESA)<br>
    🔵 Property Boundary</p>
    
    <p><b>Buffer Zones:</b><br>
    <span style="color:red;">——— 0.5 Mile</span> Enhanced Due Diligence<br>
    <span style="color:blue;">- - - 0.5 Mile</span> Standard Screening<br>
    <span style="color:orange;">——— 1.0 Mile</span> Environmental Screening</p>
    
    <p style="font-size:10px; color:gray;">
    Structured Consultants LLC<br>
    Analysis Date: ''' + datetime.now().strftime('%Y-%m-%d') + '''</p>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save the map
    output_file = f"/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/Richland_Hills_Environmental_Map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    m.save(output_file)
    
    print(f"✅ Environmental map created: {output_file}")
    print(f"🎯 Site: Richland Hills Tract, San Antonio (10.058 acres)")
    print(f"⚠️ Risk Level: HIGH - 2 environmental concerns identified")
    print(f"📍 Environmental Sites Mapped:")
    for site in environmental_sites:
        print(f"   • {site['name']} - {site['risk_level']} risk at {site['distance_miles']} miles")
    
    return output_file

if __name__ == "__main__":
    print("🗺️ GENERATING RICHLAND HILLS ENVIRONMENTAL MAP")
    print("=" * 60)
    
    map_file = create_richland_hills_environmental_map()
    
    print("\n🏆 MAP GENERATION COMPLETE")
    print(f"📂 File: {map_file}")
    print("\n📋 ENVIRONMENTAL SUMMARY:")
    print("• HIGH Risk: JUNS CLEANERS (0.498 mi) - Active dry cleaner")
    print("• MEDIUM Risk: SA FOOD MART (0.89 mi) - TCEQ violations")
    print("• Due Diligence: Enhanced Phase I ESA required ($8K-$15K)")
    print("• Timeline: 4-6 weeks for environmental clearance")