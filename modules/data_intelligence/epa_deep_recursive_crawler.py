#!/usr/bin/env python3
"""
EPA Deep Recursive Crawler
Crawls ALL EPA directories to unlimited depth to find environmental data
Saves progress for resume capability
WINGMAN Federal Environmental Data Mission - Deep Discovery
Date: 2025-08-10
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from pathlib import Path
from datetime import datetime
import re
import pickle

class EPADeepCrawler:
    """Deep recursive crawler for EPA data repository"""
    
    def __init__(self, resume=False):
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.output_path = self.base_path / "data_sets" / "federal"
        self.base_url = "https://edg.epa.gov/data/public/"
        
        # State management for resume capability
        self.state_file = self.output_path / "crawler_state.pkl"
        self.progress_file = self.output_path / "crawler_progress.json"
        
        if resume and self.state_file.exists():
            self.load_state()
        else:
            self.discovered_files = []
            self.explored_directories = set()
            self.to_explore = []
            self.errors = []
            self.start_time = datetime.now()
            self.file_count = 0
            self.dir_count = 0
        
        # Environmental keywords (comprehensive)
        self.keywords = {
            'critical': ['superfund', 'npl', 'cercla', 'cerclis', 'rcra', 'hazardous', 'toxic'],
            'high': ['brownfield', 'contamina', 'cleanup', 'remediat', 'corrective', 'enforce'],
            'medium': ['ust', 'lust', 'tank', 'storage', 'underground', 'permit', 'violation'],
            'low': ['water', 'air', 'soil', 'discharge', 'emission', 'waste', 'pollut']
        }
        
    def save_state(self):
        """Save crawler state for resume capability"""
        state = {
            'discovered_files': self.discovered_files,
            'explored_directories': self.explored_directories,
            'to_explore': self.to_explore,
            'errors': self.errors,
            'start_time': self.start_time,
            'file_count': self.file_count,
            'dir_count': self.dir_count
        }
        
        with open(self.state_file, 'wb') as f:
            pickle.dump(state, f)
        
        # Also save human-readable progress
        progress = {
            'last_update': datetime.now().isoformat(),
            'directories_explored': len(self.explored_directories),
            'directories_pending': len(self.to_explore),
            'files_found': self.file_count,
            'valuable_files': len([f for f in self.discovered_files if f['priority_score'] > 10]),
            'errors': len(self.errors)
        }
        
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def load_state(self):
        """Load saved crawler state"""
        print("📂 Resuming from saved state...")
        with open(self.state_file, 'rb') as f:
            state = pickle.load(f)
        
        self.discovered_files = state['discovered_files']
        self.explored_directories = state['explored_directories']
        self.to_explore = state['to_explore']
        self.errors = state['errors']
        self.start_time = state['start_time']
        self.file_count = state['file_count']
        self.dir_count = state['dir_count']
        
        print(f"  Resumed: {len(self.explored_directories)} dirs explored, {self.file_count} files found")
    
    def crawl_directory(self, dir_path, depth=0, max_depth=10):
        """Recursively crawl a directory to any depth"""
        
        # Avoid infinite loops
        if depth > max_depth:
            print(f"    ⚠️ Max depth {max_depth} reached at {dir_path}")
            return
        
        # Skip if already explored
        if dir_path in self.explored_directories:
            return
        
        url = self.base_url + dir_path
        if not dir_path.endswith('/'):
            url += '/'
        
        # Update progress
        self.dir_count += 1
        if self.dir_count % 10 == 0:
            print(f"  📊 Progress: {self.dir_count} dirs explored, {self.file_count} files found")
            self.save_state()  # Save every 10 directories
        
        indent = "  " * depth
        print(f"{indent}📁 Exploring: {dir_path}")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                self.errors.append({'dir': dir_path, 'error': f'HTTP {response.status_code}'})
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Mark as explored
            self.explored_directories.add(dir_path)
            
            # Find all links
            for link in soup.find_all('a'):
                href = link.get('href', '')
                text = link.text.strip()
                
                # Skip parent directory
                if 'Parent Directory' in text or not href:
                    continue
                
                # Check if it's a file
                if '.' in href and not href.endswith('/'):
                    # Extract file information
                    file_info = self.extract_file_info(dir_path, text, link)
                    if file_info:
                        self.discovered_files.append(file_info)
                        self.file_count += 1
                        
                        if file_info['priority_score'] > 20:
                            print(f"{indent}  ⭐ HIGH VALUE: {text} (Score: {file_info['priority_score']}, Size: {file_info['size_display']})")
                
                # Check if it's a subdirectory
                elif href.endswith('/') and not href.startswith('/'):
                    subdir_name = href.rstrip('/')
                    
                    # Skip metadata directories
                    if 'metadata' in subdir_name.lower():
                        continue
                    
                    # Recursively explore subdirectory
                    subdir_path = f"{dir_path}/{subdir_name}" if dir_path else subdir_name
                    
                    # Add delay to be nice to EPA servers
                    time.sleep(0.5)
                    
                    # Recursive call
                    self.crawl_directory(subdir_path, depth + 1, max_depth)
                    
        except Exception as e:
            self.errors.append({'dir': dir_path, 'error': str(e)})
            print(f"{indent}  ❌ Error: {e}")
    
    def extract_file_info(self, directory, filename, link_element):
        """Extract detailed file information"""
        try:
            # Get the parent row for size info
            parent = link_element.parent.parent
            row_text = parent.text if parent else ''
            
            # Extract size
            size_info = self.extract_size(row_text)
            
            # Calculate priority score
            priority = self.calculate_priority(filename, size_info['mb'])
            
            # Skip tiny files (likely metadata)
            if size_info['mb'] < 0.01 and priority < 20:
                return None
            
            file_info = {
                'directory': directory,
                'filename': filename,
                'url': f"{self.base_url}{directory}/{filename}" if directory else f"{self.base_url}{filename}",
                'extension': Path(filename).suffix.lower(),
                'size_mb': size_info['mb'],
                'size_display': size_info['display'],
                'priority_score': priority,
                'discovered_time': datetime.now().isoformat()
            }
            
            return file_info
            
        except Exception as e:
            return None
    
    def extract_size(self, text):
        """Extract file size from directory listing"""
        # Look for size patterns
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(KB|MB|GB)', text, re.IGNORECASE)
        if size_match:
            size_val = float(size_match.group(1))
            unit = size_match.group(2).upper()
            
            # Convert to MB
            if unit == 'KB':
                mb_size = size_val / 1024
            elif unit == 'GB':
                mb_size = size_val * 1024
            else:
                mb_size = size_val
                
            return {'display': size_match.group(0), 'mb': mb_size}
        
        # Check for raw byte count
        byte_match = re.search(r'\b(\d{7,})\b', text)
        if byte_match:
            bytes_val = int(byte_match.group(1))
            mb_size = bytes_val / (1024 * 1024)
            
            if mb_size > 1024:
                return {'display': f"{mb_size/1024:.1f} GB", 'mb': mb_size}
            else:
                return {'display': f"{mb_size:.1f} MB", 'mb': mb_size}
        
        return {'display': 'Unknown', 'mb': 0}
    
    def calculate_priority(self, filename, size_mb):
        """Calculate file priority for download"""
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
        if filename_lower.endswith('.gdb.zip'):
            score += 25  # Geodatabases are gold
        elif filename_lower.endswith('.zip'):
            score += 15
        elif filename_lower.endswith('.csv'):
            score += 10
        elif filename_lower.endswith('.gpkg'):
            score += 20  # GeoPackages are valuable
        
        # Size bonus (prefer substantial files)
        if 1 < size_mb < 100:
            score += 10
        elif 100 < size_mb < 500:
            score += 5
        
        # Penalties
        if 'metadata' in filename_lower or 'readme' in filename_lower:
            score -= 10
        if filename_lower.endswith('.xml'):
            score -= 5
        
        return max(0, score)  # Don't go negative
    
    def run_deep_crawl(self):
        """Execute deep recursive crawl of EPA repository"""
        print("\n" + "="*80)
        print("EPA DEEP RECURSIVE CRAWLER")
        print("Exploring ALL directories to unlimited depth")
        print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Main EPA directories to explore
        root_directories = [
            "", # Root directory
            "OLEM",  # Land and Emergency Management (PRIORITY)
            "OECA",  # Enforcement and Compliance (PRIORITY)
            "OW",    # Water (PRIORITY)
            "OAR",   # Air and Radiation
            "OCSPP", # Chemical Safety
            "ORD",   # Research and Development
            "R1", "R2", "R3", "R3-CBP", "R4", "R5", "R6", "R7", "R8", "R9", "R10",  # Regions
            "OITA", "OIG", "OCFO", "OGC", "OARM", "OA", "OP", "OEI", "FOIA",
            "Extramural_Research"
        ]
        
        # Start crawling
        for root_dir in root_directories:
            if root_dir in self.explored_directories:
                print(f"\n⏭️ Skipping already explored: {root_dir}")
                continue
                
            print(f"\n🔍 CRAWLING ROOT: {root_dir if root_dir else 'EPA Root'}")
            print("-"*40)
            
            self.crawl_directory(root_dir, depth=0, max_depth=10)
            
            # Save state after each root directory
            self.save_state()
            
            # Brief pause between root directories
            time.sleep(2)
        
        # Final save
        self.save_state()
        
        # Generate comprehensive report
        self.generate_report()
        
        return len(self.discovered_files)
    
    def generate_report(self):
        """Generate comprehensive crawler report"""
        
        # Filter valuable files
        valuable_files = [f for f in self.discovered_files if f['priority_score'] > 10]
        valuable_files.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Calculate statistics
        total_size_mb = sum(f['size_mb'] for f in self.discovered_files)
        valuable_size_mb = sum(f['size_mb'] for f in valuable_files)
        
        # Group by directory
        by_directory = {}
        for f in self.discovered_files:
            dir_name = f['directory'].split('/')[0] if f['directory'] else 'Root'
            if dir_name not in by_directory:
                by_directory[dir_name] = {'count': 0, 'size_mb': 0}
            by_directory[dir_name]['count'] += 1
            by_directory[dir_name]['size_mb'] += f['size_mb']
        
        report = {
            'crawl_date': self.start_time.isoformat(),
            'crawl_duration_minutes': (datetime.now() - self.start_time).total_seconds() / 60,
            'directories_explored': len(self.explored_directories),
            'total_files_found': len(self.discovered_files),
            'valuable_files': len(valuable_files),
            'total_size_gb': round(total_size_mb / 1024, 2),
            'valuable_size_gb': round(valuable_size_mb / 1024, 2),
            'errors_encountered': len(self.errors),
            'files_by_root_directory': by_directory,
            'top_50_files': valuable_files[:50],
            'explored_paths': list(self.explored_directories)[:100]
        }
        
        # Save report
        report_file = self.output_path / "epa_deep_crawl_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*80)
        print("DEEP CRAWL COMPLETE")
        print("="*80)
        print(f"Duration: {report['crawl_duration_minutes']:.1f} minutes")
        print(f"Directories Explored: {len(self.explored_directories)}")
        print(f"Total Files Found: {len(self.discovered_files)}")
        print(f"Valuable Files: {len(valuable_files)}")
        print(f"Total Data Size: {report['total_size_gb']:.1f} GB")
        print(f"Errors: {len(self.errors)}")
        
        print("\n📊 Top Directories by File Count:")
        for dir_name, stats in sorted(by_directory.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
            print(f"  {dir_name}: {stats['count']} files ({stats['size_mb']:.1f} MB)")
        
        print("\n🎯 Top 10 Most Valuable Files:")
        for i, f in enumerate(valuable_files[:10], 1):
            print(f"  {i}. {f['filename']}")
            print(f"     Score: {f['priority_score']}, Size: {f['size_display']}")
            print(f"     Path: {f['directory']}")
        
        print("="*80)
        print(f"\n📄 Full report saved: {report_file.name}")
        
        # Create download list
        self.create_download_list(valuable_files[:100])
    
    def create_download_list(self, files):
        """Create prioritized download list"""
        download_list = {
            'created': datetime.now().isoformat(),
            'total_files': len(files),
            'total_size_mb': sum(f['size_mb'] for f in files),
            'files': files
        }
        
        download_file = self.output_path / "epa_priority_download_list.json"
        with open(download_file, 'w') as f:
            json.dump(download_list, f, indent=2)
        
        print(f"📥 Download list created: {download_file.name}")
        print(f"   Contains top {len(files)} files for download")

def main():
    print("\n🕷️ EPA DEEP RECURSIVE CRAWLER")
    print("This will explore ALL EPA directories recursively")
    print("Progress is saved for resume capability")
    print("-"*60)
    
    # Check if we should resume
    state_file = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/federal/crawler_state.pkl")
    resume = state_file.exists()
    
    if resume:
        print("📂 Found previous crawler state")
        print("Resuming from last position...")
    
    crawler = EPADeepCrawler(resume=resume)
    file_count = crawler.run_deep_crawl()
    
    print(f"\n✅ DEEP CRAWL COMPLETE")
    print(f"Discovered {file_count} files across EPA repository")
    print("\nNext step: Run epa_intelligent_downloader.py to download priority files")

if __name__ == "__main__":
    main()