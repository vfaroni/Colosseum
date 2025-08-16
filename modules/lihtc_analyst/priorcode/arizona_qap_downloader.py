#!/usr/bin/env python3
"""
Arizona QAP Downloader
Download Arizona QAPs using verified URLs from web search
"""

import os
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
import json

class ArizonaQAPDownloader:
    """Download Arizona QAPs using verified working URLs"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.results = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'by_state': {},
            'errors': []
        }
        
        # Verified working URLs from web search
        self.arizona_urls = {
            'AZ_2024_2025_FINAL': {
                'url': 'https://housing.az.gov/sites/default/files/2024-10/2024-2025%20QAP%20Amended%20-%20Second%20Draft%20.pdf',
                'title': 'AZ 2024-2025 QAP Amended Second Draft',
                'description': 'Arizona 2024-2025 QAP Final Amended Version'
            },
            'AZ_2024_2025_REDLINED': {
                'url': 'https://housing.az.gov/sites/default/files/documents/files/Final-Second-Draft-QAP-2024-2025-Redlined.pdf',
                'title': 'AZ 2024-2025 QAP Redlined',
                'description': 'Arizona 2024-2025 QAP with changes marked'
            }
        }
    
    def download_file(self, url: str, save_path: Path, timeout: int = 45) -> dict:
        """Download a single file with comprehensive error handling"""
        result = {
            'success': False,
            'file_size': 0,
            'md5_hash': None,
            'error': None,
            'response_code': None,
            'content_type': None,
            'final_url': url
        }
        
        try:
            # Headers optimized for Arizona state website
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/pdf,application/octet-stream,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'no-cache'
            }
            
            # Make request with longer timeout for large PDFs
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
            result['final_url'] = response.url
            
            print(f"    📡 {response.status_code} | {result['content_type']}")
            
            if response.status_code == 200:
                # Download content with progress tracking
                content = b''
                content_length = response.headers.get('content-length')
                if content_length:
                    total_size = int(content_length)
                    print(f"    📊 Expected size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
                
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        content += chunk
                        downloaded += len(chunk)
                        
                        # Progress indicator for large files
                        if downloaded % (512*1024) == 0:  # Every 512KB
                            progress = (downloaded / total_size * 100) if content_length else 0
                            size_mb = downloaded / 1024 / 1024
                            if content_length:
                                print(f"    📥 Progress: {progress:.1f}% ({size_mb:.1f} MB)")
                            else:
                                print(f"    📥 Downloaded: {size_mb:.1f} MB")
                
                # Validate content
                if content.startswith(b'%PDF'):
                    # Valid PDF
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(save_path, 'wb') as f:
                        f.write(content)
                    
                    result['file_size'] = len(content)
                    result['md5_hash'] = hashlib.md5(content).hexdigest()
                    result['success'] = True
                    
                    print(f"    ✅ {result['file_size']:,} bytes ({result['file_size']/1024/1024:.1f} MB)")
                    
                elif b'<html' in content[:500].lower():
                    # Got HTML page instead of PDF
                    result['error'] = "HTML page returned instead of PDF - document may have moved"
                    print(f"    🌐 HTML page returned - URL may redirect to landing page")
                    
                else:
                    result['error'] = f"Invalid content format (starts with: {content[:20]})"
                    print(f"    ❌ Invalid format")
                    
            elif response.status_code == 403:
                result['error'] = "Access forbidden (403) - site blocking access"
                print(f"    🚫 Access denied")
            elif response.status_code == 404:
                result['error'] = "Document not found (404) - URL may be outdated"
                print(f"    🔍 File not found")
            else:
                result['error'] = f"HTTP {response.status_code}: {response.reason}"
                print(f"    ❌ HTTP error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            result['error'] = f"Timeout ({timeout}s)"
            print(f"    ⏱️  Download timeout")
        except requests.exceptions.ConnectionError:
            result['error'] = "Connection error"
            print(f"    🔌 Connection failed")
        except requests.exceptions.SSLError:
            result['error'] = "SSL certificate error"
            print(f"    🔒 SSL issue")
        except Exception as e:
            result['error'] = f"Error: {str(e)}"
            print(f"    💥 Unexpected error: {e}")
        
        return result
    
    def download_arizona_qaps(self):
        """Download Arizona QAP documents"""
        print(f"🌵 Downloading Arizona QAP Documents...")
        print(f"📋 Attempting {len(self.arizona_urls)} documents...")
        
        for i, (doc_id, doc_info) in enumerate(self.arizona_urls.items(), 1):
            state_code = 'AZ'
            url = doc_info['url']
            title = doc_info['title']
            
            print(f"\n[{i}/{len(self.arizona_urls)}] {title}")
            print(f"    URL: {url}")
            
            # Determine save path
            state_dir = self.base_dir / "QAP" / state_code / "current"
            filename = self.get_filename_from_doc_id(doc_id, title)
            save_path = state_dir / filename
            
            # Skip if already exists
            if save_path.exists():
                print(f"    📁 Already exists: {filename}")
                continue
            
            # Attempt download
            self.results['attempted'] += 1
            result = self.download_file(url, save_path)
            
            if result['success']:
                self.results['successful'] += 1
                self.results['by_state'][state_code] = self.results['by_state'].get(state_code, 0) + 1
                
            else:
                self.results['failed'] += 1
                self.results['errors'].append({
                    'doc_id': doc_id,
                    'state': state_code,
                    'title': title,
                    'url': url,
                    'error': result['error'],
                    'http_code': result['response_code'],
                    'final_url': result['final_url']
                })
            
            # Respectful delay between requests
            time.sleep(3)
    
    def get_filename_from_doc_id(self, doc_id: str, title: str) -> str:
        """Generate appropriate filename"""
        import re
        clean_title = re.sub(r'[^\w\s\-\.]', '', title)
        clean_title = re.sub(r'\s+', '_', clean_title)
        
        if not clean_title.endswith('.pdf'):
            clean_title += '.pdf'
        
        return clean_title
    
    def generate_download_report(self) -> str:
        """Generate download report"""
        report = f"""
=== ARIZONA QAP DOWNLOAD REPORT ===
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
                report += f"- {error['title']}\n"
                report += f"  Error: {error['error']} (HTTP {error['http_code']})\n"
                if error['final_url'] != error['url']:
                    report += f"  Redirected to: {error['final_url']}\n"
                report += f"  Original URL: {error['url']}\n\n"
        
        if self.results['successful'] > 0:
            report += f"""
SUCCESS! Arizona QAPs downloaded successfully.

NEXT STEPS:
1. Process Arizona QAPs through PDF chunking system
2. Update RAG indexes to include Arizona content
3. Test 5-state RAG system (CA, TX, HI, NM, AZ)
4. Expand to additional priority states

ARIZONA FILES READY FOR PROCESSING:
"""
            # List downloaded files
            state_dir = self.base_dir / "QAP" / "AZ" / "current"
            if state_dir.exists():
                for pdf_file in state_dir.glob("*.pdf"):
                    report += f"- AZ: {pdf_file.name} ({pdf_file.stat().st_size:,} bytes)\n"
        
        return report

def main():
    """Download Arizona QAP documents"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    
    print("🚀 Starting Arizona QAP Downloads...")
    
    downloader = ArizonaQAPDownloader(base_dir)
    
    # Download Arizona QAPs
    downloader.download_arizona_qaps()
    
    # Generate and display report
    report = downloader.generate_download_report()
    print(report)
    
    # Save report
    report_file = Path(base_dir) / "QAP" / "_cache" / f"arizona_download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"💾 Report saved to: {report_file}")
    
    if downloader.results['successful'] > 0:
        print(f"🎯 Success! {downloader.results['successful']} Arizona QAP documents downloaded!")
        print("📊 Ready to process through PDF chunking system!")

if __name__ == "__main__":
    main()