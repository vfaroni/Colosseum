#!/usr/bin/env python3
"""
Investigate FL QAP structure to understand the actual format
"""

from docling.document_converter import DocumentConverter

def investigate_fl_structure():
    """Investigate the actual FL QAP structure"""
    
    pdf_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/FL/current/FL_2025_QAP_Final.pdf"
    
    print("🔍 INVESTIGATING FL QAP STRUCTURE")
    print("=" * 50)
    
    # Process with docling
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    doc_text = result.document.export_to_markdown()
    
    print(f"📄 Document stats:")
    print(f"  Total characters: {len(doc_text):,}")
    print(f"  Total lines: {len(doc_text.split(chr(10))):,}")
    
    # Show first 2000 characters to understand structure
    print(f"\n📋 FIRST 2000 CHARACTERS:")
    print("-" * 40)
    print(doc_text[:2000])
    
    # Show last 1000 characters
    print(f"\n📋 LAST 1000 CHARACTERS:")
    print("-" * 40)
    print(doc_text[-1000:])
    
    # Look for common patterns
    print(f"\n🔍 PATTERN ANALYSIS:")
    
    import re
    
    # Look for chapters
    chapters = re.findall(r'Chapter\s+\d+[^\n]*', doc_text, re.IGNORECASE)
    print(f"  Chapters found: {len(chapters)}")
    for i, chapter in enumerate(chapters[:5]):
        print(f"    {i+1}. {chapter}")
    
    # Look for sections
    sections = re.findall(r'Section\s+[^\n]*', doc_text, re.IGNORECASE)
    print(f"  Sections found: {len(sections)}")
    for i, section in enumerate(sections[:5]):
        print(f"    {i+1}. {section}")
    
    # Look for numbered patterns
    numbered = re.findall(r'^\d+\.\s+[^\n]*', doc_text, re.MULTILINE)
    print(f"  Numbered items found: {len(numbered)}")
    for i, item in enumerate(numbered[:5]):
        print(f"    {i+1}. {item}")
    
    # Look for headers with ##
    headers = re.findall(r'^##\s+[^\n]*', doc_text, re.MULTILINE)
    print(f"  Headers (##) found: {len(headers)}")
    for i, header in enumerate(headers[:10]):
        print(f"    {i+1}. {header}")

if __name__ == "__main__":
    investigate_fl_structure()