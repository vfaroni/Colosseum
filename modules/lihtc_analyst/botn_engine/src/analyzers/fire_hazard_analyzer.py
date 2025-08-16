#!/usr/bin/env python3
"""
Fire Hazard Analyzer for LIHTC Site Scoring

This module analyzes fire hazard risk for potential development sites
using CAL FIRE's Fire Hazard Severity Zone (FHSZ) data.

Per Site Recommendation Contract, sites in High or Very High fire 
hazard zones cannot be recommended for development.
"""

import requests
import logging
from typing import Dict, Tuple, Any
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point

logger = logging.getLogger(__name__)

class FireHazardAnalyzer:
    """
    Analyzes fire hazard risk at given coordinates using CAL FIRE data
    """
    
    # CAL FIRE REST API endpoint
    FHSZ_API_BASE = "https://services.gis.ca.gov/arcgis/rest/services/Environment/Fire_Severity_Zones/MapServer"
    
    # Acceptable fire risk levels per Site Recommendation Contract
    ACCEPTABLE_RISK_LEVELS = ['No Risk', 'Low Risk', 'Moderate', 'Non-VHFHSZ']
    UNACCEPTABLE_RISK_LEVELS = ['High', 'Very High']
    
    def __init__(self, use_api=True, shapefile_path=None):
        """
        Initialize Fire Hazard Analyzer
        
        Args:
            use_api (bool): Use REST API (True) or local shapefile (False)
            shapefile_path (str): Path to FHSZ shapefile if not using API
        """
        self.use_api = use_api
        
        if not use_api and shapefile_path:
            self.fire_hazard_gdf = self._load_shapefile(shapefile_path)
        else:
            self.fire_hazard_gdf = None
            
        logger.info("FireHazardAnalyzer initialized successfully")
    
    def _load_shapefile(self, shapefile_path: str) -> gpd.GeoDataFrame:
        """Load and prepare fire hazard shapefile"""
        try:
            gdf = gpd.read_file(shapefile_path)
            # Ensure correct coordinate system
            if gdf.crs != 'EPSG:4326':
                gdf = gdf.to_crs('EPSG:4326')
            logger.info(f"Loaded fire hazard shapefile with {len(gdf)} zones")
            return gdf
        except Exception as e:
            logger.error(f"Failed to load shapefile: {e}")
            raise
    
    def analyze_fire_risk(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Analyze fire hazard risk at given coordinates
        
        Args:
            latitude: Site latitude
            longitude: Site longitude
            
        Returns:
            Dict containing:
                - hazard_class: Fire hazard classification
                - hazard_code: Numeric hazard code
                - responsibility_area: SRA or LRA
                - meets_criteria: Boolean if site meets safety criteria
                - data_source: API or shapefile
        """
        if self.use_api:
            return self._query_api(latitude, longitude)
        else:
            return self._query_shapefile(latitude, longitude)
    
    def _query_api(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Query CAL FIRE REST API for fire hazard data"""
        try:
            # Construct identify query
            query_url = f"{self.FHSZ_API_BASE}/identify"
            
            params = {
                'geometry': f'{longitude},{latitude}',
                'geometryType': 'esriGeometryPoint',
                'sr': '4326',  # WGS84
                'layers': 'all',
                'tolerance': '0',
                'mapExtent': f'{longitude-0.01},{latitude-0.01},{longitude+0.01},{latitude+0.01}',
                'imageDisplay': '96,96,96',
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            logger.debug(f"Querying fire hazard API for {latitude}, {longitude}")
            response = requests.get(query_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse results
            if 'results' in data and data['results']:
                result = data['results'][0]  # Take first result
                attributes = result.get('attributes', {})
                
                hazard_class = attributes.get('HAZ_CLASS', 'Unknown')
                hazard_code = attributes.get('HAZ_CODE', 0)
                sra = attributes.get('SRA', 'N')
                
                return {
                    'hazard_class': hazard_class,
                    'hazard_code': hazard_code,
                    'responsibility_area': 'SRA' if sra == 'Y' else 'LRA',
                    'meets_criteria': hazard_class not in self.UNACCEPTABLE_RISK_LEVELS,
                    'data_source': 'CAL FIRE API',
                    'raw_attributes': attributes
                }
            else:
                # CRITICAL BUG FIX: No API results should NOT be interpreted as "safe"
                # This requires manual verification with official CAL FIRE maps
                return {
                    'hazard_class': 'API_NO_DATA',
                    'hazard_code': None,
                    'responsibility_area': 'Unknown',
                    'meets_criteria': None,  # Changed from True to None - requires verification
                    'data_source': 'CAL FIRE API (no data returned)',
                    'error': 'API returned no fire hazard data for this location',
                    'manual_verification_required': True,
                    'verification_sources': [
                        'https://osfm.fire.ca.gov/divisions/wildfire-planning-engineering/wildland-hazards-building-codes/fire-hazard-severity-zones-maps/',
                        'https://egis.fire.ca.gov/FHSZ/',
                        'Local fire department hazard maps'
                    ]
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {
                'hazard_class': 'Unknown',
                'hazard_code': None,
                'meets_criteria': None,
                'error': str(e),
                'data_source': 'CAL FIRE API (failed)'
            }
        except Exception as e:
            logger.error(f"Unexpected error in API query: {e}")
            return {
                'hazard_class': 'Unknown',
                'hazard_code': None,
                'meets_criteria': None,
                'error': str(e),
                'data_source': 'CAL FIRE API (error)'
            }
    
    def _query_shapefile(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Query local shapefile for fire hazard data"""
        if self.fire_hazard_gdf is None:
            return {
                'hazard_class': 'Unknown',
                'meets_criteria': None,
                'error': 'No shapefile loaded',
                'data_source': 'Shapefile (not loaded)'
            }
        
        try:
            # Create point geometry
            point = Point(longitude, latitude)
            
            # Find intersecting polygons
            mask = self.fire_hazard_gdf.contains(point)
            
            if mask.any():
                # Get first matching zone
                zone = self.fire_hazard_gdf[mask].iloc[0]
                
                hazard_class = zone.get('HAZ_CLASS', 'Unknown')
                hazard_code = zone.get('HAZ_CODE', 0)
                sra = zone.get('SRA', 'N')
                
                return {
                    'hazard_class': hazard_class,
                    'hazard_code': hazard_code,
                    'responsibility_area': 'SRA' if sra == 'Y' else 'LRA',
                    'meets_criteria': hazard_class not in self.UNACCEPTABLE_RISK_LEVELS,
                    'data_source': 'Local shapefile'
                }
            else:
                # No fire hazard zone found in shapefile - requires verification
                return {
                    'hazard_class': 'SHAPEFILE_NO_DATA',
                    'hazard_code': None,
                    'responsibility_area': 'Unknown',
                    'meets_criteria': None,  # Requires manual verification
                    'data_source': 'Local shapefile (no data found)',
                    'manual_verification_required': True,
                    'note': 'Location not found in fire hazard shapefile - verify with official CAL FIRE maps'
                }
                
        except Exception as e:
            logger.error(f"Shapefile query error: {e}")
            return {
                'hazard_class': 'Unknown',
                'hazard_code': None,
                'meets_criteria': None,
                'error': str(e),
                'data_source': 'Local shapefile (error)'
            }
    
    def get_fire_risk_summary(self, hazard_class: str) -> str:
        """
        Get human-readable fire risk summary
        
        Args:
            hazard_class: Fire hazard classification
            
        Returns:
            Human-readable risk description
        """
        risk_descriptions = {
            'Non-VHFHSZ': 'No designated fire hazard',
            'Moderate': 'Moderate fire hazard risk',
            'High': 'High fire hazard risk - NOT SUITABLE for development',
            'Very High': 'Very high fire hazard risk - NOT SUITABLE for development',
            'Unknown': 'Fire hazard risk could not be determined'
        }
        
        return risk_descriptions.get(hazard_class, 'Unknown fire hazard classification')
    
    def validate_site_fire_safety(self, latitude: float, longitude: float) -> Tuple[bool, str]:
        """
        Validate if site meets fire safety requirements
        
        Args:
            latitude: Site latitude
            longitude: Site longitude
            
        Returns:
            Tuple of (meets_requirements, explanation)
        """
        result = self.analyze_fire_risk(latitude, longitude)
        
        if result.get('error') or result.get('manual_verification_required'):
            verification_msg = f"Fire hazard data unavailable from API - MANUAL VERIFICATION REQUIRED. "
            verification_msg += f"Check: {', '.join(result.get('verification_sources', ['CAL FIRE official maps']))}"
            return (None, verification_msg)
        
        hazard_class = result['hazard_class']
        meets_criteria = result.get('meets_criteria')
        
        if meets_criteria is None:
            return (None, "Fire hazard classification unknown - manual verification required")
        elif meets_criteria:
            return (True, f"Site has acceptable fire risk level: {hazard_class}")
        else:
            return (False, f"Site is in {hazard_class} fire hazard zone - fails safety requirements")


# Example usage
if __name__ == "__main__":
    # Test the analyzer
    analyzer = FireHazardAnalyzer(use_api=True)
    
    # Test locations
    test_sites = [
        (34.393171, -118.543503, "Test Site 1"),
        (37.8716, -122.2727, "Berkeley Hills (high risk)"),
        (37.7749, -122.4194, "San Francisco Downtown (low risk)")
    ]
    
    for lat, lon, name in test_sites:
        print(f"\nAnalyzing {name} ({lat}, {lon}):")
        result = analyzer.analyze_fire_risk(lat, lon)
        print(f"  Hazard Class: {result['hazard_class']}")
        print(f"  Meets Criteria: {result['meets_criteria']}")
        print(f"  Summary: {analyzer.get_fire_risk_summary(result['hazard_class'])}")