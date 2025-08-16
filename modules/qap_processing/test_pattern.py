#!/usr/bin/env python3

from docling.document_converter import DocumentConverter
import re

pdf_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/FL/current/FL_2025_QAP_Final.pdf"

converter = DocumentConverter()
result = converter.convert(pdf_path)
doc_text = result.document.export_to_markdown()

# Test the exact pattern
pattern = r'(##\s*IV\.\s*Compliance.*?)(?=\\Z)'
matches = re.findall(pattern, doc_text, re.DOTALL | re.IGNORECASE)

print(f"Pattern: {pattern}")
print(f"Matches: {len(matches)}")

if matches:
    print(f"Match content: {matches[0][:500]}...")
else:
    # Find where IV is
    iv_start = doc_text.find("## IV. Compliance")
    if iv_start != -1:
        print(f"Found '## IV. Compliance' at position {iv_start}")
        print(f"Content from there: {doc_text[iv_start:iv_start+200]}")
        
        # Test different end patterns
        test_patterns = [
            r'(##\s*IV\.\s*Compliance.*)',  # Just everything after IV
            r'(##\s*IV\..*?)$',             # To end of string
            r'(##\s*IV\..*)',               # Everything after IV
        ]
        
        for i, test_pattern in enumerate(test_patterns):
            test_matches = re.findall(test_pattern, doc_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            print(f"Test pattern {i+1}: {len(test_matches)} matches")
            if test_matches:
                print(f"  First 100 chars: {test_matches[0][:100]}...")