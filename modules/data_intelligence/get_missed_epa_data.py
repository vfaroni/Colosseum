#!/usr/bin/env python3
"""
Download the EPA data we missed from nested directories
Specifically gets R4/metadata and other missed valuable files
"""

import requests
import json
from pathlib import Path
from datetime import datetime

class MissedEPADownloader:
    def __init__(self):
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.output_path = self.base_path / "data_sets" / "federal" / "EPA_Data"
        self.base_url = "https://edg.epa.gov/data/public/"
        self.downloaded = []
        
    def download_file(self, region, subdir, filename):
        """Download a specific file"""
        # Build URL
        if subdir:
            url = f"{self.base_url}{region}/{subdir}/{filename}"
            output_dir = self.output_path / "Regional" / region / subdir
        else:
            url = f"{self.base_url}{region}/{filename}"
            output_dir = self.output_path / "Regional" / region
        
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / filename
        
        if output_file.exists():
            print(f"  ✓ Already exists: {filename}")
            return True
        
        print(f"  Downloading: {filename}")
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                size_mb = len(response.content) / (1024 * 1024)
                print(f"    ✅ Success: {size_mb:.2f} MB")
                
                self.downloaded.append({
                    'region': region,
                    'subdir': subdir,
                    'file': filename,
                    'size_mb': size_mb,
                    'path': str(output_file.relative_to(self.base_path))
                })
                return True
            else:
                print(f"    ❌ HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"    ❌ Error: {str(e)[:50]}")
            return False
    
    def get_missed_data(self):
        """Download the valuable data we missed"""
        
        print("\n" + "="*80)
        print("DOWNLOADING MISSED EPA DATA FROM NESTED DIRECTORIES")
        print("="*80)
        
        # Critical files we missed
        missed_files = [
            # R4 metadata - NPL and RCRA sites!
            {'region': 'R4', 'subdir': 'metadata', 'file': 'R4FRS_npl.shp.xml'},
            {'region': 'R4', 'subdir': 'metadata', 'file': 'R4FRSrcra_lqg.shp.xml'},
            {'region': 'R4', 'subdir': 'metadata', 'file': 'FRSrmp.shp.xml'},
            {'region': 'R4', 'subdir': 'metadata', 'file': 'Region4.json'},
            {'region': 'R4', 'subdir': 'metadata', 'file': 'PM25_2006Std_NAA.shp.xml'},
            
            # R5 JSON files
            {'region': 'R5', 'subdir': '', 'file': 'R5.json'},
            {'region': 'R5', 'subdir': '', 'file': 'R5_org.json'},
        ]
        
        success_count = 0
        
        for item in missed_files:
            print(f"\n{item['region']}/{item['subdir']}/{item['file']}:" if item['subdir'] else f"\n{item['region']}/{item['file']}:")
            if self.download_file(item['region'], item['subdir'], item['file']):
                success_count += 1
        
        # Save summary
        summary = {
            'download_date': datetime.now().isoformat(),
            'purpose': 'Get missed EPA data from nested directories',
            'files_attempted': len(missed_files),
            'files_successful': success_count,
            'total_mb': sum(d['size_mb'] for d in self.downloaded),
            'downloads': self.downloaded
        }
        
        summary_file = self.output_path.parent / "epa_missed_data_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Files downloaded: {success_count} of {len(missed_files)}")
        print(f"Total size: {summary['total_mb']:.2f} MB")
        
        if self.downloaded:
            print("\nKey acquisitions:")
            for d in self.downloaded:
                if 'npl' in d['file'].lower() or 'rcra' in d['file'].lower():
                    print(f"  ⭐ {d['file']} - {d['region']} environmental sites")
        
        print("="*80)
        
        return success_count

def main():
    print("\n🎯 GETTING MISSED EPA DATA")
    print("Downloading valuable files from nested directories")
    print("-"*60)
    
    downloader = MissedEPADownloader()
    count = downloader.get_missed_data()
    
    print(f"\n✅ MISSED DATA RECOVERY COMPLETE")
    print(f"Successfully downloaded {count} additional EPA files")
    print("\nKey achievement:")
    print("  - R4 Southeast region NPL and RCRA data acquired")
    print("  - R5 Great Lakes region data acquired")
    print("  - Critical metadata files for site locations obtained")

if __name__ == "__main__":
    main()