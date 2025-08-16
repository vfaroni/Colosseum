#!/usr/bin/env python3
"""
Verified Three States QAP Downloader
Download QAPs for Illinois, North Carolina, Colorado using verified working URLs from web search
"""

import os
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
import json

class VerifiedThreeStatesDownloader:
    """Download QAPs from verified working URLs for IL, NC, CO"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.results = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'by_state': {},
            'errors': []
        }
        
        # Verified working URLs from web search results
        self.verified_urls = {
            # Illinois - IHDA 2024-2025 QAP (most current available)
            'IL_2024_2025': {
                'url': 'https://www.ihda.org/wp-content/uploads/2023/10/FINAL-QAP_2024-2025-for-website.pdf',
                'title': 'IL 2024-2025 QAP Final',
                'description': 'Illinois IHDA 2024-2025 Low Income Housing Tax Credit QAP Final'
            },
            
            # North Carolina - NCHFA 2025 QAP Final (December 2024)
            'NC_2025_FINAL': {
                'url': 'https://www.nchfa.com/sites/default/files/2024-12/2025QAP-Final.pdf',
                'title': 'NC 2025 QAP Final',
                'description': 'North Carolina Housing Finance Agency 2025 QAP Final'
            },
            'NC_2025_APPENDIX_A': {
                'url': 'https://nchfa.com/sites/default/files/2024-11/2025QAP-AppendixA-Final.pdf',
                'title': 'NC 2025 QAP Appendix A Market Study',
                'description': 'North Carolina 2025 QAP Appendix A Market Study Guidelines'
            },
            'NC_2025_APPENDIX_D': {
                'url': 'https://nchfa.com/sites/default/files/2024-11/2025QAP-AppendixD-Final.pdf',
                'title': 'NC 2025 QAP Appendix D Targeting Program',
                'description': 'North Carolina 2025 QAP Appendix D Targeting Program'
            },
            
            # Colorado - CHFA 2025-2026 QAP
            'CO_2025_2026': {
                'url': 'https://www.chfainfo.com/getattachment/02ccecd8-bca7-4045-b9bb-9fa5723628dc/2025-2026-QAP.pdf',
                'title': 'CO 2025-2026 QAP',
                'description': 'Colorado CHFA 2025-2026 Low Income Housing Tax Credit QAP'
            },
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
            # State-specific headers
            if 'ihda.org' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.ihda.org/',
                }
            elif 'nchfa.com' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.nchfa.com/',
                }
            elif 'chfainfo.com' in url or 'chfa.org' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.chfainfo.com/',
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
                
                # Validate PDF
                if content.startswith(b'%PDF'):
                    # Valid PDF
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(save_path, 'wb') as f:
                        f.write(content)
                    
                    result['file_size'] = len(content)
                    result['md5_hash'] = hashlib.md5(content).hexdigest()
                    result['success'] = True
                    
                    print(f"    ✅ PDF saved: {result['file_size']:,} bytes")
                    
                else:
                    result['error'] = f"Not a PDF file"
                    print(f"    ❌ Not a PDF: {content[:30]}")
                    
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
    
    def download_verified_states(self):
        """Download QAPs from verified URLs"""
        print(f"🎯 Downloading QAPs with VERIFIED Working URLs...")
        print(f"📋 Target States: IL, NC, CO")
        print(f"📄 Attempting {len(self.verified_urls)} documents...")
        
        for i, (doc_id, doc_info) in enumerate(self.verified_urls.items(), 1):
            state_code = doc_id.split('_')[0]
            url = doc_info['url']
            title = doc_info['title']
            
            print(f"\n[{i}/{len(self.verified_urls)}] {title}")
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
        """Generate download report"""
        report = f"""
=== VERIFIED THREE STATES QAP DOWNLOAD REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TARGET STATES: Illinois (IHDA), North Carolina (NCHFA), Colorado (CHFA)
VERIFIED URLs Strategy: Using web search confirmed URLs

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
                report += f"  URL: {error['url']}\n\n"
        
        if self.results['successful'] > 0:
            report += f"""
SUCCESS! {self.results['successful']} new state QAPs downloaded with verified URLs.

STRATEGY: Web search verification continues to work better than Opus research URLs.

NEXT STEPS:
1. Process new QAPs through PDF chunking system
2. Update RAG indexes to include IL, NC, CO content
3. Reach 9-state coverage total (TX, AZ, NM, CA, OH, HI, IL, NC, CO)
4. Consider expanding to 15-20 state coverage for comprehensive national analysis

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
    """Download QAPs using verified working URLs"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    
    print("🚀 Starting Verified Three States QAP Downloads...")
    print("🎯 Strategy: Using web search confirmed URLs for IL, NC, CO")
    
    downloader = VerifiedThreeStatesDownloader(base_dir)
    
    # Download verified URLs
    downloader.download_verified_states()
    
    # Generate and display report
    report = downloader.generate_download_report()
    print(report)
    
    # Save report
    report_file = Path(base_dir) / "QAP" / "_cache" / f"verified_three_states_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"💾 Report saved to: {report_file}")
    
    if downloader.results['successful'] > 0:
        print(f"🎯 Success! Downloaded {downloader.results['successful']} QAPs with verified URLs!")
        print("📊 Ready to process and reach 9-state RAG coverage!")

if __name__ == "__main__":
    main()