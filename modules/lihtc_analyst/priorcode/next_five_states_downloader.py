#!/usr/bin/env python3
"""
Next Five States QAP Downloader
Target high-priority states: Florida, Ohio, Illinois, North Carolina, Colorado
"""

import os
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
import json

class NextFiveStatesDownloader:
    """Download QAPs from the next 5 priority states"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.results = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'by_state': {},
            'errors': []
        }
        
        # Next 5 priority states with verified URLs from Opus research
        self.target_states = {
            # Florida - Large LIHTC market
            'FL_2024': {
                'url': 'https://www.floridahousing.org/docs/default-source/multifamily/2024-universal-application-package/2024-qap.pdf',
                'title': 'FL 2024 QAP',
                'description': 'Florida 2024 QAP'
            },
            
            # Ohio - Good track record from Opus research
            'OH_2025': {
                'url': 'https://ohiohome.org/static/20241031-2025-9-lihtc-qap-final.pdf',
                'title': 'OH 2025 9% LIHTC QAP Final',
                'description': 'Ohio 2025 9% QAP Final'
            },
            'OH_2024': {
                'url': 'https://ohiohome.org/static/20231027-2024-9-lihtc-qap-final-with-amendment.pdf',
                'title': 'OH 2024 9% LIHTC QAP Final',
                'description': 'Ohio 2024 9% QAP Final with Amendment'
            },
            
            # Illinois - Major market
            'IL_2026': {
                'url': 'https://www.ihda.org/documents/2026-qualified-allocation-plan/',
                'title': 'IL 2026 QAP',
                'description': 'Illinois 2026 QAP'
            },
            
            # North Carolina - Strong program
            'NC_2025': {
                'url': 'https://www.nchfa.com/rental-housing-partners/tax-credit-assistance/qap-documents',
                'title': 'NC QAP Documents',
                'description': 'North Carolina QAP Documents Page'
            },
            
            # Colorado - Good Western addition
            'CO_2025': {
                'url': 'https://www.chfainfo.com/rental-housing-development/housing-tax-credits',
                'title': 'CO Housing Tax Credits',
                'description': 'Colorado Housing Tax Credits Page'
            },
            
            # Alternative direct URLs
            'FL_ALT': {
                'url': 'https://www.floridahousing.org/docs/default-source/multifamily/universal-application-package-other-docs/2025-qap-draft.pdf',
                'title': 'FL 2025 QAP Draft',
                'description': 'Florida 2025 QAP Draft'
            },
            
            'OH_ALT': {
                'url': 'https://ohiohome.org/static/documents/multifamily/qap/2025-qap-clean.pdf',
                'title': 'OH 2025 QAP Clean',
                'description': 'Ohio 2025 QAP Clean Version'
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
            # State-specific headers for better compatibility
            if 'floridahousing.org' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.floridahousing.org/',
                }
            elif 'ohiohome.org' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://ohiohome.org/',
                }
            elif 'ihda.org' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.ihda.org/',
                }
            else:
                # Default headers
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                }
            
            # Make request
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
            if response.url != url:
                print(f"    🔄 Redirected to: {response.url}")
            
            if response.status_code == 200:
                # Download content
                content = b''
                content_length = response.headers.get('content-length')
                if content_length:
                    total_size = int(content_length)
                    print(f"    📊 Size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
                
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        content += chunk
                        downloaded += len(chunk)
                        
                        # Progress for large files
                        if downloaded % (1024*1024) == 0:  # Every MB
                            progress = (downloaded / total_size * 100) if content_length else 0
                            if content_length:
                                print(f"    📥 {progress:.0f}% downloaded")
                
                # Check content type
                if content.startswith(b'%PDF'):
                    # Valid PDF
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(save_path, 'wb') as f:
                        f.write(content)
                    
                    result['file_size'] = len(content)
                    result['md5_hash'] = hashlib.md5(content).hexdigest()
                    result['success'] = True
                    
                    print(f"    ✅ PDF saved: {result['file_size']:,} bytes")
                    
                elif b'<html' in content[:500].lower():
                    # HTML page - look for PDF links
                    content_str = content.decode('utf-8', errors='ignore')
                    import re
                    pdf_links = re.findall(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', content_str, re.IGNORECASE)
                    
                    if pdf_links:
                        result['error'] = f"HTML page with {len(pdf_links)} PDF links found"
                        print(f"    🔗 Found {len(pdf_links)} PDF links in HTML")
                        # Show first few links
                        for i, link in enumerate(pdf_links[:3]):
                            print(f"    📎 Link {i+1}: {link}")
                    else:
                        result['error'] = "HTML page returned, no PDF links found"
                        print(f"    🌐 HTML page without PDF links")
                        
                else:
                    result['error'] = f"Unknown content format"
                    print(f"    ❓ Unknown format: {content[:30]}")
                    
            else:
                result['error'] = f"HTTP {response.status_code}: {response.reason}"
                print(f"    ❌ HTTP error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            result['error'] = f"Timeout ({timeout}s)"
            print(f"    ⏱️  Timeout")
        except requests.exceptions.ConnectionError:
            result['error'] = "Connection error"
            print(f"    🔌 Connection failed")
        except Exception as e:
            result['error'] = f"Error: {str(e)}"
            print(f"    💥 Error: {e}")
        
        return result
    
    def download_next_five_states(self):
        """Download QAPs from the next 5 priority states"""
        print(f"🎯 Downloading QAPs from Next 5 Priority States...")
        print(f"📋 Target States: FL, OH, IL, NC, CO")
        print(f"📄 Attempting {len(self.target_states)} documents...")
        
        for i, (doc_id, doc_info) in enumerate(self.target_states.items(), 1):
            state_code = doc_id.split('_')[0]
            url = doc_info['url']
            title = doc_info['title']
            
            print(f"\n[{i}/{len(self.target_states)}] {title}")
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
            
            # Respectful delay
            time.sleep(2)
    
    def get_filename_from_doc_id(self, doc_id: str, title: str) -> str:
        """Generate filename from doc ID and title"""
        import re
        clean_title = re.sub(r'[^\w\s\-\.]', '', title)
        clean_title = re.sub(r'\s+', '_', clean_title)
        
        if not clean_title.endswith('.pdf'):
            clean_title += '.pdf'
        
        return clean_title
    
    def generate_download_report(self) -> str:
        """Generate comprehensive download report"""
        report = f"""
=== NEXT 5 STATES QAP DOWNLOAD REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TARGET STATES: Florida, Ohio, Illinois, North Carolina, Colorado

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
                if 'PDF links found' in error['error']:
                    report += f"  🔗 Action: Manual PDF extraction needed\n"
                report += f"  URL: {error['url']}\n\n"
        
        if self.results['successful'] > 0:
            report += f"""
SUCCESS! {self.results['successful']} new state QAPs downloaded.

NEXT STEPS:
1. Process new QAPs through PDF chunking system
2. Update RAG indexes to include new states
3. Test expanded multi-state RAG system
4. Consider adding more states to reach 15-20 total

NEW FILES READY FOR PROCESSING:
"""
            # List downloaded files by state
            for state_code in sorted(self.results['by_state'].keys()):
                state_dir = self.base_dir / "QAP" / state_code / "current"
                if state_dir.exists():
                    for pdf_file in state_dir.glob("*.pdf"):
                        report += f"- {state_code}: {pdf_file.name} ({pdf_file.stat().st_size:,} bytes)\n"
        
        return report

def main():
    """Download QAPs from the next 5 priority states"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    
    print("🚀 Starting Next 5 States QAP Downloads...")
    print("🎯 Target: FL, OH, IL, NC, CO")
    
    downloader = NextFiveStatesDownloader(base_dir)
    
    # Download from next 5 states
    downloader.download_next_five_states()
    
    # Generate and display report
    report = downloader.generate_download_report()
    print(report)
    
    # Save report
    report_file = Path(base_dir) / "QAP" / "_cache" / f"next_five_states_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"💾 Report saved to: {report_file}")
    
    if downloader.results['successful'] > 0:
        print(f"🎯 Success! Downloaded {downloader.results['successful']} QAPs from new states!")
        print("📊 Ready to process and expand to 10-state RAG system!")

if __name__ == "__main__":
    main()