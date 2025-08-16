#!/usr/bin/env python3
"""
CTCAC 2025 R2 4% APPLICATION DOWNLOADER
Download applications 25-522 through 25-650 with proper naming
"""

import requests
import time
from pathlib import Path
from datetime import datetime
import logging

class CTCAC2025R2Downloader:
    """Download 2025 Round 2 4% applications from CTCAC website"""
    
    def __init__(self):
        self.base_url = "https://www.treasurer.ca.gov/ctcac/2025/secondround/4percent/applications"
        self.output_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Data_Sets/california/CA_LIHTC_Applications/raw_data")
        self.setup_logging()
        
        # Range: 25-522 to 25-650 (full download)
        self.start_num = 522
        self.end_num = 650
        
        self.stats = {
            'attempted': 0,
            'downloaded': 0,
            'already_exists': 0,
            'errors': 0,
            'error_list': []
        }
    
    def setup_logging(self):
        """Setup logging for download tracking"""
        log_dir = Path("download_logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"ctcac_2025_r2_download_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def download_all_applications(self):
        """Download all 2025 R2 applications from 25-522 to 25-650"""
        self.logger.info("🚀 Starting CTCAC 2025 R2 4% Application Download")
        self.logger.info(f"Range: 25-{self.start_num} to 25-{self.end_num}")
        self.logger.info(f"Output Directory: {self.output_dir}")
        self.logger.info("=" * 80)
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        for app_num in range(self.start_num, self.end_num + 1):
            self.stats['attempted'] += 1
            
            # Construct URLs and filenames
            download_url = f"{self.base_url}/25-{app_num}.xlsx"
            output_filename = f"2025_4pct_R2_25-{app_num}.xlsx"
            output_path = self.output_dir / output_filename
            
            # Check if file already exists
            if output_path.exists():
                self.logger.info(f"⏭️  [{app_num - self.start_num + 1}/{self.end_num - self.start_num + 1}] Already exists: {output_filename}")
                self.stats['already_exists'] += 1
                continue
            
            try:
                self.logger.info(f"⬇️  [{app_num - self.start_num + 1}/{self.end_num - self.start_num + 1}] Downloading: {download_url}")
                
                # Download with timeout and proper headers
                response = requests.get(
                    download_url, 
                    timeout=30,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    }
                )
                
                if response.status_code == 200:
                    # Check if it's actually an Excel file
                    content_type = response.headers.get('content-type', '')
                    if 'excel' in content_type.lower() or 'spreadsheet' in content_type.lower() or len(response.content) > 10000:
                        
                        # Save the file
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        
                        file_size = len(response.content) / 1024  # KB
                        self.logger.info(f"✅ Saved: {output_filename} ({file_size:.1f} KB)")
                        self.stats['downloaded'] += 1
                        
                    else:
                        self.logger.warning(f"⚠️  Not an Excel file: {download_url} (Content-Type: {content_type})")
                        self.stats['errors'] += 1
                        self.stats['error_list'].append(f"25-{app_num}: Not Excel file")
                
                elif response.status_code == 404:
                    self.logger.warning(f"❌ File not found: {download_url}")
                    self.stats['errors'] += 1
                    self.stats['error_list'].append(f"25-{app_num}: 404 Not Found")
                
                else:
                    self.logger.error(f"❌ HTTP {response.status_code}: {download_url}")
                    self.stats['errors'] += 1
                    self.stats['error_list'].append(f"25-{app_num}: HTTP {response.status_code}")
            
            except requests.exceptions.Timeout:
                self.logger.error(f"⏰ Timeout downloading: {download_url}")
                self.stats['errors'] += 1
                self.stats['error_list'].append(f"25-{app_num}: Timeout")
            
            except Exception as e:
                self.logger.error(f"💥 Error downloading {download_url}: {e}")
                self.stats['errors'] += 1
                self.stats['error_list'].append(f"25-{app_num}: {str(e)}")
            
            # Be nice to the server
            time.sleep(0.5)
        
        # Final report
        self.logger.info("=" * 80)
        self.logger.info("🏁 DOWNLOAD COMPLETE!")
        self.logger.info(f"📊 STATISTICS:")
        self.logger.info(f"   Attempted: {self.stats['attempted']}")
        self.logger.info(f"   Downloaded: {self.stats['downloaded']}")
        self.logger.info(f"   Already Existed: {self.stats['already_exists']}")
        self.logger.info(f"   Errors: {self.stats['errors']}")
        
        if self.stats['error_list']:
            self.logger.info(f"\\n❌ ERROR DETAILS:")
            for error in self.stats['error_list'][:10]:  # Show first 10 errors
                self.logger.info(f"   {error}")
            if len(self.stats['error_list']) > 10:
                self.logger.info(f"   ... and {len(self.stats['error_list']) - 10} more errors")
        
        total_new = self.stats['downloaded']
        if total_new > 0:
            self.logger.info(f"\\n🎯 SUCCESS: {total_new} new 2025 R2 applications downloaded!")
            self.logger.info(f"   Files saved to: {self.output_dir}")
            self.logger.info(f"   Naming format: 2025_4pct_R2_25-XXX.xlsx")
        
        return self.stats
    
    def verify_downloads(self):
        """Verify downloaded files are valid Excel files"""
        self.logger.info("\\n🔍 VERIFYING DOWNLOADED FILES...")
        
        pattern = "2025_4pct_R2_25-*.xlsx"
        files = list(self.output_dir.glob(pattern))
        
        valid_files = 0
        invalid_files = []
        
        for file_path in sorted(files):
            try:
                # Basic file size check
                if file_path.stat().st_size < 1000:  # Less than 1KB is suspicious
                    invalid_files.append(f"{file_path.name}: Too small ({file_path.stat().st_size} bytes)")
                else:
                    valid_files += 1
            except Exception as e:
                invalid_files.append(f"{file_path.name}: Error checking - {e}")
        
        self.logger.info(f"✅ Valid files: {valid_files}")
        if invalid_files:
            self.logger.warning(f"⚠️  Potentially invalid files: {len(invalid_files)}")
            for invalid in invalid_files[:5]:  # Show first 5
                self.logger.warning(f"   {invalid}")


def main():
    """Run the 2025 R2 downloader"""
    print("🚀 CTCAC 2025 R2 4% APPLICATION DOWNLOADER")
    print("=" * 50)
    print("Downloading applications 25-522 through 25-650")
    print("Output: 2025_4pct_R2_25-XXX.xlsx format")
    print("=" * 50)
    
    downloader = CTCAC2025R2Downloader()
    stats = downloader.download_all_applications()
    
    # Verify downloads
    downloader.verify_downloads()
    
    print("\\n" + "=" * 50)
    print("🏁 DOWNLOAD SESSION COMPLETE!")
    print(f"📈 New files downloaded: {stats['downloaded']}")
    print("=" * 50)


if __name__ == "__main__":
    main()