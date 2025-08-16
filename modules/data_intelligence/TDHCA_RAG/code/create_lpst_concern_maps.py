#!/usr/bin/env python3

import pandas as pd
import json
from pathlib import Path
import folium
from folium import plugins
import requests
from datetime import datetime

class LPSTConcernMapper:
    """
    Create detailed interactive maps for D'Marco sites with LPST concerns
    Shows exact parcel boundaries and LPST sites with comprehensive popups
    """
    
    def __init__(self):
        self.output_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/"
        
        # Load the precise analysis results
        self.results_file = self.output_dir + "Precise_LPST_Analysis_Results.json"
        self.database_file = self.output_dir + "D_Marco_LPST_Sites_Database.csv"
        
        # Sites with LPST concerns
        self.concern_sites = {
            'dmarco_site_06': {
                'address': 'N JJ Lemon Street Hutchins',
                'risk_level': 'MEDIUM',
                'concern': '1 LPST site within 1/2 mile'
            },
            'dmarco_site_07': {
                'address': '6053 Bellfort Ave, Houston, TX 77033', 
                'risk_level': 'LOW',
                'concern': '1 LPST site within 1 mile'
            }
        }
        
        # Risk level styling
        self.risk_colors = {
            'IMMEDIATE': '#8B0000',    # Dark red
            'CRITICAL': '#FF0000',     # Red
            'HIGH': '#FF4500',         # Orange red
            'MEDIUM': '#FFA500',       # Orange
            'LOW': '#32CD32'           # Lime green
        }
    
    def load_site_data(self):
        """Load D'Marco site coordinates and LPST analysis results"""
        
        # Load priority sites for coordinates
        sites_file = "/Users/williamrice/priority_sites_data.json"
        with open(sites_file, 'r') as f:
            sites_data = json.load(f)
        
        # Load analysis results
        with open(self.results_file, 'r') as f:
            analysis_results = json.load(f)
        
        # Load LPST database
        lpst_df = pd.read_csv(self.database_file)
        
        return sites_data, analysis_results, lpst_df
    
    def parse_coordinates(self, coord_string):
        """Parse coordinate string like '32.319481, -95.330743' into lat, lon"""
        try:
            if isinstance(coord_string, str) and ',' in coord_string:
                lat_str, lon_str = coord_string.split(',')
                lat = float(lat_str.strip())
                lon = float(lon_str.strip())
                return lat, lon
            return None, None
        except:
            return None, None
    
    def get_site_coordinates(self, sites_data, site_index):
        """Extract coordinates for a specific site"""
        site = sites_data[site_index]
        
        corners = {}
        for corner_name in ['SW', 'SE', 'NE', 'NW']:
            lat, lon = self.parse_coordinates(site.get(corner_name))
            if lat and lon:
                corners[corner_name] = {'lat': lat, 'lon': lon}
        
        # Calculate center
        if len(corners) == 4:
            center_lat = sum(corner['lat'] for corner in corners.values()) / 4
            center_lon = sum(corner['lon'] for corner in corners.values()) / 4
            
            return {
                'corners': corners,
                'center': {'lat': center_lat, 'lon': center_lon},
                'address': site.get('Address', ''),
                'size_acres': site.get('Size (Acres)', 0)
            }
        
        return None
    
    def get_lpst_sites_for_site(self, lpst_df, site_id):
        """Get LPST sites that are within risk thresholds for a specific D'Marco site"""
        
        lpst_sites = []
        
        # Column names for this site
        distance_col = f'{site_id}_Min_Distance_Miles'
        within_500ft_col = f'{site_id}_Within_500ft'
        within_quarter_mile_col = f'{site_id}_Within_Quarter_Mile'
        within_half_mile_col = f'{site_id}_Within_Half_Mile'
        within_one_mile_col = f'{site_id}_Within_One_Mile'
        
        # Filter for sites within 1 mile
        if within_one_mile_col in lpst_df.columns:
            nearby_sites = lpst_df[lpst_df[within_one_mile_col] == 'YES'].copy()
            
            for idx, row in nearby_sites.iterrows():
                try:
                    # Determine risk level based on distance
                    risk_level = 'LOW'
                    if row.get(within_500ft_col) == 'YES':
                        risk_level = 'IMMEDIATE'
                    elif row.get(within_quarter_mile_col) == 'YES':
                        risk_level = 'CRITICAL'
                    elif row.get(within_half_mile_col) == 'YES':
                        risk_level = 'HIGH'
                    elif row.get(within_one_mile_col) == 'YES':
                        risk_level = 'MEDIUM'
                    
                    lpst_site = {
                        'lpst_id': str(row.get('LPST_ID', 'Unknown')),
                        'site_name': str(row.get('Site_Name', 'Unknown')),
                        'address': str(row.get('Address', 'Unknown')),
                        'city': str(row.get('City', 'Unknown')),
                        'reported_date': str(row.get('Reported_Date', 'N/A')),
                        'tceq_region': str(row.get('TCEQ_Region', 'Unknown')),
                        'latitude': float(row.get('Latitude', 0)),
                        'longitude': float(row.get('Longitude', 0)),
                        'confidence': str(row.get('Geocoding_Confidence', 'N/A')),
                        'distance_miles': float(row.get(distance_col, 0)),
                        'distance_feet': int(float(row.get(distance_col, 0)) * 5280),
                        'risk_level': risk_level,
                        'within_500ft': row.get(within_500ft_col) == 'YES',
                        'within_quarter_mile': row.get(within_quarter_mile_col) == 'YES',
                        'within_half_mile': row.get(within_half_mile_col) == 'YES',
                        'within_one_mile': row.get(within_one_mile_col) == 'YES'
                    }
                    
                    lpst_sites.append(lpst_site)
                    
                except Exception as e:
                    continue
        
        # Sort by distance (closest first)
        lpst_sites.sort(key=lambda x: x['distance_miles'])
        
        return lpst_sites
    
    def create_site_map(self, site_data, lpst_sites, site_id, site_info):
        """Create detailed map for a single site"""
        
        # Initialize map centered on site
        center_lat = site_data['center']['lat']
        center_lon = site_data['center']['lon']
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=15,
            tiles='OpenStreetMap'
        )
        
        # Add satellite imagery option
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Add terrain layer option
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Terrain',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Create property parcel polygon from 4 corners
        parcel_coords = []
        corner_order = ['SW', 'SE', 'NE', 'NW', 'SW']  # Close the polygon
        
        for corner_name in corner_order:
            if corner_name in site_data['corners']:
                corner = site_data['corners'][corner_name]
                parcel_coords.append([corner['lat'], corner['lon']])
        
        # Add property parcel
        if len(parcel_coords) >= 5:  # Should have 5 points (closing point)
            parcel_popup = f"""
            <div style="width: 350px; font-family: Arial, sans-serif;">
                <h3 style="color: #2E8B57; margin-bottom: 10px;">
                    🏠 D'MARCO DEVELOPMENT SITE
                </h3>
                
                <div style="background-color: #f0f8f0; padding: 12px; border-radius: 5px; margin-bottom: 10px;">
                    <b>📍 Address:</b> {site_data['address']}<br>
                    <b>📏 Size:</b> {site_data['size_acres']} acres<br>
                    <b>🆔 Site ID:</b> {site_id.upper()}<br>
                </div>
                
                <div style="background-color: {'#ffe0e0' if site_info['risk_level'] in ['HIGH', 'CRITICAL'] else '#fff8e1' if site_info['risk_level'] == 'MEDIUM' else '#e8f5e8'}; 
                           padding: 12px; border-radius: 5px; border-left: 4px solid {self.risk_colors[site_info['risk_level']]};">
                    <h4 style="color: {self.risk_colors[site_info['risk_level']]}; margin: 0 0 8px 0;">
                        🛢️ PETROLEUM CONTAMINATION RISK: {site_info['risk_level']}
                    </h4>
                    <b>Environmental Concern:</b> {site_info['concern']}<br>
                    <b>LPST Sites Found:</b> {len(lpst_sites)} within 1 mile<br>
                </div>
                
                <div style="margin-top: 12px; padding: 10px; background-color: #e3f2fd; border-radius: 5px;">
                    <b>📋 Recommended Action:</b><br>
                    {'• Phase I Environmental Site Assessment recommended<br>• Budget: $3,000-$5,000' if site_info['risk_level'] in ['MEDIUM', 'HIGH'] else '• Standard environmental due diligence sufficient<br>• Minimal additional environmental costs'}
                </div>
                
                <div style="margin-top: 10px; font-size: 11px; color: #666;">
                    <b>Parcel Coordinates:</b><br>
                    SW: {site_data['corners']['SW']['lat']:.5f}, {site_data['corners']['SW']['lon']:.5f}<br>
                    NE: {site_data['corners']['NE']['lat']:.5f}, {site_data['corners']['NE']['lon']:.5f}
                </div>
            </div>
            """
            
            folium.Polygon(
                locations=parcel_coords,
                color=self.risk_colors[site_info['risk_level']],
                weight=3,
                fillColor=self.risk_colors[site_info['risk_level']],
                fillOpacity=0.2,
                popup=folium.Popup(parcel_popup, max_width=400)
            ).add_to(m)
        
        # Add site center marker with housing icon
        site_center_popup = f"""
        <div style="width: 300px; font-family: Arial, sans-serif;">
            <h3 style="color: #2E8B57;">🏠 {site_data['address']}</h3>
            <p><b>Site ID:</b> {site_id.upper()}</p>
            <p><b>Size:</b> {site_data['size_acres']} acres</p>
            <p><b>LPST Risk Level:</b> <span style="color: {self.risk_colors[site_info['risk_level']]}"><b>{site_info['risk_level']}</b></span></p>
            <p><b>Environmental Issues:</b> {len(lpst_sites)} LPST sites within 1 mile</p>
        </div>
        """
        
        folium.Marker(
            [center_lat, center_lon],
            popup=folium.Popup(site_center_popup, max_width=350),
            icon=folium.Icon(color='green', icon='home', prefix='fa'),
            tooltip=f"D'Marco Site: {site_data['address']}"
        ).add_to(m)
        
        # Add LPST sites
        for lpst_site in lpst_sites:
            
            # Determine marker color and icon based on risk level
            lpst_color_map = {
                'IMMEDIATE': 'darkred',
                'CRITICAL': 'red',
                'HIGH': 'orange', 
                'MEDIUM': 'yellow',
                'LOW': 'lightgreen'
            }
            
            lpst_color = lpst_color_map.get(lpst_site['risk_level'], 'gray')
            
            # Create comprehensive LPST popup
            lpst_popup = f"""
            <div style="width: 400px; font-family: Arial, sans-serif;">
                <h3 style="color: #d32f2f; margin-bottom: 10px;">
                    🛢️ ACTIVE PETROLEUM CONTAMINATION SITE
                </h3>
                
                <div style="background-color: #ffebee; padding: 12px; border-radius: 5px; margin-bottom: 10px;">
                    <h4 style="margin: 0 0 8px 0; color: #d32f2f;">{lpst_site['site_name']}</h4>
                    <b>📍 Address:</b> {lpst_site['address']}<br>
                    <b>🏙️ City:</b> {lpst_site['city']}<br>
                    <b>🆔 LPST ID:</b> {lpst_site['lpst_id']}<br>
                </div>
                
                <div style="background-color: {'#ffcdd2' if lpst_site['risk_level'] in ['IMMEDIATE', 'CRITICAL'] else '#ffe0b2' if lpst_site['risk_level'] == 'HIGH' else '#fff9c4' if lpst_site['risk_level'] == 'MEDIUM' else '#dcedc8'}; 
                           padding: 12px; border-radius: 5px; border-left: 4px solid {self.risk_colors[lpst_site['risk_level']]};">
                    <h4 style="color: {self.risk_colors[lpst_site['risk_level']]}; margin: 0 0 8px 0;">
                        ⚠️ PROXIMITY RISK: {lpst_site['risk_level']}
                    </h4>
                    <b>Distance to D'Marco Site:</b> {lpst_site['distance_miles']:.3f} miles ({lpst_site['distance_feet']:,} feet)<br>
                    <b>Within Critical Distances:</b><br>
                    {'✅ Within 500 feet (IMMEDIATE RISK)' if lpst_site['within_500ft'] else '❌ Not within 500 feet'}<br>
                    {'✅ Within 1/4 mile (CRITICAL RISK)' if lpst_site['within_quarter_mile'] else '❌ Not within 1/4 mile'}<br>
                    {'✅ Within 1/2 mile (HIGH RISK)' if lpst_site['within_half_mile'] else '❌ Not within 1/2 mile'}<br>
                    {'✅ Within 1 mile (MEDIUM RISK)' if lpst_site['within_one_mile'] else '❌ Not within 1 mile'}
                </div>
                
                <div style="background-color: #f3e5f5; padding: 12px; margin-top: 10px; border-radius: 5px;">
                    <h4 style="color: #7B1FA2; margin: 0 0 8px 0;">📋 REGULATORY INFORMATION</h4>
                    <b>Reported Date:</b> {lpst_site['reported_date']}<br>
                    <b>TCEQ Region:</b> {lpst_site['tceq_region']}<br>
                    <b>Current Status:</b> <span style="color: red;"><b>ACTIVE (NOT CLOSED)</b></span><br>
                    <b>Geocoding Confidence:</b> {lpst_site['confidence']}<br>
                </div>
                
                <div style="background-color: #e1f5fe; padding: 12px; margin-top: 10px; border-radius: 5px;">
                    <h4 style="color: #0277BD; margin: 0 0 8px 0;">🏗️ DEVELOPMENT IMPLICATIONS</h4>
                    <b>Environmental Concern:</b> Petroleum contamination in soil/groundwater<br>
                    <b>Potential Issues:</b> Vapor intrusion, soil contamination, groundwater impact<br>
                    <b>Due Diligence Required:</b> {'Phase I ESA with vapor assessment' if lpst_site['risk_level'] in ['IMMEDIATE', 'CRITICAL'] else 'Standard Phase I ESA recommended' if lpst_site['risk_level'] in ['HIGH', 'MEDIUM'] else 'Standard due diligence sufficient'}<br>
                </div>
                
                <div style="margin-top: 10px; font-size: 11px; color: #666;">
                    <b>Coordinates:</b> {lpst_site['latitude']:.5f}, {lpst_site['longitude']:.5f}<br>
                    <b>Data Source:</b> Texas Commission on Environmental Quality (TCEQ)
                </div>
            </div>
            """
            
            # Add LPST marker
            folium.Marker(
                [lpst_site['latitude'], lpst_site['longitude']],
                popup=folium.Popup(lpst_popup, max_width=450),
                icon=folium.Icon(color=lpst_color, icon='exclamation-triangle', prefix='fa'),
                tooltip=f"LPST: {lpst_site['site_name']} ({lpst_site['distance_miles']:.3f} mi)"
            ).add_to(m)
            
            # Add distance line
            folium.PolyLine(
                locations=[[center_lat, center_lon], [lpst_site['latitude'], lpst_site['longitude']]],
                color=self.risk_colors[lpst_site['risk_level']],
                weight=2,
                opacity=0.7,
                popup=f"Distance: {lpst_site['distance_miles']:.3f} miles"
            ).add_to(m)
        
        # Add risk buffer circles
        risk_circles = [
            {'radius': 500 * 0.3048, 'color': '#8B0000', 'label': '500 feet (IMMEDIATE)', 'opacity': 0.3},
            {'radius': 0.25 * 1609.34, 'color': '#FF0000', 'label': '1/4 mile (CRITICAL)', 'opacity': 0.2},
            {'radius': 0.5 * 1609.34, 'color': '#FFA500', 'label': '1/2 mile (HIGH)', 'opacity': 0.15},
            {'radius': 1.0 * 1609.34, 'color': '#32CD32', 'label': '1 mile (MEDIUM)', 'opacity': 0.1}
        ]
        
        for circle in risk_circles:
            folium.Circle(
                [center_lat, center_lon],
                radius=circle['radius'],
                color=circle['color'],
                weight=2,
                fillOpacity=circle['opacity'],
                popup=f"Environmental screening buffer: {circle['label']}",
                tooltip=circle['label']
            ).add_to(m)
        
        # Add CSS to ensure popups appear above everything
        popup_fix_css = '''
        <style>
        .leaflet-popup {
            z-index: 999999 !important;
        }
        .leaflet-popup-pane {
            z-index: 999999 !important;
        }
        .leaflet-popup-content-wrapper {
            z-index: 999999 !important;
        }
        .leaflet-popup-content {
            z-index: 999999 !important;
        }
        .leaflet-popup-tip {
            z-index: 999999 !important;
        }
        .leaflet-tooltip {
            z-index: 1000000 !important;
        }
        </style>
        '''
        m.get_root().html.add_child(folium.Element(popup_fix_css))
        
        # Add comprehensive legend
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 20px; right: 20px; width: 280px; height: 420px; 
                    background-color: white; border:3px solid grey; z-index:9999; 
                    font-size:12px; padding: 15px; border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3); overflow-y: auto;">
        <h3 style="margin-top: 0; color: #333;">🛢️ ENVIRONMENTAL RISK LEGEND</h3>
        
        <div style="margin-bottom: 12px;">
            <h4 style="margin: 8px 0 5px 0; color: #555;">LPST Risk Levels:</h4>
            <p style="margin: 2px 0;"><i class="fa fa-exclamation-triangle" style="color:darkred"></i> 
               <b style="color:darkred">IMMEDIATE</b>: Within 500 feet</p>
            <p style="margin: 2px 0;"><i class="fa fa-exclamation-triangle" style="color:red"></i> 
               <b style="color:red">CRITICAL</b>: Within 1/4 mile</p>
            <p style="margin: 2px 0;"><i class="fa fa-exclamation-triangle" style="color:orange"></i> 
               <b style="color:orange">HIGH</b>: Within 1/2 mile</p>
            <p style="margin: 2px 0;"><i class="fa fa-exclamation-triangle" style="color:gold"></i> 
               <b style="color:gold">MEDIUM</b>: Within 1 mile</p>
            <p style="margin: 2px 0;"><i class="fa fa-exclamation-triangle" style="color:lightgreen"></i> 
               <b style="color:lightgreen">LOW</b>: Beyond 1 mile</p>
        </div>
        
        <div style="margin-bottom: 12px;">
            <h4 style="margin: 8px 0 5px 0; color: #555;">Map Elements:</h4>
            <p style="margin: 2px 0;"><i class="fa fa-home" style="color:green"></i> D'Marco Development Site</p>
            <p style="margin: 2px 0;">🔵 Property parcel boundary</p>
            <p style="margin: 2px 0;"><span style="color: red;">━━</span> Distance lines to LPST sites</p>
            <p style="margin: 2px 0;">○ Environmental screening buffers</p>
        </div>
        
        <div style="margin-bottom: 12px;">
            <h4 style="margin: 8px 0 5px 0; color: #555;">Site Summary:</h4>
            <p style="margin: 2px 0; font-size: 11px;"><b>Address:</b> {site_data['address'][:40]}{'...' if len(site_data['address']) > 40 else ''}</p>
            <p style="margin: 2px 0; font-size: 11px;"><b>Size:</b> {site_data['size_acres']} acres</p>
            <p style="margin: 2px 0; font-size: 11px;"><b>Risk Level:</b> <span style="color: {self.risk_colors[site_info['risk_level']]};"><b>{site_info['risk_level']}</b></span></p>
            <p style="margin: 2px 0; font-size: 11px;"><b>LPST Sites:</b> {len(lpst_sites)} within 1 mile</p>
        </div>
        
        <div style="border-top: 1px solid #ccc; padding-top: 8px;">
            <p style="margin: 2px 0; font-size: 10px; color: #666;"><b>LPST:</b> Leaking Petroleum Storage Tank</p>
            <p style="margin: 2px 0; font-size: 10px; color: #666;"><b>Source:</b> Texas Commission on Environmental Quality</p>
            <p style="margin: 2px 0; font-size: 10px; color: #666;"><b>Analysis:</b> Precise geocoding with OpenStreetMap</p>
            <p style="margin: 8px 0 2px 0; font-size: 10px; color: #888; text-align: center; font-style: italic;"><b>Analysis provided by Structured Consultants LLC</b></p>
        </div>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add title with company attribution
        title_html = f'''
        <div style="position: fixed; 
                    top: 20px; left: 50%; transform: translateX(-50%); 
                    background-color: rgba(255,255,255,0.95); 
                    padding: 15px 25px; border-radius: 10px; border: 2px solid #333;
                    z-index: 9999; text-align: center;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <h3 style="margin: 0 0 5px 0; color: #333; font-size: 18px;">🛢️ {site_id.upper()}: PETROLEUM CONTAMINATION ANALYSIS</h3>
            <p style="margin: 0 0 5px 0; color: #666; font-size: 14px;">
                {site_data['address']} • Risk Level: <span style="color: {self.risk_colors[site_info['risk_level']]}"><b>{site_info['risk_level']}</b></span>
            </p>
            <p style="margin: 0; color: #888; font-size: 12px; font-style: italic;">
                <b>Analysis provided by Structured Consultants LLC</b>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m
    
    def create_concern_maps(self):
        """Create detailed maps for both sites with LPST concerns"""
        
        print("🗺️ CREATING DETAILED LPST CONCERN MAPS")
        print("=" * 50)
        
        # Load data
        sites_data, analysis_results, lpst_df = self.load_site_data()
        
        maps_created = []
        
        for site_id, site_info in self.concern_sites.items():
            print(f"\n📍 Creating map for {site_id}: {site_info['address']}")
            
            # Get site index (site_id format: dmarco_site_06 -> index 5)
            site_index = int(site_id.split('_')[-1]) - 1
            
            # Get site coordinates
            site_data = self.get_site_coordinates(sites_data, site_index)
            
            if not site_data:
                print(f"   ❌ Could not get coordinates for {site_id}")
                continue
            
            # Get LPST sites for this site
            lpst_sites = self.get_lpst_sites_for_site(lpst_df, site_id)
            
            print(f"   📊 Found {len(lpst_sites)} LPST sites within 1 mile")
            
            # Create map
            site_map = self.create_site_map(site_data, lpst_sites, site_id, site_info)
            
            # Save map
            map_filename = self.output_dir + f"Environmental_Maps/{site_id}_LPST_Environmental_Concern_Map.html"
            Path(map_filename).parent.mkdir(parents=True, exist_ok=True)
            site_map.save(map_filename)
            
            maps_created.append({
                'site_id': site_id,
                'address': site_info['address'],
                'risk_level': site_info['risk_level'],
                'lpst_count': len(lpst_sites),
                'map_file': map_filename
            })
            
            print(f"   ✅ Map saved: {map_filename}")
            
            # Show LPST details
            if lpst_sites:
                print(f"   🔍 LPST Sites Found:")
                for lpst in lpst_sites[:3]:  # Show first 3
                    print(f"      • {lpst['site_name']} - {lpst['distance_miles']:.3f} miles ({lpst['risk_level']} risk)")
                if len(lpst_sites) > 3:
                    print(f"      ... and {len(lpst_sites) - 3} more")
        
        # Create summary report
        summary_file = self.output_dir + "LPST_Concern_Maps_Summary.json"
        
        summary_data = {
            'creation_date': datetime.now().isoformat(),
            'maps_created': len(maps_created),
            'sites_analyzed': maps_created,
            'total_lpst_sites_mapped': sum(map_info['lpst_count'] for map_info in maps_created),
            'analysis_summary': {
                'medium_risk_sites': len([m for m in maps_created if m['risk_level'] == 'MEDIUM']),
                'low_risk_sites': len([m for m in maps_created if m['risk_level'] == 'LOW']),
                'immediate_action_required': any(m['risk_level'] in ['IMMEDIATE', 'CRITICAL'] for m in maps_created)
            }
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        print(f"\n📋 SUMMARY:")
        print(f"   📊 Maps created: {len(maps_created)}")
        print(f"   🛢️ Total LPST sites mapped: {sum(map_info['lpst_count'] for map_info in maps_created)}")
        print(f"   📄 Summary saved: {summary_file}")
        
        return maps_created

def main():
    """Create detailed LPST concern maps"""
    
    print("🗺️ D'MARCO LPST ENVIRONMENTAL CONCERN MAPPING")
    print("=" * 55)
    
    mapper = LPSTConcernMapper()
    maps_created = mapper.create_concern_maps()
    
    if maps_created:
        print("\n🎉 LPST CONCERN MAPS COMPLETE!")
        print("✅ Detailed interactive maps created for sites with environmental concerns")
        print("✅ Comprehensive LPST data with risk analysis popups")
        print("✅ Precise parcel boundaries with 4-corner coordinates displayed")
        print("✅ Environmental screening buffers and risk levels visualized")
        
        print("\n📁 Map Files Created:")
        for map_info in maps_created:
            print(f"   • {map_info['site_id']}: {map_info['address']}")
            print(f"     Risk: {map_info['risk_level']}, LPST Sites: {map_info['lpst_count']}")
            print(f"     File: {map_info['map_file']}")
    
    else:
        print("\n❌ Map creation failed")

if __name__ == "__main__":
    main()