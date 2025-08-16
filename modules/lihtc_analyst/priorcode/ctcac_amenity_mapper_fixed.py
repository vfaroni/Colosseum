#!/usr/bin/env python3
"""
CTCAC Amenity Mapper - FIXED VERSION with correct data paths
Comprehensive Site Amenity Analysis for LIHTC Projects with available CA data
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

class CTCACAmenityMapperFixed:
    def __init__(self, data_path=None):
        """Initialize with correct data paths"""
        if data_path is None:
            self.data_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets")
        else:
            self.data_path = Path(data_path)
        
        # Complete CTCAC distance requirements (in miles)
        self.distance_rules = {
            'transit': {
                'brt_rail_ferry_high_density': {'standard': [0.33], 'points': [7], 'requires_density': True},
                'brt_rail_ferry_regular': {'standard': [0.33], 'points': [6]},
                'brt_rail_ferry_half_mile': {'standard': [0.5], 'points': [5]},
                'basic_transit_third': {'standard': [0.33], 'rural': [0.33], 'points': [4]},
                'basic_transit_half': {'standard': [0.5], 'rural': [0.5], 'points': [3]}
            },
            'public_park': {
                'park_community_center': {'standard': [0.5, 0.75], 'rural': [1.0, 1.5], 'points': [3, 2]}
            },
            'library': {
                'public_library': {'standard': [0.5, 1.0], 'rural': [1.0, 2.0], 'points': [3, 2]}
            },
            'grocery': {
                'full_scale': {'standard': [0.5, 1.0, 1.5], 'rural': [1.0, 2.0, 3.0], 'points': [5, 4, 3]},
                'neighborhood': {'standard': [0.25, 0.5], 'rural': [0.5, 1.0], 'points': [4, 3]},
                'farmers_market': {'standard': [0.5, 1.0], 'points': [2, 1]}
            },
            'schools': {
                'adult_ed_community_college': {'standard': [1.0], 'rural': [1.5], 'points': [3]},
                'elementary': {'standard': [0.25, 0.75], 'rural': [0.75, 1.25], 'points': [3, 2]},
                'middle': {'standard': [0.5, 1.0], 'rural': [1.0, 1.5], 'points': [3, 2]},
                'high': {'standard': [1.0, 1.5], 'rural': [1.5, 2.5], 'points': [3, 2]}
            },
            'medical': {
                'clinic_hospital': {'standard': [0.5, 1.0], 'rural': [1.0, 1.5], 'points': [3, 2]}
            },
            'opportunity_area': {
                'highest_high_resource': {'points': [8]}
            }
        }
        
        self.amenity_colors = {
            'transit': 'green',
            'public_park': 'darkgreen',
            'library': 'purple',
            'grocery': 'orange',
            'schools': 'blue',
            'medical': 'red',
            'pharmacy': 'pink',
            'senior_center': 'gray'
        }
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in miles"""
        R = 3959  # Earth's radius in miles
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return 2 * R * asin(sqrt(a))
    
    def load_schools_data(self):
        """Load California schools data"""
        try:
            schools_file = self.data_path / "california" / "CA_Public Schools" / "SchoolSites2324_4153587227043982744.csv"
            if schools_file.exists():
                df = pd.read_csv(schools_file)
                if 'Latitude' in df.columns and 'Longitude' in df.columns:
                    df['latitude'] = df['Latitude']
                    df['longitude'] = df['Longitude']
                    df['amenity_category'] = 'schools'
                    df['name'] = df.get('School', df.get('SchoolName', 'School'))
                    print(f"✅ Loaded {len(df)} schools")
                    return df.dropna(subset=['latitude', 'longitude'])
        except Exception as e:
            print(f"Error loading schools: {e}")
        return pd.DataFrame()
    
    def load_libraries_data(self):
        """Load California libraries data"""
        try:
            libraries_file = self.data_path / "california" / "CA_Libraries" / "CA_Libraries_OSM.geojson"
            if libraries_file.exists():
                gdf = gpd.read_file(libraries_file)
                if not gdf.empty:
                    # Extract coordinates properly
                    coords = gdf.geometry.apply(lambda geom: (geom.x, geom.y))
                    gdf['longitude'] = coords.apply(lambda x: x[0])
                    gdf['latitude'] = coords.apply(lambda x: x[1])
                    gdf['amenity_category'] = 'library'
                    gdf['name'] = gdf.get('name', 'Library').fillna('Library')
                    # Filter out rows with invalid coordinates
                    gdf = gdf.dropna(subset=['latitude', 'longitude'])
                    print(f"✅ Loaded {len(gdf)} libraries")
                    return gdf.drop('geometry', axis=1)
        except Exception as e:
            print(f"Error loading libraries: {e}")
        return pd.DataFrame()
    
    def load_medical_data(self):
        """Load California medical facilities data"""
        try:
            medical_file = self.data_path / "california" / "CA_Hospitals_Medical" / "Licensed_and_Certified_Healthcare_Facilities.csv"
            if medical_file.exists():
                df = pd.read_csv(medical_file)
                if 'LATITUDE' in df.columns and 'LONGITUDE' in df.columns:
                    df['latitude'] = df['LATITUDE']
                    df['longitude'] = df['LONGITUDE']
                    df['amenity_category'] = 'medical'
                    df['name'] = df.get('FACILITY_NAME', 'Medical Facility')
                    print(f"✅ Loaded {len(df)} medical facilities")
                    return df.dropna(subset=['latitude', 'longitude'])
        except Exception as e:
            print(f"Error loading medical facilities: {e}")
        return pd.DataFrame()
    
    def load_transit_data(self):
        """Load California transit data"""
        try:
            transit_file = self.data_path / "california" / "CA_Transit_Data" / "California_Transit_Stops.csv"
            if transit_file.exists():
                df = pd.read_csv(transit_file)
                if 'stop_lat' in df.columns and 'stop_lon' in df.columns:
                    df['latitude'] = df['stop_lat']
                    df['longitude'] = df['stop_lon']
                    df['amenity_category'] = 'transit'
                    df['name'] = df.get('stop_name', 'Transit Stop')
                    print(f"✅ Loaded {len(df)} transit stops")
                    return df.dropna(subset=['latitude', 'longitude'])
        except Exception as e:
            print(f"Error loading transit data: {e}")
        return pd.DataFrame()
    
    def load_hqta_data(self):
        """Load High Quality Transit Areas"""
        try:
            hqta_file = self.data_path / "california" / "CA_Transit_Data" / "High_Quality_Transit_Areas.csv"
            if hqta_file.exists():
                df = pd.read_csv(hqta_file)
                # HQTA areas might need coordinate extraction from geometry
                print(f"✅ Found HQTA file with {len(df)} areas")
                return df
        except Exception as e:
            print(f"Error loading HQTA data: {e}")
        return pd.DataFrame()
    
    def load_grocery_data(self):
        """Load California grocery stores data"""
        try:
            grocery_file = self.data_path / "california" / "CA_Grocery_Stores" / "CA_Grocery_Stores.csv"
            if grocery_file.exists():
                df = pd.read_csv(grocery_file)
                if 'latitude' in df.columns and 'longitude' in df.columns:
                    df['amenity_category'] = 'grocery'
                    df['name'] = df.get('name', df.get('business_name', 'Grocery Store'))
                    print(f"✅ Loaded {len(df)} grocery stores")
                    return df.dropna(subset=['latitude', 'longitude'])
        except Exception as e:
            print(f"Error loading grocery stores: {e}")
        return pd.DataFrame()
    
    def calculate_amenity_scores(self, site_lat, site_lng, is_rural=False, 
                               project_type='family', qualifying_development=False,
                               new_construction=False, large_family=False, 
                               opportunity_area_status=None):
        """Calculate CTCAC amenity scores with available data"""
        
        results = {
            'site_coordinates': (site_lat, site_lng),
            'is_rural': is_rural,
            'project_type': project_type,
            'amenities_found': {},
            'scoring_summary': {},
            'total_points': 0,
            'max_possible_points': 15
        }
        
        # Load available data
        schools = self.load_schools_data()
        libraries = self.load_libraries_data()
        medical_facilities = self.load_medical_data()
        transit_stops = self.load_transit_data()
        grocery_stores = self.load_grocery_data()
        
        # Combine all amenities
        all_amenities = []
        
        for df, category in [(schools, 'schools'), (libraries, 'library'), 
                           (medical_facilities, 'medical'), (transit_stops, 'transit'),
                           (grocery_stores, 'grocery')]:
            if not df.empty:
                df_copy = df.copy()
                df_copy['distance_miles'] = df_copy.apply(
                    lambda row: self.haversine_distance(site_lat, site_lng, row['latitude'], row['longitude']),
                    axis=1
                )
                all_amenities.append(df_copy)
        
        if not all_amenities:
            print("No amenity data loaded")
            return results
        
        all_amenities_df = pd.concat(all_amenities, ignore_index=True)
        
        # Calculate scores
        total_points = 0
        
        # Opportunity Area (if applicable)
        if opportunity_area_status in ['Highest Resource', 'High Resource']:
            opportunity_points = 8
            total_points += opportunity_points
            results['scoring_summary']['opportunity_area'] = opportunity_points
            results['amenities_found']['opportunity_area'] = {
                'status': opportunity_area_status,
                'points': opportunity_points
            }
        
        # Transit scoring
        transit_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'transit']
        if not transit_nearby.empty:
            transit_within_half = transit_nearby[transit_nearby['distance_miles'] <= 0.5]
            transit_within_third = transit_nearby[transit_nearby['distance_miles'] <= 0.33]
            
            if not transit_within_third.empty:
                transit_points = 4  # Basic transit
                total_points += transit_points
                results['scoring_summary']['transit'] = transit_points
                results['amenities_found']['transit'] = {
                    'count_0.33mi': len(transit_within_third),
                    'count_0.5mi': len(transit_within_half),
                    'closest': transit_nearby.iloc[0]['name'] if not transit_nearby.empty else None,
                    'closest_distance': round(transit_nearby.iloc[0]['distance_miles'], 2) if not transit_nearby.empty else None
                }
        
        # Schools scoring (if qualifying development)
        if qualifying_development:
            schools_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'schools']
            if not schools_nearby.empty:
                # Elementary schools within 0.75 miles
                elem_schools = schools_nearby[schools_nearby['distance_miles'] <= 0.75]
                # High schools within 1.5 miles  
                high_schools = schools_nearby[schools_nearby['distance_miles'] <= 1.5]
                
                school_points = 0
                if not elem_schools.empty:
                    school_points += 2
                if not high_schools.empty:
                    school_points += 2
                
                if school_points > 0:
                    total_points += school_points
                    results['scoring_summary']['schools'] = school_points
                    results['amenities_found']['schools'] = {
                        'elementary_within_0.75mi': len(elem_schools),
                        'high_within_1.5mi': len(high_schools),
                        'total_nearby': len(schools_nearby[schools_nearby['distance_miles'] <= 2.0])
                    }
        
        # Libraries scoring
        libraries_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'library']
        if not libraries_nearby.empty:
            lib_within_half = libraries_nearby[libraries_nearby['distance_miles'] <= 0.5]
            lib_within_one = libraries_nearby[libraries_nearby['distance_miles'] <= 1.0]
            
            library_points = 0
            if not lib_within_half.empty:
                library_points = 3
            elif not lib_within_one.empty:
                library_points = 2
            
            if library_points > 0:
                total_points += library_points
                results['scoring_summary']['library'] = library_points
                results['amenities_found']['library'] = {
                    'within_0.5mi': len(lib_within_half),
                    'within_1.0mi': len(lib_within_one),
                    'closest': libraries_nearby.iloc[0]['name'] if not libraries_nearby.empty else None
                }
        
        # Grocery scoring
        grocery_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'grocery']
        if not grocery_nearby.empty:
            grocery_within_half = grocery_nearby[grocery_nearby['distance_miles'] <= 0.5]
            grocery_within_one = grocery_nearby[grocery_nearby['distance_miles'] <= 1.0]
            
            grocery_points = 0
            if not grocery_within_half.empty:
                grocery_points = 4  # Assume neighborhood grocery
            elif not grocery_within_one.empty:
                grocery_points = 3
            
            if grocery_points > 0:
                total_points += grocery_points
                results['scoring_summary']['grocery'] = grocery_points
                results['amenities_found']['grocery'] = {
                    'within_0.5mi': len(grocery_within_half),
                    'within_1.0mi': len(grocery_within_one),
                    'closest': grocery_nearby.iloc[0]['name'] if not grocery_nearby.empty else None
                }
        
        # Medical scoring
        medical_nearby = all_amenities_df[all_amenities_df['amenity_category'] == 'medical']
        if not medical_nearby.empty:
            med_within_half = medical_nearby[medical_nearby['distance_miles'] <= 0.5]
            med_within_one = medical_nearby[medical_nearby['distance_miles'] <= 1.0]
            
            medical_points = 0
            if not med_within_half.empty:
                medical_points = 3
            elif not med_within_one.empty:
                medical_points = 2
            
            if medical_points > 0:
                total_points += medical_points
                results['scoring_summary']['medical'] = medical_points
                results['amenities_found']['medical'] = {
                    'within_0.5mi': len(med_within_half),
                    'within_1.0mi': len(med_within_one),
                    'closest': medical_nearby.iloc[0]['name'] if not medical_nearby.empty else None
                }
        
        results['total_points'] = min(total_points, 15)  # CTCAC maximum
        results['all_amenities'] = all_amenities_df
        
        return results
    
    def create_amenity_map(self, site_lat, site_lng, site_name="Development Site",
                          is_rural=False, project_type='family', qualifying_development=False,
                          new_construction=False, large_family=False, 
                          opportunity_area_status=None):
        """Create interactive map with amenities"""
        
        # Get scoring results
        results = self.calculate_amenity_scores(
            site_lat, site_lng, is_rural, project_type, 
            qualifying_development, new_construction, large_family, opportunity_area_status
        )
        
        # Create map
        m = folium.Map(location=[site_lat, site_lng], zoom_start=14)
        
        # Add site marker
        folium.Marker(
            [site_lat, site_lng],
            popup=f"<b>{site_name}</b><br>Development Site",
            icon=folium.Icon(color='red', icon='home')
        ).add_to(m)
        
        # Add distance circles
        for radius in [0.25, 0.5, 0.75, 1.0]:
            folium.Circle(
                location=[site_lat, site_lng],
                radius=radius * 1609.34,  # Convert miles to meters
                color='blue',
                weight=1,
                opacity=0.3,
                fill=False,
                popup=f"{radius} mile radius"
            ).add_to(m)
        
        # Add amenities
        if 'all_amenities' in results and not results['all_amenities'].empty:
            for _, amenity in results['all_amenities'].iterrows():
                if amenity['distance_miles'] <= 2.0:  # Only show amenities within 2 miles
                    color = self.amenity_colors.get(amenity['amenity_category'], 'gray')
                    
                    folium.Marker(
                        [amenity['latitude'], amenity['longitude']],
                        popup=f"<b>{amenity['name']}</b><br>"
                              f"Category: {amenity['amenity_category']}<br>"
                              f"Distance: {amenity['distance_miles']:.2f} miles",
                        icon=folium.Icon(color=color, icon='star')
                    ).add_to(m)
        
        # Add scoring summary
        scoring_html = f"""
        <div style='position: fixed; top: 10px; right: 10px; width: 300px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px'>
        <p><b>CTCAC Amenity Scoring</b></p>
        <p><b>Total Score: {results['total_points']}/15 points</b></p>
        """
        
        for category, points in results['scoring_summary'].items():
            scoring_html += f"<p>{category.replace('_', ' ').title()}: {points} pts</p>"
        
        scoring_html += "</div>"
        
        m.get_root().html.add_child(folium.Element(scoring_html))
        
        return m, results

def analyze_rocklin_with_fixed_mapper():
    """Analyze Rocklin site with fixed mapper"""
    
    mapper = CTCACAmenityMapperFixed()
    
    # Rocklin site details
    site_lat = 38.795282
    site_lng = -121.233117
    site_name = "Rocklin - Pacific & Midas"
    
    print("🗺️ Creating CTCAC Amenity Map for Rocklin Site")
    print("=" * 60)
    
    # Create map and get results
    map_obj, results = mapper.create_amenity_map(
        site_lat=site_lat,
        site_lng=site_lng,
        site_name=site_name,
        is_rural=False,
        project_type='family',
        qualifying_development=True,
        new_construction=True,
        large_family=True,
        opportunity_area_status='Highest Resource'
    )
    
    # Save map
    output_file = "rocklin_ctcac_amenity_analysis.html"
    map_obj.save(output_file)
    print(f"✅ Map saved to: {output_file}")
    
    # Display results
    print(f"\n📊 CTCAC AMENITY SCORING RESULTS")
    print("=" * 50)
    print(f"Total Score: {results['total_points']}/15 points")
    print()
    
    for category, points in results['scoring_summary'].items():
        print(f"{category.replace('_', ' ').title()}: {points} points")
    
    print(f"\n🎯 AMENITIES FOUND:")
    for category, details in results['amenities_found'].items():
        print(f"\n{category.replace('_', ' ').title()}:")
        if isinstance(details, dict):
            for key, value in details.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        else:
            print(f"  {details}")
    
    return results

if __name__ == "__main__":
    analyze_rocklin_with_fixed_mapper()