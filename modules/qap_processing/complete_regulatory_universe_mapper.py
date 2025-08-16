#!/usr/bin/env python3
"""
Complete Regulatory Universe Mapper
Maps all external regulations referenced by QAPs for complete RAG coverage

This addresses the critical insight that QAPs are "hubs" that reference external "spokes":
- FL QAP → Rule Chapter 67-21, 67-53 (FL Administrative Code)
- CA QAP → Title 4 CCR Division 13 (CA Code of Regulations) 
- NY QAP → IRC Section 42, Section 8 CFR, State Executive Orders
- TX QAP → Title 10 Texas Administrative Code

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

import re
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from state_regulatory_framework import StateRegulatorFramework, LegalReference

@dataclass
class ExternalRegulation:
    """External regulation referenced by QAP"""
    reference_type: str  # 'state_admin_code', 'federal_cfr', 'federal_irc', 'state_statute', 'executive_order'
    jurisdiction: str    # 'FL', 'CA', 'Federal', etc.
    title_chapter: str   # 'Rule Chapter 67-21', '26 CFR Part 1', etc.
    section: str         # 'Section 1.42-5', '67-21.027', etc.
    description: str     # Human readable description
    priority: int        # 1=Critical, 2=Important, 3=Reference
    estimated_pages: int # Estimated document size
    source_url: str = "" # Where to fetch the regulation
    status: str = "pending"  # 'pending', 'fetched', 'processed', 'integrated'

@dataclass
class RegulatoryUniverse:
    """Complete regulatory universe for a state"""
    state: str
    qap_sections: Dict[str, any]  # From our existing extraction
    external_regulations: List[ExternalRegulation]
    total_estimated_pages: int
    coverage_completeness: float  # Percentage of complete regulatory coverage

class CompleteRegulatoryUniverseMapper:
    """Maps complete regulatory universe for comprehensive QAP RAG"""
    
    def __init__(self):
        self.framework = StateRegulatorFramework()
        self.external_patterns = self._define_external_regulation_patterns()
        self.regulation_databases = self._define_regulation_databases()
    
    def _define_external_regulation_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Define patterns for external regulation references by state"""
        
        return {
            'FL': {
                'state_admin_code': [
                    r'Rule\s+Chapter\s+67-\d+[^,.\n]*',
                    r'Florida\s+Administrative\s+Code[^,.\n]*',
                    r'subsection\s+67-[\d.-]+[^,.\n]*',
                    r'Rule\s+67-[\d.-]+[^,.\n]*'
                ],
                'state_statute': [
                    r'Section\s+420\.[\d]+[^,.\n]*',
                    r'Florida\s+Statutes[^,.\n]*'
                ],
                'federal_cfr': [
                    r'26\s+CFR\s+Part\s+1\s+Section\s+[\d.-]+[^,.\n]*'
                ]
            },
            'CA': {
                'state_admin_code': [
                    r'Title\s+4\s+CCR\s+Division\s+13[^,.\n]*',
                    r'California\s+Code\s+of\s+Regulations[^,.\n]*',
                    r'4\s+CCR\s+Section\s+[\d.-]+[^,.\n]*'
                ],
                'state_statute': [
                    r'Health\s+and\s+Safety\s+Code\s+Section[s]?\s+[\d.-]+[^,.\n]*',
                    r'Revenue\s+and\s+Taxation\s+Code\s+Section[s]?\s+[\d.-]+[^,.\n]*'
                ]
            },
            'TX': {
                'state_admin_code': [
                    r'Title\s+10\s+Texas\s+Administrative\s+Code[^,.\n]*',
                    r'10\s+TAC\s+Chapter\s+\d+[^,.\n]*',
                    r'Texas\s+Administrative\s+Code[^,.\n]*'
                ],
                'state_statute': [
                    r'Texas\s+Government\s+Code[^,.\n]*',
                    r'Chapter\s+2306[^,.\n]*'
                ]
            },
            'NY': {
                'state_admin_code': [
                    r'New\s+York\s+State[^,.\n]*Code[^,.\n]*',
                    r'NYCRR[^,.\n]*'
                ],
                'executive_order': [
                    r'State\s+Executive\s+Order\s+\d+[^,.\n]*',
                    r'Executive\s+Order\s+\d+[^,.\n]*'
                ],
                'municipal_code': [
                    r'NYC[^,.\n]*Code[^,.\n]*',
                    r'New\s+York\s+City[^,.\n]*'
                ]
            },
            'federal': {  # Universal federal patterns
                'federal_irc': [
                    r'IRC\s+Section\s+\d+[a-z()0-9\(\)\[\]]*',
                    r'Internal\s+Revenue\s+Code\s+Section\s+\d+[a-z()0-9\(\)\[\]]*',
                    r'Section\s+42\s+of\s+the\s+Code[^,.\n]*'
                ],
                'federal_cfr': [
                    r'26\s+CFR\s+[\d.]+[a-z()0-9\(\)\[\]]*',
                    r'Code\s+of\s+Federal\s+Regulations[^,.\n]*'
                ],
                'federal_statute': [
                    r'Section\s+8[^,.\n]*',  # Housing Choice Voucher
                    r'Fair\s+Housing\s+Act[^,.\n]*',
                    r'Americans\s+with\s+Disabilities\s+Act[^,.\n]*'
                ]
            }
        }
    
    def _define_regulation_databases(self) -> Dict[str, Dict[str, str]]:
        """Define where to fetch external regulations"""
        
        return {
            'FL': {
                'admin_code_base': 'https://www.flrules.org/gateway/ChapterHome.asp?Chapter=',
                'statutes_base': 'http://www.leg.state.fl.us/Statutes/index.cfm?App_mode=Display_Statute&URL=',
                'description': 'Florida Administrative Code and Florida Statutes'
            },
            'CA': {
                'admin_code_base': 'https://govt.westlaw.com/calregs/',
                'statutes_base': 'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml',
                'description': 'California Code of Regulations and California Statutes'
            },
            'TX': {
                'admin_code_base': 'https://texreg.sos.state.tx.us/public/readtac$ext.ViewTAC',
                'statutes_base': 'https://statutes.capitol.texas.gov/',
                'description': 'Texas Administrative Code and Texas Statutes'
            },
            'federal': {
                'cfr_base': 'https://www.ecfr.gov/current/title-26/',
                'irc_base': 'https://www.law.cornell.edu/uscode/text/26/',
                'description': 'Code of Federal Regulations and Internal Revenue Code'
            }
        }
    
    def map_complete_regulatory_universe(self, state: str) -> RegulatoryUniverse:
        """Map complete regulatory universe for a state"""
        
        print(f"🏛️ MAPPING COMPLETE REGULATORY UNIVERSE: {state}")
        print("=" * 60)
        
        # Step 1: Extract QAP sections (existing functionality)
        print("📋 Step 1: Extracting QAP sections...")
        qap_result = self.framework.extract_state_regulatory_framework(state)
        
        # Step 2: Extract external regulation references
        print("🔍 Step 2: Mapping external regulation references...")
        external_regs = self._extract_external_regulations(state, qap_result)
        
        # Step 3: Prioritize and estimate scope
        print("📊 Step 3: Prioritizing and estimating scope...")
        prioritized_regs = self._prioritize_external_regulations(external_regs)
        
        # Step 4: Calculate completeness
        total_pages = sum(reg.estimated_pages for reg in prioritized_regs)
        completeness = self._calculate_coverage_completeness(state, len(prioritized_regs))
        
        universe = RegulatoryUniverse(
            state=state,
            qap_sections=qap_result.sections,
            external_regulations=prioritized_regs,
            total_estimated_pages=total_pages,
            coverage_completeness=completeness
        )
        
        self._print_universe_summary(universe)
        return universe
    
    def _extract_external_regulations(self, state: str, qap_result) -> List[ExternalRegulation]:
        """Extract all external regulation references from QAP content"""
        
        external_regs = []
        
        # Get patterns for this state + universal federal patterns
        state_patterns = self.external_patterns.get(state, {})
        federal_patterns = self.external_patterns.get('federal', {})
        all_patterns = {**state_patterns, **federal_patterns}
        
        # Extract from all QAP content
        full_content = ""
        for section_info in qap_result.sections.values():
            full_content += section_info.content + " "
        
        # Apply patterns to find external references
        for ref_type, patterns in all_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, full_content, re.IGNORECASE)
                
                for match in matches:
                    # Create external regulation object
                    external_reg = ExternalRegulation(
                        reference_type=ref_type,
                        jurisdiction=state if not ref_type.startswith('federal') else 'Federal',
                        title_chapter=self._extract_title_chapter(match),
                        section=self._extract_section(match),
                        description=match.strip(),
                        priority=self._assign_priority(ref_type, match),
                        estimated_pages=self._estimate_pages(ref_type, match),
                        source_url=self._generate_source_url(state, ref_type, match)
                    )
                    
                    external_regs.append(external_reg)
        
        # Remove duplicates
        unique_regs = self._deduplicate_regulations(external_regs)
        return unique_regs
    
    def _extract_title_chapter(self, reference: str) -> str:
        """Extract title/chapter from reference"""
        
        # Rule Chapter 67-21 → "Rule Chapter 67-21"
        # 26 CFR Part 1 → "26 CFR Part 1"
        title_patterns = [
            r'Rule\s+Chapter\s+[\d-]+',
            r'\d+\s+CFR\s+Part\s+\d+',
            r'Title\s+\d+[^,.\n]*',
            r'Chapter\s+\d+[^,.\n]*'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, reference, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        # Return first 3 words as string, not list
        words = reference.split()[:3]
        return " ".join(words)
    
    def _extract_section(self, reference: str) -> str:
        """Extract specific section from reference"""
        
        section_patterns = [
            r'Section\s+[\d.-]+[a-z()]*',
            r'subsection\s+[\d.-]+[a-z()]*',
            r'§\s*[\d.-]+[a-z()]*'
        ]
        
        for pattern in section_patterns:
            match = re.search(pattern, reference, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        return ""
    
    def _assign_priority(self, ref_type: str, reference: str) -> int:
        """Assign priority to regulation (1=Critical, 2=Important, 3=Reference)"""
        
        critical_keywords = ['compliance', 'monitoring', 'allocation', 'scoring', 'threshold']
        important_keywords = ['application', 'selection', 'underwriting', 'fees']
        
        ref_lower = reference.lower()
        
        if any(keyword in ref_lower for keyword in critical_keywords):
            return 1  # Critical
        elif any(keyword in ref_lower for keyword in important_keywords):
            return 2  # Important
        else:
            return 3  # Reference
    
    def _estimate_pages(self, ref_type: str, reference: str) -> int:
        """Estimate pages for external regulation"""
        
        # Rough estimates based on regulation type
        estimates = {
            'state_admin_code': 50,   # State admin codes are usually substantial
            'federal_cfr': 30,        # Federal CFR sections
            'federal_irc': 20,        # IRC sections
            'state_statute': 15,      # Individual statutes
            'executive_order': 5,     # Executive orders are shorter
            'municipal_code': 25      # Municipal codes
        }
        
        return estimates.get(ref_type, 20)  # Default 20 pages
    
    def _generate_source_url(self, state: str, ref_type: str, reference: str) -> str:
        """Generate URL to fetch the external regulation"""
        
        # This would be implemented with actual URL construction logic
        # For now, return base URLs
        
        db_info = self.regulation_databases.get(state, {})
        
        if ref_type.startswith('federal'):
            federal_db = self.regulation_databases.get('federal', {})
            if 'cfr' in ref_type:
                return federal_db.get('cfr_base', '')
            elif 'irc' in ref_type:
                return federal_db.get('irc_base', '')
        
        if 'admin_code' in ref_type:
            return db_info.get('admin_code_base', '')
        elif 'statute' in ref_type:
            return db_info.get('statutes_base', '')
        
        return ""
    
    def _deduplicate_regulations(self, regulations: List[ExternalRegulation]) -> List[ExternalRegulation]:
        """Remove duplicate regulations"""
        
        seen = set()
        unique_regs = []
        
        for reg in regulations:
            # Create unique key
            key = (reg.reference_type, reg.jurisdiction, reg.title_chapter, reg.section)
            
            if key not in seen:
                seen.add(key)
                unique_regs.append(reg)
        
        return unique_regs
    
    def _prioritize_external_regulations(self, regulations: List[ExternalRegulation]) -> List[ExternalRegulation]:
        """Sort regulations by priority"""
        
        return sorted(regulations, key=lambda r: (r.priority, -r.estimated_pages))
    
    def _calculate_coverage_completeness(self, state: str, num_external_regs: int) -> float:
        """Calculate estimated coverage completeness"""
        
        # Rough estimates of complete regulatory coverage needed
        coverage_estimates = {
            'FL': 15,  # FL has many external references
            'CA': 5,   # CA includes most in QAP
            'TX': 12,  # TX has moderate external refs
            'NY': 8    # NY has some external refs
        }
        
        expected_regs = coverage_estimates.get(state, 10)
        return min(100.0, (num_external_regs / expected_regs) * 100)
    
    def _print_universe_summary(self, universe: RegulatoryUniverse):
        """Print summary of regulatory universe"""
        
        print(f"\n📊 REGULATORY UNIVERSE SUMMARY: {universe.state}")
        print("-" * 50)
        print(f"QAP Sections: {len(universe.qap_sections)}")
        print(f"External Regulations: {len(universe.external_regulations)}")
        print(f"Total Estimated Pages: {universe.total_estimated_pages:,}")
        print(f"Coverage Completeness: {universe.coverage_completeness:.1f}%")
        
        print(f"\n🎯 TOP PRIORITY EXTERNAL REGULATIONS:")
        for i, reg in enumerate(universe.external_regulations[:5]):
            print(f"  {i+1}. {reg.description} (Priority {reg.priority}, ~{reg.estimated_pages} pages)")

def main():
    """Test complete regulatory universe mapping"""
    
    mapper = CompleteRegulatoryUniverseMapper()
    
    # Test states that show different patterns
    test_states = ["CA"]  # Critical intelligence gap for mission
    
    for state in test_states:
        print(f"\n{'='*80}")
        universe = mapper.map_complete_regulatory_universe(state)
        print(f"✅ {state} regulatory universe mapped successfully!")

if __name__ == "__main__":
    main()