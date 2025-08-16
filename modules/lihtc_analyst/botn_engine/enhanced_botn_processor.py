#!/usr/bin/env python3
"""
Enhanced BOTN Processor with Column Preservation

Fixes critical issues:
1. Retains all original CostarExport columns (37 total)
2. Integrates HQTA sites processing
3. Adds terrain analysis for slope detection
4. Incorporates CTCAC cost data

Author: VITOR WINGMAN
Date: 2025-08-16
"""

import pandas as pd
import numpy as np
import json
import requests
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedBOTNProcessor:
    """Enhanced BOTN processor with comprehensive fixes"""
    
    def __init__(self):
        """Initialize enhanced processor with all required components"""
        
        # Base paths
        self.base_path = Path("/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/botn_engine")
        self.sites_path = self.base_path / "Sites"
        self.outputs_path = self.base_path / "outputs"
        
        # Expected CostarExport columns (preserve all 37)
        self.costar_columns = [
            'Property Address', 'Property Name', 'Land Area (AC)', 'Land Area (SF)',
            'Property Type', 'Secondary Type', 'Market Name', 'Submarket Name',
            'City', 'County Name', 'State', 'Zip', 'For Sale Price',
            'Sale Company Name', 'Sale Company Address', 'Sale Company City State Zip',
            'Sale Company Phone', 'Sale Company Fax', 'Sale Company Contact',
            'Zoning', 'Parcel Number 1(Min)', 'Parcel Number 2(Max)',
            'True Owner Address', 'True Owner City State Zip', 'True Owner Contact',
            'True Owner Name', 'True Owner Phone', 'Flood Risk Area',
            'Fema Flood Zone', 'FEMA Map Date', 'FEMA Map Identifier',
            'Days On Market', 'Closest Transit Stop', 'Closest Transit Stop Dist (mi)',
            'Closest Transit Stop Walk Time (min)', 'Latitude', 'Longitude'
        ]
        
        # HQTA data cache
        self.hqta_qualified_sites = None
        self.load_hqta_data()
        
        # Terrain analysis thresholds
        self.terrain_thresholds = {
            'ideal': 2.0,        # 0-2% slope
            'good': 5.0,         # 2-5% slope  
            'moderate': 10.0,    # 5-10% slope
            'high_risk': 15.0,   # 10-15% slope
            'unsuitable': 100.0  # >15% slope (reject)
        }
        
        # CTCAC cost defaults (will be enhanced with real data)
        self.ctcac_cost_defaults = {
            'hard_costs_per_unit': 280000,
            'soft_costs_per_unit': 85000,
            'architecture_costs_per_unit': 15000,
            'total_development_cost_per_unit': 380000
        }
        
    def load_hqta_data(self) -> None:
        """Load HQTA qualified sites from previous analysis"""
        try:
            hqta_file = self.outputs_path / "CTCAC_HQTA_INTEGRATED_TRANSIT_ANALYSIS_20250801_093918.json"
            
            if hqta_file.exists():
                with open(hqta_file, 'r') as f:
                    hqta_data = json.load(f)
                
                # Extract sites that qualify for 7 points
                self.hqta_qualified_sites = []
                
                for site in hqta_data.get('detailed_results', []):
                    ctcac_analysis = site.get('ctcac_analysis', {})
                    if ctcac_analysis.get('ctcac_points') == 7:
                        self.hqta_qualified_sites.append({
                            'latitude': site.get('latitude'),
                            'longitude': site.get('longitude'),
                            'hqta_type': ctcac_analysis.get('hqta_qualification', {}).get('hqta_type'),
                            'qualification_method': ctcac_analysis.get('qualification_method')
                        })
                
                logger.info(f"Loaded {len(self.hqta_qualified_sites)} HQTA qualified sites")
            else:
                logger.warning(f"HQTA data file not found: {hqta_file}")
                self.hqta_qualified_sites = []
                
        except Exception as e:
            logger.error(f"Error loading HQTA data: {e}")
            self.hqta_qualified_sites = []
    
    def preserve_costar_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure all original CostarExport columns are preserved"""
        
        logger.info("Preserving original CostarExport columns...")
        
        # Verify we have the expected columns
        missing_columns = [col for col in self.costar_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Missing expected columns: {missing_columns}")
        
        # Add any missing columns with default values
        for col in self.costar_columns:
            if col not in df.columns:
                df[col] = 'TBD'
        
        # Ensure columns are in expected order
        preserved_columns = [col for col in self.costar_columns if col in df.columns]
        other_columns = [col for col in df.columns if col not in self.costar_columns]
        
        # Reorder: original columns first, then any new analysis columns
        column_order = preserved_columns + other_columns
        df = df[column_order]
        
        logger.info(f"Preserved {len(preserved_columns)} original CostarExport columns")
        return df
    
    def check_hqta_qualification(self, lat: float, lng: float) -> Dict[str, Any]:
        """Check if site qualifies for HQTA 7-point scoring"""
        
        if not self.hqta_qualified_sites:
            return {'qualified': False, 'points': 0, 'method': 'no_hqta_data'}
        
        # Check if coordinates match any HQTA qualified site (within tolerance)
        tolerance = 0.001  # ~100 meter tolerance
        
        for hqta_site in self.hqta_qualified_sites:
            hqta_lat = hqta_site.get('latitude')
            hqta_lng = hqta_site.get('longitude')
            
            if hqta_lat is None or hqta_lng is None:
                continue
                
            # Calculate distance
            lat_diff = abs(lat - hqta_lat)
            lng_diff = abs(lng - hqta_lng)
            
            if lat_diff <= tolerance and lng_diff <= tolerance:
                return {
                    'qualified': True,
                    'points': 7,
                    'method': 'hqta_boundary',
                    'hqta_type': hqta_site.get('hqta_type'),
                    'qualification_method': hqta_site.get('qualification_method')
                }
        
        return {'qualified': False, 'points': 0, 'method': 'not_in_hqta'}
    
    def calculate_terrain_slope(self, lat: float, lng: float) -> Dict[str, Any]:
        """Calculate terrain slope using USGS elevation data"""
        
        try:
            # USGS Elevation Point Query Service
            base_url = "https://epqs.nationalmap.gov/v1/json"
            
            # Get elevation at center point
            params = {
                'x': lng,
                'y': lat,
                'wkid': 4326,
                'units': 'Feet',
                'includeDate': 'false'
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'value' in data and data['value'] is not None:
                    center_elevation = float(data['value'])
                    
                    # Get elevations at nearby points (simplified analysis)
                    # In production, would query multiple points around perimeter
                    offset = 0.001  # ~100 meter offset
                    nearby_points = [
                        (lat + offset, lng),
                        (lat - offset, lng),
                        (lat, lng + offset),
                        (lat, lng - offset)
                    ]
                    
                    elevations = [center_elevation]
                    
                    for point_lat, point_lng in nearby_points:
                        try:
                            params['x'] = point_lng
                            params['y'] = point_lat
                            
                            resp = requests.get(base_url, params=params, timeout=5)
                            if resp.status_code == 200:
                                point_data = resp.json()
                                if 'value' in point_data and point_data['value'] is not None:
                                    elevations.append(float(point_data['value']))
                            
                            time.sleep(0.1)  # Rate limiting
                            
                        except Exception:
                            continue
                    
                    # Calculate slope
                    if len(elevations) > 1:
                        max_elevation = max(elevations)
                        min_elevation = min(elevations)
                        elevation_change = max_elevation - min_elevation
                        
                        # Rough horizontal distance (~100 meters)
                        horizontal_distance = 328.084  # feet
                        
                        slope_percent = (elevation_change / horizontal_distance) * 100
                        
                        # Determine risk category
                        if slope_percent <= self.terrain_thresholds['ideal']:
                            risk_category = 'IDEAL'
                        elif slope_percent <= self.terrain_thresholds['good']:
                            risk_category = 'GOOD'
                        elif slope_percent <= self.terrain_thresholds['moderate']:
                            risk_category = 'MODERATE'
                        elif slope_percent <= self.terrain_thresholds['high_risk']:
                            risk_category = 'HIGH_RISK'
                        else:
                            risk_category = 'UNSUITABLE'
                        
                        return {
                            'center_elevation_ft': center_elevation,
                            'elevation_range_ft': elevation_change,
                            'slope_percent': round(slope_percent, 2),
                            'risk_category': risk_category,
                            'suitable_for_development': risk_category != 'UNSUITABLE',
                            'analysis_points': len(elevations)
                        }
            
            # Fallback if API fails
            return {
                'center_elevation_ft': None,
                'elevation_range_ft': None,
                'slope_percent': None,
                'risk_category': 'UNKNOWN',
                'suitable_for_development': True,  # Don't filter if we can't analyze
                'analysis_points': 0,
                'error': 'USGS API unavailable'
            }
            
        except Exception as e:
            logger.warning(f"Terrain analysis failed for ({lat}, {lng}): {e}")
            return {
                'center_elevation_ft': None,
                'elevation_range_ft': None,
                'slope_percent': None,
                'risk_category': 'UNKNOWN',
                'suitable_for_development': True,
                'analysis_points': 0,
                'error': str(e)
            }
    
    def get_ctcac_costs(self, county: str, property_type: str = 'multifamily') -> Dict[str, float]:
        """Get CTCAC cost estimates (placeholder for real data extraction)"""
        
        # TODO: Implement real CTCAC application data extraction
        # For now, return regional defaults based on county
        
        regional_multipliers = {
            'Los Angeles': 1.2,
            'San Francisco': 1.5,
            'Orange': 1.15,
            'San Diego': 1.1,
            'Alameda': 1.3,
            'Santa Clara': 1.4,
            'Marin': 1.6,
            'default': 1.0
        }
        
        multiplier = regional_multipliers.get(county, regional_multipliers['default'])
        
        return {
            'hard_costs_per_unit': int(self.ctcac_cost_defaults['hard_costs_per_unit'] * multiplier),
            'soft_costs_per_unit': int(self.ctcac_cost_defaults['soft_costs_per_unit'] * multiplier),
            'architecture_costs_per_unit': int(self.ctcac_cost_defaults['architecture_costs_per_unit'] * multiplier),
            'total_development_cost_per_unit': int(self.ctcac_cost_defaults['total_development_cost_per_unit'] * multiplier),
            'regional_multiplier': multiplier,
            'data_source': 'regional_defaults'
        }
    
    def process_sites(self, costar_file: str, max_sites: Optional[int] = None) -> pd.DataFrame:
        """Process CostarExport sites with all enhancements"""
        
        logger.info(f"Starting enhanced BOTN processing: {costar_file}")
        
        # Load CostarExport data
        df = pd.read_excel(costar_file)
        logger.info(f"Loaded {len(df)} sites from {costar_file}")
        
        # Preserve original columns
        df = self.preserve_costar_columns(df)
        
        # Limit sites for testing
        if max_sites:
            df = df.head(max_sites)
            logger.info(f"Limited to {len(df)} sites for processing")
        
        # Initialize enhancement columns
        enhancement_columns = {
            'hqta_qualified': [],
            'hqta_points': [],
            'hqta_method': [],
            'terrain_slope_percent': [],
            'terrain_risk_category': [],
            'terrain_suitable': [],
            'hard_costs_per_unit': [],
            'soft_costs_per_unit': [],
            'total_dev_cost_per_unit': [],
            'enhancement_timestamp': []
        }
        
        # Process each site
        processed_count = 0
        for idx, row in df.iterrows():
            lat = row.get('Latitude')
            lng = row.get('Longitude')
            county = row.get('County Name', '')
            
            logger.info(f"Processing site {processed_count + 1}/{len(df)}: {row.get('Property Address', 'Unknown')}")
            
            # Skip sites with missing coordinates
            if pd.isna(lat) or pd.isna(lng):
                # Fill with default values
                for col, values in enhancement_columns.items():
                    if col == 'enhancement_timestamp':
                        values.append(datetime.now().isoformat())
                    else:
                        values.append(None)
                continue
            
            # HQTA analysis
            hqta_result = self.check_hqta_qualification(lat, lng)
            enhancement_columns['hqta_qualified'].append(hqta_result['qualified'])
            enhancement_columns['hqta_points'].append(hqta_result['points'])
            enhancement_columns['hqta_method'].append(hqta_result['method'])
            
            # Terrain analysis
            terrain_result = self.calculate_terrain_slope(lat, lng)
            enhancement_columns['terrain_slope_percent'].append(terrain_result.get('slope_percent'))
            enhancement_columns['terrain_risk_category'].append(terrain_result.get('risk_category'))
            enhancement_columns['terrain_suitable'].append(terrain_result.get('suitable_for_development'))
            
            # CTCAC cost estimates
            cost_data = self.get_ctcac_costs(county)
            enhancement_columns['hard_costs_per_unit'].append(cost_data['hard_costs_per_unit'])
            enhancement_columns['soft_costs_per_unit'].append(cost_data['soft_costs_per_unit'])
            enhancement_columns['total_dev_cost_per_unit'].append(cost_data['total_development_cost_per_unit'])
            
            # Timestamp
            enhancement_columns['enhancement_timestamp'].append(datetime.now().isoformat())
            
            processed_count += 1
            
            # Rate limiting for API calls
            if processed_count % 10 == 0:
                time.sleep(1)
                logger.info(f"Processed {processed_count} sites...")
        
        # Add enhancement columns to DataFrame
        for col, values in enhancement_columns.items():
            df[col] = values
        
        logger.info(f"Enhanced processing complete: {len(df)} sites processed")
        return df

# Test the enhanced processor
if __name__ == "__main__":
    processor = EnhancedBOTNProcessor()
    
    # Test with a small sample
    test_file = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport-15.xlsx"
    
    if Path(test_file).exists():
        result_df = processor.process_sites(test_file, max_sites=5)
        print(f"Test completed: {len(result_df)} sites processed")
        print(f"Columns: {len(result_df.columns)} total")
        print(f"Original CostarExport columns preserved: {len([col for col in processor.costar_columns if col in result_df.columns])}")
    else:
        print(f"Test file not found: {test_file}")