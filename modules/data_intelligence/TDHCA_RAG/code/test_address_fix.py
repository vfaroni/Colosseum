#!/usr/bin/env python3
"""Quick test of address extraction fix"""

import sys
from pathlib import Path
from improved_tdhca_extractor import ImprovedTDHCAExtractor

# Test on just the two known files quickly
base_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites"
extractor = ImprovedTDHCAExtractor(base_path)

test_files = ["25427.pdf", "25412.pdf"]

print("🔧 Quick Address Extraction Test")
print("=" * 50)

for filename in test_files:
    pdf_files = list(Path(base_path).glob(f"**/{filename}"))
    if pdf_files:
        print(f"\n📁 Testing {filename}")
        try:
            # Get just the text for quick testing
            text, _ = extractor.smart_extract_pdf_text(pdf_files[0])
            
            # Test improved address extraction
            street, city, zip_code = extractor._extract_address_improved(text)
            
            print(f"  📍 Street: '{street}'")
            print(f"  🏙️ City: '{city}'") 
            print(f"  📮 ZIP: '{zip_code}'")
            
            # Also test project name to confirm that still works
            project_name = extractor._extract_project_name_improved(text)
            print(f"  🏢 Project: '{project_name}'")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    else:
        print(f"❌ File not found: {filename}")

print("\n✅ Address test complete")