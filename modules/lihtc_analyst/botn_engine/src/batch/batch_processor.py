#!/usr/bin/env python3
"""
Batch Site Processor - LIHTC Site Analysis at Scale

This module provides functionality for processing multiple LIHTC sites in parallel,
with error handling, progress tracking, and performance optimization.

Features:
- Parallel processing with configurable worker threads
- Individual site error handling with continuation
- Progress tracking with callback support
- Performance metrics and timing
- Memory-efficient processing for large datasets
- Result aggregation and error reporting
"""

import logging
import time
from typing import List, Dict, Any, Optional, Callable, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass
from datetime import datetime
import threading

# Import the core site analyzer
from ..core.site_analyzer import SiteAnalyzer


@dataclass
class ProcessingProgress:
    """Data class for progress tracking information"""
    completed: int
    total: int
    percentage: float
    current_site_id: Optional[str]
    elapsed_time: float
    estimated_remaining: Optional[float]
    successful: int
    failed: int
    current_rate: float  # sites per second


@dataclass
class ProcessingMetadata:
    """Data class for processing session metadata"""
    start_time: datetime
    end_time: Optional[datetime]
    total_sites: int
    successful_sites: int
    failed_sites: int
    total_processing_time: Optional[float]
    average_processing_time: Optional[float]
    processing_rate: Optional[float]  # sites per second
    version: str = "1.0.0"


class BatchSiteProcessor:
    """
    Batch processor for LIHTC site analysis with parallel execution and error handling
    
    Processes multiple sites using the existing SiteAnalyzer with configurable
    parallelism, progress tracking, and comprehensive error handling.
    """
    
    def __init__(
        self, 
        max_workers: int = 5,
        error_handling: str = 'continue',
        progress_callback: Optional[Callable[[ProcessingProgress], None]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize batch site processor
        
        Args:
            max_workers: Maximum number of concurrent analysis threads
            error_handling: Error handling strategy ('continue' or 'stop')
            progress_callback: Optional callback for progress updates
            logger: Optional logger for processing information
        """
        self.max_workers = max_workers
        self.error_handling = error_handling
        self.progress_callback = progress_callback
        self.logger = logger or logging.getLogger(__name__)
        
        # Processing state
        self._processing_metadata = None
        self._lock = threading.Lock()
        self._completed_count = 0
        self._successful_count = 0
        self._failed_count = 0
        self._start_time = None
        
        # Initialize site analyzer (will be created per thread for thread safety)
        self._analyzer_class = SiteAnalyzer
    
    def process_sites(self, sites_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple sites in parallel
        
        Args:
            sites_data: List of site dictionaries from CSV reader
            
        Returns:
            List of processing results with success/failure status
        """
        if not sites_data:
            self.logger.warning("No sites provided for processing")
            return []
        
        total_sites = len(sites_data)
        self.logger.info(f"Starting batch processing of {total_sites} sites with {self.max_workers} workers")
        
        # Initialize processing state
        self._start_time = time.time()
        self._completed_count = 0
        self._successful_count = 0
        self._failed_count = 0
        
        # Initialize metadata
        self._processing_metadata = ProcessingMetadata(
            start_time=datetime.now(),
            end_time=None,
            total_sites=total_sites,
            successful_sites=0,
            failed_sites=0,
            total_processing_time=None,
            average_processing_time=None,
            processing_rate=None
        )
        
        results = []
        
        # Send initial progress update
        self._send_progress_update(sites_data[0]['site_id'], 0, total_sites)
        
        try:
            if self.max_workers == 1:
                # Sequential processing for debugging or low-resource environments
                results = self._process_sites_sequential(sites_data)
            else:
                # Parallel processing
                results = self._process_sites_parallel(sites_data)
        
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            raise
        
        finally:
            # Update final metadata
            end_time = time.time()
            total_time = end_time - self._start_time
            
            self._processing_metadata.end_time = datetime.now()
            self._processing_metadata.successful_sites = self._successful_count
            self._processing_metadata.failed_sites = self._failed_count
            self._processing_metadata.total_processing_time = total_time
            self._processing_metadata.average_processing_time = total_time / total_sites if total_sites > 0 else 0
            self._processing_metadata.processing_rate = total_sites / total_time if total_time > 0 else 0
            
            # Send final progress update
            self._send_progress_update(None, total_sites, total_sites)
        
        self.logger.info(
            f"Batch processing completed: {self._successful_count} successful, "
            f"{self._failed_count} failed, {total_time:.2f}s total"
        )
        
        return results
    
    def _process_sites_sequential(self, sites_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process sites sequentially (single-threaded)"""
        results = []
        
        for i, site_data in enumerate(sites_data):
            result = self._process_single_site(site_data)
            results.append(result)
            
            # Update progress
            self._update_counters(result)
            self._send_progress_update(site_data['site_id'], i + 1, len(sites_data))
            
            # Check if we should stop on error
            if not result['success'] and self.error_handling == 'stop':
                self.logger.error(f"Stopping processing due to error in site {site_data['site_id']}")
                break
        
        return results
    
    def _process_sites_parallel(self, sites_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process sites in parallel using ThreadPoolExecutor"""
        results = [None] * len(sites_data)  # Pre-allocate to maintain order
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(self._process_single_site, site_data): i
                for i, site_data in enumerate(sites_data)
            }
            
            # Process completed tasks
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                site_data = sites_data[index]
                
                try:
                    result = future.result()
                    results[index] = result
                    
                    # Update progress
                    self._update_counters(result)
                    self._send_progress_update(
                        site_data['site_id'], 
                        self._completed_count, 
                        len(sites_data)
                    )
                    
                    # Check if we should stop on error
                    if not result['success'] and self.error_handling == 'stop':
                        self.logger.error(f"Stopping processing due to error in site {site_data['site_id']}")
                        # Cancel remaining futures
                        for remaining_future in future_to_index:
                            if not remaining_future.done():
                                remaining_future.cancel()
                        break
                
                except Exception as e:
                    # This shouldn't happen as _process_single_site handles all exceptions
                    self.logger.error(f"Unexpected error processing site {site_data['site_id']}: {e}")
                    error_result = {
                        'site_id': site_data['site_id'],
                        'success': False,
                        'error_message': f"Unexpected processing error: {e}",
                        'analysis_result': None
                    }
                    results[index] = error_result
                    self._update_counters(error_result)
        
        # Filter out None results (from cancelled futures)
        return [result for result in results if result is not None]
    
    def _process_single_site(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single site with error handling
        
        Args:
            site_data: Site dictionary with coordinates and metadata
            
        Returns:
            Processing result dictionary
        """
        site_id = site_data['site_id']
        
        try:
            # Create site analyzer (thread-safe)
            analyzer = self._analyzer_class()
            
            # Extract coordinates
            latitude = site_data['latitude']
            longitude = site_data['longitude']
            
            # Perform analysis
            self.logger.debug(f"Analyzing site {site_id} at ({latitude}, {longitude})")
            analysis_result = analyzer.analyze_site(
                latitude=latitude,
                longitude=longitude,
                state='CA',  # Default to California, could be made configurable
                project_type='family'  # Default project type
            )
            
            return {
                'site_id': site_id,
                'success': True,
                'analysis_result': analysis_result,
                'processing_time': time.time(),  # Could track individual processing times
                'input_data': site_data
            }
        
        except Exception as e:
            self.logger.error(f"Analysis failed for site {site_id}: {e}")
            return {
                'site_id': site_id,
                'success': False,
                'error_message': str(e),
                'error_type': type(e).__name__,
                'analysis_result': None,
                'input_data': site_data
            }
    
    def _update_counters(self, result: Dict[str, Any]) -> None:
        """Thread-safe counter updates"""
        with self._lock:
            self._completed_count += 1
            if result['success']:
                self._successful_count += 1
            else:
                self._failed_count += 1
    
    def _send_progress_update(self, current_site_id: Optional[str], completed: int, total: int) -> None:
        """Send progress update to callback if configured"""
        if not self.progress_callback:
            return
        
        elapsed_time = time.time() - self._start_time if self._start_time else 0
        percentage = (completed / total * 100) if total > 0 else 0
        
        # Calculate processing rate and estimated remaining time
        current_rate = completed / elapsed_time if elapsed_time > 0 else 0
        estimated_remaining = (total - completed) / current_rate if current_rate > 0 else None
        
        progress = ProcessingProgress(
            completed=completed,
            total=total,
            percentage=percentage,
            current_site_id=current_site_id,
            elapsed_time=elapsed_time,
            estimated_remaining=estimated_remaining,
            successful=self._successful_count,
            failed=self._failed_count,
            current_rate=current_rate
        )
        
        try:
            self.progress_callback(progress)
        except Exception as e:
            self.logger.warning(f"Progress callback failed: {e}")
    
    def get_processing_metadata(self) -> Optional[ProcessingMetadata]:
        """Get processing session metadata"""
        return self._processing_metadata
    
    def get_error_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate error summary from processing results
        
        Args:
            results: List of processing results
            
        Returns:
            Error summary dictionary
        """
        total_processed = len(results)
        successful = sum(1 for r in results if r['success'])
        failed = total_processed - successful
        
        # Collect error details
        error_details = []
        error_types = {}
        
        for result in results:
            if not result['success']:
                error_detail = {
                    'site_id': result['site_id'],
                    'error_message': result.get('error_message', 'Unknown error'),
                    'error_type': result.get('error_type', 'Unknown')
                }
                error_details.append(error_detail)
                
                # Count error types
                error_type = result.get('error_type', 'Unknown')
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_processed': total_processed,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total_processed * 100) if total_processed > 0 else 0,
            'error_details': error_details,
            'error_types': error_types
        }
    
    def get_successful_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter and return only successful analysis results
        
        Args:
            results: List of processing results
            
        Returns:
            List of successful results only
        """
        return [result for result in results if result['success']]
    
    def get_failed_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter and return only failed analysis results
        
        Args:
            results: List of processing results
            
        Returns:
            List of failed results only
        """
        return [result for result in results if not result['success']]


def main():
    """Command-line interface for testing batch processor"""
    import sys
    import argparse
    from pathlib import Path
    
    # Add current directory to path for imports
    current_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(current_dir))
    
    from src.batch.csv_reader import CSVSiteReader
    
    parser = argparse.ArgumentParser(description='Batch process LIHTC sites from CSV')
    parser.add_argument('csv_file', help='Path to CSV file with site data')
    parser.add_argument('--workers', type=int, default=5, help='Number of worker threads')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    def progress_callback(progress: ProcessingProgress):
        """Simple progress callback for CLI"""
        print(f"Progress: {progress.completed}/{progress.total} "
              f"({progress.percentage:.1f}%) - "
              f"Success: {progress.successful}, Failed: {progress.failed}, "
              f"Rate: {progress.current_rate:.2f} sites/sec")
    
    try:
        # Read CSV
        reader = CSVSiteReader()
        sites_data = reader.load_csv(args.csv_file)
        print(f"Loaded {len(sites_data)} sites from {args.csv_file}")
        
        # Process sites
        processor = BatchSiteProcessor(
            max_workers=args.workers,
            progress_callback=progress_callback
        )
        
        results = processor.process_sites(sites_data)
        
        # Show summary
        error_summary = processor.get_error_summary(results)
        metadata = processor.get_processing_metadata()
        
        print(f"\n{'='*60}")
        print("BATCH PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total Sites: {error_summary['total_processed']}")
        print(f"Successful: {error_summary['successful']} ({error_summary['success_rate']:.1f}%)")
        print(f"Failed: {error_summary['failed']}")
        
        if metadata:
            print(f"Processing Time: {metadata.total_processing_time:.2f} seconds")
            print(f"Average Time per Site: {metadata.average_processing_time:.2f} seconds")
            print(f"Processing Rate: {metadata.processing_rate:.2f} sites/second")
        
        if error_summary['error_details']:
            print(f"\nErrors:")
            for error in error_summary['error_details'][:5]:  # Show first 5
                print(f"  {error['site_id']}: {error['error_message']}")
            
            if len(error_summary['error_details']) > 5:
                print(f"  ... and {len(error_summary['error_details']) - 5} more errors")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()