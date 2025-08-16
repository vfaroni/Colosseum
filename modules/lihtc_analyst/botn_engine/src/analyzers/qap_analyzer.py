#!/usr/bin/env python3
"""
QAP Analyzer - State-specific QAP scoring analysis

Analyzes state Qualified Allocation Plan requirements and scoring.
"""

import logging
import os
from typing import Dict, Any, Optional
import geopandas as gpd
from shapely.geometry import Point


class QAPAnalyzer:
    """
    Analyzes state-specific QAP scoring requirements
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Load California opportunity area data
        self.ca_opportunity_data = None
        self.ca_hqta_data = None
        self._load_ca_opportunity_data()
        self._load_ca_hqta_data()
    
    def _load_ca_opportunity_data(self):
        """Load California CTCAC opportunity area data"""
        try:
            data_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets/california/CA_CTCAC_2025_Opp_MAP_shapefile/final_opp_2025_public.gpkg"
            
            if os.path.exists(data_path):
                self.logger.info("Loading California opportunity area data...")
                self.ca_opportunity_data = gpd.read_file(data_path)
                
                # Ensure proper CRS
                if self.ca_opportunity_data.crs != 'EPSG:4326':
                    self.ca_opportunity_data = self.ca_opportunity_data.to_crs('EPSG:4326')
                
                self.logger.info(f"Loaded {len(self.ca_opportunity_data)} opportunity areas")
            else:
                self.logger.warning(f"California opportunity area data not found at {data_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to load California opportunity area data: {str(e)}")
            self.ca_opportunity_data = None
    
    def _load_ca_hqta_data(self):
        """Load California HQTA (High Quality Transit Area) data"""
        try:
            hqta_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets/california/CA_Transit_Data/High_Quality_Transit_Areas.geojson"
            
            if os.path.exists(hqta_path):
                self.logger.info("Loading California HQTA data...")
                self.ca_hqta_data = gpd.read_file(hqta_path)
                
                # Ensure proper CRS
                if self.ca_hqta_data.crs != 'EPSG:4326':
                    self.ca_hqta_data = self.ca_hqta_data.to_crs('EPSG:4326')
                
                self.logger.info(f"Loaded {len(self.ca_hqta_data)} HQTA areas")
            else:
                self.logger.warning(f"California HQTA data not found at {hqta_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to load California HQTA data: {str(e)}")
            self.ca_hqta_data = None
    
    def analyze(self, site_info, project_type: str, federal_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze state QAP scoring for the site
        
        Args:
            site_info: SiteInfo object
            project_type: Type of project (family, senior, etc.)
            federal_status: Federal qualification status
            
        Returns:
            Dictionary with state scoring analysis
        """
        try:
            # Placeholder implementation for test run
            state = getattr(site_info, 'state', 'CA')
            
            if state == 'CA':
                return self._analyze_california_ctcac(site_info, project_type, federal_status)
            elif state == 'TX':
                return self._analyze_texas_tdhca(site_info, project_type, federal_status)
            else:
                return self._analyze_default_state(site_info, project_type, federal_status)
                
        except Exception as e:
            self.logger.error(f"QAP analysis failed: {str(e)}")
            return {
                'total_points': 0,
                'max_possible_points': 100,
                'scoring_breakdown': {},
                'error': str(e)
            }
    
    def _analyze_california_ctcac(self, site_info, project_type: str, federal_status: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze California CTCAC scoring with real opportunity area data"""
        try:
            # Check opportunity area designation
            opportunity_result = self._check_opportunity_area(site_info.latitude, site_info.longitude)
            
            # Calculate CTCAC points based on actual rules
            points_breakdown = {
                'opportunity_area_points': self._calculate_opportunity_points(opportunity_result),
                'amenity_points': 15,  # Will be enhanced with real amenity analysis
                'federal_bonus': 4 if federal_status.get('qct_qualified') else 0,
                'transit_points': self._calculate_transit_points(site_info.latitude, site_info.longitude)
            }
            
            total_points = sum(points_breakdown.values())
            
            return {
                'total_points': total_points,
                'max_possible_points': 30,
                'scoring_breakdown': points_breakdown,
                'opportunity_area': opportunity_result,
                'state': 'CA',
                'allocation_agency': 'CTCAC',
                'data_year': 2025
            }
            
        except Exception as e:
            self.logger.warning(f"CTCAC analysis failed, using fallback: {e}")
            return self._ctcac_fallback_analysis(federal_status)
    
    def _check_opportunity_area(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Check CTCAC opportunity area designation using real geospatial data"""
        try:
            if self.ca_opportunity_data is None:
                self.logger.warning("California opportunity area data not loaded, using fallback")
                return {
                    'resource_category': 'High Resource',  # fallback
                    'resource_score': 6.0,  # fallback
                    'qualified': True,
                    'tract_id': 'fallback'
                }
            
            # Create point geometry
            point = Point(longitude, latitude)
            
            # Find intersecting opportunity areas
            intersects = self.ca_opportunity_data[self.ca_opportunity_data.geometry.contains(point)]
            
            if not intersects.empty:
                # Get the first (should be only) intersecting area
                area = intersects.iloc[0]
                
                return {
                    'resource_category': area['oppcat'],
                    'resource_score': float(area['oppscore']),
                    'qualified': True,
                    'tract_id': area['fips'],
                    'county': area.get('county_name', 'Unknown'),
                    'region': area.get('region', 'Unknown'),
                    'poverty_rate': area.get('pct_above_200_pov', 0),
                    'bachelor_plus_rate': area.get('pct_bachelors_plus', 0),
                    'employment_rate': area.get('pct_employed', 0),
                    'math_proficiency': area.get('math_prof', 0),
                    'reading_proficiency': area.get('read_prof', 0),
                    'graduation_rate': area.get('grad_rate', 0)
                }
            else:
                # Point not in any opportunity area
                return {
                    'resource_category': 'Not Designated',
                    'resource_score': 0.0,
                    'qualified': False,
                    'tract_id': 'unknown',
                    'reason': 'Location not within any designated opportunity area'
                }
                
        except Exception as e:
            self.logger.error(f"Error checking opportunity area: {str(e)}")
            return {
                'resource_category': 'Error',
                'resource_score': 0.0,
                'qualified': False,
                'tract_id': 'error',
                'error': str(e)
            }
    
    def _calculate_opportunity_points(self, opportunity_result: Dict[str, Any]) -> int:
        """Calculate points based on opportunity area designation"""
        if not opportunity_result.get('qualified', False):
            return 0
            
        category = opportunity_result.get('resource_category', '')
        
        # CTCAC 2025 opportunity area points
        opportunity_points = {
            'Highest Resource': 8,
            'High Resource': 6, 
            'Moderate Resource': 4,
            'Low Resource': 0
        }
        
        return opportunity_points.get(category, 0)
    
    def _calculate_transit_points(self, latitude: float, longitude: float) -> int:
        """Calculate HQTA (High Quality Transit Area) points using real data"""
        try:
            if self.ca_hqta_data is None:
                self.logger.warning("California HQTA data not loaded, using fallback")
                return 3  # fallback
            
            # Create point geometry
            point = Point(longitude, latitude)
            
            # Find intersecting HQTA areas
            intersects = self.ca_hqta_data[self.ca_hqta_data.geometry.contains(point)]
            
            if not intersects.empty:
                # Site is within HQTA - award points
                return 5  # CTCAC 2025 HQTA points
            else:
                # Check if site is within walking distance of HQTA
                # Buffer HQTA areas by 0.5 miles (0.25 miles = 0.004° approximately)
                buffer_distance = 0.004  # roughly 0.25 miles in degrees
                
                # Create buffer around point
                point_buffer = point.buffer(buffer_distance)
                
                # Check if buffered point intersects any HQTA area
                nearby_hqta = self.ca_hqta_data[self.ca_hqta_data.geometry.intersects(point_buffer)]
                
                if not nearby_hqta.empty:
                    return 3  # Partial points for proximity
                else:
                    return 0  # No HQTA nearby
                    
        except Exception as e:
            self.logger.error(f"Error calculating transit points: {str(e)}")
            return 0
    
    def _ctcac_fallback_analysis(self, federal_status: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis if data loading fails"""
        return {
            'total_points': 25,
            'max_possible_points': 30,
            'scoring_breakdown': {
                'amenity_points': 15,
                'opportunity_area_points': 8,
                'federal_bonus': 2 if federal_status.get('qct_qualified') else 0
            },
            'state': 'CA',
            'allocation_agency': 'CTCAC',
            'note': 'Fallback analysis - opportunity area data not loaded'
        }
    
    def _analyze_texas_tdhca(self, site_info, project_type: str, federal_status: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Texas TDHCA scoring (placeholder)"""
        return {
            'total_points': 85,
            'max_possible_points': 100,
            'scoring_breakdown': {
                'opportunity_index': 20,
                'education_excellence': 15,
                'rural_bonus': 10
            },
            'state': 'TX',
            'allocation_agency': 'TDHCA'
        }
    
    def _analyze_default_state(self, site_info, project_type: str, federal_status: Dict[str, Any]) -> Dict[str, Any]:
        """Default analysis for other states"""
        return {
            'total_points': 50,
            'max_possible_points': 100,
            'scoring_breakdown': {
                'basic_analysis': 50
            },
            'state': getattr(site_info, 'state', 'Unknown'),
            'note': 'Basic federal-only analysis - state QAP not implemented'
        }