#!/usr/bin/env python3
"""
Get the actual definitions section content to examine legal references
"""

from docling_4strategy_integration import DoclingStrategyIntegration
import re

def get_definitions_content():
    """Get the definitions section content"""
    
    print("📋 EXTRACTING DEFINITIONS SECTION")
    print("=" * 50)
    
    # Get extracted sections
    integration = DoclingStrategyIntegration()
    result = integration.process_jurisdiction("CA")
    
    if "section_definitions" in result.extracted_content:
        definitions = result.extracted_content["section_definitions"]
        print(f"Definitions section: {len(definitions):,} characters")
        
        # Show the end of definitions as user suggested
        print(f"\n📖 END OF DEFINITIONS SECTION (last 3000 chars)")
        print("-" * 60)
        print(definitions[-3000:])
        
        # Extract all legal references
        print(f"\n⚖️ ALL LEGAL CITATIONS IN DEFINITIONS")
        print("-" * 60)
        
        # More comprehensive federal references
        federal_patterns = [
            r'IRC[^.]*Section[^.]*\d+[^.]*',
            r'Internal Revenue Code[^.]*Section[^.]*\d+[^.]*',
            r'26 USC[^.]*\d+[^.]*',
            r'Public Law[^.]*\d+-\d+[^.]*'
        ]
        
        all_federal = []
        for pattern in federal_patterns:
            matches = re.findall(pattern, definitions, re.IGNORECASE)
            all_federal.extend(matches)
        
        print(f"📜 Federal References ({len(all_federal)}):")
        for i, ref in enumerate(all_federal):
            print(f"  {i+1}. {ref.strip()}")
        
        # California state code references
        ca_patterns = [
            r'Health.*Safety Code[^.]*Section[^.]*[0-9.]+[^.]*',
            r'Revenue.*Taxation Code[^.]*Section[^.]*[0-9.]+[^.]*',
            r'California[^.]*Code[^.]*Section[^.]*[0-9.]+[^.]*'
        ]
        
        all_ca = []
        for pattern in ca_patterns:
            matches = re.findall(pattern, definitions, re.IGNORECASE)
            all_ca.extend(matches)
            
        print(f"\n🏛️ California State References ({len(all_ca)}):")
        for i, ref in enumerate(all_ca):
            print(f"  {i+1}. {ref.strip()}")
            
    else:
        print("❌ Definitions section not found")
        print("Available sections:", list(result.extracted_content.keys()))

if __name__ == "__main__":
    get_definitions_content()