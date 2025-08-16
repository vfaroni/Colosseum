#!/usr/bin/env python3
"""
Priority QAP Downloader
Download QAPs from key states with verified direct URLs from Opus research
"""

import os
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from state_qap_url_tracker import StateQAPURLTracker
import json

class PriorityQAPDownloader:
    """Download QAPs from priority states with direct URLs"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.tracker = StateQAPURLTracker(base_dir)
        self.results = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'by_state': {},
            'errors': []
        }
        
        # Priority states with verified direct PDF URLs from Opus research
        self.priority_urls = {
            'CA': [
                'https://www.treasurer.ca.gov/ctcac/2025/application.asp',  # Application page
            ],
            'FL': [
                'https://www.floridahousing.org/',  # Main site - look for QAP
            ],
            'NY': [
                'https://hcr.ny.gov/',  # Main site
            ],
            'OH': [
                'https://ohiohome.org/',  # Check for 2025 QAP
            ],
            'IL': [
                'https://www.ihda.org/',  # Check for current QAP
            ],
            'NC': [
                'https://www.nchfa.com/',  # Main site
            ],
            'GA': [
                'https://www.dca.ga.gov/',  # Main site
            ],
            'CO': [
                'https://www.chfainfo.com/',  # Main site
            ],
            'WA': [
                'https://www.wshfc.org/',  # Main site
            ],
            'OR': [
                'https://www.oregon.gov/ohcs/',  # Main site
            ]
        }
        
        # Known direct PDF URLs that should work
        self.direct_pdf_urls = {
            'CA': [
                'https://www.treasurer.ca.gov/ctcac/2025/Dec11/20241211-qap-regulations-final.pdf',
            ],
            'TX': [
                # These already worked, but keeping for reference
                'https://www.tdhca.texas.gov/sites/default/files/multifamily/docs/25-QAP.pdf',
                'https://www.tdhca.texas.gov/sites/default/files/multifamily/docs/25-QAP-bl.pdf',
            ],
            'FL': [
                'https://www.floridahousing.org/docs/default-source/multifamily/2024-universal-application-package/2024-qap.pdf',
            ],
            'OH': [
                'https://ohiohome.org/static/20231027-2024-9-lihtc-qap-final-with-amendment.pdf',
            ]
        }
    
    def download_file(self, url: str, save_path: Path, timeout: int = 30) -> dict:
        """Download a single file with enhanced error handling"""
        result = {
            'success': False,
            'file_size': 0,
            'md5_hash': None,
            'error': None,
            'response_code': None,
            'content_type': None
        }
        
        try:
            # Enhanced headers to appear more like a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            
            # Make request with longer timeout and allow redirects
            response = requests.get(
                url, 
                headers=headers, 
                timeout=timeout, 
                stream=True,
                allow_redirects=True,
                verify=True
            )
            
            result['response_code'] = response.status_code
            result['content_type'] = response.headers.get('content-type', '')
            
            print(f"    📡 Response: {response.status_code} - {result['content_type']}")
            
            if response.status_code == 200:
                # Check if it's actually a PDF
                if 'pdf' in result['content_type'].lower():
                    # Download PDF file
                    content = b''
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            content += chunk
                    
                    # Validate PDF content
                    if content.startswith(b'%PDF'):
                        # Create directory if needed
                        save_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Save file
                        with open(save_path, 'wb') as f:
                            f.write(content)
                        
                        # Calculate metadata
                        result['file_size'] = len(content)
                        result['md5_hash'] = hashlib.md5(content).hexdigest()
                        result['success'] = True
                        
                        print(f"    ✅ PDF downloaded: {result['file_size']:,} bytes")
                    else:
                        result['error'] = "Downloaded file is not a valid PDF"
                        print(f"    ❌ Not a valid PDF - starts with: {content[:20]}")
                
                elif 'html' in result['content_type'].lower():
                    # It's an HTML page - save it for potential PDF link extraction
                    content = response.text
                    
                    # Look for PDF links in the HTML
                    import re
                    pdf_links = re.findall(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', content, re.IGNORECASE)
                    
                    if pdf_links:
                        print(f"    🔗 Found {len(pdf_links)} PDF links in HTML")
                        result['error'] = f"HTML page with PDF links found: {pdf_links[:3]}"  # Show first 3
                    else:
                        result['error'] = "HTML page returned, no direct PDF links found"
                        
                else:
                    result['error'] = f"Unexpected content type: {result['content_type']}"
                    
            else:
                result['error'] = f"HTTP {response.status_code}: {response.reason}"
                
        except requests.exceptions.Timeout:
            result['error'] = "Download timeout (30s)"
        except requests.exceptions.ConnectionError:
            result['error'] = "Connection error"
        except requests.exceptions.SSLError:
            result['error'] = "SSL certificate error"
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
        
        return result
    
    def download_priority_qaps(self, max_files: int = None):
        """Download QAPs from priority states"""
        print("🎯 Downloading QAPs from Priority States...")
        
        all_urls = []
        
        # Add direct PDF URLs first (highest success probability)
        for state_code, urls in self.direct_pdf_urls.items():
            for url in urls:
                all_urls.append((state_code, url, 'direct_pdf'))
        
        # Add other URLs from our tracking database
        for record_key, record in self.tracker.qap_records.items():
            if record.document_type == 'current' and record.download_status != 'downloaded':
                all_urls.append((record.state_code, record.url, 'tracked'))
        
        if max_files:
            all_urls = all_urls[:max_files]
        
        print(f"📋 Attempting to download {len(all_urls)} QAP documents...")
        
        for i, (state_code, url, source_type) in enumerate(all_urls, 1):
            print(f"\n📥 [{i}/{len(all_urls)}] {state_code} ({source_type})")
            print(f"    URL: {url}")
            
            # Determine save path
            state_dir = self.base_dir / "QAP" / state_code / "current"
            filename = self.get_filename_from_url(url, state_code)
            save_path = state_dir / filename
            
            # Skip if already exists
            if save_path.exists():
                print(f"    📁 Already exists: {save_path.name}")
                continue
            
            # Attempt download
            self.results['attempted'] += 1
            result = self.download_file(url, save_path)
            
            if result['success']:
                self.results['successful'] += 1
                self.results['by_state'][state_code] = self.results['by_state'].get(state_code, 0) + 1
                
                # Update tracker if this was a tracked URL
                if source_type == 'tracked':
                    # Find the record key and update it
                    for key, record in self.tracker.qap_records.items():
                        if record.url == url:
                            self.tracker.update_url_status(key, 'downloaded', result['md5_hash'])
                            break
                
            else:
                self.results['failed'] += 1
                self.results['errors'].append({
                    'state': state_code,
                    'url': url,
                    'error': result['error'],
                    'http_code': result['response_code'],
                    'content_type': result['content_type']
                })
            
            # Be respectful with delays
            time.sleep(2)
    
    def get_filename_from_url(self, url: str, state_code: str) -> str:
        """Generate appropriate filename from URL"""
        try:
            from urllib.parse import urlparse, unquote
            parsed = urlparse(url)
            path = unquote(parsed.path)
            
            # Get original filename if available
            if path.endswith('.pdf'):
                filename = Path(path).name
                # Add state prefix if not present
                if not filename.startswith(state_code):
                    filename = f"{state_code}_{filename}"
            else:
                # Generate descriptive filename
                timestamp = datetime.now().strftime('%Y%m%d')
                filename = f"{state_code}_QAP_{timestamp}.pdf"
                
            return filename
            
        except Exception as e:
            # Fallback filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return f"{state_code}_QAP_{timestamp}.pdf"
    
    def generate_download_report(self) -> str:
        """Generate comprehensive download report"""
        report = f"""
=== PRIORITY QAP DOWNLOAD REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL RESULTS:
- Total Attempted: {self.results['attempted']}
- Successful Downloads: {self.results['successful']}
- Failed Downloads: {self.results['failed']}
- Success Rate: {(self.results['successful']/max(1, self.results['attempted'])*100):.1f}%

SUCCESSFUL DOWNLOADS BY STATE:
"""
        
        for state, count in sorted(self.results['by_state'].items()):
            report += f"- {state}: {count} files\n"
        
        if self.results['errors']:
            report += f"""
DOWNLOAD FAILURES:
"""
            for error in self.results['errors']:
                report += f"- {error['state']}: {error['error']}\n"
                report += f"  HTTP: {error['http_code']} | Content: {error['content_type']}\n"
                if 'PDF links found' in error['error']:
                    report += f"  🔗 Action: Extract PDF URLs from HTML page\n"
                report += f"  URL: {error['url']}\n\n"
        
        report += f"""
RECOMMENDATIONS:
1. Process successful downloads through PDF chunking system
2. For HTML pages with PDF links, extract direct PDF URLs manually
3. Try alternative sources for failed states (state websites, archives)
4. Consider web scraping for states with complex navigation

NEXT STEPS:
1. Run PDF processor on new downloads
2. Update RAG indexes with new content
3. Add more direct PDF URLs from state websites
"""
        
        return report

def main():
    """Download QAPs from priority states with verified URLs"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    
    print("🚀 Starting Priority QAP Downloads...")
    
    downloader = PriorityQAPDownloader(base_dir)
    
    # Download from priority states
    downloader.download_priority_qaps(max_files=15)  # Limit for testing
    
    # Generate and display report
    report = downloader.generate_download_report()
    print(report)
    
    # Save report
    report_file = Path(base_dir) / "QAP" / "_cache" / f"priority_download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"💾 Report saved to: {report_file}")

if __name__ == "__main__":
    main()