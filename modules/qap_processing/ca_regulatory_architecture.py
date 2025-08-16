#!/usr/bin/env python3
"""
CA Regulatory Architecture Framework
New approach: Primary=State Regulatory Sections, Secondary=Generic LIHTC mapping

This implements your 3-point recommendation:
1. Primary Structure: Use CA's 17 regulatory sections as designed
2. Secondary Mapping: Optionally map to generic categories for cross-state analysis  
3. Preserve Legal Citations: Maintain §10300-§10337 structure for compliance

Built by Structured Consultants LLC
"""

import json
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from docling_4strategy_integration import DoclingStrategyIntegration

@dataclass
class LegalReference:
    """Legal citation found in QAP content"""
    reference_type: str  # 'federal_irc', 'state_code', 'cfr', 'public_law', 'internal_section'
    citation: str
    section_found_in: str
    context: str  # Surrounding text for context

@dataclass
class CARegulatorySectionInfo:
    """Information about a CA regulatory section"""
    section_number: str  # e.g., "§10300"
    section_title: str   # e.g., "Purpose and Scope"
    content: str
    character_count: int
    legal_references: List[LegalReference]
    cross_references: List[str]  # References to other CA sections
    lihtc_category: str = None  # Optional mapping to generic LIHTC category

class CARegulatorySectionExtractor:
    """Extracts CA regulatory sections with full legal reference mapping"""
    
    def __init__(self):
        self.ca_sections = self._define_ca_regulatory_sections()
        self.legal_patterns = self._define_legal_patterns()
        self.lihtc_mappings = self._define_lihtc_category_mappings()
        
    def _define_ca_regulatory_sections(self) -> Dict[str, Dict[str, str]]:
        """Define all 17 CA regulatory sections with their official titles"""
        
        return {
            "section_purpose_scope": {
                "number": "§10300",
                "title": "Purpose and Scope",
                "description": "Establishes authority and scope of CA LIHTC programs"
            },
            "section_definitions": {
                "number": "§10302", 
                "title": "Definitions",
                "description": "Legal definitions with extensive federal and state code references"
            },
            "section_general_provisions": {
                "number": "§10305",
                "title": "General Provisions", 
                "description": "General administrative provisions"
            },
            "section_reservations": {
                "number": "§10310",
                "title": "Reservations of Tax Credits",
                "description": "Credit reservation procedures and requirements"
            },
            "section_geographic_apportionments": {
                "number": "§10315",
                "title": "Set-Asides and Apportionments", 
                "description": "Geographic allocation and set-aside requirements"
            },
            "section_eligibility": {
                "number": "§10317",
                "title": "State Tax Credit Eligibility Requirements",
                "description": "State-specific eligibility criteria"
            },
            "section_committee_actions": {
                "number": "§10320",
                "title": "Actions by the Committee",
                "description": "CTCAC decision-making procedures"
            },
            "section_threshold_requirements": {
                "number": "§10322",
                "title": "Application Requirements",
                "description": "Threshold requirements for application submission"
            },
            "section_recovery_act": {
                "number": "§10323", 
                "title": "The American Recovery and Reinvestment Act of 2009",
                "description": "ARRA-specific provisions"
            },
            "section_scoring_criteria": {
                "number": "§10325",
                "title": "Application Selection Criteria-Credit Ceiling Applications",
                "description": "Complete scoring system including negative points and tiebreakers"
            },
            "section_bond_criteria": {
                "number": "§10326",
                "title": "Application Selection Criteria-Tax-Exempt Bond Applications", 
                "description": "Bond-financed project criteria"
            },
            "section_financial_requirements": {
                "number": "§10327",
                "title": "Financial Feasibility and Determination of Credit Amounts",
                "description": "Underwriting standards and credit calculations"
            },
            "section_conditions": {
                "number": "§10328",
                "title": "Conditions on Credit Reservations",
                "description": "Conditions and requirements for credit awards"
            },
            "section_appeals": {
                "number": "§10330",
                "title": "Appeals",
                "description": "Appeal procedures and requirements"
            },
            "section_fees": {
                "number": "§10335", 
                "title": "Fees and Performance Deposit",
                "description": "Fee structure and deposit requirements"
            },
            "section_tenant_rules": {
                "number": "§10336",
                "title": "Laws, Rules, Guidelines, and Regulations for Tenants",
                "description": "Tenant-related requirements and regulations"
            },
            "section_compliance_monitoring": {
                "number": "§10337",
                "title": "Compliance",
                "description": "Ongoing compliance monitoring and reporting requirements"
            }
        }
    
    def _define_legal_patterns(self) -> Dict[str, List[str]]:
        """Define regex patterns for extracting legal references"""
        
        return {
            'federal_irc': [
                r'IRC\s+Section\s+\d+[a-z()]*',
                r'Internal Revenue Code\s+Section\s+\d+[a-z()]*',
                r'26\s+USC\s+\d+[a-z()]*',
                r'Section\s+\d+[a-z()]*\s+of\s+the\s+Internal Revenue Code'
            ],
            'federal_cfr': [
                r'26\s+CFR\s+[\d.]+[a-z()]*',
                r'Code of Federal Regulations[^.]*[\d.]+[a-z()]*'
            ],
            'federal_public_law': [
                r'Public Law\s+No\.\s+\d+-\d+',
                r'P\.L\.\s+\d+-\d+'
            ],
            'ca_health_safety': [
                r'Health\s+and\s+Safety\s+Code\s+Section[s]?\s+[\d.]+[a-z()]*',
                r'H\s*&\s*S\s+Code\s+Section[s]?\s+[\d.]+[a-z()]*'
            ],
            'ca_revenue_taxation': [
                r'Revenue\s+and\s+Taxation\s+Code\s+Section[s]?\s+[\d.]+[a-z()]*',
                r'R\s*&\s*T\s+Code\s+Section[s]?\s+[\d.]+[a-z()]*'
            ],
            'internal_section_refs': [
                r'Section\s+103\d+[a-z()]*',
                r'§\s*103\d+[a-z()]*'
            ]
        }
    
    def _define_lihtc_category_mappings(self) -> Dict[str, str]:
        """Optional mapping to generic LIHTC categories for cross-state analysis"""
        
        return {
            "section_purpose_scope": "administrative_framework",
            "section_definitions": "legal_framework", 
            "section_general_provisions": "administrative_framework",
            "section_reservations": "allocation_procedures",
            "section_geographic_apportionments": "geographic_allocation",
            "section_eligibility": "eligibility_requirements",
            "section_committee_actions": "administrative_procedures", 
            "section_threshold_requirements": "application_requirements",
            "section_recovery_act": "federal_programs",
            "section_scoring_criteria": "selection_criteria",
            "section_bond_criteria": "bond_financing",
            "section_financial_requirements": "underwriting_standards",
            "section_conditions": "award_conditions",
            "section_appeals": "administrative_procedures",
            "section_fees": "administrative_procedures",
            "section_tenant_rules": "compliance_monitoring",
            "section_compliance_monitoring": "compliance_monitoring"
        }
    
    def extract_all_ca_sections(self) -> Dict[str, CARegulatorySectionInfo]:
        """Extract all CA regulatory sections with legal references"""
        
        print("🏛️ EXTRACTING CA REGULATORY ARCHITECTURE")
        print("=" * 60)
        
        # Get raw extraction from docling
        integration = DoclingStrategyIntegration()
        result = integration.process_jurisdiction("CA")
        
        ca_section_info = {}
        
        # Process each section
        for section_key in self.ca_sections.keys():
            section_def = self.ca_sections[section_key]
            
            # Get content from extraction
            content = ""
            if section_key in result.extracted_content:
                content = result.extracted_content[section_key]
            else:
                # Handle the mapping issue - look for content in other keys
                for ext_key, ext_content in result.extracted_content.items():
                    if section_def["number"].replace("§", "") in ext_key or section_def["title"].lower().replace(" ", "_") in ext_key:
                        content = ext_content
                        break
            
            if content:
                # Extract legal references
                legal_refs = self._extract_legal_references(content, section_key)
                
                # Extract cross-references to other CA sections
                cross_refs = self._extract_cross_references(content)
                
                # Create section info object
                section_info = CARegulatorySectionInfo(
                    section_number=section_def["number"],
                    section_title=section_def["title"],
                    content=content,
                    character_count=len(content),
                    legal_references=legal_refs,
                    cross_references=cross_refs,
                    lihtc_category=self.lihtc_mappings.get(section_key)
                )
                
                ca_section_info[section_key] = section_info
                
                print(f"✅ {section_def['number']} - {section_def['title']}")
                print(f"   Content: {len(content):,} chars, Legal refs: {len(legal_refs)}, Cross-refs: {len(cross_refs)}")
            else:
                print(f"❌ {section_def['number']} - {section_def['title']} - NO CONTENT")
        
        return ca_section_info
    
    def _extract_legal_references(self, content: str, section_key: str) -> List[LegalReference]:
        """Extract legal references from section content"""
        
        legal_refs = []
        
        for ref_type, patterns in self.legal_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    # Get context around the match
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end].replace('\n', ' ')
                    
                    legal_ref = LegalReference(
                        reference_type=ref_type,
                        citation=match.group().strip(),
                        section_found_in=section_key,
                        context=context
                    )
                    legal_refs.append(legal_ref)
        
        return legal_refs
    
    def _extract_cross_references(self, content: str) -> List[str]:
        """Extract references to other CA sections"""
        
        cross_refs = []
        
        # Look for references to other sections
        patterns = [
            r'Section\s+103\d+[a-z()]*',
            r'§\s*103\d+[a-z()]*'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            cross_refs.extend([m.strip() for m in matches])
        
        # Remove duplicates and sort
        return sorted(list(set(cross_refs)))
    
    def generate_regulatory_report(self, ca_sections: Dict[str, CARegulatorySectionInfo]) -> str:
        """Generate comprehensive regulatory architecture report"""
        
        report = []
        report.append("# 🏛️ CA REGULATORY ARCHITECTURE ANALYSIS")
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Total Sections**: {len(ca_sections)}")
        report.append("")
        
        # Summary stats
        total_chars = sum(section.character_count for section in ca_sections.values())
        total_legal_refs = sum(len(section.legal_references) for section in ca_sections.values())
        total_cross_refs = sum(len(section.cross_references) for section in ca_sections.values())
        
        report.append("## 📊 SUMMARY STATISTICS")
        report.append(f"- **Total Content**: {total_chars:,} characters")
        report.append(f"- **Legal References**: {total_legal_refs} citations")
        report.append(f"- **Cross-References**: {total_cross_refs} internal section references")
        report.append("")
        
        # Section-by-section analysis
        report.append("## 📋 SECTION-BY-SECTION ANALYSIS")
        report.append("")
        
        for section_key, section_info in ca_sections.items():
            report.append(f"### {section_info.section_number} - {section_info.section_title}")
            report.append(f"**Content**: {section_info.character_count:,} characters")
            report.append(f"**LIHTC Category**: {section_info.lihtc_category}")
            report.append("")
            
            if section_info.legal_references:
                report.append("**Legal References**:")
                ref_types = {}
                for ref in section_info.legal_references:
                    if ref.reference_type not in ref_types:
                        ref_types[ref.reference_type] = []
                    ref_types[ref.reference_type].append(ref.citation)
                
                for ref_type, citations in ref_types.items():
                    report.append(f"- {ref_type}: {len(citations)} citations")
                    for citation in citations[:3]:  # Show first 3
                        report.append(f"  - {citation}")
                    if len(citations) > 3:
                        report.append(f"  - ... and {len(citations)-3} more")
                report.append("")
            
            if section_info.cross_references:
                report.append(f"**Cross-References**: {', '.join(section_info.cross_references[:5])}")
                if len(section_info.cross_references) > 5:
                    report.append(f"... and {len(section_info.cross_references)-5} more")
                report.append("")
            
            report.append("---")
            report.append("")
        
        return "\n".join(report)

def main():
    """Test the CA regulatory architecture extractor"""
    
    extractor = CARegulatorySectionExtractor()
    ca_sections = extractor.extract_all_ca_sections()
    
    print(f"\n📊 EXTRACTION COMPLETE")
    print(f"Sections found: {len(ca_sections)}")
    
    # Generate report
    report = extractor.generate_regulatory_report(ca_sections)
    
    # Save report
    report_path = "ca_regulatory_architecture_report.md"
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"📄 Report saved: {report_path}")
    
    # Show key insights
    print(f"\n🎯 KEY INSIGHTS")
    
    # Sections with most legal references
    legal_dense = sorted(ca_sections.items(), 
                        key=lambda x: len(x[1].legal_references), 
                        reverse=True)[:3]
    
    print(f"📚 Most Legal References:")
    for section_key, section_info in legal_dense:
        print(f"  {section_info.section_number}: {len(section_info.legal_references)} references")
    
    # Largest sections by content
    content_large = sorted(ca_sections.items(),
                          key=lambda x: x[1].character_count,
                          reverse=True)[:3]
    
    print(f"📄 Largest Sections:")
    for section_key, section_info in content_large:
        print(f"  {section_info.section_number}: {section_info.character_count:,} characters")

if __name__ == "__main__":
    main()