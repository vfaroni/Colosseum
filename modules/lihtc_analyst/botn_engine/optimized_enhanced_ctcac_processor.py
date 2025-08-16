#!/usr/bin/env python3
"""
Optimized Enhanced CTCAC Transit Processor

Fast, efficient transit analysis combining HQTA qualification with optimized
frequency analysis using spatial indexing for 90,924+ stops.

Performance optimizations:
- Spatial indexing using buffer-based filtering before distance calculations
- Pre-computed distance matrices for frequent lookups
- Optimized data structures for faster iteration
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, time
import warnings
from shapely.geometry import Point
import math

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedEnhancedCTCACProcessor:
    """
    Optimized Enhanced CTCAC Transit Processor with spatial indexing
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent  
        self.data_dir = self.base_dir / "data"
        self.transit_dir = self.data_dir / "transit"
        self.sites_dir = self.base_dir / "Sites"
        
        # CTCAC scoring parameters
        self.distance_threshold_miles = 1/3  # 1/3 mile
        self.distance_threshold_meters = self.distance_threshold_miles * 1609.34  # ~536 meters
        self.peak_hours_am = (time(7, 0), time(9, 0))  # 7-9 AM
        self.peak_hours_pm = (time(16, 0), time(18, 0))  # 4-6 PM
        self.frequency_threshold_minutes = 30  # 30 minutes or less for qualification
        self.tiebreaker_threshold_minutes = 15  # 15 minutes for tie-breaker boost
        self.tiebreaker_distance_miles = 0.5  # 1/2 mile for tie-breaker
        
        # Spatial optimization parameters
        self.spatial_buffer_degrees = 0.006  # ~0.4 miles buffer for initial filtering
        self.tiebreaker_buffer_degrees = 0.008  # ~0.55 miles buffer for tie-breaker
        
        # Initialize datasets
        self.hqta_polygons = None
        self.transit_stops_master = None
        self.transit_stops_enhanced = None
        
        logger.info("⚡ Optimized Enhanced CTCAC Transit Processor initialized")
        logger.info(f"📍 Distance threshold: {self.distance_threshold_miles} miles ({self.distance_threshold_meters:.0f}m)")
        logger.info(f"🔍 Spatial buffer: {self.spatial_buffer_degrees:.4f} degrees (~0.4 miles)")
        
    def load_datasets(self) -> bool:
        """Load and optimize transit datasets for spatial queries"""
        logger.info("📊 Loading and optimizing transit datasets...")
        
        try:
            # Load HQTA polygons (working system)
            hqta_file = Path("/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets/california/CA_Transit_Data/High_Quality_Transit_Areas.geojson")
            if hqta_file.exists():
                self.hqta_polygons = gpd.read_file(hqta_file)
                logger.info(f"✅ Loaded {len(self.hqta_polygons)} HQTA polygons")
                logger.info(f"HQTA columns: {list(self.hqta_polygons.columns)}")
            else:
                logger.warning("⚠️ HQTA polygons not found - HQTA analysis disabled")
                
            # Load and optimize master transit stops (90,924 records)
            master_file = self.transit_dir / "california_transit_stops_master.geojson"
            if master_file.exists():
                self.transit_stops_master = gpd.read_file(master_file)
                
                # Create spatial index for faster queries
                self.transit_stops_master.sindex
                
                # Pre-process frequency data for faster analysis
                self.transit_stops_master['n_routes_clean'] = pd.to_numeric(
                    self.transit_stops_master['n_routes'], errors='coerce'
                ).fillna(1)
                
                self.transit_stops_master['n_arrivals_clean'] = pd.to_numeric(
                    self.transit_stops_master['n_arrivals'], errors='coerce'
                ).fillna(0)
                
                logger.info(f"✅ Loaded and optimized {len(self.transit_stops_master)} master transit stops")
                logger.info(f"🚀 Spatial index created for fast queries")
            else:
                logger.error("❌ Master transit stops not found!")
                return False
                
            # Load enhanced stops for supplementary data
            enhanced_file = self.transit_dir / "california_transit_stops_enhanced.geojson"
            if enhanced_file.exists():
                self.transit_stops_enhanced = gpd.read_file(enhanced_file)
                self.transit_stops_enhanced.sindex  # Create spatial index
                
                # Pre-process frequency data
                self.transit_stops_enhanced['n_routes_clean'] = pd.to_numeric(
                    self.transit_stops_enhanced['n_routes'], errors='coerce'
                ).fillna(1)
                
                self.transit_stops_enhanced['n_arrivals_clean'] = pd.to_numeric(
                    self.transit_stops_enhanced['n_arrivals'], errors='coerce'
                ).fillna(0)
                
                logger.info(f"✅ Loaded and optimized {len(self.transit_stops_enhanced)} enhanced transit stops")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load datasets: {e}")
            return False
    
    def analyze_hqta_qualification(self, latitude: float, longitude: float, site_id: str) -> Dict[str, Any]:
        """
        Check if site qualifies via HQTA polygon boundary (working system)
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
                    'analysis_method': 'HQTA_POLYGON_INTERSECTION',
                    'hqta_name': hqta_info.get('name', 'Unknown HQTA'),
                    'hqta_type': hqta_info.get('type', 'Unknown Type'),
                    'details': f'Site within HQTA boundary: {hqta_info.get("name", "Unnamed")}'
                }
            else:
                return {
                    'within_hqta': False,
                    'ctcac_points_earned': 0,
                    'analysis_method': 'HQTA_POLYGON_INTERSECTION',
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
        """Fast haversine distance calculation in meters"""
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in meters
        r = 6371000
        return c * r
    
    def find_nearby_stops_optimized(self, latitude: float, longitude: float, distance_meters: float = None) -> List[Dict]:
        """
        Optimized nearby stop search using spatial indexing
        
        Uses bounding box pre-filtering before precise distance calculations
        """
        if distance_meters is None:
            distance_meters = self.distance_threshold_meters
            
        # Create bounding box for initial filtering
        buffer_degrees = self.spatial_buffer_degrees if distance_meters <= 600 else self.tiebreaker_buffer_degrees
        
        min_lon = longitude - buffer_degrees
        max_lon = longitude + buffer_degrees  
        min_lat = latitude - buffer_degrees
        max_lat = latitude + buffer_degrees
        
        nearby_stops = []
        
        # Search master dataset with spatial filtering
        if self.transit_stops_master is not None:
            # Filter by bounding box first (much faster)
            bbox_mask = (
                (self.transit_stops_master.geometry.x >= min_lon) &
                (self.transit_stops_master.geometry.x <= max_lon) &
                (self.transit_stops_master.geometry.y >= min_lat) &
                (self.transit_stops_master.geometry.y <= max_lat)
            )
            
            candidate_stops = self.transit_stops_master[bbox_mask]
            
            # Precise distance calculation only on candidates
            for idx, stop in candidate_stops.iterrows():
                try:
                    stop_lat = stop.geometry.y
                    stop_lon = stop.geometry.x
                    distance = self.haversine_distance_meters(latitude, longitude, stop_lat, stop_lon)
                    
                    if distance <= distance_meters:
                        nearby_stops.append({
                            'stop_id': stop.get('stop_id', f'master_{idx}'),
                            'distance_meters': distance,
                            'n_routes': stop['n_routes_clean'],
                            'n_arrivals': stop['n_arrivals_clean'],
                            'agency': stop.get('agency', 'Unknown'),
                            'dataset_source': 'master'
                        })
                        
                except Exception as e:
                    continue
        
        # Also check enhanced dataset for additional coverage
        if self.transit_stops_enhanced is not None and len(nearby_stops) < 10:  # Only if we need more stops
            bbox_mask_enhanced = (
                (self.transit_stops_enhanced.geometry.x >= min_lon) &
                (self.transit_stops_enhanced.geometry.x <= max_lon) &
                (self.transit_stops_enhanced.geometry.y >= min_lat) &
                (self.transit_stops_enhanced.geometry.y <= max_lat)
            )
            
            candidate_stops_enhanced = self.transit_stops_enhanced[bbox_mask_enhanced]
            
            for idx, stop in candidate_stops_enhanced.iterrows():
                try:
                    stop_lat = stop.geometry.y 
                    stop_lon = stop.geometry.x
                    distance = self.haversine_distance_meters(latitude, longitude, stop_lat, stop_lon)
                    
                    if distance <= distance_meters:
                        # Check if stop already exists (avoid duplicates)
                        stop_id = stop.get('stop_id', f'enhanced_{idx}')
                        if not any(s['stop_id'] == stop_id for s in nearby_stops):
                            nearby_stops.append({
                                'stop_id': stop_id,
                                'distance_meters': distance,
                                'n_routes': stop['n_routes_clean'],
                                'n_arrivals': stop['n_arrivals_clean'],
                                'agency': stop.get('agency', 'Unknown'),
                                'dataset_source': 'enhanced'
                            })
                        
                except Exception as e:
                    continue
        
        return nearby_stops
    
    def analyze_service_frequency_optimized(self, stops_list: List[Dict]) -> Dict[str, Any]:
        """
        Optimized service frequency analysis
        """
        if not stops_list:
            return {
                'total_stops': 0,
                'total_routes': 0,
                'estimated_peak_frequency': 999,
                'high_frequency_stops': 0,
                'frequency_analysis': 'No stops within distance'
            }
        
        total_routes = sum(stop['n_routes'] for stop in stops_list)
        total_arrivals = sum(stop['n_arrivals'] for stop in stops_list)
        
        high_frequency_stops = 0
        best_frequency = 999
        
        for stop in stops_list:
            # Estimate peak hour frequency
            n_routes = stop['n_routes']
            n_arrivals = stop['n_arrivals']
            
            if n_arrivals > 0:
                # Use arrivals data: assume 20% during 2-hour peak
                estimated_peak_arrivals = n_arrivals * 0.2
                peak_frequency_minutes = 120 / estimated_peak_arrivals if estimated_peak_arrivals > 0 else 999
            else:
                # Fallback: estimate based on routes (30 min average per route)
                peak_frequency_minutes = 30 / n_routes if n_routes > 0 else 999
            
            stop['estimated_peak_frequency'] = peak_frequency_minutes
            
            # Track best frequency
            if peak_frequency_minutes < best_frequency:
                best_frequency = peak_frequency_minutes
            
            # Count qualifying stops
            if peak_frequency_minutes <= self.frequency_threshold_minutes:
                high_frequency_stops += 1
        
        return {
            'total_stops': len(stops_list),
            'total_routes': total_routes,
            'total_arrivals_per_day': total_arrivals,
            'estimated_peak_frequency': best_frequency,
            'high_frequency_stops': high_frequency_stops,
            'stop_details': stops_list
        }
    
    def calculate_ctcac_points_optimized(self, frequency_analysis: Dict[str, Any], site_lat: float, site_lon: float) -> Dict[str, Any]:
        """
        Optimized CTCAC points calculation
        """
        base_points = 0
        tiebreaker_points = 0
        
        # Base scoring: 4 points for ≤30 minute service within 1/3 mile
        if frequency_analysis['high_frequency_stops'] > 0:
            base_points = 4
            
        # Tie-breaker analysis: 1 point for ≤15 minute service within 1/2 mile
        tiebreaker_stops = self.find_nearby_stops_optimized(
            site_lat, site_lon, 
            distance_meters=self.tiebreaker_distance_miles * 1609.34
        )
        
        best_tiebreaker_freq = 999
        if tiebreaker_stops:
            frequencies = [
                stop.get('estimated_peak_frequency', 999) 
                for stop in tiebreaker_stops
                if 'estimated_peak_frequency' in stop
            ]
            if frequencies:
                best_tiebreaker_freq = min(frequencies)
            
            # Quick frequency estimate for tie-breaker stops
            for stop in tiebreaker_stops:
                if 'estimated_peak_frequency' not in stop:
                    n_routes = stop['n_routes']
                    n_arrivals = stop['n_arrivals']
                    
                    if n_arrivals > 0:
                        estimated_peak_arrivals = n_arrivals * 0.2
                        freq = 120 / estimated_peak_arrivals if estimated_peak_arrivals > 0 else 999
                    else:
                        freq = 30 / n_routes if n_routes > 0 else 999
                    
                    stop['estimated_peak_frequency'] = freq
            
            frequencies = [stop['estimated_peak_frequency'] for stop in tiebreaker_stops]
            best_tiebreaker_freq = min(frequencies) if frequencies else 999
            
            if best_tiebreaker_freq <= self.tiebreaker_threshold_minutes:
                tiebreaker_points = 1
        
        total_points = base_points + tiebreaker_points
        
        return {
            'base_points': base_points,
            'tiebreaker_points': tiebreaker_points,
            'total_points': total_points,
            'tiebreaker_frequency': best_tiebreaker_freq if tiebreaker_stops else 999,
            'analysis_method': 'OPTIMIZED_FREQUENCY_ANALYSIS'
        }
    
    def analyze_site_transit_optimized(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimized complete transit analysis for a single site
        """
        site_id = site_data.get('site_id', 'Unknown')
        latitude = float(site_data['latitude'])
        longitude = float(site_data['longitude'])
        
        # Step 1: HQTA qualification check (proven working system)
        hqta_result = self.analyze_hqta_qualification(latitude, longitude, site_id)
        
        if hqta_result['within_hqta']:
            # Site qualifies via HQTA - return maximum points
            return {
                'site_id': site_id,
                'latitude': latitude,
                'longitude': longitude,
                'transit_qualified': True,
                'qualification_method': 'HQTA_POLYGON',
                'ctcac_points_earned': 7,
                'hqta_details': hqta_result,
                'analysis_timestamp': datetime.now().isoformat()
            }
        
        # Step 2: Optimized frequency analysis for non-HQTA sites
        nearby_stops = self.find_nearby_stops_optimized(latitude, longitude)
        
        if not nearby_stops:
            return {
                'site_id': site_id,
                'latitude': latitude,
                'longitude': longitude,
                'transit_qualified': False,
                'qualification_method': 'NO_NEARBY_STOPS',
                'ctcac_points_earned': 0,
                'stops_found': 0,
                'analysis_timestamp': datetime.now().isoformat()
            }
        
        # Analyze service frequency
        frequency_analysis = self.analyze_service_frequency_optimized(nearby_stops)
        
        # Calculate CTCAC points
        scoring_result = self.calculate_ctcac_points_optimized(frequency_analysis, latitude, longitude)
        
        transit_qualified = scoring_result['total_points'] > 0
        qualification_method = 'FREQUENCY_QUALIFIED' if transit_qualified else 'FREQUENCY_NOT_QUALIFIED'
        
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
            'best_frequency_minutes': frequency_analysis['estimated_peak_frequency'],
            'hqta_details': hqta_result,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def process_portfolio_optimized(self, portfolio_file: str) -> Dict[str, Any]:
        """
        Optimized portfolio processing with performance tracking
        """
        logger.info("⚡ Starting Optimized Enhanced CTCAC Transit Analysis")
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
        
        # Process sites with progress tracking
        results = []
        hqta_qualified = 0
        frequency_qualified = 0
        not_qualified = 0
        
        start_time = datetime.now()
        
        for idx, row in df.iterrows():
            try:
                site_data = {
                    'site_id': row.get('Site_ID', f'Site_{idx}'),
                    'latitude': row['Latitude'],
                    'longitude': row['Longitude']  
                }
                
                # Analyze transit for this site
                site_result = self.analyze_site_transit_optimized(site_data)
                results.append(site_result)
                
                # Track qualification methods
                if site_result['qualification_method'] == 'HQTA_POLYGON':
                    hqta_qualified += 1
                elif site_result['transit_qualified']:
                    frequency_qualified += 1
                else:
                    not_qualified += 1
                
                # Progress tracking
                if (idx + 1) % 50 == 0:
                    elapsed = datetime.now() - start_time
                    avg_time = elapsed.total_seconds() / (idx + 1)
                    remaining = (len(df) - idx - 1) * avg_time
                    logger.info(f"⚡ Progress: {idx + 1}/{len(df)} sites ({(idx+1)/len(df)*100:.1f}%) - ETA: {remaining/60:.1f} min")
                
            except Exception as e:
                logger.error(f"❌ Error processing site {idx}: {e}")
                results.append({
                    'site_id': f'Site_{idx}',
                    'error': str(e),
                    'analysis_timestamp': datetime.now().isoformat()
                })
        
        # Generate summary
        total_qualified = hqta_qualified + frequency_qualified
        qualification_rate = (total_qualified / len(results)) * 100 if results else 0
        
        processing_time = datetime.now() - start_time
        
        summary = {
            'total_sites_analyzed': len(results),
            'hqta_qualified': hqta_qualified,
            'frequency_qualified': frequency_qualified,
            'not_qualified': not_qualified,
            'total_qualified': total_qualified,
            'qualification_rate_percent': qualification_rate,
            'processing_time_seconds': processing_time.total_seconds(),
            'avg_time_per_site': processing_time.total_seconds() / len(results) if results else 0,
            'analysis_method': 'OPTIMIZED_ENHANCED_ANALYSIS'
        }
        
        logger.info("=" * 70)
        logger.info("🏆 OPTIMIZED ENHANCED CTCAC ANALYSIS COMPLETE")  
        logger.info("=" * 70)
        logger.info(f"📊 Total sites: {len(results)}")
        logger.info(f"✅ HQTA qualified: {hqta_qualified} sites (7 points each)")
        logger.info(f"✅ Frequency qualified: {frequency_qualified} sites")
        logger.info(f"❌ Not qualified: {not_qualified} sites")
        logger.info(f"🎯 Overall qualification rate: {qualification_rate:.1f}%")
        logger.info(f"⚡ Processing time: {processing_time.total_seconds():.1f} seconds")
        logger.info(f"⚡ Avg time per site: {processing_time.total_seconds()/len(results):.2f} seconds")
        
        return {
            'summary': summary,
            'detailed_results': results,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def export_results(self, results: Dict[str, Any], output_dir: Path = None) -> List[str]:
        """Export optimized analysis results"""
        if output_dir is None:
            output_dir = self.base_dir
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_files = []
        
        # Export to Excel
        excel_file = output_dir / f"OPTIMIZED_ENHANCED_CTCAC_ANALYSIS_{timestamp}.xlsx"
        
        # Create detailed results DataFrame
        detailed_df = pd.json_normalize(results['detailed_results'])
        
        # Create summary DataFrame
        summary_df = pd.DataFrame([results['summary']])
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Summary sheet
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed results sheet
            detailed_df.to_excel(writer, sheet_name='Detailed_Results', index=False)
            
            # HQTA qualified sites
            hqta_df = detailed_df[detailed_df['qualification_method'] == 'HQTA_POLYGON'].copy()
            if len(hqta_df) > 0:
                hqta_df.to_excel(writer, sheet_name='HQTA_Qualified', index=False)
            
            # Frequency qualified sites
            freq_df = detailed_df[detailed_df['qualification_method'] == 'FREQUENCY_QUALIFIED'].copy()
            if len(freq_df) > 0:
                freq_df.to_excel(writer, sheet_name='Frequency_Qualified', index=False)
        
        output_files.append(str(excel_file))
        logger.info(f"📊 Excel report saved: {excel_file}")
        
        # Export to JSON
        json_file = output_dir / f"OPTIMIZED_ENHANCED_CTCAC_ANALYSIS_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        output_files.append(str(json_file))
        logger.info(f"📋 JSON report saved: {json_file}")
        
        return output_files


def main():
    """Main execution"""
    processor = OptimizedEnhancedCTCACProcessor()
    
    logger.info("⚡ OPTIMIZED ENHANCED CTCAC TRANSIT PROCESSOR")
    logger.info("🚀 Spatial indexing + HQTA qualification + enhanced frequency analysis")
    logger.info("🎯 Target: Sub-second per-site analysis with 90,924+ stops")
    logger.info("=" * 70)
    
    # Load datasets
    if not processor.load_datasets():
        logger.error("❌ Failed to load required datasets")
        return False
    
    # Process portfolio
    portfolio_file = processor.sites_dir / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
    
    if not portfolio_file.exists():
        logger.error(f"❌ Portfolio file not found: {portfolio_file}")
        return False
    
    try:
        results = processor.process_portfolio_optimized(str(portfolio_file))
        output_files = processor.export_results(results)
        
        logger.info("🏛️ ROMAN STANDARD: Optimized enhanced analysis complete!")
        logger.info(f"📁 Results saved to: {', '.join(output_files)}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)