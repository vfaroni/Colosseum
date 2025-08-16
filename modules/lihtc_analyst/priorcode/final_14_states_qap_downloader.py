#!/usr/bin/env python3
"""
Final 14 States + DC QAP Downloader
Downloads QAP documents for the remaining 15 jurisdictions using verified URLs
"""

import requests
import time
import os
from pathlib import Path
from urllib.parse import urlparse
import json
from datetime import datetime

class Final14StatesQAPDownloader:
    def __init__(self):
        self.base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/QAP")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Final 14 states + DC with verified URLs
        self.states = {
            'MD': {
                'name': 'Maryland',
                'agency': 'MD Housing & Community Development',
                'urls': [
                    'https://dhcd.maryland.gov/HousingDevelopment/Documents/QAP_MRFP/2025-QAP-Final-Draft-Clean.pdf',
                    'https://dhcd.maryland.gov/HousingDevelopment/Documents/QAP_MRFP/2024-QAP-1st-Draft-Clean.pdf'
                ],
                'year': '2025'
            },
            'MA': {
                'name': 'Massachusetts',
                'agency': 'Massachusetts Government',
                'urls': [
                    'https://www.mass.gov/doc/2023-2024-qap-0/download'
                ],
                'year': '2023-2024'
            },
            'MS': {
                'name': 'Mississippi',
                'agency': 'Mississippi Home Corporation',
                'urls': [
                    'https://www.novoco.com/public-media/documents/mississippi-lihtc-qap-final-2025-01072025.pdf',
                    'https://www.novoco.com/public-media/documents/mississippi-final-qap-2024-01312024.pdf'
                ],
                'year': '2025'
            },
            'NE': {
                'name': 'Nebraska',
                'agency': 'Nebraska Investment Finance Authority',
                'urls': [
                    'https://opportunity.nebraska.gov/wp-content/uploads/2025/05/LIHTC-2024-25-QAP.pdf'
                ],
                'year': '2024-2025'
            },
            'NJ': {
                'name': 'New Jersey',
                'agency': 'New Jersey Housing and Mortgage Finance Agency',
                'urls': [
                    'https://www.nj.gov/dca/hmfa/developers/docs/lihtc/qap/tc_qap_2024.pdf'
                ],
                'year': '2024-2025'
            },
            'ND': {
                'name': 'North Dakota',
                'agency': 'North Dakota Housing Finance Agency',
                'urls': [
                    'https://www.ndhfa.org/wp-content/uploads/2024/08/2025LIHTCQAP.pdf',
                    'https://www.ndhfa.org/wp-content/uploads/2024/02/2024LIHTCQAP.pdf'
                ],
                'year': '2025'
            },
            'OK': {
                'name': 'Oklahoma',
                'agency': 'Oklahoma Housing Finance Agency',
                'urls': [
                    'https://www.novoco.com/public-media/documents/oklahoma-lihtc-qap-final-draft-2025-09032024.pdf',
                    'https://www.ohfa.org/wp-content/uploads/2023/08/2024-QAP-2nd-Draft.pdf'
                ],
                'year': '2025'
            },
            'OR': {
                'name': 'Oregon',
                'agency': 'Oregon Housing and Community Services',
                'urls': [
                    'https://www.oregon.gov/ohcs/rental-housing/housing-development/development-resources/Documents/QAP/2025-qap-final.pdf',
                    'https://www.oregon.gov/ohcs/rental-housing/housing-development/development-resources/Documents/QAP/2024-qap-draft-for-publish.pdf'
                ],
                'year': '2025'
            },
            'RI': {
                'name': 'Rhode Island',
                'agency': 'RIHousing',
                'urls': [
                    'https://www.rihousing.com/wp-content/uploads/2025-QAP-Executed-1.pdf',
                    'https://www.rihousing.com/wp-content/uploads/2024-Section-7-2024-QAP.pdf'
                ],
                'year': '2025'
            },
            'SC': {
                'name': 'South Carolina',
                'agency': 'SC Housing Finance and Development Authority',
                'urls': [
                    'https://schousing.sc.gov/sites/schousing/files/Documents/Development/LIHTC/2025%20Housing%20Tax%20Credit%20(LIHTC)/2025-QAP-Final-Updated-20250408.pdf',
                    'https://www.schousing.com/library/Tax%20Credit/2024/2024-Draft-QAP.pdf'
                ],
                'year': '2025'
            },
            'SD': {
                'name': 'South Dakota',
                'agency': 'South Dakota Housing Development Authority',
                'urls': [
                    'https://www.sdhousing.org/s/QAP-Plan-Final.pdf'
                ],
                'year': '2024-2025'
            },
            'VT': {
                'name': 'Vermont',
                'agency': 'Vermont Housing Finance Agency',
                'urls': [
                    'https://vhfa.org/sites/default/files/documents/multifamily/Signed_VHFA%202024-25%20Vermont%20Qualified%20Allocation%20Plan_vf.pdf'
                ],
                'year': '2024-2025'
            },
            'WV': {
                'name': 'West Virginia',
                'agency': 'West Virginia Housing Development Fund',
                'urls': [
                    'https://www.wvhdf.com/wp-content/uploads/2024/12/PROPOSED-2025-AND-2026-ALLOCATION-PLAN.pdf',
                    'https://www.novoco.com/documents113294/west-virginia-qualified-allocation-plan-2023-2024-04162023.pdf'
                ],
                'year': '2025-2026'
            },
            'DC': {
                'name': 'District of Columbia',
                'agency': 'DC Department of Housing and Community Development',
                'urls': [
                    'https://dhcd.dc.gov/sites/default/files/dc/sites/dhcd/publication/attachments/DHCD%27s%202025%20Qualified%20Allocation%20Plan%20Draft_0.pdf'
                ],
                'year': '2025'
            }
        }
        
        self.results = {
            'downloaded': [],
            'failed': [],
            'skipped': []
        }

    def ensure_directory(self, state_code: str):
        """Ensure state directory exists"""
        state_dir = self.base_path / state_code / "current"
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir

    def get_filename_from_url(self, url: str, state_code: str, year: str) -> str:
        """Generate appropriate filename from URL"""
        parsed = urlparse(url)
        original_name = Path(parsed.path).name
        
        if original_name.endswith('.pdf'):
            return original_name
        elif 'download' in url:
            return f"{state_code}_{year}_QAP_download.pdf"
        else:
            return f"{state_code}_{year}_QAP.pdf"

    def download_file(self, url: str, filepath: Path) -> bool:
        """Download a single file with retry logic"""
        for attempt in range(3):
            try:
                print(f"  Attempt {attempt + 1}: Downloading from {url}")
                
                response = self.session.get(url, timeout=30, stream=True, allow_redirects=True, verify=False)
                response.raise_for_status()
                
                content_type = response.headers.get('content-type', '').lower()
                
                if 'application/pdf' in content_type or url.endswith('.pdf') or 'download' in url:
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    file_size = filepath.stat().st_size
                    if file_size > 10000:  # At least 10KB for a substantial document
                        print(f"  ✓ Downloaded: {filepath.name} ({file_size:,} bytes)")
                        return True
                    else:
                        filepath.unlink()
                        print(f"  ✗ File too small ({file_size} bytes), likely not a valid QAP PDF")
                        return False
                        
                else:
                    print(f"  ✗ Not a PDF file (content-type: {content_type})")
                    return False
                    
            except requests.exceptions.RequestException as e:
                print(f"  ✗ Attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
        
        return False

    def download_state_qaps(self, state_code: str) -> bool:
        """Download QAPs for a specific state"""
        state_info = self.states[state_code]
        state_dir = self.ensure_directory(state_code)
        
        print(f"\n📄 Downloading QAPs for {state_info['name']} ({state_code})")
        print(f"   Agency: {state_info['agency']}")
        print(f"   Year: {state_info['year']}")
        
        downloaded_any = False
        
        for i, url in enumerate(state_info['urls']):
            filename = self.get_filename_from_url(url, state_code, state_info['year'])
            filepath = state_dir / filename
            
            if filepath.exists():
                print(f"  ⏭ Skipping existing file: {filename}")
                self.results['skipped'].append({
                    'state': state_code,
                    'url': url,
                    'reason': 'File already exists'
                })
                downloaded_any = True
                continue
            
            if self.download_file(url, filepath):
                self.results['downloaded'].append({
                    'state': state_code,
                    'url': url,
                    'filename': filename,
                    'size': filepath.stat().st_size
                })
                downloaded_any = True
                # Don't break, try all URLs for this state
            else:
                self.results['failed'].append({
                    'state': state_code,
                    'url': url,
                    'reason': 'Download failed'
                })
        
        return downloaded_any

    def download_all(self):
        """Download QAPs for final 14 states + DC"""
        print("🇺🇸 FINAL 14 STATES + DC QAP DOWNLOADER")
        print("=" * 60)
        print(f"Downloading QAPs for {len(self.states)} final jurisdictions with verified URLs")
        
        for state_code in self.states:
            success = self.download_state_qaps(state_code)
            if not success:
                print(f"  ❌ Failed to download any QAP for {state_code}")
            time.sleep(1)  # Brief pause between states
        
        self.print_summary()

    def print_summary(self):
        """Print download summary"""
        print("\n" + "=" * 60)
        print("📊 DOWNLOAD SUMMARY")
        print("=" * 60)
        
        print(f"✅ Successfully downloaded: {len(self.results['downloaded'])}")
        for item in self.results['downloaded']:
            print(f"   • {item['state']}: {item['filename']} ({item['size']:,} bytes)")
        
        print(f"\n⏭ Skipped (already exist): {len(self.results['skipped'])}")
        for item in self.results['skipped']:
            print(f"   • {item['state']}: {item['reason']}")
        
        print(f"\n❌ Failed downloads: {len(self.results['failed'])}")
        for item in self.results['failed']:
            print(f"   • {item['state']}: {item['url']} - {item['reason']}")
        
        total_attempts = len(self.results['downloaded']) + len(self.results['failed'])
        success_rate = (len(self.results['downloaded']) / total_attempts * 100) if total_attempts > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}% ({len(self.results['downloaded'])}/{total_attempts})")
        
        print(f"\n🗂 Files saved to: {self.base_path}")
        
        # Calculate new total coverage
        successful_states = set([item['state'] for item in self.results['downloaded']])
        skipped_states = set([item['state'] for item in self.results['skipped']])
        new_states = successful_states | skipped_states
        
        print(f"\n🎯 COVERAGE UPDATE:")
        print(f"   Previous coverage: 37/51 jurisdictions (73%)")
        print(f"   New states added: {len(new_states)}")
        print(f"   New total coverage: {37 + len(new_states)}/51 jurisdictions ({((37 + len(new_states))/51*100):.1f}%)")

if __name__ == "__main__":
    downloader = Final14StatesQAPDownloader()
    downloader.download_all()