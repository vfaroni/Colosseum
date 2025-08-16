#!/usr/bin/env python3
"""
Phase 2C Pattern Test - Debug specific patterns on TX QAP text
"""

import json
import sys
from pathlib import Path
import re

# Direct Docling import
from docling.document_converter import DocumentConverter

def test_specific_patterns():
    """Test specific patterns that should work"""
    
    print("🔍 Phase 2C Pattern Debugging")
    print("=" * 50)
    
    # Initialize Docling converter
    converter = DocumentConverter()
    
    # Test with Texas QAP
    qap_file = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/TX/current/TX_2025_QAP.pdf")
    
    print(f"📄 Processing: {qap_file.name}")
    
    # Extract text with Docling
    result = converter.convert(str(qap_file))
    document = result.document
    text_content = document.export_to_markdown()
    
    print(f"📝 Text length: {len(text_content):,} characters")
    
    # Test the original simple pattern that worked in Phase 2B
    print(f"\n🎯 Testing Original Simple Pattern (Phase 2B Success)...")
    simple_pattern = r'"([^"]+)"\s+means\s+([^.]+(?:\.[^.]*){0,2}\.)'
    simple_matches = re.findall(simple_pattern, text_content, re.IGNORECASE)
    print(f"Simple pattern matches: {len(simple_matches)}")
    
    for i, match in enumerate(simple_matches[:5]):
        print(f"  {i+1}. '{match[0]}' = {match[1][:100]}...")
    
    # Search for actual LIHTC terms in the text
    print(f"\n🎯 LIHTC Term Search...")
    lihtc_terms = [
        "Low Income Housing Tax Credit", "LIHTC", "qualified basis", 
        "area median income", "AMI", "income limits", "compliance period",
        "affordable housing", "tax credit", "Section 42"
    ]
    
    found_terms = []
    for term in lihtc_terms:
        if term.lower() in text_content.lower():
            found_terms.append(term)
            # Find context around the term
            term_index = text_content.lower().find(term.lower())
            context = text_content[max(0, term_index-50):term_index+150]
            print(f"  ✅ '{term}' found: ...{context}...")
            
    print(f"\nFound {len(found_terms)} LIHTC terms in text")
    
    # Test broader definition patterns
    print(f"\n🎯 Testing Broader Definition Patterns...")
    
    # Pattern: Term followed by definition with colon
    colon_pattern = r'([A-Z][A-Za-z\s]{5,40}):\s*([A-Z][^.]{20,200}\.)'
    colon_matches = re.findall(colon_pattern, text_content)
    print(f"Colon definition matches: {len(colon_matches)}")
    
    for i, match in enumerate(colon_matches[:3]):
        print(f"  {i+1}. '{match[0]}': {match[1][:80]}...")
    
    # Pattern: Look for any quoted terms followed by explanatory text
    quoted_term_pattern = r'"([^"]{3,30})"\s+([A-Za-z][^.]{10,150}\.)'
    quoted_matches = re.findall(quoted_term_pattern, text_content)
    print(f"Quoted term matches: {len(quoted_matches)}")
    
    for i, match in enumerate(quoted_matches[:3]):
        print(f"  {i+1}. '{match[0]}' -> {match[1][:60]}...")
    
    # Total possible definitions
    total_possible = len(simple_matches) + len(colon_matches) + len(quoted_matches)
    print(f"\n🏆 TOTAL POSSIBLE DEFINITIONS: {total_possible}")

if __name__ == "__main__":
    test_specific_patterns()