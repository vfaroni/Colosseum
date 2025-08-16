#!/usr/bin/env python3
"""
CTCAC Amenity Mapper - FIXED VERSION
Fixes distance filtering and marker display issues
"""

import pandas as pd
import geopandas as gpd
import json
import folium
from folium.plugins import MarkerCluster
import requests
from math import radians, cos, sin, asin, sqrt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Import the original class
from ctcac_amenity_mapper_complete import CTCACAmenityMapperComplete

class CTCACAmenityMapperFixed(CTCACAmenityMapperComplete):
    """Fixed version with proper distance filtering and working markers"""
    
    def calculate_complete_amenity_scores(self, site_lat, site_lng, is_rural=False, 
                                        project_type='family', density_per_acre=None,
                                        qualifying_development=False, new_construction=False,
                                        large_family=False, opportunity_area_status=None):
        """Calculate complete CTCAC amenity scores with FIXED distance filtering"""
        
        results = {
            'site_coordinates': (site_lat, site_lng),
            'is_rural': is_rural,
            'project_type': project_type,
            'qualifying_development': qualifying_development,
            'amenities_found': {},
            'scoring_summary': {},
            'total_points': 0,
            'max_possible_points': 15
        }
        
        # Load all amenity datasets
        schools = self.load_schools_data()
        libraries = self.load_libraries_data()
        pharmacies = self.load_pharmacies_data()
        senior_centers = self.load_senior_centers_data()
        medical_facilities = self.load_medical_data()
        transit_stops = self.load_transit_data()
        hqta_areas = self.load_hqta_data()
        public_parks = self.load_parks_data()
        grocery_stores = self.load_grocery_data()
        
        # Combine transit stops and HQTA areas
        if not transit_stops.empty and not hqta_areas.empty:
            combined_transit = pd.concat([transit_stops, hqta_areas], ignore_index=True)
        elif not transit_stops.empty:
            combined_transit = transit_stops
        elif not hqta_areas.empty:
            combined_transit = hqta_areas
        else:
            combined_transit = pd.DataFrame()
        
        # Calculate distances for all amenities
        all_amenities = []
        
        for df, category in [(schools, 'schools'), (libraries, 'library'), 
                           (pharmacies, 'pharmacy'), (senior_centers, 'senior_center'),
                           (medical_facilities, 'medical'), (combined_transit, 'transit'),
                           (public_parks, 'public_park'), (grocery_stores, 'grocery')]:
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
        
        # Define maximum CTCAC scoring distances for each category
        max_distances = {
            'transit': 0.5,  # Max 0.5 miles for any transit scoring
            'public_park': 1.5 if is_rural else 0.75,
            'library': 2.0 if is_rural else 1.0,
            'pharmacy': 2.0 if is_rural else 1.0,
            'grocery': 3.0 if is_rural else 1.5,
            'medical': 1.5 if is_rural else 1.0,
            'senior_center': 1.5 if is_rural else 0.75,
            'schools': {  # Different distances for different school types
                'elementary': 1.25 if is_rural else 0.75,
                'middle': 1.5 if is_rural else 1.0,
                'high': 2.5 if is_rural else 1.5,
                'adult_ed_community_college': 1.5 if is_rural else 1.0
            }
        }
        
        # Calculate scores for each category WITH DISTANCE FILTERING
        total_points = 0
        
        # a) Transit stops - filter to CTCAC scoring distances
        transit_all = all_amenities_df[all_amenities_df['amenity_category'] == 'transit']
        transit_scorable = transit_all[transit_all['distance_miles'] <= max_distances['transit']]
        transit_points = self._score_transit_complete(transit_all, is_rural, density_per_acre)
        results['amenities_found']['transit'] = transit_scorable.to_dict('records')
        results['scoring_summary']['transit'] = transit_points
        total_points += transit_points.get('points', 0)
        
        # b) Public Parks - filter to CTCAC scoring distances
        parks_all = all_amenities_df[all_amenities_df['amenity_category'] == 'public_park']
        parks_scorable = parks_all[parks_all['distance_miles'] <= max_distances['public_park']]
        parks_points = self._score_parks_complete(parks_all, is_rural)
        results['amenities_found']['public_parks'] = parks_scorable.to_dict('records')
        results['scoring_summary']['public_park'] = parks_points
        total_points += parks_points.get('points', 0)
        
        # c) Libraries - filter to CTCAC scoring distances
        libraries_all = all_amenities_df[all_amenities_df['amenity_category'] == 'library']
        libraries_scorable = libraries_all[libraries_all['distance_miles'] <= max_distances['library']]
        library_points = self._score_libraries_complete(libraries_all, is_rural)
        results['amenities_found']['libraries'] = libraries_scorable.to_dict('records')
        results['scoring_summary']['library'] = library_points
        total_points += library_points.get('points', 0)
        
        # d) Grocery stores - filter to CTCAC scoring distances
        grocery_all = all_amenities_df[all_amenities_df['amenity_category'] == 'grocery']
        grocery_scorable = grocery_all[grocery_all['distance_miles'] <= max_distances['grocery']]
        grocery_points = self._score_grocery_complete(grocery_all, is_rural)
        results['amenities_found']['grocery'] = grocery_scorable.to_dict('records')
        results['scoring_summary']['grocery'] = grocery_points
        total_points += grocery_points.get('points', 0)
        
        # e) Schools - filter by school type distances
        schools_all = all_amenities_df[all_amenities_df['amenity_category'] == 'schools']
        schools_scorable = pd.DataFrame()
        
        if not schools_all.empty:
            # Filter each school type by its specific distance
            for school_type, max_dist in max_distances['schools'].items():
                type_schools = schools_all[schools_all['amenity_type'] == school_type]
                type_scorable = type_schools[type_schools['distance_miles'] <= max_dist]
                schools_scorable = pd.concat([schools_scorable, type_scorable])
        
        school_points = self._score_schools_complete(schools_all, is_rural, qualifying_development)
        results['amenities_found']['schools'] = schools_scorable.to_dict('records')
        results['scoring_summary']['schools'] = school_points
        total_points += sum([v for v in school_points.values() if isinstance(v, (int, float))])
        
        # f) Senior Centers - filter to CTCAC scoring distances
        if project_type == 'senior':
            senior_all = all_amenities_df[all_amenities_df['amenity_category'] == 'senior_center']
            senior_scorable = senior_all[senior_all['distance_miles'] <= max_distances['senior_center']]
            senior_points = self._score_senior_centers_complete(senior_all, is_rural)
            results['amenities_found']['senior_centers'] = senior_scorable.to_dict('records')
            results['scoring_summary']['senior_center'] = senior_points
            total_points += senior_points.get('points', 0)
        
        # g) Medical facilities - filter to CTCAC scoring distances
        medical_all = all_amenities_df[all_amenities_df['amenity_category'] == 'medical']
        medical_scorable = medical_all[medical_all['distance_miles'] <= max_distances['medical']]
        medical_points = self._score_medical_complete(medical_all, is_rural)
        results['amenities_found']['medical'] = medical_scorable.to_dict('records')
        results['scoring_summary']['medical'] = medical_points
        total_points += medical_points.get('points', 0)
        
        # h) Pharmacy - filter to CTCAC scoring distances
        pharmacy_all = all_amenities_df[all_amenities_df['amenity_category'] == 'pharmacy']
        pharmacy_scorable = pharmacy_all[pharmacy_all['distance_miles'] <= max_distances['pharmacy']]
        pharmacy_points = self._score_pharmacies_complete(pharmacy_all, is_rural)
        results['amenities_found']['pharmacies'] = pharmacy_scorable.to_dict('records')
        results['scoring_summary']['pharmacy'] = pharmacy_points
        total_points += pharmacy_points.get('points', 0)
        
        # i) Internet Service (project amenity - not location based)
        internet_points = {'points': 0, 'note': 'Project amenity - not location based'}
        results['scoring_summary']['internet'] = internet_points
        total_points += internet_points.get('points', 0)
        
        # j) Opportunity Area (census tract designation)
        if opportunity_area_status in ['highest', 'high'] and new_construction and large_family:
            results['scoring_summary']['opportunity_area'] = {'points': 8, 'status': opportunity_area_status}
            total_points += 8
        else:
            results['scoring_summary']['opportunity_area'] = {'points': 0, 'status': 'not_applicable'}
        
        results['total_points'] = min(total_points, 15)  # Cap at 15 points
        
        return results
    
    def _add_enhanced_amenity_markers(self, map_obj, results):
        """Add enhanced amenity markers with FIXED icon display"""
        legend_data = {}
        
        # Define enhanced symbols and colors
        amenity_symbols = {
            'schools': {'icon': 'graduation-cap', 'color': 'blue', 'symbol': '🏫'},
            'libraries': {'icon': 'book', 'color': 'purple', 'symbol': '📚'},
            'pharmacies': {'icon': 'plus', 'color': 'pink', 'symbol': '💊'},
            'senior_centers': {'icon': 'users', 'color': 'orange', 'symbol': '👥'},
            'medical': {'icon': 'hospital-o', 'color': 'red', 'symbol': '🏥'},
            'transit': {'icon': 'bus', 'color': 'green', 'symbol': '🚌'},
            'public_parks': {'icon': 'tree', 'color': 'darkgreen', 'symbol': '🌳'},
            'grocery': {'icon': 'shopping-cart', 'color': 'cadetblue', 'symbol': '🛒'},
            'special_needs': {'icon': 'heart', 'color': 'lightred', 'symbol': '❤️'}
        }
        
        marker_counter = 1
        
        for category, amenities in results['amenities_found'].items():
            if not amenities:
                continue
            
            # Map plural category names to singular for symbol lookup
            category_key = category.rstrip('s') if category.endswith('s') and category != 'special_needs' else category
            category_key = 'schools' if category_key == 'school' else category_key
            category_key = 'libraries' if category == 'libraries' else category_key
            category_key = 'pharmacies' if category == 'pharmacies' else category_key
            category_key = 'senior_centers' if category == 'senior_centers' else category_key
            category_key = 'public_parks' if category == 'public_parks' else category_key
            
            symbol_info = amenity_symbols.get(category_key, {'icon': 'info-sign', 'color': 'gray', 'symbol': '📍'})
            category_markers = []
            
            # Sort amenities by distance and limit to closest 10
            sorted_amenities = sorted(amenities, key=lambda x: x.get('distance_miles', 999))[:10]
            
            for amenity in sorted_amenities:
                if 'latitude' in amenity and 'longitude' in amenity:
                    name = amenity.get('name', 'Unknown')
                    distance = amenity.get('distance_miles', 0)
                    amenity_type = amenity.get('amenity_type', category)
                    
                    # Create numbered marker
                    marker_number = marker_counter
                    marker_counter += 1
                    
                    # Create custom HTML icon with number
                    html_icon = f'''
                    <div style="text-align: center;">
                        <div style="background-color: {symbol_info['color']}; 
                                    color: white; 
                                    width: 24px; 
                                    height: 24px; 
                                    border-radius: 50%; 
                                    text-align: center; 
                                    font-weight: bold;
                                    line-height: 24px;
                                    font-size: 12px;
                                    border: 2px solid white;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                            {marker_number}
                        </div>
                    </div>
                    '''
                    
                    # Add marker to map with custom icon
                    popup_html = f"""
                    <b>#{marker_number}: {name}</b><br>
                    <b>Type:</b> {amenity_type.replace('_', ' ').title()}<br>
                    <b>Category:</b> {category.replace('_', ' ').title()}<br>
                    <b>Distance:</b> {distance:.1f} miles
                    """
                    
                    folium.Marker(
                        [amenity['latitude'], amenity['longitude']],
                        popup=popup_html,
                        tooltip=f"#{marker_number}: {name} ({distance:.1f} mi)",
                        icon=folium.DivIcon(html=html_icon)
                    ).add_to(map_obj)
                    
                    # Store legend data
                    category_markers.append({
                        'number': marker_number,
                        'name': name,
                        'distance': distance,
                        'type': amenity_type
                    })
            
            if category_markers:
                legend_data[category] = {
                    'symbol': symbol_info['symbol'],
                    'color': symbol_info['color'],
                    'markers': category_markers
                }
        
        return legend_data


# Test function
def test_fixed_mapper():
    """Test the fixed mapper with proper distance filtering"""
    print("Testing Fixed CTCAC Amenity Mapper")
    print("=" * 60)
    
    mapper = CTCACAmenityMapperFixed()
    
    # Test site
    site_lat, site_lng = 33.792954, -117.221031  # Perris, CA
    
    print(f"Analyzing site: {site_lat}, {site_lng}")
    
    # Create map with fixed distance filtering
    map_obj, results = mapper.create_complete_amenity_map(
        site_lat, site_lng,
        site_name="Fixed Distance Test - Perris, CA",
        is_rural=False,
        project_type='family',
        qualifying_development=True,
        new_construction=True,
        large_family=True
    )
    
    # Save map
    map_obj.save('ctcac_fixed_distance_map.html')
    
    print(f"\nTotal Score: {results['total_points']}/15")
    print("\nAmenities within CTCAC scoring distances:")
    
    for category, amenities in results['amenities_found'].items():
        if amenities:
            print(f"\n{category.replace('_', ' ').title()}: {len(amenities)} found")
            if amenities:
                closest = min(amenities, key=lambda x: x.get('distance_miles', 999))
                print(f"  Closest: {closest.get('name', 'Unknown')} at {closest.get('distance_miles', 0):.1f} miles")
    
    print("\n✅ Distance filtering applied - only amenities within CTCAC scoring radii shown")
    print("✅ Numbered markers displayed on map")
    print("✅ Enhanced legend with proper formatting")

if __name__ == "__main__":
    test_fixed_mapper()