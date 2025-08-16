#!/usr/bin/env python3
"""
EPA Intelligent Downloader
Downloads priority EPA environmental files based on deep crawl results
Organizes by data type and manages large downloads efficiently
WINGMAN Federal Environmental Data Mission - Smart Download
Date: 2025-08-10
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
import concurrent.futures

class EPAIntelligentDownloader:
    """Smart downloader for EPA environmental data"""
    
    def __init__(self):
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.output_path = self.base_path / "data_sets" / "federal" / "EPA_Data"
        
        # Load priority download list from crawler
        self.download_list_file = self.base_path / "data_sets" / "federal" / "epa_priority_download_list.json"
        self.download_log = []
        self.start_time = datetime.now()
        
        # Category mappings for organization
        self.categories = {
            'Superfund': ['superfund', 'npl', 'cercla', 'cerclis'],
            'RCRA': ['rcra', 'hazardous', 'corrective'],
            'Brownfields': ['brownfield', 'redevelop'],
            'Water': ['water', 'discharge', 'npdes', 'sdwis', 'groundwater'],
            'Air': ['air', 'emission', 'aqs', 'nei'],
            'Enforcement': ['enforce', 'compliance', 'violation', 'echo'],
            'UST': ['ust', 'lust', 'tank', 'storage', 'underground'],
            'Chemical': ['chemical', 'toxic', 'pesticide', 'tsca'],
            'Regional': ['region', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10']
        }
    
    def load_download_list(self):
        """Load prioritized file list from crawler"""
        if not self.download_list_file.exists():
            print("❌ No download list found. Run epa_deep_recursive_crawler.py first!")
            return []
        
        with open(self.download_list_file, 'r') as f:
            data = json.load(f)
        
        print(f"📋 Loaded {data['total_files']} priority files")
        print(f"   Total size: {data['total_size_mb']:.1f} MB")
        
        return data['files']
    
    def categorize_file(self, file_info):
        """Determine category for file organization"""
        filename_lower = file_info['filename'].lower()
        directory_lower = file_info['directory'].lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in filename_lower or keyword in directory_lower:
                    return category
        
        return 'Other'
    
    def download_file(self, file_info, max_size_mb=500):
        """Download a single file with size limits"""
        
        # Skip very large files initially
        if file_info['size_mb'] > max_size_mb:
            print(f"  ⏭️ Skipping large file ({file_info['size_mb']:.1f} MB): {file_info['filename']}")
            self.download_log.append({
                'file': file_info['filename'],
                'status': 'skipped_size',
                'size_mb': file_info['size_mb']
            })
            return False
        
        # Determine output directory by category
        category = self.categorize_file(file_info)
        output_dir = self.output_path / category / file_info['directory']
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / file_info['filename']
        
        # Skip if already downloaded
        if output_file.exists():
            existing_size = output_file.stat().st_size / (1024 * 1024)
            if existing_size > 0.01:  # Skip if more than 10KB
                print(f"  ✓ Already exists: {file_info['filename']}")
                self.download_log.append({
                    'file': file_info['filename'],
                    'status': 'already_exists',
                    'category': category
                })
                return True
        
        print(f"  ⬇️ Downloading: {file_info['filename']} ({file_info['size_display']})")
        print(f"     Category: {category}")
        
        try:
            response = requests.get(file_info['url'], stream=True, timeout=60)
            
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=32768):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Progress update every 10MB
                            if downloaded % (10 * 1024 * 1024) < 32768 and total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"     Progress: {percent:.1f}%")
                
                actual_size = output_file.stat().st_size / (1024 * 1024)
                print(f"  ✅ Success: {actual_size:.1f} MB saved")
                
                self.download_log.append({
                    'file': file_info['filename'],
                    'status': 'success',
                    'size_mb': actual_size,
                    'category': category,
                    'path': str(output_file.relative_to(self.base_path))
                })
                
                return True
            else:
                print(f"  ❌ HTTP {response.status_code}")
                self.download_log.append({
                    'file': file_info['filename'],
                    'status': f'http_{response.status_code}'
                })
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
            self.download_log.append({
                'file': file_info['filename'],
                'status': 'error',
                'error': str(e)[:200]
            })
            return False
    
    def run_intelligent_download(self, max_files=100, max_size_mb=500):
        """Execute intelligent download of priority files"""
        
        print("\n" + "="*80)
        print("EPA INTELLIGENT DOWNLOADER")
        print(f"Downloading top {max_files} priority environmental datasets")
        print(f"Max file size: {max_size_mb} MB")
        print(f"Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Load priority files
        files = self.load_download_list()
        
        if not files:
            print("❌ No files to download")
            return 0
        
        # Limit to max_files
        files_to_download = files[:max_files]
        
        # Download statistics
        success_count = 0
        total_downloaded_mb = 0
        
        # Download files
        for i, file_info in enumerate(files_to_download, 1):
            print(f"\n[{i}/{len(files_to_download)}] Priority Score: {file_info['priority_score']}")
            print(f"  File: {file_info['filename']}")
            print(f"  Path: {file_info['directory']}")
            
            if self.download_file(file_info, max_size_mb):
                success_count += 1
                if 'size_mb' in self.download_log[-1]:
                    total_downloaded_mb += self.download_log[-1]['size_mb']
            
            # Delay between downloads
            time.sleep(3)
            
            # Save progress every 10 files
            if i % 10 == 0:
                self.save_progress()
        
        # Final save
        self.save_progress()
        
        # Generate download report
        self.generate_report(success_count, total_downloaded_mb)
        
        return success_count
    
    def save_progress(self):
        """Save download progress"""
        progress = {
            'last_update': datetime.now().isoformat(),
            'files_attempted': len(self.download_log),
            'files_successful': len([d for d in self.download_log if d.get('status') == 'success']),
            'total_mb_downloaded': sum(d.get('size_mb', 0) for d in self.download_log if d.get('status') == 'success')
        }
        
        progress_file = self.output_path.parent / "download_progress.json"
        with open(progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def generate_report(self, success_count, total_mb):
        """Generate comprehensive download report"""
        
        duration = (datetime.now() - self.start_time).total_seconds() / 60
        
        # Categorize downloads
        by_category = {}
        for log in self.download_log:
            if log.get('status') == 'success':
                category = log.get('category', 'Other')
                if category not in by_category:
                    by_category[category] = {'count': 0, 'size_mb': 0}
                by_category[category]['count'] += 1
                by_category[category]['size_mb'] += log.get('size_mb', 0)
        
        report = {
            'download_date': self.start_time.isoformat(),
            'duration_minutes': round(duration, 1),
            'files_attempted': len(self.download_log),
            'files_successful': success_count,
            'total_mb_downloaded': round(total_mb, 1),
            'files_by_category': by_category,
            'download_log': self.download_log
        }
        
        report_file = self.output_path.parent / "epa_download_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*80)
        print("DOWNLOAD COMPLETE")
        print("="*80)
        print(f"Duration: {duration:.1f} minutes")
        print(f"Files Downloaded: {success_count} of {len(self.download_log)}")
        print(f"Total Size: {total_mb:.1f} MB")
        print(f"Average Speed: {total_mb/duration:.1f} MB/min" if duration > 0 else "")
        
        print("\n📊 Downloads by Category:")
        for category, stats in sorted(by_category.items(), key=lambda x: x[1]['count'], reverse=True):
            print(f"  {category}: {stats['count']} files ({stats['size_mb']:.1f} MB)")
        
        print("="*80)
        print(f"\n📄 Full report: {report_file.name}")
        
        # Create data inventory
        self.create_data_inventory()
    
    def create_data_inventory(self):
        """Create inventory of all downloaded EPA data"""
        
        inventory = {
            'created': datetime.now().isoformat(),
            'categories': {}
        }
        
        # Walk through downloaded files
        for category_dir in self.output_path.iterdir():
            if category_dir.is_dir():
                category_files = []
                
                for file in category_dir.rglob('*'):
                    if file.is_file():
                        category_files.append({
                            'name': file.name,
                            'path': str(file.relative_to(self.output_path)),
                            'size_mb': round(file.stat().st_size / (1024 * 1024), 1)
                        })
                
                if category_files:
                    inventory['categories'][category_dir.name] = {
                        'file_count': len(category_files),
                        'total_mb': sum(f['size_mb'] for f in category_files),
                        'files': category_files[:20]  # Sample
                    }
        
        inventory_file = self.output_path.parent / "epa_data_inventory.json"
        with open(inventory_file, 'w') as f:
            json.dump(inventory, f, indent=2)
        
        print(f"📦 Data inventory: {inventory_file.name}")

def main():
    print("\n🎯 EPA INTELLIGENT DOWNLOADER")
    print("Downloads priority environmental datasets based on crawl results")
    print("-"*60)
    
    downloader = EPAIntelligentDownloader()
    
    # Check if download list exists
    if not downloader.download_list_file.exists():
        print("\n❌ ERROR: No download list found!")
        print("Please run epa_deep_recursive_crawler.py first")
        return
    
    # Run download with limits
    success = downloader.run_intelligent_download(
        max_files=100,  # Download top 100 files
        max_size_mb=500  # Skip files larger than 500MB
    )
    
    print(f"\n✅ INTELLIGENT DOWNLOAD COMPLETE")
    print(f"Successfully downloaded {success} priority EPA datasets")
    print("\nData organized by category in: data_sets/federal/EPA_Data/")

if __name__ == "__main__":
    main()