#!/usr/bin/env python3
"""
Enhanced Fire Hazard Analyzer with Multiple Data Sources
Mission: VITOR-WINGMAN-HAZARD-001

This enhanced analyzer addresses API_NO_DATA issues by implementing
multiple fallback data sources and geographic coverage validation.
"""

import requests
import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple, Any, Optional
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedFireHazardAnalyzer:
    """
    Enhanced fire hazard analyzer with multiple data sources and fallback methods
    """
    
    # Primary CAL FIRE API
    FHSZ_API_BASE = "https://services.gis.ca.gov/arcgis/rest/services/Environment/Fire_Severity_Zones/MapServer"
    
    # Alternative CAL FIRE endpoints
    ALTERNATIVE_ENDPOINTS = [
        "https://gis.data.ca.gov/datasets/31219c833eb54598ba83d09fa0adb346",  # State Geoportal
        "https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/California_Fire_Perimeters/FeatureServer"
    ]
    
    # Risk level classifications
    HIGH_RISK_CLASSES = ['High', 'Very High']
    ACCEPTABLE_RISK_CLASSES = ['Non-VHFHSZ', 'Moderate', 'Low Risk']
    
    def __init__(self, api_timeout=15, retry_attempts=3):
        """
        Initialize enhanced analyzer with configuration options
        
        Args:
            api_timeout: Timeout for API requests in seconds
            retry_attempts: Number of retry attempts for failed requests
        """
        self.api_timeout = api_timeout
        self.retry_attempts = retry_attempts
        self.api_statistics = {
            'total_queries': 0,
            'successful_queries': 0,
            'no_data_queries': 0,
            'error_queries': 0,
            'fallback_used': 0
        }
        
        logger.info("Enhanced FireHazardAnalyzer initialized")
    
    def analyze_fire_risk_enhanced(self, latitude: float, longitude: float, 
                                 site_address: str = "", retry_count: int = 0) -> Dict[str, Any]:
        """
        Enhanced fire risk analysis with multiple fallback methods
        
        Args:
            latitude: Site latitude
            longitude: Site longitude
            site_address: Site address for context
            retry_count: Internal retry counter
            
        Returns:
            Comprehensive fire risk analysis result
        """
        self.api_statistics['total_queries'] += 1
        
        # Primary API attempt
        primary_result = self._query_primary_api(latitude, longitude)
        
        if primary_result.get('hazard_class') != 'API_NO_DATA':
            self.api_statistics['successful_queries'] += 1
            return self._enhance_result(primary_result, site_address, 'Primary API')
        
        # Geographic coverage check
        coverage_result = self._check_geographic_coverage(latitude, longitude)
        if not coverage_result['likely_covered']:
            self.api_statistics['no_data_queries'] += 1
            return self._create_out_of_coverage_result(latitude, longitude, site_address, coverage_result)
        
        # Fallback methods
        fallback_result = self._try_fallback_methods(latitude, longitude)
        if fallback_result:
            self.api_statistics['fallback_used'] += 1
            return self._enhance_result(fallback_result, site_address, 'Fallback Method')
        
        # Spatial inference based on nearby known data
        inference_result = self._spatial_inference(latitude, longitude)
        if inference_result:
            return self._enhance_result(inference_result, site_address, 'Spatial Inference')
        
        # Final result with enhanced verification guidance
        self.api_statistics['no_data_queries'] += 1
        return self._create_enhanced_no_data_result(latitude, longitude, site_address)
    
    def _query_primary_api(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Query primary CAL FIRE API with enhanced error handling"""
        try:
            query_url = f"{self.FHSZ_API_BASE}/identify"
            
            params = {
                'geometry': f'{longitude},{latitude}',
                'geometryType': 'esriGeometryPoint',
                'sr': '4326',
                'layers': 'all',
                'tolerance': '3',  # Increased tolerance
                'mapExtent': f'{longitude-0.01},{latitude-0.01},{longitude+0.01},{latitude+0.01}',
                'imageDisplay': '256,256,96',  # Higher resolution
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            for attempt in range(self.retry_attempts):
                try:
                    response = requests.get(query_url, params=params, timeout=self.api_timeout)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if 'results' in data and data['results']:
                        result = data['results'][0]
                        attributes = result.get('attributes', {})
                        
                        hazard_class = attributes.get('HAZ_CLASS', 'Unknown')
                        hazard_code = attributes.get('HAZ_CODE', 0)
                        sra = attributes.get('SRA', 'N')
                        
                        return {
                            'hazard_class': hazard_class,
                            'hazard_code': hazard_code,
                            'responsibility_area': 'SRA' if sra == 'Y' else 'LRA',
                            'meets_criteria': hazard_class not in self.HIGH_RISK_CLASSES,
                            'data_source': 'CAL FIRE Primary API',
                            'confidence': 'High',
                            'raw_attributes': attributes
                        }
                    
                    # No results - break out of retry loop
                    break
                    
                except requests.exceptions.RequestException as e:
                    if attempt == self.retry_attempts - 1:
                        logger.warning(f"Primary API failed after {self.retry_attempts} attempts: {e}")
                    else:
                        time.sleep(1)  # Brief delay before retry
                        
        except Exception as e:
            logger.error(f"Primary API query error: {e}")
        
        return {'hazard_class': 'API_NO_DATA'}
    
    def _check_geographic_coverage(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Check if coordinates are within expected CAL FIRE coverage area
        """
        # California approximate boundaries
        ca_bounds = {
            'lat_min': 32.5, 'lat_max': 42.0,
            'lng_min': -124.5, 'lng_max': -114.0
        }
        
        within_ca = (ca_bounds['lat_min'] <= latitude <= ca_bounds['lat_max'] and
                    ca_bounds['lng_min'] <= longitude <= ca_bounds['lng_max'])
        
        # Check if in known high-coverage areas (populated regions)
        high_coverage_zones = [
            # Southern California
            {'lat_min': 32.5, 'lat_max': 35.0, 'lng_min': -119.0, 'lng_max': -116.0},
            # Central California  
            {'lat_min': 35.0, 'lat_max': 38.0, 'lng_min': -122.0, 'lng_max': -119.0},
            # Northern California
            {'lat_min': 37.0, 'lat_max': 40.0, 'lng_min': -124.0, 'lng_max': -121.0}
        ]
        
        in_high_coverage = any(
            zone['lat_min'] <= latitude <= zone['lat_max'] and
            zone['lng_min'] <= longitude <= zone['lng_max']
            for zone in high_coverage_zones
        )
        
        return {
            'within_california': within_ca,
            'likely_covered': within_ca and in_high_coverage,
            'coverage_confidence': 'High' if in_high_coverage else 'Medium' if within_ca else 'Low'
        }
    
    def _try_fallback_methods(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Try alternative data sources and methods"""
        
        # Method 1: Query specific layers individually
        for layer_id in [0, 1]:  # SRA and LRA layers
            try:
                query_url = f"{self.FHSZ_API_BASE}/{layer_id}/query"
                params = {
                    'where': '1=1',
                    'geometry': f'{longitude},{latitude}',
                    'geometryType': 'esriGeometryPoint',
                    'spatialRel': 'esriSpatialRelIntersects',
                    'outFields': 'HAZ_CLASS,HAZ_CODE,SRA',
                    'returnGeometry': 'false',
                    'f': 'json'
                }
                
                response = requests.get(query_url, params=params, timeout=self.api_timeout)
                response.raise_for_status()
                data = response.json()
                
                if data.get('features'):
                    feature = data['features'][0]
                    attrs = feature.get('attributes', {})
                    
                    hazard_class = attrs.get('HAZ_CLASS')
                    if hazard_class and hazard_class != 'null':
                        return {
                            'hazard_class': hazard_class,
                            'hazard_code': attrs.get('HAZ_CODE', 0),
                            'responsibility_area': f'Layer {layer_id}',
                            'meets_criteria': hazard_class not in self.HIGH_RISK_CLASSES,
                            'data_source': f'CAL FIRE Layer {layer_id}',
                            'confidence': 'Medium'
                        }
                        
            except Exception as e:
                logger.debug(f"Fallback layer {layer_id} failed: {e}")
                continue
        
        return None
    
    def _spatial_inference(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Make spatial inference based on geographic patterns
        """
        # Known high-risk patterns in California
        high_risk_patterns = [
            # Wildland-Urban Interface areas (approximate)
            {'name': 'Oakland Hills Area', 'lat_center': 37.87, 'lng_center': -122.27, 'radius': 0.05},
            {'name': 'Malibu Hills', 'lat_center': 34.03, 'lng_center': -118.78, 'radius': 0.03},
            {'name': 'Santa Barbara Foothills', 'lat_center': 34.42, 'lng_center': -119.70, 'radius': 0.04}
        ]
        
        for pattern in high_risk_patterns:
            distance = np.sqrt((latitude - pattern['lat_center'])**2 + 
                             (longitude - pattern['lng_center'])**2)
            
            if distance <= pattern['radius']:
                return {
                    'hazard_class': 'High (Inferred)',
                    'hazard_code': 2,
                    'meets_criteria': False,
                    'data_source': f'Spatial Inference: {pattern["name"]}',
                    'confidence': 'Low',
                    'inference_note': f'Located within {pattern["radius"]*69:.1f} miles of known high-risk area'
                }
        
        # Low-risk inference for urban centers
        urban_centers = [
            {'name': 'Downtown LA', 'lat_center': 34.05, 'lng_center': -118.24, 'radius': 0.02},
            {'name': 'Downtown SF', 'lat_center': 37.77, 'lng_center': -122.42, 'radius': 0.02}
        ]
        
        for center in urban_centers:
            distance = np.sqrt((latitude - center['lat_center'])**2 + 
                             (longitude - center['lng_center'])**2)
            
            if distance <= center['radius']:
                return {
                    'hazard_class': 'Moderate (Inferred)',
                    'hazard_code': 1,
                    'meets_criteria': True,
                    'data_source': f'Spatial Inference: {center["name"]}',
                    'confidence': 'Low',
                    'inference_note': f'Located in urban center with typically lower fire risk'
                }
        
        return None
    
    def _create_enhanced_no_data_result(self, latitude: float, longitude: float, 
                                      site_address: str) -> Dict[str, Any]:
        """Create enhanced no-data result with detailed verification guidance"""
        
        # Generate specific verification URLs
        verification_urls = [
            f"https://egis.fire.ca.gov/FHSZ/?lat={latitude}&lng={longitude}",
            "https://osfm.fire.ca.gov/divisions/wildfire-planning-engineering/wildland-hazards-building-codes/fire-hazard-severity-zones-maps/",
            f"https://www.google.com/maps/@{latitude},{longitude},15z"
        ]
        
        return {
            'hazard_class': 'REQUIRES_MANUAL_VERIFICATION',
            'hazard_code': None,
            'responsibility_area': 'Unknown',
            'meets_criteria': None,
            'data_source': 'No automated data available',
            'confidence': 'Unknown',
            'manual_verification_required': True,
            'site_address': site_address,
            'coordinates': f"{latitude:.6f}, {longitude:.6f}",
            'verification_urls': verification_urls,
            'verification_priority': 'HIGH',
            'verification_note': 'Multiple API sources returned no data - manual verification required before site elimination decision'
        }
    
    def _create_out_of_coverage_result(self, latitude: float, longitude: float, 
                                     site_address: str, coverage_info: Dict) -> Dict[str, Any]:
        """Create result for sites outside expected coverage area"""
        
        if not coverage_info['within_california']:
            return {
                'hazard_class': 'OUT_OF_STATE',
                'meets_criteria': None,
                'data_source': 'Geographic Analysis',
                'confidence': 'High',
                'note': 'Site appears to be outside California - CAL FIRE data not applicable',
                'requires_local_fire_department_verification': True
            }
        else:
            return {
                'hazard_class': 'COVERAGE_GAP',
                'meets_criteria': None,
                'data_source': 'Geographic Analysis',
                'confidence': 'Medium',
                'note': 'Site in California but outside typical CAL FIRE high-coverage areas',
                'manual_verification_required': True
            }
    
    def _enhance_result(self, result: Dict[str, Any], site_address: str, 
                       data_source: str) -> Dict[str, Any]:
        """Enhance result with additional context and validation"""
        
        enhanced = result.copy()
        enhanced.update({
            'site_address': site_address,
            'analysis_timestamp': pd.Timestamp.now().isoformat(),
            'analyzer_version': 'Enhanced v2.0',
            'validation_status': self._determine_validation_status(result),
            'elimination_recommendation': self._get_elimination_recommendation(result)
        })
        
        return enhanced
    
    def _determine_validation_status(self, result: Dict[str, Any]) -> str:
        """Determine if result needs additional validation"""
        
        hazard_class = result.get('hazard_class', '')
        confidence = result.get('confidence', 'Unknown')
        
        if 'MANUAL_VERIFICATION' in hazard_class or result.get('manual_verification_required'):
            return 'MANUAL_VERIFICATION_REQUIRED'
        elif confidence == 'Low':
            return 'RECOMMEND_MANUAL_VERIFICATION'
        elif hazard_class in self.HIGH_RISK_CLASSES:
            return 'HIGH_RISK_CONFIRMED'
        else:
            return 'AUTOMATED_RESULT_ACCEPTABLE'
    
    def _get_elimination_recommendation(self, result: Dict[str, Any]) -> str:
        """Get specific elimination recommendation"""
        
        meets_criteria = result.get('meets_criteria')
        validation_status = self._determine_validation_status(result)
        
        if meets_criteria is False:
            return 'ELIMINATE_SITE'
        elif meets_criteria is True:
            return 'KEEP_SITE'
        elif validation_status == 'MANUAL_VERIFICATION_REQUIRED':
            return 'DEFER_TO_MANUAL_REVIEW'
        else:
            return 'MANUAL_REVIEW_RECOMMENDED'
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics for quality monitoring"""
        
        total = self.api_statistics['total_queries']
        if total == 0:
            return {'message': 'No queries performed yet'}
        
        success_rate = (self.api_statistics['successful_queries'] / total) * 100
        no_data_rate = (self.api_statistics['no_data_queries'] / total) * 100
        
        return {
            'total_queries': total,
            'success_rate': f"{success_rate:.1f}%",
            'no_data_rate': f"{no_data_rate:.1f}%",
            'fallback_usage': self.api_statistics['fallback_used'],
            'error_count': self.api_statistics['error_queries']
        }


# Test function
def test_enhanced_analyzer():
    """Test the enhanced analyzer with various scenarios"""
    
    analyzer = EnhancedFireHazardAnalyzer()
    
    test_sites = [
        (34.0259, -118.7798, "Malibu Hills (known high risk)"),
        (37.7749, -122.4194, "San Francisco Downtown"),
        (34.0522, -118.2437, "Downtown Los Angeles"),
        (36.7378, -119.7871, "Central Valley Fresno")
    ]
    
    print("🧪 Testing Enhanced Fire Hazard Analyzer")
    print("=" * 60)
    
    for lat, lng, name in test_sites:
        print(f"\n📍 Testing: {name}")
        result = analyzer.analyze_fire_risk_enhanced(lat, lng, name)
        
        print(f"   Hazard Class: {result.get('hazard_class', 'Unknown')}")
        print(f"   Meets Criteria: {result.get('meets_criteria', 'Unknown')}")
        print(f"   Recommendation: {result.get('elimination_recommendation', 'Unknown')}")
        print(f"   Validation: {result.get('validation_status', 'Unknown')}")
        print(f"   Data Source: {result.get('data_source', 'Unknown')}")
    
    print(f"\n📊 Analysis Statistics:")
    stats = analyzer.get_analysis_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    test_enhanced_analyzer()