#!/usr/bin/env python3
"""
CTCAC Amenity Mapper - Comprehensive Site Amenity Analysis for LIHTC Projects

This script maps all CTCAC-eligible amenities around a development site and calculates
scoring points based on CTCAC QAP 2025 radius distance requirements.

Author: LIHTC Analysis Team
Date: June 30, 2025
"""

import pandas as pd
import geopandas as gpd
import json
import folium
import requests
from math import radians, cos, sin, asin, sqrt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class CTCACAmenityMapper:
    def __init__(self, data_path=None):
        """Initialize the CTCAC Amenity Mapper with data paths"""
        if data_path is None:
            self.data_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets")
        else:
            self.data_path = Path(data_path)
        
        # CTCAC distance requirements (in miles)
        self.distance_rules = {
            'public_schools': {
                'elementary': {'standard': [0.25, 0.75], 'rural': [0.75, 1.25], 'points': [3, 2]},
                'middle': {'standard': [0.5, 1.0], 'rural': [1.0, 1.5], 'points': [3, 2]},
                'high': {'standard': [1.0, 1.5], 'rural': [1.5, 2.0], 'points': [3, 2]}
            },
            'transit': {
                'bus_rail': {'standard': [0.33, 0.5], 'points': [5, 3]}  # Simplified
            },
            'parks': {
                'public_park': {'standard': [0.5, 0.75], 'rural': [1.0, 1.5], 'points': [3, 2]}
            },
            'libraries': {
                'public_library': {'standard': [0.5, 1.0], 'rural': [1.0, 2.0], 'points': [3, 2]}
            },
            'grocery': {
                'full_scale': {'standard': [0.5, 1.0, 1.5], 'rural': [1.0, 2.0, 3.0], 'points': [5, 4, 3]},
                'neighborhood': {'standard': [0.25, 0.5], 'points': [4, 3]}
            },
            'medical': {
                'clinic_hospital': {'standard': [0.5, 1.0], 'rural': [1.0, 1.5], 'points': [3, 2]}
            },
            'pharmacies': {
                'pharmacy': {'standard': [0.5, 1.0], 'rural': [1.0, 2.0], 'points': [2, 1]}
            },
            'adult_education': {
                'adult_ed': {'standard': [1.0], 'rural': [1.5], 'points': [3]},
                'community_college': {'standard': [1.0], 'rural': [1.5], 'points': [3]}
            }
        }
        
        self.amenity_colors = {
            'public_schools': 'blue',
            'transit': 'green',
            'parks': 'darkgreen', 
            'libraries': 'purple',
            'grocery': 'red',
            'medical': 'orange',
            'pharmacies': 'pink',
            'adult_education': 'darkblue'
        }
        
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate the great circle distance between two points in miles"""
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 3959  # Radius of earth in miles
        return c * r
    
    def geocode_address(self, address):
        """Geocode an address to lat/lng using Census Geocoding API"""
        base_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
        params = {
            'address': address,
            'benchmark': 'Public_AR_Current',
            'format': 'json'
        }
        
        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            
            if data['result']['addressMatches']:
                coords = data['result']['addressMatches'][0]['coordinates']
                return coords['y'], coords['x']  # lat, lng
            else:
                print(f"Could not geocode address: {address}")
                return None, None
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None, None
    
    def load_schools_data(self):
        """Load California public schools data"""
        schools_file = self.data_path / "CA_Public Schools" / "SchoolSites2324_4153587227043982744.csv"
        
        if not schools_file.exists():
            print(f"Schools file not found: {schools_file}")
            return pd.DataFrame()
        
        schools = pd.read_csv(schools_file)
        
        # Filter for active CTCAC-eligible schools
        eligible_schools = schools[
            (schools['Status'] == 'Active') &
            (schools['School Type'].isin(['Elementary', 'Middle', 'High'])) |
            (schools['School Level'] == 'Adult Education')
        ].copy()
        
        # Standardize school types for mapping
        eligible_schools['amenity_type'] = eligible_schools['School Type'].str.lower()
        eligible_schools['amenity_category'] = 'public_schools'
        
        # Standardize column names
        result = eligible_schools[['School Name', 'School Type', 'Street', 'City', 'Latitude', 'Longitude', 
                               'amenity_type', 'amenity_category']].dropna()
        result = result.rename(columns={'School Name': 'name', 'Latitude': 'latitude', 'Longitude': 'longitude'})
        return result
    
    def load_libraries_data(self):
        """Load California libraries data from OpenStreetMap"""
        libraries_file = self.data_path / "CA_Libraries" / "CA_Libraries_OSM.geojson"
        
        if not libraries_file.exists():
            print(f"Libraries file not found: {libraries_file}")
            return pd.DataFrame()
        
        gdf = gpd.read_file(libraries_file)
        
        # Convert geometries to centroids for non-point features
        gdf['centroid'] = gdf.geometry.centroid
        
        # Convert to DataFrame with required columns
        libraries = pd.DataFrame()
        libraries['name'] = gdf['name'].fillna('Public Library')
        libraries['amenity_type'] = 'public_library'
        libraries['amenity_category'] = 'libraries'
        libraries['latitude'] = gdf['centroid'].y
        libraries['longitude'] = gdf['centroid'].x
        
        return libraries.dropna()
    
    def load_pharmacies_data(self):
        """Load California pharmacies data from OpenStreetMap"""
        pharmacies_file = self.data_path / "CA_Pharmacies" / "CA_Pharmacies_OSM.geojson"
        
        if not pharmacies_file.exists():
            print(f"Pharmacies file not found: {pharmacies_file}")
            return pd.DataFrame()
        
        gdf = gpd.read_file(pharmacies_file)
        
        # Convert geometries to centroids for non-point features
        gdf['centroid'] = gdf.geometry.centroid
        
        # Convert to DataFrame with required columns
        pharmacies = pd.DataFrame()
        pharmacies['name'] = gdf['name'].fillna('Pharmacy')
        pharmacies['amenity_type'] = 'pharmacy'
        pharmacies['amenity_category'] = 'pharmacies'
        pharmacies['latitude'] = gdf['centroid'].y
        pharmacies['longitude'] = gdf['centroid'].x
        
        return pharmacies.dropna()
    
    def load_medical_data(self):
        """Load California medical facilities data"""
        medical_file = self.data_path / "CA_Hospitals_Medical" / "Current_CA_Healthcare_Facilities.csv"
        
        if not medical_file.exists():
            print(f"Medical facilities file not found: {medical_file}")
            return pd.DataFrame()
        
        # Note: This CSV may need geocoding if it doesn't have lat/lng
        # For now, return empty DataFrame - would need to implement geocoding
        print("Medical facilities data requires geocoding - not implemented yet")
        return pd.DataFrame()
    
    def calculate_amenity_scores(self, site_lat, site_lng, is_rural=False, project_type='family'):
        """Calculate CTCAC amenity scores for a site"""
        
        results = {
            'site_coordinates': (site_lat, site_lng),
            'is_rural': is_rural,
            'project_type': project_type,
            'amenities_found': {},
            'scoring_summary': {},
            'total_points': 0
        }
        
        # Load all amenity datasets
        schools = self.load_schools_data()
        libraries = self.load_libraries_data()
        pharmacies = self.load_pharmacies_data()
        
        # Combine all amenities
        all_amenities = []
        
        for df, category in [(schools, 'schools'), (libraries, 'libraries'), (pharmacies, 'pharmacies')]:
            if not df.empty:
                df_copy = df.copy()
                df_copy['distance_miles'] = df_copy.apply(
                    lambda row: self.haversine_distance(site_lat, site_lng, row['latitude'], row['longitude']),
                    axis=1
                )
                all_amenities.append(df_copy)
        
        # Analyze each amenity category
        total_points = 0
        
        if not all_amenities:
            print("No amenity data loaded")
            return results
        
        all_amenities_df = pd.concat(all_amenities, ignore_index=True)
        
        # Schools analysis (only for family projects with 25%+ three-bedroom units)
        if project_type == 'family':
            schools_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'public_schools']
            school_points = self._score_schools(schools_nearby, is_rural)
            results['amenities_found']['schools'] = schools_nearby.to_dict('records')
            results['scoring_summary']['schools'] = school_points
            total_points += sum(school_points.values())
        
        # Libraries analysis
        libraries_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'libraries']
        library_points = self._score_libraries(libraries_nearby, is_rural)
        results['amenities_found']['libraries'] = libraries_nearby.to_dict('records')
        results['scoring_summary']['libraries'] = library_points
        total_points += library_points.get('points', 0)
        
        # Pharmacies analysis
        pharmacies_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'pharmacies']
        pharmacy_points = self._score_pharmacies(pharmacies_nearby, is_rural)
        results['amenities_found']['pharmacies'] = pharmacies_nearby.to_dict('records')
        results['scoring_summary']['pharmacies'] = pharmacy_points
        total_points += pharmacy_points.get('points', 0)
        
        results['total_points'] = total_points
        return results
    
    def _score_schools(self, schools_df, is_rural):
        """Score schools based on CTCAC criteria"""
        if schools_df.empty:
            return {'elementary': 0, 'middle': 0, 'high': 0}
        
        points = {'elementary': 0, 'middle': 0, 'high': 0}
        distance_set = 'rural' if is_rural else 'standard'
        
        for school_type in ['elementary', 'middle', 'high']:
            schools_of_type = schools_df[schools_df['amenity_type'] == school_type]
            if not schools_of_type.empty:
                min_distance = schools_of_type['distance_miles'].min()
                distances = self.distance_rules['public_schools'][school_type][distance_set]
                point_values = self.distance_rules['public_schools'][school_type]['points']
                
                for i, max_dist in enumerate(distances):
                    if min_distance <= max_dist:
                        points[school_type] = point_values[i]
                        break
        
        return points
    
    def _score_libraries(self, libraries_df, is_rural):
        """Score libraries based on CTCAC criteria"""
        if libraries_df.empty:
            return {'points': 0, 'closest_distance': None}
        
        min_distance = libraries_df['distance_miles'].min()
        distance_set = 'rural' if is_rural else 'standard'
        distances = self.distance_rules['libraries']['public_library'][distance_set]
        point_values = self.distance_rules['libraries']['public_library']['points']
        
        points = 0
        for i, max_dist in enumerate(distances):
            if min_distance <= max_dist:
                points = point_values[i]
                break
        
        return {'points': points, 'closest_distance': min_distance}
    
    def _score_pharmacies(self, pharmacies_df, is_rural):
        """Score pharmacies based on CTCAC criteria"""
        if pharmacies_df.empty:
            return {'points': 0, 'closest_distance': None}
        
        min_distance = pharmacies_df['distance_miles'].min()
        distance_set = 'rural' if is_rural else 'standard'
        distances = self.distance_rules['pharmacies']['pharmacy'][distance_set]
        point_values = self.distance_rules['pharmacies']['pharmacy']['points']
        
        points = 0
        for i, max_dist in enumerate(distances):
            if min_distance <= max_dist:
                points = point_values[i]
                break
        
        return {'points': points, 'closest_distance': min_distance}
    
    def create_amenity_map(self, site_lat, site_lng, site_name="Development Site", 
                          is_rural=False, project_type='family', zoom_level=14):
        """Create an interactive map showing site and nearby amenities with scoring circles"""
        
        # Calculate scores
        results = self.calculate_amenity_scores(site_lat, site_lng, is_rural, project_type)
        
        # Create base map
        m = folium.Map(location=[site_lat, site_lng], zoom_start=zoom_level)
        
        # Add development site marker
        folium.Marker(
            [site_lat, site_lng],
            popup=f"<b>{site_name}</b><br>Development Site<br>Total CTCAC Points: {results['total_points']}",
            icon=folium.Icon(color='red', icon='home')
        ).add_to(m)
        
        # Add scoring circles for different amenity types
        distance_set = 'rural' if is_rural else 'standard'
        
        # Schools circles (if family project)
        if project_type == 'family':
            for school_type, color in [('elementary', 'blue'), ('middle', 'lightblue'), ('high', 'darkblue')]:
                distances = self.distance_rules['public_schools'][school_type][distance_set]
                for i, dist_miles in enumerate(distances):
                    folium.Circle(
                        [site_lat, site_lng],
                        radius=dist_miles * 1609.34,  # Convert miles to meters
                        popup=f"{school_type.title()} School: {dist_miles} mi ({self.distance_rules['public_schools'][school_type]['points'][i]} pts)",
                        color=color,
                        fillColor=color,
                        fillOpacity=0.1,
                        weight=2,
                        dashArray='5,5'
                    ).add_to(m)
        
        # Library circles
        lib_distances = self.distance_rules['libraries']['public_library'][distance_set]
        for i, dist_miles in enumerate(lib_distances):
            folium.Circle(
                [site_lat, site_lng],
                radius=dist_miles * 1609.34,
                popup=f"Library: {dist_miles} mi ({self.distance_rules['libraries']['public_library']['points'][i]} pts)",
                color='purple',
                fillColor='purple',
                fillOpacity=0.1,
                weight=2,
                dashArray='10,5'
            ).add_to(m)
        
        # Pharmacy circles
        pharm_distances = self.distance_rules['pharmacies']['pharmacy'][distance_set]
        for i, dist_miles in enumerate(pharm_distances):
            folium.Circle(
                [site_lat, site_lng],
                radius=dist_miles * 1609.34,
                popup=f"Pharmacy: {dist_miles} mi ({self.distance_rules['pharmacies']['pharmacy']['points'][i]} pts)",
                color='pink',
                fillColor='pink',
                fillOpacity=0.1,
                weight=2,
                dashArray='15,5'
            ).add_to(m)
        
        # Add amenity markers
        for category, amenities in results['amenities_found'].items():
            color = self.amenity_colors.get(category, 'gray')
            
            for amenity in amenities:
                if 'latitude' in amenity and 'longitude' in amenity:
                    name = amenity.get('name', amenity.get('School Name', 'Unknown'))
                    distance = amenity.get('distance_miles', 0)
                    
                    folium.Marker(
                        [amenity['latitude'], amenity['longitude']],
                        popup=f"<b>{name}</b><br>{category.title()}<br>Distance: {distance:.2f} miles",
                        icon=folium.Icon(color=color, icon='info-sign')
                    ).add_to(m)
        
        # Add legend
        legend_html = self._create_legend(results)
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m, results
    
    def _create_legend(self, results):
        """Create HTML legend for the map"""
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 300px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px;">
        <h4>CTCAC Amenity Scoring</h4>
        <p><b>Total Points: {results['total_points']}</b></p>
        <p><b>Project Type:</b> {results['project_type'].title()}</p>
        <p><b>Rural Status:</b> {'Yes' if results['is_rural'] else 'No'}</p>
        <hr>
        '''
        
        for category, score_data in results['scoring_summary'].items():
            if isinstance(score_data, dict):
                if 'points' in score_data:
                    legend_html += f"<p><b>{category.title()}:</b> {score_data['points']} pts</p>"
                else:
                    total_pts = sum(score_data.values()) if score_data.values() else 0
                    legend_html += f"<p><b>{category.title()}:</b> {total_pts} pts</p>"
        
        legend_html += '''
        <hr>
        <p><small>Circles show CTCAC scoring distances<br>
        Markers show actual amenity locations</small></p>
        </div>
        '''
        
        return legend_html

# Example usage functions
def analyze_site_by_address(address, is_rural=False, project_type='family'):
    """Analyze a site by address"""
    mapper = CTCACAmenityMapper()
    
    # Geocode address
    lat, lng = mapper.geocode_address(address)
    if lat is None:
        print(f"Could not geocode address: {address}")
        return None, None
    
    print(f"Analyzing site at: {lat:.6f}, {lng:.6f}")
    
    # Create map and analysis
    map_obj, results = mapper.create_amenity_map(lat, lng, address, is_rural, project_type)
    
    return map_obj, results

def analyze_site_by_coordinates(lat, lng, site_name="Development Site", is_rural=False, project_type='family'):
    """Analyze a site by coordinates"""
    mapper = CTCACAmenityMapper()
    
    # Create map and analysis
    map_obj, results = mapper.create_amenity_map(lat, lng, site_name, is_rural, project_type)
    
    return map_obj, results

if __name__ == "__main__":
    # Example usage
    print("CTCAC Amenity Mapper")
    print("===================")
    
    # Test with coordinates (Sacramento area)
    test_lat, test_lng = 38.7584, -121.2942
    
    print(f"Testing with coordinates: {test_lat}, {test_lng}")
    
    mapper = CTCACAmenityMapper()
    map_obj, results = mapper.create_amenity_map(
        test_lat, test_lng, 
        "Test Development Site",
        is_rural=False,
        project_type='family'
    )
    
    # Save map
    output_file = "ctcac_amenity_analysis.html"
    map_obj.save(output_file)
    print(f"Map saved to: {output_file}")
    
    # Print scoring summary
    print(f"\nScoring Summary:")
    print(f"Total Points: {results['total_points']}")
    for category, scores in results['scoring_summary'].items():
        print(f"{category.title()}: {scores}")