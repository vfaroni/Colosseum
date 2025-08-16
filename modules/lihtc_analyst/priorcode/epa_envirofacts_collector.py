#!/usr/bin/env python3
"""
EPA Envirofacts API Collector
Comprehensive collection system for EPA's 20+ integrated environmental databases

Status: Production Ready
Author: Structured Consultants LLC
Date: July 23, 2025
"""

import os
import json
import requests
import pandas as pd
import geopandas as gpd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import logging
import time
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

class EPAEnvirofactsCollector:
    """Collector for EPA Envirofacts Data Warehouse"""
    
    # EPA Envirofacts database systems
    EPA_SYSTEMS = {
        'rcrainfo': {
            'name': 'Resource Conservation and Recovery Act Information',
            'table': 'RCR_SITES',  
            'description': 'Hazardous waste handlers and facilities',
            'key_fields': ['HANDLER_ID', 'FACILITY_NAME', 'LONGITUDE83', 'LATITUDE83', 'STATE_CODE'],
            'lihtc_relevance': 'Critical for hazardous waste facility proximity analysis'
        },
        'tri': {
            'name': 'Toxic Release Inventory',
            'table': 'TRI_FACILITY',
            'description': 'Chemical releases from industrial facilities',
            'key_fields': ['TRI_FACILITY_ID', 'FACILITY_NAME', 'LONGITUDE', 'LATITUDE', 'STATE_ABBR'],
            'lihtc_relevance': 'Toxic chemical release screening within 1/4 mile radius'
        },
        'npdes': {
            'name': 'National Pollutant Discharge Elimination System',
            'table': 'NPDES_FACILITIES',
            'description': 'Water discharge permits and facilities',
            'key_fields': ['NPDES_ID', 'FACILITY_NAME', 'LONGITUDE', 'LATITUDE', 'STATE_CODE'],
            'lihtc_relevance': 'Water pollution source identification'
        },
        'sdwis': {
            'name': 'Safe Drinking Water Information System',
            'table': 'WATER_SYSTEM',
            'description': 'Public water system violations and monitoring',
            'key_fields': ['PWSID', 'PWS_NAME', 'STATE_CODE'],
            'lihtc_relevance': 'Drinking water quality assessment'
        },
        'icis_air': {
            'name': 'Integrated Compliance Information System - Air',
            'table': 'ICIS_AIR_FACILITIES',
            'description': 'Air quality permits and violations',
            'key_fields': ['FACILITY_ID', 'FACILITY_NAME', 'LONGITUDE', 'LATITUDE', 'STATE_CODE'],
            'lihtc_relevance': 'Air quality violation screening'
        },
        'superfund': {
            'name': 'Superfund Enterprise Management System',
            'table': 'SEMS_SITES',
            'description': 'NPL sites and CERCLIS locations',
            'key_fields': ['SITE_ID', 'SITE_NAME', 'LONGITUDE', 'LATITUDE', 'STATE_CODE', 'NPL_STATUS'],
            'lihtc_relevance': 'Critical 1-mile Superfund proximity screening'
        },
        'brownfields': {
            'name': 'Brownfields Management System',
            'table': 'BROWNFIELDS_SITES',
            'description': 'Brownfields assessment and cleanup grants',
            'key_fields': ['GRANT_ID', 'GRANTEE_NAME', 'STATE_CODE'],
            'lihtc_relevance': 'Brownfields redevelopment opportunity identification'
        }
    }
    
    def __init__(self, base_data_path: str, state_filter: Optional[List[str]] = None):
        self.base_data_path = Path(base_data_path)
        self.state_filter = state_filter or ['CA', 'TX', 'AZ', 'NM', 'HI']  # LIHTC focus states
        self.base_url = 'https://data.epa.gov/efservice/'
        self.setup_logging()
        
        # Create storage directories
        self.storage_path = self.base_data_path / "federal" / "epa_envirofacts"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def setup_logging(self):
        """Setup logging for EPA collection"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def build_api_url(self, system: str, table: str, state_code: Optional[str] = None, 
                     fields: Optional[List[str]] = None, output_format: str = 'JSON') -> str:
        """Build EPA Envirofacts API URL"""
        
        # Base URL structure: /efservice/{system}/{table}/{search_criteria}/{output_format}
        url_parts = [self.base_url.rstrip('/'), system, table]
        
        # Add state filter if specified
        if state_code:
            url_parts.extend(['STATE_CODE', state_code])
        
        # Add field selection if specified
        if fields:
            url_parts.extend(['COLS', '~'.join(fields)])
        
        # Add output format
        url_parts.append(output_format)
        
        return '/'.join(url_parts)
    
    def collect_system_data(self, system_key: str, max_records: int = 50000) -> Dict:
        """Collect data from specific EPA system"""
        system_info = self.EPA_SYSTEMS[system_key]
        self.logger.info(f"Collecting {system_info['name']} data")
        
        all_data = []
        collection_metadata = {
            'system': system_key,
            'system_name': system_info['name'],
            'collection_time': datetime.now().isoformat(),
            'states_collected': [],
            'total_records': 0,
            'errors': []
        }
        
        # Collect data for each state
        for state_code in self.state_filter:
            try:
                self.logger.info(f"Collecting {system_key} data for {state_code}")
                
                # Build API URL
                api_url = self.build_api_url(
                    system=system_key.upper(),
                    table=system_info['table'],
                    state_code=state_code,
                    fields=system_info['key_fields']
                )
                
                self.logger.debug(f"API URL: {api_url}")
                
                # Make request with retry logic
                response = self._make_request_with_retry(api_url)
                
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Handle different EPA API response formats
                        if isinstance(data, list):
                            records = data
                        elif isinstance(data, dict):
                            # Some APIs return data nested in results
                            records = data.get('Results', data.get('data', [data]))
                        else:
                            records = []
                        
                        if records:
                            # Add state code and system identifier to records
                            for record in records:
                                if isinstance(record, dict):
                                    record['EPA_SYSTEM'] = system_key
                                    record['STATE_FILTER'] = state_code
                            
                            all_data.extend(records)
                            collection_metadata['states_collected'].append(state_code)
                            self.logger.info(f"Collected {len(records)} records for {state_code}")
                        else:
                            self.logger.warning(f"No records found for {system_key} in {state_code}")
                            
                    except json.JSONDecodeError as e:
                        error_msg = f"JSON decode error for {state_code}: {str(e)}"
                        self.logger.error(error_msg)
                        collection_metadata['errors'].append(error_msg)
                        
                else:
                    error_msg = f"API request failed for {state_code}: {response.status_code if response else 'No response'}"
                    self.logger.error(error_msg)
                    collection_metadata['errors'].append(error_msg)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                error_msg = f"Error collecting {system_key} data for {state_code}: {str(e)}"
                self.logger.error(error_msg)
                collection_metadata['errors'].append(error_msg)
        
        collection_metadata['total_records'] = len(all_data)
        
        # Save data if collected
        if all_data:
            self._save_system_data(system_key, all_data, collection_metadata)
        
        return {
            'system': system_key,
            'records_collected': len(all_data),
            'metadata': collection_metadata
        }
    
    def _make_request_with_retry(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    timeout=60,
                    headers={
                        'User-Agent': 'LIHTC-Environmental-Analysis/1.0 (Structured Consultants LLC)',
                        'Accept': 'application/json'
                    }
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Rate limited, waiting {wait_time} seconds")
                    time.sleep(wait_time)
                else:
                    self.logger.warning(f"HTTP {response.status_code} on attempt {attempt + 1}")
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request exception on attempt {attempt + 1}: {str(e)}")
                
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        
        return None
    
    def _save_system_data(self, system_key: str, data: List[Dict], metadata: Dict):
        """Save collected system data with multiple formats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create system directory
        system_dir = self.storage_path / system_key
        system_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        json_file = system_dir / f"{system_key}_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        # Save as CSV for easier analysis
        try:
            df = pd.DataFrame(data)
            csv_file = system_dir / f"{system_key}_{timestamp}.csv"
            df.to_csv(csv_file, index=False)
            
            # Create GeoJSON if coordinate data exists
            coord_columns = ['LONGITUDE', 'LONGITUDE83', 'LATITUDE', 'LATITUDE83']
            available_coords = [col for col in coord_columns if col in df.columns]
            
            if len(available_coords) >= 2:
                # Use first available longitude and latitude columns
                lon_col = [col for col in available_coords if 'LON' in col][0]
                lat_col = [col for col in available_coords if 'LAT' in col][0]
                
                # Filter records with valid coordinates
                geo_df = df.dropna(subset=[lon_col, lat_col])
                geo_df = geo_df[(geo_df[lon_col] != 0) & (geo_df[lat_col] != 0)]
                
                if not geo_df.empty:
                    gdf = gpd.GeoDataFrame(
                        geo_df,
                        geometry=gpd.points_from_xy(geo_df[lon_col], geo_df[lat_col]),
                        crs='EPSG:4326'
                    )
                    
                    geojson_file = system_dir / f"{system_key}_{timestamp}.geojson"
                    gdf.to_file(geojson_file, driver='GeoJSON')
                    
                    self.logger.info(f"Created GeoJSON with {len(gdf)} georeferenced records")
            
        except Exception as e:
            self.logger.error(f"Error creating additional formats: {str(e)}")
        
        # Save metadata
        metadata_file = system_dir / f"{system_key}_{timestamp}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        self.logger.info(f"Saved {len(data)} records for {system_key}")
    
    def create_comprehensive_metadata(self, collection_results: List[Dict]) -> str:
        """Create comprehensive metadata for all collected EPA data"""
        
        total_records = sum(result['records_collected'] for result in collection_results)
        successful_systems = [r for r in collection_results if r['records_collected'] > 0]
        failed_systems = [r for r in collection_results if r['records_collected'] == 0]
        
        metadata = {
            "dataset_name": "EPA Envirofacts Comprehensive Collection",
            "source_url": "https://data.epa.gov/efservice/",
            "source_organization": "U.S. Environmental Protection Agency",
            "acquisition_date": datetime.now().isoformat(),
            "collection_scope": {
                "systems_attempted": len(collection_results),
                "systems_successful": len(successful_systems),
                "systems_failed": len(failed_systems),
                "states_covered": self.state_filter,
                "total_records": total_records
            },
            "system_details": {
                result['system']: {
                    "records_collected": result['records_collected'],
                    "system_name": self.EPA_SYSTEMS[result['system']]['name'],
                    "lihtc_relevance": self.EPA_SYSTEMS[result['system']]['lihtc_relevance']
                }
                for result in collection_results
            },
            "coordinate_system": "WGS84 (EPSG:4326)",
            "update_frequency": "Weekly to monthly by system",
            "api_endpoint": self.base_url,
            "authentication_required": False,
            "rate_limits": "1 request per second implemented",
            "lihtc_usage_notes": [
                "Primary screening for contaminated sites within 1/4 mile radius",
                "Superfund sites require 1-mile buffer analysis", 
                "Coordinate data available for mapping and distance calculations",
                "Cross-reference with state databases for comprehensive coverage"
            ],
            "data_quality_notes": [
                "Some records may have missing coordinate data",
                "State filtering applied for LIHTC focus regions",
                "Multiple output formats provided (JSON, CSV, GeoJSON)"
            ]
        }
        
        # Save comprehensive metadata
        metadata_file = self.storage_path / f"epa_envirofacts_comprehensive_metadata_{datetime.now().strftime('%Y%m%d')}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        # Create markdown summary
        summary = f"""# EPA Envirofacts Comprehensive Collection

**Collection Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Records**: {total_records:,}
**Systems Collected**: {len(successful_systems)}/{len(collection_results)}
**States Covered**: {', '.join(self.state_filter)}

## System Collection Results

"""
        
        for result in collection_results:
            system_info = self.EPA_SYSTEMS[result['system']]
            summary += f"### {system_info['name']}\n"
            summary += f"- **Records**: {result['records_collected']:,}\n"
            summary += f"- **LIHTC Relevance**: {system_info['lihtc_relevance']}\n"
            summary += f"- **Status**: {'✅ Success' if result['records_collected'] > 0 else '❌ Failed'}\n\n"
        
        summary += f"""## LIHTC Usage Guidelines

1. **Proximity Analysis**: Use coordinate data for buffer analysis around properties
2. **Risk Assessment**: Prioritize Superfund (1-mile) and hazardous waste sites (1/4 mile)
3. **Due Diligence**: Cross-reference with state environmental databases
4. **Reporting**: Include EPA system names and data collection dates in reports

## Data Formats Available
- **JSON**: Raw API response data with all fields
- **CSV**: Tabular format for spreadsheet analysis  
- **GeoJSON**: Geospatial format for mapping applications

## Next Steps
- Integrate with California EnviroStor and GeoTracker data
- Implement automated proximity analysis for LIHTC properties
- Setup scheduled updates based on EPA data refresh cycles
"""
        
        summary_file = self.storage_path / f"epa_envirofacts_collection_summary_{datetime.now().strftime('%Y%m%d')}.md"
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        return str(metadata_file)
    
    def collect_all_systems(self, priority_systems: Optional[List[str]] = None) -> List[Dict]:
        """Collect data from all EPA systems"""
        
        systems_to_collect = priority_systems or [
            'superfund',  # Highest priority - 1-mile buffer requirement
            'rcrainfo',   # High priority - hazardous waste facilities
            'tri',        # High priority - toxic releases
            'npdes',      # Medium priority - water permits
            'icis_air',   # Medium priority - air permits
            'brownfields' # Low priority - redevelopment opportunities
        ]
        
        self.logger.info(f"Starting EPA Envirofacts collection for {len(systems_to_collect)} systems")
        
        collection_results = []
        
        for system_key in systems_to_collect:
            if system_key in self.EPA_SYSTEMS:
                result = self.collect_system_data(system_key)
                collection_results.append(result)
                
                # Progress update
                self.logger.info(f"Completed {system_key}: {result['records_collected']} records")
                
                # Rate limiting between systems
                time.sleep(2)
            else:
                self.logger.warning(f"Unknown system: {system_key}")
        
        # Create comprehensive metadata
        self.create_comprehensive_metadata(collection_results)
        
        self.logger.info(f"EPA Envirofacts collection complete: {len(collection_results)} systems processed")
        
        return collection_results

def main():
    """Main execution function for testing"""
    # Initialize collector for LIHTC focus states
    collector = EPAEnvirofactsCollector(
        base_data_path="/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets",
        state_filter=['CA', 'TX', 'AZ']  # Start with 3 states for testing
    )
    
    print("EPA Envirofacts Collector")
    print("=" * 40)
    print(f"Focus States: {', '.join(collector.state_filter)}")
    print(f"Storage Path: {collector.storage_path}")
    print()
    
    # Show available systems
    print("Available EPA Systems:")
    for key, info in collector.EPA_SYSTEMS.items():
        print(f"  {key:12} | {info['name']}")
    
    print()
    print("Ready for data collection!")
    print("To collect priority systems: collector.collect_all_systems(['superfund', 'rcrainfo', 'tri'])")

if __name__ == "__main__":
    main()