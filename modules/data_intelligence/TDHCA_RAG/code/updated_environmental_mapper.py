#!/usr/bin/env python3

import pandas as pd
import json
from pathlib import Path
import folium
from datetime import datetime
import numpy as np

class ClientReadyEnvironmentalMapper:
    """
    Create client-ready environmental maps with:
    1. Industry-standard risk thresholds
    2. Professional distance-based risk categories
    3. Clean presentation for client delivery
    """
    
    def __init__(self):
        self.base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG"
        self.output_dir = f"{self.base_dir}/D'Marco_Sites/"
        
        # Load updated risk analysis
        self.updated_risk_file = f"{self.output_dir}Updated_DMarco_Environmental_Risk_Analysis.json"
        
        # Updated risk level colors (industry standard)
        self.risk_colors = {
            'CRITICAL': '#8B0000',        # Dark red
            'HIGH': '#FF0000',            # Red  
            'MODERATE-HIGH': '#FF4500',   # Orange red
            'MODERATE': '#FFA500',        # Orange
            'LOW-MODERATE': '#FFD700',    # Gold
            'LOW': '#32CD32',             # Lime green
            'NO RISK': '#90EE90',         # Light green
            'NEGLIGIBLE': '#E0E0E0'       # Light gray
        }
        
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
        
        # Updated risk thresholds for buffer circles
        self.risk_buffers = [
            {'radius': 0, 'color': '#8B0000', 'label': 'On-site (CRITICAL)', 'opacity': 0.2},
            {'radius': 500 * 0.3048, 'color': '#FF0000', 'label': '500 feet (HIGH)', 'opacity': 0.15},
            {'radius': 0.1 * 1609.34, 'color': '#FF4500', 'label': '0.1 mile (MODERATE-HIGH)', 'opacity': 0.12},
            {'radius': 0.25 * 1609.34, 'color': '#FFA500', 'label': '0.25 mile (MODERATE)', 'opacity': 0.1},
            {'radius': 0.5 * 1609.34, 'color': '#FFD700', 'label': '0.5 mile (LOW-MODERATE)', 'opacity': 0.08},
            {'radius': 1.0 * 1609.34, 'color': '#32CD32', 'label': '1.0 mile (LOW)', 'opacity': 0.05}
        ]
    
    def load_updated_data(self):
        """Load updated risk analysis and clean environmental data"""
        print("📊 Loading updated risk analysis and clean environmental data...")
        
        # Load updated risk analysis
        with open(self.updated_risk_file, 'r') as f:
            updated_risks = json.load(f)
        
        # Load and filter environmental data (same filtering as in analysis)
        env_database = f"{self.output_dir}Comprehensive_Environmental_Database.csv"
        env_df = pd.read_csv(env_database, low_memory=False)
        
        # Apply same quality filters as in updated analysis
        original_count = len(env_df)
        env_df = env_df[~(env_df['address'].isna() | env_df['address'].str.contains('nan', case=False, na=False))]
        env_df = env_df[env_df['geocoding_confidence'] >= 0.8]
        filtered_count = len(env_df)
        
        print(f"   ✅ Loaded updated risk analysis for 11 D'Marco sites")
        print(f"   ✅ Filtered environmental data: {filtered_count} valid sites (excluded {original_count - filtered_count})")
        
        return updated_risks, env_df
    
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
    
    def determine_risk_level_from_distance(self, distance_miles, contaminant_type='Unknown'):
        """Determine risk level based on distance (matching the updated analyzer)"""
        
        # Contaminant modifiers
        contaminant_modifiers = {
            'Petroleum Contamination': 1.0,
            'Active Solvent Operations': 1.2,
            'Environmental Violations': 1.1
        }
        
        modifier = contaminant_modifiers.get(contaminant_type, 1.0)
        effective_distance = distance_miles / modifier
        
        if effective_distance <= 0.001:  # On-site
            return 'CRITICAL'
        elif effective_distance <= 500 * 0.000189394:  # 500 feet
            return 'HIGH'
        elif effective_distance <= 0.1:
            return 'MODERATE-HIGH'
        elif effective_distance <= 0.25:
            return 'MODERATE'
        elif effective_distance <= 0.5:
            return 'LOW-MODERATE'
        elif effective_distance <= 1.0:
            return 'LOW'
        else:
            return 'NEGLIGIBLE'
    
    def create_updated_site_map(self, site_id, site_data, updated_risks, env_df):
        """Create updated map for a single D'Marco site with clean data and proper risk levels"""
        print(f"🗺️ Creating updated map for {site_id}...")
        
        site_risk_data = updated_risks['updated_site_analysis'][site_id]
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
            overall_risk = site_risk_data['overall_risk_level']
            total_sites = site_risk_data['total_environmental_sites']
            
            # Create comprehensive parcel popup
            parcel_popup = f"""
            <div style="width: 450px; font-family: Arial, sans-serif;">
                <h3 style="color: #2E8B57; margin-bottom: 10px;">
                    🏠 D'MARCO DEVELOPMENT SITE
                </h3>
                
                <div style="background-color: #f0f8f0; padding: 12px; border-radius: 5px; margin-bottom: 10px;">
                    <b>📍 Address:</b> {site_data['address']}<br>
                    <b>📏 Size:</b> {site_data['size_acres']} acres<br>
                    <b>🆔 Site ID:</b> {site_id.upper()}<br>
                </div>
                
                <div style="background-color: {'#ffcdd2' if overall_risk in ['CRITICAL', 'HIGH'] else '#fff3e0' if overall_risk in ['MODERATE-HIGH', 'MODERATE'] else '#fff8e1' if overall_risk == 'LOW-MODERATE' else '#e8f5e8'}; 
                           padding: 12px; border-radius: 5px; border-left: 4px solid {self.risk_colors[overall_risk]};">
                    <h4 style="color: {self.risk_colors[overall_risk]}; margin: 0 0 8px 0;">
                        🌍 ENVIRONMENTAL RISK: {overall_risk}
                    </h4>
                    <b>Environmental Sites:</b> {total_sites} within assessment range<br>
                    <b>Risk Assessment:</b> Industry-standard distance-based methodology<br>
                </div>
                
                <div style="margin-top: 12px; padding: 10px; background-color: #e3f2fd; border-radius: 5px;">
                    <b>📋 Due Diligence:</b><br>
                    {site_risk_data.get('due_diligence_requirements', {}).get('due_diligence', 'Standard environmental review')}<br>
                    <b>💰 Cost Range:</b> {site_risk_data.get('due_diligence_requirements', {}).get('cost_range', '$1,500-$5,000')}<br>
                    <b>⏱️ Timeline:</b> {site_risk_data.get('due_diligence_requirements', {}).get('timeline', '1-3 weeks')}
                </div>
                
            </div>
            """
            
            folium.Polygon(
                locations=parcel_coords,
                color=self.risk_colors[overall_risk],
                weight=4,
                fillColor=self.risk_colors[overall_risk],
                fillOpacity=0.3,
                popup=folium.Popup(parcel_popup, max_width=500)
            ).add_to(m)
        
        # Add D'Marco site center marker
        folium.Marker(
            [center_lat, center_lon],
            icon=folium.Icon(color='green', icon='home', prefix='fa'),
            tooltip=f"D'Marco Site: {site_data['address']}"
        ).add_to(m)
        
        # Add environmental sites from updated analysis
        if site_risk_data['all_risks']:
            for dataset in ['lpst', 'operating_dry_cleaners', 'enforcement']:
                # Create feature group for this dataset
                feature_group = folium.FeatureGroup(name=self.dataset_styles[dataset]['name'])
                
                dataset_sites = [risk for risk in site_risk_data['all_risks'] if risk['dataset'] == dataset]
                
                for env_site in dataset_sites:
                    # Find the site in the clean dataframe to get coordinates
                    site_match = env_df[env_df['site_name'] == env_site['site_name']]
                    if len(site_match) == 0:
                        continue
                    
                    site_row = site_match.iloc[0]
                    
                    # Create comprehensive popup
                    popup_html = f"""
                    <div style="width: 450px; font-family: Arial, sans-serif;">
                        <h3 style="color: {self.dataset_styles[dataset]['color']}; margin-bottom: 10px;">
                            🏭 {env_site['risk_type'].upper()}
                        </h3>
                        
                        <div style="background-color: #ffebee; padding: 12px; border-radius: 5px; margin-bottom: 10px;">
                            <h4 style="margin: 0 0 8px 0; color: #d32f2f;">{env_site['site_name']}</h4>
                            <b>📍 Address:</b> {env_site['address']}<br>
                            <b>🏙️ City:</b> {site_row['city']}<br>
                            <b>🆔 Site ID:</b> {site_row['site_id']}<br>
                            <b>📊 Dataset:</b> {dataset.replace('_', ' ').title()}<br>
                        </div>
                        
                        <div style="background-color: {'#ffcdd2' if env_site['risk_level'] in ['CRITICAL', 'HIGH'] else '#ffe0b2' if env_site['risk_level'] in ['MODERATE-HIGH', 'MODERATE'] else '#fff9c4' if env_site['risk_level'] == 'LOW-MODERATE' else '#dcedc8'}; 
                                   padding: 12px; border-radius: 5px; border-left: 4px solid {self.risk_colors[env_site['risk_level']]};">
                            <h4 style="color: {self.risk_colors[env_site['risk_level']]}; margin: 0 0 8px 0;">
                                ⚠️ RISK LEVEL: {env_site['risk_level']}
                            </h4>
                            <b>Distance to D'Marco Site:</b> {env_site['distance_miles']:.3f} miles<br>
                            <b>Environmental Concern:</b> {env_site['risk_type']}<br>
                        </div>
                        
                        <div style="background-color: #f3e5f5; padding: 12px; margin-top: 10px; border-radius: 5px;">
                            <h4 style="color: #7B1FA2; margin: 0 0 8px 0;">📋 METHODOLOGY</h4>
                            <b>Risk Threshold:</b> Industry-standard distance categories<br>
                            <b>Data Source:</b> Texas Commission on Environmental Quality (TCEQ)
                        </div>
                    </div>
                    """
                    
                    # Add environmental site marker
                    folium.Marker(
                        [site_row['latitude'], site_row['longitude']],
                        popup=folium.Popup(popup_html, max_width=500),
                        icon=folium.Icon(
                            color=self.dataset_styles[dataset]['marker_color'], 
                            icon=self.dataset_styles[dataset]['icon'], 
                            prefix='fa'
                        ),
                        tooltip=f"{env_site['site_name']} ({env_site['distance_miles']:.3f} mi - {env_site['risk_level']})"
                    ).add_to(feature_group)
                    
                    # Add distance line
                    folium.PolyLine(
                        locations=[[center_lat, center_lon], [site_row['latitude'], site_row['longitude']]],
                        color=self.risk_colors[env_site['risk_level']],
                        weight=3,
                        opacity=0.7,
                        popup=f"Distance: {env_site['distance_miles']:.3f} miles - Risk: {env_site['risk_level']}"
                    ).add_to(feature_group)
                
                # Add feature group to map if it has sites
                if dataset_sites:
                    feature_group.add_to(m)
        
        # Add updated risk buffer circles
        for buffer in self.risk_buffers:
            if buffer['radius'] > 0:  # Skip on-site circle
                folium.Circle(
                    [center_lat, center_lon],
                    radius=buffer['radius'],
                    color=buffer['color'],
                    weight=2,
                    fillOpacity=buffer['opacity'],
                    popup=f"Environmental screening buffer: {buffer['label']}",
                    tooltip=buffer['label']
                ).add_to(m)
        
        # Add comprehensive legend
        clean_sites_count = len(env_df)
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 20px; right: 20px; width: 350px; height: 550px; 
                    background-color: white; border:3px solid grey; z-index:9999; 
                    font-size:12px; padding: 15px; border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3); overflow-y: auto;">
        <h3 style="margin-top: 0; color: #333;">🌍 ENVIRONMENTAL ANALYSIS</h3>
        
        <div style="margin-bottom: 12px;">
            <h4 style="margin: 8px 0 5px 0; color: #555;">📏 Risk Thresholds:</h4>
            <p style="margin: 2px 0; font-size: 11px;"><span style="color:#8B0000">●</span> <b>CRITICAL</b>: On-site</p>
            <p style="margin: 2px 0; font-size: 11px;"><span style="color:#FF0000">●</span> <b>HIGH</b>: Within 500 feet</p>
            <p style="margin: 2px 0; font-size: 11px;"><span style="color:#FF4500">●</span> <b>MODERATE-HIGH</b>: 500ft - 0.1 mi</p>
            <p style="margin: 2px 0; font-size: 11px;"><span style="color:#FFA500">●</span> <b>MODERATE</b>: 0.1 - 0.25 mi</p>
            <p style="margin: 2px 0; font-size: 11px;"><span style="color:#FFD700">●</span> <b>LOW-MODERATE</b>: 0.25 - 0.5 mi</p>
            <p style="margin: 2px 0; font-size: 11px;"><span style="color:#32CD32">●</span> <b>LOW</b>: 0.5 - 1.0 mi</p>
        </div>
        
        <div style="margin-bottom: 12px;">
            <h4 style="margin: 8px 0 5px 0; color: #555;">Environmental Datasets:</h4>
            <p style="margin: 2px 0;"><i class="fa fa-tint" style="color:#8B0000"></i> 
               <b style="color:#8B0000">LPST</b>: Petroleum contamination</p>
            <p style="margin: 2px 0;"><i class="fa fa-industry" style="color:#800080"></i> 
               <b style="color:#800080">Dry Cleaners</b>: Active solvent operations</p>
            <p style="margin: 2px 0;"><i class="fa fa-gavel" style="color:#DC143C"></i> 
               <b style="color:#DC143C">Violations</b>: Environmental enforcement</p>
        </div>
        
        <div style="margin-bottom: 12px;">
            <h4 style="margin: 8px 0 5px 0; color: #555;">Site Status:</h4>
            <p style="margin: 2px 0; font-size: 11px;"><b>Overall Risk:</b> <span style="color: {self.risk_colors[site_risk_data['overall_risk_level']]}"><b>{site_risk_data['overall_risk_level']}</b></span></p>
            <p style="margin: 2px 0; font-size: 11px;"><b>Environmental Sites:</b> {site_risk_data['total_environmental_sites']} environmental risks</p>
            <p style="margin: 2px 0; font-size: 11px;"><b>Risk Types:</b> {site_risk_data['environmental_concerns']} concern categories</p>
        </div>
        
        <div style="border-top: 1px solid #ccc; padding-top: 8px;">
            <p style="margin: 2px 0; font-size: 10px; color: #666;"><b>Methodology:</b> Industry-standard distance thresholds</p>
            <p style="margin: 8px 0 2px 0; font-size: 10px; color: #888; text-align: center; font-style: italic;"><b>Analysis by Structured Consultants LLC</b></p>
        </div>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add updated title
        title_html = f'''
        <div style="position: fixed; 
                    top: 20px; left: 50%; transform: translateX(-50%); 
                    background-color: rgba(255,255,255,0.95); 
                    padding: 15px 25px; border-radius: 10px; border: 2px solid #333;
                    z-index: 9999; text-align: center;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <h3 style="margin: 0 0 5px 0; color: #333; font-size: 16px;">🌍 {site_id.upper()}: ENVIRONMENTAL ANALYSIS</h3>
            <p style="margin: 0 0 5px 0; color: #666; font-size: 14px;">
                {site_data['address']} • Risk Level: <span style="color: {self.risk_colors[site_risk_data['overall_risk_level']]}"><b>{site_risk_data['overall_risk_level']}</b></span>
            </p>
            <p style="margin: 0 0 5px 0; color: #555; font-size: 12px;">
                Industry Thresholds • {site_risk_data['total_environmental_sites']} Environmental Sites
            </p>
            <p style="margin: 0; color: #888; font-size: 11px; font-style: italic;">
                <b>Analysis by Structured Consultants LLC</b>
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
    
    def create_all_updated_maps(self):
        """Create updated environmental maps for all D'Marco sites"""
        print("🗺️ CREATING CLIENT-READY ENVIRONMENTAL MAPS WITH INDUSTRY-STANDARD RISK LEVELS")
        print("=" * 80)
        
        # Load updated data
        updated_risks, env_df = self.load_updated_data()
        
        # Load D'Marco site coordinates
        sites_file = "/Users/williamrice/priority_sites_data.json"
        with open(sites_file, 'r') as f:
            dmarco_sites = json.load(f)
        
        maps_created = []
        
        # Create maps for all sites (including NO RISK sites for comparison)
        for i in range(1, 12):
            site_id = f"dmarco_site_{str(i).zfill(2)}"
            site_data = updated_risks['updated_site_analysis'][site_id]
            
            print(f"\n📍 Creating updated map for {site_id}...")
            print(f"   🎯 Updated Risk Level: {site_data['overall_risk_level']}")
            print(f"   📊 Clean Environmental Sites: {site_data['total_environmental_sites']}")
            
            # Get site coordinates
            site_index = i - 1
            site_coords = self.get_site_coordinates(site_index)
            
            if not site_coords:
                print(f"   ❌ Could not get coordinates for {site_id}")
                continue
            
            # Create updated map
            site_map = self.create_updated_site_map(site_id, site_coords, updated_risks, env_df)
            
            # Save map
            map_filename = f"{self.output_dir}Environmental_Maps_Client_Ready/{site_id}_Environmental_Analysis_Map.html"
            Path(map_filename).parent.mkdir(parents=True, exist_ok=True)
            site_map.save(map_filename)
            
            maps_created.append({
                'site_id': site_id,
                'address': site_coords['address'],
                'updated_risk_level': site_data['overall_risk_level'],
                'clean_environmental_sites': site_data['total_environmental_sites'],
                'environmental_concerns': site_data['environmental_concerns'],
                'map_file': map_filename
            })
            
            print(f"   ✅ Updated map saved: {map_filename}")
        
        # Create summary
        summary_file = f"{self.output_dir}Environmental_Maps_Client_Summary.json"
        summary_data = {
            'creation_date': datetime.now().isoformat(),
            'analysis_type': 'Environmental Mapping with Industry-Standard Risk Levels',
            'methodology': [
                'Industry-standard distance-based risk thresholds',
                'Contaminant-specific risk modifiers applied',
                'High-quality environmental data analysis'
            ],
            'datasets_included': ['LPST', 'Operating Dry Cleaners', 'Environmental Violations'],
            'maps_created': len(maps_created),
            'sites_analyzed': maps_created
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        print(f"\n✅ CLIENT-READY ENVIRONMENTAL MAPPING COMPLETE!")
        print(f"   🗺️ Maps created: {len(maps_created)}")
        print(f"   📊 Industry-standard risk thresholds applied")
        print(f"   📋 Summary saved: {summary_file}")
        
        # Print risk level distribution
        risk_distribution = {}
        for map_data in maps_created:
            risk_level = map_data['updated_risk_level']
            risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
        
        print(f"\n📈 RISK DISTRIBUTION:")
        for risk_level, count in sorted(risk_distribution.items()):
            print(f"   • {risk_level}: {count} sites")
        
        return maps_created

def main():
    """Create client-ready environmental maps"""
    mapper = ClientReadyEnvironmentalMapper()
    maps_created = mapper.create_all_updated_maps()
    
    print("\n🎉 CLIENT-READY ENVIRONMENTAL MAPS COMPLETE!")
    print("✅ Industry-standard risk thresholds applied")
    print("📊 Professional distance-based risk categories")
    print("📋 Ready for client delivery")

if __name__ == "__main__":
    main()