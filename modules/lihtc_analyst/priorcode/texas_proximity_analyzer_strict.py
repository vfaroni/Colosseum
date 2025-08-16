"""
Strict Texas Proximity Analyzer
- Uses Texas public schools dataset
- Strict filtering for grocery stores, transit, and other amenities
- Uses proper Google Places API types
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

class TexasProximityAnalyzerStrict:
    """
    Strict proximity analyzer with proper place type filtering
    """
    
    def __init__(self, google_maps_api_key: str, 
                 schools_file: str = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/TX_Public_Schools/Schools_2024_to_2025.csv",
                 cache_dir: Optional[str] = None):
        """
        Initialize the strict analyzer
        """
        self.gmaps = googlemaps.Client(key=google_maps_api_key)
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./proximity_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load Texas public schools data
        self.schools_data = self.load_schools_data(schools_file)
        
        # Define search parameters with strict filtering
        self.amenity_configs = {
            'grocery_store': {
                'place_types': ['supermarket'],  # More specific than grocery_or_supermarket
                'keywords': 'supermarket grocery -gas -convenience -dollar',
                'radius': 3218,  # 2 miles
                'min_user_ratings': 10,  # Must have at least 10 reviews to be legitimate
                'exclude_types': ['gas_station', 'convenience_store'],
                'exclude_names': ['Gas', 'Shell', 'Exxon', 'Chevron', 'BP', 'Valero', 
                                'Circle K', '7-Eleven', 'Dollar', 'General Store', 
                                'Corner Store', 'Mini Mart', 'Quick Stop', 'Speedy']
            },
            'transit_stop': {
                'place_types': ['bus_station'],  # Specific type for bus stops
                'keywords': None,  # Let the type filter do the work
                'radius': 1609,  # 1 mile
                'min_user_ratings': 0,  # Transit stops may not have reviews
                'exclude_types': ['park', 'parking'],
                'exclude_names': ['Park', 'Parking']
            },
            'pharmacy': {
                'place_types': ['pharmacy'],
                'keywords': 'pharmacy',
                'radius': 3218,  # 2 miles
                'min_user_ratings': 5,
                'exclude_types': ['convenience_store'],
                'exclude_names': ['Dollar', 'General Store', 'Discount']
            },
            'hospital': {
                'place_types': ['hospital'],
                'keywords': 'hospital emergency',
                'radius': 8047,  # 5 miles
                'min_user_ratings': 10,
                'exclude_types': ['doctor', 'dentist', 'veterinary_care'],
                'exclude_names': ['Clinic', 'Urgent Care', 'Surgery Center', 'Plastic', 
                                'Cosmetic', 'Dental', 'Eye', 'Veterinary', 'Animal',
                                'Wellness', 'Rehab', 'Therapy']
            },
            'park': {
                'place_types': ['park'],
                'keywords': 'park -rv -trailer',
                'radius': 1609,  # 1 mile
                'min_user_ratings': 0,
                'exclude_types': ['rv_park', 'campground', 'lodging'],
                'exclude_names': ['RV', 'Trailer', 'Mobile Home', 'Manufactured']
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
        """Find nearest public schools using Texas dataset"""
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
    
    def validate_place(self, place: Dict, config: Dict) -> bool:
        """
        Validate if a place meets our strict criteria
        """
        # Check place name against exclusions
        place_name = place.get('name', '').lower()
        for exclude_term in config['exclude_names']:
            if exclude_term.lower() in place_name:
                self.logger.debug(f"Excluded '{place['name']}' - contains '{exclude_term}'")
                return False
        
        # Check place types against exclusions
        place_types = place.get('types', [])
        for exclude_type in config['exclude_types']:
            if exclude_type in place_types:
                self.logger.debug(f"Excluded '{place['name']}' - has type '{exclude_type}'")
                return False
        
        # Check minimum user ratings (indicates legitimacy)
        if config['min_user_ratings'] > 0:
            user_ratings = place.get('user_ratings_total', 0)
            if user_ratings < config['min_user_ratings']:
                self.logger.debug(f"Excluded '{place['name']}' - only {user_ratings} ratings")
                return False
        
        # For grocery stores, do additional validation
        if 'supermarket' in config.get('place_types', []):
            # Must be primarily a supermarket, not just tagged as one
            primary_type = place_types[0] if place_types else None
            if primary_type not in ['supermarket', 'grocery_or_supermarket']:
                self.logger.debug(f"Excluded '{place['name']}' - primary type is '{primary_type}'")
                return False
        
        # For hospitals, verify it's a real hospital
        if 'hospital' in config.get('place_types', []):
            if 'hospital' not in place_types[:3]:  # Must be in top 3 types
                self.logger.debug(f"Excluded '{place['name']}' - hospital not primary type")
                return False
        
        return True
    
    def search_google_amenity_strict(self, lat: float, lng: float, amenity_type: str) -> Optional[Dict]:
        """
        Search for amenities with strict validation
        """
        config = self.amenity_configs.get(amenity_type)
        if not config:
            return None
        
        valid_results = []
        
        # Use nearby search with specific place types
        for place_type in config['place_types']:
            try:
                # Nearby search is more accurate for specific types
                response = self.gmaps.places_nearby(
                    location=(lat, lng),
                    radius=config['radius'],
                    type=place_type,
                    keyword=config['keywords']
                )
                
                for place in response.get('results', []):
                    # Validate the place
                    if not self.validate_place(place, config):
                        continue
                    
                    place_lat = place['geometry']['location']['lat']
                    place_lng = place['geometry']['location']['lng']
                    
                    # Calculate distance
                    distance = geodesic((lat, lng), (place_lat, place_lng)).miles
                    
                    # Get more details to ensure validity
                    try:
                        place_details = self.gmaps.place(
                            place_id=place['place_id'],
                            fields=['name', 'formatted_address', 'types', 'rating', 
                                   'user_ratings_total', 'business_status']
                        )['result']
                        
                        # Skip if permanently closed
                        if place_details.get('business_status') != 'OPERATIONAL':
                            continue
                        
                        valid_results.append({
                            'name': place_details.get('name', 'Unknown'),
                            'distance_miles': round(distance, 2),
                            'address': place_details.get('formatted_address', ''),
                            'rating': place_details.get('rating'),
                            'rating_count': place_details.get('user_ratings_total', 0),
                            'types': place_details.get('types', []),
                            'place_id': place['place_id']
                        })
                        
                    except Exception as e:
                        self.logger.debug(f"Could not get details for place: {e}")
                        continue
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error searching {amenity_type}: {e}")
                continue
        
        # For transit, if no bus_station found, try transit_station as fallback
        if amenity_type == 'transit_stop' and not valid_results:
            try:
                response = self.gmaps.places_nearby(
                    location=(lat, lng),
                    radius=config['radius'],
                    type='transit_station'
                )
                
                for place in response.get('results', []):
                    if self.validate_place(place, config):
                        place_lat = place['geometry']['location']['lat']
                        place_lng = place['geometry']['location']['lng']
                        distance = geodesic((lat, lng), (place_lat, place_lng)).miles
                        
                        valid_results.append({
                            'name': place.get('name', 'Transit Stop'),
                            'distance_miles': round(distance, 2),
                            'address': place.get('formatted_address', ''),
                            'rating': place.get('rating'),
                            'rating_count': place.get('user_ratings_total', 0),
                            'types': place.get('types', []),
                            'place_id': place['place_id']
                        })
                
            except Exception as e:
                self.logger.error(f"Error searching transit fallback: {e}")
        
        # Sort by distance and return nearest
        if valid_results:
            valid_results.sort(key=lambda x: x['distance_miles'])
            return valid_results[0]
        
        return None
    
    def analyze_site_proximity(self, lat: float, lng: float, address: str = "") -> Dict:
        """
        Analyze proximity with strict validation
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
        
        # Search for other amenities with strict validation
        for amenity_type in self.amenity_configs.keys():
            print(f"  Searching for {amenity_type} (strict mode)...")
            amenity = self.search_google_amenity_strict(lat, lng, amenity_type)
            
            if amenity:
                results['distances'][f'{amenity_type}_name'] = amenity['name']
                results['distances'][f'{amenity_type}_distance_miles'] = amenity['distance_miles']
                results['distances'][f'{amenity_type}_address'] = amenity['address']
                results['distances'][f'{amenity_type}_types'] = ', '.join(amenity['types'][:3])
                if amenity.get('rating'):
                    results['distances'][f'{amenity_type}_rating'] = amenity['rating']
                    results['distances'][f'{amenity_type}_rating_count'] = amenity['rating_count']
            else:
                results['distances'][f'{amenity_type}_name'] = None
                results['distances'][f'{amenity_type}_distance_miles'] = None
        
        return results
    
    def analyze_multiple_sites(self, sites_df: pd.DataFrame, 
                             lat_col: str = 'Latitude', 
                             lng_col: str = 'Longitude', 
                             address_col: str = 'Address') -> pd.DataFrame:
        """
        Analyze multiple sites with strict validation
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