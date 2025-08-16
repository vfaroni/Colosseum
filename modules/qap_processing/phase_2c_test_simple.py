#!/usr/bin/env python3
"""
Phase 2C Simple Test - Test the core enhanced extraction patterns
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import time
import re

# Direct Docling import
from docling.document_converter import DocumentConverter

def test_enhanced_patterns():
    """Test enhanced QAP patterns on a single state"""
    
    print("🏛️ Phase 2C Enhanced Patterns - Simple Test")
    print("=" * 50)
    
    # Initialize Docling converter
    converter = DocumentConverter()
    
    # Test with Texas QAP (known to have 594K characters)
    qap_file = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/TX/current/TX_2025_QAP.pdf")
    
    if not qap_file.exists():
        print(f"❌ QAP file not found: {qap_file}")
        return
    
    print(f"📄 Testing with: {qap_file.name}")
    
    # Extract text with Docling
    print(f"🔍 Extracting text with Docling...")
    result = converter.convert(str(qap_file))
    document = result.document
    text_content = document.export_to_markdown()
    
    print(f"📝 Extracted {len(text_content):,} characters")
    
    # Test Pattern 1: Parenthetical Abbreviation Definitions
    print(f"\n🎯 Testing Pattern 1: Parenthetical Abbreviations...")
    parenthetical_pattern = r'([A-Z][A-Za-z\s]{10,60})\s*\(\s*[\'\""]([A-Z]{2,10})[\'\""](?:\s+or\s+[\'\""]([^\'\"]+)[\'\""])?\s*\)'
    parenthetical_matches = re.findall(parenthetical_pattern, text_content, re.IGNORECASE)
    print(f"Found {len(parenthetical_matches)} parenthetical matches")
    
    # Show examples
    for i, match in enumerate(parenthetical_matches[:3]):
        print(f"  {i+1}. {match[1]} = {match[0]}")
    
    # Test Pattern 2: Federal Code References
    print(f"\n🎯 Testing Pattern 2: Federal Code References...")
    federal_pattern = r'(?:As set forth in|pursuant to|under)\s+(?:IRC\s+)?Section\s+42[^,]*,\s*([^:]+):\s*([^.]{20,200}\.)'
    federal_matches = re.findall(federal_pattern, text_content, re.IGNORECASE | re.DOTALL)
    print(f"Found {len(federal_matches)} federal code matches")
    
    # Test Pattern 3: Shall Mean
    print(f"\n🎯 Testing Pattern 3: Shall Mean...")
    shall_mean_pattern = r'([A-Za-z\s]{3,40})\s+shall\s+mean\s+([^.]{15,300}\.)'
    shall_mean_matches = re.findall(shall_mean_pattern, text_content, re.IGNORECASE)
    print(f"Found {len(shall_mean_matches)} shall mean matches")
    
    # Show examples
    for i, match in enumerate(shall_mean_matches[:3]):
        print(f"  {i+1}. {match[0]} = {match[1][:50]}...")
    
    # Total definitions found
    total_definitions = len(parenthetical_matches) + len(federal_matches) + len(shall_mean_matches)
    print(f"\n🏆 TOTAL DEFINITIONS FOUND: {total_definitions}")
    print(f"📈 Improvement over Phase 2B: {total_definitions}x (Phase 2B found 1 from TX)")

if __name__ == "__main__":
    test_enhanced_patterns()