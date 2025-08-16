#!/usr/bin/env python3
"""
Examine Legal References in CA QAP
Look specifically at definitions section and legal citations
"""

from docling_4strategy_integration import DoclingStrategyIntegration
import re

def examine_legal_references():
    """Examine legal references throughout CA QAP sections"""
    
    print("⚖️ EXAMINING LEGAL REFERENCES IN CA QAP")
    print("=" * 60)
    
    # Get extracted sections
    integration = DoclingStrategyIntegration()
    result = integration.process_jurisdiction("CA")
    
    # Focus on definitions section first
    if "section_definitions" in result.extracted_content:
        definitions = result.extracted_content["section_definitions"]
        print(f"\n📋 DEFINITIONS SECTION ANALYSIS")
        print(f"Section length: {len(definitions):,} characters")
        
        # Look at the end of definitions as user suggested
        print(f"\n📖 END OF DEFINITIONS SECTION (last 2000 chars)")
        print("-" * 50)
        print(definitions[-2000:])
        
        # Extract legal references
        print(f"\n⚖️ LEGAL CITATIONS FOUND IN DEFINITIONS")
        print("-" * 50)
        
        # Federal Code references
        federal_refs = re.findall(r'(?:IRC|Internal Revenue Code)[^.]*(?:Section|§)\s*\d+[^\n.]*', definitions, re.IGNORECASE)
        print(f"📜 Federal IRC References ({len(federal_refs)})")
        for i, ref in enumerate(federal_refs[:10]):  # Show first 10
            print(f"  {i+1}. {ref.strip()}")
        if len(federal_refs) > 10:
            print(f"  ... and {len(federal_refs)-10} more")
            
        # California State Code references  
        ca_refs = re.findall(r'(?:California|Health.*Safety|Revenue.*Taxation)[^.]*(?:Code|Section|§)\s*[0-9.]+[^\n.]*', definitions, re.IGNORECASE)
        print(f"\n🏛️ California State Code References ({len(ca_refs)})")
        for i, ref in enumerate(ca_refs[:10]):  # Show first 10
            print(f"  {i+1}. {ref.strip()}")
        if len(ca_refs) > 10:
            print(f"  ... and {len(ca_refs)-10} more")
            
        # CFR (Code of Federal Regulations) references
        cfr_refs = re.findall(r'(?:CFR|Code of Federal Regulations)[^.]*(?:Section|§)?\s*[0-9.]+[^\n.]*', definitions, re.IGNORECASE)
        print(f"\n📚 CFR References ({len(cfr_refs)})")
        for i, ref in enumerate(cfr_refs[:5]):
            print(f"  {i+1}. {ref.strip()}")
            
        # Public Law references
        pl_refs = re.findall(r'Public Law[^.]*[0-9-]+[^\n.]*', definitions, re.IGNORECASE)
        print(f"\n🏛️ Public Law References ({len(pl_refs)})")
        for i, ref in enumerate(pl_refs):
            print(f"  {i+1}. {ref.strip()}")
    
    # Check other sections for legal references
    print(f"\n⚖️ LEGAL REFERENCES ACROSS ALL SECTIONS")
    print("-" * 50)
    
    section_legal_counts = {}
    
    for section_name, content in result.extracted_content.items():
        if section_name == "general":  # Skip duplicates
            continue
            
        # Count different types of legal references
        irc_count = len(re.findall(r'(?:IRC|Internal Revenue Code)[^.]*(?:Section|§)\s*\d+', content, re.IGNORECASE))
        ca_code_count = len(re.findall(r'(?:Health.*Safety|Revenue.*Taxation)[^.]*(?:Code|Section)\s*[0-9.]+', content, re.IGNORECASE))
        cfr_count = len(re.findall(r'(?:CFR|Code of Federal Regulations)', content, re.IGNORECASE))
        section_refs = len(re.findall(r'§\s*103\d+', content))  # Internal CA section references
        
        total_refs = irc_count + ca_code_count + cfr_count + section_refs
        
        if total_refs > 0:
            section_legal_counts[section_name] = {
                'total': total_refs,
                'irc': irc_count,
                'ca_code': ca_code_count, 
                'cfr': cfr_count,
                'internal_refs': section_refs,
                'content_size': len(content)
            }
    
    # Sort by total references
    sorted_sections = sorted(section_legal_counts.items(), key=lambda x: x[1]['total'], reverse=True)
    
    print(f"📊 LEGAL REFERENCE DENSITY BY SECTION")
    print("Section | Total Refs | IRC | CA Code | CFR | Internal | Content Size")
    print("-" * 80)
    
    for section_name, counts in sorted_sections:
        print(f"{section_name[:20]:20} | {counts['total']:9} | {counts['irc']:3} | {counts['ca_code']:7} | {counts['cfr']:3} | {counts['internal_refs']:8} | {counts['content_size']:,}")
    
    # Look for specific regulatory patterns
    print(f"\n🎯 REGULATORY ARCHITECTURE PATTERNS")
    print("-" * 50)
    
    # Check for cross-references between sections
    for section_name, content in result.extracted_content.items():
        if section_name == "general":
            continue
            
        # Find references to other CA sections
        other_section_refs = re.findall(r'(?:Section|§)\s*103(?!25\b)\d+', content)  # Exclude self-references
        
        if len(other_section_refs) > 3:  # Only show sections with significant cross-references
            print(f"🔗 {section_name}: {len(other_section_refs)} cross-references to other sections")
            unique_refs = list(set(other_section_refs))[:5]  # Show first 5 unique
            print(f"   Examples: {', '.join(unique_refs)}")

if __name__ == "__main__":
    examine_legal_references()