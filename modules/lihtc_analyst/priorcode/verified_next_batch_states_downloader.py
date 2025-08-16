#!/usr/bin/env python3
"""
Verified Next Batch States QAP Downloader
Download QAPs for Southeast, Mountain West, and Plains states using verified working URLs
"""

import os
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
import json

class VerifiedNextBatchStatesDownloader:
    """Download QAPs from verified working URLs for multiple regions"""
    
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
            # Southeast States
            'FL_2024': {
                'url': 'https://www.floridahousing.org/docs/default-source/programs/developers-multifamily-programs/competitive/2024-qualified-allocation-plan-(qap).pdf',
                'title': 'FL 2024 QAP',
                'description': 'Florida Housing Finance Corporation 2024 Qualified Allocation Plan'
            },
            'GA_2024_2025': {
                'url': 'https://www.novoco.com/public-media/documents/georgia-qap-2024-2025-board-approved-012024.pdf',
                'title': 'GA 2024-2025 QAP Board Approved',
                'description': 'Georgia DCA 2024-2025 Qualified Allocation Plan Board Approved'
            },
            'SC_2025_DRAFT': {
                'url': 'https://www.schousing.com/library/2025%20-%20Draft%20QAP%2020241010.pdf',
                'title': 'SC 2025 QAP Draft',
                'description': 'South Carolina 2025 Draft Qualified Allocation Plan'
            },
            'AL_2025': {
                'url': 'https://www.novoco.com/public-media/documents/alabama-lihtc-final-qap-2025-09182024.pdf',
                'title': 'AL 2025 QAP Final',
                'description': 'Alabama Housing Finance Authority 2025 QAP Final'
            },
            'MS_2025': {
                'url': 'https://www.novoco.com/public-media/documents/mississippi-lihtc-qap-final-2025-01072025.pdf',
                'title': 'MS 2025 QAP Final',
                'description': 'Mississippi Home Corporation 2025 QAP Final'
            },
            'TN_2025_DRAFT': {
                'url': 'https://thda.org/pdf/THDA-Draft-2025-QAP.pdf',
                'title': 'TN 2025 QAP Draft',
                'description': 'Tennessee Housing Development Agency Draft 2025 QAP'
            },
            'TN_2025_NOVOCO': {
                'url': 'https://www.novoco.com/public-media/documents/tennessee-qap-draft-2025-07312024.pdf',
                'title': 'TN 2025 QAP Draft Novoco',
                'description': 'Tennessee QAP Draft 2025 from Novoco'
            },
            'KY_2025_2026_DRAFT': {
                'url': 'https://www.kyhousing.org/Partners/Developers/Multifamily/Documents/2025-2026%20Qualified%20Allocation%20Plan%20-%20DRAFT.pdf',
                'title': 'KY 2025-2026 QAP Draft',
                'description': 'Kentucky Housing Corporation 2025-2026 QAP Draft'
            },
            
            # Mountain West States
            'MT_2025': {
                'url': 'https://housing.mt.gov/_shared/Multifamily/docs/2025QAPFINALGov.pdf',
                'title': 'MT 2025 QAP Final Governor Approved',
                'description': 'Montana Board of Housing 2025 QAP Final Governor Approved'
            },
            'MT_2025_NOVOCO': {
                'url': 'https://www.novoco.com/public-media/documents/montana-lihtc-qap-final-2025.pdf',
                'title': 'MT 2025 QAP Final Novoco',
                'description': 'Montana 2025 QAP Final from Novoco'
            },
            'WY_2025_DRAFT': {
                'url': 'https://www.wyomingcda.com/wp-content/uploads/2024/04/2025-DRAFT-AHAP.pdf',
                'title': 'WY 2025 Affordable Housing Allocation Plan Draft',
                'description': 'Wyoming Community Development Authority 2025 Draft AHAP'
            },
            'WY_2024_FINAL': {
                'url': 'https://www.novoco.com/documents116129/wyoming-lihtc-final-qap-2024-09072023.pdf',
                'title': 'WY 2024 QAP Final',
                'description': 'Wyoming 2024 LIHTC Final QAP'
            },
            'UT_2025': {
                'url': 'https://www.novoco.com/public-media/documents/utah-lihtc-final-qap-2025-05072024.pdf',
                'title': 'UT 2025 QAP Final',
                'description': 'Utah Housing Corporation 2025 Federal and State Housing Credit Program Final'
            },
            'UT_2025_REDLINE': {
                'url': 'https://utahhousingcorp.org/pdf/2025_Redline_QAP_240321.pdf',
                'title': 'UT 2025 QAP Redline',
                'description': 'Utah 2025 QAP Redline Version'
            },
            'NV_2025': {
                'url': 'https://housing.nv.gov/uploadedFiles/housingnewnvgov/Content/Programs/LIT/QAP/2025QAPfinal20241231.pdf',
                'title': 'NV 2025 QAP Final',
                'description': 'Nevada Housing Division 2025 QAP Final'
            },
            
            # Plains States
            'OK_2025_FINAL': {
                'url': 'https://www.novoco.com/public-media/documents/oklahoma-final-qap-2025-09182024.pdf',
                'title': 'OK 2025 QAP Final',
                'description': 'Oklahoma Housing Finance Agency Affordable Housing Tax Credits Program 2025 Final'
            },
            'OK_2025_DRAFT': {
                'url': 'https://www.novoco.com/public-media/documents/oklahoma-lihtc-qap-final-draft-2025-09032024.pdf',
                'title': 'OK 2025 QAP Final Draft',
                'description': 'Oklahoma 2025 Final Draft Qualified Allocation Plan'
            },
            'KS_2023': {
                'url': 'https://kshousingcorp.org/wp-content/uploads/2022/10/2023-QAP-FINAL.pdf',
                'title': 'KS 2023 QAP Final',
                'description': 'Kansas Housing Resources Corporation 2023 QAP Final'
            },
            'KS_2024_DRAFT': {
                'url': 'https://kshousingcorp.org/wp-content/uploads/2023/08/DRAFT-2024-QAP-clean.pdf',
                'title': 'KS 2024 QAP Draft',
                'description': 'Kansas Housing Resources Corporation Draft 2024 QAP'
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
            elif 'schousing.com' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.schousing.com/',
                }
            elif 'thda.org' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://thda.org/',
                }
            elif 'kyhousing.org' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.kyhousing.org/',
                }
            elif 'housing.mt.gov' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://housing.mt.gov/',
                }
            elif 'wyomingcda.com' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.wyomingcda.com/',
                }
            elif 'utahhousingcorp.org' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://utahhousingcorp.org/',
                }
            elif 'housing.nv.gov' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://housing.nv.gov/',
                }
            elif 'kshousingcorp.org' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://kshousingcorp.org/',
                }
            elif 'novoco.com' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.novoco.com/',
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
        print(f"📋 Target Regions: Southeast, Mountain West, Plains")
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
=== VERIFIED NEXT BATCH STATES QAP DOWNLOAD REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TARGET REGIONS: Southeast, Mountain West, Plains States
STATES COVERED: FL, GA, SC, AL, MS, TN, KY, MT, WY, UT, NV, OK, KS
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

STRATEGY: Multi-region approach accelerating toward complete 51-jurisdiction coverage.

COVERAGE PROGRESS:
- Previous: 18 states (TX, AZ, NM, CA, OH, HI, IL, NC, CO, NY, PA, VA, WA, MI, IN, MN, WI, MO)
- Adding: Southeast, Mountain West, Plains states
- Target: Complete 51-jurisdiction coverage (50 states + DC)

NEXT STEPS:
1. Process new regional QAPs through PDF chunking system
2. Update RAG indexes with expanded regional content
3. Continue downloading remaining states (New England, Mid-Atlantic, additional states)
4. Complete comprehensive national LIHTC analysis system

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
    
    print("🚀 Starting Verified Next Batch States QAP Downloads...")
    print("🎯 Strategy: Multi-region approach for Southeast, Mountain West, Plains states")
    
    downloader = VerifiedNextBatchStatesDownloader(base_dir)
    
    # Download verified URLs
    downloader.download_verified_states()
    
    # Generate and display report
    report = downloader.generate_download_report()
    print(report)
    
    # Save report
    report_file = Path(base_dir) / "QAP" / "_cache" / f"verified_next_batch_states_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"💾 Report saved to: {report_file}")
    
    if downloader.results['successful'] > 0:
        print(f"🎯 Success! Downloaded {downloader.results['successful']} QAPs with verified URLs!")
        print("📊 Ready to process and expand toward complete coverage!")

if __name__ == "__main__":
    main()