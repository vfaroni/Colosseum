#!/usr/bin/env python3
"""
CSV Sites Batch Processor - Complete Workflow CLI

This script provides a command-line interface for the complete CSV batch processing
workflow: CSV reading → Site analysis → Report generation.

Features:
- Complete end-to-end processing
- Progress tracking with real-time updates
- Multiple output formats (CSV summary + JSON detailed)
- Error handling and recovery
- Performance metrics and reporting
- Configurable parallel processing
"""

import sys
import argparse
import logging
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add src to path for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from src.batch.csv_reader import SiteDataReader
from src.batch.batch_processor import BatchSiteProcessor, ProcessingProgress
from src.batch.batch_reporter import BatchReporter


class CSVBatchProcessor:
    """
    Complete CSV batch processing workflow manager
    
    Orchestrates the entire process from CSV input to final reports
    with comprehensive error handling and progress tracking.
    """
    
    def __init__(
        self,
        max_workers: int = 5,
        output_formats: Optional[list] = None,
        verbose: bool = False
    ):
        """
        Initialize CSV batch processor
        
        Args:
            max_workers: Number of parallel processing threads
            output_formats: List of output formats ('csv', 'json')
            verbose: Enable verbose logging
        """
        self.max_workers = max_workers
        self.output_formats = output_formats or ['csv', 'json']
        self.verbose = verbose
        
        # Set up logging
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.file_reader = SiteDataReader(logger=self.logger)
        self.batch_processor = BatchSiteProcessor(
            max_workers=max_workers,
            progress_callback=self._progress_callback,
            logger=self.logger
        )
        self.reporter = BatchReporter(logger=self.logger)
        
        # Processing state
        self._interrupted = False
        self._current_progress = None
        
        # Set up signal handlers for graceful interruption
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def process_csv_file(
        self, 
        csv_path: str, 
        output_base: str,
        validate_only: bool = False
    ) -> dict:
        """
        Process CSV file through complete workflow
        
        Args:
            csv_path: Path to input CSV file
            output_base: Base name for output files
            validate_only: Only validate CSV without processing
            
        Returns:
            Processing results summary
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Validate and load CSV
            self.logger.info(f"Loading sites from: {csv_path}")
            
            # Quick validation first
            validation_result = self.file_reader.validate_file(csv_path)
            
            if not validation_result['valid']:
                self.logger.error("CSV validation failed:")
                for error in validation_result['errors']:
                    self.logger.error(f"  - {error}")
                return {
                    'success': False,
                    'error': 'CSV validation failed',
                    'validation_errors': validation_result['errors']
                }
            
            self.logger.info(
                f"CSV validation passed: {validation_result['row_count']} sites, "
                f"{validation_result['column_count']} columns"
            )
            
            if validate_only:
                return {
                    'success': True,
                    'validation_only': True,
                    'validation_result': validation_result
                }
            
            # Load full file data
            sites_data = self.file_reader.load_file(csv_path)
            self.logger.info(f"Successfully loaded {len(sites_data)} sites")
            
            # Step 2: Process sites
            self.logger.info(f"Starting batch processing with {self.max_workers} workers...")
            
            processing_results = self.batch_processor.process_sites(sites_data)
            
            if self._interrupted:
                self.logger.warning("Processing was interrupted by user")
                return {
                    'success': False,
                    'error': 'Processing interrupted by user',
                    'partial_results': processing_results
                }
            
            # Step 3: Generate reports
            self.logger.info("Generating reports...")
            
            # Set processing metadata for reports
            metadata = self.batch_processor.get_processing_metadata()
            if metadata:
                self.reporter.set_processing_metadata(metadata.__dict__)
            
            # Generate output files
            output_paths = self.reporter.export_multiple_formats(
                processing_results, 
                output_base, 
                self.output_formats
            )
            
            # Generate summary statistics
            error_summary = self.batch_processor.get_error_summary(processing_results)
            stats = self.reporter.generate_summary_statistics(processing_results)
            
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            return {
                'success': True,
                'total_sites': len(sites_data),
                'processing_results': processing_results,
                'error_summary': error_summary,
                'statistics': stats,
                'output_files': output_paths,
                'processing_time': total_time,
                'metadata': metadata.__dict__ if metadata else None
            }
        
        except Exception as e:
            self.logger.error(f"Processing failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _progress_callback(self, progress: ProcessingProgress) -> None:
        """Handle progress updates from batch processor"""
        self._current_progress = progress
        
        # Print progress update
        if progress.current_site_id:
            print(f"\rProcessing: {progress.current_site_id} "
                  f"({progress.completed}/{progress.total}) "
                  f"[{progress.percentage:.1f}%] "
                  f"Success: {progress.successful}, Failed: {progress.failed} "
                  f"Rate: {progress.current_rate:.2f}/sec", end='', flush=True)
        else:
            # Final update
            print(f"\rCompleted: {progress.completed}/{progress.total} sites "
                  f"({progress.percentage:.1f}%) "
                  f"Success: {progress.successful}, Failed: {progress.failed} "
                  f"Time: {progress.elapsed_time:.1f}s")
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self._interrupted = True
        
        if self._current_progress:
            print(f"\n\nInterrupted at {self._current_progress.completed}/{self._current_progress.total} sites")
            print("Finishing current analyses and generating partial report...")


def create_sample_csv(output_path: str) -> None:
    """Create a sample CSV file for testing"""
    reader = SiteDataReader()
    sample_content = reader.get_sample_csv_format()
    
    with open(output_path, 'w') as f:
        f.write(sample_content)
    
    print(f"Sample CSV created: {output_path}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='Process LIHTC sites from CSV file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process sites with default settings
  python3 scripts/process_csv_sites.py sites.csv

  # Process with custom output name and more workers
  python3 scripts/process_csv_sites.py sites.csv -o california_analysis -w 8

  # Validate CSV without processing
  python3 scripts/process_csv_sites.py sites.csv --validate-only

  # Generate sample CSV file
  python3 scripts/process_csv_sites.py --create-sample sample_sites.csv

  # Process with specific output formats
  python3 scripts/process_csv_sites.py sites.csv --format csv json
        """
    )
    
    parser.add_argument(
        'csv_file', 
        nargs='?',
        help='Path to CSV or Excel file with site data'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='batch_analysis',
        help='Base name for output files (default: batch_analysis)'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=5,
        help='Number of parallel processing threads (default: 5)'
    )
    
    parser.add_argument(
        '--format',
        nargs='+',
        choices=['csv', 'json'],
        default=['csv', 'json'],
        help='Output formats to generate (default: csv json)'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate CSV file without processing'
    )
    
    parser.add_argument(
        '--create-sample',
        metavar='OUTPUT_PATH',
        help='Create a sample CSV file and exit'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Handle sample CSV creation
    if args.create_sample:
        create_sample_csv(args.create_sample)
        return
    
    # Validate required arguments
    if not args.csv_file:
        parser.error("File path is required (use --create-sample to generate sample)")
    
    if not Path(args.csv_file).exists():
        print(f"❌ Error: File not found: {args.csv_file}")
        return 1
    
    # Process CSV file
    try:
        processor = CSVBatchProcessor(
            max_workers=args.workers,
            output_formats=args.format,
            verbose=args.verbose
        )
        
        print(f"{'='*80}")
        print("LIHTC SITE BATCH PROCESSOR")
        print(f"{'='*80}")
        print(f"Input: {args.csv_file}")
        print(f"Output: {args.output}_{{summary.csv, detailed.json}}")
        print(f"Workers: {args.workers}")
        print(f"Formats: {', '.join(args.format)}")
        
        if args.validate_only:
            print("Mode: Validation only")
        
        print(f"{'='*80}")
        
        result = processor.process_csv_file(
            csv_path=args.csv_file,
            output_base=args.output,
            validate_only=args.validate_only
        )
        
        if result['success']:
            if args.validate_only:
                print("✅ CSV validation successful")
                validation = result['validation_result']
                print(f"   Sites: {validation['row_count']}")
                print(f"   Columns: {validation['column_count']}")
                print(f"   Required columns present: {validation['required_columns_present']}")
            else:
                print(f"\n{'='*80}")
                print("PROCESSING SUMMARY")
                print(f"{'='*80}")
                
                stats = result['statistics']
                error_summary = result['error_summary']
                
                print(f"Total Sites: {result['total_sites']}")
                print(f"Successful: {stats['successful_analyses']} ({stats['success_rate']:.1f}%)")
                print(f"Failed: {stats['failed_analyses']}")
                print(f"Processing Time: {result['processing_time']:.2f} seconds")
                
                if result.get('metadata'):
                    metadata = result['metadata']
                    print(f"Average Time per Site: {metadata.get('average_processing_time', 0):.2f} seconds")
                    print(f"Processing Rate: {metadata.get('processing_rate', 0):.2f} sites/second")
                
                # Show score statistics if available
                if stats.get('avg_ctcac_points'):
                    print(f"\nSCORING STATISTICS:")
                    print(f"Average CTCAC Score: {stats['avg_ctcac_points']:.1f}")
                    print(f"Score Range: {stats['min_ctcac_points']:.1f} - {stats['max_ctcac_points']:.1f}")
                
                # Show federal qualification statistics
                if stats.get('qct_qualified_count') is not None:
                    print(f"\nFEDERAL QUALIFICATION:")
                    print(f"QCT Qualified: {stats['qct_qualified_count']} ({stats['qct_qualification_rate']:.1f}%)")
                    print(f"DDA Qualified: {stats['dda_qualified_count']} ({stats['dda_qualification_rate']:.1f}%)")
                    print(f"Any Federal: {stats['federal_qualified_count']}")
                
                # Show resource area distribution
                if stats.get('resource_category_distribution'):
                    print(f"\nRESOURCE AREAS:")
                    for category, count in stats['resource_category_distribution'].items():
                        print(f"  {category}: {count}")
                
                # Show error summary if there are failures
                if error_summary['failed'] > 0:
                    print(f"\nERRORS:")
                    for error_type, count in error_summary.get('error_types', {}).items():
                        print(f"  {error_type}: {count}")
                    
                    # Show first few error details
                    if error_summary.get('error_details'):
                        print(f"\nError Details (first 3):")
                        for error in error_summary['error_details'][:3]:
                            print(f"  {error['site_id']}: {error['error_message']}")
                
                print(f"\nOUTPUT FILES:")
                for format_type, path in result['output_files'].items():
                    print(f"  {format_type.upper()}: {path}")
                
                print(f"\n✅ Processing completed successfully!")
        
        else:
            print(f"❌ Processing failed: {result['error']}")
            if result.get('validation_errors'):
                print("Validation errors:")
                for error in result['validation_errors']:
                    print(f"  - {error}")
            return 1
    
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Processing interrupted by user")
        return 1
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())