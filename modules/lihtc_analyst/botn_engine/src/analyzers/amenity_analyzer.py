#!/usr/bin/env python3
"""
Amenity Analyzer - Proximity analysis for LIHTC scoring

Analyzes proximity to required amenities for LIHTC scoring.
Based on patterns from CTCAC amenity mapper.
"""

import logging
import os
from typing import Dict, Any, Optional, List
from math import radians, cos, sin, asin, sqrt
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd


class AmenityAnalyzer:
    """
    Analyzes amenity proximity for LIHTC scoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.schools_data = None
        self.medical_data = None
        self.grocery_data = None
        self.transit_data = None
        self.parks_data = None
        self.library_data = None
        self.pharmacy_data = None
        
        # Load amenity data
        self._load_amenity_data()
        
        # CTCAC 2025 4% LIHTC Site Amenity Scoring Rules (Maximum 10 points total)
        self.ctcac_scoring_rules = {
            'transit': {
                'high_density_bus': {'max_distance': 0.25, 'points': 7},  # ≥8 routes within 1/4 mile
                'medium_density_bus': {'max_distance': 0.25, 'points': 5},  # 4-7 routes within 1/4 mile
                'low_density_bus': {'max_distance': 0.25, 'points': 3},     # 1-3 routes within 1/4 mile
                'rail_station': {'max_distance': 0.5, 'points': 7}          # Rail/BRT within 1/2 mile
            },
            'parks': {
                'public_park': {'max_distance': 0.5, 'points': 3},  # Within 1/2 mile = 3 pts
                'public_park_quarter': {'max_distance': 0.25, 'points': 2}  # Within 1/4 mile = 2 pts
            },
            'library': {
                'public_library': {'max_distance': 0.5, 'points': 3},   # Within 1/2 mile = 3 pts
                'public_library_quarter': {'max_distance': 0.25, 'points': 2}  # Within 1/4 mile = 2 pts
            },
            'grocery': {
                'supermarket_close': {'max_distance': 0.25, 'points': 5},   # Within 1/4 mile = 5 pts
                'supermarket_half': {'max_distance': 0.5, 'points': 3},     # Within 1/2 mile = 3 pts
                'supermarket_mile': {'max_distance': 1.0, 'points': 1}      # Within 1 mile = 1 pt
            },
            'schools': {
                'public_school': {'max_distance': 0.5, 'points': 3},        # Within 1/2 mile = 3 pts
                'public_school_quarter': {'max_distance': 0.25, 'points': 2} # Within 1/4 mile = 2 pts
            },
            'medical': {
                'hospital_close': {'max_distance': 0.25, 'points': 3},      # Within 1/4 mile = 3 pts
                'hospital_half': {'max_distance': 0.5, 'points': 2},        # Within 1/2 mile = 2 pts
                'clinic_close': {'max_distance': 0.25, 'points': 3},        # Within 1/4 mile = 3 pts
                'clinic_half': {'max_distance': 0.5, 'points': 2}           # Within 1/2 mile = 2 pts
            },
            'pharmacy': {
                'pharmacy_close': {'max_distance': 0.25, 'points': 2},      # Within 1/4 mile = 2 pts
                'pharmacy_half': {'max_distance': 0.5, 'points': 1}         # Within 1/2 mile = 1 pt
            },
            'senior_center': {
                'senior_center': {'max_distance': 0.5, 'points': 3},        # Within 1/2 mile = 3 pts (senior projects only)
                'senior_center_quarter': {'max_distance': 0.25, 'points': 2} # Within 1/4 mile = 2 pts
            },
            'special_needs': {
                'special_needs_facility': {'max_distance': 0.5, 'points': 3}, # Within 1/2 mile = 3 pts (special needs only)
                'special_needs_quarter': {'max_distance': 0.25, 'points': 2}  # Within 1/4 mile = 2 pts
            },
            'internet': {
                'broadband_service': {'available': True, 'points': 3},       # Available on-site = 3 pts
                'fiber_service': {'available': True, 'points': 2}            # Fiber available = 2 pts
            }
        }
    
    def _load_amenity_data(self):
        """Load amenity data from files"""
        try:
            # Load schools data
            schools_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets/california/CA_Public Schools/SchoolSites2324_661351912866317522.gpkg"
            if os.path.exists(schools_path):
                self.logger.info("Loading schools data...")
                self.schools_data = gpd.read_file(schools_path)
                # Convert to WGS84 if needed
                if self.schools_data.crs != 'EPSG:4326':
                    self.schools_data = self.schools_data.to_crs('EPSG:4326')
                self.logger.info(f"Loaded {len(self.schools_data)} schools")
            
            # Load medical facilities data
            medical_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets/california/CA_Hospitals_Medical/Licensed_and_Certified_Healthcare_Facilities.geojson"
            if os.path.exists(medical_path):
                self.logger.info("Loading medical facilities data...")
                self.medical_data = gpd.read_file(medical_path)
                self.logger.info(f"Loaded {len(self.medical_data)} medical facilities")
            
            # Load grocery stores data
            grocery_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets/california/CA_Grocery_Stores/CA_Grocery_Stores.geojson"
            if os.path.exists(grocery_path):
                self.logger.info("Loading grocery stores data...")
                self.grocery_data = gpd.read_file(grocery_path)
                self.logger.info(f"Loaded {len(self.grocery_data)} grocery stores")
            
            # Load enhanced transit data (VTA + existing)
            transit_enhanced_path = self.config.get('data_sources', {}).get('california', {}).get('transit_stops_enhanced')
            if transit_enhanced_path and os.path.exists(transit_enhanced_path):
                self.logger.info("Loading enhanced transit data...")
                self.transit_data = gpd.read_file(transit_enhanced_path)
                self.logger.info(f"Loaded {len(self.transit_data)} transit stops")
            else:
                # Fallback to original transit data
                transit_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets/california/CA_Transit_Data/California_Transit_Stops.geojson"
                if os.path.exists(transit_path):
                    self.logger.info("Loading original transit data...")
                    self.transit_data = gpd.read_file(transit_path)
                    self.logger.info(f"Loaded {len(self.transit_data)} transit stops")
            
            # Load libraries data
            library_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets/california/CA_Libraries/CA_Libraries_OSM.geojson"
            if os.path.exists(library_path):
                self.logger.info("Loading libraries data...")
                self.library_data = gpd.read_file(library_path)
                # Convert to WGS84 if needed
                if self.library_data.crs != 'EPSG:4326':
                    self.library_data = self.library_data.to_crs('EPSG:4326')
                self.logger.info(f"Loaded {len(self.library_data)} libraries")
            
            # Note: Parks and pharmacy data would need to be sourced separately
            # For now we'll use the medical data to identify potential pharmacies
            self.parks_data = None  # TODO: Add parks data source
            self.pharmacy_data = None  # TODO: Add pharmacy data source
                
        except Exception as e:
            self.logger.error(f"Failed to load amenity data: {str(e)}")
    
    def analyze(self, site_info, project_type: str, include_detailed: bool = True) -> Dict[str, Any]:
        """
        Analyze amenity proximity for the site
        
        Args:
            site_info: SiteInfo object with coordinates
            project_type: Type of project (family, senior, etc.)
            include_detailed: Include detailed amenity analysis
            
        Returns:
            Dictionary with amenity analysis results
        """
        try:
            # Placeholder implementation for test run
            latitude = getattr(site_info, 'latitude', 0)
            longitude = getattr(site_info, 'longitude', 0)
            
            amenities = self._find_nearby_amenities(latitude, longitude)
            scoring = self._calculate_ctcac_amenity_scoring(amenities, project_type)
            
            return {
                'total_amenity_points': scoring['total_points'],
                'max_possible_points': scoring['max_points'],
                'amenity_breakdown': scoring['breakdown'],
                'nearby_amenities': amenities if include_detailed else {},
                'analysis_radius_miles': 5.0,
                'project_type': project_type
            }
            
        except Exception as e:
            self.logger.error(f"Amenity analysis failed: {str(e)}")
            return {
                'total_amenity_points': 0,
                'max_possible_points': 10,
                'error': str(e),
                'scoring_method': 'CTCAC 2025 4% LIHTC'
            }
    
    def _find_nearby_amenities(self, latitude: float, longitude: float, max_radius_miles: float = 3.0) -> Dict[str, List[Dict]]:
        """
        Find nearby amenities using real geospatial data for CTCAC scoring
        """
        amenities = {
            'schools': [],
            'medical': [],
            'grocery': [],
            'transit': [],
            'parks': [],
            'library': [],
            'pharmacy': [],
            'senior_center': [],
            'special_needs': []
        }
        
        try:
            # Create point for the site
            site_point = Point(longitude, latitude)
            
            # Find nearby schools
            if self.schools_data is not None:
                for idx, school in self.schools_data.iterrows():
                    try:
                        # Get coordinates from geometry (handle both Point and Polygon)
                        geom = school.geometry
                        if hasattr(geom, 'centroid'):
                            # For polygons, use centroid
                            lat, lon = geom.centroid.y, geom.centroid.x
                        else:
                            # For points
                            lat, lon = geom.y, geom.x
                        
                        distance = self._calculate_distance(latitude, longitude, lat, lon)
                        if distance <= max_radius_miles:
                            school_type = self._classify_school_type(school.get('SchoolLevel', ''))
                            amenities['schools'].append({
                                'name': school.get('SchoolName', 'Unknown School'),
                                'type': school_type,
                                'distance_miles': distance,
                                'coordinates': [lat, lon],
                                'address': f"{school.get('City', '')}, CA",
                                'enrollment': school.get('EnrollTotal', 0)
                            })
                    except Exception as e:
                        self.logger.warning(f"Error processing school {idx}: {str(e)}")
                        continue
            
            # Find nearby medical facilities
            if self.medical_data is not None:
                for idx, facility in self.medical_data.iterrows():
                    try:
                        # Get coordinates from geometry (handle both Point and Polygon)
                        geom = facility.geometry
                        if hasattr(geom, 'centroid'):
                            # For polygons, use centroid
                            lat, lon = geom.centroid.y, geom.centroid.x
                        else:
                            # For points
                            lat, lon = geom.y, geom.x
                        
                        distance = self._calculate_distance(latitude, longitude, lat, lon)
                        if distance <= max_radius_miles:
                            facility_type = self._classify_medical_type(facility.get('FAC_TYPE_CODE', ''))
                            amenities['medical'].append({
                                'name': facility.get('FACNAME', 'Unknown Facility'),
                                'type': facility_type,
                                'distance_miles': distance,
                                'coordinates': [lat, lon],
                                'address': f"{facility.get('CITY', '')}, CA",
                                'facility_code': facility.get('FAC_TYPE_CODE', '')
                            })
                    except Exception as e:
                        self.logger.warning(f"Error processing medical facility {idx}: {str(e)}")
                        continue
            
            # Find nearby grocery stores
            if self.grocery_data is not None:
                for idx, store in self.grocery_data.iterrows():
                    try:
                        # Get coordinates from geometry (handle both Point and Polygon)
                        geom = store.geometry
                        if hasattr(geom, 'centroid'):
                            # For polygons, use centroid
                            lat, lon = geom.centroid.y, geom.centroid.x
                        else:
                            # For points
                            lat, lon = geom.y, geom.x
                        
                        distance = self._calculate_distance(latitude, longitude, lat, lon)
                        if distance <= max_radius_miles:
                            amenities['grocery'].append({
                                'name': store.get('name', 'Unknown Store'),
                                'type': 'supermarket',  # Classify all as supermarket for now
                                'distance_miles': distance,
                                'coordinates': [lat, lon],
                                'address': store.get('address', '')
                            })
                    except Exception as e:
                        self.logger.warning(f"Error processing grocery store {idx}: {str(e)}")
                        continue
            
            # Find nearby libraries
            if self.library_data is not None:
                for idx, library in self.library_data.iterrows():
                    try:
                        # Get coordinates from geometry (handle both Point and Polygon)
                        geom = library.geometry
                        if hasattr(geom, 'centroid'):
                            # For polygons, use centroid
                            lat, lon = geom.centroid.y, geom.centroid.x
                        else:
                            # For points
                            lat, lon = geom.y, geom.x
                        
                        distance = self._calculate_distance(latitude, longitude, lat, lon)
                        if distance <= max_radius_miles:
                            amenities['library'].append({
                                'name': library.get('name', library.get('Name', 'Public Library')),
                                'type': 'public_library',
                                'distance_miles': distance,
                                'coordinates': [lat, lon],
                                'address': library.get('addr:full', library.get('address', ''))
                            })
                    except Exception as e:
                        self.logger.warning(f"Error processing library {idx}: {str(e)}")
                        continue
            
            # Find nearby pharmacies (extract from medical data)
            if self.medical_data is not None:
                for idx, facility in self.medical_data.iterrows():
                    try:
                        # Get coordinates from geometry (handle both Point and Polygon)
                        geom = facility.geometry
                        if hasattr(geom, 'centroid'):
                            # For polygons, use centroid
                            lat, lon = geom.centroid.y, geom.centroid.x
                        else:
                            # For points
                            lat, lon = geom.y, geom.x
                        
                        distance = self._calculate_distance(latitude, longitude, lat, lon)
                        if distance <= max_radius_miles:
                            facility_type = facility.get('FAC_TYPE_CODE', '')
                            facility_name = facility.get('FACNAME', '').lower()
                            
                            # Check if this is a pharmacy
                            if ('pharmacy' in facility_name or 'cvs' in facility_name or 
                                'walgreens' in facility_name or 'rite aid' in facility_name or
                                facility_type in ['PHARM', 'RETAIL']):
                                amenities['pharmacy'].append({
                                    'name': facility.get('FACNAME', 'Pharmacy'),
                                    'type': 'pharmacy',
                                    'distance_miles': distance,
                                    'coordinates': [lat, lon],
                                    'address': f"{facility.get('CITY', '')}, CA"
                                })
                    except Exception as e:
                        self.logger.warning(f"Error processing pharmacy {idx}: {str(e)}")
                        continue
            
            # TODO: Add parks data when source becomes available
            # TODO: Add senior center data when source becomes available
            # TODO: Add special needs facility data when source becomes available
            
            # Find nearby transit stops
            if self.transit_data is not None:
                for idx, stop in self.transit_data.iterrows():
                    try:
                        # Get coordinates from geometry (handle both Point and Polygon)
                        geom = stop.geometry
                        if hasattr(geom, 'centroid'):
                            # For polygons, use centroid
                            lat, lon = geom.centroid.y, geom.centroid.x
                        else:
                            # For points
                            lat, lon = geom.y, geom.x
                        
                        distance = self._calculate_distance(latitude, longitude, lat, lon)
                        if distance <= max_radius_miles:
                            # Determine transit type based on available fields
                            transit_type = self._classify_transit_type(stop)
                            amenities['transit'].append({
                                'name': stop.get('stop_name', stop.get('name', 'Transit Stop')),
                                'type': transit_type,
                                'distance_miles': distance,
                                'coordinates': [lat, lon],
                                'stop_id': stop.get('stop_id', ''),
                                'agency': stop.get('agency_name', 'VTA'),
                                'route_id': stop.get('route_id', stop.get('stop_name', ''))  # For transit scoring
                            })
                    except Exception as e:
                        self.logger.warning(f"Error processing transit stop {idx}: {str(e)}")
                        continue
            
            # Sort by distance and limit results for performance
            for category in amenities:
                amenities[category] = sorted(amenities[category], key=lambda x: x['distance_miles'])[:20]
                
        except Exception as e:
            self.logger.error(f"Error finding nearby amenities: {str(e)}")
            
        return amenities
    
    def _classify_school_type(self, school_level: str) -> str:
        """Classify school type based on school level"""
        if not school_level:
            return 'unknown'
        
        level = school_level.lower()
        if 'elementary' in level or 'primary' in level:
            return 'elementary'
        elif 'middle' in level or 'intermediate' in level:
            return 'middle'
        elif 'high' in level or 'secondary' in level:
            return 'high'
        elif 'k-12' in level or 'k-8' in level:
            return 'elementary'  # Treat as elementary for scoring
        else:
            return 'elementary'  # Default to elementary
    
    def _classify_medical_type(self, facility_code: str) -> str:
        """Classify medical facility type based on facility code"""
        if not facility_code:
            return 'clinic'
        
        code = facility_code.upper()
        # Hospital codes
        if code in ['GEN', 'PSYC', 'REHAB', 'LTAC', 'CHILD', 'SPEC']:
            return 'hospital'
        # Clinic codes
        else:
            return 'clinic'
    
    def _classify_transit_type(self, stop) -> str:
        """Classify transit stop type based on available data"""
        # Check stop name for rail indicators
        stop_name = str(stop.get('stop_name', stop.get('name', ''))).lower()
        
        # Light rail indicators
        if any(keyword in stop_name for keyword in ['light rail', 'station', 'lrt', 'metro']):
            return 'rail_station'
        
        # Caltrain indicators  
        if 'caltrain' in stop_name:
            return 'rail_station'
            
        # Default to bus stop
        return 'bus_stop'
    
    def _calculate_ctcac_amenity_scoring(self, amenities: Dict[str, List[Dict]], project_type: str) -> Dict[str, Any]:
        """Calculate CTCAC 2025 4% LIHTC amenity scoring (max 10 points total)"""
        breakdown = {}
        points_earned = []
        
        # Transit scoring (3-7 points based on density and distance)
        transit_points = self._score_transit_amenities(amenities.get('transit', []))
        if transit_points > 0:
            points_earned.append(('transit', transit_points))
            breakdown['transit'] = {'points_earned': transit_points, 'max_possible': 7}
        
        # Public park scoring (2-3 points)
        park_points = self._score_parks(amenities.get('parks', []))
        if park_points > 0:
            points_earned.append(('parks', park_points))
            breakdown['parks'] = {'points_earned': park_points, 'max_possible': 3}
        
        # Library scoring (2-3 points)
        library_points = self._score_library(amenities.get('library', []))
        if library_points > 0:
            points_earned.append(('library', library_points))
            breakdown['library'] = {'points_earned': library_points, 'max_possible': 3}
        
        # Grocery/market scoring (1-5 points)
        grocery_points = self._score_grocery(amenities.get('grocery', []))
        if grocery_points > 0:
            points_earned.append(('grocery', grocery_points))
            breakdown['grocery'] = {'points_earned': grocery_points, 'max_possible': 5}
        
        # School scoring (2-3 points, only for projects with 25%+ 3BR units)
        if self._has_family_units(project_type):
            school_points = self._score_schools(amenities.get('schools', []))
            if school_points > 0:
                points_earned.append(('schools', school_points))
                breakdown['schools'] = {'points_earned': school_points, 'max_possible': 3}
        
        # Medical clinic/hospital scoring (2-3 points)
        medical_points = self._score_medical(amenities.get('medical', []))
        if medical_points > 0:
            points_earned.append(('medical', medical_points))
            breakdown['medical'] = {'points_earned': medical_points, 'max_possible': 3}
        
        # Pharmacy scoring (1-2 points)
        pharmacy_points = self._score_pharmacy(amenities.get('pharmacy', []))
        if pharmacy_points > 0:
            points_earned.append(('pharmacy', pharmacy_points))
            breakdown['pharmacy'] = {'points_earned': pharmacy_points, 'max_possible': 2}
        
        # Senior center scoring (2-3 points, senior projects only)
        if project_type.lower() == 'senior':
            senior_points = self._score_senior_center(amenities.get('senior_center', []))
            if senior_points > 0:
                points_earned.append(('senior_center', senior_points))
                breakdown['senior_center'] = {'points_earned': senior_points, 'max_possible': 3}
        
        # Special needs facility (2-3 points, special needs projects only)
        if project_type.lower() == 'special_needs':
            special_points = self._score_special_needs(amenities.get('special_needs', []))
            if special_points > 0:
                points_earned.append(('special_needs', special_points))
                breakdown['special_needs'] = {'points_earned': special_points, 'max_possible': 3}
        
        # Sort by points (highest first) and take top scoring amenities up to 10 points
        points_earned.sort(key=lambda x: x[1], reverse=True)
        total_points = 0
        final_breakdown = {}
        
        for amenity_type, points in points_earned:
            if total_points + points <= 10:
                total_points += points
                final_breakdown[amenity_type] = breakdown[amenity_type]
                final_breakdown[amenity_type]['points_counted'] = points
            else:
                remaining_points = 10 - total_points
                if remaining_points > 0:
                    final_breakdown[amenity_type] = breakdown[amenity_type]
                    final_breakdown[amenity_type]['points_counted'] = remaining_points
                    total_points = 10
                break
        
        return {
            'total_points': min(total_points, 10),
            'max_points': 10,
            'breakdown': final_breakdown,
            'scoring_method': 'CTCAC 2025 4% LIHTC'
        }
    
    def _score_transit_amenities(self, transit_stops: List[Dict]) -> int:
        """Score transit amenities based on CTCAC rules"""
        if not transit_stops:
            return 0
        
        # Check for rail/BRT within 0.5 miles
        rail_stops = [s for s in transit_stops if s.get('type') == 'rail_station' and s.get('distance_miles', 999) <= 0.5]
        if rail_stops:
            return 7
        
        # Count bus routes within 0.25 miles
        bus_stops = [s for s in transit_stops if s.get('type') == 'bus_stop' and s.get('distance_miles', 999) <= 0.25]
        route_count = len(set(s.get('route_id', s.get('name', '')) for s in bus_stops))
        
        if route_count >= 8:
            return 7
        elif route_count >= 4:
            return 5
        elif route_count >= 1:
            return 3
        
        return 0
    
    def _score_parks(self, parks: List[Dict]) -> int:
        """Score public parks"""
        if not parks:
            return 0
        
        closest_park = min(parks, key=lambda p: p.get('distance_miles', 999))
        distance = closest_park.get('distance_miles', 999)
        
        if distance <= 0.25:
            return 3
        elif distance <= 0.5:
            return 2
        
        return 0
    
    def _score_library(self, libraries: List[Dict]) -> int:
        """Score public libraries"""
        if not libraries:
            return 0
        
        closest_library = min(libraries, key=lambda l: l.get('distance_miles', 999))
        distance = closest_library.get('distance_miles', 999)
        
        if distance <= 0.25:
            return 3
        elif distance <= 0.5:
            return 2
        
        return 0
    
    def _score_grocery(self, grocery_stores: List[Dict]) -> int:
        """Score grocery stores/supermarkets"""
        if not grocery_stores:
            return 0
        
        closest_store = min(grocery_stores, key=lambda g: g.get('distance_miles', 999))
        distance = closest_store.get('distance_miles', 999)
        
        if distance <= 0.25:
            return 5
        elif distance <= 0.5:
            return 3
        elif distance <= 1.0:
            return 1
        
        return 0
    
    def _score_schools(self, schools: List[Dict]) -> int:
        """Score public schools (for family projects with 25%+ 3BR units)"""
        if not schools:
            return 0
        
        closest_school = min(schools, key=lambda s: s.get('distance_miles', 999))
        distance = closest_school.get('distance_miles', 999)
        
        if distance <= 0.25:
            return 3
        elif distance <= 0.5:
            return 2
        
        return 0
    
    def _score_medical(self, medical_facilities: List[Dict]) -> int:
        """Score medical clinics and hospitals"""
        if not medical_facilities:
            return 0
        
        closest_facility = min(medical_facilities, key=lambda m: m.get('distance_miles', 999))
        distance = closest_facility.get('distance_miles', 999)
        
        if distance <= 0.25:
            return 3
        elif distance <= 0.5:
            return 2
        
        return 0
    
    def _score_pharmacy(self, pharmacies: List[Dict]) -> int:
        """Score pharmacies"""
        if not pharmacies:
            return 0
        
        closest_pharmacy = min(pharmacies, key=lambda p: p.get('distance_miles', 999))
        distance = closest_pharmacy.get('distance_miles', 999)
        
        if distance <= 0.25:
            return 2
        elif distance <= 0.5:
            return 1
        
        return 0
    
    def _score_senior_center(self, senior_centers: List[Dict]) -> int:
        """Score senior centers (senior projects only)"""
        if not senior_centers:
            return 0
        
        closest_center = min(senior_centers, key=lambda s: s.get('distance_miles', 999))
        distance = closest_center.get('distance_miles', 999)
        
        if distance <= 0.25:
            return 3
        elif distance <= 0.5:
            return 2
        
        return 0
    
    def _score_special_needs(self, special_facilities: List[Dict]) -> int:
        """Score special needs facilities (special needs projects only)"""
        if not special_facilities:
            return 0
        
        closest_facility = min(special_facilities, key=lambda s: s.get('distance_miles', 999))
        distance = closest_facility.get('distance_miles', 999)
        
        if distance <= 0.25:
            return 3
        elif distance <= 0.5:
            return 2
        
        return 0
    
    def _has_family_units(self, project_type: str) -> bool:
        """Determine if project has 25%+ 3BR units (affects school scoring eligibility)"""
        # This would need to be determined from actual project data
        # For now, assume family projects have 3BR units
        return project_type.lower() in ['family', 'mixed', 'general']
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points on earth in miles
        """
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