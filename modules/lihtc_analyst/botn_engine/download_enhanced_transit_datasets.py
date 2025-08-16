#!/usr/bin/env python3
"""
Enhanced Transit Dataset Downloader for CTCAC Analysis

Downloads and processes multiple California transit datasets to improve
transit stop analysis for non-HQTA sites. Based on transit_datasets_ca.json
specifications and optimized for 1/3 mile CTCAC scoring requirements.
"""

import requests
import json
import pandas as pd
import geopandas as gpd
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedTransitDownloader:
    """
    Downloads and processes enhanced transit datasets for CTCAC analysis
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.transit_dir = self.base_dir / "data" / "transit"
        self.transit_dir.mkdir(parents=True, exist_ok=True)
        
        # Caltrans ArcGIS REST API endpoints
        self.caltrans_endpoints = {
            'hqts': 'https://services1.arcgis.com/KTcxiTdBatUPgs26/arcgis/rest/services/High_Quality_Transit_Stops/FeatureServer/0',
            'transit_stops': 'https://services1.arcgis.com/KTcxiTdBatUPgs26/arcgis/rest/services/California_Transit_Stops/FeatureServer/0', 
            'transit_routes': 'https://services1.arcgis.com/KTcxiTdBatUPgs26/arcgis/rest/services/California_Transit_Routes/FeatureServer/0'
        }
        
        # API parameters for statewide downloads
        self.api_params = {
            'f': 'geojson',
            'where': '1=1',  # Get all records
            'outFields': '*',
            'returnGeometry': 'true'
        }
        
    def download_caltrans_hqts(self) -> bool:
        """
        Download Caltrans High-Quality Transit Stops (HQTS)
        
        This provides detailed stop-level data including:
        - Stop ID, agency, route IDs
        - Average trips per peak hour
        - Service frequency indicators
        """
        logger.info("🚌 Downloading Caltrans High-Quality Transit Stops (HQTS)...")
        
        try:
            url = self.caltrans_endpoints['hqts'] + '/query'
            
            # Make request
            response = requests.get(url, params=self.api_params, timeout=120)
            response.raise_for_status()
            
            # Save raw GeoJSON
            hqts_file = self.transit_dir / "caltrans_hqts_stops.geojson"
            with open(hqts_file, 'w') as f:
                json.dump(response.json(), f, indent=2)
            
            # Load and analyze
            gdf = gpd.read_file(hqts_file)
            logger.info(f"✅ Downloaded {len(gdf)} HQTS stops")
            logger.info(f"HQTS columns: {list(gdf.columns)}")
            
            # Create summary
            summary = {
                'dataset': 'Caltrans High-Quality Transit Stops',
                'records': len(gdf),
                'columns': list(gdf.columns),
                'agencies': gdf['agency'].value_counts().head(10).to_dict() if 'agency' in gdf.columns else {},
                'download_date': datetime.now().isoformat(),
                'usage': 'High-quality stops with service frequency data for detailed analysis'
            }
            
            summary_file = self.transit_dir / "caltrans_hqts_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download HQTS: {e}")
            return False
    
    def download_caltrans_transit_stops(self) -> bool:
        """
        Download Caltrans California Transit Stops (comprehensive)
        
        Provides complete statewide coverage with:
        - Number of routes serving each stop (n_routes)
        - Number of arrivals per day (n_arrivals)  
        - Hours in service
        - Route IDs
        """
        logger.info("🚌 Downloading Caltrans California Transit Stops (comprehensive)...")
        
        try:
            url = self.caltrans_endpoints['transit_stops'] + '/query'
            
            # For large datasets, we may need to paginate
            all_features = []
            offset = 0
            batch_size = 1000
            
            while True:
                params = {
                    **self.api_params,
                    'resultOffset': offset,
                    'resultRecordCount': batch_size
                }
                
                response = requests.get(url, params=params, timeout=120)
                response.raise_for_status()
                data = response.json()
                
                if 'features' not in data or len(data['features']) == 0:
                    break
                
                all_features.extend(data['features'])
                logger.info(f"Downloaded batch: {len(all_features)} total stops")
                
                offset += batch_size
                time.sleep(0.5)  # Rate limiting
                
                # Safety limit
                if len(all_features) > 500000:
                    logger.warning("Reached 500K limit, stopping download")
                    break
            
            # Create complete GeoJSON
            complete_data = {
                'type': 'FeatureCollection',
                'features': all_features
            }
            
            # Save complete dataset
            stops_file = self.transit_dir / "caltrans_comprehensive_stops.geojson"
            with open(stops_file, 'w') as f:
                json.dump(complete_data, f, indent=2)
            
            # Load and analyze
            gdf = gpd.read_file(stops_file)
            logger.info(f"✅ Downloaded {len(gdf)} comprehensive transit stops")
            logger.info(f"Comprehensive stops columns: {list(gdf.columns)}")
            
            # Create summary with key statistics
            summary = {
                'dataset': 'Caltrans California Transit Stops (Comprehensive)',
                'records': len(gdf),
                'columns': list(gdf.columns),
                'n_routes_stats': {
                    'mean': gdf['n_routes'].mean() if 'n_routes' in gdf.columns else 0,
                    'max': gdf['n_routes'].max() if 'n_routes' in gdf.columns else 0,
                    'stops_with_multiple_routes': len(gdf[gdf['n_routes'] > 1]) if 'n_routes' in gdf.columns else 0
                },
                'n_arrivals_stats': {
                    'mean': gdf['n_arrivals'].mean() if 'n_arrivals' in gdf.columns else 0,
                    'max': gdf['n_arrivals'].max() if 'n_arrivals' in gdf.columns else 0
                },
                'download_date': datetime.now().isoformat(),
                'usage': 'Complete statewide stops with route counts and arrival frequencies'
            }
            
            summary_file = self.transit_dir / "caltrans_comprehensive_stops_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download comprehensive stops: {e}")
            return False
    
    def download_caltrans_transit_routes(self) -> bool:
        """
        Download Caltrans California Transit Routes
        
        Provides route-level data for frequency analysis:
        - Route name and type
        - Number of trips per route
        - Service patterns
        """
        logger.info("🚌 Downloading Caltrans California Transit Routes...")
        
        try:
            url = self.caltrans_endpoints['transit_routes'] + '/query'
            
            # Routes dataset may be large, use pagination
            all_features = []
            offset = 0
            batch_size = 1000
            
            while True:
                params = {
                    **self.api_params,
                    'resultOffset': offset,
                    'resultRecordCount': batch_size
                }
                
                response = requests.get(url, params=params, timeout=120)
                response.raise_for_status()
                data = response.json()
                
                if 'features' not in data or len(data['features']) == 0:
                    break
                
                all_features.extend(data['features'])
                logger.info(f"Downloaded batch: {len(all_features)} total routes")
                
                offset += batch_size
                time.sleep(0.5)  # Rate limiting
                
                # Safety limit
                if len(all_features) > 100000:
                    logger.warning("Reached 100K route limit, stopping download")
                    break
            
            # Create complete GeoJSON
            complete_data = {
                'type': 'FeatureCollection',
                'features': all_features
            }
            
            # Save routes dataset
            routes_file = self.transit_dir / "caltrans_transit_routes.geojson"
            with open(routes_file, 'w') as f:
                json.dump(complete_data, f, indent=2)
            
            # Load and analyze
            gdf = gpd.read_file(routes_file)
            logger.info(f"✅ Downloaded {len(gdf)} transit routes")
            logger.info(f"Routes columns: {list(gdf.columns)}")
            
            # Create summary
            summary = {
                'dataset': 'Caltrans California Transit Routes',
                'records': len(gdf),
                'columns': list(gdf.columns),
                'route_types': gdf['route_type'].value_counts().to_dict() if 'route_type' in gdf.columns else {},
                'n_trips_stats': {
                    'mean': gdf['n_trips'].mean() if 'n_trips' in gdf.columns else 0,
                    'max': gdf['n_trips'].max() if 'n_trips' in gdf.columns else 0
                },
                'download_date': datetime.now().isoformat(),
                'usage': 'Route-level data for service frequency analysis'
            }
            
            summary_file = self.transit_dir / "caltrans_routes_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download routes: {e}")
            return False
    
    def test_transitland_api(self, test_lat: float = 37.7749, test_lon: float = -122.4194) -> bool:
        """
        Test Transitland v2 API and download sample data
        
        This provides real-time GTFS data aggregation across the US
        """
        logger.info("🚌 Testing Transitland v2 API...")
        
        try:
            # Test API with San Francisco coordinates
            base_url = "https://transit.land/api/v2/rest/stops"
            params = {
                'lat': test_lat,
                'lon': test_lon,
                'radius': 1000,  # 1km radius for test
                'limit': 100
            }
            
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✅ Transitland API working: {len(data.get('stops', []))} stops found")
            
            # Save sample data and API documentation
            sample_file = self.transit_dir / "transitland_api_sample.json"
            with open(sample_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Create API usage guide
            api_guide = {
                'api_endpoint': 'https://transit.land/api/v2/rest/stops',
                'usage': 'Real-time GTFS data aggregation for US transit systems',
                'parameters': {
                    'lat': 'Latitude coordinate',
                    'lon': 'Longitude coordinate', 
                    'radius': 'Search radius in meters (max 10000)',
                    'limit': 'Maximum results to return'
                },
                'ctcac_usage': 'For 1/3 mile analysis, use radius=536 meters',
                'example_request': f"{base_url}?lat={test_lat}&lon={test_lon}&radius=536",
                'test_results': {
                    'stops_found': len(data.get('stops', [])),
                    'sample_fields': list(data.get('stops', [{}])[0].keys()) if data.get('stops') else []
                }
            }
            
            guide_file = self.transit_dir / "transitland_api_guide.json"
            with open(guide_file, 'w') as f:
                json.dump(api_guide, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Transitland API test failed: {e}")
            return False
    
    def download_all_datasets(self) -> Dict[str, bool]:
        """Download all enhanced transit datasets"""
        logger.info("🚀 Starting enhanced transit dataset downloads...")
        
        results = {}
        
        # Download Caltrans datasets
        results['hqts'] = self.download_caltrans_hqts()
        results['comprehensive_stops'] = self.download_caltrans_transit_stops()
        results['routes'] = self.download_caltrans_transit_routes()
        
        # Test Transitland API
        results['transitland_api'] = self.test_transitland_api()
        
        # Create master summary
        master_summary = {
            'download_session': datetime.now().isoformat(),
            'datasets_downloaded': results,
            'successful_downloads': sum(results.values()),
            'total_attempted': len(results),
            'next_steps': [
                'Integrate HQTS data for high-quality stop identification',
                'Use comprehensive stops for complete 1/3 mile analysis',
                'Leverage routes data for service frequency calculations',
                'Implement Transitland API for real-time data queries'
            ],
            'ctcac_integration': {
                'hqta_boundary_check': 'WORKING - 28 sites identified',
                'transit_stop_analysis': 'TO BE ENHANCED with new datasets',
                'methodology': 'HQTA first, then enhanced stop analysis for non-HQTA sites'
            }
        }
        
        summary_file = self.transit_dir / "enhanced_datasets_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(master_summary, f, indent=2)
        
        logger.info("="*70)
        logger.info("🏆 ENHANCED TRANSIT DATASET DOWNLOAD SUMMARY")
        logger.info("="*70)
        for dataset, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            logger.info(f"{dataset}: {status}")
        
        logger.info(f"\n📊 Success Rate: {sum(results.values())}/{len(results)} datasets")
        logger.info(f"📁 Files saved to: {self.transit_dir}")
        
        return results


def main():
    """Main execution"""
    downloader = EnhancedTransitDownloader()
    
    logger.info("🎯 ENHANCED TRANSIT DATASET DOWNLOADER")
    logger.info("📋 Improving CTCAC transit analysis for non-HQTA sites")
    logger.info("🏆 HQTA boundary analysis already working (28 sites qualified)")
    logger.info("="*70)
    
    results = downloader.download_all_datasets()
    
    if sum(results.values()) > 0:
        logger.info("\n🏛️ ROMAN STANDARD: Enhanced transit datasets acquired!")
        logger.info("⚔️ Ready for improved non-HQTA transit stop analysis")
        return True
    else:
        logger.error("\n❌ Failed to download enhanced datasets")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)