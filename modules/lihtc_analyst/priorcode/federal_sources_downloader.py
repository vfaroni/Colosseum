#!/usr/bin/env python3
"""
Federal LIHTC Sources Downloader
Downloads Tier 1 federal LIHTC documents from official government sources
Based on research from TIER1_SOURCES_COLLECTION_GUIDE.md
"""

import os
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import time
import hashlib
from urllib.parse import urlparse

class FederalSourcesDownloader:
    """Download federal LIHTC sources from official government websites"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.federal_dir = self.base_dir / "federal" / "LIHTC_Federal_Sources"
        self.current_dir = self.federal_dir / "current"
        self.cache_dir = self.federal_dir / "_cache"
        self.logs_dir = self.federal_dir / "_logs"
        
        # Create directories
        for directory in [self.current_dir, self.cache_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Download session configuration
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Download tracking
        self.download_log = {
            'session_start': datetime.now().isoformat(),
            'downloads_attempted': 0,
            'downloads_successful': 0,
            'downloads_failed': 0,
            'total_bytes_downloaded': 0,
            'sources': {},
            'errors': []
        }
        
        # Tier 1 federal sources from research
        self.tier1_sources = {
            'IRC_Section_42': {
                'urls': [
                    'http://uscode.house.gov/view.xhtml?req=(title:26+section:42+edition:prelim)',
                    'https://www.law.cornell.edu/uscode/text/26/42'
                ],
                'authority_level': 'statutory',
                'description': 'Internal Revenue Code Section 42 - Core LIHTC statute',
                'target_directory': 'IRC_Section_42',
                'expected_format': 'html'
            },
            'Treasury_Regulations': {
                'urls': [
                    'https://ecfr.gov/current/title-26/chapter-I/subchapter-A/part-1/section-1.42-1',
                    'https://ecfr.gov/current/title-26/chapter-I/subchapter-A/part-1/section-1.42-5',
                    'https://www.law.cornell.edu/cfr/text/26/1.42-5'
                ],
                'authority_level': 'regulatory',
                'description': 'Treasury Regulations 26 CFR 1.42 series',
                'target_directory': 'Treasury_Regulations',
                'expected_format': 'html'
            },
            'Revenue_Procedure_2024_40': {
                'urls': [
                    'https://www.irs.gov/pub/irs-drop/rp-24-40.pdf'
                ],
                'authority_level': 'guidance',
                'description': 'Revenue Procedure 2024-40 - 2025 inflation adjustments',
                'target_directory': 'Revenue_Procedures',
                'expected_format': 'pdf'
            },
            'Average_Income_Test_Regulations': {
                'urls': [
                    'https://www.federalregister.gov/documents/2022/10/12/2022-22070/section-42-low-income-housing-credit-average-income-test-regulations',
                    'https://www.federalregister.gov/documents/2022/11/30/2022-26073/section-42-low-income-housing-credit-average-income-test-regulations-correction'
                ],
                'authority_level': 'regulatory',
                'description': 'Average Income Test Final Regulations (2022)',
                'target_directory': 'Federal_Register',
                'expected_format': 'html'
            }
        }
    
    def download_file(self, url: str, destination: Path, source_name: str) -> Tuple[bool, str, int]:
        """Download a single file with error handling and validation"""
        print(f"  📥 Downloading: {url}")
        
        try:
            # Add delay to be respectful to government servers
            time.sleep(1)
            
            response = self.session.get(url, verify=True, timeout=30)
            response.raise_for_status()
            
            # Validate content
            content_length = len(response.content)
            if content_length < 1000:  # Minimum size check
                return False, f"Content too small ({content_length} bytes) - likely error page", 0
            
            # Create destination directory
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(destination, 'wb') as f:
                f.write(response.content)
            
            # Verify file was written
            if not destination.exists() or destination.stat().st_size == 0:
                return False, "File write failed or empty file", 0
            
            print(f"    ✅ Downloaded {content_length:,} bytes to {destination.name}")
            return True, "Success", content_length
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {e}"
            print(f"    ❌ {error_msg}")
            return False, error_msg, 0
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(f"    ❌ {error_msg}")
            return False, error_msg, 0
    
    def generate_filename(self, url: str, source_name: str, format_hint: str) -> str:
        """Generate appropriate filename for downloaded content"""
        parsed_url = urlparse(url)
        
        # Extract filename from URL if available
        if parsed_url.path and '.' in parsed_url.path.split('/')[-1]:
            filename = parsed_url.path.split('/')[-1]
        else:
            # Generate filename based on source and format
            timestamp = datetime.now().strftime('%Y%m%d')
            
            if format_hint == 'pdf':
                filename = f"{source_name}_{timestamp}.pdf"
            elif format_hint == 'html':
                filename = f"{source_name}_{timestamp}.html"
            else:
                filename = f"{source_name}_{timestamp}.txt"
        
        # Clean filename
        filename = filename.replace(' ', '_').replace('(', '').replace(')', '')
        return filename
    
    def download_source_group(self, source_name: str, source_config: Dict) -> bool:
        """Download all URLs for a specific federal source"""
        print(f"\n📋 Downloading {source_name}: {source_config['description']}")
        
        target_dir = self.current_dir / source_config['target_directory']
        urls = source_config['urls']
        authority_level = source_config['authority_level']
        expected_format = source_config['expected_format']
        
        success_count = 0
        total_bytes = 0
        
        for i, url in enumerate(urls):
            # Generate filename
            filename = self.generate_filename(url, f"{source_name}_{i+1}", expected_format)
            destination = target_dir / filename
            
            # Skip if already downloaded
            if destination.exists():
                file_size = destination.stat().st_size
                if file_size > 1000:  # Reasonable size check
                    print(f"    ⏭️  Already exists: {filename} ({file_size:,} bytes)")
                    success_count += 1
                    total_bytes += file_size
                    continue
            
            # Download file
            success, error_msg, bytes_downloaded = self.download_file(url, destination, source_name)
            
            # Update tracking
            self.download_log['downloads_attempted'] += 1
            if success:
                self.download_log['downloads_successful'] += 1
                success_count += 1
                total_bytes += bytes_downloaded
                self.download_log['total_bytes_downloaded'] += bytes_downloaded
            else:
                self.download_log['downloads_failed'] += 1
                self.download_log['errors'].append({
                    'source': source_name,
                    'url': url,
                    'error': error_msg,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Update source tracking
        self.download_log['sources'][source_name] = {
            'description': source_config['description'],
            'authority_level': authority_level,
            'target_directory': source_config['target_directory'],
            'urls_total': len(urls),
            'downloads_successful': success_count,
            'total_bytes': total_bytes,
            'completion_rate': f"{(success_count/len(urls)*100):.1f}%"
        }
        
        print(f"    📊 {source_name} Summary: {success_count}/{len(urls)} successful ({total_bytes:,} bytes)")
        return success_count > 0  # Success if at least one download worked
    
    def download_all_tier1_sources(self):
        """Download all Tier 1 federal sources"""
        print("🇺🇸 Federal LIHTC Sources Download Starting")
        print(f"📁 Target directory: {self.current_dir}")
        print(f"🎯 Tier 1 sources: {len(self.tier1_sources)} groups")
        
        overall_success = 0
        
        for source_name, source_config in self.tier1_sources.items():
            try:
                success = self.download_source_group(source_name, source_config)
                if success:
                    overall_success += 1
            except Exception as e:
                error_msg = f"Failed to download {source_name}: {e}"
                print(f"❌ {error_msg}")
                self.download_log['errors'].append({
                    'source': source_name,
                    'error': error_msg,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Generate download report
        self.generate_download_report()
        
        print(f"\n🎉 Federal sources download complete!")
        print(f"📊 Success rate: {(overall_success/len(self.tier1_sources)*100):.1f}% ({overall_success}/{len(self.tier1_sources)} source groups)")
        print(f"📥 Total downloaded: {self.download_log['total_bytes_downloaded']:,} bytes")
        print(f"📄 Individual files: {self.download_log['downloads_successful']}/{self.download_log['downloads_attempted']} successful")
        
        if self.download_log['errors']:
            print(f"⚠️  {len(self.download_log['errors'])} errors occurred - check download report for details")
    
    def generate_download_report(self):
        """Generate comprehensive download report"""
        self.download_log['session_end'] = datetime.now().isoformat()
        
        # Save detailed JSON report
        report_path = self.logs_dir / f"federal_download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.download_log, f, indent=2, ensure_ascii=False)
        
        # Generate human-readable summary
        summary_path = self.logs_dir / f"federal_download_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("Federal LIHTC Sources Download Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Session: {self.download_log['session_start']} to {self.download_log['session_end']}\n")
            f.write(f"Total Bytes Downloaded: {self.download_log['total_bytes_downloaded']:,}\n")
            f.write(f"Downloads Successful: {self.download_log['downloads_successful']}/{self.download_log['downloads_attempted']}\n\n")
            
            f.write("Source Groups Summary:\n")
            f.write("-" * 30 + "\n")
            for source_name, source_info in self.download_log['sources'].items():
                f.write(f"\n{source_name}:\n")
                f.write(f"  Description: {source_info['description']}\n")
                f.write(f"  Authority Level: {source_info['authority_level']}\n")
                f.write(f"  Success Rate: {source_info['completion_rate']}\n")
                f.write(f"  Bytes Downloaded: {source_info['total_bytes']:,}\n")
                f.write(f"  Target Directory: {source_info['target_directory']}\n")
            
            if self.download_log['errors']:
                f.write(f"\n\nErrors ({len(self.download_log['errors'])}):\n")
                f.write("-" * 20 + "\n")
                for error in self.download_log['errors']:
                    f.write(f"\n{error['source']}: {error['error']}\n")
                    f.write(f"  URL: {error.get('url', 'N/A')}\n")
                    f.write(f"  Time: {error['timestamp']}\n")
        
        print(f"📄 Download report saved: {report_path}")
        print(f"📄 Download summary saved: {summary_path}")
    
    def validate_downloads(self):
        """Validate all downloaded files"""
        print("\n🔍 Validating downloaded files...")
        
        validation_results = {
            'valid_files': 0,
            'invalid_files': 0,
            'missing_files': 0,
            'total_size': 0,
            'issues': []
        }
        
        for source_name, source_config in self.tier1_sources.items():
            target_dir = self.current_dir / source_config['target_directory']
            
            if not target_dir.exists():
                validation_results['missing_files'] += 1
                validation_results['issues'].append(f"Missing directory: {target_dir}")
                continue
            
            files_found = list(target_dir.glob('*'))
            if not files_found:
                validation_results['missing_files'] += 1
                validation_results['issues'].append(f"No files in directory: {target_dir}")
                continue
            
            for file_path in files_found:
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    validation_results['total_size'] += file_size
                    
                    if file_size > 1000:  # Reasonable minimum size
                        validation_results['valid_files'] += 1
                        print(f"    ✅ {file_path.name} ({file_size:,} bytes)")
                    else:
                        validation_results['invalid_files'] += 1
                        validation_results['issues'].append(f"File too small: {file_path} ({file_size} bytes)")
                        print(f"    ⚠️  {file_path.name} ({file_size:,} bytes) - may be error page")
        
        print(f"\n📊 Validation Summary:")
        print(f"    Valid files: {validation_results['valid_files']}")
        print(f"    Invalid files: {validation_results['invalid_files']}")
        print(f"    Missing files: {validation_results['missing_files']}")
        print(f"    Total size: {validation_results['total_size']:,} bytes")
        
        if validation_results['issues']:
            print(f"    Issues found: {len(validation_results['issues'])}")
            for issue in validation_results['issues']:
                print(f"      - {issue}")
        
        return validation_results

def main():
    """Main execution function"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    downloader = FederalSourcesDownloader(base_dir)
    
    # Download all Tier 1 sources
    downloader.download_all_tier1_sources()
    
    # Validate downloads
    downloader.validate_downloads()

if __name__ == "__main__":
    main()