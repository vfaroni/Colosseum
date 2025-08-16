#!/usr/bin/env python3
"""
Enhanced Flood Risk Analyzer for LIHTC Site Assessment
Mission: VITOR-WINGMAN-HAZARD-001

This analyzer processes flood risk for sites using multiple data sources:
1. Existing FEMA flood data in the dataset
2. FEMA Web Map Service API for missing data  
3. National Flood Hazard Layer (NFHL) data
4. Spatial analysis and inference methods
"""

import pandas as pd
import requests
import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedFloodAnalyzer:
    """
    Comprehensive flood risk analyzer with multiple data sources
    """
    
    # FEMA Map Service endpoints
    FEMA_WMS_BASE = "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer"
    FEMA_FLOOD_ZONES_LAYER = "28"  # NFHL flood zones layer
    
    # Alternative endpoints
    ALTERNATIVE_ENDPOINTS = [
        "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Flood_Hazard_Areas/FeatureServer/0",
        "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Hydro/MapServer"
    ]
    
    # Risk level classifications
    HIGH_RISK_ZONES = ['A', 'AE', 'AH', 'AO', 'AR', 'A99', 'V', 'VE']
    MODERATE_RISK_ZONES = ['B', 'X500', '0.2 PCT ANNUAL CHANCE FLOOD HAZARD']
    LOW_RISK_ZONES = ['C', 'X', 'AREA OF MINIMAL FLOOD HAZARD']
    
    # SFHA (Special Flood Hazard Area) zones
    SFHA_ZONES = ['A', 'AE', 'AH', 'AO', 'AR', 'A99', 'V', 'VE', 'D']
    
    def __init__(self, api_timeout=20, retry_attempts=3):
        """
        Initialize enhanced flood analyzer
        
        Args:
            api_timeout: Timeout for API requests
            retry_attempts: Number of retry attempts
        """
        self.api_timeout = api_timeout
        self.retry_attempts = retry_attempts
        self.analysis_stats = {
            'total_analyzed': 0,
            'existing_data_used': 0,
            'api_queries': 0,
            'api_successes': 0,
            'inferences_made': 0,
            'manual_verification_needed': 0
        }
        
        logger.info("Enhanced FloodAnalyzer initialized")
    
    def analyze_flood_risk_comprehensive(self, latitude: float, longitude: float, 
                                       existing_data: Dict[str, Any] = None,
                                       site_address: str = "") -> Dict[str, Any]:
        """
        Comprehensive flood risk analysis using all available methods
        
        Args:
            latitude: Site latitude
            longitude: Site longitude  
            existing_data: Any existing flood data from dataset
            site_address: Site address for context
            
        Returns:
            Comprehensive flood risk assessment
        """
        self.analysis_stats['total_analyzed'] += 1
        
        # Check if we already have reliable existing data
        if existing_data and self._has_reliable_existing_data(existing_data):
            self.analysis_stats['existing_data_used'] += 1
            return self._process_existing_flood_data(existing_data, site_address)
        
        # Query FEMA API for missing data
        api_result = self._query_fema_flood_api(latitude, longitude)
        if api_result and api_result.get('flood_zone') != 'NO_DATA':
            self.analysis_stats['api_successes'] += 1
            return self._process_api_flood_data(api_result, site_address, latitude, longitude)
        
        # Try alternative data sources
        alt_result = self._try_alternative_flood_sources(latitude, longitude)
        if alt_result:
            return self._process_api_flood_data(alt_result, site_address, latitude, longitude)
        
        # Spatial inference based on geographic patterns
        inference_result = self._flood_spatial_inference(latitude, longitude)
        if inference_result:
            self.analysis_stats['inferences_made'] += 1
            return self._process_inference_result(inference_result, site_address, latitude, longitude)
        
        # Final fallback - requires manual verification
        self.analysis_stats['manual_verification_needed'] += 1
        return self._create_manual_verification_result(latitude, longitude, site_address)
    
    def _has_reliable_existing_data(self, existing_data: Dict[str, Any]) -> bool:
        """Check if existing flood data is complete and reliable"""
        
        sfha_status = existing_data.get('In SFHA')
        flood_risk_area = existing_data.get('Flood Risk Area')
        fema_flood_zone = existing_data.get('Fema Flood Zone')
        
        # Consider data reliable if we have SFHA status and either risk area or FEMA zone
        has_sfha = sfha_status in ['Yes', 'No']
        has_risk_or_zone = (
            pd.notna(flood_risk_area) or 
            pd.notna(fema_flood_zone)
        )
        
        return has_sfha and has_risk_or_zone
    
    def _process_existing_flood_data(self, existing_data: Dict[str, Any], 
                                   site_address: str) -> Dict[str, Any]:
        """Process existing flood data from the dataset"""
        
        sfha_status = existing_data.get('In SFHA', 'Unknown')
        flood_risk_area = existing_data.get('Flood Risk Area')
        fema_flood_zone = existing_data.get('Fema Flood Zone', 'Unknown')
        
        # Determine risk level
        is_high_risk = (
            sfha_status == 'Yes' or
            flood_risk_area == 'High Risk Areas'
        )
        
        is_moderate_risk = (
            flood_risk_area == 'Moderate to Low Risk Areas' or
            'moderate' in str(fema_flood_zone).lower()
        )
        
        if is_high_risk:
            risk_level = 'High'
            meets_criteria = False
            elimination_reason = f"SFHA: {sfha_status}, Risk Area: {flood_risk_area}"
        elif is_moderate_risk:
            risk_level = 'Moderate'
            meets_criteria = True
            elimination_reason = None
        else:
            risk_level = 'Low'
            meets_criteria = True
            elimination_reason = None
        
        return {
            'flood_risk_level': risk_level,
            'fema_flood_zone': fema_flood_zone,
            'sfha_status': sfha_status,
            'flood_risk_area': flood_risk_area,
            'meets_flood_criteria': meets_criteria,
            'elimination_reason': elimination_reason,
            'data_source': 'Existing Dataset',
            'confidence': 'High',
            'site_address': site_address,
            'analysis_method': 'Existing Data Processing',
            'requires_verification': False
        }
    
    def _query_fema_flood_api(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Query FEMA flood data API"""
        
        self.analysis_stats['api_queries'] += 1
        
        try:
            # FEMA NFHL identify query
            query_url = f"{self.FEMA_WMS_BASE}/identify"
            
            params = {
                'geometry': f'{longitude},{latitude}',
                'geometryType': 'esriGeometryPoint',
                'sr': '4326',
                'layers': f'visible:{self.FEMA_FLOOD_ZONES_LAYER}',
                'tolerance': '3',
                'mapExtent': f'{longitude-0.01},{latitude-0.01},{longitude+0.01},{latitude+0.01}',
                'imageDisplay': '512,512,96',
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
                        
                        flood_zone = attributes.get('FLD_ZONE', attributes.get('ZONE', 'Unknown'))
                        sfha_flag = attributes.get('SFHA_TF', attributes.get('SFHA', 'Unknown'))
                        
                        return {
                            'flood_zone': flood_zone,
                            'sfha_flag': sfha_flag,
                            'raw_attributes': attributes,
                            'data_source': 'FEMA NFHL API'
                        }
                    
                    # No results found
                    break
                    
                except requests.exceptions.RequestException as e:
                    if attempt == self.retry_attempts - 1:
                        logger.warning(f"FEMA API failed after {self.retry_attempts} attempts: {e}")
                    else:
                        time.sleep(2)  # Wait before retry
                        
        except Exception as e:
            logger.error(f"FEMA API query error: {e}")
        
        return {'flood_zone': 'NO_DATA'}
    
    def _try_alternative_flood_sources(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Try alternative flood data sources"""
        
        # Alternative source 1: ESRI USA Flood Hazard
        try:
            alt_url = self.ALTERNATIVE_ENDPOINTS[0] + "/query"
            params = {
                'where': '1=1',
                'geometry': f'{longitude},{latitude}',
                'geometryType': 'esriGeometryPoint',
                'spatialRel': 'esriSpatialRelIntersects',
                'outFields': 'ZONE,SFHA,RISK_LEVEL',
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            response = requests.get(alt_url, params=params, timeout=self.api_timeout)
            response.raise_for_status()
            data = response.json()
            
            if data.get('features'):
                feature = data['features'][0]
                attrs = feature.get('attributes', {})
                
                return {
                    'flood_zone': attrs.get('ZONE', 'Unknown'),
                    'sfha_flag': attrs.get('SFHA', 'Unknown'),
                    'risk_level': attrs.get('RISK_LEVEL', 'Unknown'),
                    'data_source': 'Alternative Flood Source',
                    'raw_attributes': attrs
                }
                
        except Exception as e:
            logger.debug(f"Alternative flood source failed: {e}")
        
        return None
    
    def _flood_spatial_inference(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Make spatial inference about flood risk based on geographic patterns"""
        
        # Known flood-prone areas in California (approximate)
        high_flood_risk_areas = [
            # Central Valley
            {'name': 'Sacramento Valley', 'lat_min': 38.0, 'lat_max': 40.0, 
             'lng_min': -122.5, 'lng_max': -121.0, 'risk': 'Moderate'},
            # LA River areas  
            {'name': 'LA River Basin', 'lat_min': 33.7, 'lat_max': 34.3,
             'lng_min': -118.7, 'lng_max': -117.8, 'risk': 'Moderate'},
            # San Diego coastal
            {'name': 'San Diego Coastal', 'lat_min': 32.5, 'lat_max': 33.2,
             'lng_min': -117.3, 'lng_max': -117.1, 'risk': 'Low'}
        ]
        
        for area in high_flood_risk_areas:
            if (area['lat_min'] <= latitude <= area['lat_max'] and
                area['lng_min'] <= longitude <= area['lng_max']):
                
                return {
                    'flood_zone': f'{area["risk"]} Risk (Inferred)',
                    'inference_area': area['name'],
                    'risk_level': area['risk'],
                    'confidence': 'Low',
                    'data_source': 'Spatial Inference'
                }
        
        # Default inference for coastal vs inland
        if longitude > -118.0:  # Inland areas
            return {
                'flood_zone': 'Low Risk (Inferred - Inland)',
                'risk_level': 'Low',
                'confidence': 'Low',
                'data_source': 'Geographic Inference'
            }
        
        return None
    
    def _process_api_flood_data(self, api_result: Dict[str, Any], site_address: str,
                              latitude: float, longitude: float) -> Dict[str, Any]:
        """Process flood data obtained from API sources"""
        
        flood_zone = api_result.get('flood_zone', 'Unknown')
        sfha_flag = api_result.get('sfha_flag', 'Unknown')
        
        # Determine risk level based on FEMA flood zone
        if any(zone in flood_zone for zone in self.HIGH_RISK_ZONES):
            risk_level = 'High'
            meets_criteria = False
            elimination_reason = f"Located in FEMA flood zone {flood_zone}"
        elif any(zone in flood_zone for zone in self.MODERATE_RISK_ZONES):
            risk_level = 'Moderate'
            meets_criteria = True
            elimination_reason = None
        elif any(zone in flood_zone for zone in self.LOW_RISK_ZONES):
            risk_level = 'Low'
            meets_criteria = True
            elimination_reason = None
        else:
            risk_level = 'Unknown'
            meets_criteria = None
            elimination_reason = None
        
        # Check SFHA status
        is_sfha = (
            sfha_flag in ['Y', 'Yes', True, 1] or
            any(zone in flood_zone for zone in self.SFHA_ZONES)
        )
        
        if is_sfha and risk_level != 'High':
            risk_level = 'High'
            meets_criteria = False
            elimination_reason = f"Located in SFHA (Special Flood Hazard Area), Zone: {flood_zone}"
        
        return {
            'flood_risk_level': risk_level,
            'fema_flood_zone': flood_zone,
            'sfha_status': 'Yes' if is_sfha else 'No',
            'meets_flood_criteria': meets_criteria,
            'elimination_reason': elimination_reason,
            'data_source': api_result.get('data_source', 'API'),
            'confidence': 'High' if 'API' in api_result.get('data_source', '') else 'Medium',
            'site_address': site_address,
            'coordinates': f"{latitude:.6f}, {longitude:.6f}",
            'analysis_method': 'API Query',
            'requires_verification': False
        }
    
    def _process_inference_result(self, inference_result: Dict[str, Any], site_address: str,
                                latitude: float, longitude: float) -> Dict[str, Any]:
        """Process spatially inferred flood data"""
        
        risk_level = inference_result.get('risk_level', 'Unknown')
        flood_zone = inference_result.get('flood_zone', 'Unknown')
        
        meets_criteria = risk_level in ['Low', 'Moderate']
        
        return {
            'flood_risk_level': risk_level,
            'fema_flood_zone': flood_zone,
            'sfha_status': 'Unknown',
            'meets_flood_criteria': meets_criteria,
            'elimination_reason': None if meets_criteria else f"Inferred high flood risk in {inference_result.get('inference_area', 'unknown area')}",
            'data_source': inference_result.get('data_source', 'Inference'),
            'confidence': inference_result.get('confidence', 'Low'),
            'site_address': site_address,
            'coordinates': f"{latitude:.6f}, {longitude:.6f}",
            'analysis_method': 'Spatial Inference',
            'requires_verification': True,
            'verification_note': 'Result based on spatial inference - recommend manual verification'
        }
    
    def _create_manual_verification_result(self, latitude: float, longitude: float,
                                         site_address: str) -> Dict[str, Any]:
        """Create result requiring manual verification"""
        
        verification_urls = [
            f"https://msc.fema.gov/portal/search?AddressLine={latitude},{longitude}#searchresultsanchor",
            "https://www.fema.gov/flood-maps",
            f"https://www.google.com/maps/@{latitude},{longitude},15z"
        ]
        
        return {
            'flood_risk_level': 'REQUIRES_MANUAL_VERIFICATION',
            'fema_flood_zone': 'Unknown',
            'sfha_status': 'Unknown',
            'meets_flood_criteria': None,
            'elimination_reason': None,
            'data_source': 'Manual Verification Required',
            'confidence': 'Unknown',
            'site_address': site_address,
            'coordinates': f"{latitude:.6f}, {longitude:.6f}",
            'analysis_method': 'Requires Manual Review',
            'requires_verification': True,
            'verification_urls': verification_urls,
            'verification_priority': 'HIGH',
            'verification_note': 'No automated flood data available - manual FEMA map review required'
        }
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get flood analysis statistics"""
        
        total = self.analysis_stats['total_analyzed']
        if total == 0:
            return {'message': 'No flood analyses performed yet'}
        
        return {
            'total_analyzed': total,
            'existing_data_rate': f"{(self.analysis_stats['existing_data_used']/total)*100:.1f}%",
            'api_success_rate': f"{(self.analysis_stats['api_successes']/max(1,self.analysis_stats['api_queries']))*100:.1f}%",
            'inference_rate': f"{(self.analysis_stats['inferences_made']/total)*100:.1f}%",
            'manual_verification_rate': f"{(self.analysis_stats['manual_verification_needed']/total)*100:.1f}%"
        }


def test_flood_analyzer():
    """Test the flood analyzer with sample data"""
    
    analyzer = EnhancedFloodAnalyzer()
    
    # Test cases with different scenarios
    test_cases = [
        {
            'lat': 34.0522, 'lng': -118.2437, 
            'address': 'Downtown Los Angeles',
            'existing_data': {'In SFHA': 'No', 'Flood Risk Area': None, 'Fema Flood Zone': None}
        },
        {
            'lat': 38.5816, 'lng': -121.4944,
            'address': 'Sacramento (flood-prone area)',
            'existing_data': None
        },
        {
            'lat': 37.7749, 'lng': -122.4194,
            'address': 'San Francisco',
            'existing_data': {'In SFHA': 'Yes', 'Flood Risk Area': 'High Risk Areas', 'Fema Flood Zone': 'AE'}
        }
    ]
    
    print("🧪 Testing Enhanced Flood Analyzer")
    print("=" * 60)
    
    for case in test_cases:
        print(f"\\n📍 Testing: {case['address']}")
        result = analyzer.analyze_flood_risk_comprehensive(
            case['lat'], case['lng'], case['existing_data'], case['address']
        )
        
        print(f"   Risk Level: {result.get('flood_risk_level', 'Unknown')}")
        print(f"   FEMA Zone: {result.get('fema_flood_zone', 'Unknown')}")
        print(f"   SFHA Status: {result.get('sfha_status', 'Unknown')}")
        print(f"   Meets Criteria: {result.get('meets_flood_criteria', 'Unknown')}")
        print(f"   Data Source: {result.get('data_source', 'Unknown')}")
        print(f"   Requires Verification: {result.get('requires_verification', False)}")
    
    print(f"\\n📊 Analysis Statistics:")
    stats = analyzer.get_analysis_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    test_flood_analyzer()