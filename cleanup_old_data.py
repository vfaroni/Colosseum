#!/usr/bin/env python3
"""
Automated cleanup script for Colosseum LIHTC Platform
Archives old data files to S3 and removes them from local storage
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cloud_storage import S3CloudStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/cleanup.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)


def cleanup_directory(storage: S3CloudStorage, directory: str, days_old: int, 
                     delete_local: bool = False, dry_run: bool = False) -> tuple:
    """
    Clean up old files in a directory by archiving to S3
    
    Args:
        storage: S3CloudStorage instance
        directory: Directory to clean
        days_old: Age threshold in days
        delete_local: Whether to delete local files after upload
        dry_run: If True, only show what would be done without actually doing it
    
    Returns:
        Tuple of (files_processed, files_archived, total_size_mb)
    """
    if not os.path.exists(directory):
        logger.warning(f"Directory does not exist: {directory}")
        return 0, 0, 0
    
    files_processed = 0
    files_archived = 0
    total_size = 0
    
    logger.info(f"{'[DRY RUN] ' if dry_run else ''}Processing directory: {directory}")
    
    if dry_run:
        # In dry run mode, just list what would be archived
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_stat = os.stat(file_path)
                file_modified = datetime.fromtimestamp(file_stat.st_mtime)
                
                if file_modified < cutoff_date:
                    size_mb = file_stat.st_size / (1024 * 1024)
                    logger.info(f"  Would archive: {file_path} ({size_mb:.2f} MB)")
                    files_processed += 1
                    total_size += file_stat.st_size
    else:
        # Actually perform the archive
        results = storage.archive_old_files(directory, days_old=days_old, delete_local=delete_local)
        files_processed = len(results)
        files_archived = sum(1 for v in results.values() if v)
        
        # Calculate total size of archived files
        for file_path in results:
            if results[file_path] and os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
    
    total_size_mb = total_size / (1024 * 1024)
    return files_processed, files_archived, total_size_mb


def main():
    parser = argparse.ArgumentParser(
        description='Archive old Colosseum data files to S3 cloud storage'
    )
    parser.add_argument(
        '--days', 
        type=int, 
        default=7,
        help='Archive files older than this many days (default: 7)'
    )
    parser.add_argument(
        '--delete-local',
        action='store_true',
        help='Delete local files after successful upload to S3'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be archived without actually doing it'
    )
    parser.add_argument(
        '--directories',
        nargs='*',
        default=['analysis_results', 'reports', 'logs', 'temp_data'],
        help='Directories to clean (default: analysis_results reports logs temp_data)'
    )
    parser.add_argument(
        '--bucket',
        help='S3 bucket name (overrides environment variable)'
    )
    
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logger.info("=" * 60)
    logger.info(f"Starting cleanup process - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Settings: days_old={args.days}, delete_local={args.delete_local}, dry_run={args.dry_run}")
    
    try:
        # Initialize S3 storage
        storage = S3CloudStorage(bucket_name=args.bucket)
        
        total_files = 0
        total_archived = 0
        total_size = 0
        
        # Process each directory
        for directory in args.directories:
            files_processed, files_archived, size_mb = cleanup_directory(
                storage, directory, args.days, args.delete_local, args.dry_run
            )
            
            total_files += files_processed
            total_archived += files_archived
            total_size += size_mb
            
            if args.dry_run:
                logger.info(f"  {directory}: Would archive {files_processed} files ({size_mb:.2f} MB)")
            else:
                logger.info(f"  {directory}: Archived {files_archived}/{files_processed} files ({size_mb:.2f} MB)")
        
        # Summary
        logger.info("-" * 60)
        if args.dry_run:
            logger.info(f"DRY RUN SUMMARY: Would archive {total_files} files totaling {total_size:.2f} MB")
        else:
            logger.info(f"SUMMARY: Successfully archived {total_archived}/{total_files} files")
            logger.info(f"Total size: {total_size:.2f} MB")
            if args.delete_local and total_archived > 0:
                logger.info(f"Local files deleted: {total_archived}")
        
        logger.info(f"Cleanup completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        return 0 if total_archived == total_files or args.dry_run else 1
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())