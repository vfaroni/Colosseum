#!/usr/bin/env python3
"""
AWS S3 Cloud Storage Integration Module for Colosseum LIHTC Platform
Handles upload, download, and management of analysis results and reports in S3
"""

import os
import json
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class S3CloudStorage:
    """Manages S3 operations for Colosseum platform data"""
    
    def __init__(self, bucket_name: str = None, region: str = 'us-east-1'):
        """
        Initialize S3 client
        
        Args:
            bucket_name: S3 bucket name (can be overridden by environment variable)
            region: AWS region (default: us-east-1)
        """
        self.bucket_name = bucket_name or os.environ.get('COLOSSEUM_S3_BUCKET', 'colosseum-lihtc-data')
        self.region = region
        
        try:
            self.s3_client = boto3.client('s3', region_name=region)
            self.s3_resource = boto3.resource('s3', region_name=region)
            logger.info(f"S3 client initialized for bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please configure AWS CLI or set environment variables.")
            raise
    
    def upload_file(self, local_path: str, s3_key: str = None, metadata: Dict[str, str] = None) -> bool:
        """
        Upload a file to S3
        
        Args:
            local_path: Path to local file
            s3_key: S3 object key (default: uses local filename with date prefix)
            metadata: Optional metadata to attach to the S3 object
        
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(local_path):
            logger.error(f"File not found: {local_path}")
            return False
        
        if s3_key is None:
            # Generate S3 key with date prefix for organization
            date_prefix = datetime.now().strftime('%Y/%m/%d')
            filename = os.path.basename(local_path)
            s3_key = f"{date_prefix}/{filename}"
        
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            # Determine content type
            if local_path.endswith('.json'):
                extra_args['ContentType'] = 'application/json'
            elif local_path.endswith('.txt'):
                extra_args['ContentType'] = 'text/plain'
            elif local_path.endswith('.md'):
                extra_args['ContentType'] = 'text/markdown'
            
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key, ExtraArgs=extra_args)
            logger.info(f"Successfully uploaded {local_path} to s3://{self.bucket_name}/{s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return False
    
    def upload_directory(self, local_dir: str, s3_prefix: str = None) -> Dict[str, bool]:
        """
        Upload all files in a directory to S3
        
        Args:
            local_dir: Path to local directory
            s3_prefix: S3 prefix for uploaded files
        
        Returns:
            Dictionary mapping filenames to upload success status
        """
        if not os.path.isdir(local_dir):
            logger.error(f"Directory not found: {local_dir}")
            return {}
        
        results = {}
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, local_dir)
                
                if s3_prefix:
                    s3_key = f"{s3_prefix}/{relative_path}"
                else:
                    s3_key = relative_path
                
                results[local_path] = self.upload_file(local_path, s3_key)
        
        return results
    
    def download_file(self, s3_key: str, local_path: str = None) -> bool:
        """
        Download a file from S3
        
        Args:
            s3_key: S3 object key
            local_path: Local path to save file (default: current directory)
        
        Returns:
            True if successful, False otherwise
        """
        if local_path is None:
            local_path = os.path.basename(s3_key)
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            logger.info(f"Successfully downloaded s3://{self.bucket_name}/{s3_key} to {local_path}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to download {s3_key}: {e}")
            return False
    
    def list_files(self, prefix: str = "", max_results: int = 1000) -> List[Dict[str, Any]]:
        """
        List files in S3 bucket with optional prefix filter
        
        Args:
            prefix: S3 prefix to filter results
            max_results: Maximum number of results to return
        
        Returns:
            List of dictionaries containing file information
        """
        files = []
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=prefix,
                PaginationConfig={'MaxItems': max_results}
            )
            
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        files.append({
                            'key': obj['Key'],
                            'size': obj['Size'],
                            'last_modified': obj['LastModified'].isoformat(),
                            'etag': obj['ETag']
                        })
            
            logger.info(f"Found {len(files)} files with prefix '{prefix}'")
            return files
            
        except ClientError as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3
        
        Args:
            s3_key: S3 object key to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Successfully deleted s3://{self.bucket_name}/{s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete {s3_key}: {e}")
            return False
    
    def archive_old_files(self, local_dir: str, days_old: int = 7, delete_local: bool = False) -> Dict[str, bool]:
        """
        Archive files older than specified days to S3
        
        Args:
            local_dir: Local directory to scan
            days_old: Age threshold in days
            delete_local: Whether to delete local files after successful upload
        
        Returns:
            Dictionary mapping filenames to archive success status
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        results = {}
        
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_stat = os.stat(file_path)
                file_modified = datetime.fromtimestamp(file_stat.st_mtime)
                
                if file_modified < cutoff_date:
                    # Archive to S3 with archive prefix
                    archive_key = f"archive/{os.path.relpath(file_path, local_dir)}"
                    success = self.upload_file(file_path, archive_key, 
                                             metadata={'archived_date': datetime.now().isoformat()})
                    results[file_path] = success
                    
                    if success and delete_local:
                        try:
                            os.remove(file_path)
                            logger.info(f"Deleted local file: {file_path}")
                        except Exception as e:
                            logger.error(f"Failed to delete local file {file_path}: {e}")
        
        return results
    
    def get_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for temporary access to an S3 object
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
        
        Returns:
            Presigned URL string or None if failed
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {s3_key}: {e}")
            return None


def upload_analysis_results(filepath: str) -> bool:
    """
    Convenience function to upload analysis results to S3
    
    Args:
        filepath: Path to analysis result file
    
    Returns:
        True if successful, False otherwise
    """
    storage = S3CloudStorage()
    return storage.upload_file(filepath, s3_key=f"analysis_results/{os.path.basename(filepath)}")


def upload_report(filepath: str) -> bool:
    """
    Convenience function to upload reports to S3
    
    Args:
        filepath: Path to report file
    
    Returns:
        True if successful, False otherwise
    """
    storage = S3CloudStorage()
    return storage.upload_file(filepath, s3_key=f"reports/{os.path.basename(filepath)}")


def cleanup_old_local_files(days: int = 7):
    """
    Archive and remove old local files
    
    Args:
        days: Age threshold in days for archiving
    """
    storage = S3CloudStorage()
    
    directories = [
        'analysis_results',
        'reports',
        'logs',
        'temp_data'
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"Archiving old files from {directory}...")
            results = storage.archive_old_files(directory, days_old=days, delete_local=True)
            archived = sum(1 for v in results.values() if v)
            print(f"Archived {archived}/{len(results)} files from {directory}")


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="S3 Cloud Storage Management for Colosseum")
    parser.add_argument('action', choices=['upload', 'download', 'list', 'cleanup'],
                       help='Action to perform')
    parser.add_argument('--file', help='File path for upload/download')
    parser.add_argument('--key', help='S3 key for operations')
    parser.add_argument('--prefix', help='S3 prefix for list operation')
    parser.add_argument('--days', type=int, default=7, help='Days threshold for cleanup')
    
    args = parser.parse_args()
    
    storage = S3CloudStorage()
    
    if args.action == 'upload' and args.file:
        success = storage.upload_file(args.file, args.key)
        print(f"Upload {'successful' if success else 'failed'}")
    
    elif args.action == 'download' and args.key:
        success = storage.download_file(args.key, args.file)
        print(f"Download {'successful' if success else 'failed'}")
    
    elif args.action == 'list':
        files = storage.list_files(prefix=args.prefix or '')
        for file in files:
            print(f"{file['key']} - {file['size']} bytes - {file['last_modified']}")
    
    elif args.action == 'cleanup':
        cleanup_old_local_files(days=args.days)