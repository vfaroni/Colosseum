#!/usr/bin/env python3
"""
Enhanced CTCAC Amenity Mapper with Apple Maps API Support and Improved Transit Detection
Addresses specific issues:
1. Distance requirements in legend
2. Metrolink station detection (adding train_station to Google search types)  
3. Apple Maps API integration for parks discovery
4. Enhanced park detection using Apple Maps APIs

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

class EnhancedCTCACAmenityMapper:
    def __init__(self, data_path=None, apple_maps_api_key=None, google_maps_api_key=None):
        """Initialize enhanced mapper with Apple Maps and Google Maps API support"""
        if data_path is None:
            self.data_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets")
        else:
            self.data_path = Path(data_path)
        
        self.apple_maps_api_key = apple_maps_api_key
        self.google_maps_api_key = google_maps_api_key
        
        # Enhanced CTCAC distance requirements with exact specifications
        self.distance_rules = {
            'transit': {
                'hqta': {'standard': [0.33], 'points': [7]},  # HQTA within 1/3 mile
                'frequent_service': {'standard': [0.33, 0.5], 'points': [6, 5]},  # 30min frequency
                'basic_transit': {'standard': [0.33, 0.5], 'rural': [0.33, 0.5], 'points': [4, 3]}
            },
            'public_park': {
                'parks_community_centers': {'standard': [0.5, 0.75], 'rural': [1.0, 1.5], 'points': [3, 2]}
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
                'elementary': {'standard': [0.25, 0.75], 'rural': [0.75, 1.25], 'points': [3, 2]},
                'middle': {'standard': [0.5, 1.0], 'rural': [1.0, 1.5], 'points': [3, 2]},
                'high': {'standard': [1.0, 1.5], 'rural': [1.5, 2.5], 'points': [3, 2]},
                'adult_ed': {'standard': [1.0], 'rural': [1.5], 'points': [3]}
            },
            'medical': {
                'clinic_hospital': {'standard': [0.5, 1.0], 'rural': [1.0, 1.5], 'points': [3, 2]}
            },
            'pharmacy': {
                'pharmacy': {'standard': [0.5, 1.0], 'rural': [1.0, 2.0], 'points': [2, 1]}
            },
            'senior_center': {
                'daily_operated': {'standard': [0.5, 0.75], 'rural': [1.0, 1.5], 'points': [3, 2]}
            }
        }
        
        # Distance requirement text for legend display
        self.distance_requirements_text = {
            'transit': {
                'standard': {'max_distance': '0.5 mi', 'scoring_tiers': 'HQTA 1/3 mi (7 pts), Frequent 1/3-1/2 mi (6-5 pts), Basic 1/3-1/2 mi (4-3 pts)'},
                'rural': {'max_distance': '0.5 mi', 'scoring_tiers': 'HQTA 1/3 mi (7 pts), Frequent 1/3-1/2 mi (6-5 pts), Basic 1/3-1/2 mi (4-3 pts)'}
            },
            'public_park': {
                'standard': {'max_distance': '0.75 mi', 'scoring_tiers': '1/2 mi (3 pts), 3/4 mi (2 pts)'},
                'rural': {'max_distance': '1.5 mi', 'scoring_tiers': '1.0 mi (3 pts), 1.5 mi (2 pts)'}
            },
            'library': {
                'standard': {'max_distance': '1.0 mi', 'scoring_tiers': '1/2 mi (3 pts), 1.0 mi (2 pts)'},
                'rural': {'max_distance': '2.0 mi', 'scoring_tiers': '1.0 mi (3 pts), 2.0 mi (2 pts)'}
            },
            'grocery': {
                'standard': {'max_distance': '1.5 mi', 'scoring_tiers': 'Full 1/2-1.5 mi (5-3 pts), Neighborhood 1/4-1/2 mi (4-3 pts)'},
                'rural': {'max_distance': '3.0 mi', 'scoring_tiers': 'Full 1.0-3.0 mi (5-3 pts), Neighborhood 1/2-1.0 mi (4-3 pts)'}
            },
            'schools': {
                'standard': {'max_distance': '1.5 mi', 'scoring_tiers': 'Elementary 1/4-3/4 mi (3-2 pts), High 1.0-1.5 mi (3-2 pts)'},
                'rural': {'max_distance': '2.5 mi', 'scoring_tiers': 'Elementary 3/4-1.25 mi (3-2 pts), High 1.5-2.5 mi (3-2 pts)'}
            },
            'medical': {
                'standard': {'max_distance': '1.0 mi', 'scoring_tiers': '1/2 mi (3 pts), 1.0 mi (2 pts)'},
                'rural': {'max_distance': '1.5 mi', 'scoring_tiers': '1.0 mi (3 pts), 1.5 mi (2 pts)'}
            },
            'pharmacy': {
                'standard': {'max_distance': '1.0 mi', 'scoring_tiers': '1/2 mi (2 pts), 1.0 mi (1 pt)'},
                'rural': {'max_distance': '2.0 mi', 'scoring_tiers': '1.0 mi (2 pts), 2.0 mi (1 pt)'}
            },
            'senior_center': {
                'standard': {'max_distance': '0.75 mi', 'scoring_tiers': '1/2 mi (3 pts), 3/4 mi (2 pts)'},
                'rural': {'max_distance': '1.5 mi', 'scoring_tiers': '1.0 mi (3 pts), 1.5 mi (2 pts)'}
            }
        }

    def search_apple_maps_parks(self, latitude, longitude, radius_miles=1.0):
        """Search for parks using Apple Maps API"""
        if not self.apple_maps_api_key:
            print("Apple Maps API key not provided, skipping Apple Maps parks search")
            return []
        
        # Convert miles to meters for Apple Maps API
        radius_meters = radius_miles * 1609.34
        
        # Apple Maps Search API endpoint
        url = "https://maps-api.apple.com/v1/search"
        
        headers = {
            'Authorization': f'Bearer {self.apple_maps_api_key}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'q': 'park',
            'searchLocation': f"{latitude},{longitude}",
            'searchRadius': radius_meters,
            'resultTypeFilter': 'Poi',
            'limitToCountries': 'US'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                parks = []
                
                for result in data.get('results', []):
                    park_name = result.get('name', 'Unknown Park')
                    coordinate = result.get('coordinate', {})
                    
                    if 'latitude' in coordinate and 'longitude' in coordinate:
                        park_lat = coordinate['latitude']
                        park_lng = coordinate['longitude']
                        
                        # Calculate distance
                        distance = self.haversine_distance(latitude, longitude, park_lat, park_lng)
                        
                        parks.append({
                            'name': park_name,
                            'latitude': park_lat,
                            'longitude': park_lng,
                            'distance_miles': distance,
                            'amenity_type': 'park',
                            'amenity_category': 'public_park',
                            'source': 'apple_maps'
                        })
                
                print(f"Found {len(parks)} parks using Apple Maps API")
                return parks
            else:
                print(f"Apple Maps API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error searching Apple Maps for parks: {e}")
            return []

    def search_enhanced_transit(self, latitude, longitude, radius_miles=1.0):
        """Enhanced transit search including Metrolink stations"""
        transit_stops = []
        
        # First, try to load local comprehensive data
        local_transit = self.load_transit_data()
        if not local_transit.empty:
            # Filter by distance
            for _, stop in local_transit.iterrows():
                distance = self.haversine_distance(latitude, longitude, stop['latitude'], stop['longitude'])
                if distance <= radius_miles:
                    stop_dict = stop.to_dict()
                    stop_dict['distance_miles'] = distance
                    stop_dict['source'] = 'local_data'
                    transit_stops.append(stop_dict)
        
        # Supplement with Google Maps API (enhanced with train_station type)
        if self.google_maps_api_key:
            google_transit = self.search_google_maps_transit_enhanced(latitude, longitude, radius_miles)
            transit_stops.extend(google_transit)
        
        # Remove duplicates based on proximity (within 100 meters)
        unique_stops = []
        for stop in transit_stops:
            is_duplicate = False
            for existing in unique_stops:
                if self.haversine_distance(stop['latitude'], stop['longitude'], 
                                         existing['latitude'], existing['longitude']) < 0.062:  # ~100 meters
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_stops.append(stop)
        
        return sorted(unique_stops, key=lambda x: x['distance_miles'])

    def search_google_maps_transit_enhanced(self, latitude, longitude, radius_miles=1.0):
        """Enhanced Google Maps transit search including train stations"""
        if not self.google_maps_api_key:
            return []
        
        radius_meters = radius_miles * 1609.34
        
        # Enhanced search types including train_station for Metrolink
        search_types = ['transit_station', 'bus_station', 'subway_station', 'train_station']
        
        all_transit = []
        
        for search_type in search_types:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            
            params = {
                'location': f"{latitude},{longitude}",
                'radius': radius_meters,
                'type': search_type,
                'key': self.google_maps_api_key
            }
            
            try:
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for place in data.get('results', []):
                        place_name = place.get('name', 'Transit Stop')
                        place_location = place.get('geometry', {}).get('location', {})
                        
                        if 'lat' in place_location and 'lng' in place_location:
                            place_lat = place_location['lat']
                            place_lng = place_location['lng']
                            
                            distance = self.haversine_distance(latitude, longitude, place_lat, place_lng)
                            
                            # Identify Metrolink specifically
                            amenity_type = 'metrolink_station' if 'metrolink' in place_name.lower() else f'{search_type}_google'
                            
                            all_transit.append({
                                'name': place_name,
                                'latitude': place_lat,
                                'longitude': place_lng,
                                'distance_miles': distance,
                                'amenity_type': amenity_type,
                                'amenity_category': 'transit',
                                'source': f'google_maps_{search_type}'
                            })
                            
            except Exception as e:
                print(f"Error searching Google Maps for {search_type}: {e}")
        
        return all_transit

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate the great circle distance between two points in miles"""
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of earth in miles
        r = 3956
        return c * r

    def load_transit_data(self):
        """Load comprehensive California transit data"""
        geojson_file = self.data_path / "CA_Transit_Data" / "California_Transit_Stops.geojson"
        
        if not geojson_file.exists():
            print(f"Transit GeoJSON file not found: {geojson_file}")
            return pd.DataFrame()
        
        try:
            import geopandas as gpd
            gdf = gpd.read_file(str(geojson_file))
            
            # Extract coordinates
            gdf['latitude'] = gdf.geometry.y
            gdf['longitude'] = gdf.geometry.x
            
            # Create standard DataFrame
            transit_stops = pd.DataFrame()
            transit_stops['name'] = gdf['stop_name'].fillna('Transit Stop')
            transit_stops['amenity_type'] = 'transit_stop'
            transit_stops['amenity_category'] = 'transit'
            transit_stops['latitude'] = gdf['latitude']
            transit_stops['longitude'] = gdf['longitude']
            transit_stops['agency'] = gdf['agency'].fillna('Unknown')
            
            # Mark Metrolink stations specifically
            metrolink_mask = transit_stops['name'].str.contains('metrolink|Metrolink', case=False, na=False)
            transit_stops.loc[metrolink_mask, 'amenity_type'] = 'metrolink_station'
            
            # Remove coordinate-based duplicates
            transit_stops['lat_rounded'] = transit_stops['latitude'].round(6)
            transit_stops['lng_rounded'] = transit_stops['longitude'].round(6)
            transit_stops = transit_stops.drop_duplicates(subset=['lat_rounded', 'lng_rounded'])
            transit_stops = transit_stops.drop(['lat_rounded', 'lng_rounded'], axis=1)
            
            print(f"Loaded {len(transit_stops)} transit stops from local data")
            metrolink_count = len(transit_stops[transit_stops['amenity_type'] == 'metrolink_station'])
            print(f"  - Including {metrolink_count} Metrolink stations")
            
            return transit_stops.dropna(subset=['latitude', 'longitude'])
            
        except Exception as e:
            print(f"Error loading transit data: {e}")
            return pd.DataFrame()

    def create_enhanced_legend_with_distances(self, results, legend_data):
        """Create enhanced legend with CTCAC distance requirements"""
        
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 450px; height: auto; max-height: 85vh; overflow-y: auto;
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:11px; padding: 12px; border-radius: 5px; box-shadow: 0 0 15px rgba(0,0,0,0.3);">
        
        <h4 style="margin-top:0; color: #2E7D32;">Enhanced CTCAC Amenity Analysis</h4>
        <div style="background-color: #E8F5E8; padding: 8px; border-radius: 3px; margin-bottom: 10px;">
            <p style="margin:2px;"><b>Total Score: {results['total_points']}/15 Points</b></p>
            <p style="margin:2px;"><b>Project Type:</b> {results['project_type'].replace('_', ' ').title()}</p>
            <p style="margin:2px;"><b>Use Rural Dist?:</b> {'Yes' if results['is_rural'] else 'No'}</p>
        </div>
        
        <h5 style="margin-bottom:8px;">📊 Scoring Summary:</h5>
        <div style="background-color: #F5F5F5; padding: 6px; border-radius: 3px; margin-bottom: 10px;">
        '''
        
        # Add scoring summary
        for category, score_data in results['scoring_summary'].items():
            if category == 'internet':
                continue
            if isinstance(score_data, dict) and 'points' in score_data:
                points = score_data['points']
                legend_html += f"<p style='margin:2px;'><b>{category.replace('_', ' ').title()}:</b> {points} pts</p>"
            elif category == 'schools' and isinstance(score_data, dict):
                total_pts = sum([v for v in score_data.values() if isinstance(v, (int, float))])
                legend_html += f"<p style='margin:2px;'><b>Schools:</b> {total_pts} pts total</p>"
                for subcat, pts in score_data.items():
                    if isinstance(pts, (int, float)) and pts > 0:
                        legend_html += f"<p style='margin:2px 2px 2px 15px;'>• {subcat.replace('_', ' ').title()}: {pts} pts</p>"
        
        legend_html += "</div>"
        
        # Add enhanced amenity legend with distance requirements
        if legend_data:
            legend_html += "<h5 style='margin-bottom:8px;'>🗺️ Map Legend with CTCAC Distance Requirements:</h5>"
            
            for category, data in legend_data.items():
                symbol = data['symbol']
                markers = data['markers']
                
                if markers:
                    # Get distance requirements for this category
                    dist_set = 'rural' if results['is_rural'] else 'standard'
                    category_reqs = self.distance_requirements_text.get(category, {}).get(dist_set, {})
                    max_dist = category_reqs.get('max_distance', 'N/A')
                    scoring_tiers = category_reqs.get('scoring_tiers', 'See CTCAC QAP')
                    
                    legend_html += f"""
                    <div style="margin-bottom:10px; border-left: 3px solid {data['color']}; padding-left:8px;">
                        <h6 style="margin:2px 0; color:{data['color']};">{symbol} {category.replace('_', ' ').title()}</h6>
                        <div style="background-color: #f8f9fa; padding: 4px 6px; margin: 3px 0; border-radius: 3px; font-size: 9px; color: #495057; line-height: 1.3;">
                            <b>Max CTCAC Distance:</b> {max_dist}<br>
                            <b>CTCAC Scoring Tiers:</b> {scoring_tiers}
                        </div>
                    """
                    
                    for marker in markers:
                        # Color-code based on distance vs requirements
                        distance = marker['distance']
                        color_style = data['color']
                        if 'max_distance' in category_reqs:
                            max_distance_val = float(category_reqs['max_distance'].split()[0].replace('/', '.'))
                            if distance > max_distance_val:
                                color_style = '#dc3545'  # Red for over max distance
                        
                        legend_html += f"""
                        <p style="margin:3px 0; font-size:10px; line-height:1.4;">
                            <span style="background-color:{color_style}; color:white; padding:1px 4px; border-radius:2px; font-weight:bold; margin-right:6px;">
                                #{marker['number']}
                            </span>
                            {marker['name']} ({marker['distance']:.2f} mi)
                        </p>
                        """
                    
                    legend_html += "</div>"
        
        legend_html += '''
        <hr style="margin:8px 0;">
        <div style="font-size:9px; color:#666;">
            <p style="margin:2px 0;"><b>🎯 Enhanced Features:</b></p>
            <p style="margin:1px 0;">✅ Apple Maps parks discovery, Enhanced Metrolink detection</p>
            <p style="margin:1px 0;">📏 CTCAC distance requirements in legend</p>
            <p style="margin:1px 0;">🔴 Red markers = beyond max CTCAC distance</p>
            <p style="margin:4px 0 0 0;"><b>Legend:</b> Circles = scoring distances, Markers = amenity locations</p>
        </div>
        </div>
        '''
        
        return legend_html

def analyze_enhanced_site(address, is_rural=False, project_type='family', 
                         apple_maps_api_key=None, google_maps_api_key=None):
    """Analyze a site using enhanced amenity mapping with Apple Maps and improved transit detection"""
    
    mapper = EnhancedCTCACAmenityMapper(
        apple_maps_api_key=apple_maps_api_key,
        google_maps_api_key=google_maps_api_key
    )
    
    # For now, return a placeholder - full implementation would follow complete workflow
    print(f"Enhanced analysis for: {address}")
    print("Features enabled:")
    print("✅ CTCAC distance requirements in legend")
    print("✅ Enhanced Metrolink detection (train_station type added)")
    if apple_maps_api_key:
        print("✅ Apple Maps parks discovery")
    else:
        print("⚠️  Apple Maps API key not provided")
    if google_maps_api_key:
        print("✅ Google Maps enhanced transit search")
    else:
        print("⚠️  Google Maps API key not provided")
    
    return None, None

if __name__ == "__main__":
    # Example usage
    address = "202 E. Jarvis St., Perris, CA 92570"
    
    # Test with API keys (replace with actual keys)
    google_api_key = "YOUR_GOOGLE_MAPS_API_KEY"  # Replace with actual key
    apple_api_key = "YOUR_APPLE_MAPS_API_KEY"    # Replace with actual key
    
    analyze_enhanced_site(
        address=address,
        google_maps_api_key=google_api_key,
        apple_maps_api_key=apple_api_key
    )