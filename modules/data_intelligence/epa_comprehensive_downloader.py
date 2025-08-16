#!/usr/bin/env python3
"""
EPA Comprehensive Environmental Data Downloader
Downloads ALL critical environmental contamination datasets
WINGMAN Federal Environmental Data Mission - Phase 2
Date: 2025-08-10
"""

import requests
import time
import zipfile
import json
from pathlib import Path
from datetime import datetime

class EPAComprehensiveDownloader:
    """Download all EPA environmental contamination datasets"""
    
    def __init__(self):
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.output_path = self.base_path / "data_sets" / "federal"
        self.base_url = "https://edg.epa.gov/data/public/"
        
        # Track downloads
        self.download_log = []
        self.start_time = datetime.now()
        
    def download_file(self, url, output_dir, filename, description):
        """Download with progress tracking"""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / filename
        
        # Skip if exists
        if output_file.exists():
            print(f"⚠️ {filename} already exists, skipping")
            return True
        
        print(f"\n{'='*60}")
        print(f"DOWNLOADING: {description}")
        print(f"File: {filename}")
        print(f"{'='*60}")
        
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
                            
                            # Progress updates
                            if downloaded % (500 * 1024) < 8192 and total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"Progress: {percent:.1f}% ({downloaded:,} / {total_size:,} bytes)")
                
                file_size_mb = output_file.stat().st_size / (1024 * 1024)
                print(f"✅ SUCCESS: Downloaded {file_size_mb:.1f} MB")
                
                self.download_log.append({
                    'file': filename,
                    'size_mb': round(file_size_mb, 1),
                    'status': 'success',
                    'description': description
                })
                
                # Extract if ZIP
                if filename.endswith('.zip'):
                    self.extract_zip(output_file)
                
                return True
            else:
                print(f"❌ HTTP {response.status_code}")
                self.download_log.append({
                    'file': filename,
                    'status': f'failed_{response.status_code}',
                    'description': description
                })
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            self.download_log.append({
                'file': filename,
                'status': 'error',
                'description': description
            })
            return False
    
    def extract_zip(self, zip_file):
        """Extract ZIP files"""
        extract_dir = zip_file.parent / zip_file.stem
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                print(f"  📦 Extracted to {extract_dir.name}/")
                return True
        except Exception as e:
            print(f"  ⚠️ Could not extract: {e}")
            return False
    
    def run_comprehensive_download(self):
        """Download all critical EPA environmental datasets"""
        
        print("\n" + "="*80)
        print("EPA COMPREHENSIVE ENVIRONMENTAL DATA DOWNLOAD")
        print("Critical Contamination Databases")
        print(f"Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Define priority downloads
        critical_downloads = [
            # RCRA Hazardous Waste
            {
                'url': f"{self.base_url}OLEM/RCRA_Facility_Information.xml",
                'dir': "EPA_RCRA",
                'file': "RCRA_Facility_Information.xml",
                'desc': "RCRA Hazardous Waste Facility Information"
            },
            {
                'url': f"{self.base_url}OLEM/Resource_Conservation_and_Recovery_Act_Information_(RCRAInfo).xml",
                'dir': "EPA_RCRA",
                'file': "RCRAInfo.xml",
                'desc': "RCRA Comprehensive Information System"
            },
            
            # Brownfields
            {
                'url': f"{self.base_url}OLEM/Brownfields_Site_Information.xml",
                'dir': "EPA_Brownfields",
                'file': "Brownfields_Site_Information.xml",
                'desc': "EPA Brownfields Site Database"
            },
            {
                'url': f"{self.base_url}OLEM/Brownfields_Grants_Information.xml",
                'dir': "EPA_Brownfields",
                'file': "Brownfields_Grants_Information.xml",
                'desc': "Brownfields Grant Recipients"
            },
            
            # Underground Storage Tanks
            {
                'url': f"{self.base_url}OLEM/USTLUST_Site_Information.xml",
                'dir': "EPA_UST",
                'file': "USTLUST_Site_Information.xml",
                'desc': "Underground Storage Tanks and LUST Sites"
            },
            {
                'url': f"{self.base_url}OLEM/UST_Financial_Assurance_Information.xml",
                'dir': "EPA_UST",
                'file': "UST_Financial_Assurance.xml",
                'desc': "UST Financial Assurance Records"
            },
            
            # Superfund Additional
            {
                'url': f"{self.base_url}OLEM/Superfund_Site_Information.xml",
                'dir': "EPA_Superfund",
                'file': "Superfund_Site_Information.xml",
                'desc': "Superfund Comprehensive Site Information"
            },
            {
                'url': f"{self.base_url}OLEM/Superfund_Site.json",
                'dir': "EPA_Superfund",
                'file': "Superfund_Site.json",
                'desc': "Superfund Sites JSON Format"
            },
            
            # Corrective Action
            {
                'url': f"{self.base_url}OLEM/OLEM_Metadata.zipp",
                'dir': "EPA_OLEM_Metadata",
                'file': "OLEM_Metadata.zip",
                'desc': "OLEM Complete Metadata Package"
            }
        ]
        
        # Process downloads with delays
        success_count = 0
        for i, dl in enumerate(critical_downloads, 1):
            print(f"\n{'='*60}")
            print(f"DOWNLOAD {i} OF {len(critical_downloads)}")
            
            output_dir = self.output_path / dl['dir']
            
            if self.download_file(dl['url'], output_dir, dl['file'], dl['desc']):
                success_count += 1
            
            # Delay between downloads
            if i < len(critical_downloads):
                print(f"\n⏳ Waiting 3 seconds...")
                time.sleep(3)
        
        # Save summary
        self.save_summary(success_count, len(critical_downloads))
        
        return success_count
    
    def save_summary(self, success_count, total_count):
        """Save download summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        summary = {
            'mission': 'EPA Comprehensive Environmental Data Download',
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_seconds': round(duration, 2),
            'total_attempted': total_count,
            'successful': success_count,
            'downloads': self.download_log
        }
        
        summary_file = self.output_path / "epa_comprehensive_download_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print("\n" + "="*80)
        print("DOWNLOAD SUMMARY")
        print("="*80)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Files Attempted: {total_count}")
        print(f"Files Successful: {success_count}")
        print(f"Success Rate: {(success_count/total_count)*100:.1f}%")
        print("="*80)
        
        # Update master README
        self.update_documentation()
    
    def update_documentation(self):
        """Update federal data documentation"""
        readme = f"""EPA COMPREHENSIVE ENVIRONMENTAL DATASETS
=========================================
Download Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Source: EPA Environmental Dataset Gateway

CRITICAL DATASETS ACQUIRED:
===========================

1. RCRA HAZARDOUS WASTE
   - RCRA Facility Information
   - RCRAInfo comprehensive database
   - All hazardous waste handlers nationwide

2. BROWNFIELDS
   - Brownfields Site Information
   - Grant recipient locations
   - Redevelopment opportunities

3. UNDERGROUND STORAGE TANKS (UST/LUST)
   - UST/LUST site locations
   - Leaking underground storage tanks
   - Financial assurance records

4. SUPERFUND EXPANSION
   - Comprehensive site information
   - JSON formatted data
   - NPL boundaries (already downloaded)

5. OLEM METADATA
   - Complete metadata package
   - Data dictionaries
   - Field descriptions

CRITICAL FOR LIHTC:
===================
- RCRA sites: Industrial contamination risk
- Brownfields: Redevelopment opportunities
- UST/LUST: Petroleum contamination
- All require Phase I ESA consideration

NEXT STEPS:
===========
1. Process XML/JSON files to extract site data
2. Geocode facility addresses
3. Integrate with unified database
4. Create contamination risk layers

Generated by: Colosseum LIHTC Platform - WINGMAN Agent
"""
        
        readme_file = self.output_path / "README_EPA_COMPREHENSIVE.txt"
        with open(readme_file, 'w') as f:
            f.write(readme)
        
        print(f"\n📄 Updated documentation: {readme_file.name}")

def main():
    print("\n🚀 EPA COMPREHENSIVE ENVIRONMENTAL DOWNLOADER")
    print("Acquiring ALL critical contamination databases")
    print("-"*60)
    
    downloader = EPAComprehensiveDownloader()
    success_count = downloader.run_comprehensive_download()
    
    print(f"\n✅ COMPREHENSIVE DOWNLOAD COMPLETE")
    print(f"Successfully downloaded {success_count} critical datasets")
    print("Check data_sets/federal/ for all files")

if __name__ == "__main__":
    main()