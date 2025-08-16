#!/usr/bin/env python3
"""
Cleanup Obsolete Files - Remove experimental and debug code
Keeps only production-ready files for the final codebase

Author: Claude Code
Date: 2025-06-21
"""

import os
from pathlib import Path

def cleanup_obsolete_files():
    """Remove obsolete experimental and debug files"""
    
    # Current working directory
    code_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code")
    
    # PRODUCTION FILES TO KEEP
    production_files = {
        'final_195_sites_complete.py',
        'competition_fix_analyzer.py', 
        'preserve_costar_analyzer.py',
        'cleanup_obsolete_files.py',  # This script
        
        # Keep some reference files
        'costar_land_specific_analyzer.py',
        'texas_economic_viability_analyzer_final.py',
        'add_county_to_land_data.py',
        
        # Dashboard files
        'texas_deal_sourcing_dashboard.py',
        'texas_land_dashboard.py',
        'texas_land_simple_viewer.py',
        
        # California systems
        'ca_qct_dda_checker.py',
        'ca_transit_checker.py',
        
        # CTCAC QAP system
        'ctcac_qap_ocr_rag_extractor.py',
        
        # Project management
        'dmarco_dashboard.py'
    }
    
    # FILES TO DELETE (patterns)
    delete_patterns = [
        'debug*.py',
        'test*.py', 
        '4p_9p_*.py',
        'enhanced_texas_analyzer*.py',
        'enhanced_*analyzer*.py',
        'fixed_*.py',
        '*_corrected*.py',
        '*_fixed*.py',
        'quick_*.py',
        'rescue_*.py',
        'run_*.py',
        'complete_*.py',
        'working_*.py',
        'corrected_*.py',
        'final_corrected*.py',
        'integrated_*.py',
        '*copy*.py'
    ]
    
    # Scan for files to delete
    files_to_delete = []
    all_files = list(code_dir.glob('*.py'))
    
    print(f"Found {len(all_files)} Python files")
    print(f"Production files to keep: {len(production_files)}")
    
    for file_path in all_files:
        filename = file_path.name
        
        # Skip if it's a production file
        if filename in production_files:
            continue
            
        # Check if it matches deletion patterns
        should_delete = False
        for pattern in delete_patterns:
            if file_path.match(pattern):
                should_delete = True
                break
        
        if should_delete:
            files_to_delete.append(file_path)
    
    print(f"\nFiles marked for deletion: {len(files_to_delete)}")
    print("="*50)
    
    # Show files to delete
    for file_path in sorted(files_to_delete):
        print(f"DELETE: {file_path.name}")
    
    # Show files to keep
    print(f"\n\nProduction files to keep:")
    print("="*30)
    for filename in sorted(production_files):
        if (code_dir / filename).exists():
            print(f"KEEP: {filename}")
    
    print(f"\n\nSUMMARY:")
    print(f"Total files: {len(all_files)}")
    print(f"Files to delete: {len(files_to_delete)}")
    print(f"Files to keep: {len(all_files) - len(files_to_delete)}")
    print(f"Space savings: ~{len(files_to_delete) * 100}KB estimated")
    
    # Ask for confirmation
    response = input(f"\nDelete {len(files_to_delete)} obsolete files? (y/N): ")
    
    if response.lower() == 'y':
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                file_path.unlink()
                deleted_count += 1
                print(f"Deleted: {file_path.name}")
            except Exception as e:
                print(f"Error deleting {file_path.name}: {e}")
        
        print(f"\nCleanup complete! Deleted {deleted_count} files.")
    else:
        print("Cleanup cancelled.")

if __name__ == "__main__":
    cleanup_obsolete_files()