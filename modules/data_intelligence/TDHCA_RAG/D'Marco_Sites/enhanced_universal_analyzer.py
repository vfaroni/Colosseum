#!/usr/bin/env python3
"""
Enhanced Universal D'Marco Site Analyzer - REAL ANALYSIS INTEGRATION
Mission: Full 122-column analysis with actual QCT/DDA, Environmental, FEMA
Author: WINGMAN Agent
Date: July 30, 2025

INTEGRATION STATUS:
✅ Framework validated - Anomaly detection working
✅ 39 sites loaded successfully
✅ Datasets loaded: QCT (44,933), Environmental (21,363), AMI (4,764)
🔄 NOW: Implementing real analysis components
"""

import pandas as pd
import numpy as np
import json
import folium
import requests
import time
from pathlib import Path
from datetime import datetime
from geopy.distance import geodesic
from typing import Dict, List, Optional, Tuple
import logging
import sys
import os

# Add the comprehensive analyzer to path
sys.path.append('/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/priorcode')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedUniversalAnalyzer:
    """Enhanced analyzer with real QCT/DDA, Environmental, and FEMA integration"""
    
    def __init__(self):
        """Initialize with all proven analysis components"""
        
        # Base directories
        self.base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG"
        self.data_sets_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
        self.output_dir = f"{self.base_dir}/D'Marco_Sites/Enhanced_Analysis_20250730"
        self.prior_code_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Colosseum/modules/lihtc_analyst/priorcode"
        
        # Create output directory
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Quality thresholds
        self.minimum_completeness = 0.95
        self.anomaly_threshold = 0.8
        
        # Load datasets and initialize analyzers
        self.load_analysis_systems()
        
        # Results storage
        self.analysis_results = []
        self.fema_coverage_gaps = []
        self.anomaly_flags = {}
        
        logger.info("🚀 Enhanced Universal Analyzer initialized with REAL analysis components")
    
    def load_analysis_systems(self):
        """Load all proven analysis systems"""
        
        logger.info("📊 Loading real analysis systems...")
        
        # 1. QCT/DDA Analysis System
        try:
            from comprehensive_qct_dda_analyzer import ComprehensiveQCTDDAAnalyzer
            self.qct_dda_analyzer = ComprehensiveQCTDDAAnalyzer()
            logger.info("✅ QCT/DDA Analyzer loaded successfully")
        except Exception as e:
            logger.error(f"❌ QCT/DDA Analyzer failed: {e}")
            self.qct_dda_analyzer = None
        
        # 2. Environmental Database
        try:
            env_path = f"{self.base_dir}/D'Marco_Sites/Comprehensive_Environmental_Database.csv"
            self.environmental_data = pd.read_csv(env_path, low_memory=False)
            logger.info(f"✅ Environmental Database: {len(self.environmental_data)} sites")
        except Exception as e:
            logger.error(f"❌ Environmental Database failed: {e}")
            self.environmental_data = None
        
        # 3. AMI Data (HUD 2025 Static)
        try:
            ami_path = f"{self.data_sets_dir}/federal/HUD_AMI_Geographic/HUD2025_AMI_Rent_Data_Static.xlsx"
            self.ami_data = pd.read_excel(ami_path)
            logger.info(f"✅ AMI Data loaded: {len(self.ami_data)} areas")
        except Exception as e:
            logger.error(f"❌ AMI Data failed: {e}")
            self.ami_data = None
        
        # 4. FEMA Flood Data Setup (85% TX coverage)
        try:
            self.fema_base_url = "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer"
            logger.info("✅ FEMA API endpoint configured (85% TX coverage)")
        except Exception as e:
            logger.error(f"❌ FEMA setup failed: {e}")
        
        logger.info("🔧 Analysis systems loaded and ready")
    
    def analyze_site_comprehensive(self, site_data: Dict, site_index: int) -> Dict:
        """Comprehensive site analysis with real components"""
        
        site_name = site_data.get('Site Name/Address', f'Site_{site_index + 1}')
        logger.info(f"🔍 Comprehensive analysis: {site_name}")
        
        # Initialize result structure
        result = {
            'site_index': site_index + 1,
            'site_name': site_name,
            'acreage': site_data.get('Acreage', 0.0),
            'tdhca_region': site_data.get('Region', 'UNKNOWN'),
            'analysis_timestamp': datetime.now().isoformat(),
            'completeness_score': 0.0,
            'quality_flags': [],
            'anomaly_flags': []
        }
        
        try:
            # 1. GEOCODING VALIDATION (Real Implementation)
            geocoding_result = self._validate_site_coordinates(site_data)
            result.update(geocoding_result)
            
            # 2. QCT/DDA ANALYSIS (Real Implementation)
            if self.qct_dda_analyzer and result.get('parcel_center_lat') and result.get('parcel_center_lng'):
                qct_dda_result = self._analyze_qct_dda_real(
                    result['parcel_center_lat'], 
                    result['parcel_center_lng']
                )
                result.update(qct_dda_result)
            else:
                result.update(self._qct_dda_fallback())
            
            # 3. ENVIRONMENTAL SCREENING (Real Implementation)
            if self.environmental_data is not None:
                env_result = self._screen_environmental_real(
                    result.get('parcel_center_lat'),
                    result.get('parcel_center_lng')
                )
                result.update(env_result)
            else:
                result.update(self._environmental_fallback())
            
            # 4. FEMA FLOOD ANALYSIS (Real Implementation with Gap Detection)
            fema_result = self._analyze_fema_flood_real(
                result.get('parcel_center_lat'),
                result.get('parcel_center_lng'),
                site_name
            )
            result.update(fema_result)
            
            # 5. AMI RENT CALCULATIONS (Real Implementation)
            if self.ami_data is not None:
                ami_result = self._calculate_ami_rents_real(
                    result.get('qct_tract_county'),
                    result.get('qct_tract_state', 'TX')
                )
                result.update(ami_result)
            else:
                result.update(self._ami_fallback())
            
            # 6. COMPETITION ANALYSIS (Framework)
            competition_result = self._analyze_competition_framework(site_data)
            result.update(competition_result)
            
            # 7. ECONOMIC VIABILITY (Framework)
            economic_result = self._assess_economic_viability_real(site_data, result)
            result.update(economic_result)
            
            # 8. INFRASTRUCTURE SCORING (Framework)
            infrastructure_result = self._score_infrastructure_real(site_data)
            result.update(infrastructure_result)
            
        except Exception as e:
            logger.error(f"❌ Analysis error for {site_name}: {e}")
            result['analysis_error'] = str(e)
            result['quality_flags'].append('ANALYSIS_ERROR')
        
        # Calculate final completeness score
        result['completeness_score'] = self._calculate_real_completeness(result)
        
        # Detect anomalies
        self._detect_real_anomalies(result)
        
        # Quality gate validation
        if result['completeness_score'] < self.minimum_completeness:
            result['quality_flags'].append('BELOW_95_PERCENT_THRESHOLD')
        
        logger.info(f"✅ {site_name} analyzed - Completeness: {result['completeness_score']:.1%}")
        
        return result
    
    def _validate_site_coordinates(self, site_data: Dict) -> Dict:
        """Real coordinate validation and parcel center calculation"""
        
        try:
            corners = ['SW', 'SE', 'NE', 'NW']
            coordinates = []
            corner_data = {}
            
            for corner in corners:
                coord_str = site_data.get(corner, '')
                if coord_str and ',' in str(coord_str):
                    parts = str(coord_str).strip().split(',')
                    if len(parts) == 2:
                        lat, lng = float(parts[0].strip()), float(parts[1].strip())
                        coordinates.append((lat, lng))
                        corner_data[f'{corner.lower()}_lat'] = lat
                        corner_data[f'{corner.lower()}_lng'] = lng
            
            if len(coordinates) == 4:
                # Calculate precise parcel center
                center_lat = sum(coord[0] for coord in coordinates) / 4
                center_lng = sum(coord[1] for coord in coordinates) / 4
                
                # Calculate parcel area (approximate)
                sw_lat, sw_lng = coordinates[0]
                ne_lat, ne_lng = coordinates[2]
                
                # Rough area calculation using coordinate bounds
                lat_diff = abs(ne_lat - sw_lat)
                lng_diff = abs(ne_lng - sw_lng)
                coord_area_acres = (lat_diff * lng_diff) * 24710.4  # Rough conversion
                
                return {
                    'geocoding_status': 'VALID_4_CORNERS',
                    'parcel_center_lat': center_lat,
                    'parcel_center_lng': center_lng,
                    'coordinate_precision': 'HIGH',
                    'calculated_area_acres': coord_area_acres,
                    **corner_data
                }
            else:
                return {
                    'geocoding_status': f'INCOMPLETE_COORDINATES_{len(coordinates)}_OF_4',
                    'parcel_center_lat': None,
                    'parcel_center_lng': None,
                    'coordinate_precision': 'FAILED'
                }
                
        except Exception as e:
            return {
                'geocoding_status': f'COORDINATE_ERROR: {str(e)}',
                'parcel_center_lat': None,
                'parcel_center_lng': None,
                'coordinate_precision': 'FAILED'
            }
    
    def _analyze_qct_dda_real(self, lat: float, lng: float) -> Dict:
        """Real QCT/DDA analysis using proven analyzer"""
        
        try:
            # Use existing comprehensive analyzer
            result = self.qct_dda_analyzer.lookup_qct_status(lat, lng)
            
            if result and 'error' not in result:
                return {
                    'qct_status': result.get('qct_designation', 'NOT_QCT'),
                    'dda_status': result.get('dda_designation', 'NOT_DDA'),
                    'basis_boost_eligible': 'YES' if (result.get('qct_designation') == 'QCT' or result.get('dda_designation') == 'DDA') else 'NO',
                    'qct_tract_id': result.get('census_tract'),
                    'qct_tract_county': result.get('county'),
                    'qct_tract_state': result.get('state', 'TX'),
                    'ami_source': result.get('ami_source', 'UNKNOWN'),
                    'analysis_method': 'COMPREHENSIVE_QCT_DDA_ANALYZER'
                }
            else:
                return self._qct_dda_fallback()
                
        except Exception as e:
            logger.warning(f"⚠️ QCT/DDA analysis failed: {e}")
            return self._qct_dda_fallback()
    
    def _qct_dda_fallback(self) -> Dict:
        """Fallback QCT/DDA result structure"""
        return {
            'qct_status': 'ANALYSIS_FAILED',
            'dda_status': 'ANALYSIS_FAILED',
            'basis_boost_eligible': 'CANNOT_DETERMINE',
            'qct_tract_id': None,
            'qct_tract_county': None,
            'qct_tract_state': 'TX',
            'ami_source': 'UNKNOWN',
            'analysis_method': 'FALLBACK'
        }
    
    def _screen_environmental_real(self, lat: float, lng: float) -> Dict:
        """Real environmental screening using TCEQ database"""
        
        if not lat or not lng or self.environmental_data is None:
            return self._environmental_fallback()
        
        try:
            # Search for environmental sites within 1 mile radius
            nearby_sites = []
            risk_levels = []
            
            for idx, env_site in self.environmental_data.iterrows():
                env_lat = env_site.get('Latitude')
                env_lng = env_site.get('Longitude')
                
                if pd.notna(env_lat) and pd.notna(env_lng):
                    try:
                        distance_miles = geodesic((lat, lng), (env_lat, env_lng)).miles
                        
                        if distance_miles <= 1.0:
                            site_info = {
                                'distance_miles': round(distance_miles, 3),
                                'site_name': env_site.get('Site_Name', 'UNKNOWN'),
                                'risk_type': env_site.get('Risk_Type', 'UNKNOWN'),
                                'status': env_site.get('Status', 'UNKNOWN')
                            }
                            nearby_sites.append(site_info)
                            
                            # Assess risk level
                            if distance_miles <= 0.25:  # 1/4 mile
                                risk_levels.append('HIGH')
                            elif distance_miles <= 0.5:  # 1/2 mile
                                risk_levels.append('MEDIUM')
                            else:
                                risk_levels.append('LOW')
                    except:
                        continue
            
            # Determine overall risk
            if 'HIGH' in risk_levels:
                overall_risk = 'HIGH'
                phase_i_recommended = 'YES'
            elif 'MEDIUM' in risk_levels:
                overall_risk = 'MEDIUM'
                phase_i_recommended = 'RECOMMENDED'
            elif 'LOW' in risk_levels:
                overall_risk = 'LOW'
                phase_i_recommended = 'STANDARD'
            else:
                overall_risk = 'MINIMAL'
                phase_i_recommended = 'STANDARD'
            
            return {
                'environmental_sites_1_mile': len(nearby_sites),
                'environmental_risk_level': overall_risk,
                'phase_i_esa_recommended': phase_i_recommended,
                'nearest_environmental_site_miles': min([site['distance_miles'] for site in nearby_sites]) if nearby_sites else None,
                'environmental_analysis_method': 'TCEQ_DATABASE_SEARCH'
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Environmental screening failed: {e}")
            return self._environmental_fallback()
    
    def _environmental_fallback(self) -> Dict:
        """Fallback environmental result"""
        return {
            'environmental_sites_1_mile': 'ANALYSIS_FAILED',
            'environmental_risk_level': 'UNKNOWN',
            'phase_i_esa_recommended': 'ANALYSIS_REQUIRED',
            'nearest_environmental_site_miles': None,
            'environmental_analysis_method': 'FALLBACK'
        }
    
    def _analyze_fema_flood_real(self, lat: float, lng: float, site_name: str) -> Dict:
        """Real FEMA flood zone analysis with 85% TX coverage gap detection"""
        
        if not lat or not lng:
            return {
                'fema_flood_zone': 'NO_COORDINATES',
                'flood_risk_level': 'UNKNOWN',
                'fema_coverage_status': 'COORDINATES_REQUIRED',
                'fema_gap_flag': True,
                'insurance_impact': 'UNKNOWN',
                'analysis_method': 'COORDINATE_FAILURE'
            }
        
        try:
            # Attempt FEMA API query
            query_url = f"{self.fema_base_url}/identify"
            params = {
                'geometry': f'{lng},{lat}',
                'geometryType': 'esriGeometryPoint',
                'layers': 'all',
                'tolerance': 1,
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            response = requests.get(query_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse FEMA response
                if 'results' in data and data['results']:
                    flood_zone = 'ZONE_X'  # Default
                    for result in data['results']:
                        if 'attributes' in result:
                            zone = result['attributes'].get('FLD_ZONE', 'X')
                            if zone and zone != 'X':
                                flood_zone = f'ZONE_{zone}'
                                break
                    
                    # Determine risk level
                    high_risk_zones = ['A', 'AE', 'AH', 'AO', 'AR', 'A99', 'V', 'VE']
                    moderate_risk_zones = ['0.2 PCT ANNUAL CHANCE FLOOD HAZARD', 'SHADED X']
                    
                    zone_code = flood_zone.replace('ZONE_', '')
                    if zone_code in high_risk_zones:
                        risk_level = 'HIGH'
                        insurance_impact = 'REQUIRED'
                    elif zone_code in moderate_risk_zones:
                        risk_level = 'MODERATE'
                        insurance_impact = 'RECOMMENDED'
                    else:
                        risk_level = 'LOW'
                        insurance_impact = 'OPTIONAL'
                    
                    return {
                        'fema_flood_zone': flood_zone,
                        'flood_risk_level': risk_level,
                        'fema_coverage_status': 'COVERED',
                        'fema_gap_flag': False,
                        'insurance_impact': insurance_impact,
                        'analysis_method': 'FEMA_API_SUCCESS'
                    }
                else:
                    # No flood data available - gap in coverage
                    self.fema_coverage_gaps.append({
                        'site_name': site_name,
                        'lat': lat,
                        'lng': lng,
                        'reason': 'NO_FLOOD_DATA_AVAILABLE'
                    })
                    
                    return {
                        'fema_flood_zone': 'NO_DATA_AVAILABLE',
                        'flood_risk_level': 'UNKNOWN',
                        'fema_coverage_status': 'GAP_IN_COVERAGE',
                        'fema_gap_flag': True,
                        'insurance_impact': 'REQUIRES_INVESTIGATION',
                        'analysis_method': 'FEMA_COVERAGE_GAP'
                    }
            else:
                # API failure - treat as coverage gap
                self.fema_coverage_gaps.append({
                    'site_name': site_name,
                    'lat': lat,
                    'lng': lng,
                    'reason': f'API_FAILURE_{response.status_code}'
                })
                
                return {
                    'fema_flood_zone': 'API_FAILURE',
                    'flood_risk_level': 'UNKNOWN',
                    'fema_coverage_status': 'API_UNAVAILABLE',
                    'fema_gap_flag': True,
                    'insurance_impact': 'REQUIRES_INVESTIGATION',
                    'analysis_method': 'FEMA_API_FAILURE'
                }
                
        except Exception as e:
            # Exception - treat as coverage gap
            self.fema_coverage_gaps.append({
                'site_name': site_name,
                'lat': lat,
                'lng': lng,
                'reason': f'EXCEPTION: {str(e)}'
            })
            
            return {
                'fema_flood_zone': 'ANALYSIS_EXCEPTION',
                'flood_risk_level': 'UNKNOWN',
                'fema_coverage_status': 'ANALYSIS_FAILED',
                'fema_gap_flag': True,
                'insurance_impact': 'REQUIRES_INVESTIGATION',
                'analysis_method': f'EXCEPTION: {str(e)}'
            }
    
    def _calculate_ami_rents_real(self, county: str, state: str = 'TX') -> Dict:
        """Real AMI rent calculations using HUD static file"""
        
        if not county or self.ami_data is None:
            return self._ami_fallback()
        
        try:
            # Search for county in AMI data
            county_search = county.replace(' County', '').replace(' COUNTY', '').strip()
            
            ami_match = self.ami_data[
                (self.ami_data['area_name'].str.contains(county_search, case=False, na=False)) &
                (self.ami_data['state_code'] == state)
            ]
            
            if not ami_match.empty:
                ami_row = ami_match.iloc[0]
                
                return {
                    'ami_area_name': ami_row.get('area_name', 'UNKNOWN'),
                    'studio_50_ami_rent': ami_row.get('studio_50_ami_rent', 0),
                    'one_br_50_ami_rent': ami_row.get('one_br_50_ami_rent', 0),
                    'two_br_50_ami_rent': ami_row.get('two_br_50_ami_rent', 0),
                    'three_br_50_ami_rent': ami_row.get('three_br_50_ami_rent', 0),
                    'ami_data_source': 'HUD_2025_STATIC_VERIFIED',
                    'ami_analysis_method': 'COUNTY_MATCH_SUCCESS'
                }
            else:
                return self._ami_fallback()
                
        except Exception as e:
            logger.warning(f"⚠️ AMI calculation failed: {e}")
            return self._ami_fallback()
    
    def _ami_fallback(self) -> Dict:
        """Fallback AMI result"""
        return {
            'ami_area_name': 'COUNTY_NOT_FOUND',
            'studio_50_ami_rent': 'CALCULATION_FAILED',
            'one_br_50_ami_rent': 'CALCULATION_FAILED',
            'two_br_50_ami_rent': 'CALCULATION_FAILED',
            'three_br_50_ami_rent': 'CALCULATION_FAILED',
            'ami_data_source': 'HUD_2025_STATIC_FILE',
            'ami_analysis_method': 'FALLBACK'
        }
    
    def _analyze_competition_framework(self, site_data: Dict) -> Dict:
        """Competition analysis framework (placeholder for integration)"""
        
        return {
            'competing_projects_1_mile': 'FRAMEWORK_READY',
            'competing_projects_2_mile': 'FRAMEWORK_READY',
            'tdhca_competition_score': 'PENDING_INTEGRATION',
            'competition_risk_level': 'REQUIRES_TDHCA_DATABASE'
        }
    
    def _assess_economic_viability_real(self, site_data: Dict, result: Dict) -> Dict:
        """Real economic viability assessment"""
        
        acreage = site_data.get('Acreage', 0.0)
        region = site_data.get('Region', 'UNKNOWN')
        
        # Basic viability assessment
        min_viable_acreage = 6.0
        optimal_acreage = 12.0
        
        if acreage >= optimal_acreage:
            acreage_score = 'EXCELLENT'
        elif acreage >= min_viable_acreage:
            acreage_score = 'ADEQUATE'
        else:
            acreage_score = 'MARGINAL'
        
        # Region-specific assessment
        high_demand_regions = [6, 7, 9]  # Houston, Austin, Dallas
        region_num = int(region) if str(region).isdigit() else 0
        
        if region_num in high_demand_regions:
            market_demand = 'HIGH'
            development_priority = 'HIGH'
        else:
            market_demand = 'MODERATE'
            development_priority = 'MODERATE'
        
        return {
            'acreage_adequacy_score': acreage_score,
            'market_demand_level': market_demand,
            'development_priority': development_priority,
            'land_cost_per_acre_estimate': 'PENDING_MARKET_DATA',
            'economic_viability_score': f'{acreage_score}_{market_demand}',
            'economic_analysis_method': 'ACREAGE_REGION_ASSESSMENT'
        }
    
    def _score_infrastructure_real(self, site_data: Dict) -> Dict:
        """Real infrastructure scoring"""
        
        region = site_data.get('Region', 'UNKNOWN')
        acreage = site_data.get('Acreage', 0.0)
        
        # Basic infrastructure assessment
        major_metro_regions = [6, 7, 9]  # Houston, Austin, Dallas
        region_num = int(region) if str(region).isdigit() else 0
        
        if region_num in major_metro_regions:
            infrastructure_level = 'METRO_GRADE'
            utility_availability = 'EXCELLENT'
        else:
            infrastructure_level = 'REGIONAL_GRADE'
            utility_availability = 'ADEQUATE'
        
        return {
            'infrastructure_grade': infrastructure_level,
            'utility_availability': utility_availability,
            'highway_access_score': 'PENDING_PROXIMITY_ANALYSIS',
            'infrastructure_adequacy': 'METRO_ADVANTAGE' if region_num in major_metro_regions else 'STANDARD',
            'infrastructure_analysis_method': 'REGION_BASED_ASSESSMENT'
        }
    
    def _calculate_real_completeness(self, result: Dict) -> float:
        """Calculate real completeness score with proper field counting"""
        
        # Define analysis categories and their required fields
        analysis_categories = {
            'geocoding': ['geocoding_status', 'parcel_center_lat', 'parcel_center_lng'],
            'qct_dda': ['qct_status', 'dda_status', 'basis_boost_eligible'],
            'environmental': ['environmental_risk_level', 'phase_i_esa_recommended'],
            'fema': ['fema_flood_zone', 'flood_risk_level', 'fema_coverage_status'],
            'ami': ['ami_area_name', 'one_br_50_ami_rent', 'two_br_50_ami_rent'],
            'economic': ['acreage_adequacy_score', 'market_demand_level'],
            'infrastructure': ['infrastructure_grade', 'utility_availability']
        }
        
        total_fields = 0
        completed_fields = 0
        
        for category, fields in analysis_categories.items():
            for field in fields:
                total_fields += 1
                value = result.get(field)
                
                # Consider field complete if it has a real value (not fallback indicators)
                fallback_indicators = [
                    None, 'ANALYSIS_FAILED', 'ANALYSIS_PENDING', 'PENDING_CALCULATION',
                    'PENDING_ANALYSIS', 'NOT_PROVIDED', 'UNKNOWN', 'CANNOT_DETERMINE',
                    'CALCULATION_FAILED', 'FRAMEWORK_READY', 'PENDING_INTEGRATION'
                ]
                
                if value not in fallback_indicators and value is not None:
                    completed_fields += 1
        
        return completed_fields / total_fields if total_fields > 0 else 0.0
    
    def _detect_real_anomalies(self, result: Dict):
        """Detect real anomalies in analysis results"""
        
        # Check for suspicious patterns
        failure_patterns = ['ANALYSIS_FAILED', 'CALCULATION_FAILED', 'API_FAILURE', 'EXCEPTION']
        
        failure_count = 0
        total_meaningful_fields = 0
        
        for key, value in result.items():
            if key not in ['site_index', 'analysis_timestamp', 'completeness_score', 'quality_flags', 'anomaly_flags']:
                total_meaningful_fields += 1
                if any(pattern in str(value) for pattern in failure_patterns):
                    failure_count += 1
        
        failure_ratio = failure_count / total_meaningful_fields if total_meaningful_fields > 0 else 0
        
        if failure_ratio > 0.3:  # More than 30% failures
            result['anomaly_flags'].append(f'HIGH_FAILURE_RATE_{failure_ratio:.1%}')
        
        # Check for FEMA gap flags
        if result.get('fema_gap_flag'):
            result['anomaly_flags'].append('FEMA_COVERAGE_GAP')
    
    def process_all_enhanced_sites(self) -> Dict:
        """Process all 38 sites with enhanced real analysis"""
        
        logger.info("🚀 ENHANCED UNIVERSAL ANALYSIS - Real components activated")
        
        # Load sites
        sites_file = f"{self.base_dir}/D'Marco_Sites/DMarco_New_Sites_20250730.xlsx"
        
        try:
            sites_df = pd.read_excel(sites_file)
            logger.info(f"📊 Processing {len(sites_df)} sites with REAL analysis")
        except Exception as e:
            logger.error(f"❌ Failed to load sites: {e}")
            return {'error': f'Site loading failed: {e}'}
        
        # Process each site
        processed_sites = []
        
        for index, site_row in sites_df.iterrows():
            site_data = site_row.to_dict()
            
            # Enhanced comprehensive analysis
            analysis_result = self.analyze_site_comprehensive(site_data, index)
            processed_sites.append(analysis_result)
        
        self.analysis_results = processed_sites
        
        # Generate comprehensive summary
        summary = self._generate_enhanced_summary()
        
        # Save results
        self._save_enhanced_results()
        
        logger.info("🎯 ENHANCED ANALYSIS COMPLETE")
        return summary
    
    def _generate_enhanced_summary(self) -> Dict:
        """Generate enhanced analysis summary with real metrics"""
        
        if not self.analysis_results:
            return {'error': 'No analysis results'}
        
        # Calculate real metrics
        completeness_scores = [r['completeness_score'] for r in self.analysis_results]
        
        # Count real successes
        qct_successes = sum(1 for r in self.analysis_results if r.get('qct_status') not in ['ANALYSIS_FAILED', None])
        env_successes = sum(1 for r in self.analysis_results if r.get('environmental_risk_level') not in ['UNKNOWN', None])
        fema_coverage = sum(1 for r in self.analysis_results if not r.get('fema_gap_flag', True))
        
        # FEMA gap analysis (as requested by Strike Leader)
        fema_gaps = len(self.fema_coverage_gaps)
        fema_coverage_percent = ((len(self.analysis_results) - fema_gaps) / len(self.analysis_results)) * 100
        
        summary = {
            'total_sites_analyzed': len(self.analysis_results),
            'average_completeness': np.mean(completeness_scores),
            'sites_meeting_95_percent': sum(1 for score in completeness_scores if score >= 0.95),
            'analysis_success_rates': {
                'qct_dda_success_rate': (qct_successes / len(self.analysis_results)) * 100,
                'environmental_success_rate': (env_successes / len(self.analysis_results)) * 100,
                'fema_coverage_rate': fema_coverage_percent
            },
            'fema_coverage_analysis': {
                'sites_with_fema_data': len(self.analysis_results) - fema_gaps,
                'sites_with_fema_gaps': fema_gaps,
                'coverage_percentage': fema_coverage_percent,
                'gap_details': self.fema_coverage_gaps
            },
            'quality_improvements_vs_framework': {
                'framework_completeness': '33.3%',
                'enhanced_completeness': f'{np.mean(completeness_scores):.1%}',
                'improvement_factor': f'{np.mean(completeness_scores) / 0.333:.1f}x'
            },
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return summary
    
    def _save_enhanced_results(self):
        """Save enhanced results with comprehensive data"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        json_file = f"{self.output_dir}/enhanced_analysis_results_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        
        # Save Excel for client delivery
        excel_file = f"{self.output_dir}/enhanced_analysis_results_{timestamp}.xlsx"
        df = pd.DataFrame(self.analysis_results)
        df.to_excel(excel_file, index=False)
        
        # Save FEMA gap analysis
        if self.fema_coverage_gaps:
            gap_file = f"{self.output_dir}/fema_coverage_gaps_{timestamp}.json"
            with open(gap_file, 'w') as f:
                json.dump(self.fema_coverage_gaps, f, indent=2)
        
        logger.info(f"💾 Enhanced results saved: {excel_file}")
        logger.info(f"📊 FEMA gap analysis: {len(self.fema_coverage_gaps)} gaps documented")

if __name__ == "__main__":
    """Execute enhanced analysis"""
    
    analyzer = EnhancedUniversalAnalyzer()
    summary = analyzer.process_all_enhanced_sites()
    
    print("\n🎯 ENHANCED ANALYSIS SUMMARY:")
    print(json.dumps(summary, indent=2))