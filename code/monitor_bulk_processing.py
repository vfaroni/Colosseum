#!/usr/bin/env python3
"""
CTCAC Bulk Processing Monitor
Track progress of V1.7 bulk processing across all 804 applications
"""

import time
import subprocess
from pathlib import Path
from datetime import datetime

def monitor_processing():
    """Monitor the bulk processing progress"""
    processed_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/processed_ctcac_data")
    log_file = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/bulk_processing_v17.log")
    
    print("🔍 CTCAC V1.7 BULK PROCESSING MONITOR")
    print("=" * 50)
    print(f"Target: 798 files across 2023-2025")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    while True:
        try:
            # Count processed files
            processed_count = 0
            year_counts = {}
            
            for year in [2023, 2024, 2025]:
                year_dir = processed_dir / str(year)
                if year_dir.exists():
                    year_files = list(year_dir.rglob("*.json"))
                    year_counts[year] = len(year_files)
                    processed_count += len(year_files)
                else:
                    year_counts[year] = 0
            
            # Calculate progress
            progress_pct = (processed_count / 798) * 100
            
            # Get latest log lines
            if log_file.exists():
                try:
                    result = subprocess.run(['tail', '-3', str(log_file)], 
                                          capture_output=True, text=True, timeout=5)
                    latest_lines = result.stdout.strip().split('\n')[-1] if result.stdout.strip() else "Processing..."
                except:
                    latest_lines = "Log monitoring error"
            else:
                latest_lines = "Log file not found"
            
            # Display status
            print(f"\r🚀 Progress: {processed_count}/798 ({progress_pct:.1f}%) | "
                  f"2023: {year_counts[2023]} | 2024: {year_counts[2024]} | 2025: {year_counts[2025]} | "
                  f"{datetime.now().strftime('%H:%M:%S')}", end="")
            
            # Check if complete
            if processed_count >= 798:
                print(f"\n🎯 BULK PROCESSING COMPLETE!")
                print(f"Total processed: {processed_count} files")
                print(f"Final breakdown: 2023:{year_counts[2023]}, 2024:{year_counts[2024]}, 2025:{year_counts[2025]}")
                break
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print(f"\n⏸️  Monitoring stopped by user")
            print(f"Current progress: {processed_count}/798 ({progress_pct:.1f}%)")
            break
        except Exception as e:
            print(f"\n❌ Monitor error: {e}")
            time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    monitor_processing()