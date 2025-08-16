#!/usr/bin/env python3
"""
EPA Regional and Additional Data Downloader
Downloads Regional (R1-R10), Water, Air, and OSWER datasets
WINGMAN Federal Environmental Data Mission - Phase 3
Date: 2025-08-10
"""

import requests
import time
import zipfile
import json
from pathlib import Path
from datetime import datetime

class EPARegionalDownloader:
    """Download EPA regional and specialized environmental datasets"""
    
    def __init__(self):
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.output_path = self.base_path / "data_sets" / "federal"
        self.base_url = "https://edg.epa.gov/data/public/"
        
        self.download_log = []
        self.start_time = datetime.now()
        
    def explore_directory(self, dir_path):
        """Explore what's in a directory"""
        url = f"{self.base_url}{dir_path}"
        print(f"Exploring: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Look for links to files
                content = response.text
                # Basic HTML parsing to find files
                if '.zip' in content or '.csv' in content or '.json' in content:
                    print(f"  ✓ Found data files in {dir_path}")
                    return True
            return False
        except:
            return False
    
    def download_file(self, url, output_dir, filename, description):
        """Download with progress tracking"""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / filename
        
        if output_file.exists():
            print(f"  ⚠️ {filename} already exists, skipping")
            return True
        
        print(f"  Downloading: {filename}")
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Progress update every 1MB
                            if downloaded % (1024 * 1024) < 8192 and total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"    Progress: {percent:.1f}%")
                
                size_mb = output_file.stat().st_size / (1024 * 1024)
                
                # Check if it's real data or just metadata
                if size_mb < 0.01:  # Less than 10KB
                    print(f"    ⚠️ File too small ({size_mb:.3f} MB) - likely metadata")
                    self.download_log.append({
                        'file': filename,
                        'size_mb': round(size_mb, 3),
                        'status': 'metadata_only',
                        'description': description
                    })
                else:
                    print(f"    ✅ Success: {size_mb:.1f} MB")
                    self.download_log.append({
                        'file': filename,
                        'size_mb': round(size_mb, 1),
                        'status': 'success',
                        'description': description
                    })
                    
                    # Extract if ZIP and substantial size
                    if filename.endswith('.zip') and size_mb > 0.1:
                        self.extract_zip(output_file)
                
                return True
            else:
                print(f"    ❌ HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            return False
    
    def extract_zip(self, zip_file):
        """Extract ZIP files"""
        extract_dir = zip_file.parent / zip_file.stem
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                print(f"    📦 Extracted to {extract_dir.name}/")
                return True
        except:
            return False
    
    def download_regional_data(self):
        """Download data from EPA Regional offices"""
        print("\n" + "="*80)
        print("DOWNLOADING EPA REGIONAL DATA (R1-R10)")
        print("="*80)
        
        regions = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10']
        
        # Common regional data files to look for
        potential_files = [
            'regional_sites.zip',
            'enforcement.zip', 
            'contaminated_sites.csv',
            'rcra_facilities.zip',
            'brownfields.zip',
            'superfund_regional.zip'
        ]
        
        success_count = 0
        
        for region in regions:
            print(f"\n{region} - EPA Region {region[1:]}:")
            
            # Explore what's available
            has_data = self.explore_directory(region + '/')
            
            if has_data:
                # Try to download common files
                for file in potential_files:
                    url = f"{self.base_url}{region}/{file}"
                    output_dir = self.output_path / f"EPA_Regional/{region}"
                    
                    if self.download_file(url, output_dir, file, f"{region} {file}"):
                        success_count += 1
                        time.sleep(2)  # Be nice to EPA servers
            else:
                print(f"  No data files found in {region}")
        
        return success_count
    
    def download_water_quality_data(self):
        """Download water quality data from OW directory"""
        print("\n" + "="*80)
        print("DOWNLOADING EPA WATER QUALITY DATA")
        print("="*80)
        
        water_files = [
            'SDWIS_Data.zip',  # Safe Drinking Water Information System
            'WATERS_Data.zip',  # Watershed Assessment data
            'STORET_Data.zip',  # Water quality data
            'NPDES_Permits.zip',  # Discharge permits
            'WQX_Data.zip'  # Water Quality Exchange
        ]
        
        success_count = 0
        
        for file in water_files:
            url = f"{self.base_url}OW/{file}"
            output_dir = self.output_path / "EPA_Water"
            
            print(f"\nAttempting: {file}")
            if self.download_file(url, output_dir, file, f"Water Quality - {file}"):
                success_count += 1
                time.sleep(3)
        
        return success_count
    
    def download_air_quality_data(self):
        """Download air quality data from OAR directory"""
        print("\n" + "="*80)
        print("DOWNLOADING EPA AIR QUALITY DATA")
        print("="*80)
        
        air_files = [
            'AQS_Sites.zip',  # Air Quality System monitoring sites
            'NEI_Emissions.zip',  # National Emissions Inventory
            'TRI_Releases.zip',  # Toxic Release Inventory
            'NAAQS_Counties.csv',  # Non-attainment areas
            'Environmental_Justice.zip'  # EJ screening data
        ]
        
        success_count = 0
        
        for file in air_files:
            url = f"{self.base_url}OAR/{file}"
            output_dir = self.output_path / "EPA_Air"
            
            print(f"\nAttempting: {file}")
            if self.download_file(url, output_dir, file, f"Air Quality - {file}"):
                success_count += 1
                time.sleep(3)
        
        return success_count
    
    def run_comprehensive_regional_download(self):
        """Execute all regional and specialized downloads"""
        
        print("\n" + "="*80)
        print("EPA COMPREHENSIVE REGIONAL & SPECIALIZED DATA DOWNLOAD")
        print(f"Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        total_success = 0
        
        # Download regional data
        print("\n🌎 PHASE 1: Regional Data")
        regional_count = self.download_regional_data()
        total_success += regional_count
        
        # Download water quality data
        print("\n💧 PHASE 2: Water Quality Data")
        water_count = self.download_water_quality_data()
        total_success += water_count
        
        # Download air quality data
        print("\n🌬️ PHASE 3: Air Quality Data")
        air_count = self.download_air_quality_data()
        total_success += air_count
        
        # Save summary
        self.save_summary(total_success)
        
        return total_success
    
    def save_summary(self, success_count):
        """Save download summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        # Separate real data from metadata
        real_data = [d for d in self.download_log if d.get('status') == 'success']
        metadata_only = [d for d in self.download_log if d.get('status') == 'metadata_only']
        
        summary = {
            'mission': 'EPA Regional and Specialized Data Download',
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_seconds': round(duration, 2),
            'total_attempted': len(self.download_log),
            'real_data_files': len(real_data),
            'metadata_files': len(metadata_only),
            'total_size_mb': sum(d.get('size_mb', 0) for d in real_data),
            'downloads': self.download_log
        }
        
        summary_file = self.output_path / "epa_regional_download_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print("\n" + "="*80)
        print("DOWNLOAD SUMMARY")
        print("="*80)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Files Attempted: {len(self.download_log)}")
        print(f"Real Data Files: {len(real_data)}")
        print(f"Metadata Files: {len(metadata_only)}")
        print(f"Total Data Size: {summary['total_size_mb']:.1f} MB")
        print("="*80)
        
        # Update documentation
        self.update_documentation(summary)
    
    def update_documentation(self, summary):
        """Update federal data documentation"""
        readme = f"""EPA REGIONAL AND SPECIALIZED ENVIRONMENTAL DATASETS
====================================================
Download Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Source: EPA Environmental Dataset Gateway

DOWNLOAD RESULTS:
================
Real Data Files: {summary['real_data_files']}
Metadata Files: {summary['metadata_files']}
Total Size: {summary['total_size_mb']:.1f} MB

ATTEMPTED SOURCES:
==================

1. REGIONAL DATA (R1-R10)
   - EPA Region 1: New England
   - EPA Region 2: NY, NJ, PR, VI
   - EPA Region 3: Mid-Atlantic
   - EPA Region 4: Southeast
   - EPA Region 5: Great Lakes
   - EPA Region 6: South Central
   - EPA Region 7: Midwest
   - EPA Region 8: Mountains & Plains
   - EPA Region 9: Pacific Southwest
   - EPA Region 10: Pacific Northwest

2. WATER QUALITY (OW)
   - Safe Drinking Water Information
   - Watershed Assessment
   - Water Quality Exchange
   - NPDES Discharge Permits

3. AIR QUALITY (OAR)
   - Air Quality System Sites
   - National Emissions Inventory
   - Toxic Release Inventory
   - Environmental Justice Screening

CRITICAL FOR LIHTC:
===================
- Regional contamination varies significantly
- Water quality affects property viability
- Air quality impacts environmental justice scoring
- Combined data enables comprehensive screening

STATUS:
=======
Many EPA directories contain only metadata XML files (0 KB).
Real data may require:
- Direct portal access
- API authentication
- FOIA requests
- Commercial data providers

RECOMMENDATION:
==============
For comprehensive coverage, consider:
1. EDR (Environmental Data Resources) - Commercial provider
2. State environmental agencies - Often better data
3. EPA web portals - Manual downloads
4. FOIA requests - For specific datasets

Generated by: Colosseum LIHTC Platform - WINGMAN Agent
"""
        
        readme_file = self.output_path / "README_EPA_REGIONAL.txt"
        with open(readme_file, 'w') as f:
            f.write(readme)
        
        print(f"\n📄 Updated documentation: {readme_file.name}")

def main():
    print("\n🚀 EPA REGIONAL & SPECIALIZED DATA DOWNLOADER")
    print("Attempting to acquire regional and specialized datasets")
    print("-"*60)
    
    downloader = EPARegionalDownloader()
    success_count = downloader.run_comprehensive_regional_download()
    
    print(f"\n✅ REGIONAL DOWNLOAD COMPLETE")
    print(f"Check data_sets/federal/ for downloaded files")
    print("\nNOTE: Most EPA directories contain metadata only.")
    print("Real data requires manual portal access or commercial providers.")

if __name__ == "__main__":
    main()