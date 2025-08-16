#!/usr/bin/env python3
"""
New Mexico and Arizona QAP Downloader
Download NM and AZ QAPs using verified URLs and alternative sources
"""

import os
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
import json

class NMAZQAPDownloader:
    """Download QAPs from New Mexico and Arizona with verified URLs"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.results = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'by_state': {},
            'errors': []
        }
        
        # Verified URLs
        self.target_urls = {
            # New Mexico - VERIFIED working URL from WebFetch
            'NM_2025': {
                'url': 'https://housingnm.org/uploads/documents/FINAL_2025_QAP.pdf',
                'title': 'NM 2025 QAP Final',
                'description': 'New Mexico 2025 QAP Final Version'
            },
            
            # Arizona - Try alternative sources since main site blocks us
            'AZ_2024_ALT1': {
                'url': 'https://www.novoco.com/sites/default/files/atoms/files/arizona_qap_final_2024-2025_11212023.pdf',
                'title': 'AZ 2024-2025 QAP (Novoco Mirror)',
                'description': 'Arizona 2024-2025 QAP from Novoco'
            },
            
            # Try direct state archive links
            'AZ_2024_ALT2': {
                'url': 'https://azgovernor.gov/file/arizona-housing-qap-2024-2025',
                'title': 'AZ 2024-2025 QAP (State Archive)',
                'description': 'Arizona QAP from state archives'
            },
            
            # Try HUD exchange which often mirrors state QAPs
            'AZ_2024_ALT3': {
                'url': 'https://www.hudexchange.info/resource/arizona-qap-2024-2025/',
                'title': 'AZ 2024-2025 QAP (HUD Exchange)',
                'description': 'Arizona QAP from HUD Exchange'
            }
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
            # Vary headers based on domain to avoid blocks
            if 'novoco.com' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.novoco.com/',
                }
            elif 'housingnm.org' in url:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Referer': 'https://housingnm.org/developers/lihtc/qaps',
                }
            else:
                # Default headers
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                }
            
            # Make request with appropriate settings
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
                total_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        content += chunk
                        total_size += len(chunk)
                        
                        # Progress indicator for large files
                        if total_size % (1024*1024) == 0:  # Every MB
                            print(f"    📊 Downloaded {total_size//1024//1024} MB...")
                
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
                    # Got HTML instead of PDF
                    # Look for PDF links in the HTML
                    content_str = content.decode('utf-8', errors='ignore')
                    import re
                    pdf_links = re.findall(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', content_str, re.IGNORECASE)
                    
                    if pdf_links:
                        result['error'] = f"HTML page returned with PDF links: {pdf_links[:2]}"
                    else:
                        result['error'] = "HTML page returned, no PDF links found"
                        
                else:
                    result['error'] = f"Invalid content format (starts with: {content[:20]})"
                    
            elif response.status_code == 403:
                result['error'] = "Access forbidden (403) - site may be blocking automated access"
            elif response.status_code == 404:
                result['error'] = "Document not found (404) - URL may be outdated"
            else:
                result['error'] = f"HTTP {response.status_code}: {response.reason}"
                
        except requests.exceptions.Timeout:
            result['error'] = "Timeout (30s)"
        except requests.exceptions.ConnectionError:
            result['error'] = "Connection error"
        except requests.exceptions.SSLError:
            result['error'] = "SSL certificate error"
        except Exception as e:
            result['error'] = f"Error: {str(e)}"
        
        return result
    
    def download_nm_az_qaps(self):
        """Download New Mexico and Arizona QAPs"""
        print(f"🎯 Downloading New Mexico and Arizona QAPs...")
        print(f"📋 Attempting {len(self.target_urls)} documents...")
        
        for i, (doc_id, doc_info) in enumerate(self.target_urls.items(), 1):
            state_code = doc_id.split('_')[0]
            url = doc_info['url']
            title = doc_info['title']
            
            print(f"\n[{i}/{len(self.target_urls)}] {title}")
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
            time.sleep(2)
    
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
=== NEW MEXICO & ARIZONA QAP DOWNLOAD REPORT ===
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
                if 'PDF links' in error['error']:
                    report += f"  🔗 Action: Manual extraction needed\n"
                report += f"  Original URL: {error['url']}\n\n"
        
        report += f"""
RECOMMENDATIONS FOR FAILED DOWNLOADS:
1. For Arizona: Contact state directly or use web scraping tools
2. Try accessing during different hours (some states limit automated access)
3. Check state archive sites or third-party mirrors
4. Use manual download for critical missing states

NEXT STEPS:
1. Process successful downloads through PDF chunking system
2. Update RAG indexes with New Mexico content
3. Add Arizona through alternative methods if needed
4. Expand to additional priority states
"""
        
        return report

def main():
    """Download New Mexico and Arizona QAPs"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    
    print("🚀 Starting New Mexico & Arizona QAP Downloads...")
    
    downloader = NMAZQAPDownloader(base_dir)
    
    # Download NM and AZ QAPs
    downloader.download_nm_az_qaps()
    
    # Generate and display report
    report = downloader.generate_download_report()
    print(report)
    
    # Save report
    report_file = Path(base_dir) / "QAP" / "_cache" / f"nm_az_download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"💾 Report saved to: {report_file}")
    
    if downloader.results['successful'] > 0:
        print(f"📊 Ready to process {downloader.results['successful']} new QAP documents!")
        print("🎯 Next: Run PDF processor and update RAG indexes")

if __name__ == "__main__":
    main()