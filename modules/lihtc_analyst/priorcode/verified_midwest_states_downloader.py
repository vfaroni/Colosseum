#!/usr/bin/env python3
"""
Verified Midwest States QAP Downloader
Download QAPs for MI, IN, MN, WI, MO, IA using verified working URLs from web search
"""

import os
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
import json

class VerifiedMidwestStatesDownloader:
    """Download QAPs from verified working URLs for MI, IN, MN, WI, MO, IA"""
    
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
            # Michigan - MSHDA 2024-2025 QAP (2-year cycle, most current)
            'MI_2024_2025': {
                'url': 'https://www.novoco.com/documents116086/michigan-lihtc-qap-2024-final-08212023.pdf',
                'title': 'MI 2024-2025 QAP Final',
                'description': 'Michigan MSHDA 2024-2025 Qualified Allocation Plan Final'
            },
            'MI_2024_2025_STAFF_REPORT': {
                'url': 'https://www.michigan.gov/mshda/-/media/Project/Websites/mshda/developers/lihtc/assets/liqap/mshda_li_qap_2024_2025_staff_report_final.pdf?rev=d6ef1ef0da9c47a9858f73b6d92e500f&hash=F033ABED546A09FC99499B7F01D14026',
                'title': 'MI 2024-2025 QAP Staff Report',
                'description': 'Michigan MSHDA 2024-2025 QAP Staff Report Final'
            },
            
            # Indiana - IHCDA 2025 QAP (standalone year)
            'IN_2025': {
                'url': 'https://www.in.gov/ihcda/files/2025-QAP-Final.pdf',
                'title': 'IN 2025 QAP Final',
                'description': 'Indiana IHCDA State of Indiana 2025 Qualified Allocation Plan Final'
            },
            'IN_2025_NOVOCO': {
                'url': 'https://www.novoco.com/public-media/documents/indiana-final-qap-2025-04102024.pdf',
                'title': 'IN 2025 QAP Final Novoco',
                'description': 'Indiana 2025 QAP Final from Novoco'
            },
            'IN_2025_CHANGES': {
                'url': 'https://www.novoco.com/public-media/documents/indiana-lihtc-summary-changes-2025-qap-first-draft-02152024.pdf',
                'title': 'IN 2025 QAP Summary of Changes',
                'description': 'Indiana Summary of Changes for 2025 QAP First Draft'
            },
            
            # Minnesota - 2024-2025 QAP (2-year cycle)
            'MN_2024_2025': {
                'url': 'https://www.mnhousing.gov/get/mhfa_251053',
                'title': 'MN 2024-2025 QAP',
                'description': 'Minnesota Housing Finance Agency 2024-2025 Housing Tax Credit QAP'
            },
            
            # Wisconsin - WHEDA 2025-2026 QAP (2-year cycle)
            'WI_2025_2026': {
                'url': 'https://www.wheda.com/globalassets/documents/tax-credits/htc/2025/2025-26-qap.pdf',
                'title': 'WI 2025-2026 QAP',
                'description': 'Wisconsin WHEDA 2025-2026 Qualified Allocation Plan'
            },
            'WI_2025_2026_CHANGES': {
                'url': 'https://www.wheda.com/globalassets/documents/tax-credits/htc/2025/2025-2026-qap---summary-of-major-changes.pdf',
                'title': 'WI 2025-2026 QAP Summary of Changes',
                'description': 'Wisconsin 2025-2026 QAP Summary of Major Changes'
            },
            'WI_2025_APPENDIX_D': {
                'url': 'https://www.wheda.com/globalassets/documents/tax-credits/htc/2025/appendices/appendix-d---underwriting-criteria-2025.pdf',
                'title': 'WI 2025 QAP Appendix D Underwriting',
                'description': 'Wisconsin 2025-26 QAP Appendix D Underwriting Criteria'
            },
            
            # Missouri - MHDC 2025 QAP
            'MO_2025': {
                'url': 'https://mhdc.com/media/4gumckfx/2025-qualified-allocation-plan.pdf',
                'title': 'MO 2025 QAP',
                'description': 'Missouri MHDC 2025 Qualified Allocation Plan'
            },
            'MO_2025_REDLINE': {
                'url': 'https://mhdc.com/media/2tsbhhmt/draft-2025-qualified-allocation-plan-redline-version.pdf',
                'title': 'MO 2025 QAP Draft Redline',
                'description': 'Missouri MHDC Draft 2025 QAP Redline Version'
            },
            'MO_2025_NOVOCO': {
                'url': 'https://www.novoco.com/public-media/documents/missouri-lihtc-qap-2025-07162024.pdf',
                'title': 'MO 2025 QAP Novoco',
                'description': 'Missouri 2025 QAP from Novoco'
            },
            
            # Iowa - IFA 2025 QAP (separate 4% and 9%)
            'IA_2025_4PCT': {
                'url': 'https://www.iowafinance.com/content/uploads/2024/09/2025-IFA-QAP-4percent-LIHTC_05282024-Watermarked.pdf',
                'title': 'IA 2025 4% QAP Draft',
                'description': 'Iowa IFA 2025 Draft 4% Qualified Allocation Plan'
            },
            'IA_2025_9PCT': {
                'url': 'https://www.iowafinance.com/content/uploads/2024/09/2025-IFA-QAP-9-percent-LIHTC_05282024-Watermarked.pdf',
                'title': 'IA 2025 9% QAP Draft',
                'description': 'Iowa IFA 2025 Draft 9% Qualified Allocation Plan'
            },
            'IA_2025_9PCT_NOVOCO': {
                'url': 'https://www.novoco.com/public-media/documents/iowa-lihtc-draft-qap-9-percent-2025-06142024.pdf',
                'title': 'IA 2025 9% QAP Draft Novoco',
                'description': 'Iowa 2025 Draft 9% QAP from Novoco'
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
            if 'michigan.gov' in url or 'mshda' in url.lower():
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.michigan.gov/',
                }
            elif 'in.gov' in url or 'ihcda' in url.lower():
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.in.gov/',
                }
            elif 'mnhousing.gov' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.mnhousing.gov/',
                }
            elif 'wheda.com' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.wheda.com/',
                }
            elif 'mhdc.com' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://mhdc.com/',
                }
            elif 'iowafinance.com' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.iowafinance.com/',
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
        print(f"📋 Target States: MI, IN, MN, WI, MO, IA")
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
=== VERIFIED MIDWEST STATES QAP DOWNLOAD REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TARGET STATES: Michigan, Indiana, Minnesota, Wisconsin, Missouri, Iowa
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

STRATEGY: Continuing comprehensive coverage with Midwest states.

COVERAGE UPDATE:
- Previous: 13 states (TX, AZ, NM, CA, OH, HI, IL, NC, CO, NY, PA, VA, WA)
- Adding: MI, IN, MN, WI, MO, IA (Midwest region)
- Progress: Moving toward complete 51-jurisdiction coverage

NEXT STEPS:
1. Process new Midwest QAPs through PDF chunking system
2. Update RAG indexes to include MI, IN, MN, WI, MO, IA content
3. Continue downloading remaining states for complete coverage
4. Build comprehensive national LIHTC analysis system

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
    
    print("🚀 Starting Verified Midwest States QAP Downloads...")
    print("🎯 Strategy: Using web search confirmed URLs for MI, IN, MN, WI, MO, IA")
    
    downloader = VerifiedMidwestStatesDownloader(base_dir)
    
    # Download verified URLs
    downloader.download_verified_states()
    
    # Generate and display report
    report = downloader.generate_download_report()
    print(report)
    
    # Save report
    report_file = Path(base_dir) / "QAP" / "_cache" / f"verified_midwest_states_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"💾 Report saved to: {report_file}")
    
    if downloader.results['successful'] > 0:
        print(f"🎯 Success! Downloaded {downloader.results['successful']} QAPs with verified URLs!")
        print("📊 Ready to process and expand RAG coverage!")

if __name__ == "__main__":
    main()