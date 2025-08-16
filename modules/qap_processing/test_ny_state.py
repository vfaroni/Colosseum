#!/usr/bin/env python3
"""
Test NY state extraction to prove architecture scalability
"""

from state_regulatory_framework import StateRegulatorFramework

def test_ny_state():
    """Test framework on NY state"""
    
    print("🏛️ NEW YORK QAP EXTRACTION TEST")
    print("=" * 40)
    
    framework = StateRegulatorFramework()
    
    state = "NY"
    
    try:
        print(f"🚀 Testing {state} QAP extraction...")
        
        result = framework.extract_state_regulatory_framework(state)
        
        print(f"\n📊 {state} RESULTS:")
        print(f"  Sections: {result.total_sections}")
        print(f"  Content: {result.total_characters:,} chars")
        print(f"  Legal refs: {result.total_legal_references}")
        print(f"  Time: {result.processing_time_seconds:.2f}s")
        
        # Show what sections were found
        print(f"\n📋 SECTIONS FOUND:")
        for section_key, section_info in result.sections.items():
            print(f"  {section_info.section_number}: {section_info.character_count:,} chars, {len(section_info.legal_references)} legal refs")
        
        # Save results
        output_files = framework.save_framework_result(result)
        print(f"\n📄 OUTPUT FILES:")
        for file_type, path in output_files.items():
            print(f"  {file_type.upper()}: {path}")
        
        print(f"\n✅ {state} extraction successful!")
        return True
        
    except Exception as e:
        print(f"❌ {state} extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ny_state()