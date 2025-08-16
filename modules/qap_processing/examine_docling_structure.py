#!/usr/bin/env python3
"""
Examine Docling Document Structure
Debug what docling is actually extracting from the CA QAP
"""

import sys
from pathlib import Path
from docling.document_converter import DocumentConverter
import re

def examine_ca_qap():
    """Examine the actual docling structure"""
    
    pdf_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/CA/current/CA_2025_QAP_Regulations_Dec_2024.pdf"
    
    print("🔍 EXAMINING DOCLING STRUCTURE FOR CA QAP")
    print("=" * 60)
    
    # Create converter
    converter = DocumentConverter()
    
    print(f"\nProcessing: {Path(pdf_path).name}")
    result = converter.convert(pdf_path)
    
    if not result or not result.document:
        print("❌ Docling conversion failed")
        return
    
    doc = result.document
    print(f"✅ Document processed successfully")
    
    # Export to markdown
    doc_text = doc.export_to_markdown()
    print(f"📄 Full document: {len(doc_text):,} characters")
    
    # Look for CA regulatory sections
    print(f"\n🔍 SEARCHING FOR CA REGULATORY SECTIONS")
    print("-" * 40)
    
    section_pattern = r'(§103\d+\..*?)(?=§103\d+\.|\Z)'
    sections = re.findall(section_pattern, doc_text, re.DOTALL)
    
    print(f"Found {len(sections)} sections using regex")
    
    for i, section in enumerate(sections[:5]):  # Show first 5
        lines = section.strip().split('\n')
        header = lines[0] if lines else "No header"
        content_lines = len(lines)
        char_count = len(section.strip())
        
        print(f"\nSection {i+1}: {header}")
        print(f"  Lines: {content_lines}, Characters: {char_count:,}")
        print(f"  Preview: {section.strip()[:200]}...")
        
        # Check for specific content
        if "scoring" in section.lower() or "criteria" in section.lower():
            print("  *** SCORING CONTENT DETECTED ***")
        if "geographic" in section.lower() or "apportionment" in section.lower():
            print("  *** GEOGRAPHIC CONTENT DETECTED ***")
        if "threshold" in section.lower() or "requirement" in section.lower():
            print("  *** THRESHOLD CONTENT DETECTED ***")
    
    # Look for specific sections by number
    print(f"\n🎯 LOOKING FOR SPECIFIC SECTIONS")
    print("-" * 40)
    
    specific_sections = [
        ("§10300", "Purpose and Scope"),
        ("§10315", "Set-Asides and Apportionments"),
        ("§10322", "Application Requirements"), 
        ("§10325", "Scoring Criteria"),
        ("§10327", "Financial Feasibility"),
        ("§10337", "Compliance")
    ]
    
    for section_num, description in specific_sections:
        pattern = rf'({re.escape(section_num)}\..*?)(?=§103\d+\.|\Z)'
        matches = re.findall(pattern, doc_text, re.DOTALL | re.IGNORECASE)
        
        if matches:
            content = matches[0].strip()
            lines = content.split('\n')
            print(f"\n✅ {section_num} - {description}")
            print(f"   Characters: {len(content):,}")
            print(f"   Lines: {len(lines)}")
            print(f"   First 300 chars: {content[:300]}...")
        else:
            print(f"\n❌ {section_num} - {description} - NOT FOUND")
    
    # Show document structure markers
    print(f"\n📋 DOCUMENT STRUCTURE ANALYSIS")
    print("-" * 40)
    
    # Look for page markers
    page_markers = re.findall(r'page\s+\d+', doc_text, re.IGNORECASE)
    print(f"Page markers found: {len(page_markers)}")
    if page_markers:
        print(f"Sample page markers: {page_markers[:5]}")
    
    # Look for section breaks
    section_breaks = re.findall(r'§103\d+\.', doc_text)
    print(f"Section breaks (§103X.): {len(section_breaks)}")
    
    # Show first 2000 characters to understand structure
    print(f"\n📖 DOCUMENT START (first 2000 chars)")
    print("-" * 40)
    print(doc_text[:2000])
    
    # Show around scoring section
    scoring_pos = doc_text.lower().find('§10325')
    if scoring_pos >= 0:
        print(f"\n🎯 AROUND SCORING SECTION (§10325)")
        print("-" * 40)
        start = max(0, scoring_pos - 200)
        end = min(len(doc_text), scoring_pos + 1500)
        print(doc_text[start:end])

if __name__ == "__main__":
    examine_ca_qap()