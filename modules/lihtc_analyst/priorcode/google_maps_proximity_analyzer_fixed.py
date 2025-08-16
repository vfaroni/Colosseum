"""
Google Maps Proximity Analyzer for Texas Land Sites - FIXED VERSION
Analyzes proximity to key amenities using Google Places API
Fixes:
1. Only public schools (excludes religious/private schools)
2. Excludes Dollar General from pharmacy searches
3. Better grocery store and transit detection
4. Adds competing LIHTC projects search
"""

import googlemaps
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json
import os
from pathlib import Path
import time
import logging

class GoogleMapsProximityAnalyzer:
    """
    Analyzes proximity to key amenities for land sites using Google Maps API
    """
    
    def __init__(self, api_key: str, cache_dir: Optional[str] = None):
        """
        Initialize the analyzer with Google Maps API key
        
        Args:
            api_key: Google Maps API key with Places API enabled
            cache_dir: Directory for caching results (optional)
        """
        self.gmaps = googlemaps.Client(key=api_key)
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./proximity_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Define search parameters for each amenity type
        self.amenity_configs = {
            'elementary_school': {
                'types': ['primary_school', 'school'],
                'keywords': 'public elementary school -private -catholic -christian -religious -montessori -charter',
                'max_results': 3,
                'radius': 3218,  # 2 miles in meters
                'exclude_keywords': ['private', 'catholic', 'christian', 'religious', 'montessori', 'saint', 'st.', 'academy', 'preparatory']
            },
            'middle_school': {
                'types': ['school'],
                'keywords': 'public middle school -private -catholic -christian -religious -montessori -charter',
                'max_results': 3,
                'radius': 4828,  # 3 miles in meters
                'exclude_keywords': ['private', 'catholic', 'christian', 'religious', 'montessori', 'saint', 'st.', 'academy', 'preparatory']
            },
            'high_school': {
                'types': ['secondary_school', 'school'],
                'keywords': 'public high school -private -catholic -christian -religious -montessori -charter',
                'max_results': 3,
                'radius': 4828,  # 3 miles in meters
                'exclude_keywords': ['private', 'catholic', 'christian', 'religious', 'montessori', 'saint', 'st.', 'academy', 'preparatory']
            },
            'grocery_store': {
                'types': ['grocery_or_supermarket', 'supermarket'],
                'keywords': 'grocery store supermarket',  # More explicit keywords
                'max_results': 5,
                'radius': 1609,  # 1 mile in meters
                'exclude_keywords': ['dollar general', 'dollar tree', 'family dollar', 'convenience store', 'gas station']
            },
            'transit_stop': {
                'types': ['transit_station', 'bus_station', 'subway_station', 'light_rail_station'],
                'keywords': 'bus stop transit station',  # More explicit keywords
                'max_results': 5,
                'radius': 805,   # 0.5 miles in meters
                'exclude_keywords': []
            },
            'pharmacy': {
                'types': ['pharmacy', 'drugstore'],
                'keywords': 'pharmacy drugstore CVS Walgreens',  # Add major pharmacy chains
                'max_results': 3,
                'radius': 3218,  # 2 miles in meters
                'exclude_keywords': ['dollar general', 'dollar tree', 'family dollar', 'walmart', 'target']  # Exclude non-pharmacy stores
            },
            'hospital': {
                'types': ['hospital'],
                'keywords': None,
                'max_results': 3,
                'radius': 8047,  # 5 miles in meters
                'exclude_keywords': []
            },
            'park': {
                'types': ['park'],
                'keywords': 'public park',
                'max_results': 5,
                'radius': 1609,  # 1 mile in meters
                'exclude_keywords': []
            },
            'competing_lihtc': {
                'types': ['real_estate_agency', 'establishment'],  # Broad search
                'keywords': 'affordable housing apartment complex low income housing LIHTC',
                'max_results': 10,
                'radius': 16093,  # 10 miles for competing projects
                'exclude_keywords': ['for sale', 'realtor', 'real estate', 'broker']
            }
        }
        
    def _get_cache_key(self, lat: float, lng: float, amenity_type: str) -> str:
        """Generate cache key for a location and amenity type"""
        return f"{lat:.6f}_{lng:.6f}_{amenity_type}"
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Load cached results if available and not expired"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                # Check if cache is less than 30 days old
                cache_time = datetime.fromisoformat(data['timestamp'])
                if (datetime.now() - cache_time).days < 30:
                    return data['results']
            except Exception as e:
                self.logger.warning(f"Cache read error: {e}")
        return None
    
    def _save_to_cache(self, cache_key: str, results: Dict):
        """Save results to cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'results': results
                }, f)
        except Exception as e:
            self.logger.warning(f"Cache write error: {e}")
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate distance between two points in miles using Haversine formula
        """
        R = 3959  # Earth's radius in miles
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        dlat = np.radians(lat2 - lat1)
        dlng = np.radians(lng2 - lng1)
        
        a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlng/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def _is_excluded(self, place_name: str, exclude_keywords: List[str]) -> bool:
        """Check if a place name contains any excluded keywords"""
        if not exclude_keywords:
            return False
        
        place_name_lower = place_name.lower()
        for keyword in exclude_keywords:
            if keyword.lower() in place_name_lower:
                return True
        return False
    
    def search_nearby_amenity(self, lat: float, lng: float, amenity_type: str) -> List[Dict]:
        """
        Search for nearby amenities of a specific type
        
        Args:
            lat: Latitude of the land site
            lng: Longitude of the land site
            amenity_type: Type of amenity to search for
            
        Returns:
            List of amenity dictionaries with details
        """
        # Check cache first
        cache_key = self._get_cache_key(lat, lng, amenity_type)
        cached_results = self._load_from_cache(cache_key)
        if cached_results is not None:
            return cached_results
        
        config = self.amenity_configs.get(amenity_type)
        if not config:
            raise ValueError(f"Unknown amenity type: {amenity_type}")
        
        results = []
        
        try:
            # For transit stops, try multiple search strategies
            if amenity_type == 'transit_stop':
                # Try text search first for better results
                text_response = self.gmaps.places(
                    query='bus stop near me',
                    location=(lat, lng),
                    radius=config['radius']
                )
                
                for place in text_response.get('results', [])[:config['max_results']]:
                    place_lat = place['geometry']['location']['lat']
                    place_lng = place['geometry']['location']['lng']
                    distance = self._calculate_distance(lat, lng, place_lat, place_lng)
                    
                    if distance <= config['radius'] / 1609.34:  # Convert meters to miles
                        results.append({
                            'name': place.get('name', 'Bus Stop'),
                            'address': place.get('formatted_address', 'Unknown'),
                            'distance_miles': round(distance, 2),
                            'rating': place.get('rating'),
                            'rating_count': place.get('user_ratings_total', 0),
                            'place_id': place['place_id'],
                            'lat': place_lat,
                            'lng': place_lng,
                            'types': place.get('types', [])
                        })
            
            # Standard nearby search for other amenities
            else:
                for place_type in config['types']:
                    response = self.gmaps.places_nearby(
                        location=(lat, lng),
                        radius=config['radius'],
                        type=place_type,
                        keyword=config['keywords']
                    )
                    
                    for place in response.get('results', []):
                        place_name = place.get('name', 'Unknown')
                        
                        # Skip if excluded
                        if self._is_excluded(place_name, config['exclude_keywords']):
                            self.logger.debug(f"Excluded {place_name} for {amenity_type}")
                            continue
                        
                        place_lat = place['geometry']['location']['lat']
                        place_lng = place['geometry']['location']['lng']
                        
                        # Calculate distance
                        distance = self._calculate_distance(lat, lng, place_lat, place_lng)
                        
                        # Get additional details if needed
                        place_details = self.gmaps.place(
                            place_id=place['place_id'],
                            fields=['name', 'formatted_address', 'rating', 'user_ratings_total', 'types']
                        )['result']
                        
                        # Additional filtering for schools - check types
                        if 'school' in amenity_type:
                            place_types = place_details.get('types', [])
                            # Skip if it has types suggesting non-public school
                            skip_types = ['place_of_worship', 'church', 'mosque', 'synagogue']
                            if any(skip_type in place_types for skip_type in skip_types):
                                continue
                        
                        results.append({
                            'name': place_details.get('name', 'Unknown'),
                            'address': place_details.get('formatted_address', 'Unknown'),
                            'distance_miles': round(distance, 2),
                            'rating': place_details.get('rating'),
                            'rating_count': place_details.get('user_ratings_total', 0),
                            'place_id': place['place_id'],
                            'lat': place_lat,
                            'lng': place_lng,
                            'types': place.get('types', [])
                        })
                    
                    # Delay to respect API rate limits
                    time.sleep(0.1)
            
            # For grocery stores, if we didn't find enough, try text search
            if amenity_type == 'grocery_store' and len(results) < 2:
                text_response = self.gmaps.places(
                    query='grocery store supermarket HEB Kroger Walmart grocery',
                    location=(lat, lng),
                    radius=config['radius']
                )
                
                for place in text_response.get('results', []):
                    place_name = place.get('name', 'Unknown')
                    if not self._is_excluded(place_name, config['exclude_keywords']):
                        place_lat = place['geometry']['location']['lat']
                        place_lng = place['geometry']['location']['lng']
                        distance = self._calculate_distance(lat, lng, place_lat, place_lng)
                        
                        if distance <= config['radius'] / 1609.34:
                            results.append({
                                'name': place_name,
                                'address': place.get('formatted_address', 'Unknown'),
                                'distance_miles': round(distance, 2),
                                'rating': place.get('rating'),
                                'rating_count': place.get('user_ratings_total', 0),
                                'place_id': place['place_id'],
                                'lat': place_lat,
                                'lng': place_lng,
                                'types': place.get('types', [])
                            })
                
        except Exception as e:
            self.logger.error(f"Error searching {amenity_type}: {e}")
        
        # Remove duplicates based on place_id
        seen_ids = set()
        unique_results = []
        for result in results:
            if result['place_id'] not in seen_ids:
                seen_ids.add(result['place_id'])
                unique_results.append(result)
        
        # Sort by distance
        unique_results.sort(key=lambda x: x['distance_miles'])
        
        # Keep only the configured maximum number of results
        unique_results = unique_results[:config['max_results']]
        
        # Save to cache
        self._save_to_cache(cache_key, unique_results)
        
        return unique_results
    
    def analyze_site_proximity(self, lat: float, lng: float, address: str = "") -> Dict:
        """
        Analyze proximity to all amenity types for a single site
        
        Args:
            lat: Latitude of the land site
            lng: Longitude of the land site
            address: Address of the site (optional)
            
        Returns:
            Dictionary with proximity analysis results
        """
        self.logger.info(f"Analyzing proximity for site at {lat}, {lng}")
        
        results = {
            'address': address,
            'lat': lat,
            'lng': lng,
            'timestamp': datetime.now().isoformat(),
            'amenities': {}
        }
        
        # Search for each amenity type
        for amenity_type in self.amenity_configs.keys():
            try:
                amenities = self.search_nearby_amenity(lat, lng, amenity_type)
                results['amenities'][amenity_type] = amenities
                
                # Add summary statistics
                if amenities:
                    results['amenities'][f'{amenity_type}_nearest_distance'] = amenities[0]['distance_miles']
                    results['amenities'][f'{amenity_type}_count'] = len(amenities)
                else:
                    results['amenities'][f'{amenity_type}_nearest_distance'] = None
                    results['amenities'][f'{amenity_type}_count'] = 0
                    
            except Exception as e:
                self.logger.error(f"Error analyzing {amenity_type}: {e}")
                results['amenities'][amenity_type] = []
                results['amenities'][f'{amenity_type}_nearest_distance'] = None
                results['amenities'][f'{amenity_type}_count'] = 0
        
        # Calculate proximity scores
        results['proximity_scores'] = self.calculate_proximity_scores(results['amenities'])
        
        return results
    
    def calculate_proximity_scores(self, amenities: Dict) -> Dict:
        """
        Calculate proximity scores based on distance to amenities
        
        Scoring logic:
        - Closer amenities get higher scores
        - Multiple nearby amenities increase score
        - Different weights for different amenity types
        """
        scores = {}
        
        # Define scoring weights and thresholds
        scoring_config = {
            'elementary_school': {'weight': 15, 'ideal_distance': 1.0, 'max_distance': 2.0},
            'middle_school': {'weight': 10, 'ideal_distance': 1.5, 'max_distance': 3.0},
            'high_school': {'weight': 10, 'ideal_distance': 2.0, 'max_distance': 3.0},
            'grocery_store': {'weight': 20, 'ideal_distance': 0.5, 'max_distance': 1.0},
            'transit_stop': {'weight': 15, 'ideal_distance': 0.25, 'max_distance': 0.5},
            'pharmacy': {'weight': 10, 'ideal_distance': 1.0, 'max_distance': 2.0},
            'hospital': {'weight': 10, 'ideal_distance': 3.0, 'max_distance': 5.0},
            'park': {'weight': 10, 'ideal_distance': 0.5, 'max_distance': 1.0}
        }
        
        # Note: competing_lihtc is not included in scoring - it's informational only
        
        total_score = 0
        max_possible_score = sum(config['weight'] for config in scoring_config.values())
        
        for amenity_type, config in scoring_config.items():
            amenity_list = amenities.get(amenity_type, [])
            
            if amenity_list:
                # Get nearest distance
                nearest_distance = amenity_list[0]['distance_miles']
                
                # Calculate distance score (1.0 at ideal distance or closer, 0.0 at max distance or further)
                if nearest_distance <= config['ideal_distance']:
                    distance_score = 1.0
                elif nearest_distance >= config['max_distance']:
                    distance_score = 0.0
                else:
                    # Linear interpolation between ideal and max
                    distance_score = 1.0 - ((nearest_distance - config['ideal_distance']) / 
                                           (config['max_distance'] - config['ideal_distance']))
                
                # Bonus for multiple amenities nearby
                count_bonus = min(0.2 * (len(amenity_list) - 1), 0.4)  # Max 40% bonus
                
                # Calculate weighted score
                score = config['weight'] * distance_score * (1 + count_bonus)
                scores[amenity_type] = round(score, 2)
                total_score += score
            else:
                scores[amenity_type] = 0
        
        # Calculate overall proximity score (0-100)
        scores['total_proximity_score'] = round((total_score / max_possible_score) * 100, 2)
        
        # Add categorical ratings
        if scores['total_proximity_score'] >= 80:
            scores['proximity_rating'] = 'Excellent'
        elif scores['total_proximity_score'] >= 60:
            scores['proximity_rating'] = 'Good'
        elif scores['total_proximity_score'] >= 40:
            scores['proximity_rating'] = 'Fair'
        else:
            scores['proximity_rating'] = 'Poor'
        
        return scores
    
    def analyze_multiple_sites(self, sites_df: pd.DataFrame, lat_col: str = 'latitude', 
                             lng_col: str = 'longitude', address_col: str = 'address') -> pd.DataFrame:
        """
        Analyze proximity for multiple sites
        
        Args:
            sites_df: DataFrame with site information
            lat_col: Column name for latitude
            lng_col: Column name for longitude
            address_col: Column name for address (optional)
            
        Returns:
            DataFrame with proximity analysis results
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
                
                # Add proximity scores
                for score_name, score_value in site_results['proximity_scores'].items():
                    flat_results[f'score_{score_name}'] = score_value
                
                # Add nearest distances for each amenity
                for amenity_type in self.amenity_configs.keys():
                    nearest_dist = site_results['amenities'].get(f'{amenity_type}_nearest_distance')
                    count = site_results['amenities'].get(f'{amenity_type}_count', 0)
                    
                    flat_results[f'{amenity_type}_nearest_miles'] = nearest_dist
                    flat_results[f'{amenity_type}_count'] = count
                    
                    # Add name of nearest amenity
                    amenity_list = site_results['amenities'].get(amenity_type, [])
                    if amenity_list:
                        flat_results[f'{amenity_type}_nearest_name'] = amenity_list[0]['name']
                
                results.append(flat_results)
                
                # Respect API rate limits
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Error processing site {idx}: {e}")
                continue
        
        return pd.DataFrame(results)
    
    def generate_proximity_report(self, analysis_results: pd.DataFrame, output_path: str):
        """
        Generate a comprehensive proximity report
        
        Args:
            analysis_results: DataFrame with proximity analysis results
            output_path: Path for output Excel file
        """
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary sheet
            analysis_results.to_excel(writer, sheet_name='Proximity Analysis', index=False)
            
            # Top sites by proximity score
            top_sites = analysis_results.nlargest(20, 'score_total_proximity_score')
            top_sites.to_excel(writer, sheet_name='Top 20 Sites', index=False)
            
            # Sites with excellent transit access
            transit_sites = analysis_results[
                analysis_results['transit_stop_nearest_miles'] <= 0.25
            ].sort_values('transit_stop_nearest_miles')
            transit_sites.to_excel(writer, sheet_name='Excellent Transit Access', index=False)
            
            # Sites with nearby schools
            school_sites = analysis_results[
                (analysis_results['elementary_school_nearest_miles'] <= 1.0) &
                (analysis_results['middle_school_nearest_miles'] <= 2.0) &
                (analysis_results['high_school_nearest_miles'] <= 2.0)
            ].sort_values('score_total_proximity_score', ascending=False)
            school_sites.to_excel(writer, sheet_name='Near All School Types', index=False)
            
        self.logger.info(f"Proximity report generated: {output_path}")