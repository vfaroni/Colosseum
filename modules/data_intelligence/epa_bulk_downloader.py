#!/usr/bin/env python3
"""
EPA Bulk Data Downloader with Status Updates
Downloads federal environmental databases from EPA's public repository
Includes delays and progress reporting to prevent timeouts
WINGMAN Federal Environmental Data Mission
Date: 2025-08-10
"""

import requests
import time
import os
import zipfile
from pathlib import Path
from datetime import datetime
import json

class EPABulkDownloader:
    """Download EPA datasets with progress tracking and delays"""
    
    def __init__(self):
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.output_path = self.base_path / "data_sets" / "federal"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # EPA public data base URL
        self.base_url = "https://edg.epa.gov/data/public/"
        
        # Track what we download
        self.download_log = []
        self.start_time = datetime.now()
        
    def download_with_progress(self, url, output_file, description):
        """Download file with progress updates"""
        print(f"\n{'='*60}")
        print(f"DOWNLOADING: {description}")
        print(f"URL: {url}")
        print(f"Target: {output_file.name}")
        print(f"{'='*60}")
        
        try:
            # Start download with streaming
            response = requests.get(url, stream=True, timeout=30)
            
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                
                # Write file in chunks with progress updates
                chunk_size = 8192
                downloaded = 0
                
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Show progress every 100KB
                            if downloaded % (100 * 1024) < chunk_size:
                                if total_size > 0:
                                    percent = (downloaded / total_size) * 100
                                    print(f"Progress: {percent:.1f}% ({downloaded:,} / {total_size:,} bytes)")
                                else:
                                    print(f"Downloaded: {downloaded:,} bytes")
                
                file_size_mb = output_file.stat().st_size / (1024 * 1024)
                print(f"✅ SUCCESS: Downloaded {file_size_mb:.1f} MB")
                
                # Log successful download
                self.download_log.append({
                    'file': output_file.name,
                    'url': url,
                    'size_mb': round(file_size_mb, 1),
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
                
                return True
                
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                self.download_log.append({
                    'file': output_file.name,
                    'url': url,
                    'status': f'failed_http_{response.status_code}',
                    'timestamp': datetime.now().isoformat()
                })
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            self.download_log.append({
                'file': output_file.name,
                'url': url,
                'status': f'error_{type(e).__name__}',
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def extract_zip(self, zip_file):
        """Extract ZIP file if it exists"""
        if zip_file.exists():
            extract_dir = zip_file.parent / zip_file.stem
            extract_dir.mkdir(exist_ok=True)
            
            print(f"\nExtracting {zip_file.name}...")
            try:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                    files = zip_ref.namelist()
                    print(f"✅ Extracted {len(files)} files to {extract_dir.name}/")
                    
                    # Show first 5 files
                    for f in files[:5]:
                        print(f"  - {f}")
                    if len(files) > 5:
                        print(f"  ... and {len(files)-5} more files")
                    
                    return True
            except Exception as e:
                print(f"❌ Extraction failed: {e}")
                return False
        return False
    
    def run_downloads(self):
        """Execute downloads with delays between files"""
        
        print("\n" + "="*80)
        print("EPA FEDERAL ENVIRONMENTAL DATA BULK DOWNLOAD")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Define priority downloads
        downloads = [
            # OLEM - Land and Emergency Management
            {
                'url': f"{self.base_url}OLEM/NPL.zip",
                'dir': "EPA_Superfund",
                'file': "NPL.zip",
                'desc': "National Priorities List (Superfund Sites)",
                'extract': True
            },
            # OECA - Enforcement and Compliance
            {
                'url': f"{self.base_url}OECA/AnnualResults2015.zip",
                'dir': "EPA_Enforcement",
                'file': "AnnualResults2015.zip",
                'desc': "EPA Enforcement Annual Results 2015",
                'extract': True
            },
            {
                'url': f"{self.base_url}OECA/AnnualReport.zip",
                'dir': "EPA_Enforcement",
                'file': "AnnualReport.zip",
                'desc': "EPA Enforcement Annual Report",
                'extract': True
            },
            {
                'url': f"{self.base_url}OECA/CAFO_Density.zip",
                'dir': "EPA_Agriculture",
                'file': "CAFO_Density.zip",
                'desc': "Concentrated Animal Feeding Operations Density",
                'extract': True
            }
        ]
        
        # Process each download with delays
        for i, dl in enumerate(downloads, 1):
            print(f"\n{'='*60}")
            print(f"DOWNLOAD {i} OF {len(downloads)}")
            print(f"{'='*60}")
            
            # Create output directory
            output_dir = self.output_path / dl['dir']
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / dl['file']
            
            # Check if already exists
            if output_file.exists():
                print(f"⚠️ {dl['file']} already exists, skipping download")
                if dl.get('extract'):
                    self.extract_zip(output_file)
            else:
                # Download the file
                success = self.download_with_progress(dl['url'], output_file, dl['desc'])
                
                # Extract if successful and requested
                if success and dl.get('extract'):
                    time.sleep(2)  # Brief pause before extraction
                    self.extract_zip(output_file)
            
            # Delay between downloads (except last one)
            if i < len(downloads):
                print(f"\n⏳ Waiting 5 seconds before next download...")
                time.sleep(5)
        
        # Save download log
        self.save_summary()
        
        return True
    
    def save_summary(self):
        """Save download summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        summary = {
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_seconds': round(duration, 2),
            'downloads': self.download_log,
            'total_attempted': len(self.download_log),
            'successful': sum(1 for d in self.download_log if d.get('status') == 'success')
        }
        
        # Save summary
        summary_file = self.output_path / "epa_download_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print final summary
        print("\n" + "="*80)
        print("DOWNLOAD SUMMARY")
        print("="*80)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Files Attempted: {summary['total_attempted']}")
        print(f"Files Successful: {summary['successful']}")
        print(f"Output Directory: {self.output_path}")
        print("="*80)
        
        # Create master README
        self.create_readme()
    
    def create_readme(self):
        """Create README for federal datasets"""
        readme = f"""FEDERAL EPA ENVIRONMENTAL DATASETS
===================================
Download Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Source: EPA Public Data Repository (https://edg.epa.gov/data/public/)

DATASETS DOWNLOADED:
===================

1. SUPERFUND NPL (National Priorities List)
   Location: EPA_Superfund/NPL/
   Description: Most contaminated sites in America requiring cleanup
   
2. EPA ENFORCEMENT DATA
   Location: EPA_Enforcement/
   Description: Annual enforcement results and compliance data
   
3. CAFO DENSITY
   Location: EPA_Agriculture/
   Description: Concentrated Animal Feeding Operations locations

USAGE FOR LIHTC:
===============
- Screen properties for proximity to Superfund sites
- Check enforcement history in project areas
- Identify agricultural contamination risks (CAFOs)
- Support Phase I ESA investigations

NEXT STEPS:
==========
1. Process NPL data for geocoded Superfund sites
2. Extract enforcement violations by location
3. Integrate with California environmental database
4. Create unified search interface

Generated by: Colosseum LIHTC Platform - WINGMAN Agent
"""
        
        readme_file = self.output_path / "README_FEDERAL_EPA.txt"
        with open(readme_file, 'w') as f:
            f.write(readme)
        
        print(f"\n📄 Created README at {readme_file}")

def main():
    print("\n🚀 EPA BULK DATA DOWNLOADER")
    print("This will download key EPA environmental datasets")
    print("Including delays to prevent timeouts")
    print("-"*60)
    
    downloader = EPABulkDownloader()
    success = downloader.run_downloads()
    
    if success:
        print("\n✅ EPA DATA DOWNLOAD COMPLETE")
        print("Check data_sets/federal/ for downloaded files")
    else:
        print("\n⚠️ Some downloads may have failed")
        print("Check epa_download_summary.json for details")

if __name__ == "__main__":
    main()