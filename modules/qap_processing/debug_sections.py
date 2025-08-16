#!/usr/bin/env python3
"""
Debug Section Detection
Check what sections are actually being found in the CA QAP extraction
"""

import sys
from pathlib import Path
from docling_4strategy_integration import DoclingStrategyIntegration

def debug_ca_sections():
    """Debug what sections are found in CA processing"""
    
    print("🔍 DEBUGGING CA QAP SECTION DETECTION")
    print("=" * 50)
    
    # Process CA
    integration = DoclingStrategyIntegration()
    result = integration.process_jurisdiction("CA")
    
    if result.extracted_content:
        print(f"\nFound {len(result.extracted_content)} sections:")
        print(f"Total content: {sum(len(v) for v in result.extracted_content.values()):,} characters")
        
        for section_key, content in result.extracted_content.items():
            print(f"\nSection: {section_key}")
            print(f"Length: {len(content):,} characters")
            print(f"Preview: {content[:200]}...")
            
            # Check for negative points content
            if any(keyword in content.lower() for keyword in 
                   ["negative", "deduction", "penalty", "prior performance", "returned credit"]):
                print("  *** CONTAINS NEGATIVE POINTS KEYWORDS ***")
    else:
        print("No extracted content found!")

if __name__ == "__main__":
    debug_ca_sections()