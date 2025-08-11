#!/usr/bin/env python3
"""
Ultimate CTCAC Transit Processor - CORRECTED BY STRIKE LEADER

STRIKE_LEADER: This is a corrected version of Vitor's ultimate_ctcac_transit_processor.py
Key fixes implemented:
1. Proper frequency calculation (not 30/n_routes nonsense)
2. Full CTCAC scoring tiers (3-7 points, not just 4-5)
3. High-frequency validation (30+ arrivals, 8+ hours service)
4. Peak hour analysis improvements

All changes marked with "STRIKE_LEADER FIX:" comments
Original structure preserved for compatibility
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, time
import math
import warnings
from shapely.geometry import Point

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltimateCTCACTransitProcessor:
    """
    Ultimate CTCAC Transit Processor using all available comprehensive datasets
    
    STRIKE_LEADER: Enhanced with proper frequency calculations and scoring tiers
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.sites_dir = self.base_dir / "Sites"
        self.transit_dir = self.base_dir / "data" / "transit"
        
        # Path to existing comprehensive datasets
        self.existing_data_path = Path("/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets/california/CA_Transit_Data")
        
        # CTCAC parameters
        self.distance_threshold_miles = 1/3  # 1/3 mile
        self.distance_threshold_meters = self.distance_threshold_miles * 1609.34  # ~536 meters
        self.frequency_threshold_minutes = 30  # 30 minutes for qualification
        self.tiebreaker_threshold_minutes = 15  # 15 minutes for tie-breaker
        self.tiebreaker_distance_miles = 0.5  # 1/2 mile for tie-breaker
        
        # STRIKE_LEADER FIX: Add high-density threshold
        self.high_density_threshold = 25  # units per acre for 7-point qualification
        
        # Spatial optimization
        self.spatial_buffer_degrees = 0.006  # ~0.4 miles buffer
        self.tiebreaker_buffer_degrees = 0.008  # ~0.55 miles buffer
        
        # Initialize datasets
        self.hqta_polygons = None
        self.comprehensive_stops = None
        self.hqts_peak_data = None
        self.routes_data = None
        
        logger.info("🏛️ Ultimate CTCAC Transit Processor initialized (STRIKE LEADER CORRECTED)")
        logger.info(f"📍 Distance threshold: {self.distance_threshold_miles} miles ({self.distance_threshold_meters:.0f}m)")
        
    def load_all_datasets(self) -> bool:
        """Load all comprehensive datasets"""
        logger.info("📊 Loading ultimate dataset combination...")
        
        try:
            # 1. Load EXISTING HQTA polygons (PROVEN working system)
            hqta_file = self.existing_data_path / "High_Quality_Transit_Areas.geojson"
            if hqta_file.exists():
                self.hqta_polygons = gpd.read_file(hqta_file)
                logger.info(f"✅ Loaded {len(self.hqta_polygons):,} HQTA polygons (PROVEN system)")
            else:
                logger.warning("⚠️ HQTA polygons not found")
                
            # 2. Load EXISTING comprehensive transit stops (264K stops - 2x better coverage)
            comprehensive_stops_file = self.existing_data_path / "California_Transit_Stops.geojson"
            if comprehensive_stops_file.exists():
                self.comprehensive_stops = gpd.read_file(comprehensive_stops_file)
                
                # Create spatial index for fast queries
                self.comprehensive_stops.sindex
                
                # Pre-process frequency data
                self.comprehensive_stops['n_routes_clean'] = pd.to_numeric(
                    self.comprehensive_stops['n_routes'], errors='coerce'
                ).fillna(1)
                
                self.comprehensive_stops['n_arrivals_clean'] = pd.to_numeric(
                    self.comprehensive_stops['n_arrivals'], errors='coerce'
                ).fillna(0)
                
                # STRIKE_LEADER FIX: Add service hours processing
                self.comprehensive_stops['n_hours_in_service_clean'] = pd.to_numeric(
                    self.comprehensive_stops.get('n_hours_in_service', 0), errors='coerce'
                ).fillna(0)
                
                logger.info(f"✅ Loaded {len(self.comprehensive_stops):,} comprehensive transit stops (2x coverage)")
                logger.info(f"🚀 Spatial index created for ultra-fast queries")
            else:
                logger.error("❌ Comprehensive stops not found!")
                return False
                
            # 3. Load NEW HQTS peak hour data (actual trip frequencies)
            hqts_csv_file = self.transit_dir / "hqts_CSV_20250801.csv"
            if hqts_csv_file.exists():
                hqts_df = pd.read_csv(hqts_csv_file)
                
                # Handle duplicates and create lookup
                hqts_df = hqts_df.drop_duplicates(subset=['stop_id'], keep='first')
                
                # Filter for stops with actual peak hour data
                peak_data_mask = (
                    hqts_df['avg_trips_per_peak_hr'].notna() & 
                    (hqts_df['avg_trips_per_peak_hr'] > 0)
                )
                hqts_with_peak = hqts_df[peak_data_mask]
                
                # Create lookup dictionary
                self.hqts_peak_data = hqts_with_peak.set_index('stop_id').to_dict('index')
                
                logger.info(f"✅ Loaded {len(hqts_with_peak):,} HQTS stops with actual peak hour data")
                logger.info(f"   📊 Peak hour trip range: {hqts_with_peak['avg_trips_per_peak_hr'].min():.1f} - {hqts_with_peak['avg_trips_per_peak_hr'].max():.1f} trips/hour")
            else:
                logger.warning("⚠️ HQTS peak hour data not found")
                
            # 4. Load EXISTING routes data for validation
            routes_file = self.existing_data_path / "California_Transit_Routes.geojson"
            if routes_file.exists():
                self.routes_data = gpd.read_file(routes_file)
                logger.info(f"✅ Loaded {len(self.routes_data):,} transit routes for validation")
                
                if 'n_trips' in self.routes_data.columns:
                    trip_stats = self.routes_data['n_trips'].describe()
                    logger.info(f"   📊 Route trips - mean: {trip_stats['mean']:.1f}, max: {trip_stats['max']:.0f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load datasets: {e}")
            return False
    
    def analyze_hqta_qualification(self, latitude: float, longitude: float, site_id: str) -> Dict[str, Any]:
        """
        HQTA polygon qualification - PROVEN working system (28 sites @ 7 points)
        
        STRIKE_LEADER: This part works correctly - no changes needed
        """
        if self.hqta_polygons is None:
            return {
                'within_hqta': False,
                'ctcac_points_earned': 0,
                'analysis_method': 'HQTA_DISABLED',
                'details': 'HQTA polygons not loaded'
            }
        
        try:
            # Create point geometry
            site_point = Point(longitude, latitude)
            
            # Check intersection with HQTA polygons
            intersecting_hqtas = self.hqta_polygons[self.hqta_polygons.contains(site_point)]
            
            if len(intersecting_hqtas) > 0:
                hqta_info = intersecting_hqtas.iloc[0]
                return {
                    'within_hqta': True,
                    'ctcac_points_earned': 7,  # Maximum points for HQTA qualification
                    'analysis_method': 'HQTA_POLYGON_PROVEN',
                    'hqta_type': hqta_info.get('hqta_type', 'Unknown Type'),
                    'agency_primary': hqta_info.get('agency_primary', 'Unknown Agency'),
                    'details': f'Site within HQTA boundary - {hqta_info.get("hqta_type", "Unknown")}'
                }
            else:
                return {
                    'within_hqta': False,
                    'ctcac_points_earned': 0,
                    'analysis_method': 'HQTA_POLYGON_PROVEN',
                    'details': 'Site not within any HQTA boundary'
                }
                
        except Exception as e:
            logger.warning(f"⚠️ HQTA analysis error for {site_id}: {e}")
            return {
                'within_hqta': False,
                'ctcac_points_earned': 0,
                'analysis_method': 'HQTA_ERROR',
                'details': f'HQTA analysis failed: {str(e)}'
            }
    
    def haversine_distance_meters(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Fast haversine distance calculation"""
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371000  # Earth radius in meters
        return c * r
    
    def find_nearby_stops_ultimate(self, latitude: float, longitude: float, distance_meters: float = None) -> List[Dict]:
        """
        Ultimate nearby stop search using 264K comprehensive stops + HQTS peak data
        
        STRIKE_LEADER: Enhanced with proper frequency calculations
        """
        if distance_meters is None:
            distance_meters = self.distance_threshold_meters
            
        # Create bounding box for spatial filtering
        buffer_degrees = self.spatial_buffer_degrees if distance_meters <= 600 else self.tiebreaker_buffer_degrees
        
        min_lon = longitude - buffer_degrees
        max_lon = longitude + buffer_degrees  
        min_lat = latitude - buffer_degrees
        max_lat = latitude + buffer_degrees
        
        nearby_stops = []
        
        # Search comprehensive stops dataset (264K stops)
        if self.comprehensive_stops is not None:
            # Spatial filtering for performance
            bbox_mask = (
                (self.comprehensive_stops.geometry.x >= min_lon) &
                (self.comprehensive_stops.geometry.x <= max_lon) &
                (self.comprehensive_stops.geometry.y >= min_lat) &
                (self.comprehensive_stops.geometry.y <= max_lat)
            )
            
            candidate_stops = self.comprehensive_stops[bbox_mask]
            
            # Precise distance calculation on candidates
            for idx, stop in candidate_stops.iterrows():
                try:
                    stop_lat = stop.geometry.y
                    stop_lon = stop.geometry.x
                    distance = self.haversine_distance_meters(latitude, longitude, stop_lat, stop_lon)
                    
                    if distance <= distance_meters:
                        stop_id = stop.get('stop_id', f'comp_{idx}')
                        
                        # Get base frequency data from comprehensive dataset
                        n_routes = stop['n_routes_clean']
                        n_arrivals = stop['n_arrivals_clean']
                        n_hours_in_service = stop['n_hours_in_service_clean']
                        
                        # Check if this stop has HQTS peak hour data
                        hqts_enhancement = None
                        if self.hqts_peak_data and stop_id in self.hqts_peak_data:
                            hqts_data = self.hqts_peak_data[stop_id]
                            peak_trips = hqts_data.get('avg_trips_per_peak_hr', 0)
                            if peak_trips > 0:
                                hqts_enhancement = {
                                    'actual_peak_trips_per_hour': peak_trips,
                                    'hqts_frequency_minutes': 120 / peak_trips,  # 2 hours / trips
                                    'data_source': 'HQTS_ACTUAL_PEAK_DATA'
                                }
                        
                        # STRIKE_LEADER FIX: Proper frequency calculation
                        if hqts_enhancement:
                            # Use actual HQTS peak hour data (most accurate)
                            frequency_minutes = hqts_enhancement['hqts_frequency_minutes']
                            frequency_method = 'HQTS_ACTUAL_PEAK'
                        elif n_arrivals > 0 and n_hours_in_service >= 8:
                            # STRIKE_LEADER FIX: Proper peak hour calculation
                            # Peak hours are ~4 hours (7-9 AM + 4-6 PM)
                            # If service runs 8+ hours, estimate peak concentration
                            peak_arrivals = n_arrivals * (4.0 / n_hours_in_service)
                            frequency_minutes = 240 / peak_arrivals if peak_arrivals > 0 else 999
                            frequency_method = 'COMPREHENSIVE_PEAK_ESTIMATE'
                        elif n_arrivals > 0:
                            # STRIKE_LEADER FIX: Fallback for limited service hours
                            # Assume 20% of arrivals during peak (conservative)
                            peak_arrivals = n_arrivals * 0.2
                            frequency_minutes = 240 / peak_arrivals if peak_arrivals > 0 else 999
                            frequency_method = 'COMPREHENSIVE_ARRIVALS'
                        else:
                            # STRIKE_LEADER FIX: Last resort - use route count
                            # Assume each route runs every 60 minutes (very conservative)
                            frequency_minutes = 60 / n_routes if n_routes > 0 else 999
                            frequency_method = 'COMPREHENSIVE_ROUTES_FALLBACK'
                        
                        # STRIKE_LEADER FIX: Add high-frequency flag
                        is_high_frequency = (
                            frequency_minutes <= self.frequency_threshold_minutes and
                            n_arrivals >= 30 and
                            n_hours_in_service >= 8
                        )
                        
                        nearby_stops.append({
                            'stop_id': stop_id,
                            'distance_meters': distance,
                            'distance_miles': distance / 1609.34,  # STRIKE_LEADER: Added for clarity
                            'agency': stop.get('agency', 'Unknown'),
                            'stop_name': stop.get('stop_name', 'Unknown'),
                            'n_routes': n_routes,
                            'n_arrivals': n_arrivals,
                            'n_hours_in_service': n_hours_in_service,  # STRIKE_LEADER: Added
                            'calculated_frequency_minutes': frequency_minutes,
                            'frequency_method': frequency_method,
                            'is_high_frequency': is_high_frequency,  # STRIKE_LEADER: Added
                            'hqts_enhancement': hqts_enhancement,
                            'dataset_source': 'COMPREHENSIVE_264K'
                        })
                        
                except Exception as e:
                    continue
        
        return sorted(nearby_stops, key=lambda x: x['distance_meters'])
    
    def analyze_ultimate_frequency(self, stops_list: List[Dict]) -> Dict[str, Any]:
        """
        Ultimate frequency analysis using all available data sources
        
        STRIKE_LEADER: Enhanced with proper high-frequency detection
        """
        if not stops_list:
            return {
                'total_stops': 0,
                'total_routes': 0,
                'estimated_peak_frequency': 999,
                'high_frequency_stops': 0,
                'hqts_enhanced_stops': 0,
                'frequency_analysis': 'No stops within distance',
                'high_frequency_validated_stops': 0  # STRIKE_LEADER: Added
            }
        
        total_routes = sum(stop['n_routes'] for stop in stops_list)
        high_frequency_stops = 0
        high_frequency_validated_stops = 0  # STRIKE_LEADER: Added
        hqts_enhanced_stops = 0
        best_frequency = 999
        
        for stop in stops_list:
            frequency = stop['calculated_frequency_minutes']
            
            # Track best frequency
            if frequency < best_frequency:
                best_frequency = frequency
            
            # Count qualifying stops
            if frequency <= self.frequency_threshold_minutes:
                high_frequency_stops += 1
            
            # STRIKE_LEADER FIX: Count properly validated high-frequency stops
            if stop.get('is_high_frequency', False):
                high_frequency_validated_stops += 1
            
            # Count HQTS enhanced stops
            if stop.get('hqts_enhancement'):
                hqts_enhanced_stops += 1
        
        return {
            'total_stops': len(stops_list),
            'total_routes': total_routes,
            'estimated_peak_frequency': best_frequency,
            'high_frequency_stops': high_frequency_stops,
            'high_frequency_validated_stops': high_frequency_validated_stops,  # STRIKE_LEADER: Added
            'hqts_enhanced_stops': hqts_enhanced_stops,
            'stop_details': stops_list[:5],  # Top 5 closest stops
            'frequency_methods_used': list(set(stop['frequency_method'] for stop in stops_list))
        }
    
    def calculate_ultimate_ctcac_points(self, frequency_analysis: Dict[str, Any], 
                                       site_lat: float, site_lon: float,
                                       density_per_acre: float = None) -> Dict[str, Any]:
        """
        Ultimate CTCAC points calculation with proper scoring tiers
        
        STRIKE_LEADER FIX: Complete rewrite with correct CTCAC scoring
        - 7 points: HQTA or high-frequency within 1/3 mile + high density (>25 units/acre)
        - 6 points: HQTA or high-frequency within 1/3 mile
        - 5 points: HQTA or high-frequency within 1/2 mile
        - 4 points: Basic transit within 1/3 mile
        - 3 points: Basic transit within 1/2 mile
        - 0 points: No qualifying transit
        """
        base_points = 0
        tiebreaker_points = 0
        scoring_method = 'NO_TRANSIT'
        
        # STRIKE_LEADER FIX: Check for high-density bonus eligibility
        is_high_density = density_per_acre is not None and density_per_acre > self.high_density_threshold
        
        # STRIKE_LEADER FIX: First check 1/3 mile high-frequency
        if frequency_analysis['high_frequency_validated_stops'] > 0:
            # We have validated high-frequency service within 1/3 mile
            if is_high_density:
                base_points = 7
                scoring_method = 'HIGH_FREQUENCY_HIGH_DENSITY'
            else:
                base_points = 6
                scoring_method = 'HIGH_FREQUENCY_REGULAR'
        elif frequency_analysis['high_frequency_stops'] > 0:
            # We have stops with ≤30 min frequency (but not fully validated)
            if is_high_density:
                base_points = 6  # Conservative: 6 instead of 7
                scoring_method = 'FREQUENCY_HIGH_DENSITY'
            else:
                base_points = 6
                scoring_method = 'FREQUENCY_REGULAR'
        elif frequency_analysis['total_stops'] > 0:
            # Basic transit within 1/3 mile
            base_points = 4
            scoring_method = 'BASIC_TRANSIT_THIRD_MILE'
        
        # STRIKE_LEADER FIX: Now check 1/2 mile if we haven't achieved 5+ points
        if base_points < 5:
            # Search for stops within 1/2 mile
            half_mile_stops = self.find_nearby_stops_ultimate(
                site_lat, site_lon, 
                distance_meters=0.5 * 1609.34
            )
            
            if half_mile_stops:
                # Analyze frequency at 1/2 mile
                half_mile_analysis = self.analyze_ultimate_frequency(half_mile_stops)
                
                if half_mile_analysis['high_frequency_validated_stops'] > 0 or \
                   half_mile_analysis['high_frequency_stops'] > 0:
                    # High-frequency at 1/2 mile = 5 points
                    if base_points < 5:
                        base_points = 5
                        scoring_method = 'HIGH_FREQUENCY_HALF_MILE'
                elif half_mile_analysis['total_stops'] > 0 and base_points < 3:
                    # Basic transit at 1/2 mile = 3 points
                    base_points = 3
                    scoring_method = 'BASIC_TRANSIT_HALF_MILE'
        
        # STRIKE_LEADER FIX: Tie-breaker analysis for ≤15 minute service
        # Only relevant if we're already scoring points
        if base_points > 0:
            # Get stops within 1/2 mile for tiebreaker
            tiebreaker_stops = self.find_nearby_stops_ultimate(
                site_lat, site_lon, 
                distance_meters=self.tiebreaker_distance_miles * 1609.34
            )
            
            best_tiebreaker_freq = 999
            if tiebreaker_stops:
                frequencies = [stop['calculated_frequency_minutes'] for stop in tiebreaker_stops]
                best_tiebreaker_freq = min(frequencies) if frequencies else 999
                
                if best_tiebreaker_freq <= self.tiebreaker_threshold_minutes:
                    tiebreaker_points = 1
        else:
            best_tiebreaker_freq = 999
        
        total_points = base_points + tiebreaker_points
        
        return {
            'base_points': base_points,
            'tiebreaker_points': tiebreaker_points,
            'total_points': total_points,
            'scoring_method': scoring_method,
            'tiebreaker_frequency_minutes': best_tiebreaker_freq,
            'is_high_density': is_high_density,
            'density_per_acre': density_per_acre,
            'analysis_method': 'ULTIMATE_COMPREHENSIVE_ANALYSIS_CORRECTED'
        }
    
    def analyze_site_ultimate(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ultimate site analysis combining all data sources
        
        STRIKE_LEADER: Enhanced with density parameter passing
        """
        site_id = site_data.get('site_id', 'Unknown')
        latitude = float(site_data['latitude'])
        longitude = float(site_data['longitude'])
        density_per_acre = site_data.get('density_per_acre', None)  # STRIKE_LEADER: Added
        
        # Step 1: HQTA qualification check (PROVEN working system)
        hqta_result = self.analyze_hqta_qualification(latitude, longitude, site_id)
        
        if hqta_result['within_hqta']:
            # Site qualifies via HQTA - return maximum points
            # STRIKE_LEADER FIX: HQTA always gets 7 points regardless of density
            return {
                'site_id': site_id,
                'latitude': latitude,
                'longitude': longitude,
                'transit_qualified': True,
                'qualification_method': 'HQTA_POLYGON_PROVEN',
                'ctcac_points_earned': 7,
                'hqta_details': hqta_result,
                'analysis_timestamp': datetime.now().isoformat(),
                'dataset_sources': ['HQTA_POLYGONS_26K']
            }
        
        # Step 2: Ultimate frequency analysis for non-HQTA sites
        nearby_stops = self.find_nearby_stops_ultimate(latitude, longitude)
        
        if not nearby_stops:
            return {
                'site_id': site_id,
                'latitude': latitude,
                'longitude': longitude,
                'transit_qualified': False,
                'qualification_method': 'NO_NEARBY_STOPS',
                'ctcac_points_earned': 0,
                'stops_found': 0,
                'analysis_timestamp': datetime.now().isoformat(),
                'dataset_sources': ['COMPREHENSIVE_264K_SEARCHED']
            }
        
        # Analyze service frequency
        frequency_analysis = self.analyze_ultimate_frequency(nearby_stops)
        
        # Calculate CTCAC points with density consideration
        scoring_result = self.calculate_ultimate_ctcac_points(
            frequency_analysis, latitude, longitude, density_per_acre
        )
        
        transit_qualified = scoring_result['total_points'] > 0
        qualification_method = scoring_result['scoring_method']
        
        # Determine data sources used
        dataset_sources = ['COMPREHENSIVE_264K_STOPS']
        if frequency_analysis['hqts_enhanced_stops'] > 0:
            dataset_sources.append('HQTS_45K_PEAK_DATA')
        dataset_sources.extend(frequency_analysis['frequency_methods_used'])
        
        return {
            'site_id': site_id,
            'latitude': latitude,
            'longitude': longitude,
            'transit_qualified': transit_qualified,
            'qualification_method': qualification_method,
            'ctcac_points_earned': scoring_result['total_points'],
            'base_points': scoring_result['base_points'],
            'tiebreaker_points': scoring_result['tiebreaker_points'],
            'stops_found': len(nearby_stops),
            'hqts_enhanced_stops': frequency_analysis['hqts_enhanced_stops'],
            'high_frequency_validated_stops': frequency_analysis['high_frequency_validated_stops'],  # STRIKE_LEADER: Added
            'best_frequency_minutes': frequency_analysis['estimated_peak_frequency'],
            'tiebreaker_frequency': scoring_result['tiebreaker_frequency_minutes'],
            'hqta_details': hqta_result,
            'frequency_analysis': frequency_analysis,
            'scoring_details': scoring_result,  # STRIKE_LEADER: Added full details
            'dataset_sources': dataset_sources,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def process_portfolio_ultimate(self, portfolio_file: str) -> Dict[str, Any]:
        """
        Ultimate portfolio processing with all comprehensive datasets
        
        STRIKE_LEADER: Enhanced with better scoring distribution tracking
        """
        logger.info("🏛️ Starting ULTIMATE CTCAC Transit Analysis (STRIKE LEADER CORRECTED)")
        logger.info("⚔️ All datasets combined: HQTA + 264K stops + 45K peak data + 37K routes")
        logger.info("✅ Proper frequency calculations and 3-7 point scoring implemented")
        logger.info("=" * 70)
        
        # Load portfolio data
        portfolio_path = Path(portfolio_file)
        if not portfolio_path.exists():
            raise FileNotFoundError(f"Portfolio file not found: {portfolio_file}")
        
        if portfolio_path.suffix.lower() == '.xlsx':
            df = pd.read_excel(portfolio_path)
        else:
            df = pd.read_csv(portfolio_path)
        
        logger.info(f"📊 Loaded {len(df)} sites from portfolio")
        
        # STRIKE_LEADER: Check for density data
        has_density = 'Density_Per_Acre' in df.columns or 'density_per_acre' in df.columns
        if has_density:
            logger.info("✅ Density data found - will calculate 7-point eligibility")
        else:
            logger.info("⚠️ No density data - maximum 6 points possible (except HQTA)")
        
        # Process sites with performance tracking
        results = []
        hqta_qualified = 0
        
        # STRIKE_LEADER FIX: Better scoring distribution tracking
        score_distribution = {0: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
        method_distribution = {}
        
        start_time = datetime.now()
        
        for idx, row in df.iterrows():
            try:
                site_data = {
                    'site_id': row.get('Site_ID', f'Site_{idx}'),
                    'latitude': row['Latitude'],
                    'longitude': row['Longitude'],
                    'density_per_acre': row.get('Density_Per_Acre', row.get('density_per_acre', None))
                }
                
                # Analyze transit for this site
                site_result = self.analyze_site_ultimate(site_data)
                results.append(site_result)
                
                # Track results
                points = site_result['ctcac_points_earned']
                method = site_result['qualification_method']
                
                if method == 'HQTA_POLYGON_PROVEN':
                    hqta_qualified += 1
                
                # STRIKE_LEADER: Track score distribution
                if points in score_distribution:
                    score_distribution[points] += 1
                
                if method not in method_distribution:
                    method_distribution[method] = 0
                method_distribution[method] += 1
                
                # Progress tracking
                if (idx + 1) % 50 == 0:
                    elapsed = datetime.now() - start_time
                    avg_time = elapsed.total_seconds() / (idx + 1)
                    remaining = (len(df) - idx - 1) * avg_time
                    logger.info(f"🏛️ Progress: {idx + 1}/{len(df)} sites ({(idx+1)/len(df)*100:.1f}%) - ETA: {remaining/60:.1f} min")
                
            except Exception as e:
                logger.error(f"❌ Error processing site {idx}: {e}")
                results.append({
                    'site_id': f'Site_{idx}',
                    'error': str(e),
                    'analysis_timestamp': datetime.now().isoformat()
                })
        
        # Generate ultimate summary
        total_qualified = sum(1 for r in results if r.get('transit_qualified', False))
        qualification_rate = (total_qualified / len(results)) * 100 if results else 0
        processing_time = datetime.now() - start_time
        
        summary = {
            'total_sites_analyzed': len(results),
            'hqta_qualified': hqta_qualified,
            'total_transit_qualified': total_qualified,
            'qualification_rate_percent': qualification_rate,
            'score_distribution': score_distribution,
            'method_distribution': method_distribution,
            'processing_time_seconds': processing_time.total_seconds(),
            'avg_time_per_site': processing_time.total_seconds() / len(results) if results else 0,
            'analysis_method': 'ULTIMATE_COMPREHENSIVE_CORRECTED',
            'datasets_used': [
                'HQTA_POLYGONS_26669',
                'COMPREHENSIVE_STOPS_264311', 
                'HQTS_PEAK_DATA_45024',
                'ROUTES_DATA_37083'
            ]
        }
        
        logger.info("=" * 70)
        logger.info("🏆 ULTIMATE CTCAC ANALYSIS COMPLETE (STRIKE LEADER CORRECTED)")  
        logger.info("=" * 70)
        logger.info(f"📊 Total sites: {len(results)}")
        logger.info(f"✅ HQTA qualified: {hqta_qualified} sites (7 points each)")
        logger.info(f"✅ Total transit qualified: {total_qualified} sites")
        logger.info(f"🏛️ Overall qualification rate: {qualification_rate:.1f}%")
        
        # STRIKE_LEADER: Show score distribution
        logger.info("\n📊 SCORE DISTRIBUTION:")
        for points in sorted(score_distribution.keys()):
            count = score_distribution[points]
            if count > 0:
                logger.info(f"   {points} points: {count} sites ({count/len(results)*100:.1f}%)")
        
        logger.info(f"\n⚡ Processing time: {processing_time.total_seconds():.1f} seconds")
        logger.info(f"⚡ Avg time per site: {processing_time.total_seconds()/len(results):.2f} seconds")
        
        return {
            'summary': summary,
            'detailed_results': results,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def export_ultimate_results(self, results: Dict[str, Any], output_dir: Path = None) -> List[str]:
        """Export ultimate analysis results with enhanced details"""
        if output_dir is None:
            output_dir = self.base_dir
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_files = []
        
        # Export to Excel
        excel_file = output_dir / f"ULTIMATE_CTCAC_TRANSIT_ANALYSIS_CORRECTED_{timestamp}.xlsx"
        
        # Create detailed results DataFrame
        detailed_df = pd.json_normalize(results['detailed_results'])
        
        # Create summary DataFrame
        summary_df = pd.DataFrame([results['summary']])
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Summary sheet
            summary_df.to_excel(writer, sheet_name='Ultimate_Summary', index=False)
            
            # Detailed results sheet
            detailed_df.to_excel(writer, sheet_name='Ultimate_Results', index=False)
            
            # HQTA qualified sites
            hqta_df = detailed_df[detailed_df['qualification_method'] == 'HQTA_POLYGON_PROVEN'].copy()
            if len(hqta_df) > 0:
                hqta_df.to_excel(writer, sheet_name='HQTA_Qualified', index=False)
            
            # STRIKE_LEADER: Add sheets by score
            for points in [7, 6, 5, 4, 3]:
                score_df = detailed_df[detailed_df['ctcac_points_earned'] == points].copy()
                if len(score_df) > 0:
                    score_df.to_excel(writer, sheet_name=f'{points}_Point_Sites', index=False)
        
        output_files.append(str(excel_file))
        logger.info(f"📊 Ultimate Excel report saved: {excel_file}")
        
        # Export to JSON
        json_file = output_dir / f"ULTIMATE_CTCAC_TRANSIT_ANALYSIS_CORRECTED_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        output_files.append(str(json_file))
        logger.info(f"📋 Ultimate JSON report saved: {json_file}")
        
        return output_files


def main():
    """Main execution"""
    processor = UltimateCTCACTransitProcessor()
    
    logger.info("🏛️ ULTIMATE CTCAC TRANSIT PROCESSOR (STRIKE LEADER CORRECTED)")
    logger.info("⚔️ Roman Engineering: All datasets combined for maximum accuracy")
    logger.info("📊 HQTA (26K) + Comprehensive Stops (264K) + HQTS Peak Data (45K) + Routes (37K)")
    logger.info("🎯 Target: Correct CTCAC scoring with 3-7 point range")
    logger.info("=" * 70)
    
    # Load all datasets
    if not processor.load_all_datasets():
        logger.error("❌ Failed to load required datasets")
        return False
    
    # Process portfolio
    portfolio_file = processor.sites_dir / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
    
    if not portfolio_file.exists():
        logger.error(f"❌ Portfolio file not found: {portfolio_file}")
        return False
    
    try:
        results = processor.process_portfolio_ultimate(str(portfolio_file))
        output_files = processor.export_ultimate_results(results)
        
        logger.info("🏛️ ROMAN STANDARD ACHIEVED: Ultimate transit analysis complete!")
        logger.info("⚔️ All comprehensive datasets successfully integrated")
        logger.info("✅ CTCAC scoring corrected: 3-7 points now properly assigned")
        logger.info(f"📁 Ultimate results saved to: {', '.join(output_files)}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ultimate analysis failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)