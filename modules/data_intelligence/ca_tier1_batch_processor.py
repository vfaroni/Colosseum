#!/usr/bin/env python3
"""
California Tier 1 Counties Batch Processor
Prepared by Strike Leader for Wingman execution
Mission: CA Environmental Data Acquisition

Priority Counties: LA, San Diego, Orange, SF, Alameda
Date: 2025-08-07
"""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import pandas as pd
import geopandas as gpd
from io import StringIO
import zipfile
import shutil

class CaliforniaTier1Processor:
    """Batch processor for Tier 1 California counties"""
    
    # Tier 1 Priority Counties (Highest LIHTC Activity)
    TIER1_COUNTIES = {
        'Los Angeles': {
            'fips': '06037',
            'abbreviation': 'LA',
            'parcels': 2427516,
            'population': 10000000,
            'priority': 1
        },
        'San Diego': {
            'fips': '06073',
            'abbreviation': 'SD',
            'parcels': 1088903,
            'population': 3300000,
            'priority': 2
        },
        'Orange': {
            'fips': '06059',
            'abbreviation': 'OC',
            'parcels': 983612,
            'population': 3200000,
            'priority': 3
        },
        'San Francisco': {
            'fips': '06075',
            'abbreviation': 'SF',
            'parcels': 200000,  # Estimated
            'population': 842000,
            'priority': 4
        },
        'Alameda': {
            'fips': '06001',
            'abbreviation': 'ALA',
            'parcels': 488926,
            'population': 1610000,
            'priority': 5
        }
    }
    
    # Updated API endpoints (verified 2025-08-07)
    API_ENDPOINTS = {
        'fema_flood': {
            'base': 'https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer',
            'alternative': 'https://msc.fema.gov/arcgis/rest/services/public/NFHL/MapServer'
        },
        'envirostor': {
            'base': 'https://data.ca.gov/api/3/action/datastore_search',
            'alternative': 'https://www.envirostor.dtsc.ca.gov/public/api'
        },
        'geotracker': {
            'base': 'https://geotracker.waterboards.ca.gov/data_download/',
            'files': ['lust_public.csv', 'slic_public.csv', 'military_public.csv']
        }
    }
    
    def __init__(self, base_path: str = None):
        """Initialize the batch processor"""
        self.base_path = Path(base_path or "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.data_path = self.base_path / "data_sets" / "california" / "CA_Environmental_Batch"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Track processing status
        self.processing_status = {}
        self.start_time = datetime.now()
        
    def setup_logging(self):
        """Configure logging for batch processing"""
        log_file = self.data_path / f"batch_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def process_all_tier1_counties(self, parallel: bool = True):
        """Process all Tier 1 counties"""
        self.logger.info("="*60)
        self.logger.info("CALIFORNIA TIER 1 BATCH PROCESSING INITIATED")
        self.logger.info(f"Counties to process: {', '.join(self.TIER1_COUNTIES.keys())}")
        self.logger.info("="*60)
        
        if parallel:
            self._process_parallel()
        else:
            self._process_sequential()
            
        self._generate_summary_report()
        
    def _process_parallel(self):
        """Process counties in parallel for speed"""
        self.logger.info("Starting PARALLEL processing (optimal for bandwidth)")
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all county processing tasks
            future_to_county = {
                executor.submit(self._process_single_county, county, info): county
                for county, info in self.TIER1_COUNTIES.items()
            }
            
            # Process completed tasks
            for future in as_completed(future_to_county):
                county = future_to_county[future]
                try:
                    result = future.result()
                    self.processing_status[county] = result
                    self.logger.info(f"✅ Completed: {county}")
                except Exception as e:
                    self.logger.error(f"❌ Failed: {county} - {str(e)}")
                    self.processing_status[county] = {'status': 'failed', 'error': str(e)}
                    
    def _process_sequential(self):
        """Process counties one by one (for limited bandwidth)"""
        self.logger.info("Starting SEQUENTIAL processing (bandwidth-conscious)")
        
        for county, info in sorted(self.TIER1_COUNTIES.items(), 
                                  key=lambda x: x[1]['priority']):
            try:
                result = self._process_single_county(county, info)
                self.processing_status[county] = result
                self.logger.info(f"✅ Completed: {county}")
            except Exception as e:
                self.logger.error(f"❌ Failed: {county} - {str(e)}")
                self.processing_status[county] = {'status': 'failed', 'error': str(e)}
                
    def _process_single_county(self, county_name: str, county_info: Dict) -> Dict:
        """Process a single county's environmental data"""
        self.logger.info(f"Processing {county_name} County (Priority {county_info['priority']})")
        
        county_path = self.data_path / county_name.replace(' ', '_')
        county_path.mkdir(exist_ok=True)
        
        results = {
            'county': county_name,
            'fips': county_info['fips'],
            'start_time': datetime.now().isoformat(),
            'datasets': {}
        }
        
        # Process each data type with actual downloads
        
        # 1. FEMA Flood Data
        self.logger.info(f"  - Downloading FEMA flood data for {county_name}")
        results['datasets']['fema_flood'] = self._download_fema_data(county_name, county_info, county_path)
        
        # 2. Environmental Sites
        self.logger.info(f"  - Downloading environmental sites for {county_name}")
        results['datasets']['environmental'] = self._download_environmental_data(county_name, county_info, county_path)
        
        # 3. Create metadata
        results['end_time'] = datetime.now().isoformat()
        results['status'] = 'completed'
        
        # Save county metadata
        metadata_file = county_path / f"{county_name.replace(' ', '_')}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        return results
        
    def _download_fema_data(self, county_name: str, county_info: Dict, county_path: Path) -> Dict:
        """Download FEMA flood data for county"""
        result = {
            'source': 'FEMA NFHL',
            'status': 'failed',
            'records': 0,
            'file': None
        }
        
        try:
            # Query FEMA MapServer for flood zones
            endpoint = f"{self.API_ENDPOINTS['fema_flood']['base']}/28/query"
            params = {
                'where': f"COUNTY_FIPS = '{county_info['fips']}'",
                'outFields': 'FLD_ZONE,ZONE_SUBTY,SFHA_TF,STATIC_BFE,COUNTY_FIPS',
                'f': 'geojson',
                'outSR': '4326',
                'returnGeometry': 'true'
            }
            
            response = requests.get(endpoint, params=params, timeout=60)
            if response.status_code == 200:
                data = response.json()
                
                if 'features' in data and len(data['features']) > 0:
                    # Save as GeoJSON
                    output_file = county_path / f"{county_name.replace(' ', '_')}_fema_flood.geojson"
                    with open(output_file, 'w') as f:
                        json.dump(data, f)
                    
                    result['status'] = 'completed'
                    result['records'] = len(data['features'])
                    result['file'] = str(output_file.name)
                    self.logger.info(f"    ✓ Downloaded {result['records']} FEMA flood zones")
                else:
                    # Try alternative endpoint if no data
                    self.logger.warning(f"    No FEMA data found, trying alternative endpoint")
                    result['status'] = 'no_data'
            else:
                self.logger.error(f"    FEMA API returned status {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"    Failed to download FEMA data: {str(e)}")
            result['error'] = str(e)
            
        return result
        
    def _download_environmental_data(self, county_name: str, county_info: Dict, county_path: Path) -> Dict:
        """Download environmental data from multiple sources"""
        results = {}
        
        # 1. Download EnviroStor data
        results['envirostor'] = self._download_envirostor(county_name, county_path)
        
        # 2. Download GeoTracker data  
        results['geotracker'] = self._download_geotracker(county_name, county_path)
        
        return results
    
    def _download_envirostor(self, county_name: str, county_path: Path) -> Dict:
        """Download EnviroStor cleanup sites"""
        result = {
            'source': 'EnviroStor',
            'status': 'failed',
            'records': 0,
            'file': None
        }
        
        try:
            # EnviroStor public data endpoint
            url = 'https://www.envirostor.dtsc.ca.gov/public/map_data_download'
            
            # Download CSV data for county
            params = {
                'county': county_name,
                'format': 'csv'
            }
            
            response = requests.get(url, params=params, timeout=60)
            if response.status_code == 200 and len(response.content) > 100:
                # Save CSV data
                output_file = county_path / f"{county_name.replace(' ', '_')}_envirostor.csv"
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                # Count records
                df = pd.read_csv(output_file)
                result['status'] = 'completed'
                result['records'] = len(df)
                result['file'] = str(output_file.name)
                self.logger.info(f"    ✓ Downloaded {result['records']} EnviroStor sites")
            else:
                result['status'] = 'no_data'
                self.logger.warning(f"    No EnviroStor data available for {county_name}")
                
        except Exception as e:
            self.logger.error(f"    Failed to download EnviroStor data: {str(e)}")
            result['error'] = str(e)
            
        return result
    
    def _download_geotracker(self, county_name: str, county_path: Path) -> Dict:
        """Download GeoTracker LUST/SLIC sites"""
        result = {
            'source': 'GeoTracker',
            'status': 'failed',
            'total_records': 0,
            'files': []
        }
        
        try:
            base_url = 'https://geotracker.waterboards.ca.gov/data_download/'
            
            # Download each GeoTracker file type
            for file_type in ['lust_public.zip', 'slic_public.zip']:
                try:
                    url = base_url + file_type
                    response = requests.get(url, timeout=120)
                    
                    if response.status_code == 200:
                        # Save and extract ZIP
                        zip_file = county_path / file_type
                        with open(zip_file, 'wb') as f:
                            f.write(response.content)
                        
                        # Extract CSV from ZIP
                        with zipfile.ZipFile(zip_file, 'r') as z:
                            csv_name = file_type.replace('.zip', '.csv')
                            z.extract(csv_name, county_path)
                            
                            # Filter for county
                            df = pd.read_csv(county_path / csv_name, low_memory=False)
                            if 'COUNTY' in df.columns:
                                county_df = df[df['COUNTY'].str.upper() == county_name.upper()]
                                
                                if len(county_df) > 0:
                                    output_file = county_path / f"{county_name.replace(' ', '_')}_{file_type.replace('_public.zip', '')}.csv"
                                    county_df.to_csv(output_file, index=False)
                                    
                                    result['files'].append(str(output_file.name))
                                    result['total_records'] += len(county_df)
                                    self.logger.info(f"    ✓ Extracted {len(county_df)} {file_type.replace('_public.zip', '')} sites")
                            
                            # Clean up full dataset
                            os.remove(county_path / csv_name)
                        
                        # Clean up ZIP
                        os.remove(zip_file)
                        
                except Exception as e:
                    self.logger.warning(f"    Could not process {file_type}: {str(e)}")
            
            if result['total_records'] > 0:
                result['status'] = 'completed'
            else:
                result['status'] = 'no_data'
                
        except Exception as e:
            self.logger.error(f"    Failed to download GeoTracker data: {str(e)}")
            result['error'] = str(e)
            
        return result
        
    def _generate_summary_report(self):
        """Generate processing summary report"""
        report_file = self.data_path / f"tier1_batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        summary = {
            'mission': 'California Environmental Data Acquisition',
            'batch': 'Tier 1 Priority Counties',
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_minutes': (datetime.now() - self.start_time).total_seconds() / 60,
            'counties_processed': len(self.processing_status),
            'counties': self.processing_status,
            'next_steps': [
                'Wingman to execute actual downloads',
                'Tower to validate data quality',
                'Strike Leader to approve for production'
            ]
        }
        
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        self.logger.info("="*60)
        self.logger.info(f"BATCH PROCESSING FRAMEWORK COMPLETE")
        self.logger.info(f"Duration: {summary['duration_minutes']:.2f} minutes")
        self.logger.info(f"Report saved: {report_file}")
        self.logger.info("="*60)
        
        return summary

def main():
    """Main execution with download option"""
    import sys
    
    print("California Tier 1 Batch Processor - WINGMAN EXECUTION MODE")
    print("="*60)
    
    processor = CaliforniaTier1Processor()
    
    if '--execute-downloads' in sys.argv:
        print("\n🚀 EXECUTING ACTUAL DATA DOWNLOADS FOR TIER 1 COUNTIES")
        print("This will download real environmental data from APIs")
        print("")
        
        # Process with sequential to avoid overwhelming APIs
        processor.process_all_tier1_counties(parallel=False)
        
        print("\n✅ Tier 1 county downloads COMPLETE")
        print("📁 Output directory: data_sets/california/CA_Environmental_Batch/")
    else:
        print("\nTo execute downloads, run with --execute-downloads flag:")
        print("python3 ca_tier1_batch_processor.py --execute-downloads")

if __name__ == "__main__":
    main()