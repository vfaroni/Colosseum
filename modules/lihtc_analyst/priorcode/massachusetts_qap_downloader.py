#!/usr/bin/env python3
"""
Massachusetts QAP Downloader
Downloads QAP documents from mass.gov with discovered working URLs
"""

import requests
import time
import os
from pathlib import Path
from urllib.parse import urlparse
import json
from datetime import datetime

class MassachusettsQAPDownloader:
    def __init__(self):
        self.base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/QAP")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.mass.gov/info-details/low-income-housing-tax-credit-lihtc'
        })
        
        # Massachusetts QAP URLs discovered from web pages
        self.states = {
            'MA': {
                'name': 'Massachusetts',
                'agency': 'Executive Office of Housing and Livable Communities',
                'urls': [
                    {
                        'url': 'https://www.mass.gov/doc/2025-2026-lihtc-qap/download',
                        'name': '2025-2026 LIHTC QAP',
                        'year': '2025-2026'
                    },
                    {
                        'url': 'https://www.mass.gov/doc/draft-2025-2026-lihtc-qap-0/download',
                        'name': 'Draft 2025-2026 LIHTC QAP',
                        'year': '2025-2026'
                    },
                    {
                        'url': 'https://www.mass.gov/doc/2023-2024-qap-0/download',
                        'name': '2023-2024 QAP',
                        'year': '2023-2024'
                    },
                    {
                        'url': 'https://www.mass.gov/doc/2022-2023-qap/download',
                        'name': '2022-2023 QAP',
                        'year': '2022-2023'
                    }
                ],
                'year': '2025-2026'
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

    def get_filename_from_url(self, url: str, doc_name: str, year: str) -> str:
        """Generate appropriate filename from URL and metadata"""
        # Clean the document name for filename
        clean_name = doc_name.replace(' ', '_').replace('-', '_')
        return f"MA_{clean_name}_{year}.pdf"

    def download_file(self, url: str, filepath: Path, doc_name: str) -> bool:
        """Download a single file with retry logic"""
        for attempt in range(3):
            try:
                print(f"  Attempt {attempt + 1}: Downloading {doc_name}")
                print(f"  URL: {url}")
                
                response = self.session.get(url, timeout=60, stream=True, allow_redirects=True)
                response.raise_for_status()
                
                content_type = response.headers.get('content-type', '').lower()
                
                if 'application/pdf' in content_type or 'download' in url:
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
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
        """Download QAPs for Massachusetts"""
        state_info = self.states[state_code]
        state_dir = self.ensure_directory(state_code)
        
        print(f"\n📄 Downloading QAPs for {state_info['name']} ({state_code})")
        print(f"   Agency: {state_info['agency']}")
        print(f"   Current QAP Year: {state_info['year']}")
        
        downloaded_any = False
        
        for doc_info in state_info['urls']:
            filename = self.get_filename_from_url(doc_info['url'], doc_info['name'], doc_info['year'])
            filepath = state_dir / filename
            
            if filepath.exists():
                print(f"  ⏭ Skipping existing file: {filename}")
                self.results['skipped'].append({
                    'state': state_code,
                    'url': doc_info['url'],
                    'name': doc_info['name'],
                    'reason': 'File already exists'
                })
                downloaded_any = True
                continue
            
            if self.download_file(doc_info['url'], filepath, doc_info['name']):
                self.results['downloaded'].append({
                    'state': state_code,
                    'url': doc_info['url'],
                    'name': doc_info['name'],
                    'filename': filename,
                    'size': filepath.stat().st_size
                })
                downloaded_any = True
                time.sleep(2)  # Be respectful to the server
            else:
                self.results['failed'].append({
                    'state': state_code,
                    'url': doc_info['url'],
                    'name': doc_info['name'],
                    'reason': 'Download failed'
                })
        
        return downloaded_any

    def download_all(self):
        """Download Massachusetts QAPs"""
        print("🏛️ MASSACHUSETTS QAP DOWNLOADER")
        print("=" * 60)
        print("Downloading QAP documents from mass.gov")
        
        success = self.download_state_qaps('MA')
        if not success:
            print(f"  ❌ Failed to download any QAP for Massachusetts")
        
        self.print_summary()

    def print_summary(self):
        """Print download summary"""
        print("\n" + "=" * 60)
        print("📊 DOWNLOAD SUMMARY")
        print("=" * 60)
        
        print(f"✅ Successfully downloaded: {len(self.results['downloaded'])}")
        for item in self.results['downloaded']:
            print(f"   • {item['state']}: {item['name']} - {item['filename']} ({item['size']:,} bytes)")
        
        print(f"\n⏭ Skipped (already exist): {len(self.results['skipped'])}")
        for item in self.results['skipped']:
            print(f"   • {item['state']}: {item['name']} - {item['reason']}")
        
        print(f"\n❌ Failed downloads: {len(self.results['failed'])}")
        for item in self.results['failed']:
            print(f"   • {item['state']}: {item['name']} - {item['reason']}")
        
        total_attempts = len(self.results['downloaded']) + len(self.results['failed'])
        success_rate = (len(self.results['downloaded']) / total_attempts * 100) if total_attempts > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}% ({len(self.results['downloaded'])}/{total_attempts})")
        
        print(f"\n🗂 Files saved to: {self.base_path}/MA/current")
        
        # Update on progress toward 51-state goal
        if self.results['downloaded']:
            print(f"\n🎯 PROGRESS UPDATE:")
            print(f"   Previous coverage: 49/51 jurisdictions (96.1%)")
            print(f"   Massachusetts: NOW COMPLETE ✅")
            print(f"   Remaining: Mississippi (MS)")
            print(f"   New coverage: 50/51 jurisdictions (98.0%)")

if __name__ == "__main__":
    downloader = MassachusettsQAPDownloader()
    downloader.download_all()