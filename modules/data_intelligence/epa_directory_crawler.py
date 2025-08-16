#!/usr/bin/env python3
"""
EPA Directory Crawler and Smart Downloader
Crawls EPA public data directories to find and download actual data files
WINGMAN Federal Environmental Data Mission - Phase 4
Date: 2025-08-10
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from pathlib import Path
from datetime import datetime
import re

class EPADirectoryCrawler:
    """Crawl EPA directories and download relevant environmental data"""
    
    def __init__(self):
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.output_path = self.base_path / "data_sets" / "federal"
        self.base_url = "https://edg.epa.gov/data/public/"
        
        self.discovered_files = []
        self.download_queue = []
        self.start_time = datetime.now()
        
        # Keywords to identify relevant files
        self.keywords = [
            'rcra', 'superfund', 'brownfield', 'contamina', 'hazard', 'waste',
            'toxic', 'chemical', 'pollut', 'enforce', 'compliance', 'violat',
            'cleanup', 'remediat', 'npl', 'cercl', 'underground', 'storage',
            'tank', 'ust', 'lust', 'corrective', 'action', 'emission', 'discharge',
            'water', 'air', 'soil', 'sediment', 'groundwater', 'site'
        ]
        
        # File extensions we want
        self.valid_extensions = ['.zip', '.gdb.zip', '.csv', '.json', '.gpkg', '.xlsx']
        
    def crawl_directory(self, dir_path=""):
        """Crawl a directory and find all files"""
        url = self.base_url + dir_path
        print(f"\n📁 Exploring: {dir_path if dir_path else 'root'}")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links
            links = soup.find_all('a')
            
            for link in links:
                href = link.get('href', '')
                text = link.text.strip()
                
                # Skip parent directory and metadata
                if 'Parent Directory' in text or not href:
                    continue
                
                # Check if it's a file or directory
                if any(ext in href.lower() for ext in self.valid_extensions):
                    # It's a file
                    file_info = {
                        'name': text,
                        'path': dir_path + text,
                        'url': url + text,
                        'directory': dir_path,
                        'size': self.extract_size(link.parent.parent.text),
                        'relevance': self.calculate_relevance(text)
                    }
                    
                    self.discovered_files.append(file_info)
                    print(f"  📄 Found: {text} ({file_info['size']})")
                    
                elif href.endswith('/') and not href.startswith('/'):
                    # It's a subdirectory - recursively explore
                    if 'metadata' not in href.lower():  # Skip metadata directories
                        subdir = dir_path + href
                        print(f"  📂 Subdirectory: {href}")
                        time.sleep(0.5)  # Be nice to EPA servers
                        self.crawl_directory(subdir)
                        
        except Exception as e:
            print(f"  ❌ Error crawling {dir_path}: {e}")
            
    def extract_size(self, text):
        """Extract file size from directory listing text"""
        # Look for patterns like "2.5 MB" or "15234567"
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(KB|MB|GB)', text, re.IGNORECASE)
        if size_match:
            return size_match.group(0)
        
        # Look for raw byte count
        byte_match = re.search(r'\b(\d{4,})\b', text)
        if byte_match:
            bytes_val = int(byte_match.group(1))
            if bytes_val > 1024 * 1024:
                return f"{bytes_val / (1024*1024):.1f} MB"
            elif bytes_val > 1024:
                return f"{bytes_val / 1024:.1f} KB"
            else:
                return f"{bytes_val} bytes"
        
        return "Unknown"
    
    def calculate_relevance(self, filename):
        """Calculate relevance score based on keywords"""
        filename_lower = filename.lower()
        score = 0
        
        # High priority keywords
        high_priority = ['rcra', 'superfund', 'npl', 'brownfield', 'cercl', 'contamina', 'hazard']
        for keyword in high_priority:
            if keyword in filename_lower:
                score += 10
        
        # Medium priority keywords
        for keyword in self.keywords:
            if keyword in filename_lower:
                score += 5
        
        # Bonus for certain file types
        if '.gdb.zip' in filename_lower:
            score += 3  # Geodatabases are valuable
        
        return score
    
    def prioritize_downloads(self):
        """Prioritize files for download based on relevance and size"""
        # Sort by relevance score
        self.discovered_files.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Select top files for download
        for file in self.discovered_files:
            # Skip if no relevance
            if file['relevance'] == 0:
                continue
                
            # Skip if metadata or too small
            if 'metadata' in file['name'].lower():
                continue
                
            # Add to download queue
            self.download_queue.append(file)
            
            # Limit downloads to prevent overwhelming
            if len(self.download_queue) >= 20:
                break
    
    def download_file(self, file_info):
        """Download a specific file"""
        # Determine output directory based on content
        if 'rcra' in file_info['name'].lower():
            subdir = 'EPA_RCRA'
        elif 'superfund' in file_info['name'].lower() or 'npl' in file_info['name'].lower():
            subdir = 'EPA_Superfund'
        elif 'brownfield' in file_info['name'].lower():
            subdir = 'EPA_Brownfields'
        elif file_info['directory'].startswith('R'):
            # Regional data
            region = file_info['directory'].split('/')[0]
            subdir = f'EPA_Regional/{region}'
        else:
            subdir = 'EPA_Other'
        
        output_dir = self.output_path / subdir
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / file_info['name']
        
        if output_file.exists():
            print(f"  ⚠️ Already exists: {file_info['name']}")
            return True
        
        print(f"  ⬇️ Downloading: {file_info['name']} ({file_info['size']})")
        
        try:
            response = requests.get(file_info['url'], stream=True, timeout=30)
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                actual_size = output_file.stat().st_size / (1024 * 1024)
                print(f"  ✅ Downloaded: {actual_size:.1f} MB")
                return True
            else:
                print(f"  ❌ HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def run_smart_crawl(self):
        """Execute smart crawl and download"""
        print("\n" + "="*80)
        print("EPA DIRECTORY CRAWLER - SMART ENVIRONMENTAL DATA DISCOVERY")
        print(f"Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Define directories to explore
        directories_to_crawl = [
            "",  # Root directory
            "R1/", "R2/", "R3/", "R4/", "R5/",  # Regional offices
            "R6/", "R7/", "R8/", "R9/", "R10/",
            "OLEM/",  # Land and Emergency Management
            "OECA/",  # Enforcement and Compliance
            "OW/",    # Water
            "OAR/",   # Air
            "OSWER/"  # Solid Waste and Emergency Response
        ]
        
        # Crawl each directory
        print("\n🔍 PHASE 1: DISCOVERING FILES")
        print("-"*40)
        
        for directory in directories_to_crawl:
            self.crawl_directory(directory)
            time.sleep(1)  # Be nice to EPA servers
        
        print(f"\n📊 Discovered {len(self.discovered_files)} total files")
        
        # Prioritize downloads
        print("\n🎯 PHASE 2: PRIORITIZING DOWNLOADS")
        print("-"*40)
        self.prioritize_downloads()
        print(f"Selected {len(self.download_queue)} high-priority files")
        
        # Show what we're going to download
        print("\n📋 DOWNLOAD QUEUE (Top 10):")
        for i, file in enumerate(self.download_queue[:10], 1):
            print(f"  {i}. {file['name']} (Relevance: {file['relevance']}) - {file['size']}")
        
        # Download files
        print("\n⬇️ PHASE 3: DOWNLOADING HIGH-PRIORITY FILES")
        print("-"*40)
        
        success_count = 0
        for i, file in enumerate(self.download_queue, 1):
            print(f"\n[{i}/{len(self.download_queue)}] {file['name']}")
            if self.download_file(file):
                success_count += 1
            time.sleep(3)  # Delay between downloads
        
        # Save discovery report
        self.save_discovery_report(success_count)
        
        return success_count
    
    def save_discovery_report(self, success_count):
        """Save report of discovered and downloaded files"""
        
        report = {
            'crawl_date': self.start_time.isoformat(),
            'total_discovered': len(self.discovered_files),
            'high_priority_files': len(self.download_queue),
            'successfully_downloaded': success_count,
            'discovered_files': self.discovered_files[:100],  # Save top 100
            'download_queue': self.download_queue
        }
        
        report_file = self.output_path / "epa_crawler_discovery_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Create summary
        print("\n" + "="*80)
        print("CRAWLER SUMMARY")
        print("="*80)
        print(f"Files Discovered: {len(self.discovered_files)}")
        print(f"High Priority: {len(self.download_queue)}")
        print(f"Downloaded: {success_count}")
        print(f"Success Rate: {(success_count/len(self.download_queue)*100):.1f}%" if self.download_queue else "N/A")
        
        # Show file type breakdown
        extensions = {}
        for file in self.discovered_files:
            ext = Path(file['name']).suffix.lower()
            extensions[ext] = extensions.get(ext, 0) + 1
        
        print("\nFile Types Found:")
        for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ext}: {count}")
        
        print("="*80)
        
        # Create documentation
        self.create_documentation(report)
    
    def create_documentation(self, report):
        """Create comprehensive documentation of crawl results"""
        
        readme = f"""EPA DATA CRAWLER DISCOVERY REPORT
==================================
Crawl Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Source: EPA Environmental Dataset Gateway

DISCOVERY RESULTS:
==================
Total Files Found: {report['total_discovered']}
High Priority Files: {report['high_priority_files']}
Successfully Downloaded: {report['successfully_downloaded']}

TOP DISCOVERED FILES:
=====================
"""
        
        for i, file in enumerate(report['download_queue'][:20], 1):
            readme += f"{i}. {file['name']}\n"
            readme += f"   Directory: {file['directory']}\n"
            readme += f"   Size: {file['size']}\n"
            readme += f"   Relevance Score: {file['relevance']}\n\n"
        
        readme += """
KEY FINDINGS:
=============
- EPA data is organized by regional offices (R1-R10)
- Most valuable data is in geodatabase format (.gdb.zip)
- RCRA, Superfund, and enforcement data available
- Regional variations in data availability

DOWNLOADED DATA LOCATIONS:
==========================
- EPA_Superfund/ - NPL and CERCLIS data
- EPA_RCRA/ - Hazardous waste handlers
- EPA_Brownfields/ - Redevelopment sites
- EPA_Regional/ - Regional office specific data
- EPA_Other/ - Additional environmental data

USAGE FOR LIHTC:
================
1. Check EPA_Superfund for NPL sites
2. Review EPA_RCRA for hazardous waste facilities
3. Examine regional data for local contamination
4. Use for Phase I ESA support

Generated by: Colosseum LIHTC Platform - WINGMAN Agent
Mission: Federal Environmental Data Acquisition
"""
        
        readme_file = self.output_path / "README_EPA_CRAWLER.txt"
        with open(readme_file, 'w') as f:
            f.write(readme)
        
        print(f"\n📄 Created documentation: {readme_file.name}")

def main():
    print("\n🤖 EPA SMART DIRECTORY CRAWLER")
    print("Discovering and downloading environmental datasets")
    print("-"*60)
    
    crawler = EPADirectoryCrawler()
    success_count = crawler.run_smart_crawl()
    
    print(f"\n✅ CRAWL COMPLETE")
    print(f"Successfully downloaded {success_count} priority files")
    print("Check data_sets/federal/ for downloaded data")
    print("\nFull report: epa_crawler_discovery_report.json")

if __name__ == "__main__":
    main()