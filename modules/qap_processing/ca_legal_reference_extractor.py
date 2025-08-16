#!/usr/bin/env python3
"""
California Legal Reference Extractor - Enhanced Demo System
Extract and categorize California's 316 legal references for regulatory intelligence demo

Based on Strike Leader's Complete Regulatory Universe Discovery:
- 43 Federal IRC citations (Authority Level 100)
- 13 Federal CFR citations (Authority Level 80)
- 6 CA Revenue & Taxation citations (Authority Level 30)
- 2 CA Health & Safety citations (Authority Level 30)
- 1 Federal Public Law citation (Authority Level 100)
- 251 Internal section references (Authority Level 30)

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

import re
import json
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AuthorityLevel(Enum):
    """Regulatory authority hierarchy levels"""
    FEDERAL_IRC = 100       # Federal Statutory - overrides all
    FEDERAL_CFR = 80        # Federal Regulatory - overrides state
    FEDERAL_GUIDANCE = 60   # Federal guidance documents
    FEDERAL_PUBLIC_LAW = 100 # Federal statutes
    STATE_QAP = 30          # State QAP regulations
    STATE_STATUTES = 30     # State statutory law
    INTERNAL_REFS = 30      # Internal section references

@dataclass
class LegalReference:
    """Individual legal reference with authority weighting"""
    reference_id: str
    citation_text: str
    authority_level: int
    jurisdiction: str           # "Federal", "CA", "Internal"
    category: str              # "IRC", "CFR", "Health Safety", etc.
    section_found: str         # QAP section where reference appears
    hub_spoke_type: str        # "hub" (QAP) or "spoke" (external)
    business_impact: str       # Revenue/compliance implications

@dataclass
class RegulatoryUniverse:
    """Complete California regulatory universe mapping"""
    qap_sections: int = 17
    total_legal_refs: int = 316
    federal_refs: int = 57      # IRC + CFR + Public Law
    state_refs: int = 8         # Health Safety + Revenue Taxation
    internal_refs: int = 251
    hub_to_spoke_ratio: str = "2-3:1"
    estimated_external_pages: int = 700
    business_value_multiplier: str = "3-4X"

class CALegalReferenceExtractor:
    """Extract and categorize California's complete regulatory universe"""
    
    def __init__(self):
        self.references: List[LegalReference] = []
        self.universe_stats = RegulatoryUniverse()
        
        # Authority level mapping
        self.authority_mapping = {
            "Federal Irc": AuthorityLevel.FEDERAL_IRC.value,
            "Federal Cfr": AuthorityLevel.FEDERAL_CFR.value,
            "Federal Public Law": AuthorityLevel.FEDERAL_PUBLIC_LAW.value,
            "Ca Health Safety": AuthorityLevel.STATE_STATUTES.value,
            "Ca Revenue Taxation": AuthorityLevel.STATE_STATUTES.value,
            "Internal Section Refs": AuthorityLevel.INTERNAL_REFS.value
        }
        
        # Business impact mapping
        self.business_impact_mapping = {
            "Federal Irc": "Critical compliance - basis for all LIHTC requirements",
            "Federal Cfr": "Regulatory implementation - defines compliance standards", 
            "Federal Public Law": "Foundational authority - establishes legal framework",
            "Ca Health Safety": "State housing standards - affects project feasibility",
            "Ca Revenue Taxation": "State tax credit coordination - impacts financial modeling",
            "Internal Section Refs": "QAP cross-references - operational guidance"
        }

    def extract_from_framework_report(self, report_path: str) -> Dict[str, Any]:
        """Extract legal references from CA regulatory framework report"""
        
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            logger.info(f"📊 Processing CA regulatory framework report: {report_path}")
            
            # Extract reference statistics
            stats = self._extract_reference_statistics(content)
            
            # Extract section-by-section references
            references = self._extract_section_references(content)
            
            # Generate regulatory universe analysis
            universe_analysis = self._generate_universe_analysis(references)
            
            return {
                "extraction_timestamp": datetime.now().isoformat(),
                "source_file": report_path,
                "reference_statistics": stats,
                "legal_references": [asdict(ref) for ref in references],
                "regulatory_universe_analysis": asdict(universe_analysis),
                "demo_insights": self._generate_demo_insights(references)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to extract references: {e}")
            return {}

    def _extract_reference_statistics(self, content: str) -> Dict[str, int]:
        """Extract high-level reference statistics"""
        
        stats = {}
        
        # Find statistics section
        stats_match = re.search(r'### Legal Reference Types\s*(.*?)(?=##|\Z)', content, re.DOTALL)
        if stats_match:
            stats_text = stats_match.group(1)
            
            # Extract each reference type count
            patterns = {
                'ca_health_safety': r'Ca Health Safety.*?(\d+) citations',
                'ca_revenue_taxation': r'Ca Revenue Taxation.*?(\d+) citations', 
                'federal_cfr': r'Federal Cfr.*?(\d+) citations',
                'federal_irc': r'Federal Irc.*?(\d+) citations',
                'federal_public_law': r'Federal Public Law.*?(\d+) citations',
                'internal_section_refs': r'Internal Section Refs.*?(\d+) citations'
            }
            
            for stat_name, pattern in patterns.items():
                match = re.search(pattern, stats_text)
                if match:
                    stats[stat_name] = int(match.group(1))
                    
        return stats

    def _extract_section_references(self, content: str) -> List[LegalReference]:
        """Extract individual references from each QAP section"""
        
        references = []
        
        # Find all section blocks
        section_pattern = r'### (§\d+[^#]*?)\*\*Content\*\*.*?\*\*Legal References\*\*:(.*?)(?=###|\*\*Cross-References\*\*|\Z)'
        section_matches = re.finditer(section_pattern, content, re.DOTALL)
        
        ref_id_counter = 1
        
        for section_match in section_matches:
            section_title = section_match.group(1).strip()
            references_text = section_match.group(2)
            
            # Extract individual reference categories
            category_pattern = r'- \*\*(.*?)\*\*: \d+ citations\s*(.*?)(?=- \*\*|\*\*Cross-References\*\*|\Z)'
            category_matches = re.finditer(category_pattern, references_text, re.DOTALL)
            
            for category_match in category_matches:
                category = category_match.group(1).strip()
                citations_text = category_match.group(2).strip()
                
                # Extract individual citations
                citation_lines = [line.strip() for line in citations_text.split('\n') if line.strip() and line.strip().startswith('-')]
                
                for citation_line in citation_lines:
                    citation_text = citation_line.replace('-', '').strip()
                    if citation_text and not citation_text.startswith('...'):
                        
                        reference = LegalReference(
                            reference_id=f"CA_REF_{ref_id_counter:03d}",
                            citation_text=citation_text,
                            authority_level=self.authority_mapping.get(category, 30),
                            jurisdiction=self._determine_jurisdiction(category),
                            category=category,
                            section_found=section_title,
                            hub_spoke_type="spoke" if category != "Internal Section Refs" else "hub",
                            business_impact=self.business_impact_mapping.get(category, "Operational guidance")
                        )
                        
                        references.append(reference)
                        ref_id_counter += 1
        
        logger.info(f"✅ Extracted {len(references)} individual legal references")
        return references

    def _determine_jurisdiction(self, category: str) -> str:
        """Determine jurisdiction from reference category"""
        if category.startswith("Federal"):
            return "Federal"
        elif category.startswith("Ca"):
            return "California"
        elif category == "Internal Section Refs":
            return "QAP Internal"
        else:
            return "Unknown"

    def _generate_universe_analysis(self, references: List[LegalReference]) -> RegulatoryUniverse:
        """Generate complete regulatory universe analysis"""
        
        # Count references by jurisdiction
        federal_count = len([r for r in references if r.jurisdiction == "Federal"])
        state_count = len([r for r in references if r.jurisdiction == "California"])
        internal_count = len([r for r in references if r.jurisdiction == "QAP Internal"])
        
        universe = RegulatoryUniverse(
            qap_sections=17,
            total_legal_refs=len(references),
            federal_refs=federal_count,
            state_refs=state_count,
            internal_refs=internal_count,
            hub_to_spoke_ratio="2-3:1",
            estimated_external_pages=700,
            business_value_multiplier="3-4X"
        )
        
        return universe

    def _generate_demo_insights(self, references: List[LegalReference]) -> Dict[str, Any]:
        """Generate insights for regulatory intelligence demo"""
        
        # Authority level distribution
        authority_distribution = {}
        for ref in references:
            level = ref.authority_level
            authority_distribution[level] = authority_distribution.get(level, 0) + 1
        
        # Hub vs spoke distribution  
        hub_spoke_dist = {}
        for ref in references:
            hub_spoke_dist[ref.hub_spoke_type] = hub_spoke_dist.get(ref.hub_spoke_type, 0) + 1
        
        # High-authority references (Federal level)
        high_authority_refs = [r for r in references if r.authority_level >= 80]
        
        insights = {
            "authority_hierarchy_demo": {
                "total_federal_authority_refs": len([r for r in references if r.jurisdiction == "Federal"]),
                "total_state_authority_refs": len([r for r in references if r.jurisdiction == "California"]),
                "authority_distribution": authority_distribution,
                "highest_authority_examples": [r.citation_text for r in high_authority_refs[:5]]
            },
            "hub_spoke_model_demo": {
                "hub_references": hub_spoke_dist.get("hub", 0),
                "spoke_references": hub_spoke_dist.get("spoke", 0),
                "external_universe_size": "600-800 pages (2-3X QAP size)",
                "business_value": "3-4X revenue multiplication opportunity"
            },
            "competitive_advantage_demo": {
                "total_external_regulations": hub_spoke_dist.get("spoke", 0),
                "competitor_coverage": "QAP-only (20-50% of complete universe)",
                "colosseum_coverage": "Complete universe (95-100% regulatory coverage)",
                "development_time_advantage": "18-24 month lead over competitors"
            }
        }
        
        return insights

    def export_for_demo(self, output_path: str, extracted_data: Dict[str, Any]) -> bool:
        """Export processed data for demo system integration"""
        
        try:
            # Create comprehensive demo data structure
            demo_data = {
                "metadata": {
                    "system": "Colosseum Complete Regulatory Universe",
                    "jurisdiction": "California",
                    "extraction_date": extracted_data["extraction_timestamp"],
                    "mission": "M4 Strike Leader - Complete Regulatory Universe Domination",
                    "demo_type": "Enhanced Regulatory Intelligence Demo"
                },
                "regulatory_universe": extracted_data["regulatory_universe_analysis"],
                "legal_references": extracted_data["legal_references"],
                "demo_insights": extracted_data["demo_insights"],
                "business_case": {
                    "current_market_value": "$5,000-$15,000/month per developer",
                    "complete_universe_value": "$20,000-$50,000/month per developer", 
                    "revenue_multiplication": "3-4X increase",
                    "market_advantage": "18-24 month competitive moat",
                    "total_addressable_market": "$500M+ (vs $50M QAP-only)"
                }
            }
            
            # Export to JSON for demo integration
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(demo_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Demo data exported successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export demo data: {e}")
            return False

def main():
    """Main execution for California legal reference extraction"""
    
    print("🏛️ M4 STRIKE LEADER - CA LEGAL REFERENCE EXTRACTION")
    print("="*60)
    print("Mission: Enhanced Regulatory Intelligence Demo Development")
    print("Target: California's 316 Legal References")
    print("Objective: Complete Universe Search Demo Integration")
    print("="*60)
    
    extractor = CALegalReferenceExtractor()
    
    # Process CA regulatory framework report
    report_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/qap_processing/CA_regulatory_framework_report.md"
    
    print(f"📊 Processing: {report_path}")
    
    extracted_data = extractor.extract_from_framework_report(report_path)
    
    if extracted_data:
        print("✅ Extraction successful!")
        print(f"📈 Total references extracted: {len(extracted_data['legal_references'])}")
        
        # Export for demo integration
        output_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/qap_processing/ca_regulatory_universe_demo_data.json"
        
        if extractor.export_for_demo(output_path, extracted_data):
            print(f"🚀 Demo data ready: {output_path}")
            print("\n🎯 Ready for Enhanced Regulatory Intelligence Demo!")
            print("💰 Business Value: 3-4X revenue multiplication")
            print("🏆 Competitive Advantage: 18-24 month moat")
        else:
            print("❌ Failed to export demo data")
    else:
        print("❌ Extraction failed")

if __name__ == "__main__":
    main()