#!/usr/bin/env python3
"""
California Financial Intelligence Downloader
Colosseum Infrastructure - State Controller's Office Data Acquisition

Acquires municipal financial datasets from California State Controller's Office
for LIHTC development intelligence and municipal health assessment.
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class CaliforniaFinancialIntelligenceDownloader:
    """Downloads financial intelligence datasets from California State Controller's Office"""
    
    def __init__(self):
        self.base_url = "https://data.ca.gov"
        self.api_base = "https://data.ca.gov/api/3/action"
        self.org_filter = "california-state-controllers-office"
        
        # Store in separate financial intelligence directory
        self.data_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/california/CA_Financial_Intelligence")
        
        # Priority financial datasets for LIHTC development
        self.priority_financial_datasets = {
            'property_tax_levies': {
                'search_terms': ['property tax', 'levies', 'tax levy'],
                'name': 'Property Tax Levies',
                'description': 'Historical property tax data 2002-2025',
                'priority': 1,
                'use_case': 'Property tax burden analysis and pro forma accuracy',
                'expected_years': '2002-2025'
            },
            'city_revenues_per_capita': {
                'search_terms': ['city revenues', 'per capita', 'municipal revenue'],
                'name': 'City Revenues Per Capita',
                'description': 'Municipal revenue analysis by city',
                'priority': 1,
                'use_case': 'Municipal financial health assessment',
                'analysis_type': 'revenue_trends'
            },
            'city_expenditures_per_capita': {
                'search_terms': ['city expenditures', 'per capita', 'municipal spending'],
                'name': 'City Expenditures Per Capita', 
                'description': 'Municipal spending patterns by city',
                'priority': 1,
                'use_case': 'Service delivery and infrastructure investment analysis',
                'analysis_type': 'spending_priorities'
            },
            'special_districts_listing': {
                'search_terms': ['special districts', 'districts listing', 'special district'],
                'name': 'Special Districts Listing',
                'description': 'Special district governance and location data',
                'priority': 2,
                'use_case': 'Hidden costs and special assessments identification',
                'governance_focus': 'development_fees'
            },
            'counties_raw_data': {
                'search_terms': ['counties raw data', 'county financial', 'county data'],
                'name': 'Counties Raw Data',
                'description': 'Comprehensive county financial data',
                'priority': 2, 
                'use_case': 'Regional economic context for development decisions',
                'scope': 'county_level'
            },
            'demographic_assumptions': {
                'search_terms': ['demographic assumption', 'demographic rates', 'population'],
                'name': 'Demographic Assumption Rates',
                'description': 'Population dynamics and demographic trends',
                'priority': 3,
                'use_case': 'Housing demand analysis and resident profile prediction',
                'focus': 'population_trends'
            }
        }
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"💰 CALIFORNIA FINANCIAL INTELLIGENCE DOWNLOADER INITIALIZED")
        print(f"🏛️ Source: California State Controller's Office")
        print(f"📁 Data storage: {self.data_dir}")
        print(f"🎯 Priority datasets: {len(self.priority_financial_datasets)}")
    
    def search_controller_datasets(self):
        """Search for all datasets from State Controller's Office"""
        url = f"{self.api_base}/package_search"
        
        params = {
            'q': '',  # Empty query to get all
            'fq': f'organization:{self.org_filter}',
            'sort': 'views_recent desc',
            'rows': 100  # Get up to 100 datasets
        }
        
        try:
            print(f"🔍 Searching State Controller's Office datasets...")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    packages = data['result']['results']
                    print(f"✅ Found {len(packages)} Controller datasets")
                    return packages
                else:
                    print("❌ API returned success=false")
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Search error: {e}")
        
        return []
    
    def match_dataset_to_priority(self, package, priority_datasets):
        """Match discovered package to our priority list"""
        package_title = package.get('title', '').lower()
        package_notes = package.get('notes', '').lower()
        
        for dataset_key, dataset_config in priority_datasets.items():
            search_terms = dataset_config['search_terms']
            
            # Check if any search terms match title or description
            for term in search_terms:
                if term.lower() in package_title or term.lower() in package_notes:
                    print(f"🎯 MATCH FOUND: {package.get('title')} → {dataset_config['name']}")
                    return dataset_key, dataset_config
        
        return None, None
    
    def download_financial_dataset(self, package, dataset_key, dataset_config):
        """Download financial dataset with comprehensive metadata"""
        print(f"\n💰 ACQUIRING: {dataset_config['name']}")
        print(f"📊 Package: {package.get('title')}")
        print(f"🎯 Use case: {dataset_config['use_case']}")
        
        # Create dataset directory
        dataset_dir = self.data_dir / dataset_key
        dataset_dir.mkdir(exist_ok=True)
        
        acquisition_start = datetime.now()
        
        # Download resources
        downloaded_files = []
        resources = package.get('resources', [])
        
        print(f"📁 Resources available: {len(resources)}")
        
        for i, resource in enumerate(resources[:5], 1):  # Limit to 5 resources
            download_result = self.download_resource(resource, dataset_dir, f"resource_{i}")
            if download_result:
                downloaded_files.append(download_result)
            
            time.sleep(1)  # Rate limiting
        
        # Generate financial intelligence metadata
        metadata_content = self.generate_financial_metadata(
            package, dataset_config, downloaded_files, acquisition_start
        )
        
        metadata_file = dataset_dir / "DATASET_METADATA.md"
        with open(metadata_file, 'w') as f:
            f.write(metadata_content)
        
        print(f"📋 Metadata saved: {metadata_file.name}")
        print(f"✅ Successfully downloaded {len(downloaded_files)} files")
        
        return len(downloaded_files) > 0
    
    def download_resource(self, resource, dataset_dir, prefix):
        """Download individual resource file"""
        download_url = resource.get('url')
        filename = resource.get('name', 'unknown_file')
        format_type = resource.get('format', 'unknown').lower()
        
        if not download_url:
            print(f"⚠️ No download URL for: {filename}")
            return None
        
        try:
            print(f"📥 Downloading: {filename} ({format_type})")
            
            response = requests.get(download_url, timeout=120, stream=True)
            
            if response.status_code == 200:
                # Clean filename
                safe_filename = f"{prefix}_{filename}".replace(' ', '_').replace('/', '_')
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
                    'original_name': filename
                }
            else:
                print(f"❌ Download failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Download error: {e}")
        
        return None
    
    def generate_financial_metadata(self, package, dataset_config, downloaded_files, acquisition_time):
        """Generate comprehensive financial intelligence metadata"""
        
        title = package.get('title', dataset_config['name'])
        description = package.get('notes', dataset_config['description'])
        organization = package.get('organization', {}).get('title', 'California State Controller\'s Office')
        last_updated = package.get('metadata_modified', 'Unknown')
        created = package.get('metadata_created', 'Unknown')
        
        # File information
        file_info = ""
        if downloaded_files:
            file_info += "### Downloaded Files\n"
            for file_data in downloaded_files:
                file_info += f"- **{file_data['filename']}**: {file_data['format'].upper()} ({file_data['file_size']:,} bytes)\n"
                file_info += f"  - Original: {file_data['original_name']}\n"
        
        metadata = f"""# {title}
## Financial Intelligence Dataset Metadata

### Source Information
**Dataset Name**: {title}
**Source Organization**: {organization}
**Data Authority**: California State Controller's Office
**Source URL**: https://data.ca.gov/dataset/{package.get('name', 'unknown')}
**Package ID**: {package.get('name', 'unknown')}
**License**: {package.get('license_title', 'Public Domain')}

### Financial Intelligence Classification
**Priority Level**: {dataset_config['priority']} (1=Critical, 3=Supporting)
**Analysis Type**: {dataset_config.get('analysis_type', 'Financial Intelligence')}
**LIHTC Use Case**: {dataset_config['use_case']}
**Data Scope**: {dataset_config.get('scope', 'Municipal/County Level')}

### Acquisition Details
**Acquisition Date**: {acquisition_time.strftime('%Y-%m-%d %H:%M:%S %Z')}
**Acquired By**: Colosseum Financial Intelligence Downloader
**Mission**: California Municipal Financial Health Analysis
**Total Files Downloaded**: {len(downloaded_files) if downloaded_files else 0}

{file_info}

### Dataset Timeline
**Dataset Created**: {created}
**Dataset Last Updated**: {last_updated}
**Update Frequency**: {package.get('update_frequency', 'Varies - typically annual')}

### Update Monitoring
**Update Check URL**: https://data.ca.gov/dataset/{package.get('name', 'unknown')}
**Organization Filter**: california-state-controllers-office
**Next Scheduled Check**: {(acquisition_time.replace(day=1) + pd.DateOffset(months=3)).strftime('%Y-%m-%d')}
**Update Responsibility**: Financial Intelligence Downloader
**Critical for**: LIHTC municipal financial health assessment

### Technical Specifications
**Geographic Coverage**: California Statewide
**Data Level**: Municipal and County Financial Data
**Tags**: {', '.join([tag['name'] for tag in package.get('tags', [])])}
**Resources Available**: {len(package.get('resources', []))}

### LIHTC Development Applications
**Primary Use Cases**:
- {dataset_config['use_case']}
- Municipal financial stability assessment
- Property tax burden analysis
- Development risk evaluation

**Integration Requirements**:
- Combine with transportation analysis for complete site intelligence
- Cross-reference with existing California datasets
- Municipal health scoring for site selection

**Analysis Framework**:
- Financial trend analysis (5-year minimum)
- Comparative municipal analysis
- Risk assessment scoring
- Pro forma impact calculations

### Quality Assessment
**Data Authority**: Official California State Controller records
**Completeness**: {len(downloaded_files)} of {len(package.get('resources', []))} resources acquired
**Source Validation**: State financial reporting requirements
**Fitness for LIHTC Analysis**: Critical financial intelligence for development decisions

### Usage Notes
**Dataset Description**: {description}

**Strategic Value**:
- Municipal financial health directly impacts LIHTC project viability
- Property tax trends affect long-term resident affordability
- Revenue/expenditure patterns indicate service delivery capacity
- Special district data reveals hidden development costs

**Analytical Applications**:
- Pre-development municipal risk screening
- Comparative site selection based on financial stability
- Property tax impact modeling for pro formas
- Long-term municipal viability assessment

### Resources Information
"""
        
        # Add resource details
        resources = package.get('resources', [])
        for i, resource in enumerate(resources, 1):
            metadata += f"""
**Resource {i}**: {resource.get('name', 'Unnamed')}
- Format: {resource.get('format', 'Unknown')}
- Size: {resource.get('size', 'Unknown')}
- Description: {resource.get('description', 'No description')[:100]}...
- URL: {resource.get('url', 'No URL')}
"""
        
        metadata += f"""
---
*Financial Intelligence Metadata generated from California State Controller's Office*  
*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*Standards Version: DATASET_ACQUISITION_STANDARDS.md v1.0*  
*Mission: California Municipal Financial Intelligence for LIHTC Development*
"""
        
        return metadata
    
    def acquire_all_financial_datasets(self):
        """Execute complete financial intelligence acquisition mission"""
        print("💰 CALIFORNIA FINANCIAL INTELLIGENCE ACQUISITION MISSION")
        print("=" * 80)
        print("🏛️ Source: California State Controller's Office")
        print("🎯 Objective: Municipal financial health intelligence for LIHTC development")
        
        mission_start = datetime.now()
        
        # Search all Controller datasets
        all_packages = self.search_controller_datasets()
        
        if not all_packages:
            print("❌ No datasets found from State Controller's Office")
            return 0, 0
        
        # Match packages to our priorities
        matched_datasets = {}
        
        for package in all_packages:
            dataset_key, dataset_config = self.match_dataset_to_priority(
                package, self.priority_financial_datasets
            )
            
            if dataset_key:
                matched_datasets[dataset_key] = {
                    'package': package,
                    'config': dataset_config
                }
        
        print(f"\n📊 DATASET MATCHING RESULTS:")
        print(f"   Total Controller datasets: {len(all_packages)}")
        print(f"   Matched to priorities: {len(matched_datasets)}")
        print(f"   Match rate: {len(matched_datasets)/len(self.priority_financial_datasets)*100:.1f}%")
        
        # Download matched datasets
        success_count = 0
        
        # Sort by priority
        sorted_matches = sorted(
            matched_datasets.items(),
            key=lambda x: x[1]['config']['priority']
        )
        
        for dataset_key, dataset_info in sorted_matches:
            print(f"\n🎯 PRIORITY {dataset_info['config']['priority']}")
            
            success = self.download_financial_dataset(
                dataset_info['package'], 
                dataset_key, 
                dataset_info['config']
            )
            
            if success:
                success_count += 1
            
            # Rate limiting between datasets
            time.sleep(3)
        
        mission_duration = datetime.now() - mission_start
        
        print(f"\n" + "=" * 80)
        print(f"💰 FINANCIAL INTELLIGENCE MISSION COMPLETE")
        print(f"📊 Success Rate: {success_count}/{len(matched_datasets)} matched datasets")
        print(f"🎯 Priority Coverage: {len(matched_datasets)}/{len(self.priority_financial_datasets)} priorities found")
        print(f"⏱️ Duration: {mission_duration}")
        
        return success_count, len(matched_datasets)

if __name__ == "__main__":
    downloader = CaliforniaFinancialIntelligenceDownloader()
    success, total = downloader.acquire_all_financial_datasets()
    
    print(f"\n✅ California financial intelligence acquisition complete!")
    print(f"📁 Data stored in: {downloader.data_dir}")
    print(f"💡 Ready for municipal financial health analysis integration")