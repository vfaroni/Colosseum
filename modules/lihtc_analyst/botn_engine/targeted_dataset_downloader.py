#!/usr/bin/env python3
"""
Targeted Dataset Downloader for the 3 Missing Datasets

Downloads the specific datasets identified from CA.gov portal:
1. High Quality Transit Stops (HQTS) - with peak hour frequency data
2. California Transit Stops - enhanced comprehensive coverage
3. Average Transit Speeds by Stop - frequency/speed indicators

Also extracts detailed schedule data from existing GTFS ZIP files.
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
import zipfile
import io

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TargetedDatasetDownloader:
    """
    Downloads the 3 specific datasets we identified as accessible
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.transit_dir = self.base_dir / "data" / "transit"
        self.transit_dir.mkdir(parents=True, exist_ok=True)
        
        # Specific datasets to download from CA.gov
        self.target_datasets = {
            'hqts': {
                'name': 'High Quality Transit Stops',
                'url': 'https://data.ca.gov/dataset/high-quality-transit-stops',
                'description': 'Stop-level data with peak hour frequency information'
            },
            'enhanced_stops': {
                'name': 'California Transit Stops', 
                'url': 'https://data.ca.gov/dataset/california-transit-stops',
                'description': 'Enhanced comprehensive transit stops dataset'
            },
            'transit_speeds': {
                'name': 'Average Transit Speeds by Stop',
                'url': 'https://data.ca.gov/dataset/average-transit-speeds-by-stop', 
                'description': 'Speed and frequency indicators by stop'
            }
        }
        
        logger.info("🎯 Targeted Dataset Downloader initialized")
        logger.info(f"📁 Target directory: {self.transit_dir}")
        logger.info(f"📊 {len(self.target_datasets)} specific datasets identified")
    
    def get_dataset_resources(self, dataset_url: str) -> List[Dict]:
        """Get available resources (files) from a CA.gov dataset page"""
        try:
            # Extract dataset name from URL
            dataset_name = dataset_url.split('/')[-1]
            
            # Use CKAN API to get dataset details
            api_url = f"https://data.ca.gov/api/3/action/package_show?id={dataset_name}"
            
            response = requests.get(api_url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    resources = data.get('result', {}).get('resources', [])
                    
                    # Filter for downloadable formats
                    downloadable = []
                    for resource in resources:
                        format_type = resource.get('format', '').lower()
                        if format_type in ['geojson', 'csv', 'json', 'zip', 'shp', 'xlsx']:
                            downloadable.append({
                                'name': resource.get('name', 'Unknown'),
                                'format': format_type,
                                'url': resource.get('url'),
                                'size': resource.get('size'),
                                'last_modified': resource.get('last_modified'),
                                'description': resource.get('description', '')
                            })
                    
                    return downloadable
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Failed to get resources for {dataset_url}: {e}")
            return []
    
    def download_resource(self, resource: Dict, dataset_key: str) -> Optional[str]:
        """Download a specific resource file"""
        try:
            url = resource['url']
            format_type = resource['format']
            
            logger.info(f"⬇️ Downloading {resource['name']} ({format_type.upper()})...")
            
            response = requests.get(url, timeout=120, stream=True)
            response.raise_for_status()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d")
            safe_name = resource['name'].replace(' ', '_').replace('/', '_')
            filename = f"{dataset_key}_{safe_name}_{timestamp}.{format_type}"
            
            file_path = self.transit_dir / filename
            
            # Download with progress tracking
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (1024*1024) == 0:  # Log every MB
                                logger.info(f"   Progress: {progress:.1f}% ({downloaded:,} / {total_size:,} bytes)")
            
            file_size = file_path.stat().st_size
            logger.info(f"✅ Downloaded: {filename} ({file_size:,} bytes)")
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Download failed for {resource['name']}: {e}")
            return None
    
    def download_dataset(self, dataset_key: str, dataset_info: Dict) -> Dict[str, Any]:
        """Download all resources for a specific dataset"""
        logger.info(f"📦 Downloading dataset: {dataset_info['name']}")
        
        # Get available resources
        resources = self.get_dataset_resources(dataset_info['url'])
        
        if not resources:
            return {
                'status': 'no_resources',
                'message': 'No downloadable resources found'
            }
        
        logger.info(f"📄 Found {len(resources)} downloadable resources:")
        for resource in resources:
            size_info = f" ({resource['size']} bytes)" if resource['size'] else ""
            logger.info(f"   - {resource['name']} ({resource['format'].upper()}){size_info}")
        
        # Download resources (prioritize GeoJSON and CSV)
        downloaded_files = []
        priority_formats = ['geojson', 'csv', 'json']
        
        # First, download priority formats
        for format_type in priority_formats:
            matching_resources = [r for r in resources if r['format'] == format_type]
            for resource in matching_resources[:2]:  # Limit to 2 per format
                file_path = self.download_resource(resource, dataset_key)
                if file_path:
                    downloaded_files.append({
                        'file_path': file_path,
                        'resource_info': resource
                    })
        
        return {
            'status': 'success',
            'resources_found': len(resources),
            'files_downloaded': len(downloaded_files),
            'downloaded_files': downloaded_files
        }
    
    def extract_gtfs_schedule_data(self) -> Dict[str, Any]:
        """Extract detailed schedule data from existing GTFS ZIP files"""
        logger.info("📦 Extracting detailed schedule data from GTFS files...")
        
        results = {}
        gtfs_files = list(self.transit_dir.glob("*.zip"))
        
        for zip_file in gtfs_files:
            logger.info(f"🔍 Processing {zip_file.name}...")
            
            try:
                with zipfile.ZipFile(zip_file, 'r') as zf:
                    # Extract stop_times.txt for frequency analysis
                    if 'stop_times.txt' in zf.namelist():
                        logger.info(f"   📄 Extracting stop_times.txt...")
                        
                        # Extract to CSV for analysis
                        stop_times_path = self.transit_dir / f"{zip_file.stem}_stop_times.csv"
                        
                        with zf.open('stop_times.txt') as source:
                            with open(stop_times_path, 'wb') as target:
                                target.write(source.read())
                        
                        # Load and sample the data
                        stop_times_df = pd.read_csv(stop_times_path, nrows=10000)  # Sample first 10k rows
                        
                        logger.info(f"   ✅ Extracted {len(stop_times_df)} schedule records")
                        logger.info(f"   📊 Columns: {list(stop_times_df.columns)}")
                        
                        # Analyze peak hour patterns
                        if 'arrival_time' in stop_times_df.columns:
                            # Convert times and analyze peak hours
                            stop_times_df['hour'] = stop_times_df['arrival_time'].str.split(':').str[0].astype(int, errors='ignore')
                            
                            # Count arrivals by hour
                            hourly_counts = stop_times_df['hour'].value_counts().sort_index()
                            peak_am = hourly_counts.get(7, 0) + hourly_counts.get(8, 0)
                            peak_pm = hourly_counts.get(16, 0) + hourly_counts.get(17, 0)
                            
                            logger.info(f"   🕐 Peak AM arrivals (7-9): {peak_am}")
                            logger.info(f"   🕕 Peak PM arrivals (4-6): {peak_pm}")
                        
                        results[zip_file.name] = {
                            'status': 'success',
                            'stop_times_file': str(stop_times_path),
                            'records_extracted': len(stop_times_df),
                            'peak_am_arrivals': peak_am if 'arrival_time' in stop_times_df.columns else 0,
                            'peak_pm_arrivals': peak_pm if 'arrival_time' in stop_times_df.columns else 0,
                            'columns': list(stop_times_df.columns)
                        }
                    
                    # Also extract routes.txt if available
                    if 'routes.txt' in zf.namelist():
                        routes_path = self.transit_dir / f"{zip_file.stem}_routes.csv"
                        
                        with zf.open('routes.txt') as source:
                            with open(routes_path, 'wb') as target:
                                target.write(source.read())
                        
                        routes_df = pd.read_csv(routes_path)
                        logger.info(f"   📄 Extracted {len(routes_df)} route records")
                        
                        if zip_file.name in results:
                            results[zip_file.name]['routes_file'] = str(routes_path)
                            results[zip_file.name]['routes_extracted'] = len(routes_df)
                    
            except Exception as e:
                results[zip_file.name] = {
                    'status': 'extraction_error',
                    'error': str(e)
                }
                logger.error(f"❌ Failed to extract from {zip_file.name}: {e}")
        
        return results
    
    def run_targeted_downloads(self) -> Dict[str, Any]:
        """Execute targeted downloads of the 3 identified datasets"""
        logger.info("🚀 Starting targeted dataset downloads...")
        logger.info("=" * 70)
        
        all_results = {
            'download_timestamp': datetime.now().isoformat(),
            'target_datasets': list(self.target_datasets.keys()),
            'downloads': {},
            'gtfs_extractions': {}
        }
        
        # Download each target dataset
        for dataset_key, dataset_info in self.target_datasets.items():
            logger.info(f"🎯 {dataset_key.upper()}: {dataset_info['name']}")
            logger.info(f"   📋 {dataset_info['description']}")
            
            try:
                result = self.download_dataset(dataset_key, dataset_info)
                all_results['downloads'][dataset_key] = result
                
                if result['status'] == 'success':
                    logger.info(f"   ✅ Success: {result['files_downloaded']} files downloaded")
                else:
                    logger.warning(f"   ⚠️ {result['status']}: {result.get('message', 'Unknown error')}")
                
            except Exception as e:
                all_results['downloads'][dataset_key] = {
                    'status': 'download_error',
                    'error': str(e)
                }
                logger.error(f"   ❌ Download failed: {e}")
            
            time.sleep(1)  # Rate limiting
        
        # Extract GTFS schedule data
        logger.info("📦 GTFS Schedule Data Extraction...")
        all_results['gtfs_extractions'] = self.extract_gtfs_schedule_data()
        
        # Save comprehensive results
        results_file = self.transit_dir / f"targeted_dataset_downloads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        logger.info("=" * 70)
        logger.info("🏆 TARGETED DATASET DOWNLOADS COMPLETE")
        logger.info("=" * 70)
        logger.info(f"📄 Results saved: {results_file.name}")
        
        # Generate summary
        self.generate_download_summary(all_results)
        
        return all_results
    
    def generate_download_summary(self, results: Dict[str, Any]):
        """Generate summary of download results"""
        logger.info("\n🎯 DOWNLOAD RESULTS SUMMARY:")
        
        downloads = results.get('downloads', {})
        gtfs_extractions = results.get('gtfs_extractions', {})
        
        # Dataset downloads
        for dataset_key, result in downloads.items():
            dataset_name = self.target_datasets[dataset_key]['name']
            if result.get('status') == 'success':
                files_count = result.get('files_downloaded', 0)
                logger.info(f"   ✅ {dataset_name}: {files_count} files downloaded")
            else:
                logger.info(f"   ❌ {dataset_name}: {result.get('status', 'Failed')}")
        
        # GTFS extractions
        successful_extractions = [name for name, data in gtfs_extractions.items() if data.get('status') == 'success']
        if successful_extractions:
            total_records = sum(data.get('records_extracted', 0) for data in gtfs_extractions.values() if data.get('status') == 'success')
            logger.info(f"   ✅ GTFS Schedules: {len(successful_extractions)} files, {total_records:,} schedule records")
        else:
            logger.info(f"   ❌ GTFS Schedules: No schedule data extracted")
        
        # Next steps
        logger.info("\n💡 NEXT STEPS:")
        total_downloads = sum(1 for result in downloads.values() if result.get('status') == 'success')
        if total_downloads > 0:
            logger.info(f"   1. Integrate {total_downloads} new datasets into frequency analysis")
        if successful_extractions:
            logger.info(f"   2. Parse {len(successful_extractions)} GTFS schedule files for precise frequencies")
        logger.info("   3. Update optimized processor to use enhanced datasets")
        logger.info("   4. Re-run portfolio analysis with improved data")


def main():
    """Main execution"""
    downloader = TargetedDatasetDownloader()
    
    logger.info("🎯 TARGETED TRANSIT DATASET DOWNLOADER")
    logger.info("📋 Downloading 3 specific datasets identified from CA.gov portal:")
    logger.info("   1. High Quality Transit Stops (HQTS) - peak hour frequency")
    logger.info("   2. California Transit Stops - enhanced comprehensive")
    logger.info("   3. Average Transit Speeds by Stop - frequency indicators")
    logger.info("   + GTFS schedule extraction for precise frequency analysis")
    logger.info("=" * 70)
    
    results = downloader.run_targeted_downloads()
    
    logger.info("\n🏛️ ROMAN STANDARD: Targeted acquisition complete!")
    logger.info("⚔️ Enhanced datasets ready for integration")
    
    return results


if __name__ == "__main__":
    results = main()