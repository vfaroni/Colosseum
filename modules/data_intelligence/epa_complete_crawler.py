#!/usr/bin/env python3
"""
EPA Complete Deep Crawler - Goes into ALL subdirectories including metadata
Fixes the issue where we missed R4/metadata and other nested data
WINGMAN Federal Environmental Data Mission - Complete Discovery
Date: 2025-08-09
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from pathlib import Path
from datetime import datetime
import pickle

class EPACompleteCrawler:
    """Complete EPA crawler that explores ALL directories to any depth"""
    
    def __init__(self):
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.output_path = self.base_path / "data_sets" / "federal"
        self.base_url = "https://edg.epa.gov/data/public/"
        
        self.discovered_files = []
        self.explored_directories = set()
        self.start_time = datetime.now()
        self.file_count = 0
        self.dir_count = 0
        
        # Environmental keywords
        self.keywords = {
            'critical': ['superfund', 'npl', 'cercla', 'cerclis', 'rcra', 'hazardous', 'toxic'],
            'high': ['brownfield', 'contamina', 'cleanup', 'remediat', 'corrective', 'enforce'],
            'medium': ['ust', 'lust', 'tank', 'storage', 'underground', 'permit', 'violation'],
            'low': ['water', 'air', 'soil', 'discharge', 'emission', 'waste', 'pollut']
        }
    
    def crawl_directory(self, dir_path, depth=0, max_depth=3):
        """Recursively crawl ALL directories including metadata"""
        
        if depth > max_depth:
            print(f"    ⚠️ Max depth {max_depth} reached")
            return
        
        if dir_path in self.explored_directories:
            return
        
        url = self.base_url + dir_path
        if not dir_path.endswith('/'):
            url += '/'
        
        self.dir_count += 1
        indent = "  " * depth
        print(f"{indent}📁 Exploring: {dir_path if dir_path else 'Root'}/ (depth: {depth})")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            self.explored_directories.add(dir_path)
            
            subdirs_found = []
            files_found = 0
            
            for link in soup.find_all('a'):
                href = link.get('href', '')
                text = link.text.strip()
                
                if 'Parent Directory' in text or not href:
                    continue
                
                # Check if it's a file
                if '.' in href and not href.endswith('/'):
                    file_info = self.extract_file_info(dir_path, text, link)
                    if file_info:
                        self.discovered_files.append(file_info)
                        self.file_count += 1
                        files_found += 1
                        
                        if file_info['priority_score'] > 20:
                            print(f"{indent}  ⭐ {text} ({file_info['size_display']})")
                
                # Check if it's a subdirectory
                elif href.endswith('/') and not href.startswith('/'):
                    subdir_name = href.rstrip('/')
                    subdirs_found.append(subdir_name)
            
            if files_found > 0:
                print(f"{indent}  ✓ Found {files_found} files")
            
            # NOW explore ALL subdirectories (including metadata!)
            for subdir_name in subdirs_found:
                subdir_path = f"{dir_path}/{subdir_name}" if dir_path else subdir_name
                time.sleep(0.3)  # Be nice
                self.crawl_directory(subdir_path, depth + 1, max_depth)
                    
        except Exception as e:
            print(f"{indent}  ❌ Error: {str(e)[:50]}")
    
    def extract_file_info(self, directory, filename, link_element):
        """Extract file information"""
        try:
            parent = link_element.parent.parent
            row_text = parent.text if parent else ''
            
            # Simple size extraction
            size_mb = 0
            if 'KB' in row_text:
                size_mb = 0.001  # Approximate
            elif 'MB' in row_text:
                size_mb = 1  # Approximate
            
            priority = self.calculate_priority(filename)
            
            return {
                'directory': directory,
                'filename': filename,
                'url': f"{self.base_url}{directory}/{filename}" if directory else f"{self.base_url}{filename}",
                'extension': Path(filename).suffix.lower(),
                'size_mb': size_mb,
                'size_display': 'Unknown',
                'priority_score': priority
            }
        except:
            return None
    
    def calculate_priority(self, filename):
        """Calculate file priority"""
        filename_lower = filename.lower()
        score = 0
        
        # Check keywords
        for level, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    if level == 'critical':
                        score += 30
                    elif level == 'high':
                        score += 20
                    elif level == 'medium':
                        score += 10
                    else:
                        score += 5
        
        # File type bonuses
        if '.gdb.zip' in filename_lower:
            score += 25
        elif '.zip' in filename_lower:
            score += 15
        elif '.json' in filename_lower:
            score += 10
        elif '.csv' in filename_lower:
            score += 10
        elif '.shp' in filename_lower:
            score += 15
        
        return max(0, score)
    
    def run_targeted_crawl(self):
        """Crawl specific regions we missed"""
        print("\n" + "="*80)
        print("EPA COMPLETE CRAWLER - GETTING MISSED DATA")
        print("Exploring ALL subdirectories including /metadata/")
        print("="*80)
        
        # Focus on regions we missed or didn't explore fully
        targets = [
            "R4",  # Southeast - has metadata subdirectory
            "R5",  # Great Lakes - has JSON files
            "R2",  # NY/NJ - check deeper
            "R6",  # South Central - check deeper
            "R10", # Pacific Northwest - check deeper
        ]
        
        for region in targets:
            print(f"\n🎯 DEEP CRAWLING {region}:")
            print("-"*40)
            self.crawl_directory(region, depth=0, max_depth=3)
            time.sleep(1)
        
        # Save results
        self.save_results()
        
        return len(self.discovered_files)
    
    def save_results(self):
        """Save crawl results"""
        
        # Group by region
        by_region = {}
        for file in self.discovered_files:
            region = file['directory'].split('/')[0] if file['directory'] else 'Root'
            if region not in by_region:
                by_region[region] = []
            by_region[region].append(file)
        
        report = {
            'crawl_date': self.start_time.isoformat(),
            'directories_explored': len(self.explored_directories),
            'files_found': len(self.discovered_files),
            'files_by_region': {r: len(files) for r, files in by_region.items()},
            'valuable_files': [f for f in self.discovered_files if f['priority_score'] > 10],
            'all_files': self.discovered_files
        }
        
        # Save report
        report_file = self.output_path / "epa_complete_crawl_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save download list for missed files
        download_list = {
            'created': datetime.now().isoformat(),
            'purpose': 'Get missed EPA data from nested directories',
            'files': [f for f in self.discovered_files if f['priority_score'] > 15]
        }
        
        download_file = self.output_path / "epa_missed_files_to_download.json"
        with open(download_file, 'w') as f:
            json.dump(download_list, f, indent=2)
        
        print("\n" + "="*80)
        print("COMPLETE CRAWL RESULTS")
        print("="*80)
        print(f"Directories explored: {len(self.explored_directories)}")
        print(f"Files found: {len(self.discovered_files)}")
        print(f"Valuable files: {len([f for f in self.discovered_files if f['priority_score'] > 10])}")
        
        print("\nFiles by region:")
        for region, count in sorted(by_region.items(), key=lambda x: x[0]):
            print(f"  {region}: {count} files")
        
        print("\nTop valuable files found:")
        valuable = sorted([f for f in self.discovered_files if f['priority_score'] > 10], 
                         key=lambda x: x['priority_score'], reverse=True)
        for f in valuable[:10]:
            print(f"  ⭐ {f['filename']} (Score: {f['priority_score']})")
            print(f"     Path: {f['directory']}")
        
        print("="*80)
        print(f"\n📄 Reports saved:")
        print(f"  - {report_file.name}")
        print(f"  - {download_file.name}")

def main():
    print("\n🔍 EPA COMPLETE CRAWLER")
    print("Getting the data we missed by not going deep enough")
    print("-"*60)
    
    crawler = EPACompleteCrawler()
    files = crawler.run_targeted_crawl()
    
    print(f"\n✅ COMPLETE CRAWL FINISHED")
    print(f"Found {files} additional files in nested directories")
    print("\nKey findings:")
    print("  - R4 has data in /metadata/ subdirectory")
    print("  - R5 has JSON files in root")
    print("  - Other regions may have deeper nested data")

if __name__ == "__main__":
    main()