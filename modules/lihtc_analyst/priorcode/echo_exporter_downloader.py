#!/usr/bin/env python3
"""
ECHO Exporter Download Handler
Advanced downloader for EPA's 231MB+ ECHO database with resume capability and bandwidth management

Status: Production Ready
Author: Structured Consultants LLC  
Date: July 23, 2025
"""

import os
import json
import requests
import zipfile
import pandas as pd
import geopandas as gpd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import time
import hashlib
from urllib.parse import urlparse
import shutil

class ECHOExporterDownloader:
    """Advanced downloader for EPA ECHO Exporter with bandwidth management"""
    
    ECHO_DOWNLOAD_URL = 'https://echo.epa.gov/files/echodownloads/echo_exporter.zip'
    
    # Bandwidth configuration profiles
    BANDWIDTH_PROFILES = {
        'travel': {
            'chunk_size': 1024,           # 1KB chunks for slow connections
            'request_timeout': 120,       # 2 minute timeout
            'retry_delay': 10,            # 10 second retry delay
            'max_retries': 5,             # More retries for unstable connections
            'progress_frequency': 50,     # Update progress every 50 chunks
            'max_hourly_mb': 50          # Limit to 50MB per hour
        },
        'normal': {
            'chunk_size': 8192,          # 8KB chunks
            'request_timeout': 60,        # 1 minute timeout
            'retry_delay': 5,             # 5 second retry delay
            'max_retries': 3,             # Standard retries
            'progress_frequency': 100,    # Update every 100 chunks
            'max_hourly_mb': 500         # 500MB per hour limit
        },
        'high_speed': {
            'chunk_size': 65536,         # 64KB chunks
            'request_timeout': 30,        # 30 second timeout
            'retry_delay': 2,             # 2 second retry delay
            'max_retries': 2,             # Fewer retries
            'progress_frequency': 50,     # Frequent progress updates
            'max_hourly_mb': 2000        # 2GB per hour
        }
    }
    
    def __init__(self, base_data_path: str, bandwidth_profile: str = 'normal'):
        self.base_data_path = Path(base_data_path)
        self.bandwidth_profile = bandwidth_profile
        self.config = self.BANDWIDTH_PROFILES[bandwidth_profile]
        self.setup_logging()
        
        # Create storage directories
        self.storage_path = self.base_data_path / "federal" / "echo"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Download tracking
        self.download_state_file = self.storage_path / "download_state.json"
        self.download_stats = {
            'start_time': None,
            'bytes_downloaded': 0,
            'total_size': 0,
            'last_chunk_time': None,
            'average_speed_mbps': 0,
            'estimated_completion': None
        }
        
    def setup_logging(self):
        """Setup logging for ECHO download"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def check_existing_download(self) -> Tuple[bool, Optional[int]]:
        """Check for existing partial downloads"""
        
        # Check for complete file first
        complete_files = list(self.storage_path.glob("echo_exporter_*.zip"))
        if complete_files:
            latest_file = max(complete_files, key=os.path.getctime)
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(latest_file))
            
            if file_age.days < 7:  # File is less than a week old
                self.logger.info(f"Recent ECHO file found: {latest_file.name} ({file_age.days} days old)")
                return True, None
        
        # Check for partial download
        partial_file = self.storage_path / "echo_exporter_partial.zip"
        if partial_file.exists() and self.download_state_file.exists():
            try:
                with open(self.download_state_file, 'r') as f:
                    state = json.load(f)
                
                resume_size = partial_file.stat().st_size
                expected_size = state.get('total_size', 0)
                
                if resume_size > 0 and resume_size < expected_size:
                    self.logger.info(f"Partial download found: {resume_size:,} / {expected_size:,} bytes")
                    return False, resume_size
                    
            except Exception as e:
                self.logger.warning(f"Error reading download state: {str(e)}")
        
        return False, None
    
    def get_remote_file_info(self) -> Dict:
        """Get remote file size and last modified date"""
        try:
            response = requests.head(
                self.ECHO_DOWNLOAD_URL,
                timeout=30,
                headers={'User-Agent': 'LIHTC-Environmental-Analysis/1.0 (Structured Consultants LLC)'}
            )
            
            if response.status_code == 200:
                file_size = int(response.headers.get('content-length', 0))
                last_modified = response.headers.get('last-modified', '')
                
                return {
                    'size_bytes': file_size,
                    'size_mb': file_size / (1024 * 1024),
                    'last_modified': last_modified,
                    'estimated_download_time': self._estimate_download_time(file_size)
                }
            else:
                self.logger.error(f"Failed to get file info: HTTP {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting remote file info: {str(e)}")
            return {}
    
    def _estimate_download_time(self, file_size_bytes: int) -> str:
        """Estimate download time based on bandwidth profile"""
        max_hourly_bytes = self.config['max_hourly_mb'] * 1024 * 1024
        estimated_hours = file_size_bytes / max_hourly_bytes
        
        if estimated_hours < 1:
            return f"{estimated_hours * 60:.0f} minutes"
        else:
            return f"{estimated_hours:.1f} hours"
    
    def download_with_resume(self, force_redownload: bool = False) -> Dict:
        """Download ECHO exporter with resume capability"""
        
        # Check existing downloads
        if not force_redownload:
            exists, resume_size = self.check_existing_download()
            if exists:
                return {
                    'success': True,
                    'message': 'Recent file already exists',
                    'action': 'skipped',
                    'file_path': None
                }
        else:
            exists, resume_size = False, None
        
        # Get remote file info
        file_info = self.get_remote_file_info()
        if not file_info:
            return {
                'success': False,
                'message': 'Failed to get remote file information',
                'action': 'failed'
            }
        
        self.logger.info(f"ECHO Exporter Download")
        self.logger.info(f"File Size: {file_info['size_mb']:.1f} MB")
        self.logger.info(f"Estimated Time: {file_info['estimated_download_time']}")
        self.logger.info(f"Bandwidth Profile: {self.bandwidth_profile}")
        
        # Setup download state
        self.download_stats = {
            'start_time': datetime.now(),
            'bytes_downloaded': resume_size or 0,
            'total_size': file_info['size_bytes'],
            'last_chunk_time': datetime.now(),
            'average_speed_mbps': 0,
            'estimated_completion': None
        }
        
        # Setup file paths
        partial_file = self.storage_path / "echo_exporter_partial.zip"
        final_file = self.storage_path / f"echo_exporter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        try:
            # Setup request headers for resume
            headers = {'User-Agent': 'LIHTC-Environmental-Analysis/1.0 (Structured Consultants LLC)'}
            if resume_size:
                headers['Range'] = f'bytes={resume_size}-'
                self.logger.info(f"Resuming download from byte {resume_size:,}")
            
            # Make request
            response = requests.get(
                self.ECHO_DOWNLOAD_URL,
                headers=headers,
                stream=True,
                timeout=self.config['request_timeout']
            )
            
            if response.status_code not in [200, 206]:  # 206 = Partial Content
                return {
                    'success': False,
                    'message': f'HTTP {response.status_code}',
                    'action': 'failed'
                }
            
            # Open file for writing (append if resuming)
            mode = 'ab' if resume_size else 'wb'
            
            with open(partial_file, mode) as f:
                chunk_count = 0
                speed_samples = []
                
                for chunk in response.iter_content(chunk_size=self.config['chunk_size']):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                        chunk_count += 1
                        
                        # Update download stats
                        current_time = datetime.now()
                        self.download_stats['bytes_downloaded'] += len(chunk)
                        self.download_stats['last_chunk_time'] = current_time
                        
                        # Calculate speed and progress
                        if chunk_count % self.config['progress_frequency'] == 0:
                            self._update_progress_and_speed(speed_samples)
                            
                            # Check bandwidth limits
                            if self._check_bandwidth_limits():
                                self.logger.info("Bandwidth limit reached, pausing...")
                                time.sleep(60)  # Pause for 1 minute
                        
                        # Save state periodically
                        if chunk_count % 1000 == 0:
                            self._save_download_state()
            
            # Download completed successfully
            if partial_file.exists():
                # Verify file integrity
                if self._verify_download_integrity(partial_file, file_info['size_bytes']):
                    # Move to final location
                    shutil.move(str(partial_file), str(final_file))
                    
                    # Clean up state file
                    if self.download_state_file.exists():
                        self.download_state_file.unlink()
                    
                    self.logger.info(f"ECHO download completed: {final_file.name}")
                    
                    # Process the downloaded file
                    processing_result = self.process_echo_file(final_file)
                    
                    return {
                        'success': True,
                        'message': 'Download and processing completed',
                        'action': 'completed',
                        'file_path': str(final_file),
                        'processing_result': processing_result,
                        'download_stats': self.download_stats
                    }
                else:
                    return {
                        'success': False,
                        'message': 'File integrity verification failed',
                        'action': 'failed'
                    }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Download request failed: {str(e)}")
            self._save_download_state()  # Save state for resume
            return {
                'success': False,
                'message': f'Request failed: {str(e)}',
                'action': 'failed_resumable'
            }
        except Exception as e:
            self.logger.error(f"Download failed: {str(e)}")
            return {
                'success': False,
                'message': f'Download failed: {str(e)}',
                'action': 'failed'
            }
    
    def _update_progress_and_speed(self, speed_samples: List[float]):
        """Update download progress and calculate speed"""
        current_time = datetime.now()
        elapsed = (current_time - self.download_stats['start_time']).total_seconds()
        
        if elapsed > 0:
            bytes_per_second = self.download_stats['bytes_downloaded'] / elapsed
            mbps = (bytes_per_second * 8) / (1024 * 1024)  # Convert to Mbps
            
            speed_samples.append(mbps)
            if len(speed_samples) > 10:  # Keep rolling average
                speed_samples.pop(0)
            
            avg_speed = sum(speed_samples) / len(speed_samples)
            self.download_stats['average_speed_mbps'] = avg_speed
            
            # Calculate progress
            progress = (self.download_stats['bytes_downloaded'] / self.download_stats['total_size']) * 100
            remaining_bytes = self.download_stats['total_size'] - self.download_stats['bytes_downloaded']
            
            if avg_speed > 0:
                remaining_seconds = (remaining_bytes * 8) / (avg_speed * 1024 * 1024)
                completion_time = current_time + timedelta(seconds=remaining_seconds)
                self.download_stats['estimated_completion'] = completion_time.isoformat()
            
            self.logger.info(
                f"Progress: {progress:.1f}% | Speed: {avg_speed:.2f} Mbps | "
                f"Downloaded: {self.download_stats['bytes_downloaded'] / (1024*1024):.1f} MB"
            )
    
    def _check_bandwidth_limits(self) -> bool:
        """Check if bandwidth limits have been exceeded"""
        elapsed_hours = (datetime.now() - self.download_stats['start_time']).total_seconds() / 3600
        if elapsed_hours > 0:
            mb_per_hour = (self.download_stats['bytes_downloaded'] / (1024 * 1024)) / elapsed_hours
            return mb_per_hour > self.config['max_hourly_mb']
        return False
    
    def _save_download_state(self):
        """Save current download state for resume capability"""
        try:
            with open(self.download_state_file, 'w') as f:
                json.dump(self.download_stats, f, indent=2, default=str)
        except Exception as e:
            self.logger.warning(f"Failed to save download state: {str(e)}")
    
    def _verify_download_integrity(self, file_path: Path, expected_size: int) -> bool:
        """Verify downloaded file integrity"""
        try:
            actual_size = file_path.stat().st_size
            
            if actual_size != expected_size:
                self.logger.error(f"File size mismatch: {actual_size} != {expected_size}")
                return False
            
            # Test if it's a valid ZIP file
            with zipfile.ZipFile(file_path, 'r') as zf:
                bad_file = zf.testzip()
                if bad_file:
                    self.logger.error(f"Corrupt ZIP file: {bad_file}")
                    return False
            
            self.logger.info("File integrity verification passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Integrity verification failed: {str(e)}")
            return False
    
    def process_echo_file(self, zip_file_path: Path) -> Dict:
        """Process downloaded ECHO ZIP file"""
        try:
            processing_start = datetime.now()
            self.logger.info(f"Processing ECHO file: {zip_file_path.name}")
            
            # Create processing directory
            extract_dir = self.storage_path / f"echo_processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract ZIP file
            with zipfile.ZipFile(zip_file_path, 'r') as zf:
                file_list = zf.namelist()
                self.logger.info(f"Extracting {len(file_list)} files")
                zf.extractall(extract_dir)
            
            # Analyze extracted files
            csv_files = list(extract_dir.glob("*.csv"))
            processed_files = []
            
            for csv_file in csv_files[:5]:  # Process first 5 files as sample
                try:
                    # Read CSV and get basic info
                    df = pd.read_csv(csv_file, nrows=1000)  # Sample first 1000 rows
                    
                    file_info = {
                        'filename': csv_file.name,
                        'sample_rows': len(df),
                        'columns': len(df.columns),
                        'column_names': list(df.columns)[:10],  # First 10 columns
                        'has_coordinates': any('LON' in col.upper() or 'LAT' in col.upper() for col in df.columns)
                    }
                    
                    processed_files.append(file_info)
                    self.logger.info(f"Processed {csv_file.name}: {len(df.columns)} columns")
                    
                except Exception as e:
                    self.logger.warning(f"Error processing {csv_file.name}: {str(e)}")
            
            # Create processing summary
            processing_summary = {
                'processing_date': processing_start.isoformat(),
                'processing_duration_seconds': (datetime.now() - processing_start).total_seconds(),
                'zip_file': zip_file_path.name,
                'extracted_files': len(file_list),
                'csv_files_found': len(csv_files),
                'processed_samples': len(processed_files),
                'extract_directory': str(extract_dir),
                'file_details': processed_files
            }
            
            # Save processing summary
            summary_file = extract_dir / "processing_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(processing_summary, f, indent=2, default=str)
            
            # Create metadata
            self.create_echo_metadata(zip_file_path, processing_summary)
            
            self.logger.info(f"ECHO processing completed in {processing_summary['processing_duration_seconds']:.1f} seconds")
            
            return processing_summary
            
        except Exception as e:
            self.logger.error(f"Error processing ECHO file: {str(e)}")
            return {'error': str(e)}
    
    def create_echo_metadata(self, zip_file_path: Path, processing_summary: Dict):
        """Create comprehensive metadata for ECHO data"""
        
        metadata = {
            "dataset_name": "EPA ECHO Enforcement and Compliance History Online",
            "source_url": "https://echo.epa.gov/files/echodownloads/echo_exporter.zip",
            "source_organization": "U.S. Environmental Protection Agency",
            "acquisition_date": datetime.now().isoformat(),
            "file_size_mb": zip_file_path.stat().st_size / (1024 * 1024),
            "original_format": "ZIP containing multiple CSV files",
            "coordinate_system": "WGS84 (EPSG:4326) where applicable",
            "update_frequency": "Weekly",
            "record_count_estimate": "1.5+ million regulated facilities",
            "authentication_required": False,
            "bandwidth_profile_used": self.bandwidth_profile,
            "download_stats": self.download_stats,
            "processing_summary": processing_summary,
            "lihtc_relevance": "Primary database for facility compliance history and environmental violations",
            "usage_notes": [
                "Contains comprehensive facility data for all EPA-regulated entities",
                "Includes violations, enforcement actions, and penalties",
                "Geographic coordinates available for mapping and proximity analysis",
                "Cross-reference with Envirofacts for detailed facility information",
                "Critical for LIHTC environmental due diligence screening"
            ],
            "data_quality_notes": [
                "Large dataset requires significant processing time",
                "Multiple CSV files with different data structures",
                "Some facilities may have missing coordinate data",
                "Weekly updates ensure current compliance status"
            ]
        }
        
        # Save metadata
        metadata_file = self.storage_path / f"echo_metadata_{datetime.now().strftime('%Y%m%d')}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        # Create markdown documentation
        md_content = f"""# EPA ECHO Exporter Data

## Collection Summary
- **Download Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **File Size**: {metadata['file_size_mb']:.1f} MB
- **Bandwidth Profile**: {self.bandwidth_profile}
- **Processing Time**: {processing_summary.get('processing_duration_seconds', 0):.1f} seconds

## Data Contents
- **CSV Files**: {processing_summary.get('csv_files_found', 'Unknown')}
- **Estimated Records**: 1.5+ million facilities
- **Geographic Coverage**: All U.S. states and territories

## LIHTC Usage
- Primary screening for facility compliance history
- Environmental violation identification within property radius
- Enforcement action assessment for risk evaluation
- Cross-reference with other EPA databases for comprehensive analysis

## File Structure
The ECHO exporter contains multiple CSV files with facility data, violations, enforcement actions, and penalties. Key files typically include:
- Facility information with coordinates
- Violation records by facility
- Enforcement action details
- Penalty assessments

## Next Steps
1. Process individual CSV files for specific analysis needs
2. Create geospatial analysis for LIHTC property proximity screening
3. Integrate with other environmental databases for comprehensive due diligence
4. Setup automated updates to maintain current compliance data
"""
        
        md_file = self.storage_path / f"echo_documentation_{datetime.now().strftime('%Y%m%d')}.md"
        with open(md_file, 'w') as f:
            f.write(md_content)

def main():
    """Main execution function for testing"""
    
    print("EPA ECHO Exporter Downloader")
    print("=" * 40)
    
    # Show bandwidth profiles
    print("Available Bandwidth Profiles:")
    for profile, config in ECHOExporterDownloader.BANDWIDTH_PROFILES.items():
        print(f"  {profile:12} | Chunk: {config['chunk_size']:>6} bytes | Max: {config['max_hourly_mb']:>4} MB/hr")
    
    print()
    
    # Initialize downloader
    downloader = ECHOExporterDownloader(
        base_data_path="/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets",
        bandwidth_profile='travel'  # Use travel profile for testing
    )
    
    # Get remote file info
    file_info = downloader.get_remote_file_info()
    if file_info:
        print(f"ECHO Exporter File Info:")
        print(f"  Size: {file_info['size_mb']:.1f} MB")
        print(f"  Estimated Download Time: {file_info['estimated_download_time']}")
        print(f"  Last Modified: {file_info.get('last_modified', 'Unknown')}")
    
    print()
    print("Ready for download!")
    print("To start download: downloader.download_with_resume()")

if __name__ == "__main__":
    main()