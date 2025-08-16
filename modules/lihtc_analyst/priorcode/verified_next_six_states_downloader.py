#!/usr/bin/env python3
"""
Verified Next Six States QAP Downloader
Download QAPs for FL, NY, GA, WA, VA, PA using verified working URLs from web search
"""

import os
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
import json

class VerifiedNextSixStatesDownloader:
    """Download QAPs from verified working URLs for FL, NY, GA, WA, VA, PA"""
    
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
            # Florida - 2024 QAP (most current available - 2025 not yet published)
            'FL_2024': {
                'url': 'https://www.floridahousing.org/docs/default-source/programs/developers-multifamily-programs/competitive/2024-qualified-allocation-plan-(qap).pdf?sfvrsn=5bd3f17b_1',
                'title': 'FL 2024 QAP',
                'description': 'Florida Housing Finance Corporation 2024 Qualified Allocation Plan'
            },
            'FL_2023': {
                'url': 'https://www.floridahousing.org/docs/default-source/programs/developers-multifamily-programs/competitive/2023-qualified-allocation-plan-(qap).pdf?sfvrsn=dbc8f37b_2',
                'title': 'FL 2023 QAP',
                'description': 'Florida Housing Finance Corporation 2023 Qualified Allocation Plan'
            },
            
            # New York - Both State and NYC QAPs for 2025
            'NY_NYC_2025': {
                'url': 'https://www.nyc.gov/assets/hpd/downloads/pdfs/services/2025-qualified-allocation-plan.pdf',
                'title': 'NY NYC 2025 QAP',
                'description': 'New York City HPD 2025 Low Income Housing Tax Credit QAP'
            },
            'NY_NYC_2023': {
                'url': 'https://www.nyc.gov/assets/hpd/downloads/pdfs/services/2023-qualified-allocation-plan.pdf',
                'title': 'NY NYC 2023 QAP',
                'description': 'New York City HPD 2023 Low Income Housing Tax Credit QAP'
            },
            'NY_STATE_2021': {
                'url': 'https://hcr.ny.gov/system/files/documents/2021/05/qap-9-lihtc-part-2040.1-2040.13.pdf',
                'title': 'NY State 2021 9% LIHTC QAP',
                'description': 'New York State DHCR 9% LIHTC QAP Part 2040.1-2040.13'
            },
            
            # Georgia - 2024-2025 QAP (current cycle)
            'GA_2024_2025': {
                'url': 'https://www.novoco.com/public-media/documents/georgia-qap-2024-2025-board-approved-012024.pdf',
                'title': 'GA 2024-2025 QAP Board Approved',
                'description': 'Georgia DCA 2024-2025 Qualified Allocation Plan Board Approved January 2024'
            },
            'GA_2024_2025_DRAFT2': {
                'url': 'https://www.dca.ga.gov/sites/default/files/2024-2025_georgia_qap_draft2_0.pdf',
                'title': 'GA 2024-2025 QAP Draft 2',
                'description': 'Georgia DCA 2024-2025 Qualified Allocation Plan Draft 2'
            },
            
            # Washington - 2021 QAP (most current found - 2025 exists but not directly accessible via search)
            'WA_2021': {
                'url': 'https://www.wshfc.org/mhcf/9percent/2021application/a.qap.pdf',
                'title': 'WA 2021 QAP',
                'description': 'Washington State Housing Finance Commission 2021 Qualified Allocation Plan'
            },
            'WA_2021_NOVOCO': {
                'url': 'https://www.novoco.com/documents107445/washington-lihtc-qap-2021.pdf',
                'title': 'WA 2021 QAP Novoco',
                'description': 'Washington LIHTC QAP 2021 from Novoco'
            },
            
            # Virginia - 2025 QAP (current)
            'VA_2025': {
                'url': 'https://www.novoco.com/public-media/documents/virginia-lihtc-qap-2025-12112024.pdf',
                'title': 'VA 2025 QAP',
                'description': 'Virginia Housing (VHDA) 2025 Qualified Allocation Plan'
            },
            'VA_2023': {
                'url': 'https://assets.vpm.org/b2/90/dc9f2dba4d5aaa22cb6faa8658d4/virginia-lihtc-qap-2023-v13-04202023.pdf',
                'title': 'VA 2023 QAP v13',
                'description': 'Virginia LIHTC QAP 2023 Version 13'
            },
            'VA_2022': {
                'url': 'https://www.novoco.com/documents109888/virginia-lihtc-qap-final-2022-01032022.pdf',
                'title': 'VA 2022 QAP Final',
                'description': 'Virginia LIHTC QAP Final 2022'
            },
            
            # Pennsylvania - 2024 QAP (most current accessible - 2025-2026 exists but access restricted)
            'PA_2024': {
                'url': 'https://www.phfa.org/forms/multifamily_news/news/2023/2024-lihtc-allocation-plan.pdf',
                'title': 'PA 2024 QAP Board Approved',
                'description': 'Pennsylvania PHFA 2024 Qualified Allocation Plan for LIHTC Board Approved'
            },
            'PA_2022': {
                'url': 'https://www.phfa.org/forms/multifamily_program_notices/qap/2022/2022-lihtc-allocation-plan.pdf',
                'title': 'PA 2022 QAP Board Approved',
                'description': 'Pennsylvania PHFA 2022 Qualified Allocation Plan for LIHTC Board Approved'
            },
            'PA_2021': {
                'url': 'https://www.phfa.org/forms/multifamily_news/news/2020/2021-lihtc-allocation-plan.pdf',
                'title': 'PA 2021 QAP Board Approved',
                'description': 'Pennsylvania PHFA 2021 Qualified Allocation Plan for LIHTC Board Approved'
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
            if 'floridahousing.org' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.floridahousing.org/',
                }
            elif 'nyc.gov' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.nyc.gov/',
                }
            elif 'hcr.ny.gov' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://hcr.ny.gov/',
                }
            elif 'novoco.com' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.novoco.com/',
                }
            elif 'dca.ga.gov' in url or 'dca.georgia.gov' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.dca.ga.gov/',
                }
            elif 'wshfc.org' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.wshfc.org/',
                }
            elif 'phfa.org' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.phfa.org/',
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
        print(f"📋 Target States: FL, NY, GA, WA, VA, PA")
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
=== VERIFIED NEXT SIX STATES QAP DOWNLOAD REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TARGET STATES: Florida, New York, Georgia, Washington, Virginia, Pennsylvania
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

STRATEGY: Web search verification continues to provide the best access to current QAPs.

MILESTONE: Moving toward 15-state coverage for comprehensive national LIHTC analysis.

NEXT STEPS:
1. Process new QAPs through PDF chunking system
2. Update RAG indexes to include FL, NY, GA, WA, VA, PA content
3. Reach 15-state coverage total (TX, AZ, NM, CA, OH, HI, IL, NC, CO + FL, NY, GA, WA, VA, PA)
4. Consider expanding to 20+ states for near-complete national coverage

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
    
    print("🚀 Starting Verified Next Six States QAP Downloads...")
    print("🎯 Strategy: Using web search confirmed URLs for FL, NY, GA, WA, VA, PA")
    
    downloader = VerifiedNextSixStatesDownloader(base_dir)
    
    # Download verified URLs
    downloader.download_verified_states()
    
    # Generate and display report
    report = downloader.generate_download_report()
    print(report)
    
    # Save report
    report_file = Path(base_dir) / "QAP" / "_cache" / f"verified_next_six_states_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"💾 Report saved to: {report_file}")
    
    if downloader.results['successful'] > 0:
        print(f"🎯 Success! Downloaded {downloader.results['successful']} QAPs with verified URLs!")
        print("📊 Ready to process and reach 15-state RAG coverage!")

if __name__ == "__main__":
    main()