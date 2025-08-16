#!/usr/bin/env python3
"""
Verified QAP Downloader
Download QAPs using verified current URLs from direct website research
"""

import os
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
import json

class VerifiedQAPDownloader:
    """Download QAPs using verified working URLs"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.results = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'by_state': {},
            'errors': []
        }
        
        # Verified working URLs from website research
        self.verified_urls = {
            'CA': {
                'url': 'https://www.treasurer.ca.gov/ctcac/programreg/December-11-2024-Regulations-FINAL-APPROVED-Clean-Version.pdf',
                'title': 'CA 2025 QAP Regulations (Dec 2024)',
                'description': 'Current CTCAC regulations'
            },
            'TX': {
                'url': 'https://www.tdhca.texas.gov/sites/default/files/multifamily/docs/25-QAP.pdf',
                'title': 'TX 2025 QAP',
                'description': 'Texas 2025 QAP final version'
            },
            'TX_BL': {
                'url': 'https://www.tdhca.texas.gov/sites/default/files/multifamily/docs/25-QAP-bl.pdf',
                'title': 'TX 2025 QAP Blacklined',
                'description': 'Texas 2025 QAP with changes marked'
            },
            'TX_2024': {
                'url': 'https://www.tdhca.texas.gov/sites/default/files/multifamily/docs/24-QAP-10TAC-Ch11-clean.pdf',
                'title': 'TX 2024 QAP Clean',
                'description': 'Texas 2024 QAP clean version'
            },
            'TX_BOND': {
                'url': 'https://www.tdhca.texas.gov/sites/default/files/multifamily/docs/25-MFBondRules.pdf',
                'title': 'TX 2025 Bond Rules',
                'description': 'Texas multifamily bond rules 2025'
            },
            'HI_2025': {
                'url': 'https://dbedt.hawaii.gov/hhfdc/files/2024/12/2025-QAP-FINAL-VERSION-12.4.24.pdf',
                'title': 'HI 2025 QAP Final',
                'description': 'Hawaii 2025 QAP final version'
            },
            'HI_2024': {
                'url': 'https://dbedt.hawaii.gov/hhfdc/files/2023/09/2024-QAP-Draft-7-31-2023.pdf',
                'title': 'HI 2024 QAP Draft',
                'description': 'Hawaii 2024 QAP draft'
            },
            # Add more as we find verified URLs
        }
    
    def download_file(self, url: str, save_path: Path, timeout: int = 30) -> dict:
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
            # Professional headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # Make request with redirects
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
                # Download content
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
                    
                    print(f"    ✅ {result['file_size']:,} bytes ({result['file_size']/1024/1024:.1f} MB)")
                else:
                    result['error'] = f"Not a valid PDF (starts with: {content[:20]})"
                    print(f"    ❌ Invalid PDF format")
                    
            else:
                result['error'] = f"HTTP {response.status_code}: {response.reason}"
                print(f"    ❌ {result['error']}")
                
        except requests.exceptions.Timeout:
            result['error'] = "Timeout (30s)"
            print(f"    ⏱️  Download timeout")
        except requests.exceptions.ConnectionError:
            result['error'] = "Connection error"
            print(f"    🔌 Connection failed")
        except requests.exceptions.SSLError:
            result['error'] = "SSL error"
            print(f"    🔒 SSL certificate issue")
        except Exception as e:
            result['error'] = f"Error: {str(e)}"
            print(f"    💥 {result['error']}")
        
        return result
    
    def download_verified_qaps(self):
        """Download all verified QAP documents"""
        print(f"📥 Downloading {len(self.verified_urls)} verified QAP documents...")
        
        for i, (doc_id, doc_info) in enumerate(self.verified_urls.items(), 1):
            state_code = doc_id.split('_')[0]  # Extract state from doc_id
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
                    'http_code': result['response_code']
                })
            
            # Respectful delay
            time.sleep(1.5)
    
    def get_filename_from_doc_id(self, doc_id: str, title: str) -> str:
        """Generate appropriate filename from document ID and title"""
        # Clean up title for filename
        import re
        clean_title = re.sub(r'[^\w\s\-\.]', '', title)
        clean_title = re.sub(r'\s+', '_', clean_title)
        
        # Ensure .pdf extension
        if not clean_title.endswith('.pdf'):
            clean_title += '.pdf'
        
        return clean_title
    
    def generate_download_report(self) -> str:
        """Generate download report"""
        report = f"""
=== VERIFIED QAP DOWNLOAD REPORT ===
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
                report += f"  URL: {error['url']}\n\n"
        
        report += f"""
NEXT STEPS:
1. Process new downloads through PDF chunking system
2. Update RAG indexes with new content
3. Add more verified URLs from state websites
4. Test RAG query system with expanded content

FILES READY FOR PROCESSING:
"""
        
        # List downloaded files
        for state_code in self.results['by_state'].keys():
            state_dir = self.base_dir / "QAP" / state_code / "current"
            if state_dir.exists():
                for pdf_file in state_dir.glob("*.pdf"):
                    report += f"- {state_code}: {pdf_file.name} ({pdf_file.stat().st_size:,} bytes)\n"
        
        return report

def main():
    """Download verified QAP documents"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    
    print("🎯 Starting Verified QAP Downloads...")
    
    downloader = VerifiedQAPDownloader(base_dir)
    
    # Download all verified QAPs
    downloader.download_verified_qaps()
    
    # Generate and display report
    report = downloader.generate_download_report()
    print(report)
    
    # Save report
    report_file = Path(base_dir) / "QAP" / "_cache" / f"verified_download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"💾 Report saved to: {report_file}")
    print(f"📊 Ready to process {downloader.results['successful']} new QAP documents!")

if __name__ == "__main__":
    main()