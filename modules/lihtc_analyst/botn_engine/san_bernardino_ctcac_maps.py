#!/usr/bin/env python3
"""
Create CTCAC-style HTML maps for San Bernardino sites
Matching the style of the Perris/San Jacinto mapper
"""

import folium
from folium import plugins
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

def create_san_bernardino_map(site_name, address, lat, lng, parcel_corners, apn, area_acres):
    """
    Create CTCAC-style map for a San Bernardino site
    
    Args:
        site_name: Name of the site
        address: Site address
        lat, lng: Center coordinates
        parcel_corners: List of (lat, lng) tuples for parcel corners
        apn: Assessor Parcel Number
        area_acres: Parcel area in acres
    """
    
    # Create base map
    m = folium.Map(location=[lat, lng], zoom_start=17)
    
    # Add map controls
    plugins.MeasureControl(position='topright', active_color='blue', completed_color='red').add_to(m)
    folium.plugins.MiniMap(toggle_display=True).add_to(m)
    
    # Add parcel boundary
    if parcel_corners:
        # Ensure polygon is closed
        boundary_coords = list(parcel_corners)
        if boundary_coords[0] != boundary_coords[-1]:
            boundary_coords.append(boundary_coords[0])
            
        folium.Polygon(
            locations=boundary_coords,
            color='darkred',
            weight=3,
            fill=True,
            fillColor='red',
            fillOpacity=0.1,
            popup=f'<b>{site_name} Parcel</b><br>APN: {apn}<br>Area: {area_acres} acres'
        ).add_to(m)
        
        # Add corner markers
        for i, (corner_lat, corner_lng) in enumerate(parcel_corners[:4]):  # First 4 corners
            label = ['NW', 'NE', 'SE', 'SW'][i] if i < 4 else f'C{i+1}'
            folium.Marker(
                [corner_lat, corner_lng],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 10pt; color: darkred; font-weight: bold; '
                         f'background: white; padding: 2px 4px; border: 1px solid darkred; '
                         f'border-radius: 3px;">{label}</div>'
                )
            ).add_to(m)
    
    # Add center marker
    folium.Marker(
        [lat, lng],
        popup=f"""<b>{site_name}</b><br>
                 {address}<br>
                 APN: {apn}<br>
                 Center: {lat:.6f}, {lng:.6f}<br>
                 Area: {area_acres} acres<br>
                 <i>Note: Amenity data not loaded</i>""",
        icon=folium.Icon(color='red', icon='home')
    ).add_to(m)
    
    # Add distance circles (reference distances from site center)
    reference_distances = [
        (0.25, 'black', '0.25 mile', '5,5'),
        (0.333, 'gray', '1/3 mile', '10,5'),
        (0.5, 'darkgray', '0.5 mile', '15,5'),
        (0.75, 'lightgray', '0.75 mile', '20,5'),
        (1.0, 'lightgray', '1.0 mile', '25,5')
    ]
    
    for dist_miles, color, label, dash in reference_distances:
        # Convert miles to meters for folium
        radius_meters = dist_miles * 1609.34
        
        folium.Circle(
            location=[lat, lng],
            radius=radius_meters,
            popup=f'{label} radius',
            color=color,
            fill=False,
            weight=2,
            dash_array=dash
        ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style='position: fixed; 
                top: 10px; right: 50px; width: 300px; height: auto;
                background-color: white; z-index: 1000; 
                border:2px solid grey; font-size: 14px;
                padding: 10px'>
    <h4 style='margin-top:0; text-align: center;'>CTCAC Amenity Map</h4>
    <b>{}</b><br>
    APN: {}<br>
    <hr style='margin: 5px 0;'>
    <b>Distance Circles:</b><br>
    ⚫ 0.25 mile (Elementary School)<br>
    🔘 1/3 mile (Transit)<br>
    ⚪ 0.5 mile (Parks, Grocery, Medical)<br>
    ⚪ 0.75 mile (High School)<br>
    ⚪ 1.0 mile (Extended distances)<br>
    <hr style='margin: 5px 0;'>
    <b>Parcel Information:</b><br>
    📍 {} corners mapped<br>
    📐 Area: {} acres<br>
    <hr style='margin: 5px 0;'>
    <i>Note: Amenity locations not loaded.<br>
    Add actual grocery, transit, school,<br>
    medical, and park locations for<br>
    complete CTCAC scoring.</i>
    </div>
    '''.format(site_name, apn, len(parcel_corners), area_acres)
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m


def process_san_bernardino_sites():
    """Process the 3 San Bernardino sites and create maps"""
    
    # Load the analysis results
    results_file = Path('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport-11_SB_REAL_ANALYSIS_20250806_205547.xlsx')
    
    # Read parcel analysis results
    df = pd.read_excel(results_file, sheet_name='Parcel_Analysis')
    success_sites = df[df['status'] == 'Success']
    
    print("🗺️ Creating CTCAC Maps for San Bernardino Sites")
    print("=" * 60)
    
    for idx, row in success_sites.iterrows():
        site_num = idx + 1
        
        # Parse corner coordinates
        corners_json = row['corners_json']
        corners = json.loads(corners_json) if corners_json else []
        
        print(f"\n📍 Site {site_num}: {row['address']}")
        print(f"   APN: {row['apn']}")
        print(f"   Corners: {row['num_corners']}")
        print(f"   Area: {row['area_acres']} acres")
        
        # Create map
        m = create_san_bernardino_map(
            site_name=f"Site {site_num}",
            address=row['address'],
            lat=row['lat'],
            lng=row['lng'],
            parcel_corners=corners,
            apn=row['apn'],
            area_acres=row['area_acres']
        )
        
        # Save map
        output_file = f"san_bernardino_site_{site_num}_ctcac_map.html"
        m.save(output_file)
        print(f"   ✅ Map saved: {output_file}")
    
    print("\n" + "="*60)
    print("✅ All maps created successfully!")
    print("\nTo add amenities, you can provide:")
    print("- 🚌 Transit stops (within 1/3 mile for max points)")
    print("- 🏫 Schools (elementary within 0.25 mi, high school within 0.75 mi)")
    print("- 🛒 Grocery stores (within 0.5 mi for max points)")
    print("- 🏥 Medical facilities (within 0.5 mi)")
    print("- 🌳 Parks (within 0.5 mi)")
    print("- 💊 Pharmacies (within 0.5 mi)")


if __name__ == "__main__":
    process_san_bernardino_sites()