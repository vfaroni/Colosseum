#!/usr/bin/env python3
"""
Real California Transportation Data Downloader
Colosseum Infrastructure - Actual data.ca.gov integration

Downloads real transportation datasets from California's open data portal.
"""

import requests
import pandas as pd
import geopandas as gpd
import json
import time
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class RealCaliforniaDataDownloader:
    """Downloads real transportation datasets from data.ca.gov"""
    
    def __init__(self):
        self.base_url = "https://data.ca.gov"
        self.api_base = "https://data.ca.gov/api/3/action"
        self.data_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/california/CA_Transportation")
        
        # Real dataset identifiers from data.ca.gov
        self.real_datasets = {
            'california_transit_stops': {
                'package_id': 'california-transit-stops',
                'name': 'California Transit Stops',
                'description': 'Compiled GTFS schedule data in geospatial format',
                'priority': 1,
                'use_case': 'Enhanced transit analysis'
            },
            'high_quality_transit_areas': {
                'package_id': 'high-quality-transit-areas-hqtas',
                'name': 'High Quality Transit Areas',
                'description': 'Identifies transit corridors with frequent service',
                'priority': 1,
                'use_case': 'LIHTC transit proximity scoring'
            },
            'california_airports': {
                'package_id': 'california-airports',
                'name': 'California Airports',
                'description': 'Public and private airport locations',
                'priority': 2,
                'use_case': 'Infrastructure proximity analysis'
            },
            'california_freight_networks': {
                'package_id': 'california-freight-networks',
                'name': 'California Freight Networks', 
                'description': 'Freight transportation infrastructure',
                'priority': 2,
                'use_case': 'Economic development context'
            }
        }
        
        print(f"🌐 REAL CALIFORNIA DATA DOWNLOADER INITIALIZED")
        print(f"📡 API Base: {self.api_base}")
        print(f"📁 Data storage: {self.data_dir}")
    
    def search_package_info(self, package_id):
        """Get package information from data.ca.gov API"""
        url = f"{self.api_base}/package_show"
        params = {'id': package_id}
        
        try:
            print(f"📡 Fetching package info: {package_id}")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data['result']
                else:
                    print(f"❌ API returned success=false for {package_id}")
            else:
                print(f"❌ HTTP {response.status_code} for {package_id}")
                
        except Exception as e:
            print(f"❌ Error fetching {package_id}: {e}")
        
        return None
    
    def download_resource(self, resource, dataset_dir, dataset_name):
        """Download a specific resource file"""
        download_url = resource.get('url')
        filename = resource.get('name', 'unknown_file')
        format_type = resource.get('format', 'unknown').lower()
        
        if not download_url:
            print(f"⚠️ No download URL for resource: {filename}")
            return None
        
        try:
            print(f"📥 Downloading: {filename} ({format_type})")
            
            response = requests.get(download_url, timeout=60, stream=True)
            
            if response.status_code == 200:
                # Clean filename for filesystem
                safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                if not safe_filename.endswith(f'.{format_type}'):
                    safe_filename += f'.{format_type}'
                
                file_path = dataset_dir / safe_filename
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = file_path.stat().st_size
                print(f"✅ Downloaded: {safe_filename} ({file_size:,} bytes)")
                
                return {
                    'filename': safe_filename,
                    'file_path': str(file_path),
                    'file_size': file_size,
                    'format': format_type,
                    'download_url': download_url,
                    'success': True
                }
            else:
                print(f"❌ Download failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Download error: {e}")
        
        return None
    
    def generate_real_metadata(self, dataset_config, package_info, downloaded_files, acquisition_time):
        """Generate metadata from real data.ca.gov package information"""
        
        if not package_info:
            return "# Dataset Metadata\nError: Could not fetch package information"
        
        # Extract package information
        title = package_info.get('title', dataset_config['name'])
        description = package_info.get('notes', dataset_config['description'])
        organization = package_info.get('organization', {}).get('title', 'State of California')
        last_updated = package_info.get('metadata_modified', 'Unknown')
        created = package_info.get('metadata_created', 'Unknown')
        update_frequency = package_info.get('update_frequency', 'Unknown')
        license_title = package_info.get('license_title', 'Unknown')
        
        # File information
        file_info = ""
        if downloaded_files:
            file_info += "### Downloaded Files\n"
            for file_data in downloaded_files:
                file_info += f"- **{file_data['filename']}**: {file_data['format'].upper()} ({file_data['file_size']:,} bytes)\n"
        
        metadata = f"""# {title}
## Dataset Metadata

### Source Information
**Dataset Name**: {title}
**Source Organization**: {organization}
**Source URL**: https://data.ca.gov/dataset/{package_info.get('name', 'unknown')}
**Package ID**: {package_info.get('name', 'unknown')}
**License**: {license_title}

### Acquisition Details
**Acquisition Date**: {acquisition_time.strftime('%Y-%m-%d %H:%M:%S %Z')}
**Acquired By**: Colosseum Real California Data Downloader
**Total Files Downloaded**: {len(downloaded_files) if downloaded_files else 0}

{file_info}

### Dataset Timeline
**Dataset Created**: {created}
**Dataset Last Updated**: {last_updated}
**Update Frequency**: {update_frequency}

### Update Monitoring
**Update Check URL**: https://data.ca.gov/dataset/{package_info.get('name', 'unknown')}
**Package ID for API**: {package_info.get('name', 'unknown')}
**Next Scheduled Check**: {(acquisition_time.replace(day=1) + pd.DateOffset(months=1)).strftime('%Y-%m-%d')}
**Update Responsibility**: Real California Data Downloader

### Technical Specifications
**Geographic Coverage**: California Statewide
**Tags**: {', '.join([tag['name'] for tag in package_info.get('tags', [])])}
**Resources Available**: {len(package_info.get('resources', []))}

### Quality Assessment
**Source Validation**: Official California government data portal
**Data Authority**: State of California
**Fitness for LIHTC Analysis**: {dataset_config['use_case']}

### Usage Notes
**Primary Use Cases**: {dataset_config['use_case']}
**Integration Requirements**: Integration with existing CA transit data
**Dataset Description**: {description}

### Resources Information
"""
        
        # Add resource details
        resources = package_info.get('resources', [])
        for i, resource in enumerate(resources, 1):
            metadata += f"""
**Resource {i}**: {resource.get('name', 'Unnamed')}
- Format: {resource.get('format', 'Unknown')}
- Size: {resource.get('size', 'Unknown')}
- Last Modified: {resource.get('last_modified', 'Unknown')}
- URL: {resource.get('url', 'No URL')}
"""
        
        metadata += f"""
---
*Metadata generated from live data.ca.gov API*  
*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*Standards Version: DATASET_ACQUISITION_STANDARDS.md v1.0*
"""
        
        return metadata
    
    def download_real_dataset(self, dataset_key, dataset_config):
        """Download a real dataset with all resources"""
        print(f"\n📥 ACQUIRING: {dataset_config['name']}")
        print(f"🎯 Use case: {dataset_config['use_case']}")
        
        # Create dataset directory
        dataset_dir = self.data_dir / dataset_key
        dataset_dir.mkdir(exist_ok=True)
        
        acquisition_start = datetime.now()
        
        # Get package information from API
        package_info = self.search_package_info(dataset_config['package_id'])
        
        if not package_info:
            print(f"❌ Could not fetch package info for {dataset_config['package_id']}")
            return False
        
        print(f"✅ Package found: {package_info.get('title', 'Unknown')}")
        print(f"📊 Resources available: {len(package_info.get('resources', []))}")
        
        # Download all available resources
        downloaded_files = []
        resources = package_info.get('resources', [])
        
        for resource in resources[:3]:  # Limit to first 3 resources to avoid overwhelming
            download_result = self.download_resource(resource, dataset_dir, dataset_config['name'])
            if download_result:
                downloaded_files.append(download_result)
            
            # Rate limiting
            time.sleep(1)
        
        # Generate metadata
        metadata_content = self.generate_real_metadata(
            dataset_config, package_info, downloaded_files, acquisition_start
        )
        
        metadata_file = dataset_dir / "DATASET_METADATA.md"
        with open(metadata_file, 'w') as f:
            f.write(metadata_content)
        
        print(f"📋 Metadata saved: {metadata_file.name}")
        print(f"✅ Successfully downloaded {len(downloaded_files)} files")
        
        return True
    
    def download_all_real_datasets(self):
        """Download all real datasets from data.ca.gov"""
        print("🌐 REAL CALIFORNIA TRANSPORTATION DATA ACQUISITION")
        print("=" * 80)
        
        mission_start = datetime.now()
        success_count = 0
        
        # Sort by priority
        sorted_datasets = sorted(
            self.real_datasets.items(),
            key=lambda x: x[1]['priority']
        )
        
        for dataset_key, dataset_config in sorted_datasets:
            print(f"\n🎯 PRIORITY {dataset_config['priority']}")
            
            success = self.download_real_dataset(dataset_key, dataset_config)
            if success:
                success_count += 1
            
            # Rate limiting between datasets
            time.sleep(3)
        
        mission_duration = datetime.now() - mission_start
        
        print(f"\n" + "=" * 80)
        print(f"🎯 REAL DATA MISSION COMPLETE")
        print(f"📊 Success Rate: {success_count}/{len(self.real_datasets)} ({success_count/len(self.real_datasets)*100:.1f}%)")
        print(f"⏱️ Duration: {mission_duration}")
        
        return success_count, len(self.real_datasets)

if __name__ == "__main__":
    downloader = RealCaliforniaDataDownloader()
    success, total = downloader.download_all_real_datasets()
    
    print(f"\n✅ Real California data acquisition complete!")
    print(f"📁 Data stored in: {downloader.data_dir}")
    print(f"📋 Check metadata files for complete dataset information")