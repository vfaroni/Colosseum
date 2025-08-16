#!/usr/bin/env python3
"""
Investigate TX QAP structure to understand the actual format
"""

from docling.document_converter import DocumentConverter
import re

def investigate_tx_structure():
    """Investigate the actual TX QAP structure"""
    
    pdf_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/TX/current/TX_2025_QAP.pdf"
    
    print("🔍 INVESTIGATING TX QAP STRUCTURE")
    print("=" * 50)
    
    # Process with docling
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    doc_text = result.document.export_to_markdown()
    
    print(f"📄 Document stats:")
    print(f"  Total characters: {len(doc_text):,}")
    print(f"  Total lines: {len(doc_text.split(chr(10))):,}")
    
    # Show first 3000 characters to understand structure
    print(f"\n📋 FIRST 3000 CHARACTERS:")
    print("-" * 40)
    print(doc_text[:3000])
    
    # Look for common patterns
    print(f"\n🔍 PATTERN ANALYSIS:")
    
    # Look for section symbols
    section_symbols = re.findall(r'§\s*11\.\d+[^\n]*', doc_text, re.IGNORECASE)
    print(f"  § 11.x sections found: {len(section_symbols)}")
    for i, section in enumerate(section_symbols[:10]):
        print(f"    {i+1}. {section}")
    
    # Look for numbered subparts  
    subparts = re.findall(r'\(\w+\)[^\n]*', doc_text)
    print(f"  Subparts (x) found: {len(subparts)}")
    for i, subpart in enumerate(subparts[:10]):
        print(f"    {i+1}. {subpart}")
    
    # Look for headers with ##
    headers = re.findall(r'^##\s+[^\n]*', doc_text, re.MULTILINE)
    print(f"  Headers (##) found: {len(headers)}")
    for i, header in enumerate(headers[:15]):
        print(f"    {i+1}. {header}")

if __name__ == "__main__":
    investigate_tx_structure()