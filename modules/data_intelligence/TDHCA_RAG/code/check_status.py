#!/usr/bin/env python3
"""
Check the status of TDHCA batch processing
Shows what's completed, what's pending, and current progress
"""

import json
from pathlib import Path
import pandas as pd
from datetime import datetime

def check_batch_status():
    """Display current batch processing status"""
    
    print("📊 TDHCA BATCH PROCESSING STATUS")
    print("="*60)
    
    # Check for checkpoint file
    checkpoint_file = "batch_checkpoint.json"
    status_log = "batch_status.log"
    temp_csv = "batch_results_temp.csv"
    
    if Path(checkpoint_file).exists():
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
        
        print(f"✅ Active checkpoint found!")
        print(f"📁 Processed files: {len(checkpoint['processed_files'])}")
        print(f"📁 Total files: {checkpoint['total_files']}")
        print(f"📊 Progress: {len(checkpoint['processed_files'])/checkpoint['total_files']*100:.1f}%")
        print(f"⏰ Last update: {checkpoint['last_update']}")
        
        # Show temporary results
        if Path(temp_csv).exists():
            df = pd.read_csv(temp_csv)
            successful = len(df[df['Status'] == 'SUCCESS'])
            failed = len(df[df['Status'] != 'SUCCESS'])
            
            print(f"\n📈 Results so far:")
            print(f"   ✅ Successful: {successful}")
            print(f"   ❌ Failed: {failed}")
            print(f"   📊 Success rate: {successful/len(df)*100:.1f}%")
            
            # Show last 5 processed
            print(f"\n🕐 Last 5 files processed:")
            for _, row in df.tail(5).iterrows():
                status_icon = "✅" if row['Status'] == 'SUCCESS' else "❌"
                print(f"   {status_icon} {row['File Name']}: {row['Project Name']} ({row['Processing Time']})")
    else:
        print("❌ No active checkpoint found")
    
    # Check for completed batches
    print(f"\n📁 Completed batch files:")
    excel_files = list(Path(".").glob("TDHCA_Batch_Results_*.xlsx"))
    if excel_files:
        for file in sorted(excel_files):
            print(f"   - {file.name}")
    else:
        print("   None found")
    
    # Show recent log entries
    if Path(status_log).exists():
        print(f"\n📋 Recent activity (last 10 entries):")
        with open(status_log, 'r') as f:
            lines = f.readlines()
            for line in lines[-10:]:
                print(f"   {line.strip()}")
    
    # Show all PDFs to process
    base_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites"
    pdf_path = Path(base_path)
    all_pdfs = sorted(list(pdf_path.glob("**/*.pdf")))
    
    print(f"\n📂 Total PDF files found: {len(all_pdfs)}")
    print(f"📍 Base directory: {base_path}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if Path(checkpoint_file).exists():
        print("   - Run 'python3 batch_with_checkpoints.py' to resume")
        print("   - Or run 'python3 run_batch_5_files.py' to process next 5 files")
    else:
        print("   - Run 'python3 run_batch_5_files.py' to start processing")
        print("   - This will process 5 files at a time to avoid timeouts")

if __name__ == "__main__":
    check_batch_status()