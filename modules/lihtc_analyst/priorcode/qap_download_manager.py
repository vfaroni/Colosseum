#!/usr/bin/env python3
"""
QAP Download Manager with Progress Tracking and Retry Logic
Handles automated downloading of QAP documents with detailed progress reporting
"""

import os
import sys
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import logging
from dataclasses import dataclass, field
import json

@dataclass
class DownloadTask:
    """Individual download task with metadata"""
    url: str
    state_code: str
    document_type: str
    year: int
    save_path: Path
    priority: int = 5
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"  # pending, downloading, completed, failed
    error_message: str = ""
    file_size: Optional[int] = None
    download_time: Optional[float] = None
    md5_hash: Optional[str] = None

class QAPDownloadManager:
    """Manages downloading of QAP documents with progress tracking"""
    
    def __init__(self, base_dir: str, max_workers: int = 3):
        self.base_dir = Path(base_dir)
        self.max_workers = max_workers
        self.download_queue: List[DownloadTask] = []
        self.completed_downloads: List[DownloadTask] = []
        self.failed_downloads: List[DownloadTask] = []
        
        # Setup directories
        self.cache_dir = self.base_dir / "QAP" / "_cache"
        self.logs_dir = self.base_dir / "QAP" / "_logs"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Load download history
        self.download_history = self.load_download_history()
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def setup_logging(self):
        """Configure logging with file and console output"""
        log_file = self.logs_dir / f"download_manager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_download_history(self) -> Dict:
        """Load previous download history"""
        history_file = self.cache_dir / "download_history.json"
        if history_file.exists():
            with open(history_file, 'r') as f:
                return json.load(f)
        return {}
        
    def save_download_history(self):
        """Save download history"""
        history_file = self.cache_dir / "download_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.download_history, f, indent=2, default=str)
            
    def add_download_task(self, url: str, state_code: str, document_type: str, 
                         year: int, priority: int = 5) -> DownloadTask:
        """Add a download task to the queue"""
        # Determine save path
        save_dir = self.base_dir / "QAP" / state_code / self._get_subdir(document_type)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d")
        ext = self._get_file_extension(url)
        filename = f"{state_code}_{document_type}_{year}_{timestamp}{ext}"
        save_path = save_dir / filename
        
        # Create task
        task = DownloadTask(
            url=url,
            state_code=state_code,
            document_type=document_type,
            year=year,
            save_path=save_path,
            priority=priority
        )
        
        # Check if already downloaded
        url_hash = hashlib.md5(url.encode()).hexdigest()
        if url_hash in self.download_history:
            prev_download = self.download_history[url_hash]
            if Path(prev_download['file_path']).exists():
                task.status = "completed"
                task.file_size = prev_download.get('file_size')
                task.md5_hash = prev_download.get('md5_hash')
                self.logger.info(f"Already downloaded: {state_code} {document_type} {year}")
                self.completed_downloads.append(task)
                return task
                
        self.download_queue.append(task)
        return task
        
    def _get_subdir(self, document_type: str) -> str:
        """Map document type to subdirectory"""
        mapping = {
            "qap_current": "QAP/current",
            "qap_archive": "QAP/archive",
            "qap_redline": "QAP/redlines",
            "app_9pct": "applications/9pct",
            "app_4pct": "applications/4pct",
            "app_instructions": "applications/instructions",
            "notice": "notices",
            "awards": "awards/results",
            "scoring": "awards/scoring"
        }
        return mapping.get(document_type, "other")
        
    def _get_file_extension(self, url: str) -> str:
        """Extract file extension from URL"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        for ext in ['.pdf', '.xlsx', '.xls', '.docx', '.doc', '.zip']:
            if path.endswith(ext):
                return ext
        return '.pdf'  # Default
        
    def download_file(self, task: DownloadTask) -> DownloadTask:
        """Download a single file with retry logic"""
        task.status = "downloading"
        start_time = time.time()
        
        while task.retry_count <= task.max_retries:
            try:
                self.logger.info(f"Downloading: {task.state_code} {task.document_type} {task.year} - {task.url}")
                
                # Download with timeout
                response = self.session.get(task.url, timeout=60, stream=True)
                response.raise_for_status()
                
                # Save file
                content = b''
                with open(task.save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            content += chunk
                            
                # Calculate hash
                task.md5_hash = hashlib.md5(content).hexdigest()
                task.file_size = len(content)
                task.download_time = time.time() - start_time
                task.status = "completed"
                
                # Update history
                url_hash = hashlib.md5(task.url.encode()).hexdigest()
                self.download_history[url_hash] = {
                    'url': task.url,
                    'file_path': str(task.save_path),
                    'download_date': datetime.now().isoformat(),
                    'file_size': task.file_size,
                    'md5_hash': task.md5_hash,
                    'state_code': task.state_code,
                    'document_type': task.document_type,
                    'year': task.year
                }
                
                self.logger.info(f"✓ Completed: {task.state_code} {task.document_type} - {task.file_size:,} bytes in {task.download_time:.1f}s")
                return task
                
            except requests.exceptions.RequestException as e:
                task.retry_count += 1
                task.error_message = str(e)
                
                if task.retry_count <= task.max_retries:
                    wait_time = 2 ** task.retry_count  # Exponential backoff
                    self.logger.warning(f"Retry {task.retry_count}/{task.max_retries} for {task.state_code} after {wait_time}s")
                    time.sleep(wait_time)
                else:
                    task.status = "failed"
                    self.logger.error(f"✗ Failed: {task.state_code} {task.document_type} - {task.error_message}")
                    return task
                    
        return task
        
    def download_all(self, show_progress: bool = True) -> Dict[str, int]:
        """Download all queued files with progress tracking"""
        if not self.download_queue:
            self.logger.info("No files in download queue")
            return {'completed': 0, 'failed': 0, 'skipped': 0}
            
        # Sort by priority
        self.download_queue.sort(key=lambda x: x.priority)
        
        total_tasks = len(self.download_queue)
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Starting download of {total_tasks} files")
        self.logger.info(f"{'='*60}\n")
        
        completed_count = 0
        failed_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.download_file, task): task 
                for task in self.download_queue
            }
            
            # Process completed tasks
            for future in as_completed(future_to_task):
                task = future.result()
                
                if task.status == "completed":
                    self.completed_downloads.append(task)
                    completed_count += 1
                else:
                    self.failed_downloads.append(task)
                    failed_count += 1
                    
                # Progress update
                progress = (completed_count + failed_count) / total_tasks * 100
                self.logger.info(f"Progress: {progress:.1f}% ({completed_count + failed_count}/{total_tasks})")
                
        # Save history
        self.save_download_history()
        
        # Summary
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Download Summary:")
        self.logger.info(f"  ✓ Completed: {completed_count}")
        self.logger.info(f"  ✗ Failed: {failed_count}")
        self.logger.info(f"  ⚬ Already downloaded: {len(self.completed_downloads) - completed_count}")
        self.logger.info(f"{'='*60}\n")
        
        return {
            'completed': completed_count,
            'failed': failed_count,
            'skipped': len(self.completed_downloads) - completed_count
        }
        
    def generate_progress_report(self) -> pd.DataFrame:
        """Generate detailed progress report by state"""
        all_tasks = self.completed_downloads + self.failed_downloads + self.download_queue
        
        # Group by state
        state_data = {}
        for task in all_tasks:
            if task.state_code not in state_data:
                state_data[task.state_code] = {
                    'total': 0,
                    'completed': 0,
                    'failed': 0,
                    'pending': 0,
                    'types': set()
                }
                
            state_data[task.state_code]['total'] += 1
            state_data[task.state_code]['types'].add(task.document_type)
            
            if task.status == "completed":
                state_data[task.state_code]['completed'] += 1
            elif task.status == "failed":
                state_data[task.state_code]['failed'] += 1
            else:
                state_data[task.state_code]['pending'] += 1
                
        # Create dataframe
        report_data = []
        for state, data in sorted(state_data.items()):
            report_data.append({
                'State': state,
                'Total Files': data['total'],
                'Downloaded': data['completed'],
                'Failed': data['failed'],
                'Pending': data['pending'],
                'Progress': f"{data['completed'] / data['total'] * 100:.0f}%",
                'Document Types': ', '.join(sorted(data['types']))
            })
            
        df = pd.DataFrame(report_data)
        
        # Save report
        report_file = self.logs_dir / f"download_progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(report_file, index=False)
        
        return df
        
    def get_failed_downloads_report(self) -> pd.DataFrame:
        """Get detailed report of failed downloads"""
        if not self.failed_downloads:
            return pd.DataFrame()
            
        failed_data = []
        for task in self.failed_downloads:
            failed_data.append({
                'State': task.state_code,
                'Document Type': task.document_type,
                'Year': task.year,
                'URL': task.url,
                'Error': task.error_message,
                'Retries': task.retry_count
            })
            
        return pd.DataFrame(failed_data)

def populate_known_qap_urls(download_manager: QAPDownloadManager):
    """Populate download queue with known QAP URLs"""
    
    # Known QAP URLs - would be expanded with actual research
    known_urls = [
        # California
        {
            "state_code": "CA",
            "year": 2024,
            "url": "https://www.treasurer.ca.gov/ctcac/2024/December_11_2024_QAP_Regulations_FINAL.pdf",
            "document_type": "qap_current",
            "priority": 1
        },
        # Texas
        {
            "state_code": "TX",
            "year": 2024,
            "url": "https://www.tdhca.state.tx.us/multifamily/docs/24-QAP.pdf",
            "document_type": "qap_current",
            "priority": 1
        },
        # New York
        {
            "state_code": "NY",
            "year": 2024,
            "url": "https://hcr.ny.gov/system/files/documents/2024/01/2024-qap.pdf",
            "document_type": "qap_current",
            "priority": 1
        },
        # Florida
        {
            "state_code": "FL",
            "year": 2024,
            "url": "https://www.floridahousing.org/docs/default-source/programs/developers/2024-qap.pdf",
            "document_type": "qap_current",
            "priority": 1
        },
        # Add more states as URLs are discovered
    ]
    
    # Add tasks to download manager
    for url_info in known_urls:
        download_manager.add_download_task(
            url=url_info["url"],
            state_code=url_info["state_code"],
            document_type=url_info["document_type"],
            year=url_info["year"],
            priority=url_info.get("priority", 5)
        )
        
    return len(known_urls)

def main():
    """Run the download manager"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    
    # Initialize download manager
    manager = QAPDownloadManager(base_dir, max_workers=3)
    
    # Populate with known URLs
    print("\n=== QAP Download Manager ===\n")
    num_urls = populate_known_qap_urls(manager)
    print(f"Added {num_urls} QAP URLs to download queue")
    
    # Start downloads
    results = manager.download_all(show_progress=True)
    
    # Generate progress report
    print("\nGenerating progress report...")
    progress_df = manager.generate_progress_report()
    print("\nProgress by State:")
    print(progress_df.to_string())
    
    # Show failed downloads if any
    if manager.failed_downloads:
        print("\nFailed Downloads:")
        failed_df = manager.get_failed_downloads_report()
        print(failed_df.to_string())
        
    print(f"\nDownload logs saved to: {manager.logs_dir}")

if __name__ == "__main__":
    main()