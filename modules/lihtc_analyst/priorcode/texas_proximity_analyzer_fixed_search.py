"""
Fixed Texas Proximity Analyzer - Uses better search strategies
- Text search for grocery stores instead of type-based search
- Better fallback strategies
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

class TexasProximityAnalyzerFixed:
    """
    Fixed proximity analyzer with better search strategies
    """
    
    def __init__(self, google_maps_api_key: str, 
                 schools_file: str = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/TX_Public_Schools/Schools_2024_to_2025.csv",
                 cache_dir: Optional[str] = None):
        """
        Initialize the analyzer
        """
        self.gmaps = googlemaps.Client(key=google_maps_api_key)
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./proximity_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load Texas public schools data
        self.schools_data = self.load_schools_data(schools_file)
        
        print("Fixed Texas Proximity Analyzer initialized")
        print("✅ Using text search for better results")
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
            print(f"Error loading schools data: {e}")
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
    
    def search_grocery_stores(self, lat: float, lng: float, radius_miles: float = 5.0) -> Optional[Dict]:
        """Search for grocery stores using text search"""
        try:
            # Use text search which works better
            response = self.gmaps.places(
                query='grocery store supermarket HEB Walmart Kroger Albertsons',
                location=(lat, lng),
                radius=int(radius_miles * 1609.34)  # Convert miles to meters
            )
            
            results = []
            for place in response.get('results', []):
                name = place.get('name', '')
                
                # Exclude gas stations and convenience stores
                exclude_terms = ['Gas', 'Shell', 'Exxon', 'Chevron', 'BP', 'Valero',
                               'Circle K', '7-Eleven', 'Dollar General', 'Dollar Tree',
                               'Family Dollar', 'Corner Store', 'Mini Mart']
                
                excluded = False
                for term in exclude_terms:
                    if term.lower() in name.lower():
                        excluded = True
                        break
                
                if excluded:
                    continue
                
                # Get place details
                try:
                    details = self.gmaps.place(
                        place_id=place['place_id'],
                        fields=['name', 'formatted_address', 'type', 'rating', 
                               'user_ratings_total', 'business_status']
                    )['result']
                    
                    # Skip if closed
                    if details.get('business_status') != 'OPERATIONAL':
                        continue
                    
                    # Check if it's primarily a grocery/supermarket
                    types = place.get('types', [])  # Get types from search response
                    if 'gas_station' in types or 'convenience_store' in types:
                        continue
                    
                    # Calculate distance
                    place_lat = place['geometry']['location']['lat']
                    place_lng = place['geometry']['location']['lng']
                    distance = geodesic((lat, lng), (place_lat, place_lng)).miles
                    
                    if distance <= radius_miles:
                        results.append({
                            'name': details.get('name'),
                            'distance_miles': round(distance, 2),
                            'address': details.get('formatted_address'),
                            'rating': details.get('rating'),
                            'rating_count': details.get('user_ratings_total', 0),
                            'types': ', '.join(place.get('types', [])[:3])
                        })
                    
                except:
                    continue
                
                time.sleep(0.05)
            
            if results:
                results.sort(key=lambda x: x['distance_miles'])
                return results[0]
            
        except Exception as e:
            self.logger.error(f"Error searching grocery stores: {e}")
        
        return None
    
    def search_pharmacies(self, lat: float, lng: float, radius_miles: float = 5.0) -> Optional[Dict]:
        """Search for pharmacies using text search"""
        try:
            response = self.gmaps.places(
                query='pharmacy CVS Walgreens HEB pharmacy Walmart pharmacy',
                location=(lat, lng),
                radius=int(radius_miles * 1609.34)
            )
            
            results = []
            for place in response.get('results', []):
                name = place.get('name', '')
                
                # Exclude non-pharmacies
                exclude_terms = ['Dollar General', 'Dollar Tree', 'Family Dollar']
                if any(term.lower() in name.lower() for term in exclude_terms):
                    continue
                
                # Get details and verify it's a pharmacy
                try:
                    details = self.gmaps.place(
                        place_id=place['place_id'],
                        fields=['name', 'formatted_address', 'type', 'rating',
                               'user_ratings_total', 'business_status']
                    )['result']
                    
                    if details.get('business_status') != 'OPERATIONAL':
                        continue
                    
                    types = place.get('types', [])
                    # Must have pharmacy or drugstore in types
                    if not any(t in types for t in ['pharmacy', 'drugstore']):
                        continue
                    
                    place_lat = place['geometry']['location']['lat']
                    place_lng = place['geometry']['location']['lng']
                    distance = geodesic((lat, lng), (place_lat, place_lng)).miles
                    
                    if distance <= radius_miles:
                        results.append({
                            'name': details.get('name'),
                            'distance_miles': round(distance, 2),
                            'address': details.get('formatted_address'),
                            'rating': details.get('rating'),
                            'rating_count': details.get('user_ratings_total', 0),
                            'types': ', '.join(place.get('types', [])[:3])
                        })
                    
                except:
                    continue
                
                time.sleep(0.05)
            
            if results:
                results.sort(key=lambda x: x['distance_miles'])
                return results[0]
                
        except Exception as e:
            self.logger.error(f"Error searching pharmacies: {e}")
        
        return None
    
    def search_hospitals(self, lat: float, lng: float, radius_miles: float = 10.0) -> Optional[Dict]:
        """Search for hospitals with emergency services"""
        try:
            response = self.gmaps.places(
                query='hospital emergency room',
                location=(lat, lng),
                radius=int(radius_miles * 1609.34)
            )
            
            results = []
            for place in response.get('results', []):
                name = place.get('name', '')
                
                # Exclude non-hospitals
                exclude_terms = ['Clinic', 'Urgent Care', 'Surgery Center', 'Dental',
                               'Eye', 'Veterinary', 'Animal', 'Wellness', 'Therapy']
                if any(term.lower() in name.lower() for term in exclude_terms):
                    continue
                
                try:
                    details = self.gmaps.place(
                        place_id=place['place_id'],
                        fields=['name', 'formatted_address', 'type', 'rating',
                               'user_ratings_total', 'business_status']
                    )['result']
                    
                    if details.get('business_status') != 'OPERATIONAL':
                        continue
                    
                    types = place.get('types', [])
                    if 'hospital' not in types:
                        continue
                    
                    place_lat = place['geometry']['location']['lat']
                    place_lng = place['geometry']['location']['lng']
                    distance = geodesic((lat, lng), (place_lat, place_lng)).miles
                    
                    if distance <= radius_miles:
                        results.append({
                            'name': details.get('name'),
                            'distance_miles': round(distance, 2),
                            'address': details.get('formatted_address'),
                            'rating': details.get('rating'),
                            'rating_count': details.get('user_ratings_total', 0),
                            'types': ', '.join(place.get('types', [])[:3])
                        })
                    
                except:
                    continue
                
                time.sleep(0.05)
            
            if results:
                results.sort(key=lambda x: x['distance_miles'])
                return results[0]
                
        except Exception as e:
            self.logger.error(f"Error searching hospitals: {e}")
        
        return None
    
    def search_transit_stops(self, lat: float, lng: float, radius_miles: float = 3.0) -> Optional[Dict]:
        """Search for transit stops"""
        try:
            # Try text search for bus stops - "bus stop" works better than "bus_station"
            response = self.gmaps.places(
                query='bus stop',
                location=(lat, lng),
                radius=int(radius_miles * 1609.34)
            )
            
            results = []
            for place in response.get('results', []):
                name = place.get('name', '')
                
                # Exclude parks and parking
                if 'park' in name.lower() and 'park and ride' not in name.lower():
                    continue
                
                try:
                    place_lat = place['geometry']['location']['lat']
                    place_lng = place['geometry']['location']['lng']
                    distance = geodesic((lat, lng), (place_lat, place_lng)).miles
                    
                    if distance <= radius_miles:
                        results.append({
                            'name': name,
                            'distance_miles': round(distance, 2),
                            'address': place.get('formatted_address', ''),
                            'types': ', '.join(place.get('types', [])[:3])
                        })
                    
                except:
                    continue
            
            if results:
                results.sort(key=lambda x: x['distance_miles'])
                return results[0]
                
        except Exception as e:
            self.logger.error(f"Error searching transit: {e}")
        
        return None
    
    def search_parks(self, lat: float, lng: float, radius_miles: float = 3.0) -> Optional[Dict]:
        """Search for parks"""
        try:
            response = self.gmaps.places(
                query='park public park city park',
                location=(lat, lng),
                radius=int(radius_miles * 1609.34)
            )
            
            results = []
            for place in response.get('results', []):
                name = place.get('name', '')
                
                # Exclude RV parks, trailer parks
                exclude_terms = ['RV', 'Trailer', 'Mobile Home']
                if any(term.lower() in name.lower() for term in exclude_terms):
                    continue
                
                try:
                    place_lat = place['geometry']['location']['lat']
                    place_lng = place['geometry']['location']['lng']
                    distance = geodesic((lat, lng), (place_lat, place_lng)).miles
                    
                    if distance <= radius_miles:
                        results.append({
                            'name': name,
                            'distance_miles': round(distance, 2),
                            'address': place.get('formatted_address', ''),
                            'types': ', '.join(place.get('types', [])[:3])
                        })
                    
                except:
                    continue
            
            if results:
                results.sort(key=lambda x: x['distance_miles'])
                return results[0]
                
        except Exception as e:
            self.logger.error(f"Error searching parks: {e}")
        
        return None
    
    def analyze_site_proximity(self, lat: float, lng: float, address: str = "") -> Dict:
        """Analyze proximity using fixed search methods"""
        self.logger.info(f"Analyzing proximity for site at {lat}, {lng}")
        
        results = {
            'address': address,
            'lat': lat,
            'lng': lng,
            'timestamp': datetime.now().isoformat(),
            'distances': {}
        }
        
        # Find nearest schools
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
        
        # Search for amenities using text search
        print("  Searching for grocery stores...")
        grocery = self.search_grocery_stores(lat, lng)
        if grocery:
            results['distances']['grocery_store_name'] = grocery['name']
            results['distances']['grocery_store_distance_miles'] = grocery['distance_miles']
            results['distances']['grocery_store_address'] = grocery['address']
            results['distances']['grocery_store_rating'] = grocery.get('rating')
            results['distances']['grocery_store_rating_count'] = grocery.get('rating_count')
            results['distances']['grocery_store_types'] = grocery.get('types')
        else:
            results['distances']['grocery_store_name'] = None
            results['distances']['grocery_store_distance_miles'] = None
        
        print("  Searching for pharmacies...")
        pharmacy = self.search_pharmacies(lat, lng)
        if pharmacy:
            results['distances']['pharmacy_name'] = pharmacy['name']
            results['distances']['pharmacy_distance_miles'] = pharmacy['distance_miles']
            results['distances']['pharmacy_address'] = pharmacy['address']
            results['distances']['pharmacy_rating'] = pharmacy.get('rating')
            results['distances']['pharmacy_rating_count'] = pharmacy.get('rating_count')
            results['distances']['pharmacy_types'] = pharmacy.get('types')
        else:
            results['distances']['pharmacy_name'] = None
            results['distances']['pharmacy_distance_miles'] = None
        
        print("  Searching for hospitals...")
        hospital = self.search_hospitals(lat, lng)
        if hospital:
            results['distances']['hospital_name'] = hospital['name']
            results['distances']['hospital_distance_miles'] = hospital['distance_miles']
            results['distances']['hospital_address'] = hospital['address']
            results['distances']['hospital_rating'] = hospital.get('rating')
            results['distances']['hospital_rating_count'] = hospital.get('rating_count')
            results['distances']['hospital_types'] = hospital.get('types')
        else:
            results['distances']['hospital_name'] = None
            results['distances']['hospital_distance_miles'] = None
        
        print("  Searching for transit stops...")
        transit = self.search_transit_stops(lat, lng)
        if transit:
            results['distances']['transit_stop_name'] = transit['name']
            results['distances']['transit_stop_distance_miles'] = transit['distance_miles']
            results['distances']['transit_stop_address'] = transit['address']
            results['distances']['transit_stop_types'] = transit.get('types')
        else:
            results['distances']['transit_stop_name'] = None
            results['distances']['transit_stop_distance_miles'] = None
        
        print("  Searching for parks...")
        park = self.search_parks(lat, lng)
        if park:
            results['distances']['park_name'] = park['name']
            results['distances']['park_distance_miles'] = park['distance_miles']
            results['distances']['park_address'] = park['address']
            results['distances']['park_types'] = park.get('types')
        else:
            results['distances']['park_name'] = None
            results['distances']['park_distance_miles'] = None
        
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