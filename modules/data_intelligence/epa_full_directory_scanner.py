#!/usr/bin/env python3
"""
EPA Full Directory Scanner
Systematically explores ALL EPA directories and identifies environmental datasets
WINGMAN Federal Environmental Data Mission - Comprehensive Scan
Date: 2025-08-10
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from pathlib import Path
from datetime import datetime
import re

class EPAFullScanner:
    """Comprehensive EPA directory scanner"""
    
    def __init__(self):
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.output_path = self.base_path / "data_sets" / "federal"
        self.base_url = "https://edg.epa.gov/data/public/"
        
        self.all_files = []
        self.valuable_files = []
        self.start_time = datetime.now()
        
        # All directories from EPA site
        self.all_directories = [
            "Extramural_Research", "FOIA", "OA", "OAR", "OARM", "OCFO", "OCSPP",
            "OECA", "OEI", "OGC", "OIG", "OITA", "OLEM", "OP", "ORD", "OW",
            "R1", "R10", "R2", "R3", "R3-CBP", "R4", "R5", "R6", "R7", "R8", "R9"
        ]
        
        # Priority keywords for environmental data
        self.priority_keywords = [
            'rcra', 'superfund', 'npl', 'cercla', 'cerclis', 'brownfield',
            'contamina', 'hazard', 'waste', 'toxic', 'chemical', 'pollut',
            'enforce', 'compliance', 'violation', 'cleanup', 'remediat',
            'underground', 'storage', 'tank', 'ust', 'lust', 'corrective',
            'emission', 'discharge', 'water', 'air', 'soil', 'sediment',
            'groundwater', 'site', 'facility', 'permit', 'spill', 'release'
        ]
        
    def scan_directory(self, directory):
        """Scan a single directory for files"""
        url = f"{self.base_url}{directory}/"
        files_found = []
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return files_found
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse directory listing
            for link in soup.find_all('a'):
                href = link.get('href', '')
                text = link.text.strip()
                
                # Skip parent directory
                if 'Parent Directory' in text or not href:
                    continue
                
                # Check for files with extensions
                if '.' in href and not href.endswith('/'):
                    # Extract file info from the row
                    parent = link.parent.parent
                    size_text = parent.text if parent else ''
                    
                    file_info = {
                        'directory': directory,
                        'filename': text,
                        'url': f"{url}{text}",
                        'size': self.extract_size(size_text),
                        'extension': Path(text).suffix.lower(),
                        'relevance': self.calculate_relevance(text)
                    }
                    
                    files_found.append(file_info)
                    
                # Check for subdirectories
                elif href.endswith('/') and not href.startswith('/'):
                    # Recursively scan subdirectories (limited depth)
                    if 'metadata' not in href.lower():
                        subdir = f"{directory}/{href.rstrip('/')}"
                        print(f"    📂 Found subdirectory: {subdir}")
                        time.sleep(0.5)
                        sub_files = self.scan_directory(subdir)
                        files_found.extend(sub_files)
                        
        except Exception as e:
            print(f"    ❌ Error scanning {directory}: {e}")
            
        return files_found
    
    def extract_size(self, text):
        """Extract file size from text"""
        # Look for size patterns
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(KB|MB|GB)', text, re.IGNORECASE)
        if size_match:
            size_val = float(size_match.group(1))
            unit = size_match.group(2).upper()
            
            # Convert to MB for comparison
            if unit == 'KB':
                mb_size = size_val / 1024
            elif unit == 'GB':
                mb_size = size_val * 1024
            else:
                mb_size = size_val
                
            return {'display': size_match.group(0), 'mb': mb_size}
        
        # Check for raw byte count
        byte_match = re.search(r'\b(\d{6,})\b', text)
        if byte_match:
            bytes_val = int(byte_match.group(1))
            mb_size = bytes_val / (1024 * 1024)
            
            if mb_size > 1024:
                return {'display': f"{mb_size/1024:.1f} GB", 'mb': mb_size}
            elif mb_size > 1:
                return {'display': f"{mb_size:.1f} MB", 'mb': mb_size}
            else:
                return {'display': f"{bytes_val} bytes", 'mb': mb_size}
        
        return {'display': 'Unknown', 'mb': 0}
    
    def calculate_relevance(self, filename):
        """Calculate relevance score"""
        filename_lower = filename.lower()
        score = 0
        
        # Check for priority keywords
        for keyword in self.priority_keywords:
            if keyword in filename_lower:
                score += 10
        
        # Bonus for valuable extensions
        if filename_lower.endswith('.gdb.zip'):
            score += 20  # Geodatabases are very valuable
        elif filename_lower.endswith('.zip'):
            score += 10
        elif filename_lower.endswith('.csv'):
            score += 5
        elif filename_lower.endswith('.json'):
            score += 5
        
        # Penalty for common non-data files
        if 'metadata' in filename_lower or 'readme' in filename_lower:
            score -= 5
        if filename_lower.endswith('.xml'):
            score -= 3  # Usually metadata
            
        return score
    
    def run_comprehensive_scan(self):
        """Scan all EPA directories"""
        print("\n" + "="*80)
        print("EPA COMPREHENSIVE DIRECTORY SCAN")
        print(f"Scanning {len(self.all_directories)} directories")
        print(f"Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Scan each directory
        for i, directory in enumerate(self.all_directories, 1):
            print(f"\n[{i}/{len(self.all_directories)}] Scanning: {directory}/")
            print("-"*40)
            
            files = self.scan_directory(directory)
            self.all_files.extend(files)
            
            if files:
                print(f"  ✅ Found {len(files)} files")
                # Show top files by relevance
                top_files = sorted(files, key=lambda x: x['relevance'], reverse=True)[:3]
                for f in top_files:
                    if f['relevance'] > 0:
                        print(f"    📄 {f['filename']} (Score: {f['relevance']}, Size: {f['size']['display']})")
            else:
                print(f"  ⚠️ No files found")
            
            time.sleep(1)  # Be nice to EPA servers
        
        # Identify most valuable files
        self.identify_valuable_files()
        
        # Save results
        self.save_scan_results()
        
        return len(self.valuable_files)
    
    def identify_valuable_files(self):
        """Identify the most valuable files for download"""
        # Filter files with positive relevance and reasonable size
        self.valuable_files = [
            f for f in self.all_files 
            if f['relevance'] > 5 and f['size']['mb'] > 0.01  # Skip tiny metadata files
        ]
        
        # Sort by relevance
        self.valuable_files.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Limit to top 50 to avoid overwhelming
        self.valuable_files = self.valuable_files[:50]
    
    def save_scan_results(self):
        """Save comprehensive scan results"""
        
        # Group files by directory
        by_directory = {}
        for f in self.all_files:
            dir_name = f['directory']
            if dir_name not in by_directory:
                by_directory[dir_name] = []
            by_directory[dir_name].append(f)
        
        # Calculate statistics
        total_size_mb = sum(f['size']['mb'] for f in self.all_files)
        valuable_size_mb = sum(f['size']['mb'] for f in self.valuable_files)
        
        report = {
            'scan_date': self.start_time.isoformat(),
            'directories_scanned': len(self.all_directories),
            'total_files_found': len(self.all_files),
            'valuable_files_identified': len(self.valuable_files),
            'total_size_mb': round(total_size_mb, 1),
            'valuable_size_mb': round(valuable_size_mb, 1),
            'files_by_directory': {
                dir: len(files) for dir, files in by_directory.items()
            },
            'top_valuable_files': self.valuable_files[:20],
            'all_files_sample': self.all_files[:100]  # Save sample for reference
        }
        
        # Save JSON report
        report_file = self.output_path / "epa_comprehensive_scan_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*80)
        print("SCAN COMPLETE - SUMMARY")
        print("="*80)
        print(f"Directories Scanned: {len(self.all_directories)}")
        print(f"Total Files Found: {len(self.all_files)}")
        print(f"Valuable Files: {len(self.valuable_files)}")
        print(f"Total Data Size: {total_size_mb:.1f} MB")
        print(f"Valuable Data Size: {valuable_size_mb:.1f} MB")
        
        print("\n📊 Files by Directory:")
        for dir, count in sorted(by_directory.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {dir}: {count} files")
        
        print("\n🎯 Top 10 Most Valuable Files:")
        for i, f in enumerate(self.valuable_files[:10], 1):
            print(f"  {i}. {f['filename']}")
            print(f"     Directory: {f['directory']}")
            print(f"     Size: {f['size']['display']}")
            print(f"     Relevance: {f['relevance']}")
        
        print("="*80)
        
        # Create download script
        self.create_download_script()
    
    def create_download_script(self):
        """Create a script to download the valuable files"""
        
        script = f"""#!/usr/bin/env python3
# EPA Valuable Files Download Script
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
# Files to download: {len(self.valuable_files)}

import requests
import time
from pathlib import Path

base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
output_base = base_path / "data_sets" / "federal"

valuable_files = {json.dumps(self.valuable_files[:20], indent=2)}

def download_file(file_info):
    output_dir = output_base / "EPA_Data" / file_info['directory']
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / file_info['filename']
    
    if output_file.exists():
        print(f"Skipping existing: {{file_info['filename']}}")
        return True
    
    print(f"Downloading: {{file_info['filename']}} ({{file_info['size']['display']}})")
    
    try:
        response = requests.get(file_info['url'], stream=True, timeout=60)
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
            print(f"  ✅ Success")
            return True
    except Exception as e:
        print(f"  ❌ Error: {{e}}")
    
    return False

# Download files
success = 0
for i, file in enumerate(valuable_files, 1):
    print(f"\\n[{{i}}/{{len(valuable_files)}}]")
    if download_file(file):
        success += 1
    time.sleep(3)  # Be nice to EPA

print(f"\\n✅ Downloaded {{success}} of {{len(valuable_files)}} files")
"""
        
        script_file = self.output_path / "download_valuable_epa_files.py"
        with open(script_file, 'w') as f:
            f.write(script)
        
        print(f"\n📝 Download script created: {script_file.name}")
        print(f"   Run it to download the {len(self.valuable_files)} most valuable files")

def main():
    print("\n🔍 EPA COMPREHENSIVE DIRECTORY SCANNER")
    print("Scanning ALL EPA directories for environmental data")
    print("-"*60)
    
    scanner = EPAFullScanner()
    valuable_count = scanner.run_comprehensive_scan()
    
    print(f"\n✅ SCAN COMPLETE")
    print(f"Identified {valuable_count} valuable environmental datasets")
    print("\nReports saved:")
    print("  - epa_comprehensive_scan_report.json")
    print("  - download_valuable_epa_files.py")

if __name__ == "__main__":
    main()