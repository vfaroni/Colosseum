#!/usr/bin/env python3
"""
Debug Part IV missing in FL extraction
"""

from docling.document_converter import DocumentConverter
import re

def debug_part_iv():
    """Debug why Part IV is missing"""
    
    pdf_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/FL/current/FL_2025_QAP_Final.pdf"
    
    # Process with docling
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    doc_text = result.document.export_to_markdown()
    
    print("🔍 DEBUGGING PART IV EXTRACTION")
    print("=" * 40)
    
    # Find all instances of "IV"
    iv_matches = re.finditer(r'##\s*IV\.[^#]*', doc_text, re.IGNORECASE | re.DOTALL)
    print("Part IV matches found:")
    for i, match in enumerate(iv_matches):
        print(f"  {i+1}. {match.group()[:100]}...")
        print(f"     Start: {match.start()}, End: {match.end()}")
    
    # Look at the text around where Part IV should be
    part_iii_match = re.search(r'##\s*III\.[^#]*', doc_text, re.IGNORECASE | re.DOTALL)
    if part_iii_match:
        end_of_iii = part_iii_match.end()
        text_after_iii = doc_text[end_of_iii:end_of_iii+1000]
        print(f"\nText after Part III (next 1000 chars):")
        print("-" * 40)
        print(text_after_iii)
    
    # Test the exact regex we're using
    pattern = r'(##\s*IV\.\s*Compliance.*?)(?=##\s*[IVX]+|\\Z)'
    matches = re.findall(pattern, doc_text, re.DOTALL | re.IGNORECASE)
    print(f"\nRegex test results:")
    print(f"  Pattern: {pattern}")
    print(f"  Matches found: {len(matches)}")
    if matches:
        for i, match in enumerate(matches):
            print(f"    {i+1}. {len(match)} chars: {match[:200]}...")

if __name__ == "__main__":
    debug_part_iv()