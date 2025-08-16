"""
Simplified Texas Proximity Analyzer
- Uses Texas public schools dataset
- Reports only distances in miles (no scoring)
- Better filtering for hospitals, pharmacies, grocery stores, and transit
"""

import pandas as pd
import numpy as np
import googlemaps
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
from pathlib import Path
import time
import logging
from geopy.distance import geodesic

class TexasProximityAnalyzerSimplified:
    """
    Simplified proximity analyzer that reports distances only
    """
    
    def __init__(self, google_maps_api_key: str, 
                 schools_file: str = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/TX_Public_Schools/Schools_2024_to_2025.csv",
                 cache_dir: Optional[str] = None):
        """
        Initialize the simplified analyzer
        
        Args:
            google_maps_api_key: Google Maps API key
            schools_file: Path to Texas public schools CSV
            cache_dir: Directory for caching results
        """
        self.gmaps = googlemaps.Client(key=google_maps_api_key)
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./proximity_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load Texas public schools data
        self.schools_data = self.load_schools_data(schools_file)
        
        # Define search parameters for Google Maps amenities
        self.amenity_configs = {
            'grocery_store': {
                'search_queries': [
                    'HEB grocery store',
                    'Kroger supermarket', 
                    'Walmart Supercenter grocery',
                    'Whole Foods Market',
                    'Albertsons supermarket',
                    'Tom Thumb grocery',
                    'Randalls supermarket',
                    'Fiesta Mart',
                    'grocery store -dollar -general -tree -family'
                ],
                'types': ['grocery_or_supermarket', 'supermarket'],
                'radius': 3218,  # 2 miles in meters
                'exclude_names': ['Dollar General', 'Dollar Tree', 'Family Dollar', 'CVS', 'Walgreens']
            },
            'transit_stop': {
                'search_queries': [
                    'bus stop',
                    'metro station',
                    'dart station',
                    'transit center',
                    'park and ride',
                    'light rail station'
                ],
                'types': ['transit_station', 'bus_station', 'subway_station', 'light_rail_station'],
                'radius': 1609,  # 1 mile in meters
                'exclude_names': []
            },
            'pharmacy': {
                'search_queries': [
                    'CVS pharmacy',
                    'Walgreens pharmacy',
                    'HEB pharmacy',
                    'Walmart pharmacy',
                    'Kroger pharmacy',
                    'Costco pharmacy'
                ],
                'types': ['pharmacy', 'drugstore'],
                'radius': 3218,  # 2 miles in meters
                'exclude_names': ['Dollar General', 'Dollar Tree', 'Family Dollar', '99 Cents', 'Discount']
            },
            'hospital': {
                'search_queries': [
                    'hospital emergency room',
                    'emergency hospital',
                    'medical center emergency',
                    'hospital ER'
                ],
                'types': ['hospital'],
                'radius': 8047,  # 5 miles in meters
                'exclude_names': ['Clinic', 'Urgent Care', 'Surgery Center', 'Plastic', 'Cosmetic', 'Dental', 'Eye', 'Veterinary']
            },
            'park': {
                'search_queries': [
                    'public park',
                    'city park',
                    'county park',
                    'state park',
                    'recreation center'
                ],
                'types': ['park'],
                'radius': 1609,  # 1 mile in meters
                'exclude_names': ['RV Park', 'Trailer Park', 'Mobile Home Park']
            }
        }
    
    def load_schools_data(self, schools_file: str) -> pd.DataFrame:
        """Load and prepare Texas public schools data"""
        try:
            print(f"Loading Texas public schools data...")
            df = pd.read_csv(schools_file, encoding='utf-8-sig')
            
            # Filter for active schools only
            df = df[df['USER_School_Status'] == 'Active']
            
            # Extract relevant columns
            schools_df = pd.DataFrame({
                'name': df['USER_School_Name'],
                'type': df['School_Type'],
                'grade_range': df['USER_Grade_Range'],
                'address': df['USER_School_Street_Address'],
                'city': df['USER_School_City'],
                'zip': df['USER_School_Zip'],
                'lat': pd.to_numeric(df['Y'], errors='coerce'),
                'lng': pd.to_numeric(df['X'], errors='coerce'),
                'district': df['USER_District_Name'],
                'enrollment': pd.to_numeric(df['USER_School_Enrollment_as_of_Oc'], errors='coerce')
            })
            
            # Remove schools without coordinates
            schools_df = schools_df.dropna(subset=['lat', 'lng'])
            
            print(f"Loaded {len(schools_df)} active Texas public schools")
            return schools_df
            
        except Exception as e:
            print(f"Error loading schools data: {e}")
            return pd.DataFrame()
    
    def find_nearest_schools(self, lat: float, lng: float, school_types: List[str] = None) -> Dict:
        """
        Find nearest public schools using Texas dataset
        
        Args:
            lat: Latitude of the site
            lng: Longitude of the site
            school_types: List of school types to search for
            
        Returns:
            Dictionary with nearest schools by type
        """
        if self.schools_data.empty:
            return {}
        
        site_coords = (lat, lng)
        results = {}
        
        # Define school type mappings
        type_mappings = {
            'elementary': ['Elementary School'],
            'middle': ['Middle School', 'Junior High School'],
            'high': ['High School']
        }
        
        if not school_types:
            school_types = list(type_mappings.keys())
        
        for school_category in school_types:
            school_type_list = type_mappings.get(school_category, [])
            
            # Filter schools by type
            typed_schools = self.schools_data[self.schools_data['type'].isin(school_type_list)]
            
            if len(typed_schools) == 0:
                results[f'{school_category}_school'] = None
                continue
            
            # Calculate distances
            distances = []
            for idx, school in typed_schools.iterrows():
                school_coords = (school['lat'], school['lng'])
                try:
                    distance = geodesic(site_coords, school_coords).miles
                    distances.append({
                        'name': school['name'],
                        'distance_miles': round(distance, 2),
                        'address': f"{school['address']}, {school['city']}, TX {school['zip']}",
                        'district': school['district'],
                        'grades': school['grade_range'],
                        'enrollment': int(school['enrollment']) if pd.notna(school['enrollment']) else None
                    })
                except:
                    continue
            
            # Sort by distance and get nearest
            if distances:
                distances.sort(key=lambda x: x['distance_miles'])
                results[f'{school_category}_school'] = distances[0]
            else:
                results[f'{school_category}_school'] = None
        
        return results
    
    def search_google_amenity(self, lat: float, lng: float, amenity_type: str) -> Optional[Dict]:
        """
        Search for nearest amenity using Google Maps with multiple search strategies
        """
        config = self.amenity_configs.get(amenity_type)
        if not config:
            return None
        
        all_results = []
        
        # Try each search query
        for query in config['search_queries']:
            try:
                # Text search for specific queries
                response = self.gmaps.places(
                    query=query,
                    location=(lat, lng),
                    radius=config['radius']
                )
                
                for place in response.get('results', []):
                    # Skip if name contains excluded terms
                    place_name = place.get('name', '')
                    skip = False
                    for exclude in config['exclude_names']:
                        if exclude.lower() in place_name.lower():
                            skip = True
                            break
                    
                    if skip:
                        continue
                    
                    # For hospitals, verify it has emergency services
                    if amenity_type == 'hospital':
                        types = place.get('types', [])
                        # Must be a hospital type
                        if 'hospital' not in types:
                            continue
                        
                        # Try to verify emergency services in name or via details
                        if not any(term in place_name.lower() for term in ['hospital', 'medical center']):
                            continue
                    
                    place_lat = place['geometry']['location']['lat']
                    place_lng = place['geometry']['location']['lng']
                    
                    # Calculate distance
                    distance = geodesic((lat, lng), (place_lat, place_lng)).miles
                    
                    # Only include if within configured radius
                    if distance <= config['radius'] / 1609.34:  # Convert meters to miles
                        all_results.append({
                            'name': place_name,
                            'distance_miles': round(distance, 2),
                            'address': place.get('formatted_address', ''),
                            'rating': place.get('rating'),
                            'place_id': place['place_id']
                        })
                
                # Small delay between queries
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error searching {amenity_type} with query '{query}': {e}")
                continue
        
        # Remove duplicates by place_id
        seen_ids = set()
        unique_results = []
        for result in all_results:
            if result['place_id'] not in seen_ids:
                seen_ids.add(result['place_id'])
                unique_results.append(result)
        
        # Sort by distance and return nearest
        if unique_results:
            unique_results.sort(key=lambda x: x['distance_miles'])
            return unique_results[0]
        
        return None
    
    def analyze_site_proximity(self, lat: float, lng: float, address: str = "") -> Dict:
        """
        Analyze proximity to amenities for a single site
        Returns only distances in miles, no scoring
        """
        self.logger.info(f"Analyzing proximity for site at {lat}, {lng}")
        
        results = {
            'address': address,
            'lat': lat,
            'lng': lng,
            'timestamp': datetime.now().isoformat(),
            'distances': {}
        }
        
        # Find nearest schools from Texas dataset
        print("  Finding nearest public schools...")
        school_results = self.find_nearest_schools(lat, lng)
        for school_type, school_data in school_results.items():
            if school_data:
                results['distances'][f'{school_type}_name'] = school_data['name']
                results['distances'][f'{school_type}_distance_miles'] = school_data['distance_miles']
                results['distances'][f'{school_type}_district'] = school_data['district']
                results['distances'][f'{school_type}_grades'] = school_data['grades']
            else:
                results['distances'][f'{school_type}_name'] = None
                results['distances'][f'{school_type}_distance_miles'] = None
        
        # Search for other amenities via Google Maps
        for amenity_type in self.amenity_configs.keys():
            print(f"  Searching for {amenity_type}...")
            amenity = self.search_google_amenity(lat, lng, amenity_type)
            
            if amenity:
                results['distances'][f'{amenity_type}_name'] = amenity['name']
                results['distances'][f'{amenity_type}_distance_miles'] = amenity['distance_miles']
                results['distances'][f'{amenity_type}_address'] = amenity['address']
                if amenity.get('rating'):
                    results['distances'][f'{amenity_type}_rating'] = amenity['rating']
            else:
                results['distances'][f'{amenity_type}_name'] = None
                results['distances'][f'{amenity_type}_distance_miles'] = None
        
        return results
    
    def analyze_multiple_sites(self, sites_df: pd.DataFrame, 
                             lat_col: str = 'Latitude', 
                             lng_col: str = 'Longitude', 
                             address_col: str = 'Address') -> pd.DataFrame:
        """
        Analyze multiple sites and return distances only
        """
        results = []
        
        for idx, row in sites_df.iterrows():
            try:
                self.logger.info(f"Processing site {idx + 1} of {len(sites_df)}")
                
                lat = row[lat_col]
                lng = row[lng_col]
                address = row.get(address_col, "") if address_col in sites_df.columns else ""
                
                # Analyze proximity
                site_results = self.analyze_site_proximity(lat, lng, address)
                
                # Flatten results for DataFrame
                flat_results = {
                    'original_index': idx,
                    'address': address,
                    'latitude': lat,
                    'longitude': lng
                }
                
                # Add all distance measurements
                for key, value in site_results['distances'].items():
                    flat_results[key] = value
                
                results.append(flat_results)
                
                # Respect API rate limits
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Error processing site {idx}: {e}")
                continue
        
        return pd.DataFrame(results)