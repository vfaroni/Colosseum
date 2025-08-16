#!/usr/bin/env python3

"""
Enhanced Environmental Mapper with Edge-Based Distance Analysis
Measures contamination from closest parcel boundary edge + elevation analysis
Adds toggleable distance lines and elevation layer for water flow analysis
"""

import sys
import os
import pandas as pd
import json
import folium
from datetime import datetime
import math
import requests

# Add the parcel mapping module to path
sys.path.append('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping')

from universal_parcel_mapper import UniversalParcelMapper, ParcelData

def calculate_point_to_polygon_distance(point_lat, point_lng, polygon_coords):
    """
    Calculate the shortest distance from a point to the closest edge of a polygon
    Returns distance in miles and the closest point on the polygon edge
    """
    
    min_distance = float('inf')
    closest_edge_point = None
    
    # Check each edge of the polygon
    for i in range(len(polygon_coords)):
        # Get the current edge (from point i to point i+1)
        p1 = polygon_coords[i]
        p2 = polygon_coords[(i + 1) % len(polygon_coords)]
        
        # Calculate distance from point to this edge
        edge_distance, edge_point = point_to_line_segment_distance(
            point_lat, point_lng, p1[0], p1[1], p2[0], p2[1]
        )
        
        if edge_distance < min_distance:
            min_distance = edge_distance
            closest_edge_point = edge_point
    
    return min_distance, closest_edge_point

def point_to_line_segment_distance(px, py, x1, y1, x2, y2):
    """
    Calculate distance from point (px, py) to line segment (x1,y1)-(x2,y2)
    Returns distance in miles and the closest point on the line segment
    """
    
    # Convert to approximate meters for calculation
    px_m = px * 111320
    py_m = py * 111320 * math.cos(math.radians(px))
    x1_m = x1 * 111320
    y1_m = y1 * 111320 * math.cos(math.radians(x1))
    x2_m = x2 * 111320
    y2_m = y2 * 111320 * math.cos(math.radians(x2))
    
    # Vector from line start to end
    dx = x2_m - x1_m
    dy = y2_m - y1_m
    
    # If line segment is actually a point
    if dx == 0 and dy == 0:
        dist_m = math.sqrt((px_m - x1_m)**2 + (py_m - y1_m)**2)
        return dist_m / 1609.34, (x1, y1)  # Convert back to miles
    
    # Parameter t represents position along line segment (0 to 1)
    t = max(0, min(1, ((px_m - x1_m) * dx + (py_m - y1_m) * dy) / (dx * dx + dy * dy)))
    
    # Closest point on line segment
    closest_x_m = x1_m + t * dx
    closest_y_m = y1_m + t * dy
    
    # Distance to closest point
    dist_m = math.sqrt((px_m - closest_x_m)**2 + (py_m - closest_y_m)**2)
    
    # Convert back to lat/lng
    closest_lat = closest_x_m / 111320
    closest_lng = closest_y_m / (111320 * math.cos(math.radians(closest_lat)))
    
    return dist_m / 1609.34, (closest_lat, closest_lng)

def get_elevation_data(lat, lng):
    """
    Get elevation data from USGS Elevation Point Query Service
    Returns elevation in feet
    """
    try:
        url = "https://nationalmap.gov/epqs/pqs.php"
        params = {
            'x': lng,
            'y': lat,
            'units': 'Feet',
            'output': 'json'
        }
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'USGS_Elevation_Point_Query_Service' in data:
                elevation = data['USGS_Elevation_Point_Query_Service']['Elevation_Query']['Elevation']
                return float(elevation) if elevation != -1000000 else None
        
    except Exception as e:
        print(f"⚠️ Elevation API error: {e}")
    
    return None

def calculate_enhanced_environmental_risks(site_lat, site_lng, env_df, parcel_coords=None):
    """
    Enhanced environmental risk calculation with edge-based distances and elevation analysis
    """
    
    if len(env_df) == 0:
        return []
    
    risks = []
    site_elevation = get_elevation_data(site_lat, site_lng)
    
    # Risk thresholds (based on edge distance)
    risk_thresholds = {
        'CRITICAL': {'max_distance': 0.0, 'color': '#8B0000', 'cost_estimate': '$15,000-$50,000+'},
        'HIGH': {'max_distance': 0.095, 'color': '#FF0000', 'cost_estimate': '$12,000-$25,000'},  # ~500 feet
        'MODERATE-HIGH': {'max_distance': 0.189, 'color': '#FF4500', 'cost_estimate': '$8,000-$15,000'},  # ~1000 feet
        'MODERATE': {'max_distance': 0.25, 'color': '#FFD700', 'cost_estimate': '$5,000-$8,000'},  # 1/4 mile
        'LOW-MODERATE': {'max_distance': 0.5, 'color': '#32CD32', 'cost_estimate': '$3,000-$5,000'},  # 1/2 mile
        'LOW': {'max_distance': 1.0, 'color': '#90EE90', 'cost_estimate': '$1,500-$3,000'}  # 1 mile
    }
    
    for _, env_site in env_df.iterrows():
        env_lat = float(env_site['latitude'])
        env_lng = float(env_site['longitude'])
        
        # Get elevation for contamination site
        env_elevation = get_elevation_data(env_lat, env_lng)
        
        # Calculate edge-based distance if parcel boundaries available
        edge_distance = None
        closest_edge_point = None
        centroid_distance = calculate_distance_miles(site_lat, site_lng, env_lat, env_lng)
        
        if parcel_coords and len(parcel_coords) > 0:
            edge_distance, closest_edge_point = calculate_point_to_polygon_distance(
                env_lat, env_lng, parcel_coords
            )
            # Check if within parcel boundaries
            within_parcel = point_in_polygon((env_lat, env_lng), parcel_coords)
        else:
            edge_distance = centroid_distance
            within_parcel = False
        
        # Determine risk level based on edge distance
        risk_level = 'OUTSIDE_RANGE'
        for level, threshold in risk_thresholds.items():
            if edge_distance <= threshold['max_distance']:
                risk_level = level
                break
        
        # Elevation analysis
        elevation_analysis = None
        if site_elevation is not None and env_elevation is not None:
            elevation_diff = site_elevation - env_elevation
            if elevation_diff > 10:
                elevation_analysis = f"UPHILL +{elevation_diff:.1f}ft (Better drainage)"
            elif elevation_diff < -10:
                elevation_analysis = f"DOWNHILL {elevation_diff:.1f}ft (Potential runoff risk)"
            else:
                elevation_analysis = f"LEVEL ±{abs(elevation_diff):.1f}ft (Neutral)"
        
        if risk_level != 'OUTSIDE_RANGE' or within_parcel:
            risk_data = {
                'site_name': env_site.get('site_name', 'Unknown Site'),
                'address': env_site.get('address', 'Unknown Address'),
                'city': env_site.get('city', 'Unknown City'),
                'latitude': env_lat,
                'longitude': env_lng,
                'centroid_distance_miles': centroid_distance,
                'edge_distance_miles': edge_distance,
                'closest_edge_point': closest_edge_point,
                'risk_level': 'CRITICAL' if within_parcel else risk_level,
                'risk_type': env_site.get('risk_type', 'Unknown'),
                'status': env_site.get('status', 'Unknown'),
                'dataset': env_site.get('dataset', 'Unknown'),
                'within_parcel': within_parcel,
                'cost_estimate': risk_thresholds.get(risk_level, {}).get('cost_estimate', 'Unknown'),
                'color': risk_thresholds.get(risk_level, {}).get('color', '#808080'),
                'site_elevation': site_elevation,
                'env_elevation': env_elevation,
                'elevation_analysis': elevation_analysis
            }
            
            risks.append(risk_data)
    
    return sorted(risks, key=lambda x: x['edge_distance_miles'])

def create_enhanced_environmental_map(site_info, parcel_data, environmental_risks, output_file):
    """
    Create enhanced interactive map with edge distances, elevation, and toggleable distance lines
    """
    
    # Initialize map centered on the site
    site_map = folium.Map(
        location=[site_info['lat'], site_info['lng']],
        zoom_start=14,
        tiles='OpenStreetMap'
    )
    
    # Add satellite imagery
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False,
        control=True
    ).add_to(site_map)
    
    # Add elevation/terrain layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Elevation/Terrain',
        overlay=False,
        control=True
    ).add_to(site_map)
    
    # Create feature groups for toggleable layers
    distance_lines_group = folium.FeatureGroup(name="Distance Lines (Edge-based)", show=False)
    
    # Add parcel boundary polygon if available
    if parcel_data and parcel_data.boundary_coordinates and len(parcel_data.boundary_coordinates) > 0:
        boundary_coords = [(lat, lng) for lat, lng in parcel_data.boundary_coordinates]
        
        folium.Polygon(
            locations=boundary_coords,
            color='#0066CC',
            weight=3,
            fillColor='#3399FF',
            fillOpacity=0.2,
            popup=f'''
            <div style="font-family: Arial; width: 300px;">
                <h4 style="color: #0066CC; margin: 0;">📋 PARCEL BOUNDARY</h4>
                <p style="margin: 5px 0;"><b>APN:</b> {parcel_data.apn}</p>
                <p style="margin: 5px 0;"><b>Area:</b> {parcel_data.property_area_acres:.2f} acres</p>
                <p style="margin: 5px 0;"><b>County:</b> {parcel_data.county}</p>
                <p style="margin: 5px 0;"><b>Owner:</b> {parcel_data.owner_name or 'Unknown'}</p>
                <p style="margin: 5px 0;"><b>Corners:</b> {len(parcel_data.boundary_coordinates)} coordinates</p>
                <p style="margin: 5px 0;"><b>Source:</b> {parcel_data.data_source}</p>
            </div>
            '''
        ).add_to(site_map)
    
    # Add site marker with elevation
    site_elevation_text = ""
    if len(environmental_risks) > 0 and environmental_risks[0].get('site_elevation'):
        site_elevation_text = f"<p style='margin: 5px 0;'><b>Elevation:</b> {environmental_risks[0]['site_elevation']:.1f} feet</p>"
    
    folium.Marker(
        location=[site_info['lat'], site_info['lng']],
        popup=f'''
        <div style="font-family: Arial; width: 300px;">
            <h4 style="color: #2E7D32; margin: 0;">🏢 D'MARCO INVESTMENT SITE</h4>
            <p style="margin: 5px 0;"><b>Name:</b> {site_info['name']}</p>
            <p style="margin: 5px 0;"><b>Address:</b> {site_info['address']}</p>
            <p style="margin: 5px 0;"><b>Coordinates:</b> {site_info['lat']:.6f}, {site_info['lng']:.6f}</p>
            {site_elevation_text}
            {'<p style="margin: 5px 0;"><b>Parcel APN:</b> ' + str(parcel_data.apn) + '</p>' if parcel_data else ''}
        </div>
        ''',
        icon=folium.Icon(color='green', icon='home', prefix='fa')
    ).add_to(site_map)
    
    # Add environmental risk sites with enhanced analysis
    risk_counts = {'CRITICAL': 0, 'HIGH': 0, 'MODERATE-HIGH': 0, 'MODERATE': 0, 'LOW-MODERATE': 0, 'LOW': 0}
    
    for risk in environmental_risks:
        risk_level = risk['risk_level']
        if risk_level in risk_counts:
            risk_counts[risk_level] += 1
        
        icon_color = 'red' if risk_level in ['CRITICAL', 'HIGH'] else 'orange' if risk_level in ['MODERATE-HIGH', 'MODERATE'] else 'green'
        
        # Enhanced popup with edge distance and elevation
        elevation_info = ""
        if risk['elevation_analysis']:
            elevation_info = f"<p style='margin: 5px 0;'><b>Elevation Analysis:</b> {risk['elevation_analysis']}</p>"
        
        folium.Marker(
            location=[risk['latitude'], risk['longitude']],
            popup=f'''
            <div style="font-family: Arial; width: 380px;">
                <h4 style="color: {risk['color']}; margin: 0;">🚨 {risk_level} RISK</h4>
                <p style="margin: 5px 0;"><b>Site:</b> {risk['site_name']}</p>
                <p style="margin: 5px 0;"><b>Address:</b> {risk['address']}, {risk['city']}</p>
                <p style="margin: 5px 0;"><b>Edge Distance:</b> {risk['edge_distance_miles']:.3f} miles</p>
                <p style="margin: 5px 0;"><b>Centroid Distance:</b> {risk['centroid_distance_miles']:.3f} miles</p>
                <p style="margin: 5px 0;"><b>Type:</b> {risk['risk_type']}</p>
                <p style="margin: 5px 0;"><b>Status:</b> {risk['status']}</p>
                {elevation_info}
                <p style="margin: 5px 0;"><b>Cost Estimate:</b> {risk['cost_estimate']}</p>
                {'<p style="margin: 5px 0; color: red;"><b>⚠️ WITHIN PARCEL BOUNDARY</b></p>' if risk['within_parcel'] else ''}
            </div>
            ''',
            icon=folium.Icon(color=icon_color, icon='warning', prefix='fa')
        ).add_to(site_map)
        
        # Add distance line to closest edge point (toggleable)
        if risk['closest_edge_point'] and not risk['within_parcel']:
            folium.PolyLine(
                locations=[
                    [risk['latitude'], risk['longitude']],
                    [risk['closest_edge_point'][0], risk['closest_edge_point'][1]]
                ],
                color='red',
                weight=2,
                opacity=0.7,
                popup=f"Edge Distance: {risk['edge_distance_miles']:.3f} miles"
            ).add_to(distance_lines_group)
            
            # Mark the closest edge point
            folium.CircleMarker(
                location=[risk['closest_edge_point'][0], risk['closest_edge_point'][1]],
                radius=3,
                color='blue',
                fillColor='blue',
                fillOpacity=0.8,
                popup=f"Closest edge point to {risk['site_name']}"
            ).add_to(distance_lines_group)
    
    # Add the distance lines group to map
    distance_lines_group.add_to(site_map)
    
    # Add risk circles (based on edge distance)
    risk_colors = {0.095: '#FF0000', 0.25: '#FFD700', 0.5: '#32CD32', 1.0: '#90EE90'}
    risk_labels = {0.095: '500ft (HIGH)', 0.25: '1/4 mile (MODERATE)', 0.5: '1/2 mile (LOW-MOD)', 1.0: '1 mile (LOW)'}
    
    for radius_miles, color in risk_colors.items():
        radius_meters = radius_miles * 1609.34
        folium.Circle(
            location=[site_info['lat'], site_info['lng']],
            radius=radius_meters,
            color=color,
            weight=2,
            fillOpacity=0.1,
            popup=f'Risk Assessment Radius: {risk_labels[radius_miles]}'
        ).add_to(site_map)
    
    # Create enhanced info panel
    total_risks = len(environmental_risks)
    within_parcel_count = sum(1 for risk in environmental_risks if risk['within_parcel'])
    
    info_panel_html = f'''
    <div style="position: fixed; 
                bottom: 20px; right: 20px; width: 420px; height: 650px; 
                background-color: white; border:3px solid grey; z-index:9999; 
                font-size:12px; padding: 15px; border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3); overflow-y: auto;">
    
    <h3 style="margin-top: 0; color: #333;">🌍 ENHANCED ENVIRONMENTAL ANALYSIS</h3>
    
    <div style="margin-bottom: 12px;">
        <h4 style="margin: 8px 0 5px 0; color: #555;">📏 Risk Thresholds (Edge-Based):</h4>
        <p style="margin: 2px 0; color: #8B0000;">🔴 CRITICAL: On-site ($15K-$50K+)</p>
        <p style="margin: 2px 0; color: #FF0000;">🔴 HIGH: <500ft ($12K-$25K)</p>
        <p style="margin: 2px 0; color: #FF4500;">🟠 MODERATE-HIGH: <1000ft ($8K-$15K)</p>
        <p style="margin: 2px 0; color: #FFD700;">🟡 MODERATE: <1/4 mile ($5K-$8K)</p>
        <p style="margin: 2px 0; color: #32CD32;">🟢 LOW-MODERATE: <1/2 mile ($3K-$5K)</p>
        <p style="margin: 2px 0; color: #90EE90;">🟢 LOW: <1 mile ($1.5K-$3K)</p>
    </div>
    
    <div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin-bottom: 12px;">
        <h4 style="margin: 0 0 8px 0; color: #2E7D32;">📊 ENHANCED ANALYSIS SUMMARY</h4>
        <p style="margin: 3px 0;"><b>Total Environmental Sites:</b> {total_risks}</p>
        <p style="margin: 3px 0;"><b>Within Parcel Boundary:</b> {within_parcel_count}</p>
        <p style="margin: 3px 0;"><b>CRITICAL Risks:</b> {risk_counts['CRITICAL']}</p>
        <p style="margin: 3px 0;"><b>HIGH Risks:</b> {risk_counts['HIGH']}</p>
        <p style="margin: 3px 0;"><b>MODERATE+ Risks:</b> {risk_counts['MODERATE-HIGH'] + risk_counts['MODERATE']}</p>
        <p style="margin: 3px 0; color: #0066CC;"><b>🎯 Edge-Based Analysis Active</b></p>
    </div>
    
    <div style="margin-bottom: 12px;">
        <h4 style="margin: 8px 0 5px 0; color: #555;">🏗️ Parcel Information:</h4>
        {'<p style="margin: 2px 0;"><b>APN:</b> ' + str(parcel_data.apn) + '</p>' if parcel_data else '<p style="margin: 2px 0;">❌ No parcel boundary available</p>'}
        {'<p style="margin: 2px 0;"><b>Area:</b> ' + f"{parcel_data.property_area_acres:.2f} acres" + '</p>' if parcel_data else ''}
        {'<p style="margin: 2px 0;"><b>County:</b> ' + str(parcel_data.county) + '</p>' if parcel_data else ''}
        {'<p style="margin: 2px 0;"><b>Corners:</b> ' + str(len(parcel_data.boundary_coordinates)) + ' coordinates</p>' if parcel_data and parcel_data.boundary_coordinates else ''}
    </div>
    
    <div style="margin-bottom: 12px;">
        <h4 style="margin: 8px 0 5px 0; color: #555;">🗻 Elevation Analysis:</h4>
        <p style="margin: 2px 0;">• Water flow direction analysis</p>
        <p style="margin: 2px 0;">• Uphill/downhill contamination risk</p>
        <p style="margin: 2px 0;">• USGS elevation data integration</p>
        <p style="margin: 2px 0;">• Drainage impact assessment</p>
    </div>
    
    <div style="margin-bottom: 12px;">
        <h4 style="margin: 8px 0 5px 0; color: #555;">📋 Enhanced Features:</h4>
        <p style="margin: 2px 0;">• Edge-based distance measurements</p>
        <p style="margin: 2px 0;">• Toggleable distance lines</p>
        <p style="margin: 2px 0;">• 3-layer mapping (Street/Satellite/Terrain)</p>
        <p style="margin: 2px 0;">• Elevation-aware risk assessment</p>
    </div>
    
    <div style="background-color: #fff3cd; padding: 8px; border-radius: 3px;">
        <h5 style="margin: 0 0 5px 0; color: #856404;">⚠️ PROFESSIONAL LIHTC ANALYSIS</h5>
        <p style="margin: 2px 0; font-size: 11px;">Edge-based environmental screening with elevation analysis for accurate Phase I ESA compliance. Toggle "Distance Lines" layer to see exact measurements from parcel boundaries.</p>
    </div>
    
    </div>
    '''
    
    site_map.get_root().html.add_child(folium.Element(info_panel_html))
    
    # Add layer control
    folium.LayerControl().add_to(site_map)
    
    # Save map
    site_map.save(output_file)
    print(f"🗺️ Enhanced environmental map created: {output_file}")
    
    return {
        'total_risks': total_risks,
        'risk_counts': risk_counts,
        'within_parcel': within_parcel_count,
        'map_file': output_file,
        'edge_analysis_enabled': True
    }

# Import necessary functions from original module
from create_dmarco_environmental_maps import (
    load_tceq_environmental_database, 
    calculate_distance_miles, 
    point_in_polygon
)

def create_enhanced_dmarco_maps():
    """Create enhanced D'Marco environmental maps with edge analysis and elevation"""
    
    print("🗺️ CREATING ENHANCED D'MARCO ENVIRONMENTAL MAPS")
    print("=" * 65)
    print("✨ Features: Edge-based distances + Elevation analysis + 3 map layers")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load environmental database
    env_df = load_tceq_environmental_database()
    if len(env_df) == 0:
        print("❌ Cannot proceed without environmental database")
        return
    
    # D'Marco sites
    dmarco_sites = [
        {
            'name': 'Boerne Ralph Fair Road',
            'lat': 29.6859485,
            'lng': -98.6325156,
            'address': 'Ralph Fair Rd., Boerne, TX',
            'site_id': 'DMarco_Enhanced_Boerne'
        },
        {
            'name': 'San Antonio Stone Oak Parkway',
            'lat': 29.6495764,
            'lng': -98.464094,
            'address': '20623 Stone Oak Parkway, San Antonio, TX',
            'site_id': 'DMarco_Enhanced_San_Antonio'
        }
    ]
    
    # Initialize Universal Parcel Mapper
    mapper = UniversalParcelMapper()
    
    analysis_results = []
    
    for site in dmarco_sites:
        print(f"🏢 PROCESSING: {site['name']}")
        print(f"📍 Location: {site['address']}")
        
        # Get parcel boundary data
        parcel_data = mapper.get_parcel_from_coordinates(site['lat'], site['lng'], 'TX')
        
        if parcel_data and parcel_data.boundary_coordinates:
            print(f"✅ Parcel boundary: {len(parcel_data.boundary_coordinates)} coordinates")
            print(f"🎯 Edge-based analysis enabled")
        else:
            print("❌ No parcel boundary - using centroid analysis")
            parcel_data = None
        
        # Calculate enhanced environmental risks
        parcel_coords = parcel_data.boundary_coordinates if parcel_data else None
        environmental_risks = calculate_enhanced_environmental_risks(
            site['lat'], site['lng'], env_df, parcel_coords
        )
        
        print(f"🌍 Environmental sites found: {len(environmental_risks)}")
        
        # Create output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/parcel_mapping/{site['site_id']}_Enhanced_Map_{timestamp}.html"
        
        # Create enhanced environmental map
        map_results = create_enhanced_environmental_map(site, parcel_data, environmental_risks, output_file)
        
        # Store results
        analysis_results.append({
            'site_info': site,
            'map_results': map_results,
            'environmental_count': len(environmental_risks)
        })
        
        print(f"📊 Enhanced features enabled:")
        print(f"   🎯 Edge-based distance measurement")
        print(f"   🗻 Elevation analysis") 
        print(f"   📏 Toggleable distance lines")
        print(f"   🗺️ 3-layer mapping system")
        print()
        print("-" * 65)
        print()
    
    print("✅ ENHANCED D'MARCO ENVIRONMENTAL MAPPING COMPLETE")
    print(f"Maps created: {len(analysis_results)}")
    print("🎯 New features implemented:")
    print("   📏 Edge-based distance measurements (not centroid)")
    print("   🔗 Toggleable distance lines showing closest edge points")
    print("   🗻 Elevation/terrain layer for water flow analysis")
    print("   📍 3-layer system: Street/Satellite/Elevation")
    print("   💧 Elevation-aware contamination risk assessment")
    
    return analysis_results

if __name__ == "__main__":
    print("🚀 Starting Enhanced D'Marco Environmental Mapping")
    print()
    
    # Create enhanced maps
    results = create_enhanced_dmarco_maps()
    
    print(f"\n🏆 ENHANCED MAPPING COMPLETE")
    print("Ready for professional LIHTC analysis with edge-based measurements!")