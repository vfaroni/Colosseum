#!/usr/bin/env python3
"""
Create CTCAC maps for San Bernardino sites with real amenity data
"""

import folium
from folium import plugins
import pandas as pd
import geopandas as gpd
import json
from pathlib import Path
import numpy as np

class SanBernardinoAmenityMapper:
    def __init__(self):
        self.data_base = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Data_Sets/california")
        
    def load_transit_data(self):
        """Load California transit stops"""
        transit_file = self.data_base / "CA_Transit_Data/California_Transit_Stops.geojson"
        if transit_file.exists():
            return gpd.read_file(transit_file)
        return None
    
    def load_hqta_data(self):
        """Load High Quality Transit Areas"""
        hqta_file = self.data_base / "CA_Transit_Data/High_Quality_Transit_Areas.geojson"
        if hqta_file.exists():
            return gpd.read_file(hqta_file)
        return None
    
    def load_schools_data(self):
        """Load California public schools"""
        # Check what school files we have
        schools_path = self.data_base / "CA_Public Schools"
        for file in schools_path.glob("*.geojson"):
            return gpd.read_file(file)
        for file in schools_path.glob("*.csv"):
            df = pd.read_csv(file)
            if 'Latitude' in df.columns and 'Longitude' in df.columns:
                return df
        return None
    
    def load_medical_data(self):
        """Load hospitals/medical facilities"""
        medical_path = self.data_base / "CA_Hospitals_Medical"
        for file in medical_path.glob("*.geojson"):
            return gpd.read_file(file)
        for file in medical_path.glob("*.csv"):
            return pd.read_csv(file)
        return None
    
    def load_grocery_data(self):
        """Load grocery stores"""
        grocery_path = self.data_base / "CA_Grocery_Stores"
        for file in grocery_path.glob("*.geojson"):
            return gpd.read_file(file)
        for file in grocery_path.glob("*.csv"):
            return pd.read_csv(file)
        return None
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance in miles between two points"""
        R = 3959  # Earth's radius in miles
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        return R * c
    
    def find_nearby_amenities(self, site_lat, site_lng, amenity_df, max_distance=1.5):
        """Find amenities within max_distance miles"""
        nearby = []
        
        if amenity_df is None:
            return nearby
            
        # Handle different data types
        if isinstance(amenity_df, gpd.GeoDataFrame) and 'geometry' in amenity_df.columns:
            # For GeoDataFrame with point geometry
            for idx, row in amenity_df.iterrows():
                if row.geometry and hasattr(row.geometry, 'y'):
                    dist = self.calculate_distance(site_lat, site_lng, row.geometry.y, row.geometry.x)
                    if dist <= max_distance:
                        nearby.append({
                            'name': row.get('Name', row.get('name', f'Amenity {idx}')),
                            'lat': row.geometry.y,
                            'lng': row.geometry.x,
                            'distance': dist
                        })
        else:
            # For regular DataFrame with lat/lng columns
            lat_cols = ['Latitude', 'latitude', 'lat', 'LAT', 'Y']
            lng_cols = ['Longitude', 'longitude', 'lng', 'lon', 'LON', 'LONG', 'X']
            name_cols = ['Name', 'name', 'School', 'SchoolName', 'FACILITY_NAME']
            
            lat_col = next((c for c in lat_cols if c in amenity_df.columns), None)
            lng_col = next((c for c in lng_cols if c in amenity_df.columns), None)
            name_col = next((c for c in name_cols if c in amenity_df.columns), None)
            
            if lat_col and lng_col:
                for idx, row in amenity_df.iterrows():
                    if pd.notna(row[lat_col]) and pd.notna(row[lng_col]):
                        dist = self.calculate_distance(site_lat, site_lng, row[lat_col], row[lng_col])
                        if dist <= max_distance:
                            nearby.append({
                                'name': row[name_col] if name_col else f'Amenity {idx}',
                                'lat': row[lat_col],
                                'lng': row[lng_col],
                                'distance': dist
                            })
        
        return sorted(nearby, key=lambda x: x['distance'])
    
    def create_enhanced_map(self, site_info, parcel_corners):
        """Create map with real amenity data"""
        lat, lng = site_info['lat'], site_info['lng']
        
        # Create base map
        m = folium.Map(location=[lat, lng], zoom_start=16)
        
        # Add controls
        plugins.MeasureControl(position='topright').add_to(m)
        folium.plugins.MiniMap().add_to(m)
        
        # Add parcel boundary
        if parcel_corners:
            boundary = list(parcel_corners)
            if boundary[0] != boundary[-1]:
                boundary.append(boundary[0])
            
            folium.Polygon(
                locations=boundary,
                color='darkred',
                weight=3,
                fill=True,
                fillColor='red',
                fillOpacity=0.1,
                popup=f"<b>{site_info['address']}</b><br>APN: {site_info['apn']}<br>Area: {site_info['area_acres']} acres"
            ).add_to(m)
        
        # Add site marker
        folium.Marker(
            [lat, lng],
            popup=f"<b>{site_info['address']}</b><br>Center: {lat:.6f}, {lng:.6f}",
            icon=folium.Icon(color='red', icon='home')
        ).add_to(m)
        
        # Load and add amenities
        print(f"\n📍 Loading amenities for {site_info['address']}...")
        
        # Transit stops
        transit_data = self.load_transit_data()
        transit_stops = self.find_nearby_amenities(lat, lng, transit_data, 1.0)
        print(f"   Found {len(transit_stops)} transit stops within 1 mile")
        
        for stop in transit_stops[:10]:  # Show closest 10
            color = 'blue' if stop['distance'] <= 0.333 else 'lightblue'
            folium.Marker(
                [stop['lat'], stop['lng']],
                popup=f"<b>Transit Stop</b><br>{stop['name']}<br>{stop['distance']:.2f} miles",
                icon=folium.Icon(color=color, icon='bus', prefix='fa')
            ).add_to(m)
        
        # Schools
        schools_data = self.load_schools_data()
        schools = self.find_nearby_amenities(lat, lng, schools_data, 1.0)
        print(f"   Found {len(schools)} schools within 1 mile")
        
        for school in schools[:10]:
            color = 'green' if school['distance'] <= 0.25 else 'lightgreen'
            folium.Marker(
                [school['lat'], school['lng']],
                popup=f"<b>School</b><br>{school['name']}<br>{school['distance']:.2f} miles",
                icon=folium.Icon(color=color, icon='graduation-cap', prefix='fa')
            ).add_to(m)
        
        # Medical facilities
        medical_data = self.load_medical_data()
        medical = self.find_nearby_amenities(lat, lng, medical_data, 1.0)
        print(f"   Found {len(medical)} medical facilities within 1 mile")
        
        for facility in medical[:5]:
            color = 'darkred' if facility['distance'] <= 0.5 else 'pink'
            folium.Marker(
                [facility['lat'], facility['lng']],
                popup=f"<b>Medical</b><br>{facility['name']}<br>{facility['distance']:.2f} miles",
                icon=folium.Icon(color=color, icon='hospital-o', prefix='fa')
            ).add_to(m)
        
        # Add distance circles
        for dist_miles, color, label in [(0.25, 'black', '0.25 mi'), (0.333, 'gray', '1/3 mi'), 
                                         (0.5, 'darkgray', '0.5 mi'), (1.0, 'lightgray', '1.0 mi')]:
            folium.Circle(
                [lat, lng],
                radius=dist_miles * 1609.34,
                color=color,
                fill=False,
                weight=2,
                dash_array='10,5'
            ).add_to(m)
        
        # Calculate CTCAC scores
        transit_score = 7 if any(s['distance'] <= 0.333 for s in transit_stops) else 0
        school_score = 3 if any(s['distance'] <= 0.25 for s in schools) else 0
        medical_score = 3 if any(s['distance'] <= 0.5 for s in medical) else 0
        
        print(f"   CTCAC Scores: Transit={transit_score}, School={school_score}, Medical={medical_score}")
        
        # Add legend
        legend_html = f'''
        <div style='position: fixed; top: 10px; right: 50px; width: 300px;
                    background-color: white; z-index: 1000; border:2px solid grey;
                    font-size: 14px; padding: 10px'>
        <h4 style='margin-top:0;'>CTCAC Amenity Analysis</h4>
        <b>{site_info['address']}</b><br>
        <hr>
        <b>Amenities Found:</b><br>
        🚌 Transit: {len(transit_stops)} stops<br>
        🏫 Schools: {len(schools)}<br>
        🏥 Medical: {len(medical)}<br>
        <hr>
        <b>CTCAC Points:</b><br>
        Transit: {transit_score}/7<br>
        Schools: {school_score}/3<br>
        Medical: {medical_score}/3<br>
        <hr>
        <i>Data from CA datasets</i>
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m


def main():
    # Load San Bernardino analysis results
    results_file = Path('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport-11_SB_REAL_ANALYSIS_20250806_205547.xlsx')
    
    df = pd.read_excel(results_file, sheet_name='Parcel_Analysis')
    sites = df[df['status'] == 'Success'].head(3)
    
    mapper = SanBernardinoAmenityMapper()
    
    print("🗺️ Creating Enhanced CTCAC Maps with Real Amenity Data")
    print("=" * 60)
    
    for idx, row in sites.iterrows():
        site_num = idx + 1
        
        # Parse corners
        corners = json.loads(row['corners_json']) if row['corners_json'] else []
        
        site_info = {
            'address': row['address'],
            'lat': row['lat'],
            'lng': row['lng'],
            'apn': row['apn'],
            'area_acres': row['area_acres']
        }
        
        # Create enhanced map
        m = mapper.create_enhanced_map(site_info, corners)
        
        # Save map
        output_file = f"san_bernardino_site_{site_num}_enhanced_ctcac_map.html"
        m.save(output_file)
        print(f"\n✅ Enhanced map saved: {output_file}")
    
    print("\n" + "="*60)
    print("✅ All enhanced maps created with real California amenity data!")


if __name__ == "__main__":
    main()