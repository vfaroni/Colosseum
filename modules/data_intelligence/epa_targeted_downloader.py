#!/usr/bin/env python3
"""
EPA Targeted Data Downloader
Downloads specific high-value EPA environmental datasets
Based on actual files discovered in EPA directories
WINGMAN Federal Environmental Data Mission - Phase 5
Date: 2025-08-10
"""

import requests
import time
from pathlib import Path
from datetime import datetime
import json

class EPATargetedDownloader:
    """Download specific EPA files we know exist"""
    
    def __init__(self):
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.output_path = self.base_path / "data_sets" / "federal"
        self.base_url = "https://edg.epa.gov/data/public/"
        
        self.download_log = []
        self.start_time = datetime.now()
        
    def download_file(self, url, output_dir, filename, description):
        """Download a specific file with progress tracking"""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / filename
        
        if output_file.exists():
            print(f"  ⚠️ {filename} already exists")
            return True
        
        print(f"  Downloading: {filename}")
        print(f"  Description: {description}")
        
        try:
            response = requests.get(url, stream=True, timeout=60)
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=32768):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Progress update every 5MB
                            if downloaded % (5 * 1024 * 1024) < 32768 and total_size > 0:
                                percent = (downloaded / total_size) * 100
                                mb_down = downloaded / (1024 * 1024)
                                mb_total = total_size / (1024 * 1024)
                                print(f"    Progress: {percent:.1f}% ({mb_down:.1f}/{mb_total:.1f} MB)")
                
                final_size = output_file.stat().st_size / (1024 * 1024)
                print(f"  ✅ Success: {final_size:.1f} MB downloaded")
                
                self.download_log.append({
                    'file': filename,
                    'size_mb': round(final_size, 1),
                    'status': 'success',
                    'description': description
                })
                return True
            else:
                print(f"  ❌ HTTP {response.status_code}")
                self.download_log.append({
                    'file': filename,
                    'status': f'failed_{response.status_code}'
                })
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            self.download_log.append({
                'file': filename,
                'status': 'error'
            })
            return False
    
    def run_targeted_downloads(self):
        """Download specific high-value EPA datasets"""
        
        print("\n" + "="*80)
        print("EPA TARGETED ENVIRONMENTAL DATA DOWNLOAD")
        print("High-Value Datasets Based on Directory Discovery")
        print(f"Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # High-priority files discovered in EPA directories
        priority_downloads = [
            # Region 1 - New England
            {
                'url': f"{self.base_url}R1/Region1_RCRA_CA_GIS_DATA.gdb.zip",
                'dir': "EPA_RCRA/Region1",
                'file': "Region1_RCRA_CA_GIS_DATA.gdb.zip",
                'desc': "Region 1 RCRA Corrective Action Sites - New England"
            },
            {
                'url': f"{self.base_url}R1/RAINE.gdb.zip",
                'dir': "EPA_Regional/R1",
                'file': "RAINE.gdb.zip",
                'desc': "Region 1 Environmental Database (35MB)"
            },
            
            # Region 3 - Mid-Atlantic (if exists)
            {
                'url': f"{self.base_url}R3-CBP/CBP_Data.zip",
                'dir': "EPA_Regional/R3",
                'file': "CBP_Data.zip",
                'desc': "Chesapeake Bay Program Environmental Data"
            },
            
            # OLEM - Core contamination data
            {
                'url': f"{self.base_url}OLEM/Superfund_NPL_Sites.gdb.zip",
                'dir': "EPA_Superfund",
                'file': "Superfund_NPL_Sites.gdb.zip",
                'desc': "National Priorities List Superfund Sites"
            },
            {
                'url': f"{self.base_url}OLEM/RCRA_Sites.gdb.zip",
                'dir': "EPA_RCRA",
                'file': "RCRA_Sites.gdb.zip",
                'desc': "RCRA Hazardous Waste Handler Database"
            },
            {
                'url': f"{self.base_url}OLEM/Brownfields_Sites.gdb.zip",
                'dir': "EPA_Brownfields",
                'file': "Brownfields_Sites.gdb.zip",
                'desc': "EPA Brownfields Site Inventory"
            },
            
            # Additional valuable datasets
            {
                'url': f"{self.base_url}R1/CombinedSewerOutfalls.gdb.zip",
                'dir': "EPA_Water/R1",
                'file': "CombinedSewerOutfalls.gdb.zip",
                'desc': "Combined Sewer Overflow Locations"
            },
            {
                'url': f"{self.base_url}R1/Valleys_R1239.gdb.zip",
                'dir': "EPA_Regional/R1",
                'file': "Valleys_R1239.gdb.zip",
                'desc': "Region 1 Valley Environmental Data (2GB)"
            }
        ]
        
        # Download files with status updates
        success_count = 0
        total_size = 0
        
        for i, dl in enumerate(priority_downloads, 1):
            print(f"\n[{i}/{len(priority_downloads)}] DOWNLOAD ATTEMPT")
            print("-"*40)
            
            output_dir = self.output_path / dl['dir']
            
            if self.download_file(dl['url'], output_dir, dl['file'], dl['desc']):
                success_count += 1
                # Get actual file size
                downloaded_file = output_dir / dl['file']
                if downloaded_file.exists():
                    size_mb = downloaded_file.stat().st_size / (1024 * 1024)
                    total_size += size_mb
            
            # Delay between downloads
            if i < len(priority_downloads):
                print("\n⏳ Waiting 5 seconds before next download...")
                time.sleep(5)
        
        # Save summary
        self.save_summary(success_count, len(priority_downloads), total_size)
        
        return success_count
    
    def save_summary(self, success_count, total_attempted, total_size):
        """Save download summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        summary = {
            'mission': 'EPA Targeted Environmental Data Download',
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_seconds': round(duration, 2),
            'total_attempted': total_attempted,
            'successful': success_count,
            'total_size_mb': round(total_size, 1),
            'downloads': self.download_log
        }
        
        summary_file = self.output_path / "epa_targeted_download_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print("\n" + "="*80)
        print("DOWNLOAD SUMMARY")
        print("="*80)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Files Attempted: {total_attempted}")
        print(f"Files Successful: {success_count}")
        print(f"Total Data Size: {total_size:.1f} MB")
        print(f"Success Rate: {(success_count/total_attempted)*100:.1f}%")
        print("="*80)
        
        # Create documentation
        self.create_documentation(summary)
    
    def create_documentation(self, summary):
        """Create documentation for downloaded data"""
        
        readme = f"""EPA TARGETED ENVIRONMENTAL DATASETS
=====================================
Download Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Source: EPA Environmental Dataset Gateway

DOWNLOAD RESULTS:
=================
Files Downloaded: {summary['successful']} of {summary['total_attempted']}
Total Size: {summary['total_size_mb']:.1f} MB
Duration: {summary['duration_seconds']:.1f} seconds

KEY DATASETS ACQUIRED:
======================

1. RCRA CORRECTIVE ACTION
   - Region 1 RCRA CA Sites (New England)
   - Hazardous waste cleanup sites
   - Critical for LIHTC screening

2. REGIONAL ENVIRONMENTAL DATA
   - RAINE Database (Region 1)
   - Valley environmental data
   - Regional contamination sources

3. WATER QUALITY
   - Combined Sewer Outfalls
   - Water discharge points
   - Flood and contamination risk

CRITICAL FOR LIHTC:
===================
- RCRA sites indicate industrial contamination
- Regional data shows local environmental risks
- Water quality affects property development
- All require Phase I ESA consideration

DATA PROCESSING:
================
Most files are geodatabases (.gdb.zip) which require:
1. Extraction of ZIP files
2. Processing with geopandas or GDAL
3. Conversion to CSV/Parquet for analysis

NEXT STEPS:
===========
1. Extract geodatabase files
2. Convert to usable formats
3. Geocode facility locations
4. Integrate with unified database

Generated by: Colosseum LIHTC Platform - WINGMAN Agent
Mission: Federal Environmental Data Acquisition
"""
        
        readme_file = self.output_path / "README_EPA_TARGETED.txt"
        with open(readme_file, 'w') as f:
            f.write(readme)
        
        print(f"\n📄 Created documentation: {readme_file.name}")

def main():
    print("\n🎯 EPA TARGETED DATA DOWNLOADER")
    print("Downloading specific high-value environmental datasets")
    print("-"*60)
    
    downloader = EPATargetedDownloader()
    success_count = downloader.run_targeted_downloads()
    
    print(f"\n✅ TARGETED DOWNLOAD COMPLETE")
    print(f"Successfully downloaded {success_count} datasets")
    print("Check data_sets/federal/ for downloaded files")

if __name__ == "__main__":
    main()