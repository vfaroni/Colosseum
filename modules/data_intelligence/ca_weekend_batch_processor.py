#!/usr/bin/env python3
"""
California Tier 2-4 Counties Weekend Batch Processor
Strategic coordination by Strike Leader for automated weekend execution
Mission: Complete environmental data acquisition for remaining 14 counties

Counties covered:
- Tier 2: Riverside, San Bernardino, Sacramento, Contra Costa, Santa Clara
- Tier 3: Ventura, San Joaquin, Fresno, Kern, San Mateo
- Tier 4: Stanislaus, Sonoma, Marin, Monterey

Date: 2025-08-09
"""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import requests
import pandas as pd
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

class CaliforniaWeekendBatchProcessor:
    """Weekend batch processor for remaining California counties"""
    
    # Tier 2-4 Counties (Remaining from 19-county empire)
    WEEKEND_COUNTIES = {
        # Tier 2 - Major Markets
        'Riverside': {
            'fips': '06065',
            'tier': 2,
            'parcels': 766000,
            'priority': 6
        },
        'San Bernardino': {
            'fips': '06071', 
            'tier': 2,
            'parcels': 753000,
            'priority': 7
        },
        'Sacramento': {
            'fips': '06067',
            'tier': 2,
            'parcels': 460000,
            'priority': 8
        },
        'Contra Costa': {
            'fips': '06013',
            'tier': 2,
            'parcels': 437000,
            'priority': 9
        },
        'Santa Clara': {
            'fips': '06085',
            'tier': 2,
            'parcels': 415000,
            'priority': 10
        },
        # Tier 3 - Secondary Markets
        'Ventura': {
            'fips': '06111',
            'tier': 3,
            'parcels': 305000,
            'priority': 11
        },
        'San Joaquin': {
            'fips': '06077',
            'tier': 3,
            'parcels': 260000,
            'priority': 12
        },
        'Fresno': {
            'fips': '06019',
            'tier': 3,
            'parcels': 339000,
            'priority': 13
        },
        'Kern': {
            'fips': '06029',
            'tier': 3,
            'parcels': 344000,
            'priority': 14
        },
        'San Mateo': {
            'fips': '06081',
            'tier': 3,
            'parcels': 247000,
            'priority': 15
        },
        # Tier 4 - Emerging Markets
        'Stanislaus': {
            'fips': '06099',
            'tier': 4,
            'parcels': 188000,
            'priority': 16
        },
        'Sonoma': {
            'fips': '06097',
            'tier': 4,
            'parcels': 214000,
            'priority': 17
        },
        'Marin': {
            'fips': '06041',
            'tier': 4,
            'parcels': 108000,
            'priority': 18
        },
        'Monterey': {
            'fips': '06053',
            'tier': 4,
            'parcels': 149000,
            'priority': 19
        }
    }
    
    # Enhanced API endpoints with weekend-specific optimizations
    API_ENDPOINTS = {
        'fema_flood': {
            'base': 'https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer',
            'layer': 28,
            'batch_size': 5000
        },
        'envirostor': {
            'base': 'https://www.envirostor.dtsc.ca.gov/public/map_data_download',
            'format': 'csv'
        },
        'geotracker': {
            'base': 'https://geotracker.waterboards.ca.gov/data_download/',
            'files': ['lust_public.zip', 'slic_public.zip', 'military_public.zip']
        },
        'epa_superfund': {
            'base': 'https://www.epa.gov/superfund/superfund-data-and-reports',
            'california_filter': 'STATE = CA'
        }
    }
    
    def __init__(self, base_path: str = None):
        """Initialize weekend batch processor"""
        self.base_path = Path(base_path or "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.data_path = self.base_path / "data_sets" / "california" / "CA_Environmental_Batch"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging for weekend runs
        self.setup_logging()
        
        # Track processing
        self.start_time = datetime.now()
        self.processing_status = {}
        
    def setup_logging(self):
        """Configure logging for weekend batch"""
        log_file = self.data_path / f"weekend_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def process_all_weekend_counties(self, tier: Optional[int] = None):
        """Process all or specific tier counties"""
        self.logger.info("="*60)
        self.logger.info("CALIFORNIA WEEKEND BATCH PROCESSOR - STRIKE LEADER COORDINATION")
        self.logger.info(f"Start Time: {self.start_time}")
        self.logger.info("="*60)
        
        # Filter by tier if specified
        counties_to_process = {
            name: info for name, info in self.WEEKEND_COUNTIES.items()
            if tier is None or info['tier'] == tier
        }
        
        self.logger.info(f"Processing {len(counties_to_process)} counties")
        
        # Process counties by tier for organization
        for current_tier in [2, 3, 4]:
            tier_counties = {
                name: info for name, info in counties_to_process.items()
                if info['tier'] == current_tier
            }
            
            if tier_counties:
                self.logger.info(f"\n{'='*40}")
                self.logger.info(f"PROCESSING TIER {current_tier} COUNTIES")
                self.logger.info(f"{'='*40}")
                
                for county_name, county_info in tier_counties.items():
                    self._process_county(county_name, county_info)
                    
                    # Add delay between counties to avoid API overwhelm
                    time.sleep(30)
        
        # Generate summary report
        self._generate_weekend_summary()
        
    def _process_county(self, county_name: str, county_info: Dict):
        """Process single county with all data sources"""
        self.logger.info(f"\nProcessing {county_name} County (Tier {county_info['tier']})")
        self.logger.info(f"  FIPS: {county_info['fips']}")
        self.logger.info(f"  Parcels: {county_info['parcels']:,}")
        
        # Create county directory
        county_path = self.data_path / county_name.replace(' ', '_')
        county_path.mkdir(exist_ok=True)
        
        results = {
            'county': county_name,
            'fips': county_info['fips'],
            'tier': county_info['tier'],
            'start_time': datetime.now().isoformat(),
            'datasets': {}
        }
        
        # Download each data type
        try:
            # 1. FEMA Flood Data
            self.logger.info(f"  - Downloading FEMA flood data...")
            results['datasets']['fema_flood'] = self._download_fema_data(
                county_name, county_info, county_path
            )
            
            # 2. EnviroStor Data
            self.logger.info(f"  - Downloading EnviroStor data...")
            results['datasets']['envirostor'] = self._download_envirostor(
                county_name, county_path
            )
            
            # 3. GeoTracker Data
            self.logger.info(f"  - Downloading GeoTracker data...")
            results['datasets']['geotracker'] = self._download_geotracker(
                county_name, county_path
            )
            
            results['status'] = 'completed'
            
        except Exception as e:
            self.logger.error(f"  ERROR processing {county_name}: {str(e)}")
            results['status'] = 'failed'
            results['error'] = str(e)
        
        results['end_time'] = datetime.now().isoformat()
        
        # Save county metadata
        metadata_file = county_path / f"{county_name.replace(' ', '_')}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Create README.txt per CLAUDE.md requirements
        self._create_county_readme(county_name, county_path, results)
        
        self.processing_status[county_name] = results
        
        return results
    
    def _download_fema_data(self, county_name: str, county_info: Dict, county_path: Path) -> Dict:
        """Download FEMA flood data"""
        result = {
            'source': 'FEMA NFHL',
            'status': 'failed',
            'records': 0,
            'file': None
        }
        
        try:
            endpoint = f"{self.API_ENDPOINTS['fema_flood']['base']}/{self.API_ENDPOINTS['fema_flood']['layer']}/query"
            params = {
                'where': f"COUNTY_FIPS = '{county_info['fips']}'",
                'outFields': 'FLD_ZONE,ZONE_SUBTY,SFHA_TF,STATIC_BFE,COUNTY_FIPS',
                'f': 'geojson',
                'outSR': '4326',
                'returnGeometry': 'true'
            }
            
            response = requests.get(endpoint, params=params, timeout=120)
            if response.status_code == 200:
                data = response.json()
                
                if 'features' in data and len(data['features']) > 0:
                    output_file = county_path / f"{county_name.replace(' ', '_')}_fema_flood.geojson"
                    with open(output_file, 'w') as f:
                        json.dump(data, f)
                    
                    result['status'] = 'completed'
                    result['records'] = len(data['features'])
                    result['file'] = str(output_file.name)
                    self.logger.info(f"    ✓ Downloaded {result['records']} FEMA flood zones")
                else:
                    result['status'] = 'no_data'
                    self.logger.warning(f"    No FEMA data found for {county_name}")
                    
        except Exception as e:
            self.logger.error(f"    Failed to download FEMA data: {str(e)}")
            result['error'] = str(e)
            
        return result
    
    def _download_envirostor(self, county_name: str, county_path: Path) -> Dict:
        """Download EnviroStor cleanup sites"""
        result = {
            'source': 'EnviroStor',
            'status': 'failed',
            'records': 0,
            'file': None
        }
        
        try:
            url = self.API_ENDPOINTS['envirostor']['base']
            params = {
                'county': county_name,
                'format': 'csv'
            }
            
            response = requests.get(url, params=params, timeout=120)
            if response.status_code == 200 and len(response.content) > 100:
                output_file = county_path / f"{county_name.replace(' ', '_')}_envirostor.csv"
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                df = pd.read_csv(output_file)
                result['status'] = 'completed'
                result['records'] = len(df)
                result['file'] = str(output_file.name)
                self.logger.info(f"    ✓ Downloaded {result['records']} EnviroStor sites")
            else:
                result['status'] = 'no_data'
                
        except Exception as e:
            self.logger.error(f"    Failed to download EnviroStor data: {str(e)}")
            result['error'] = str(e)
            
        return result
    
    def _download_geotracker(self, county_name: str, county_path: Path) -> Dict:
        """Download GeoTracker contamination data"""
        result = {
            'source': 'GeoTracker',
            'status': 'failed',
            'total_records': 0,
            'files': []
        }
        
        try:
            base_url = self.API_ENDPOINTS['geotracker']['base']
            
            for file_type in self.API_ENDPOINTS['geotracker']['files']:
                try:
                    url = base_url + file_type
                    response = requests.get(url, timeout=180)
                    
                    if response.status_code == 200:
                        zip_file = county_path / file_type
                        with open(zip_file, 'wb') as f:
                            f.write(response.content)
                        
                        with zipfile.ZipFile(zip_file, 'r') as z:
                            csv_name = file_type.replace('.zip', '.csv')
                            z.extract(csv_name, county_path)
                            
                            df = pd.read_csv(county_path / csv_name, low_memory=False)
                            if 'COUNTY' in df.columns:
                                county_df = df[df['COUNTY'].str.upper() == county_name.upper()]
                                
                                if len(county_df) > 0:
                                    output_file = county_path / f"{county_name.replace(' ', '_')}_{file_type.replace('_public.zip', '')}.csv"
                                    county_df.to_csv(output_file, index=False)
                                    
                                    result['files'].append(str(output_file.name))
                                    result['total_records'] += len(county_df)
                                    self.logger.info(f"    ✓ Extracted {len(county_df)} {file_type.replace('_public.zip', '')} sites")
                            
                            os.remove(county_path / csv_name)
                        
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
    
    def _create_county_readme(self, county_name: str, county_path: Path, results: Dict):
        """Create README.txt per CLAUDE.md requirements"""
        readme_content = f"""DATASET: California Environmental Sites - {county_name} County
SOURCE: FEMA NFHL, CA EnviroStor, CA GeoTracker
SOURCE DATE: 2025-08-09
DOWNLOAD DATE: {datetime.now().strftime('%Y-%m-%d')}
DESCRIPTION: Comprehensive environmental contamination data for LIHTC site screening
FORMAT: CSV, GeoJSON
RECORDS: {self._count_total_records(results)}
COVERAGE: {county_name} County, California
UPDATE FREQUENCY: Quarterly (FEMA), Monthly (EnviroStor/GeoTracker)
NOTES: Weekend batch processing for Tier {results.get('tier', 'N/A')} county. Part of 19-county California environmental intelligence initiative.

FILE INVENTORY:"""
        
        # Add file inventory
        for dataset_name, dataset_info in results.get('datasets', {}).items():
            if isinstance(dataset_info, dict):
                if dataset_info.get('file'):
                    readme_content += f"\n- {dataset_info['file']} - {dataset_info.get('records', 0)} records"
                elif dataset_info.get('files'):
                    for file in dataset_info['files']:
                        readme_content += f"\n- {file}"
        
        readme_content += f"""

PROCESSING NOTES:
- Automated weekend batch processing via Colosseum platform
- County contains {self.WEEKEND_COUNTIES[county_name]['parcels']:,} parcels
- Priority level: {self.WEEKEND_COUNTIES[county_name]['priority']}
- Processing status: {results.get('status', 'unknown')}"""
        
        readme_file = county_path / "README.txt"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
            
    def _count_total_records(self, results: Dict) -> int:
        """Count total records across all datasets"""
        total = 0
        for dataset in results.get('datasets', {}).values():
            if isinstance(dataset, dict):
                total += dataset.get('records', 0)
                total += dataset.get('total_records', 0)
        return total
    
    def _generate_weekend_summary(self):
        """Generate weekend batch summary report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() / 60
        
        summary = {
            'mission': 'California Environmental Data Acquisition - Weekend Batch',
            'batch': 'Tier 2-4 Counties',
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_minutes': duration,
            'counties_processed': len(self.processing_status),
            'counties': self.processing_status,
            'statistics': {
                'successful': sum(1 for s in self.processing_status.values() if s.get('status') == 'completed'),
                'failed': sum(1 for s in self.processing_status.values() if s.get('status') == 'failed'),
                'no_data': sum(1 for s in self.processing_status.values() if s.get('status') == 'no_data'),
                'total_parcels': sum(self.WEEKEND_COUNTIES[c]['parcels'] for c in self.processing_status.keys())
            }
        }
        
        # Save summary
        summary_file = self.data_path / f"weekend_batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info("\n" + "="*60)
        self.logger.info("WEEKEND BATCH PROCESSING COMPLETE")
        self.logger.info(f"Duration: {duration:.2f} minutes")
        self.logger.info(f"Counties Processed: {summary['statistics']['successful']}/{len(self.processing_status)}")
        self.logger.info(f"Total Parcels Covered: {summary['statistics']['total_parcels']:,}")
        self.logger.info(f"Summary saved: {summary_file}")
        self.logger.info("="*60)
        
        return summary

def main():
    """Main execution for weekend batch"""
    import sys
    
    print("California Weekend Batch Processor - AUTOMATED EXECUTION")
    print("="*60)
    print("Processing Tier 2-4 Counties (14 total)")
    print("")
    
    processor = CaliforniaWeekendBatchProcessor()
    
    if '--tier' in sys.argv:
        # Process specific tier
        tier_idx = sys.argv.index('--tier') + 1
        tier = int(sys.argv[tier_idx])
        print(f"Processing Tier {tier} counties only")
        processor.process_all_weekend_counties(tier=tier)
    else:
        # Process all weekend counties
        print("Processing all Tier 2-4 counties")
        processor.process_all_weekend_counties()
    
    print("\n✅ Weekend batch processing COMPLETE")
    print("📁 Output: data_sets/california/CA_Environmental_Batch/")
    print("📊 Check weekend_batch_summary_*.json for detailed results")

if __name__ == "__main__":
    main()