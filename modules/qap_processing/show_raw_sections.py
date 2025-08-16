#!/usr/bin/env python3
"""
Show raw extracted sections before generic LIHTC mapping destroys them
"""

from docling_4strategy_integration import DoclingStrategyIntegration

def show_raw_extraction():
    """Show what we actually extract before the mapping layer"""
    
    print("🏛️ RAW CA REGULATORY SECTIONS (BEFORE MAPPING)")
    print("=" * 60)
    
    # Access the raw docling extraction
    integration = DoclingStrategyIntegration()
    
    # Get the raw result before mapping
    result = integration.process_jurisdiction("CA")
    
    # But we need to bypass the mapping - let's get the original docling output
    from modules.qap_processing.docling_connector import DoclingConnector
    
    connector = DoclingConnector()
    pdf_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/CA/current/CA_2025_QAP_Regulations_Dec_2024.pdf"
    
    # Get raw chunks before mapping
    raw_chunks = connector.process_pdf_with_strategy(pdf_path, "complex_outline", {})
    
    print(f"📊 RAW SECTIONS EXTRACTED: {len(raw_chunks)}")
    
    # Show each section
    for section_key, content in raw_chunks.items():
        print(f"\n✅ {section_key}")
        print(f"   Length: {len(content):,} characters")
        
        # Show preview
        preview = content.replace('\n', ' ')[:200] + "..."
        print(f"   Preview: {preview}")
        
        # For definitions, show the end where legal references are
        if "definition" in section_key.lower():
            print(f"\n📚 END OF DEFINITIONS (last 1000 chars with legal references):")
            print("-" * 50)
            print(content[-1000:])

if __name__ == "__main__":
    show_raw_extraction()