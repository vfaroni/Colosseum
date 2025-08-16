#!/usr/bin/env python3
"""
TDHCA Batch Processor with Checkpoint System
- Saves progress after each file
- Can resume from interruptions
- Creates status log file for monitoring
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import sys
from improved_tdhca_extractor import ImprovedTDHCAExtractor

class CheckpointBatchProcessor:
    def __init__(self, base_path):
        self.base_path = base_path
        self.checkpoint_file = "batch_checkpoint.json"
        self.status_log_file = "batch_status.log"
        self.results_csv = "batch_results_temp.csv"
        self.extractor = ImprovedTDHCAExtractor(base_path)
        
    def log_status(self, message):
        """Write status to both console and log file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.status_log_file, 'a') as f:
            f.write(log_message + '\n')
    
    def save_checkpoint(self, processed_files, total_files, results):
        """Save current progress"""
        checkpoint = {
            'processed_files': processed_files,
            'total_files': total_files,
            'last_update': datetime.now().isoformat(),
            'results_count': len(results)
        }
        
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        # Also save results to CSV for safety
        if results:
            df = pd.DataFrame(results)
            df.to_csv(self.results_csv, index=False)
    
    def load_checkpoint(self):
        """Load previous progress if exists"""
        if Path(self.checkpoint_file).exists():
            with open(self.checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
            
            # Load previous results
            results = []
            if Path(self.results_csv).exists():
                df = pd.read_csv(self.results_csv)
                results = df.to_dict('records')
            
            return checkpoint['processed_files'], results
        
        return [], []
    
    def process_batch(self, resume=True):
        """Process all PDFs with checkpoint support"""
        
        # Find all PDFs
        pdf_path = Path(self.base_path)
        all_pdfs = sorted(list(pdf_path.glob("**/*.pdf")))
        total_files = len(all_pdfs)
        
        # Load checkpoint if resuming
        processed_files = []
        results = []
        
        if resume:
            processed_files, results = self.load_checkpoint()
            if processed_files:
                self.log_status(f"RESUMING from checkpoint: {len(processed_files)} files already processed")
        
        self.log_status(f"BATCH START: {total_files} total files to process")
        self.log_status(f"Base path: {self.base_path}")
        
        # Process each file
        start_time = datetime.now()
        
        for i, pdf_file in enumerate(all_pdfs):
            filename = pdf_file.name
            
            # Skip if already processed
            if filename in processed_files:
                self.log_status(f"Skipping {filename} - already processed")
                continue
            
            # Process file
            file_start_time = datetime.now()
            self.log_status(f"Processing [{i+1}/{total_files}]: {filename}")
            
            try:
                result = self.extractor.process_application_improved(pdf_file)
                processing_time = (datetime.now() - file_start_time).total_seconds()
                
                if result:
                    result_dict = {
                        'File Name': filename,
                        'Project Name': result.project_name or 'NOT_FOUND',
                        'Street Address': result.street_address or 'NOT_FOUND',
                        'City': result.city or 'NOT_FOUND',
                        'ZIP Code': result.zip_code or 'NOT_FOUND',
                        'County': result.county or 'NOT_FOUND',
                        'Total Units': result.total_units or 0,
                        'Developer': result.developer_name or 'NOT_FOUND',
                        'Processing Time': f"{processing_time:.1f}s",
                        'Status': 'SUCCESS'
                    }
                    results.append(result_dict)
                    
                    self.log_status(f"✅ SUCCESS: {result.project_name} ({processing_time:.1f}s)")
                else:
                    results.append({
                        'File Name': filename,
                        'Project Name': 'EXTRACTION_FAILED',
                        'Street Address': '', 'City': '', 'ZIP Code': '', 
                        'County': '', 'Total Units': 0, 'Developer': '',
                        'Processing Time': f"{processing_time:.1f}s",
                        'Status': 'FAILED'
                    })
                    
                    self.log_status(f"❌ FAILED: No data extracted ({processing_time:.1f}s)")
                    
            except Exception as e:
                processing_time = (datetime.now() - file_start_time).total_seconds()
                results.append({
                    'File Name': filename,
                    'Project Name': 'ERROR',
                    'Street Address': '', 'City': '', 'ZIP Code': '', 
                    'County': '', 'Total Units': 0, 'Developer': '',
                    'Processing Time': f"{processing_time:.1f}s",
                    'Status': f'ERROR: {str(e)[:50]}'
                })
                
                self.log_status(f"💥 ERROR: {str(e)[:100]} ({processing_time:.1f}s)")
            
            # Update checkpoint after each file
            processed_files.append(filename)
            self.save_checkpoint(processed_files, total_files, results)
            
            # Progress update every 5 files
            if len(processed_files) % 5 == 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                avg_time = elapsed / len(processed_files)
                remaining = total_files - len(processed_files)
                eta_seconds = avg_time * remaining
                
                self.log_status(f"PROGRESS: {len(processed_files)}/{total_files} files")
                self.log_status(f"Average: {avg_time:.1f}s/file | ETA: {eta_seconds/60:.1f} minutes")
        
        # Final summary
        total_time = (datetime.now() - start_time).total_seconds()
        successful = len([r for r in results if r['Status'] == 'SUCCESS'])
        
        self.log_status("="*60)
        self.log_status(f"BATCH COMPLETE!")
        self.log_status(f"Total files: {total_files}")
        self.log_status(f"Successful: {successful}")
        self.log_status(f"Failed: {total_files - successful}")
        self.log_status(f"Total time: {total_time/60:.1f} minutes")
        self.log_status(f"Success rate: {successful/total_files*100:.1f}%")
        
        # Create final Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"TDHCA_Batch_Results_{timestamp}.xlsx"
        
        df = pd.DataFrame(results)
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='All Results', index=False)
            
            # Summary sheet
            summary_data = {
                'Metric': ['Total Files', 'Successful', 'Failed', 'Success Rate', 'Total Time (min)'],
                'Value': [total_files, successful, total_files-successful, 
                         f"{successful/total_files*100:.1f}%", f"{total_time/60:.1f}"]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        self.log_status(f"Excel saved: {excel_filename}")
        
        # Cleanup checkpoint files
        for file in [self.checkpoint_file, self.results_csv]:
            if Path(file).exists():
                Path(file).unlink()
        
        return excel_filename

def main():
    """Run batch processing with monitoring"""
    print("🚀 TDHCA Batch Processor with Checkpoint System")
    print("="*60)
    print("This process will:")
    print("1. Save progress after each file")
    print("2. Create status.log file you can monitor")  
    print("3. Resume from interruptions automatically")
    print("4. Work in small batches to avoid timeouts")
    print("="*60)
    
    base_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites"
    
    processor = CheckpointBatchProcessor(base_path)
    
    # Check if resuming
    if Path("batch_checkpoint.json").exists():
        print("\n⚠️  Found previous checkpoint!")
        response = input("Resume from checkpoint? (y/n): ")
        resume = response.lower() == 'y'
    else:
        resume = False
    
    try:
        excel_file = processor.process_batch(resume=resume)
        print(f"\n✅ COMPLETE! Results in: {excel_file}")
        print(f"📋 Check batch_status.log for detailed history")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  INTERRUPTED - Progress saved!")
        print("Run again to resume from checkpoint")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        print("Progress saved - run again to resume")
        sys.exit(1)

if __name__ == "__main__":
    main()