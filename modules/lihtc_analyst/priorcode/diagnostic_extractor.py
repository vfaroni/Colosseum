#!/usr/bin/env python3
"""
Diagnostic CTCAC Extractor - Find out what's wrong
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

def main():
    print("🔍 DIAGNOSTIC MODE - Finding the Issue")
    print("=" * 50)
    
    # Define file paths
    input_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data'
    output_path_4p = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data/JSON_data/4p'
    output_path_9p = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data/JSON_data/9p'
    log_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/logs'
    
    print(f"📁 Checking paths...")
    print(f"Input: {input_path}")
    print(f"4% Output: {output_path_4p}")
    print(f"9% Output: {output_path_9p}")
    print(f"Logs: {log_path}")
    
    # Check if paths exist
    input_dir = Path(input_path)
    print(f"\n🔍 Path Analysis:")
    print(f"Input directory exists: {input_dir.exists()}")
    
    if not input_dir.exists():
        print("❌ INPUT DIRECTORY DOES NOT EXIST!")
        print("This is likely the problem.")
        
        # Check parent directory
        parent_dir = input_dir.parent
        print(f"\nChecking parent directory: {parent_dir}")
        print(f"Parent exists: {parent_dir.exists()}")
        
        if parent_dir.exists():
            print("Contents of parent directory:")
            for item in parent_dir.iterdir():
                print(f"  - {item.name} ({'folder' if item.is_dir() else 'file'})")
        
        return
    
    # Check for Excel files
    print(f"\n📊 Looking for Excel files...")
    excel_files = list(input_dir.glob("*.xlsx")) + list(input_dir.glob("*.xls"))
    print(f"Found {len(excel_files)} Excel files")
    
    if len(excel_files) == 0:
        print("❌ NO EXCEL FILES FOUND!")
        print("Let's see what's in the directory:")
        
        all_files = list(input_dir.iterdir())
        print(f"Total items in directory: {len(all_files)}")
        
        # Show first 20 items
        for i, item in enumerate(all_files[:20]):
            file_type = "folder" if item.is_dir() else "file"
            print(f"  {i+1}. {item.name} ({file_type})")
        
        if len(all_files) > 20:
            print(f"  ... and {len(all_files) - 20} more items")
        
        return
    
    # Show sample Excel files
    print(f"\nSample Excel files found:")
    for i, file_path in enumerate(excel_files[:5]):
        print(f"  {i+1}. {file_path.name}")
    
    # Check output directories
    print(f"\n📁 Checking output directories...")
    output_4p = Path(output_path_4p)
    output_9p = Path(output_path_9p)
    log_dir = Path(log_path)
    
    print(f"4% output exists: {output_4p.exists()}")
    print(f"9% output exists: {output_9p.exists()}")
    print(f"Log directory exists: {log_dir.exists()}")
    
    # Try to create directories
    try:
        output_4p.mkdir(parents=True, exist_ok=True)
        output_9p.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Successfully created/verified output directories")
    except Exception as e:
        print(f"❌ Error creating directories: {e}")
        return
    
    # Check Python imports
    print(f"\n🐍 Checking Python imports...")
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except Exception as e:
        print(f"❌ pandas import failed: {e}")
    
    try:
        import openpyxl
        print("✅ openpyxl imported successfully")
    except Exception as e:
        print(f"❌ openpyxl import failed: {e}")
    
    try:
        import logging
        print("✅ logging imported successfully")
    except Exception as e:
        print(f"❌ logging import failed: {e}")
    
    # Test basic file access
    print(f"\n🧪 Testing file access...")
    try:
        test_file = excel_files[0]
        print(f"Testing file: {test_file.name}")
        
        # Try to open with openpyxl
        import openpyxl
        workbook = openpyxl.load_workbook(test_file, data_only=True)
        print(f"✅ Successfully opened Excel file")
        print(f"Sheets: {workbook.sheetnames}")
        workbook.close()
        
    except Exception as e:
        print(f"❌ Error opening Excel file: {e}")
        return
    
    # Test logging
    print(f"\n📋 Testing logging...")
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_log_file = log_dir / f"diagnostic_test_{timestamp}.log"
        
        import logging
        logging.basicConfig(
            filename=test_log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        logging.info("Diagnostic test log entry")
        print(f"✅ Created test log file: {test_log_file.name}")
        
    except Exception as e:
        print(f"❌ Error with logging: {e}")
    
    # Summary
    print(f"\n📊 DIAGNOSTIC SUMMARY:")
    print(f"✅ Input directory: {'✅' if input_dir.exists() else '❌'}")
    print(f"✅ Excel files found: {len(excel_files)}")
    print(f"✅ Output directories: {'✅' if all([output_4p.exists(), output_9p.exists(), log_dir.exists()]) else '❌'}")
    print(f"✅ Python imports: Check individual results above")
    
    if len(excel_files) > 0:
        print(f"\n🚀 Everything looks good! The extractor should work.")
        print(f"If it's still not working, the issue might be:")
        print(f"   1. The main() function not being called")
        print(f"   2. The extractor class not being instantiated")
        print(f"   3. Silent errors in the extraction process")
    else:
        print(f"\n❌ Main issue: No Excel files found")

if __name__ == "__main__":
    main()