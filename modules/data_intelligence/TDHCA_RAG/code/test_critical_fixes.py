#!/usr/bin/env python3
"""
Test the critical fixes: county extraction and project name patterns
"""

from pathlib import Path
from improved_tdhca_extractor import ImprovedTDHCAExtractor

def test_critical_fixes():
    """Test county and project name fixes on known files"""
    
    base_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites"
    extractor = ImprovedTDHCAExtractor(base_path)
    
    # Test files with known issues
    test_files = [
        "25427.pdf",  # Bay Terrace - was showing "ϳϳϱϮϬ", county "Zip"
        "25412.pdf",  # Wyndham Park - was showing truncated name, county "Zip"
    ]
    
    print("🔧 Testing Critical Fixes")
    print("=" * 60)
    print("Testing: County extraction + Project name patterns")
    print()
    
    for filename in test_files:
        pdf_files = list(Path(base_path).glob(f"**/{filename}"))
        if pdf_files:
            print(f"📁 Testing {filename}")
            print("-" * 40)
            
            try:
                result = extractor.process_application_improved(pdf_files[0])
                
                if result:
                    print(f"✅ Project Name: '{result.project_name}'")
                    print(f"🏛️ County: '{result.county}'")  # Should NOT be "Zip"
                    print(f"📍 Address: '{result.street_address}, {result.city} {result.zip_code}'")
                    print(f"🏢 Units: {result.total_units}")
                    print(f"🏗️ Developer: '{result.developer_name}'")
                    print(f"📊 Confidence: {result.confidence_scores.get('overall', 0):.2f}")
                    
                    # Validate fixes
                    if result.county == "Zip":
                        print("❌ COUNTY FIX FAILED - still showing 'Zip'")
                    elif result.county:
                        print(f"✅ COUNTY FIX SUCCESS - extracted '{result.county}'")
                    else:
                        print("⚠️ COUNTY EMPTY - needs fallback logic")
                    
                    if "Property City ProgramControl" in result.project_name:
                        print("❌ PROJECT NAME FIX FAILED - still showing generic text")
                    elif result.project_name and len(result.project_name) > 3:
                        print(f"✅ PROJECT NAME FIX SUCCESS - extracted '{result.project_name}'")
                    else:
                        print("⚠️ PROJECT NAME EMPTY - needs better patterns")
                        
                else:
                    print("❌ Extraction failed completely")
                    
            except Exception as e:
                print(f"💥 Error: {e}")
            
            print()
    
    print("🎯 Fix Summary:")
    print("- County extraction: Should show actual county names, not 'Zip'")
    print("- Project names: Should avoid 'Property City ProgramControl began'")
    print("- Addresses: Should be clean without comma issues")

if __name__ == "__main__":
    test_critical_fixes()