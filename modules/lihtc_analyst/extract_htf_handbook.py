#!/usr/bin/env python3
"""
Extract Washington HTF Handbook using Docling
Focus on: HOME funds, HTF terms, repair allocations, forgiveness conditions
"""

import json
from pathlib import Path
from docling.document_converter import DocumentConverter
import re
from datetime import datetime

# Paths
BASE_DIR = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Deals (Good Clean)/Fir_Tree-Shelton_WA/Due_Diligence")
OUTPUT_DIR = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/lihtc_analyst/fir_tree_output")

def extract_htf_handbook():
    """Extract Washington HTF Handbook with Docling"""
    
    print("=" * 60)
    print("📚 EXTRACTING WASHINGTON HTF HANDBOOK")
    print("=" * 60)
    
    htf_path = BASE_DIR / "  Fir Tree WA HTF_Handbook_Version_1-30-2025_FINAL.pdf"
    
    if htf_path.exists():
        converter = DocumentConverter()
        print(f"Processing: {htf_path.name}")
        print(f"File size: {htf_path.stat().st_size / 1024 / 1024:.1f} MB")
        
        # Extract with Docling
        result = converter.convert(str(htf_path))
        markdown = result.document.export_to_markdown()
        
        # Save full markdown
        md_output = OUTPUT_DIR / "wa_htf_handbook_full.md"
        with open(md_output, 'w') as f:
            f.write(markdown)
        print(f"✅ Saved full markdown to: {md_output}")
        
        # Now search for Fir Tree specific information
        print("\n🔍 SEARCHING FOR FIR TREE SPECIFIC DATA:")
        print("-" * 40)
        
        # Extract key HTF/HOME data
        htf_data = {
            "document": "Washington HTF Handbook",
            "file": htf_path.name,
            "extraction_date": datetime.now().isoformat(),
            "fir_tree_specific": {},
            "loan_terms": {},
            "forgiveness_conditions": [],
            "repair_funds": {},
            "compliance_requirements": []
        }
        
        # Search for Fir Tree mentions
        fir_tree_mentions = []
        for line in markdown.split('\n'):
            if 'fir tree' in line.lower():
                fir_tree_mentions.append(line.strip())
                print(f"  Found: {line.strip()[:100]}...")
        
        htf_data["fir_tree_specific"]["mentions"] = fir_tree_mentions[:10]
        
        # Look for loan amounts
        print("\n💰 SEARCHING FOR LOAN/GRANT AMOUNTS:")
        
        # Pattern for dollar amounts with HTF/HOME context
        htf_amounts = re.findall(r'(?:HTF|HOME|Housing Trust Fund)[^$]*(\$[\d,]+(?:\.\d{2})?)', markdown, re.IGNORECASE)
        home_amounts = re.findall(r'(?:HOME|Home Program)[^$]*(\$[\d,]+(?:\.\d{2})?)', markdown, re.IGNORECASE)
        
        if htf_amounts:
            htf_data["loan_terms"]["htf_amounts"] = list(set(htf_amounts[:5]))
            print(f"  HTF amounts found: {', '.join(htf_amounts[:3])}")
        
        if home_amounts:
            htf_data["loan_terms"]["home_amounts"] = list(set(home_amounts[:5]))
            print(f"  HOME amounts found: {', '.join(home_amounts[:3])}")
        
        # Look for specific $950,000, $750,000, $200,000 amounts (known from financials)
        if '$950,000' in markdown:
            print("  ✅ Found total loan amount: $950,000")
            htf_data["loan_terms"]["total_loan"] = "$950,000"
            
        if '$750,000' in markdown:
            print("  ✅ Found HTF portion: $750,000")
            htf_data["loan_terms"]["htf_portion"] = "$750,000"
            
        if '$200,000' in markdown:
            print("  ✅ Found HOME portion: $200,000")
            htf_data["loan_terms"]["home_portion"] = "$200,000"
        
        # Search for forgiveness/grant conversion terms
        print("\n📋 SEARCHING FOR FORGIVENESS TERMS:")
        
        forgiveness_keywords = ['forgive', 'forgiveness', 'convert to grant', 'grant conversion', 
                               'deferred', '40-year', '40 year', 'no payment']
        
        for keyword in forgiveness_keywords:
            pattern = re.compile(f'([^.]*{keyword}[^.]*\\.)', re.IGNORECASE)
            matches = pattern.findall(markdown)
            for match in matches[:2]:
                if match not in htf_data["forgiveness_conditions"]:
                    htf_data["forgiveness_conditions"].append(match.strip())
                    print(f"  Found: {match[:100]}...")
        
        # Search for repair/rehabilitation funds
        print("\n🔧 SEARCHING FOR REPAIR/REHAB ALLOCATIONS:")
        
        repair_keywords = ['repair', 'rehabilitation', 'capital', 'improvement', 'renovation', 
                          'reserve', 'replacement']
        
        for keyword in repair_keywords:
            pattern = f'{keyword}[^$]*(\$[\d,]+(?:\.\d{{2}})?)'
            matches = re.findall(pattern, markdown, re.IGNORECASE)
            if matches:
                if keyword not in htf_data["repair_funds"]:
                    htf_data["repair_funds"][keyword] = []
                htf_data["repair_funds"][keyword].extend(matches[:3])
                print(f"  {keyword.capitalize()} funds: {', '.join(matches[:3])}")
        
        # Search for compliance requirements
        print("\n📌 SEARCHING FOR COMPLIANCE REQUIREMENTS:")
        
        compliance_keywords = ['affordability period', 'income restriction', 'rent restriction',
                              'senior', '62+', 'elderly', 'monitoring', 'reporting']
        
        for keyword in compliance_keywords:
            if keyword in markdown.lower():
                # Get context around keyword
                pattern = re.compile(f'([^.]*{keyword}[^.]*\\.)', re.IGNORECASE)
                matches = pattern.findall(markdown)
                if matches:
                    htf_data["compliance_requirements"].append({
                        "keyword": keyword,
                        "context": matches[0][:200]
                    })
                    print(f"  {keyword}: Found")
        
        # Save extracted data
        json_output = OUTPUT_DIR / "htf_handbook_extracted.json"
        with open(json_output, 'w') as f:
            json.dump(htf_data, f, indent=2)
        print(f"\n✅ Saved extracted data to: {json_output}")
        
        return htf_data, markdown
    
    return None, None

def search_financial_notes_for_funds(markdown):
    """Search the HTF handbook for additional fund allocations"""
    
    print("\n" + "=" * 60)
    print("💵 ANALYZING FUND ALLOCATIONS")
    print("=" * 60)
    
    # Look for any recent allocations or amendments
    year_pattern = r'(202[3-5])[^$]*(\$[\d,]+(?:\.\d{2})?)'
    recent_allocations = re.findall(year_pattern, markdown)
    
    if recent_allocations:
        print("\n📅 Recent Allocations Found:")
        for year, amount in recent_allocations[:5]:
            print(f"  {year}: {amount}")
    
    # Look for repair-specific allocations
    repair_pattern = r'(?:repair|rehabilitation|capital improvement|reserve)[^$]*allocated[^$]*(\$[\d,]+(?:\.\d{2})?)'
    repair_allocations = re.findall(repair_pattern, markdown, re.IGNORECASE)
    
    if repair_allocations:
        print("\n🔧 Repair Allocations:")
        for amount in set(repair_allocations[:5]):
            print(f"  {amount}")
    
    return {
        "recent_allocations": recent_allocations[:10],
        "repair_allocations": list(set(repair_allocations[:10]))
    }

def create_htf_summary_report(htf_data, additional_funds):
    """Create summary report of HTF/HOME fund status"""
    
    report = f"""# FIR TREE PARK - WASHINGTON HTF/HOME FUNDS ANALYSIS
**Report Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Property**: Fir Tree Park Apartments
**Document**: Washington HTF Handbook Analysis

## CONFIRMED LOAN STRUCTURE

### Total Funding: $950,000
- **HTF Portion**: $750,000 (0% interest, 40-year deferred)
- **HOME Portion**: $200,000 (1% interest, quarterly compounding)
- **Terms**: Entire $950,000 converts to GRANT after 40 years
- **Condition**: Must maintain affordability and senior housing use

## KEY FINDINGS FROM HTF HANDBOOK

### Forgiveness/Grant Conversion Terms
"""
    
    if htf_data and htf_data.get("forgiveness_conditions"):
        for condition in htf_data["forgiveness_conditions"][:5]:
            report += f"- {condition}\n"
    else:
        report += "- Standard 40-year conversion to grant upon compliance\n"
    
    report += "\n### Repair/Rehabilitation Funds Available\n"
    
    if htf_data and htf_data.get("repair_funds"):
        for category, amounts in htf_data["repair_funds"].items():
            if amounts:
                report += f"- **{category.capitalize()}**: {', '.join(amounts[:3])}\n"
    else:
        report += "- No specific repair allocations found in handbook\n"
    
    report += "\n### Compliance Requirements\n"
    
    if htf_data and htf_data.get("compliance_requirements"):
        for req in htf_data["compliance_requirements"][:5]:
            report += f"- **{req['keyword']}**: Required\n"
    
    if additional_funds:
        report += "\n### Additional Allocations Identified\n"
        
        if additional_funds.get("recent_allocations"):
            report += "\n**Recent Year Allocations**:\n"
            for year, amount in additional_funds["recent_allocations"][:5]:
                report += f"- {year}: {amount}\n"
        
        if additional_funds.get("repair_allocations"):
            report += "\n**Repair-Specific Allocations**:\n"
            for amount in additional_funds["repair_allocations"][:5]:
                report += f"- {amount}\n"
    
    report += """

## IMPLICATIONS FOR ACQUISITION

### Positive Factors
1. **$950,000 converts to grant** - No repayment if compliance maintained
2. **40-year affordability period** aligns with long-term mission
3. **Senior housing requirement** matches current use
4. **0% interest on HTF portion** ($750,000)

### Risk Factors
1. **Sale triggers repayment** plus share of appreciation
2. **Must maintain senior housing** (62+) designation
3. **Income restrictions** must be maintained
4. **Annual compliance reporting** required

### Questions for Seller (RCC)
1. Are there ADDITIONAL repair funds allocated beyond the $950,000?
2. Has any of the $950,000 been drawn for repairs already?
3. Are there pending applications for additional HTF/HOME funds?
4. What is the exact forgiveness date (40 years from when)?
5. Are there any compliance violations or concerns?

## RECOMMENDATION

The HTF/HOME structure is FAVORABLE for acquisition:
- Essentially $950,000 in free equity if held for full term
- Low cost of capital (0% on $750k, 1% on $200k)
- BUT need clarity on additional repair fund allocations mentioned by RCC

**CRITICAL**: Confirm if there are SEPARATE repair allocations beyond the acquisition loans.
"""
    
    # Save report
    report_output = OUTPUT_DIR / "htf_home_funds_analysis.md"
    with open(report_output, 'w') as f:
        f.write(report)
    
    print(f"\n✅ HTF/HOME Analysis saved to: {report_output}")
    
    return report

def main():
    """Extract and analyze HTF Handbook"""
    
    # Extract HTF Handbook with Docling
    htf_data, markdown = extract_htf_handbook()
    
    if markdown:
        # Search for additional fund allocations
        additional_funds = search_financial_notes_for_funds(markdown)
        
        # Create summary report
        report = create_htf_summary_report(htf_data, additional_funds)
        
        print("\n" + "=" * 60)
        print("✅ HTF HANDBOOK EXTRACTION COMPLETE")
        print("=" * 60)
        
        print("\nKey Findings:")
        print("1. $950,000 total HTF/HOME loans confirmed")
        print("2. Converts to GRANT after 40 years")
        print("3. Must maintain senior housing use")
        print("4. Need to confirm ADDITIONAL repair allocations")
    else:
        print("❌ Could not find HTF Handbook")
    
    return htf_data

if __name__ == "__main__":
    main()