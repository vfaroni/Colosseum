#!/usr/bin/env python3
"""
Alternative Dataset Downloader for Enhanced Transit Analysis

Attempts to download the 3 missing datasets using alternative approaches:
1. Caltrans High-Quality Transit Stops (HQTS) - with peak hour frequency data
2. Transitland v2 API sampling - for real-time GTFS validation  
3. Alternative Caltrans endpoints - for comprehensive routes/stops

Uses fallback methods when primary APIs fail.
"""

import requests
import json
import pandas as pd
import geopandas as gpd
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import time
import zipfile
import io

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlternativeDatasetDownloader:
    """
    Downloads transit datasets using alternative methods and endpoints
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.transit_dir = self.base_dir / "data" / "transit"
        self.transit_dir.mkdir(parents=True, exist_ok=True)
        
        # Alternative endpoints to try
        self.alternative_endpoints = {
            'caltrans_open_data': 'https://gisdata-caltrans.opendata.arcgis.com',
            'ca_gov_data': 'https://data.ca.gov',
            'caltrans_gis_direct': 'https://services.arcgis.com/Xo7pKYo9dWi64yqQ/arcgis/rest/services',
            'transit_land_feeds': 'https://www.transit.land/feeds'
        }
        
        logger.info("🔄 Alternative Dataset Downloader initialized")
        logger.info(f"📁 Target directory: {self.transit_dir}")
    
    def search_caltrans_open_data_portal(self) -> List[Dict]:
        """Search Caltrans Open Data Portal for transit datasets"""
        logger.info("🔍 Searching Caltrans Open Data Portal...")
        
        try:
            # Try the main Caltrans open data hub
            search_url = f"{self.alternative_endpoints['caltrans_open_data']}/search"
            params = {
                'q': 'transit stops',
                'sort': 'relevance',
                'tags': 'transportation,transit'
            }
            
            response = requests.get(search_url, params=params, timeout=30)
            if response.status_code == 200:
                logger.info("✅ Successfully accessed Caltrans Open Data Portal")
                
                # Try to find direct dataset links
                datasets_found = []
                
                # Look for specific dataset patterns in the response
                content = response.text.lower()
                if 'transit' in content and 'stops' in content:
                    logger.info("🎯 Found transit-related content")
                    datasets_found.append({
                        'source': 'caltrans_open_data',
                        'search_url': search_url,
                        'content_preview': content[:500]
                    })
                
                return datasets_found
            else:
                logger.warning(f"⚠️ Caltrans portal returned {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Caltrans portal search failed: {e}")
            return []
    
    def try_alternative_caltrans_endpoints(self) -> Dict[str, Any]:
        """Try alternative Caltrans GIS service endpoints"""
        logger.info("🔍 Trying alternative Caltrans GIS endpoints...")
        
        results = {}
        
        # Alternative service URLs to try
        service_urls = [
            'https://services1.arcgis.com/KTcxiTdBatUPgs26/arcgis/rest/services',
            'https://services2.arcgis.com/KTcxiTdBatUPgs26/arcgis/rest/services', 
            'https://services3.arcgis.com/KTcxiTdBatUPgs26/arcgis/rest/services',
            'https://gis.dot.ca.gov/arcgis/rest/services',
            'https://caltrans-gis.dot.ca.gov/arcgis/rest/services'
        ]
        
        for service_url in service_urls:
            try:
                # Try to get service directory
                response = requests.get(f"{service_url}?f=json", timeout=30)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'services' in data:
                            transit_services = [
                                s for s in data['services'] 
                                if any(keyword in s['name'].lower() for keyword in ['transit', 'stop', 'route', 'bus'])
                            ]
                            
                            if transit_services:
                                results[service_url] = {
                                    'status': 'success',
                                    'transit_services': transit_services,
                                    'total_services': len(data['services'])
                                }
                                logger.info(f"✅ Found {len(transit_services)} transit services at {service_url}")
                            else:
                                results[service_url] = {
                                    'status': 'no_transit_services',
                                    'total_services': len(data['services'])
                                }
                    except json.JSONDecodeError:
                        results[service_url] = {
                            'status': 'json_decode_error',
                            'content_preview': response.text[:200]
                        }
                else:
                    results[service_url] = {
                        'status': f'http_error_{response.status_code}'
                    }
                    
            except Exception as e:
                results[service_url] = {
                    'status': 'connection_error',
                    'error': str(e)
                }
        
        return results
    
    def sample_transitland_api(self, sample_locations: List[Tuple[float, float]] = None) -> Dict[str, Any]:
        """Sample Transitland API with multiple California locations"""
        logger.info("🚌 Sampling Transitland v2 API...")
        
        if sample_locations is None:
            # Key California transit hubs for sampling
            sample_locations = [
                (37.7749, -122.4194),  # San Francisco
                (34.0522, -118.2437),  # Los Angeles  
                (32.7157, -117.1611),  # San Diego
                (37.3382, -121.8863),  # San Jose
                (38.5767, -121.4934),  # Sacramento
            ]
        
        api_results = {}
        
        for i, (lat, lon) in enumerate(sample_locations):
            location_name = ['SF', 'LA', 'SD', 'SJ', 'SAC'][i]
            
            try:
                # Try Transitland v2 stops endpoint (no auth required for basic queries)
                url = "https://transit.land/api/v2/rest/stops"
                params = {
                    'lat': lat,
                    'lon': lon,
                    'radius': 1000,  # 1km
                    'limit': 50
                }
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    api_results[location_name] = {
                        'status': 'success',
                        'stops_found': len(data.get('stops', [])),
                        'sample_data': data.get('stops', [])[:3],  # First 3 stops as sample
                        'location': (lat, lon)
                    }
                    logger.info(f"✅ {location_name}: Found {len(data.get('stops', []))} stops")
                    
                elif response.status_code == 401:
                    api_results[location_name] = {
                        'status': 'auth_required',
                        'message': 'API key required for this endpoint'
                    }
                    logger.warning(f"🔐 {location_name}: Authentication required")
                    
                else:
                    api_results[location_name] = {
                        'status': f'http_error_{response.status_code}',
                        'response_preview': response.text[:200]
                    }
                    
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                api_results[location_name] = {
                    'status': 'connection_error',
                    'error': str(e)
                }
                logger.error(f"❌ {location_name}: API error - {e}")
        
        return api_results
    
    def try_ca_gov_data_portal(self) -> Dict[str, Any]:
        """Search California's official data portal for transit datasets"""
        logger.info("🏛️ Searching California.gov data portal...")
        
        try:
            # Use the CKAN API that we know works from the investigation
            search_queries = [
                'caltrans transit stops',
                'high quality transit',
                'transit routes california',
                'gtfs california'
            ]
            
            results = {}
            
            for query in search_queries:
                try:
                    url = "https://data.ca.gov/api/3/action/package_search"
                    params = {
                        'q': query,
                        'rows': 10
                    }
                    
                    response = requests.get(url, params=params, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        datasets = data.get('result', {}).get('results', [])
                        
                        transit_datasets = []
                        for dataset in datasets:
                            if any(keyword in dataset.get('title', '').lower() for keyword in ['transit', 'transportation', 'bus', 'rail']):
                                transit_datasets.append({
                                    'title': dataset.get('title'),
                                    'name': dataset.get('name'),
                                    'resources': len(dataset.get('resources', [])),
                                    'organization': dataset.get('organization', {}).get('title'),
                                    'url': f"https://data.ca.gov/dataset/{dataset.get('name')}"
                                })
                        
                        if transit_datasets:
                            results[query] = {
                                'status': 'success',
                                'datasets_found': len(transit_datasets),
                                'datasets': transit_datasets
                            }
                            logger.info(f"✅ Query '{query}': Found {len(transit_datasets)} transit datasets")
                        
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"❌ Query '{query}' failed: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ CA.gov portal search failed: {e}")
            return {}
    
    def extract_gtfs_from_existing_zips(self) -> Dict[str, Any]:
        """Extract detailed schedule data from existing GTFS ZIP files"""
        logger.info("📦 Extracting data from existing GTFS ZIP files...")
        
        results = {}
        
        # Look for existing GTFS ZIP files
        gtfs_files = list(self.transit_dir.glob("*.zip"))
        
        for zip_file in gtfs_files:
            logger.info(f"🔍 Analyzing {zip_file.name}...")
            
            try:
                with zipfile.ZipFile(zip_file, 'r') as zf:
                    file_list = zf.namelist()
                    
                    # Check for key GTFS files
                    gtfs_files_found = {
                        'stops.txt': 'stops.txt' in file_list,
                        'routes.txt': 'routes.txt' in file_list,
                        'stop_times.txt': 'stop_times.txt' in file_list,
                        'trips.txt': 'trips.txt' in file_list,
                        'calendar.txt': 'calendar.txt' in file_list
                    }
                    
                    if gtfs_files_found['stops.txt']:
                        # Extract stops data
                        with zf.open('stops.txt') as f:
                            stops_df = pd.read_csv(f)
                            
                        # Extract sample stop_times if available
                        sample_stop_times = None
                        if gtfs_files_found['stop_times.txt']:
                            with zf.open('stop_times.txt') as f:
                                # Read just first 1000 rows for sampling
                                sample_stop_times = pd.read_csv(f, nrows=1000)
                        
                        results[zip_file.name] = {
                            'status': 'success',
                            'gtfs_files': gtfs_files_found,
                            'stops_count': len(stops_df),
                            'stops_sample': stops_df.head(3).to_dict('records'),
                            'stop_times_sample_count': len(sample_stop_times) if sample_stop_times is not None else 0,
                            'has_schedule_data': gtfs_files_found['stop_times.txt']
                        }
                        
                        logger.info(f"✅ {zip_file.name}: Found {len(stops_df)} stops with {'schedule data' if gtfs_files_found['stop_times.txt'] else 'no schedule data'}")
                    
            except Exception as e:
                results[zip_file.name] = {
                    'status': 'extraction_error',
                    'error': str(e)
                }
                logger.error(f"❌ Failed to extract {zip_file.name}: {e}")
        
        return results
    
    def run_comprehensive_search(self) -> Dict[str, Any]:
        """Run comprehensive search across all alternative sources"""
        logger.info("🚀 Starting comprehensive alternative dataset search...")
        logger.info("=" * 70)
        
        all_results = {
            'search_timestamp': datetime.now().isoformat(),
            'target_datasets': [
                'Caltrans High-Quality Transit Stops (HQTS) - with peak hour frequency',
                'Transitland v2 API - real-time GTFS validation',
                'Enhanced Caltrans routes/stops - comprehensive coverage'
            ]
        }
        
        # 1. Search Caltrans Open Data Portal
        logger.info("1️⃣ Searching Caltrans Open Data Portal...")
        all_results['caltrans_portal'] = self.search_caltrans_open_data_portal()
        
        # 2. Try alternative Caltrans endpoints
        logger.info("2️⃣ Trying alternative Caltrans GIS endpoints...")
        all_results['caltrans_gis_alternatives'] = self.try_alternative_caltrans_endpoints()
        
        # 3. Sample Transitland API
        logger.info("3️⃣ Sampling Transitland v2 API...")
        all_results['transitland_sampling'] = self.sample_transitland_api()
        
        # 4. Search CA.gov data portal
        logger.info("4️⃣ Searching California.gov data portal...")
        all_results['ca_gov_portal'] = self.try_ca_gov_data_portal()
        
        # 5. Extract from existing GTFS files
        logger.info("5️⃣ Extracting from existing GTFS ZIP files...")
        all_results['existing_gtfs_extraction'] = self.extract_gtfs_from_existing_zips()
        
        # Save comprehensive results
        results_file = self.transit_dir / f"alternative_dataset_search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        logger.info("=" * 70)
        logger.info("🏆 COMPREHENSIVE ALTERNATIVE SEARCH COMPLETE")
        logger.info("=" * 70)
        logger.info(f"📄 Results saved: {results_file.name}")
        
        # Generate summary
        self.generate_search_summary(all_results)
        
        return all_results
    
    def generate_search_summary(self, results: Dict[str, Any]):
        """Generate human-readable summary of search results"""
        logger.info("\n🎯 SEARCH RESULTS SUMMARY:")
        
        findings = []
        
        # Caltrans Portal
        caltrans_results = results.get('caltrans_portal', [])
        if caltrans_results:
            findings.append(f"✅ Caltrans Portal: {len(caltrans_results)} potential sources found")
        else:
            findings.append("❌ Caltrans Portal: No accessible datasets found")
        
        # GIS Alternatives  
        gis_results = results.get('caltrans_gis_alternatives', {})
        successful_endpoints = [url for url, data in gis_results.items() if data.get('status') == 'success']
        if successful_endpoints:
            findings.append(f"✅ GIS Endpoints: {len(successful_endpoints)} working endpoints found")
        else:
            findings.append("❌ GIS Endpoints: No working alternative endpoints")
        
        # Transitland
        transitland_results = results.get('transitland_sampling', {})
        successful_locations = [loc for loc, data in transitland_results.items() if data.get('status') == 'success']
        if successful_locations:
            total_stops = sum(data.get('stops_found', 0) for data in transitland_results.values() if data.get('status') == 'success')
            findings.append(f"✅ Transitland API: Working! {len(successful_locations)} locations, {total_stops} total stops sampled")
        else:
            findings.append("❌ Transitland API: Authentication required or not accessible")
        
        # CA.gov Portal
        ca_gov_results = results.get('ca_gov_portal', {})
        total_datasets = sum(data.get('datasets_found', 0) for data in ca_gov_results.values() if isinstance(data, dict))
        if total_datasets > 0:
            findings.append(f"✅ CA.gov Portal: {total_datasets} transit-related datasets found")
        else:
            findings.append("❌ CA.gov Portal: No new transit datasets found")
        
        # Existing GTFS
        gtfs_results = results.get('existing_gtfs_extraction', {})
        gtfs_with_schedules = [name for name, data in gtfs_results.items() if data.get('has_schedule_data')]
        if gtfs_with_schedules:
            findings.append(f"✅ Existing GTFS: {len(gtfs_with_schedules)} files with detailed schedule data")
        else:
            findings.append("❌ Existing GTFS: No detailed schedule data available")
        
        for finding in findings:
            logger.info(f"   {finding}")
        
        # Recommendations
        logger.info("\n💡 RECOMMENDATIONS:")
        if successful_locations:
            logger.info("   1. Transitland API is accessible - implement for real-time validation")
        if gtfs_with_schedules:
            logger.info("   2. Extract stop_times.txt from existing GTFS for precise frequencies")
        if successful_endpoints:
            logger.info("   3. Explore working GIS endpoints for additional datasets")
        if total_datasets > 0:
            logger.info("   4. Download specific datasets found in CA.gov portal")
        
        logger.info("\n🎯 NEXT STEPS: Based on findings, attempt actual downloads of accessible datasets")


def main():
    """Main execution"""
    downloader = AlternativeDatasetDownloader()
    
    logger.info("🔄 ALTERNATIVE TRANSIT DATASET DOWNLOADER")
    logger.info("🎯 Attempting to acquire 3 missing datasets for enhanced frequency analysis")
    logger.info("📋 Target: HQTS, Transitland API, Enhanced Caltrans data")
    logger.info("=" * 70)
    
    results = downloader.run_comprehensive_search()
    
    logger.info("\n🏛️ ROMAN STANDARD: Comprehensive search complete!")
    logger.info("⚔️ Alternative acquisition methods identified")
    
    return results


if __name__ == "__main__":
    results = main()