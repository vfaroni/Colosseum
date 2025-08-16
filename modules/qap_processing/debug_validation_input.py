#!/usr/bin/env python3
"""
Debug what the validation framework actually receives
"""

from docling_4strategy_integration import DoclingStrategyIntegration
from ca_qap_validation_checklist import CaliforniaQAPValidator

def debug_validation_input():
    print("🔍 DEBUGGING VALIDATION INPUT")
    print("=" * 50)
    
    # Get extracted content
    integration = DoclingStrategyIntegration()
    result = integration.process_jurisdiction("CA")
    
    print(f"\n📊 EXTRACTED CONTENT FROM INTEGRATION")
    print(f"Keys: {list(result.extracted_content.keys())}")
    for key, content in result.extracted_content.items():
        print(f"  {key}: {len(content):,} chars")
    
    # Run validation and see what it gets
    validator = CaliforniaQAPValidator()
    
    print(f"\n🔍 VALIDATION FRAMEWORK TEST")
    print(f"Expected keys: {list(validator.critical_sections.keys())}")
    
    # Manual test of what validation would see
    for expected_key in validator.critical_sections.keys():
        if expected_key in result.extracted_content:
            content = result.extracted_content[expected_key]
            print(f"✅ {expected_key}: {len(content):,} chars")
        else:
            print(f"❌ {expected_key}: NOT FOUND")
    
    # Test the actual validation process
    validation_results = validator.validate_ca_qap_extraction(result.extracted_content)
    
    print(f"\n📋 VALIDATION RESULTS")
    print(f"Overall completeness: {validation_results.get('overall_completeness', 'unknown')}")
    print(f"Sections found: {validation_results.get('critical_sections_found', 'unknown')}")

if __name__ == "__main__":
    debug_validation_input()