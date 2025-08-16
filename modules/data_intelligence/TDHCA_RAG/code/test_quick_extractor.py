#!/usr/bin/env python3
"""
Quick test of key extraction functionality
Uses limited pages for faster processing
"""

from pathlib import Path
import logging
import PyPDF2
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def quick_extract_test():
    """Quick extraction test on limited pages"""
    
    # Test file path
    test_file = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/Successful_2023_Applications/Dallas_Fort_Worth/TDHCA_23461_Estates_at_Ferguson.pdf")
    
    if not test_file.exists():
        logger.error(f"Test file not found: {test_file}")
        return
    
    logger.info(f"Quick test on: {test_file.name}")
    
    # Extract text from first 20 pages only
    text = ""
    try:
        with open(test_file, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            logger.info(f"PDF has {len(pdf_reader.pages)} pages")
            
            # Process only first 20 pages
            for page_num in range(min(20, len(pdf_reader.pages))):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                text += f"\n--- Page {page_num+1} ---\n{page_text}"
                
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        return
    
    # Quick extraction tests
    logger.info("Testing extraction patterns...")
    
    # Clean text
    clean_text = text.replace('\n', ' ').replace('\r', ' ')
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    # Test 1: Project name
    name_match = re.search(r'(?:Project|Development)\s*Name[:\s]+([^.]+?)(?:\s|$)', clean_text, re.IGNORECASE)
    if name_match:
        logger.info(f"✓ Project Name: {name_match.group(1).strip()}")
    else:
        logger.warning("✗ Project name not found")
    
    # Test 2: Address extraction
    address_patterns = [
        r'(?:Property|Site)\s*Address[:\s]+([^,]+),\s*([^,]+),\s*TX\s*(\d{5})',
        r'(\d+\s+[A-Z][^,]{5,50}),\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*TX\s*(\d{5})'
    ]
    
    address_found = False
    for pattern in address_patterns:
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            logger.info(f"✓ Address: {match.group(1).strip()}, {match.group(2).strip()}, TX {match.group(3)}")
            address_found = True
            break
    
    if not address_found:
        logger.warning("✗ Address not found with patterns")
    
    # Test 3: Total units
    unit_match = re.search(r'Total Units[:\s]+(\d+)', clean_text, re.IGNORECASE)
    if unit_match:
        logger.info(f"✓ Total Units: {unit_match.group(1)}")
    else:
        logger.warning("✗ Total units not found")
    
    # Test 4: QCT/DDA status
    qct_found = re.search(r'(?:QCT|Qualified Census Tract)', clean_text, re.IGNORECASE)
    dda_found = re.search(r'(?:DDA|Difficult Development Area)', clean_text, re.IGNORECASE)
    
    if qct_found and dda_found:
        logger.info("✓ QCT/DDA Status: Both")
    elif qct_found:
        logger.info("✓ QCT/DDA Status: QCT")
    elif dda_found:
        logger.info("✓ QCT/DDA Status: DDA")
    else:
        logger.info("✓ QCT/DDA Status: Neither")
    
    # Test 5: Scoring information
    score_match = re.search(r'(?:Total\s*)?(?:TDHCA\s*)?Score[:\s]+(\d+)', clean_text, re.IGNORECASE)
    if score_match:
        logger.info(f"✓ TDHCA Score: {score_match.group(1)}")
    else:
        logger.warning("✗ TDHCA score not found")
    
    # Display sample text to understand structure
    logger.info("\n=== SAMPLE TEXT FROM FIRST PAGE ===")
    first_page_text = text.split('--- Page 2 ---')[0] if '--- Page 2 ---' in text else text[:1000]
    print(first_page_text[:500] + "...")

if __name__ == "__main__":
    quick_extract_test()