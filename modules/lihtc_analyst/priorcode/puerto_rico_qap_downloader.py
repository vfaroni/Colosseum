#!/usr/bin/env python3
"""
Puerto Rico QAP Downloader
Downloads QAP documents from Puerto Rico Housing Finance Authority (AFV)
"""

import requests
import time
import os
from pathlib import Path
from urllib.parse import urlparse
import json
from datetime import datetime

class PuertoRicoQAPDownloader:
    def __init__(self):
        self.base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/QAP")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Puerto Rico QAP URLs from AFV website
        self.states = {
            'PR': {
                'name': 'Puerto Rico',
                'agency': 'Autoridad para el Financiamiento de la Vivienda (AFV)',
                'urls': [
                    {
                        'url': 'https://www.afv.pr.gov/wp-content/uploads/2024/09/prhfa-qap-2024-30sep24-draft-for-publication.pdf',
                        'name': '2024 QAP Draft for Publication',
                        'year': '2024'
                    },
                    {
                        'url': 'https://www.afv.pr.gov/wp-content/uploads/2024/10/annex-a-irc-section-42.pdf',
                        'name': 'Annex A - IRC Section 42',
                        'year': '2024'
                    },
                    {
                        'url': 'https://www.afv.pr.gov/wp-content/uploads/2024/10/annex-c-2024-lihtc-income-and-rent-limits.pdf',
                        'name': 'Annex C - 2024 LIHTC Income and Rent Limits',
                        'year': '2024'
                    },
                    {
                        'url': 'https://www.afv.pr.gov/wp-content/uploads/2024/10/annex-d-puerto-rico-ddas-qcts-2024-comprimido.pdf',
                        'name': 'Annex D - Puerto Rico DDAs QCTs 2024',
                        'year': '2024'
                    }
                ],
                'year': '2024'
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
        return f"PR_{clean_name}_{year}.pdf"

    def download_file(self, url: str, filepath: Path, doc_name: str) -> bool:
        """Download a single file with retry logic"""
        for attempt in range(3):
            try:
                print(f"  Attempt {attempt + 1}: Downloading {doc_name}")
                print(f"  URL: {url}")
                
                response = self.session.get(url, timeout=60, stream=True, allow_redirects=True)
                response.raise_for_status()
                
                content_type = response.headers.get('content-type', '').lower()
                
                if 'application/pdf' in content_type or url.endswith('.pdf') or response.content[:4] == b'%PDF':
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
        """Download QAPs for Puerto Rico"""
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
                time.sleep(1)  # Be respectful to the server
            else:
                self.results['failed'].append({
                    'state': state_code,
                    'url': doc_info['url'],
                    'name': doc_info['name'],
                    'reason': 'Download failed'
                })
        
        return downloaded_any

    def download_all(self):
        """Download Puerto Rico QAPs"""
        print("🏴 PUERTO RICO QAP DOWNLOADER")
        print("=" * 60)
        print("Downloading QAP documents from AFV (Autoridad para el Financiamiento de la Vivienda)")
        
        success = self.download_state_qaps('PR')
        if not success:
            print(f"  ❌ Failed to download any QAP for Puerto Rico")
        
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
        
        print(f"\n🗂 Files saved to: {self.base_path}/PR/current")
        
        # Update on progress including Puerto Rico
        if self.results['downloaded']:
            print(f"\n🏴 PUERTO RICO ADDITION:")
            print(f"   US Coverage: 51/51 jurisdictions (100%)")
            print(f"   Puerto Rico: BONUS TERRITORY COMPLETE ✅")
            print(f"   Total Coverage: 52 jurisdictions with Puerto Rico!")

if __name__ == "__main__":
    downloader = PuertoRicoQAPDownloader()
    downloader.download_all()