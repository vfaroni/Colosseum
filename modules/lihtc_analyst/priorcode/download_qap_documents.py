#!/usr/bin/env python3
"""
Download QAP Documents Using Populated URL Database
Downloads current QAP documents from the Opus research URLs
"""

import os
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from state_qap_url_tracker import StateQAPURLTracker
import json

class QAPDocumentDownloader:
    """Download QAP documents from populated URL database"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.tracker = StateQAPURLTracker(base_dir)
        self.results = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'by_state': {},
            'by_type': {},
            'errors': []
        }
        
    def create_download_directories(self):
        """Create organized directory structure for downloads"""
        states_processed = set()
        
        for record in self.tracker.qap_records.values():
            if record.state_code not in states_processed:
                state_dir = self.base_dir / "QAP" / record.state_code
                
                # Create subdirectories
                (state_dir / "current").mkdir(parents=True, exist_ok=True)
                (state_dir / "archive").mkdir(parents=True, exist_ok=True)
                (state_dir / "applications").mkdir(parents=True, exist_ok=True)
                (state_dir / "awards").mkdir(parents=True, exist_ok=True)
                (state_dir / "notices").mkdir(parents=True, exist_ok=True)
                
                states_processed.add(record.state_code)
                
        print(f"✅ Created directories for {len(states_processed)} states")
    
    def get_filename_from_url(self, url: str, state_code: str, doc_type: str) -> str:
        """Generate appropriate filename from URL"""
        try:
            # Parse URL to get filename
            from urllib.parse import urlparse, unquote
            parsed = urlparse(url)
            path = unquote(parsed.path)
            
            # Get original filename if available
            if path.endswith('.pdf'):
                filename = Path(path).name
            else:
                # Generate descriptive filename
                timestamp = datetime.now().strftime('%Y%m%d')
                filename = f"{state_code}_{doc_type}_{timestamp}.pdf"
                
            return filename
            
        except Exception as e:
            # Fallback filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return f"{state_code}_{doc_type}_{timestamp}.pdf"
    
    def download_file(self, url: str, save_path: Path, timeout: int = 30) -> dict:
        """Download a single file with error handling"""
        result = {
            'success': False,
            'file_size': 0,
            'md5_hash': None,
            'error': None,
            'response_code': None
        }
        
        try:
            # Add headers to appear like a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/pdf,application/octet-stream,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Make request with timeout
            response = requests.get(url, headers=headers, timeout=timeout, stream=True)
            result['response_code'] = response.status_code
            
            if response.status_code == 200:
                # Create directory if needed
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Download file
                content = b''
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        content += chunk
                
                # Save file
                with open(save_path, 'wb') as f:
                    f.write(content)
                
                # Calculate metadata
                result['file_size'] = len(content)
                result['md5_hash'] = hashlib.md5(content).hexdigest()
                result['success'] = True
                
            else:
                result['error'] = f"HTTP {response.status_code}: {response.reason}"
                
        except requests.exceptions.Timeout:
            result['error'] = "Download timeout"
        except requests.exceptions.ConnectionError:
            result['error'] = "Connection error"
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def download_qap_documents(self, doc_types: list = None, max_files: int = None):
        """Download QAP documents by type"""
        if doc_types is None:
            doc_types = ['current']  # Focus on current QAPs first
        
        # Filter records by document type
        target_records = [
            (key, record) for key, record in self.tracker.qap_records.items()
            if record.document_type in doc_types and record.download_status != 'downloaded'
        ]
        
        if max_files:
            target_records = target_records[:max_files]
        
        print(f"🎯 Targeting {len(target_records)} documents of types: {doc_types}")
        
        # Create directories
        self.create_download_directories()
        
        # Download each file
        for i, (key, record) in enumerate(target_records, 1):
            print(f"\n📥 [{i}/{len(target_records)}] Downloading: {record.state_code} - {record.title}")
            print(f"    URL: {record.url}")
            
            # Determine save path
            type_dir = "current" if record.document_type == "current" else record.document_type
            state_dir = self.base_dir / "QAP" / record.state_code / type_dir
            filename = self.get_filename_from_url(record.url, record.state_code, record.document_type)
            save_path = state_dir / filename
            
            # Attempt download
            self.results['attempted'] += 1
            
            result = self.download_file(record.url, save_path)
            
            if result['success']:
                print(f"    ✅ Success: {result['file_size']:,} bytes ({result['file_size']/1024/1024:.1f} MB)")
                
                # Update tracker
                self.tracker.update_url_status(key, 'downloaded', result['md5_hash'])
                
                self.results['successful'] += 1
                self.results['by_state'][record.state_code] = self.results['by_state'].get(record.state_code, 0) + 1
                self.results['by_type'][record.document_type] = self.results['by_type'].get(record.document_type, 0) + 1
                
            else:
                print(f"    ❌ Failed: {result['error']} (HTTP {result['response_code']})")
                
                # Update tracker
                self.tracker.update_url_status(key, 'failed')
                
                self.results['failed'] += 1
                self.results['errors'].append({
                    'state': record.state_code,
                    'url': record.url,
                    'error': result['error'],
                    'http_code': result['response_code']
                })
            
            # Small delay to be respectful
            time.sleep(1)
        
        return self.results
    
    def generate_download_report(self) -> str:
        """Generate comprehensive download report"""
        report = f"""
=== QAP DOWNLOAD REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL RESULTS:
- Total Attempted: {self.results['attempted']}
- Successful Downloads: {self.results['successful']}
- Failed Downloads: {self.results['failed']}
- Success Rate: {(self.results['successful']/self.results['attempted']*100):.1f}% if self.results['attempted'] > 0 else 0%

DOWNLOADS BY STATE:
"""
        
        for state, count in sorted(self.results['by_state'].items()):
            report += f"- {state}: {count} files\n"
        
        report += f"""
DOWNLOADS BY TYPE:
"""
        for doc_type, count in sorted(self.results['by_type'].items()):
            report += f"- {doc_type}: {count} files\n"
        
        if self.results['errors']:
            report += f"""
ERRORS ENCOUNTERED:
"""
            for error in self.results['errors']:
                report += f"- {error['state']}: {error['error']} (HTTP {error['http_code']})\n"
                report += f"  URL: {error['url']}\n"
        
        report += f"""
NEXT STEPS:
1. Review failed downloads and update URLs if needed
2. Retry failed downloads with updated URLs
3. Proceed to PDF processing for successful downloads
"""
        
        return report

def main():
    """Download QAP documents from populated URL database"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    
    print("📥 Starting QAP Document Downloads...")
    
    downloader = QAPDocumentDownloader(base_dir)
    
    # Focus on current QAP documents first (most important)
    print("🎯 Downloading current QAP documents...")
    results = downloader.download_qap_documents(
        doc_types=['current'], 
        max_files=20  # Start with top 20 to test
    )
    
    # Generate and display report
    report = downloader.generate_download_report()
    print(report)
    
    # Save report to file
    report_file = Path(base_dir) / "QAP" / "_cache" / f"download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"💾 Report saved to: {report_file}")
    
    print("🎯 TASK IN PROGRESS: Download current QAP documents from populated URLs")

if __name__ == "__main__":
    main()