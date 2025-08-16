#!/usr/bin/env python3
"""
Process TDHCA files in batches of 5 to avoid timeouts
Each batch takes ~5 minutes, well under the 2-minute timeout
"""

import sys
from pathlib import Path
from batch_with_checkpoints import CheckpointBatchProcessor

def process_small_batch(start_index=0, batch_size=5):
    """Process just 5 files at a time"""
    
    base_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites"
    
    # Get all PDFs
    pdf_path = Path(base_path)
    all_pdfs = sorted(list(pdf_path.glob("**/*.pdf")))
    total_files = len(all_pdfs)
    
    # Calculate batch range
    end_index = min(start_index + batch_size, total_files)
    batch_files = all_pdfs[start_index:end_index]
    
    print(f"🚀 PROCESSING BATCH: Files {start_index+1}-{end_index} of {total_files}")
    print(f"📁 Files in this batch:")
    for f in batch_files:
        print(f"   - {f.name}")
    print("="*60)
    
    # Process just this batch
    processor = CheckpointBatchProcessor(base_path)
    
    # Only process files in current batch
    for i, pdf_file in enumerate(batch_files):
        try:
            processor.log_status(f"Processing [{i+1}/{len(batch_files)}] in batch: {pdf_file.name}")
            result = processor.extractor.process_application_improved(pdf_file)
            
            if result and result.project_name:
                processor.log_status(f"✅ {result.project_name}: {result.street_address}, {result.city}")
            else:
                processor.log_status(f"❌ Failed to extract: {pdf_file.name}")
                
        except Exception as e:
            processor.log_status(f"💥 Error: {str(e)[:100]}")
    
    print(f"\n✅ BATCH COMPLETE!")
    print(f"📊 Processed files {start_index+1}-{end_index} of {total_files}")
    
    if end_index < total_files:
        print(f"\n🔄 NEXT BATCH: Run with start_index={end_index}")
        print(f"   python3 run_batch_5_files.py {end_index}")
    else:
        print(f"\n🎉 ALL FILES COMPLETE!")
        print(f"📋 Check batch_status.log for full history")
    
    return end_index, total_files

if __name__ == "__main__":
    # Get start index from command line
    start_index = 0
    if len(sys.argv) > 1:
        start_index = int(sys.argv[1])
    
    process_small_batch(start_index, batch_size=5)