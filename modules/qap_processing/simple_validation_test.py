#!/usr/bin/env python3
"""
Simple validation test to check what sections we actually have
"""

from docling_4strategy_integration import DoclingStrategyIntegration
from ca_qap_validation_checklist import CaliforniaQAPValidator

def test_validation():
    print("🔍 SIMPLE VALIDATION TEST")
    print("=" * 40)
    
    # Get extracted sections
    integration = DoclingStrategyIntegration()
    result = integration.process_jurisdiction("CA")
    
    print(f"\n📊 EXTRACTED SECTIONS ({len(result.extracted_content)})")
    for key, content in result.extracted_content.items():
        print(f"✅ '{key}': {len(content):,} chars")
    
    # Get expected sections
    validator = CaliforniaQAPValidator()
    
    print(f"\n🎯 EXPECTED SECTIONS ({len(validator.critical_sections)})")
    for key, section in validator.critical_sections.items():
        print(f"📋 '{key}': {section.section_name}")
    
    # Check matches
    print(f"\n🔄 MATCHING ANALYSIS")
    for expected_key in validator.critical_sections.keys():
        if expected_key in result.extracted_content:
            size = len(result.extracted_content[expected_key])
            print(f"✅ '{expected_key}' FOUND: {size:,} chars")
        else:
            print(f"❌ '{expected_key}' MISSING")

if __name__ == "__main__":
    test_validation()