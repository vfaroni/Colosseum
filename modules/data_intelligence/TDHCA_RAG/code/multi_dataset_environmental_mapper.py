#!/usr/bin/env python3

import pandas as pd
import json
from pathlib import Path
import folium
from datetime import datetime
import numpy as np

class MultiDatasetEnvironmentalMapper:
    """
    Create comprehensive environmental maps showing all 3 TCEQ datasets:
    1. LPST (Petroleum Contamination) - 215 sites
    2. Operating Dry Cleaners (Active Solvent Operations) - 1,478 sites  
    3. Environmental Violations (Enforcement Notices) - 19,670 sites
    """
    
    def __init__(self):
        self.base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG"
        self.output_dir = f"{self.base_dir}/D'Marco_Sites/"
        
        # Load comprehensive environmental database
        self.env_database = f"{self.output_dir}Comprehensive_Environmental_Database.csv"
        self.risk_analysis = f"{self.output_dir}DMarco_Environmental_Risk_Analysis.json"
        
        # Dataset styling
        self.dataset_styles = {
            'lpst': {
                'color': '#8B0000',      # Dark red
                'icon': 'tint',
                'name': 'Petroleum Contamination (LPST)',
                'marker_color': 'darkred'
            },
            'operating_dry_cleaners': {
                'color': '#800080',      # Purple
                'icon': 'industry', 
                'name': 'Active Solvent Operations',
                'marker_color': 'purple'
            },
            'enforcement': {
                'color': '#DC143C',      # Crimson
                'icon': 'gavel',
                'name': 'Environmental Violations',
                'marker_color': 'red'
            }
        }
        
        # Risk level colors
        self.risk_colors = {
            'IMMEDIATE': '#8B0000',    # Dark red
            'CRITICAL': '#FF0000',     # Red
            'HIGH': '#FF4500',         # Orange red
            'MEDIUM': '#FFA500',       # Orange
            'LOW': '#32CD32',          # Lime green
            'NO RISK': '#90EE90'       # Light green
        }
        
        # Sites with significant environmental concerns (CRITICAL/HIGH risk)
        self.priority_sites = ['dmarco_site_02', 'dmarco_site_04', 'dmarco_site_05', 
                              'dmarco_site_06', 'dmarco_site_09', 'dmarco_site_10']
    
    def load_environmental_data(self):
        """Load comprehensive environmental database and risk analysis"""
        print("📊 Loading comprehensive environmental data...")
        
        # Load environmental sites
        env_df = pd.read_csv(self.env_database)
        print(f"   ✅ Loaded {len(env_df)} environmental sites")
        
        # Load risk analysis
        with open(self.risk_analysis, 'r') as f:
            risk_data = json.load(f)
        print(f"   ✅ Loaded risk analysis for {len(risk_data)} D'Marco sites")
        
        return env_df, risk_data
    
    def get_site_coordinates(self, site_index):
        """Get D'Marco site coordinates from priority sites data"""
        sites_file = "/Users/williamrice/priority_sites_data.json"
        with open(sites_file, 'r') as f:
            sites_data = json.load(f)
        
        site = sites_data[site_index]
        
        # Parse 4 corners
        corners = {}
        for corner_name in ['SW', 'SE', 'NE', 'NW']:
            coord_str = site.get(corner_name, "")
            if coord_str and ',' in coord_str:
                try:
                    lat_str, lon_str = coord_str.split(',')
                    lat, lon = float(lat_str.strip()), float(lon_str.strip())
                    corners[corner_name] = {'lat': lat, 'lon': lon}
                except:
                    continue
        
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
    
    def create_comprehensive_site_map(self, site_id, site_data, risk_data, env_df):
        """Create comprehensive map for a single D'Marco site with all environmental datasets"""
        print(f"🗺️ Creating comprehensive map for {site_id}...")
        
        site_risk = risk_data[site_id]
        center_lat = site_data['center']['lat']
        center_lon = site_data['center']['lon']
        
        # Initialize map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=14,
            tiles='OpenStreetMap'
        )
        
        # Add satellite and terrain layers
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite',
            overlay=False,
            control=True
        ).add_to(m)
        
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Terrain',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Add property parcel polygon
        parcel_coords = []
        corner_order = ['SW', 'SE', 'NE', 'NW', 'SW']
        
        for corner_name in corner_order:
            if corner_name in site_data['corners']:
                corner = site_data['corners'][corner_name]
                parcel_coords.append([corner['lat'], corner['lon']])
        
        if len(parcel_coords) >= 5:
            parcel_popup = f"""
            <div style="width: 400px; font-family: Arial, sans-serif;">
                <h3 style="color: #2E8B57; margin-bottom: 10px;">
                    🏠 D'MARCO DEVELOPMENT SITE
                </h3>
                
                <div style="background-color: #f0f8f0; padding: 12px; border-radius: 5px; margin-bottom: 10px;">
                    <b>📍 Address:</b> {site_data['address']}<br>
                    <b>📏 Size:</b> {site_data['size_acres']} acres<br>
                    <b>🆔 Site ID:</b> {site_id.upper()}<br>
                </div>
                
                <div style="background-color: {'#ffcdd2' if site_risk['overall_risk_level'] in ['CRITICAL', 'HIGH'] else '#fff8e1' if site_risk['overall_risk_level'] == 'MEDIUM' else '#e8f5e8'}; 
                           padding: 12px; border-radius: 5px; border-left: 4px solid {self.risk_colors[site_risk['overall_risk_level']]};">
                    <h4 style="color: {self.risk_colors[site_risk['overall_risk_level']]}; margin: 0 0 8px 0;">
                        🌍 COMPREHENSIVE ENVIRONMENTAL RISK: {site_risk['overall_risk_level']}
                    </h4>
                    <b>Total Environmental Sites:</b> {site_risk['total_environmental_sites']} within 1 mile<br>
                    <b>Environmental Concern Types:</b> {site_risk['environmental_concerns']}<br>
                    <b>Risk Categories Found:</b><br>
                    {''.join([f"• {risk_type}: {len(risks)} sites<br>" for risk_type, risks in site_risk['risks_by_type'].items()])}
                </div>
                
                <div style="margin-top: 12px; padding: 10px; background-color: #e3f2fd; border-radius: 5px;">
                    <b>📋 Due Diligence Required:</b><br>
                    {'• Phase I ESA with vapor assessment<br>• Enhanced subsurface investigation<br>• Budget: $8,000-$15,000' if site_risk['overall_risk_level'] in ['CRITICAL', 'HIGH'] else '• Standard Phase I ESA<br>• Budget: $3,000-$5,000' if site_risk['overall_risk_level'] == 'MEDIUM' else '• Standard environmental due diligence<br>• Budget: $1,500-$3,000'}
                </div>
            </div>
            """
            
            folium.Polygon(
                locations=parcel_coords,
                color=self.risk_colors[site_risk['overall_risk_level']],
                weight=4,
                fillColor=self.risk_colors[site_risk['overall_risk_level']],
                fillOpacity=0.3,
                popup=folium.Popup(parcel_popup, max_width=450)
            ).add_to(m)
        
        # Add D'Marco site center marker
        folium.Marker(
            [center_lat, center_lon],
            icon=folium.Icon(color='green', icon='home', prefix='fa'),
            tooltip=f"D'Marco Site: {site_data['address']}"
        ).add_to(m)
        
        # Add environmental sites within 1 mile for each dataset
        for dataset in ['lpst', 'operating_dry_cleaners', 'enforcement']:
            dataset_sites = env_df[
                (env_df['dataset'] == dataset) & 
                (env_df[f'{site_id}_within_1_mile'] == True)
            ]
            
            print(f"   📊 Adding {len(dataset_sites)} {dataset} sites")
            
            # Create feature group for this dataset
            feature_group = folium.FeatureGroup(name=self.dataset_styles[dataset]['name'])
            
            for idx, env_site in dataset_sites.iterrows():
                # Create comprehensive popup
                popup_html = f"""
                <div style="width: 450px; font-family: Arial, sans-serif;">
                    <h3 style="color: {self.dataset_styles[dataset]['color']}; margin-bottom: 10px;">
                        🏭 {env_site['risk_type'].upper()}
                    </h3>
                    
                    <div style="background-color: #ffebee; padding: 12px; border-radius: 5px; margin-bottom: 10px;">
                        <h4 style="margin: 0 0 8px 0; color: #d32f2f;">{env_site['site_name']}</h4>
                        <b>📍 Address:</b> {env_site['address']}<br>
                        <b>🏙️ City:</b> {env_site['city']}<br>
                        <b>🆔 Site ID:</b> {env_site['site_id']}<br>
                        <b>📊 Dataset:</b> {dataset.replace('_', ' ').title()}<br>
                    </div>
                    
                    <div style="background-color: {'#ffcdd2' if env_site[f'{site_id}_risk_level'] in ['IMMEDIATE', 'CRITICAL'] else '#ffe0b2' if env_site[f'{site_id}_risk_level'] == 'HIGH' else '#fff9c4' if env_site[f'{site_id}_risk_level'] == 'MEDIUM' else '#dcedc8'}; 
                               padding: 12px; border-radius: 5px; border-left: 4px solid {self.risk_colors[env_site[f'{site_id}_risk_level']]};">
                        <h4 style="color: {self.risk_colors[env_site[f'{site_id}_risk_level']]}; margin: 0 0 8px 0;">
                            ⚠️ PROXIMITY RISK: {env_site[f'{site_id}_risk_level']}
                        </h4>
                        <b>Distance to D'Marco Site:</b> {env_site[f'{site_id}_distance_miles']:.3f} miles<br>
                        <b>Environmental Concern:</b> {env_site['risk_type']}<br>
                        <b>Status:</b> {env_site['status']}<br>
                    </div>
                    
                    <div style="background-color: #f3e5f5; padding: 12px; margin-top: 10px; border-radius: 5px;">
                        <h4 style="color: #7B1FA2; margin: 0 0 8px 0;">📋 REGULATORY INFORMATION</h4>
                        <b>TCEQ Region:</b> {env_site.get('tceq_region', 'Unknown')}<br>
                        <b>Geocoding Confidence:</b> {env_site['geocoding_confidence']:.2f}<br>
                        <b>Data Source:</b> Texas Commission on Environmental Quality
                    </div>
                </div>
                """
                
                # Add environmental site marker
                folium.Marker(
                    [env_site['latitude'], env_site['longitude']],
                    popup=folium.Popup(popup_html, max_width=500),
                    icon=folium.Icon(
                        color=self.dataset_styles[dataset]['marker_color'], 
                        icon=self.dataset_styles[dataset]['icon'], 
                        prefix='fa'
                    ),
                    tooltip=f"{env_site['site_name']} ({env_site[f'{site_id}_distance_miles']:.3f} mi)"
                ).add_to(feature_group)
                
                # Add distance line
                folium.PolyLine(
                    locations=[[center_lat, center_lon], [env_site['latitude'], env_site['longitude']]],
                    color=self.dataset_styles[dataset]['color'],
                    weight=2,
                    opacity=0.6,
                    popup=f"Distance: {env_site[f'{site_id}_distance_miles']:.3f} miles"
                ).add_to(feature_group)
            
            # Add feature group to map
            feature_group.add_to(m)
        
        # Add risk buffer circles
        risk_circles = [
            {'radius': 500 * 0.3048, 'color': '#8B0000', 'label': '500 feet (IMMEDIATE)', 'opacity': 0.15},
            {'radius': 0.25 * 1609.34, 'color': '#FF0000', 'label': '1/4 mile (CRITICAL)', 'opacity': 0.1},
            {'radius': 0.5 * 1609.34, 'color': '#FFA500', 'label': '1/2 mile (HIGH)', 'opacity': 0.08},
            {'radius': 1.0 * 1609.34, 'color': '#32CD32', 'label': '1 mile (MEDIUM)', 'opacity': 0.05}
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
        
        # Add comprehensive legend
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 20px; right: 20px; width: 320px; height: 500px; 
                    background-color: white; border:3px solid grey; z-index:9999; 
                    font-size:12px; padding: 15px; border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3); overflow-y: auto;">
        <h3 style="margin-top: 0; color: #333;">🌍 MULTI-DATASET ENVIRONMENTAL LEGEND</h3>
        
        <div style="margin-bottom: 12px;">
            <h4 style="margin: 8px 0 5px 0; color: #555;">Environmental Datasets:</h4>
            <p style="margin: 2px 0;"><i class="fa fa-tint" style="color:#8B0000"></i> 
               <b style="color:#8B0000">LPST</b>: Petroleum contamination ({len(env_df[env_df['dataset'] == 'lpst'])} sites)</p>
            <p style="margin: 2px 0;"><i class="fa fa-industry" style="color:#800080"></i> 
               <b style="color:#800080">Dry Cleaners</b>: Active solvent operations ({len(env_df[env_df['dataset'] == 'operating_dry_cleaners'])} sites)</p>
            <p style="margin: 2px 0;"><i class="fa fa-gavel" style="color:#DC143C"></i> 
               <b style="color:#DC143C">Violations</b>: Environmental enforcement ({len(env_df[env_df['dataset'] == 'enforcement'])} sites)</p>
        </div>
        
        <div style="margin-bottom: 12px;">
            <h4 style="margin: 8px 0 5px 0; color: #555;">Risk Levels:</h4>
            <p style="margin: 2px 0;"><span style="color:#8B0000">●</span> <b>IMMEDIATE</b>: Within 500 feet</p>
            <p style="margin: 2px 0;"><span style="color:#FF0000">●</span> <b>CRITICAL</b>: Within 1/4 mile</p>
            <p style="margin: 2px 0;"><span style="color:#FFA500">●</span> <b>HIGH</b>: Within 1/2 mile</p>
            <p style="margin: 2px 0;"><span style="color:#32CD32">●</span> <b>MEDIUM</b>: Within 1 mile</p>
        </div>
        
        <div style="margin-bottom: 12px;">
            <h4 style="margin: 8px 0 5px 0; color: #555;">Site Summary:</h4>
            <p style="margin: 2px 0; font-size: 11px;"><b>Address:</b> {site_data['address'][:35]}{'...' if len(site_data['address']) > 35 else ''}</p>
            <p style="margin: 2px 0; font-size: 11px;"><b>Size:</b> {site_data['size_acres']} acres</p>
            <p style="margin: 2px 0; font-size: 11px;"><b>Overall Risk:</b> <span style="color: {self.risk_colors[site_risk['overall_risk_level']]}"><b>{site_risk['overall_risk_level']}</b></span></p>
            <p style="margin: 2px 0; font-size: 11px;"><b>Environmental Sites:</b> {site_risk['total_environmental_sites']} within 1 mile</p>
            <p style="margin: 2px 0; font-size: 11px;"><b>Concern Types:</b> {site_risk['environmental_concerns']}</p>
        </div>
        
        <div style="border-top: 1px solid #ccc; padding-top: 8px;">
            <p style="margin: 2px 0; font-size: 10px; color: #666;"><b>Analysis:</b> 3-dataset comprehensive screening</p>
            <p style="margin: 2px 0; font-size: 10px; color: #666;"><b>Total Sites:</b> 21,363 environmental locations</p>
            <p style="margin: 8px 0 2px 0; font-size: 10px; color: #888; text-align: center; font-style: italic;"><b>Analysis by Structured Consultants LLC</b></p>
        </div>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add title with comprehensive info
        title_html = f'''
        <div style="position: fixed; 
                    top: 20px; left: 50%; transform: translateX(-50%); 
                    background-color: rgba(255,255,255,0.95); 
                    padding: 15px 25px; border-radius: 10px; border: 2px solid #333;
                    z-index: 9999; text-align: center;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <h3 style="margin: 0 0 5px 0; color: #333; font-size: 16px;">🌍 {site_id.upper()}: COMPREHENSIVE ENVIRONMENTAL ANALYSIS</h3>
            <p style="margin: 0 0 5px 0; color: #666; font-size: 14px;">
                {site_data['address']} • Risk Level: <span style="color: {self.risk_colors[site_risk['overall_risk_level']]}"><b>{site_risk['overall_risk_level']}</b></span>
            </p>
            <p style="margin: 0 0 5px 0; color: #555; font-size: 12px;">
                3 Datasets • {site_risk['total_environmental_sites']} Environmental Sites • {site_risk['environmental_concerns']} Concern Types
            </p>
            <p style="margin: 0; color: #888; font-size: 11px; font-style: italic;">
                <b>Analysis provided by Structured Consultants LLC</b>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add popup z-index fix
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
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m
    
    def create_all_priority_site_maps(self):
        """Create comprehensive environmental maps for all priority sites"""
        print("🗺️ CREATING COMPREHENSIVE MULTI-DATASET ENVIRONMENTAL MAPS")
        print("=" * 70)
        
        # Load data
        env_df, risk_data = self.load_environmental_data()
        
        # Load D'Marco site coordinates
        sites_file = "/Users/williamrice/priority_sites_data.json"
        with open(sites_file, 'r') as f:
            dmarco_sites = json.load(f)
        
        maps_created = []
        
        # Create maps for all sites with environmental concerns (not just priority)
        for i in range(1, 12):  # All 11 D'Marco sites
            site_id = f"dmarco_site_{str(i).zfill(2)}"
            site_risk = risk_data[site_id]
            
            # Skip only if no environmental concerns at all
            if site_risk['overall_risk_level'] == 'NO RISK':
                print(f"   ⚪ Skipping {site_id} - No environmental concerns")
                continue
            
            print(f"\n📍 Creating comprehensive map for {site_id}...")
            print(f"   🎯 Risk Level: {site_risk['overall_risk_level']}")
            print(f"   📊 Environmental Sites: {site_risk['total_environmental_sites']}")
            
            # Get site coordinates
            site_index = i - 1
            site_data = self.get_site_coordinates(site_index)
            
            if not site_data:
                print(f"   ❌ Could not get coordinates for {site_id}")
                continue
            
            # Create comprehensive map
            site_map = self.create_comprehensive_site_map(site_id, site_data, risk_data, env_df)
            
            # Save map
            map_filename = f"{self.output_dir}Environmental_Maps/{site_id}_Comprehensive_Environmental_Map.html"
            Path(map_filename).parent.mkdir(parents=True, exist_ok=True)
            site_map.save(map_filename)
            
            maps_created.append({
                'site_id': site_id,
                'address': site_data['address'],
                'overall_risk_level': site_risk['overall_risk_level'],
                'total_environmental_sites': site_risk['total_environmental_sites'],
                'environmental_concerns': site_risk['environmental_concerns'],
                'map_file': map_filename
            })
            
            print(f"   ✅ Map saved: {map_filename}")
        
        # Create summary
        summary_file = f"{self.output_dir}Comprehensive_Environmental_Maps_Summary.json"
        summary_data = {
            'creation_date': datetime.now().isoformat(),
            'analysis_type': 'Multi-Dataset Comprehensive Environmental Mapping',
            'datasets_included': ['LPST', 'Operating Dry Cleaners', 'Environmental Violations'],
            'total_environmental_sites': len(env_df),
            'maps_created': len(maps_created),
            'sites_analyzed': maps_created
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        print(f"\n✅ COMPREHENSIVE ENVIRONMENTAL MAPPING COMPLETE!")
        print(f"   🗺️ Maps created: {len(maps_created)}")
        print(f"   📊 Environmental sites analyzed: {len(env_df):,}")
        print(f"   📋 Summary saved: {summary_file}")
        
        return maps_created

def main():
    """Create comprehensive multi-dataset environmental maps"""
    mapper = MultiDatasetEnvironmentalMapper()
    maps_created = mapper.create_all_priority_site_maps()
    
    print("\n🎉 READY FOR DETAILED STATUS REPORT CREATION!")

if __name__ == "__main__":
    main()