#!/usr/bin/env python3
"""
Test specific file extraction
"""

from final_extractor import LIHTC4PctExtractor
from pathlib import Path
import json

def test_specific_file():
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    
    extractor = LIHTC4PctExtractor(source_dir)
    
    # Test the Marina Towers file specifically
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    if test_file.exists():
        print(f"Testing specific file: {test_file.name}")
        result = extractor.process_file(test_file)
        
        print("\n=== Extraction Results ===")
        print(json.dumps(result, indent=2))
        
        # Check if county matches
        county = result['application_data'].get('county', '')
        print(f"\nCounty detected: '{county}'")
        
        if "solano" in county.lower():
            print("✓ County matches Solano filter")
        else:
            print("✗ County does not match Solano filter")
    else:
        print(f"File not found: {test_file}")

if __name__ == "__main__":
    test_specific_file()