"""
Improved Texas Proximity Analyzer - Better distance handling
- Searches wider radius but returns nearest result
- Uses text search for better results
- Strict filtering for quality
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

class TexasProximityAnalyzerImproved:
    """
    Improved proximity analyzer with better search and distance handling
    """
    
    def __init__(self, google_maps_api_key: str, 
                 schools_file: str = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/TX_Public_Schools/Schools_2024_to_2025.csv",
                 cache_dir: Optional[str] = None):
        """Initialize the analyzer"""
        self.gmaps = googlemaps.Client(key=google_maps_api_key)
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./proximity_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load Texas public schools
        self.schools_data = self.load_schools_data(schools_file)
        
        print("Improved Texas Proximity Analyzer initialized")
        print("✅ Searches wider area, returns nearest result")
        print("✅ Texas public schools loaded")
    
    def load_schools_data(self, schools_file: str) -> pd.DataFrame:
        """Load Texas public schools data"""
        try:
            df = pd.read_csv(schools_file, encoding='utf-8-sig')
            df = df[df['USER_School_Status'] == 'Active']
            
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
            
            schools_df = schools_df.dropna(subset=['lat', 'lng'])
            print(f"Loaded {len(schools_df)} active Texas public schools")
            return schools_df
            
        except Exception as e:
            print(f"Error loading schools: {e}")
            return pd.DataFrame()
    
    def find_nearest_schools(self, lat: float, lng: float) -> Dict:
        """Find nearest public schools"""
        if self.schools_data.empty:
            return {}
        
        site_coords = (lat, lng)
        results = {}
        
        type_mappings = {
            'elementary': ['Elementary School'],
            'middle': ['Middle School', 'Junior High School'],
            'high': ['High School']
        }
        
        for school_category, school_type_list in type_mappings.items():
            typed_schools = self.schools_data[self.schools_data['type'].isin(school_type_list)]
            
            if len(typed_schools) == 0:
                results[f'{school_category}_school'] = None
                continue
            
            distances = []
            for idx, school in typed_schools.iterrows():
                school_coords = (school['lat'], school['lng'])
                try:
                    distance = geodesic(site_coords, school_coords).miles
                    distances.append({
                        'name': school['name'],
                        'distance_miles': round(distance, 2),
                        'district': school['district'],
                        'grades': school['grade_range']
                    })
                except:
                    continue
            
            if distances:
                distances.sort(key=lambda x: x['distance_miles'])
                results[f'{school_category}_school'] = distances[0]
            else:
                results[f'{school_category}_school'] = None
        
        return results
    
    def search_amenity_generic(self, lat: float, lng: float, query: str, 
                             exclude_terms: List[str], validate_types: List[str] = None,
                             search_radius_miles: float = 15.0) -> Optional[Dict]:
        """Generic amenity search with better distance handling"""
        try:
            # Search with large radius to get more results
            response = self.gmaps.places(
                query=query,
                location=(lat, lng),
                radius=int(search_radius_miles * 1609.34)
            )
            
            all_results = []
            
            for place in response.get('results', []):
                name = place.get('name', '')
                
                # Check exclusions
                excluded = False
                for term in exclude_terms:
                    if term.lower() in name.lower():
                        excluded = True
                        break
                
                if excluded:
                    continue
                
                try:
                    # Calculate distance first
                    place_lat = place['geometry']['location']['lat']
                    place_lng = place['geometry']['location']['lng']
                    distance = geodesic((lat, lng), (place_lat, place_lng)).miles
                    
                    # Get details
                    details = self.gmaps.place(
                        place_id=place['place_id'],
                        fields=['name', 'formatted_address', 'rating', 
                               'user_ratings_total', 'business_status']
                    )['result']
                    
                    if details.get('business_status') != 'OPERATIONAL':
                        continue
                    
                    # Check types if validation required
                    types = place.get('types', [])
                    if validate_types:
                        type_valid = any(vt in types for vt in validate_types)
                        if not type_valid:
                            continue
                    
                    all_results.append({
                        'name': details.get('name'),
                        'distance_miles': round(distance, 2),
                        'address': details.get('formatted_address'),
                        'rating': details.get('rating'),
                        'rating_count': details.get('user_ratings_total', 0),
                        'types': ', '.join(types[:3])
                    })
                    
                except Exception as e:
                    self.logger.debug(f"Error processing place: {e}")
                    continue
                
                time.sleep(0.05)
            
            # Sort by distance and return nearest
            if all_results:
                all_results.sort(key=lambda x: x['distance_miles'])
                return all_results[0]
                
        except Exception as e:
            self.logger.error(f"Search error: {e}")
        
        return None
    
    def search_grocery_stores(self, lat: float, lng: float) -> Optional[Dict]:
        """Search for grocery stores"""
        return self.search_amenity_generic(
            lat, lng,
            query='grocery store supermarket HEB Walmart Kroger Albertsons Randalls Fiesta',
            exclude_terms=['Gas', 'Shell', 'Exxon', 'Chevron', 'BP', 'Valero',
                          'Circle K', '7-Eleven', 'Dollar General', 'Dollar Tree',
                          'Family Dollar', 'Corner Store', 'Mini Mart'],
            validate_types=['grocery_or_supermarket', 'supermarket']
        )
    
    def search_pharmacies(self, lat: float, lng: float) -> Optional[Dict]:
        """Search for pharmacies"""
        return self.search_amenity_generic(
            lat, lng,
            query='pharmacy CVS Walgreens HEB pharmacy Walmart pharmacy',
            exclude_terms=['Dollar General', 'Dollar Tree', 'Family Dollar'],
            validate_types=['pharmacy', 'drugstore']
        )
    
    def search_hospitals(self, lat: float, lng: float) -> Optional[Dict]:
        """Search for hospitals"""
        return self.search_amenity_generic(
            lat, lng,
            query='hospital emergency room',
            exclude_terms=['Clinic', 'Urgent Care', 'Surgery Center', 'Dental',
                          'Eye', 'Veterinary', 'Animal', 'Wellness', 'Therapy'],
            validate_types=['hospital']
        )
    
    def search_transit_stops(self, lat: float, lng: float) -> Optional[Dict]:
        """Search for transit stops"""
        # First try bus stop
        result = self.search_amenity_generic(
            lat, lng,
            query='bus stop',
            exclude_terms=['Park', 'Parking'],
            search_radius_miles=5.0
        )
        
        # If no bus stop found, try transit station
        if not result:
            result = self.search_amenity_generic(
                lat, lng,
                query='transit station metro Capital Metro',
                exclude_terms=['Park', 'Parking'],
                search_radius_miles=10.0
            )
        
        return result
    
    def search_parks(self, lat: float, lng: float) -> Optional[Dict]:
        """Search for parks"""
        return self.search_amenity_generic(
            lat, lng,
            query='park public park city park',
            exclude_terms=['RV', 'Trailer', 'Mobile Home', 'Apartment'],
            validate_types=['park'],
            search_radius_miles=5.0
        )
    
    def analyze_site_proximity(self, lat: float, lng: float, address: str = "") -> Dict:
        """Analyze proximity for a site"""
        self.logger.info(f"Analyzing proximity for site at {lat}, {lng}")
        
        results = {
            'address': address,
            'lat': lat,
            'lng': lng,
            'timestamp': datetime.now().isoformat(),
            'distances': {}
        }
        
        # Schools
        print("  Finding public schools...")
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
        
        # Amenities
        amenity_searches = [
            ('grocery_store', 'grocery stores', self.search_grocery_stores),
            ('pharmacy', 'pharmacies', self.search_pharmacies),
            ('hospital', 'hospitals', self.search_hospitals),
            ('transit_stop', 'transit stops', self.search_transit_stops),
            ('park', 'parks', self.search_parks)
        ]
        
        for amenity_key, amenity_name, search_func in amenity_searches:
            print(f"  Searching for {amenity_name}...")
            amenity = search_func(lat, lng)
            
            if amenity:
                results['distances'][f'{amenity_key}_name'] = amenity['name']
                results['distances'][f'{amenity_key}_distance_miles'] = amenity['distance_miles']
                results['distances'][f'{amenity_key}_address'] = amenity['address']
                results['distances'][f'{amenity_key}_rating'] = amenity.get('rating')
                results['distances'][f'{amenity_key}_rating_count'] = amenity.get('rating_count')
                results['distances'][f'{amenity_key}_types'] = amenity.get('types')
            else:
                results['distances'][f'{amenity_key}_name'] = None
                results['distances'][f'{amenity_key}_distance_miles'] = None
        
        return results
    
    def analyze_multiple_sites(self, sites_df: pd.DataFrame, 
                             lat_col: str = 'Latitude', 
                             lng_col: str = 'Longitude', 
                             address_col: str = 'Address') -> pd.DataFrame:
        """Analyze multiple sites"""
        results = []
        
        for idx, row in sites_df.iterrows():
            try:
                self.logger.info(f"Processing site {idx + 1} of {len(sites_df)}")
                
                lat = row[lat_col]
                lng = row[lng_col]
                address = row.get(address_col, "") if address_col in sites_df.columns else ""
                
                site_results = self.analyze_site_proximity(lat, lng, address)
                
                flat_results = {
                    'original_index': idx,
                    'address': address,
                    'latitude': lat,
                    'longitude': lng
                }
                
                for key, value in site_results['distances'].items():
                    flat_results[key] = value
                
                results.append(flat_results)
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Error processing site {idx}: {e}")
                continue
        
        return pd.DataFrame(results)