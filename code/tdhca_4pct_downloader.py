#!/usr/bin/env python3
"""
TDHCA 4% Bond Application Downloader
Mission: TDHCA_4PCT_ACQUISITION_20250811
Agent: BILL's WINGMAN

Intelligent acquisition system for TDHCA 4% bond applications 2023-2025
"""

import requests
import os
import time
import json
from pathlib import Path
from datetime import datetime

class TDHCA4PctDownloader:
    def __init__(self):
        self.base_urls = {
            '2023': 'https://www.tdhca.state.tx.us/multifamily/docs/imaged/2023-4-TEBApps/',
            '2024': 'https://www.tdhca.state.tx.us/multifamily/docs/imaged/2024-4-TEBApps/',
            '2025': 'https://www.tdhca.state.tx.us/multifamily/docs/imaged/2025-4-TEBApps/'
        }
        self.base_dir = Path('/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum')
        self.output_dir = self.base_dir / 'data_sets/texas/TDHCA_Applications'
        self.consecutive_misses = 0
        self.max_consecutive_misses = 2
        
        # Progress tracking
        self.progress = {
            "2023_4pct": {"target": 150, "downloaded": 0, "errors": [], "found": []},
            "2024_4pct": {"target": 200, "downloaded": 4, "errors": [], "found": [24400, 24403, 24600, 24601]},
            "2025_4pct": {"target": 150, "downloaded": 0, "errors": [], "found": []},
            "session_start": datetime.now().isoformat(),
            "total_bytes": 0
        }
        
    def smart_range_detection(self, year, start_id, end_id, existing_files=None):
        """
        Intelligent detection of available applications with gap handling
        """
        if existing_files is None:
            existing_files = []
            
        current_id = start_id
        hundred_block_misses = 0
        found_files = []
        
        print(f"\n🎯 Starting smart detection for {year} 4% applications ({start_id}-{end_id})")
        print(f"   Skipping existing files: {existing_files}")
        
        while current_id <= end_id and hundred_block_misses < 3:
            # Skip if we already have this file
            if current_id in existing_files:
                print(f"✅ Already have: {year}_4pct_{current_id}.pdf")
                found_files.append(current_id)
                current_id += 1
                continue
                
            # Try current ID
            if self.try_download(year, current_id):
                found_files.append(current_id)
                self.consecutive_misses = 0
                current_id += 1
            else:
                # Try +1 position
                if current_id + 1 <= end_id and self.try_download(year, current_id + 1):
                    found_files.append(current_id + 1)
                    self.consecutive_misses = 0
                    current_id += 2
                # Try +2 position  
                elif current_id + 2 <= end_id and self.try_download(year, current_id + 2):
                    found_files.append(current_id + 2)
                    self.consecutive_misses = 0
                    current_id += 3
                else:
                    # No hits in next 2 positions, jump to next 100
                    next_hundred = ((current_id // 100) + 1) * 100
                    
                    print(f"🔍 No files found around {current_id}, checking {next_hundred} block...")
                    
                    # Test next hundred block
                    block_has_files = False
                    for test_offset in range(3):  # Test xx00, xx01, xx02
                        test_id = next_hundred + test_offset
                        if test_id <= end_id and self.check_exists(year, test_id):
                            block_has_files = True
                            print(f"✅ Found files in {next_hundred} block")
                            break
                    
                    if block_has_files:
                        current_id = next_hundred
                        hundred_block_misses = 0
                    else:
                        hundred_block_misses += 1
                        current_id = next_hundred
                        print(f"❌ No files in {next_hundred} block ({hundred_block_misses}/3 empty blocks)")
                        
        print(f"🎯 Smart detection complete: Found {len(found_files)} applications")
        return found_files
    
    def try_download(self, year, app_id):
        """
        Attempt to download a specific application
        Returns True if successful, False if not found
        """
        url = f"{self.base_urls[year]}{app_id}.pdf"
        output_path = self.output_dir / year / '4pct' / f"{year}_4pct_{app_id}.pdf"
        
        # Skip if already exists
        if output_path.exists():
            print(f"✅ Already have: {year}_4pct_{app_id}.pdf")
            return True
            
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                # File exists, download it
                print(f"📥 Downloading: {year}_4pct_{app_id}.pdf")
                response = requests.get(url, timeout=30)
                
                # Create directory if needed
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save file
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                file_size_mb = len(response.content) / 1024 / 1024
                print(f"✅ Saved: {output_path.name} ({file_size_mb:.1f}MB)")
                
                # Update progress
                self.progress[f"{year}_4pct"]["downloaded"] += 1
                self.progress[f"{year}_4pct"]["found"].append(app_id)
                self.progress["total_bytes"] += len(response.content)
                
                time.sleep(1)  # Be polite to server
                return True
            else:
                return False
        except Exception as e:
            print(f"❌ Error downloading {app_id}: {e}")
            self.progress[f"{year}_4pct"]["errors"].append(f"{app_id}: {str(e)}")
            return False
    
    def check_exists(self, year, app_id):
        """Quick check if file exists without downloading"""
        url = f"{self.base_urls[year]}{app_id}.pdf"
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def save_progress(self):
        """Save progress to JSON file"""
        progress_file = self.base_dir / 'TDHCA_4pct_acquisition_progress.json'
        self.progress["last_updated"] = datetime.now().isoformat()
        
        with open(progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
        
        print(f"💾 Progress saved to {progress_file}")
        
    def generate_report(self):
        """Generate mission completion report"""
        total_downloaded = sum(self.progress[year]["downloaded"] for year in ["2023_4pct", "2024_4pct", "2025_4pct"])
        total_errors = sum(len(self.progress[year]["errors"]) for year in ["2023_4pct", "2024_4pct", "2025_4pct"])
        total_gb = self.progress["total_bytes"] / 1024 / 1024 / 1024
        
        report = f"""
🎯 TDHCA 4% ACQUISITION MISSION REPORT
=====================================

Mission ID: TDHCA_4PCT_ACQUISITION_20250811
Agent: BILL's WINGMAN
Completion Time: {datetime.now().isoformat()}

📊 ACQUISITION STATISTICS
------------------------
2023 4% Applications: {self.progress['2023_4pct']['downloaded']}/{self.progress['2023_4pct']['target']} ({len(self.progress['2023_4pct']['found'])} found)
2024 4% Applications: {self.progress['2024_4pct']['downloaded']}/{self.progress['2024_4pct']['target']} ({len(self.progress['2024_4pct']['found'])} found)
2025 4% Applications: {self.progress['2025_4pct']['downloaded']}/{self.progress['2025_4pct']['target']} ({len(self.progress['2025_4pct']['found'])} found)

Total Downloaded: {total_downloaded} applications
Total Storage: {total_gb:.2f} GB
Total Errors: {total_errors}

🎯 MISSION STATUS: {"✅ SUCCESS" if total_downloaded > 300 else "⚠️ PARTIAL"}

Victory Condition: {"ACHIEVED" if total_downloaded > 300 else "IN PROGRESS"}
"""
        
        report_file = self.base_dir / 'TDHCA_4pct_mission_report.txt'
        with open(report_file, 'w') as f:
            f.write(report)
            
        print(report)
        return report

def main():
    """Execute TDHCA 4% acquisition mission"""
    downloader = TDHCA4PctDownloader()
    
    print("🏛️ COLOSSEUM LIHTC PLATFORM - TDHCA 4% ACQUISITION")
    print("=" * 50)
    print("Mission: TDHCA_4PCT_ACQUISITION_20250811")
    print("Agent: BILL's WINGMAN")
    print("Objective: Acquire complete 4% bond application collection")
    print("=" * 50)
    
    try:
        # Phase 1: 2024 Applications (highest priority)
        print("\n🎯 PHASE 1: 2024 4% APPLICATIONS")
        existing_2024 = [24400, 24403, 24600, 24601]
        found_2024 = downloader.smart_range_detection('2024', 24400, 24703, existing_2024)
        downloader.save_progress()
        
        # Phase 2: 2025 Applications 
        print("\n🎯 PHASE 2: 2025 4% APPLICATIONS")
        found_2025 = downloader.smart_range_detection('2025', 25401, 25606)
        downloader.save_progress()
        
        # Phase 3: 2023 Applications
        print("\n🎯 PHASE 3: 2023 4% APPLICATIONS")  
        found_2023 = downloader.smart_range_detection('2023', 23400, 23618)
        downloader.save_progress()
        
        # Generate final report
        print("\n🎯 GENERATING MISSION REPORT")
        downloader.generate_report()
        
        print("\n🎯 MISSION COMPLETE - TDHCA 4% INTELLIGENCE ACQUIRED")
        
    except KeyboardInterrupt:
        print("\n⚠️ Mission interrupted - saving progress...")
        downloader.save_progress()
    except Exception as e:
        print(f"\n❌ Mission error: {e}")
        downloader.save_progress()

if __name__ == "__main__":
    main()