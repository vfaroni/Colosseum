#!/usr/bin/env python3
"""
Show the actual definitions section with all the legal references
"""

from docling_connector import DoclingConnector

def show_definitions_with_legal_refs():
    """Show definitions section with legal references"""
    
    print("📚 CA DEFINITIONS SECTION - LEGAL REFERENCES")
    print("=" * 60)
    
    connector = DoclingConnector()
    pdf_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/CA/current/CA_2025_QAP_Regulations_Dec_2024.pdf"
    
    # Get the actual docling output with proper text
    from docling.document_converter import DocumentConverter
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    doc_text = result.document.export_to_markdown()
    
    print(f"Total document: {len(doc_text):,} characters")
    
    # Find the definitions section specifically
    import re
    
    # Look for Section 10302 Definitions
    definitions_match = re.search(r'(##\s*Section\s+10302\..*?)(?=##\s*Section\s+103\d+\.|\Z)', doc_text, re.DOTALL)
    
    if definitions_match:
        definitions_content = definitions_match.group(1)
        print(f"\n📋 DEFINITIONS SECTION FOUND")
        print(f"Length: {len(definitions_content):,} characters")
        
        # Show the end where legal references are concentrated
        print(f"\n📚 END OF DEFINITIONS (last 2000 chars - the 'WOW' legal references):")
        print("-" * 60)
        print(definitions_content[-2000:])
        
        # Extract and count legal references
        print(f"\n⚖️ LEGAL REFERENCES ANALYSIS")
        print("-" * 60)
        
        # Federal IRC references
        irc_refs = re.findall(r'IRC[^.]*Section[^.]*\d+[^.]*|Internal Revenue Code[^.]*Section[^.]*\d+[^.]*', definitions_content, re.IGNORECASE)
        print(f"📜 Federal IRC References: {len(irc_refs)}")
        for i, ref in enumerate(irc_refs[:5]):
            print(f"  {i+1}. {ref.strip()}")
        if len(irc_refs) > 5:
            print(f"  ... and {len(irc_refs)-5} more")
        
        # California Health & Safety Code
        hs_refs = re.findall(r'Health.*Safety.*Code.*Section[s]?.*[0-9.]+[^.]*', definitions_content, re.IGNORECASE)
        print(f"\n🏛️ CA Health & Safety Code: {len(hs_refs)}")
        for i, ref in enumerate(hs_refs[:3]):
            print(f"  {i+1}. {ref.strip()}")
        
        # California Revenue & Taxation Code
        rt_refs = re.findall(r'Revenue.*Taxation.*Code.*Section[s]?.*[0-9.]+[^.]*', definitions_content, re.IGNORECASE)
        print(f"\n💰 CA Revenue & Taxation Code: {len(rt_refs)}")
        for i, ref in enumerate(rt_refs[:3]):
            print(f"  {i+1}. {ref.strip()}")
        
        # CFR references
        cfr_refs = re.findall(r'CFR[^.]*[0-9.]+[^.]*|Code of Federal Regulations[^.]*', definitions_content, re.IGNORECASE)
        print(f"\n📚 Federal CFR References: {len(cfr_refs)}")
        for i, ref in enumerate(cfr_refs):
            print(f"  {i+1}. {ref.strip()}")
            
        print(f"\n🎯 TOTAL LEGAL CITATIONS: {len(irc_refs) + len(hs_refs) + len(rt_refs) + len(cfr_refs)}")
        
    else:
        print("❌ Definitions section not found in expected format")
        
        # Show what sections we do find
        sections = re.findall(r'##\s*Section\s+103\d+\..*', doc_text)
        print(f"Found sections: {len(sections)}")
        for section in sections[:5]:
            print(f"  - {section}")

if __name__ == "__main__":
    show_definitions_with_legal_refs()