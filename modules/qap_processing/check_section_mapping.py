#!/usr/bin/env python3
"""
Check Section Mapping
Debug what sections we extracted vs what the validator expects
"""

from docling_4strategy_integration import DoclingStrategyIntegration

def check_section_mapping():
    """Check what sections we extracted and what validator expects"""
    
    print("🔍 CA SECTION MAPPING ANALYSIS")
    print("=" * 50)
    
    # Get extracted sections
    integration = DoclingStrategyIntegration()
    result = integration.process_jurisdiction("CA")
    
    print(f"\n📊 EXTRACTED SECTIONS ({len(result.extracted_content)} total)")
    print("-" * 30)
    
    for section_key, content in result.extracted_content.items():
        print(f"✅ {section_key}")
        print(f"   Length: {len(content):,} characters")
        
        # Show first 150 chars to identify content
        preview = content.replace('\n', ' ')[:150] + "..."
        print(f"   Preview: {preview}")
        
        # Check for specific keywords
        content_lower = content.lower()
        keywords_found = []
        
        if any(kw in content_lower for kw in ["scoring", "point", "criteria", "selection"]):
            keywords_found.append("SCORING")
        if any(kw in content_lower for kw in ["threshold", "requirement", "application"]):
            keywords_found.append("THRESHOLD")
        if any(kw in content_lower for kw in ["geographic", "apportionment", "set-aside"]):
            keywords_found.append("GEOGRAPHIC")
        if any(kw in content_lower for kw in ["compliance", "monitoring", "regulatory"]):
            keywords_found.append("COMPLIANCE")
        if any(kw in content_lower for kw in ["financial", "underwriting", "feasibility"]):
            keywords_found.append("FINANCIAL")
        if any(kw in content_lower for kw in ["negative", "penalty", "deduction"]):
            keywords_found.append("NEGATIVE")
        if any(kw in content_lower for kw in ["tiebreaker", "tie-breaker", "tie breaker"]):
            keywords_found.append("TIEBREAKER")
        if any(kw in content_lower for kw in ["deadline", "procedure", "submission"]):
            keywords_found.append("PROCEDURES")
            
        if keywords_found:
            print(f"   Keywords: {', '.join(keywords_found)}")
        print()
    
    # Show expected validation sections
    print(f"\n🎯 EXPECTED VALIDATION SECTIONS")
    print("-" * 30)
    
    expected_sections = [
        "Complete Scoring Criteria",
        "Geographic Apportionments & Set-Asides", 
        "Threshold Requirements",
        "Application Procedures & Deadlines",
        "Compliance & Monitoring",
        "Financial Underwriting Standards",
        "Tiebreaker Criteria",
        "Negative Points"
    ]
    
    for section in expected_sections:
        print(f"🔍 {section}")
    
    # Suggest mapping
    print(f"\n💡 SUGGESTED MAPPING")
    print("-" * 30)
    
    mapping_suggestions = [
        ("section_scoring_criteria", "Complete Scoring Criteria"),
        ("section_geographic_apportionments", "Geographic Apportionments & Set-Asides"),
        ("section_threshold_requirements", "Threshold Requirements"), 
        ("section_threshold_requirements", "Application Procedures & Deadlines"),  # Same section
        ("section_compliance_monitoring", "Compliance & Monitoring"),
        ("section_financial_requirements", "Financial Underwriting Standards"),
        ("section_scoring_criteria", "Tiebreaker Criteria"),  # Usually in scoring
        ("section_scoring_criteria", "Negative Points")  # Usually in scoring
    ]
    
    for extracted, expected in mapping_suggestions:
        if extracted in result.extracted_content:
            size = len(result.extracted_content[extracted])
            print(f"✅ {extracted} ({size:,} chars) → {expected}")
        else:
            print(f"❌ {extracted} → {expected} (NOT FOUND)")

if __name__ == "__main__":
    check_section_mapping()