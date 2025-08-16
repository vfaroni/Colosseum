#!/usr/bin/env python3
"""
Debug TDHCA Extraction - Diagnose extraction issues
"""

import re
from pathlib import Path
from ultimate_tdhca_extractor import UltimateTDHCAExtractor

def debug_single_pdf(pdf_path, output_file):
    """Debug extraction on a single PDF"""
    
    def log(message):
        print(message)
        output_file.write(message + '\n')
    
    log(f"🔍 DEBUGGING: {pdf_path.name}")
    log("=" * 60)
    
    extractor = UltimateTDHCAExtractor("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites")
    
    # Extract raw text
    try:
        text, stats = extractor.smart_extract_pdf_text(pdf_path)
        log(f"✅ Text extraction: {len(text)} characters")
        log(f"📊 Pages processed: {stats['processed_pages']}/{stats['total_pages']}")
        
        # Show first 1000 characters
        log(f"\n📄 FIRST 1000 CHARACTERS:")
        log("-" * 40)
        log(text[:1000])
        log("-" * 40)
        
        # Look for key patterns
        log(f"\n🔍 KEY PATTERN ANALYSIS:")
        
        # Project name patterns
        project_patterns = [
            r'Project\s+Name[:\s]+([^\n]+)',
            r'Development\s+Name[:\s]+([^\n]+)',
            r'Property\s+Name[:\s]+([^\n]+)'
        ]
        
        log(f"\n📝 PROJECT NAME SEARCH:")
        for pattern in project_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                log(f"  Pattern '{pattern}': {matches[:3]}")
        
        # Address patterns  
        log(f"\n🏠 ADDRESS SEARCH:")
        address_patterns = [
            r'Site\s+Address[:\s]+([^\n]+)',
            r'Property\s+Address[:\s]+([^\n]+)', 
            r'(\d+\s+[A-Za-z][^,\n]{10,60}),?\s*([A-Z][a-z]+),?\s*TX\s*(\d{5})'
        ]
        
        for pattern in address_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                log(f"  Pattern '{pattern}': {matches[:3]}")
        
        # Unit information
        log(f"\n🏢 UNIT COUNT SEARCH:")
        unit_patterns = [
            r'Total\s+Units[:\s]+(\d+)',
            r'Number\s+of\s+Units[:\s]+(\d+)',
            r'(\d+)\s+units?',
            r'Unit\s+Mix[:\s]*([^\n]+)'
        ]
        
        for pattern in unit_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE) 
            if matches:
                log(f"  Pattern '{pattern}': {matches[:3]}")
        
        # Developer info
        log(f"\n🏗️ DEVELOPER SEARCH:")
        dev_patterns = [
            r'Developer[:\s]+([^\n]+)',
            r'General\s+Partner[:\s]+([^\n]+)',
            r'Applicant[:\s]+([^\n]+)'
        ]
        
        for pattern in dev_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                log(f"  Pattern '{pattern}': {matches[:3]}")
                
    except Exception as e:
        log(f"❌ ERROR: {e}")
    
    log(f"\n" + "=" * 60)

if __name__ == "__main__":
    # Debug the first few PDFs that had issues
    base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites")
    pdfs = list(base_path.glob("**/*.pdf"))[:3]
    
    # Create output file with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = f"debug_extraction_report_{timestamp}.txt"
    
    with open(output_file_path, 'w') as output_file:
        output_file.write(f"TDHCA PDF Debug Report - {datetime.now()}\n")
        output_file.write("=" * 80 + "\n\n")
        
        for pdf in pdfs:
            debug_single_pdf(pdf, output_file)
            output_file.write(f"\n\n")
    
    print(f"✅ Debug report saved to: {output_file_path}")