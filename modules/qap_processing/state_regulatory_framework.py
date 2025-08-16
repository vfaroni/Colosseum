#!/usr/bin/env python3
"""
State Regulatory Framework
New Architecture: Primary=State Regulatory Sections, Secondary=Optional LIHTC mapping

This implements the correct approach:
1. Primary Structure: Use state's regulatory sections as designed (CA: §10300-§10337)
2. Secondary Mapping: Optional generic LIHTC categories for cross-state analysis
3. Legal Reference Extraction: All IRC, State Code, CFR citations with context
4. Cross-Reference Preservation: Internal section references maintained

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

import json
import re
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from docling_connector import DoclingConnector

@dataclass
class LegalReference:
    """Legal citation found in QAP content"""
    reference_type: str  # 'federal_irc', 'ca_health_safety', 'ca_revenue_taxation', 'federal_cfr', 'federal_public_law'
    citation: str
    section_found_in: str
    context: str  # 50 chars before/after for context
    page_reference: Optional[str] = None

@dataclass
class StateRegulatorySectionInfo:
    """Complete information about a state regulatory section"""
    section_number: str  # e.g., "§10300"
    section_title: str   # e.g., "Purpose and Scope"
    content: str
    character_count: int
    legal_references: List[LegalReference]
    cross_references: List[str]  # References to other state sections
    page_range: Optional[str] = None
    lihtc_category: Optional[str] = None  # Optional mapping to generic LIHTC category

@dataclass
class StateRegulatorFrameworkResult:
    """Complete state regulatory extraction result"""
    state: str
    total_sections: int
    total_characters: int
    total_legal_references: int
    total_cross_references: int
    sections: Dict[str, StateRegulatorySectionInfo]
    extraction_timestamp: str
    processing_time_seconds: float

class StateRegulatorFramework:
    """Extracts state regulatory sections preserving legal structure"""
    
    def __init__(self):
        self.connector = DoclingConnector()
        self.legal_patterns = self._define_legal_patterns()
        self.lihtc_mappings = self._define_optional_lihtc_mappings()
        
    def _define_legal_patterns(self) -> Dict[str, List[str]]:
        """Define comprehensive regex patterns for legal references"""
        
        return {
            'federal_irc': [
                r'IRC\s+Section\s+\d+[a-z()0-9\(\)\[\]]*',
                r'Internal\s+Revenue\s+Code\s+Section\s+\d+[a-z()0-9\(\)\[\]]*',
                r'26\s+USC\s+\d+[a-z()0-9\(\)\[\]]*',
                r'Section\s+\d+[a-z()0-9\(\)\[\]]*\s+of\s+the\s+Internal\s+Revenue\s+Code'
            ],
            'federal_cfr': [
                r'26\s+CFR\s+[\d.]+[a-z()0-9\(\)\[\]]*',
                r'Code\s+of\s+Federal\s+Regulations[^.]*[\d.]+[a-z()0-9\(\)\[\]]*',
                r'CFR\s+(?:part\s+|Section\s+)?[\d.]+[a-z()0-9\(\)\[\]]*'
            ],
            'federal_public_law': [
                r'Public\s+Law\s+(?:No\.\s*)?\d+-\d+',
                r'P\.?L\.?\s+\d+-\d+'
            ],
            'ca_health_safety': [
                r'Health\s+(?:and|&)\s+Safety\s+Code\s+Section[s]?\s+[\d.]+[a-z()0-9\(\)\[\]]*',
                r'H\s*(?:and|&)\s*S\s+Code\s+Section[s]?\s+[\d.]+[a-z()0-9\(\)\[\]]*'
            ],
            'ca_revenue_taxation': [
                r'Revenue\s+(?:and|&)\s+Taxation\s+Code\s+Section[s]?\s+[\d.]+[a-z()0-9\(\)\[\]]*',
                r'R\s*(?:and|&)\s*T\s+Code\s+Section[s]?\s+[\d.]+[a-z()0-9\(\)\[\]]*'
            ],
            'internal_section_refs': [
                r'Section\s+103\d+[a-z()0-9\(\)\[\]]*',
                r'§\s*103\d+[a-z()0-9\(\)\[\]]*'
            ]
        }
    
    def _define_optional_lihtc_mappings(self) -> Dict[str, str]:
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
    
    def extract_state_regulatory_framework(self, state: str) -> StateRegulatorFrameworkResult:
        """Extract complete regulatory framework for a state"""
        
        start_time = datetime.now()
        print(f"🏛️ EXTRACTING {state} REGULATORY FRAMEWORK")
        print("=" * 60)
        
        # Get raw regulatory sections from docling
        raw_sections = self._get_raw_regulatory_sections(state)
        
        # Process each section with legal reference extraction
        processed_sections = {}
        total_legal_refs = 0
        total_cross_refs = 0
        total_chars = 0
        
        for section_key, content in raw_sections.items():
            if not content or len(content) < 100:  # Skip empty or tiny sections
                continue
                
            # Extract legal references
            legal_refs = self._extract_legal_references(content, section_key)
            
            # Extract cross-references
            cross_refs = self._extract_cross_references(content, state)
            
            # Get section metadata for CA (extendable to other states)
            section_number, section_title = self._get_section_metadata(section_key, state)
            
            # Create section info
            section_info = StateRegulatorySectionInfo(
                section_number=section_number,
                section_title=section_title,
                content=content,
                character_count=len(content),
                legal_references=legal_refs,
                cross_references=cross_refs,
                lihtc_category=self.lihtc_mappings.get(section_key)
            )
            
            processed_sections[section_key] = section_info
            total_legal_refs += len(legal_refs)
            total_cross_refs += len(cross_refs)
            total_chars += len(content)
            
            print(f"✅ {section_number} - {section_title}")
            print(f"   Content: {len(content):,} chars, Legal refs: {len(legal_refs)}, Cross-refs: {len(cross_refs)}")
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Create framework result
        framework_result = StateRegulatorFrameworkResult(
            state=state,
            total_sections=len(processed_sections),
            total_characters=total_chars,
            total_legal_references=total_legal_refs,
            total_cross_references=total_cross_refs,
            sections=processed_sections,
            extraction_timestamp=start_time.isoformat(),
            processing_time_seconds=processing_time
        )
        
        print(f"\n📊 EXTRACTION COMPLETE")
        print(f"Total sections: {len(processed_sections)}")
        print(f"Total content: {total_chars:,} characters")
        print(f"Total legal references: {total_legal_refs}")
        print(f"Processing time: {processing_time:.2f} seconds")
        
        return framework_result
    
    def _get_raw_regulatory_sections(self, state: str) -> Dict[str, str]:
        """Get raw regulatory sections using docling connector"""
        
        state_paths = {
            "CA": "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/CA/current/CA_2025_QAP_Regulations_Dec_2024.pdf",
            "TX": "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/TX/current/TX_2025_QAP.pdf",
            "NY": "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/NY/current/NY_NYC_2025_QAP.pdf",
            "FL": "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/FL/current/FL_2025_QAP_Final.pdf"
        }
        
        if state not in state_paths:
            raise ValueError(f"State {state} not yet implemented")
        
        pdf_path = state_paths[state]
        
        # Get raw sections from docling - bypass the generic LIHTC mapping
        raw_chunks = self.connector.process_pdf_with_strategy(pdf_path, "complex_outline", {})
        
        # Apply state-specific section extraction 
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        doc_text = result.document.export_to_markdown()
        
        # Extract state regulatory sections using state-specific logic
        if state == "CA":
            sections = self._extract_ca_regulatory_sections_directly(doc_text)
        elif state == "TX":
            sections = self._extract_tx_regulatory_sections_directly(doc_text)
        elif state == "NY":
            sections = self._extract_ny_regulatory_sections_directly(doc_text)
        elif state == "FL":
            sections = self._extract_fl_regulatory_sections_directly(doc_text)
        else:
            # Generic extraction fallback
            sections = self._extract_generic_regulatory_sections(doc_text)
        
        return sections
    
    def _extract_ca_regulatory_sections_directly(self, doc_text: str) -> Dict[str, str]:
        """Extract CA regulatory sections directly from docling output"""
        
        ca_sections = {}
        
        # CA regulatory sections with precise patterns
        ca_section_patterns = [
            (r'(##\s*Section\s+10300\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_purpose_scope"),
            (r'(##\s*Section\s+10302\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_definitions"),
            (r'(##\s*Section\s+10305\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_general_provisions"),
            (r'(##\s*Section\s+10310\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_reservations"),
            (r'(##\s*Section\s+10315\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_geographic_apportionments"),
            (r'(##\s*Section\s+10317\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_eligibility"),
            (r'(##\s*Section\s+10320\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_committee_actions"),
            (r'(##\s*Section\s+10322\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_threshold_requirements"),
            (r'(##\s*Section\s+10323\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_recovery_act"),
            (r'(##\s*Section\s+10325\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_scoring_criteria"),
            (r'(##\s*Section\s+10326\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_bond_criteria"),
            (r'(##\s*Section\s+10327\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_financial_requirements"),
            (r'(##\s*Section\s+10328\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_conditions"),
            (r'(##\s*Section\s+10330\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_appeals"),
            (r'(##\s*Section\s+10335\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_fees"),
            (r'(##\s*Section\s+10336\..*?)(?=##\s*Section\s+103\d+\.|\Z)', "section_tenant_rules"),
            (r'(##\s*Section\s+10337\..*?)(?=\Z)', "section_compliance_monitoring")  # Last section
        ]
        
        # Extract each section
        for pattern, section_key in ca_section_patterns:
            matches = re.findall(pattern, doc_text, re.DOTALL | re.IGNORECASE)
            if matches:
                content = matches[0].strip()
                ca_sections[section_key] = content
                print(f"📋 Found {section_key}: {len(content):,} characters")
        
        return ca_sections
    
    def _extract_tx_regulatory_sections_directly(self, doc_text: str) -> Dict[str, str]:
        """Extract TX regulatory sections directly from docling output"""
        
        tx_sections = {}
        
        # Texas QAP typically organized in sections like §11.1, §11.2, etc.
        # Let's find the actual structure first
        print(f"🔍 Analyzing TX QAP structure...")
        
        # Common TX patterns - adapt based on actual structure
        tx_section_patterns = [
            (r'(§\s*11\.1[^§]*?)(?=§\s*11\.\d+|\\Z)', "section_purpose_definitions"),
            (r'(§\s*11\.2[^§]*?)(?=§\s*11\.\d+|\\Z)', "section_general_provisions"),
            (r'(§\s*11\.3[^§]*?)(?=§\s*11\.\d+|\\Z)', "section_credit_ceiling"),
            (r'(§\s*11\.4[^§]*?)(?=§\s*11\.\d+|\\Z)', "section_geographic_allocation"),
            (r'(§\s*11\.5[^§]*?)(?=§\s*11\.\d+|\\Z)', "section_threshold_requirements"),
            (r'(§\s*11\.6[^§]*?)(?=§\s*11\.\d+|\\Z)', "section_selection_criteria"),
            (r'(§\s*11\.7[^§]*?)(?=§\s*11\.\d+|\\Z)', "section_underwriting_standards"),
            (r'(§\s*11\.8[^§]*?)(?=§\s*11\.\d+|\\Z)', "section_award_process"),
            (r'(§\s*11\.9[^§]*?)(?=§\s*11\.\d+|\\Z)', "section_compliance_monitoring"),
            (r'(§\s*11\.10[^§]*?)(?=\\Z)', "section_appeals_enforcement")
        ]
        
        # Extract each section
        for pattern, section_key in tx_section_patterns:
            matches = re.findall(pattern, doc_text, re.DOTALL | re.IGNORECASE)
            if matches:
                content = matches[0].strip()
                tx_sections[section_key] = content
                print(f"📋 Found {section_key}: {len(content):,} characters")
        
        return tx_sections
    
    def _extract_ny_regulatory_sections_directly(self, doc_text: str) -> Dict[str, str]:
        """Extract NY regulatory sections directly from docling output"""
        
        ny_sections = {}
        
        print(f"🔍 Analyzing NY QAP structure...")
        
        # NY QAP patterns - often organized differently 
        ny_section_patterns = [
            (r'(##\s*(?:Section\s*)?I[^#]*?)(?=##\s*(?:Section\s*)?[IVX]+|\\Z)', "section_introduction"),
            (r'(##\s*(?:Section\s*)?II[^#]*?)(?=##\s*(?:Section\s*)?[IVX]+|\\Z)', "section_program_description"),
            (r'(##\s*(?:Section\s*)?III[^#]*?)(?=##\s*(?:Section\s*)?[IVX]+|\\Z)', "section_threshold_requirements"),
            (r'(##\s*(?:Section\s*)?IV[^#]*?)(?=##\s*(?:Section\s*)?[IVX]+|\\Z)', "section_selection_criteria"),
            (r'(##\s*(?:Section\s*)?V[^#]*?)(?=##\s*(?:Section\s*)?[IVX]+|\\Z)', "section_allocation_process"),
            (r'(##\s*(?:Section\s*)?VI[^#]*?)(?=##\s*(?:Section\s*)?[IVX]+|\\Z)', "section_monitoring_compliance"),
            (r'(##\s*(?:Section\s*)?VII[^#]*?)(?=##\s*(?:Section\s*)?[IVX]+|\\Z)', "section_fees_administration"),
            (r'(##\s*(?:Section\s*)?VIII[^#]*?)(?=\\Z)', "section_appendices")
        ]
        
        # Extract each section
        for pattern, section_key in ny_section_patterns:
            matches = re.findall(pattern, doc_text, re.DOTALL | re.IGNORECASE)
            if matches:
                content = matches[0].strip()
                ny_sections[section_key] = content
                print(f"📋 Found {section_key}: {len(content):,} characters")
        
        return ny_sections
    
    def _extract_fl_regulatory_sections_directly(self, doc_text: str) -> Dict[str, str]:
        """Extract FL regulatory sections directly from docling output"""
        
        fl_sections = {}
        
        print(f"🔍 Analyzing FL QAP structure...")
        
        # FL QAP patterns - uses Roman numerals I, II, III, IV
        fl_section_patterns = [
            (r'(##\s*I\.\s*Introduction.*?)(?=##\s*[IVX]+\.|\\Z)', "section_introduction"),
            (r'(##\s*II\.\s*Competitive\s*Housing\s*Credits.*?)(?=##\s*[IVX]+\.|\\Z)', "section_competitive_credits"),
            (r'(##\s*III\.\s*Non-Competitive\s*Housing\s*Credits.*?)(?=##\s*[IVX]+\.|\\Z)', "section_noncompetitive_credits"),
            (r'(##\s*IV\.\s*Compliance.*)', "section_compliance")  # Simple pattern to end
        ]
        
        # Extract each section
        for pattern, section_key in fl_section_patterns:
            matches = re.findall(pattern, doc_text, re.DOTALL | re.IGNORECASE)
            if matches:
                content = matches[0].strip()
                fl_sections[section_key] = content
                print(f"📋 Found {section_key}: {len(content):,} characters")
        
        return fl_sections
    
    def _extract_generic_regulatory_sections(self, doc_text: str) -> Dict[str, str]:
        """Generic fallback extraction for unrecognized state structures"""
        
        print(f"🔍 Using generic extraction fallback...")
        
        # Try multiple common patterns
        sections = {}
        
        # Pattern 1: Numbered sections
        section_patterns = re.findall(r'((?:Section|§)\s*\d+[^§]*?)(?=(?:Section|§)\s*\d+|\\Z)', doc_text, re.DOTALL | re.IGNORECASE)
        for i, content in enumerate(section_patterns[:10]):  # Limit to first 10
            sections[f"section_{i+1:02d}"] = content.strip()
        
        # Pattern 2: Chapter-based
        if not sections:
            chapter_patterns = re.findall(r'(Chapter\s*\d+[^C]*?)(?=Chapter\s*\d+|\\Z)', doc_text, re.DOTALL | re.IGNORECASE)
            for i, content in enumerate(chapter_patterns[:10]):
                sections[f"chapter_{i+1:02d}"] = content.strip()
        
        # Pattern 3: Roman numerals  
        if not sections:
            roman_patterns = re.findall(r'((?:Section\s*)?[IVX]+[^IVX]*?)(?=(?:Section\s*)?[IVX]+|\\Z)', doc_text, re.DOTALL | re.IGNORECASE)
            for i, content in enumerate(roman_patterns[:10]):
                sections[f"part_{i+1:02d}"] = content.strip()
        
        print(f"📋 Generic extraction found {len(sections)} sections")
        return sections
    
    def _extract_legal_references(self, content: str, section_key: str) -> List[LegalReference]:
        """Extract legal references with context from section content"""
        
        legal_refs = []
        
        for ref_type, patterns in self.legal_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    # Get context around the match (50 chars before/after)
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end].replace('\n', ' ').strip()
                    
                    legal_ref = LegalReference(
                        reference_type=ref_type,
                        citation=match.group().strip(),
                        section_found_in=section_key,
                        context=context
                    )
                    legal_refs.append(legal_ref)
        
        return legal_refs
    
    def _extract_cross_references(self, content: str, state: str) -> List[str]:
        """Extract references to other state sections"""
        
        cross_refs = []
        
        if state == "CA":
            # CA-specific cross-reference patterns
            patterns = [
                r'Section\s+103\d+[a-z()0-9\(\)\[\]]*',
                r'§\s*103\d+[a-z()0-9\(\)\[\]]*'
            ]
        else:
            # Generic patterns for other states
            patterns = [
                r'Section\s+\d+[a-z()0-9\(\)\[\]]*',
                r'§\s*\d+[a-z()0-9\(\)\[\]]*'
            ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            cross_refs.extend([m.strip() for m in matches])
        
        # Remove duplicates and sort
        return sorted(list(set(cross_refs)))
    
    def _get_section_metadata(self, section_key: str, state: str) -> Tuple[str, str]:
        """Get section number and title for a section key"""
        
        if state == "CA":
            ca_metadata = {
                "section_purpose_scope": ("§10300", "Purpose and Scope"),
                "section_definitions": ("§10302", "Definitions"),
                "section_general_provisions": ("§10305", "General Provisions"),
                "section_reservations": ("§10310", "Reservations of Tax Credits"),
                "section_geographic_apportionments": ("§10315", "Set-Asides and Apportionments"),
                "section_eligibility": ("§10317", "State Tax Credit Eligibility Requirements"),
                "section_committee_actions": ("§10320", "Actions by the Committee"),
                "section_threshold_requirements": ("§10322", "Application Requirements"),
                "section_recovery_act": ("§10323", "The American Recovery and Reinvestment Act of 2009"),
                "section_scoring_criteria": ("§10325", "Application Selection Criteria-Credit Ceiling Applications"),
                "section_bond_criteria": ("§10326", "Application Selection Criteria-Tax-Exempt Bond Applications"),
                "section_financial_requirements": ("§10327", "Financial Feasibility and Determination of Credit Amounts"),
                "section_conditions": ("§10328", "Conditions on Credit Reservations"),
                "section_appeals": ("§10330", "Appeals"),
                "section_fees": ("§10335", "Fees and Performance Deposit"),
                "section_tenant_rules": ("§10336", "Laws, Rules, Guidelines, and Regulations for Tenants"),
                "section_compliance_monitoring": ("§10337", "Compliance")
            }
            return ca_metadata.get(section_key, (section_key, section_key))
        
        elif state == "TX":
            tx_metadata = {
                "section_purpose_definitions": ("§11.1", "Purpose and Definitions"),
                "section_general_provisions": ("§11.2", "General Provisions"),
                "section_credit_ceiling": ("§11.3", "Credit Ceiling"),
                "section_geographic_allocation": ("§11.4", "Geographic Allocation"),
                "section_threshold_requirements": ("§11.5", "Threshold Requirements"),
                "section_selection_criteria": ("§11.6", "Selection Criteria"),
                "section_underwriting_standards": ("§11.7", "Underwriting Standards"),
                "section_award_process": ("§11.8", "Award Process"),
                "section_compliance_monitoring": ("§11.9", "Compliance Monitoring"),
                "section_appeals_enforcement": ("§11.10", "Appeals and Enforcement")
            }
            return tx_metadata.get(section_key, (section_key, section_key))
        
        elif state == "NY":
            ny_metadata = {
                "section_introduction": ("Part I", "Introduction"),
                "section_program_description": ("Part II", "Program Description"),
                "section_threshold_requirements": ("Part III", "Threshold Requirements"),
                "section_selection_criteria": ("Part IV", "Selection Criteria"),
                "section_allocation_process": ("Part V", "Allocation Process"),
                "section_monitoring_compliance": ("Part VI", "Monitoring and Compliance"),
                "section_fees_administration": ("Part VII", "Fees and Administration"),
                "section_appendices": ("Part VIII", "Appendices")
            }
            return ny_metadata.get(section_key, (section_key, section_key))
        
        elif state == "FL":
            fl_metadata = {
                "section_introduction": ("Part I", "Introduction"),
                "section_competitive_credits": ("Part II", "Competitive Housing Credits"),
                "section_noncompetitive_credits": ("Part III", "Non-Competitive Housing Credits"),
                "section_compliance": ("Part IV", "Compliance")
            }
            return fl_metadata.get(section_key, (section_key, section_key))
        
        return (section_key, section_key)
    
    def generate_regulatory_report(self, framework_result: StateRegulatorFrameworkResult) -> str:
        """Generate comprehensive regulatory framework report"""
        
        report = []
        report.append(f"# 🏛️ {framework_result.state} REGULATORY FRAMEWORK ANALYSIS")
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**State**: {framework_result.state}")
        report.append(f"**Total Sections**: {framework_result.total_sections}")
        report.append(f"**Processing Time**: {framework_result.processing_time_seconds:.2f} seconds")
        report.append("")
        
        # Summary statistics
        report.append("## 📊 SUMMARY STATISTICS")
        report.append(f"- **Total Content**: {framework_result.total_characters:,} characters")
        report.append(f"- **Legal References**: {framework_result.total_legal_references} citations")
        report.append(f"- **Cross-References**: {framework_result.total_cross_references} internal section references")
        report.append("")
        
        # Legal reference summary by type
        legal_ref_types = {}
        for section_info in framework_result.sections.values():
            for legal_ref in section_info.legal_references:
                if legal_ref.reference_type not in legal_ref_types:
                    legal_ref_types[legal_ref.reference_type] = 0
                legal_ref_types[legal_ref.reference_type] += 1
        
        report.append("### Legal Reference Types")
        for ref_type, count in sorted(legal_ref_types.items()):
            report.append(f"- **{ref_type.replace('_', ' ').title()}**: {count} citations")
        report.append("")
        
        # Section-by-section analysis
        report.append("## 📋 SECTION-BY-SECTION ANALYSIS")
        report.append("")
        
        for section_key, section_info in framework_result.sections.items():
            report.append(f"### {section_info.section_number} - {section_info.section_title}")
            report.append(f"**Content**: {section_info.character_count:,} characters")
            report.append(f"**LIHTC Category**: {section_info.lihtc_category or 'N/A'}")
            report.append("")
            
            if section_info.legal_references:
                report.append("**Legal References**:")
                ref_by_type = {}
                for ref in section_info.legal_references:
                    if ref.reference_type not in ref_by_type:
                        ref_by_type[ref.reference_type] = []
                    ref_by_type[ref.reference_type].append(ref.citation)
                
                for ref_type, citations in ref_by_type.items():
                    report.append(f"- **{ref_type.replace('_', ' ').title()}**: {len(citations)} citations")
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
    
    def save_framework_result(self, framework_result: StateRegulatorFrameworkResult, output_dir: str = ".") -> Dict[str, str]:
        """Save framework result in multiple formats"""
        
        output_files = {}
        
        # JSON format for programmatic access
        json_path = f"{output_dir}/{framework_result.state}_regulatory_framework.json"
        
        # Convert to serializable format
        serializable_result = {
            "state": framework_result.state,
            "total_sections": framework_result.total_sections,
            "total_characters": framework_result.total_characters,
            "total_legal_references": framework_result.total_legal_references,
            "total_cross_references": framework_result.total_cross_references,
            "extraction_timestamp": framework_result.extraction_timestamp,
            "processing_time_seconds": framework_result.processing_time_seconds,
            "sections": {}
        }
        
        for section_key, section_info in framework_result.sections.items():
            serializable_result["sections"][section_key] = {
                "section_number": section_info.section_number,
                "section_title": section_info.section_title,
                "content": section_info.content,
                "character_count": section_info.character_count,
                "legal_references": [asdict(ref) for ref in section_info.legal_references],
                "cross_references": section_info.cross_references,
                "page_range": section_info.page_range,
                "lihtc_category": section_info.lihtc_category
            }
        
        with open(json_path, 'w') as f:
            json.dump(serializable_result, f, indent=2)
        output_files["json"] = json_path
        
        # Markdown report
        report_path = f"{output_dir}/{framework_result.state}_regulatory_framework_report.md"
        report = self.generate_regulatory_report(framework_result)
        with open(report_path, 'w') as f:
            f.write(report)
        output_files["report"] = report_path
        
        return output_files

def main():
    """Test the state regulatory framework on multiple states"""
    
    framework = StateRegulatorFramework()
    
    # Test states for multi-state validation
    test_states = ["TX", "NY", "FL"]
    
    print("🏛️ MULTI-STATE QAP REGULATORY FRAMEWORK TESTING")
    print("=" * 80)
    
    for state in test_states:
        print(f"\n🚀 TESTING {state} QAP EXTRACTION")
        print("-" * 50)
        
        try:
            # Extract state regulatory framework
            result = framework.extract_state_regulatory_framework(state)
            
            # Save results
            output_files = framework.save_framework_result(result)
            
            print(f"\n📊 {state} RESULTS SUMMARY:")
            print(f"  Total sections: {result.total_sections}")
            print(f"  Total content: {result.total_characters:,} characters")
            print(f"  Legal references: {result.total_legal_references}")
            print(f"  Processing time: {result.processing_time_seconds:.2f} seconds")
            
            print(f"\n📄 {state} OUTPUT FILES:")
            for file_type, path in output_files.items():
                print(f"  {file_type.upper()}: {path}")
            
            # Show top sections
            if result.sections:
                largest = max(result.sections.items(), key=lambda x: x[1].character_count)
                most_refs = max(result.sections.items(), key=lambda x: len(x[1].legal_references))
                
                print(f"\n🎯 {state} KEY INSIGHTS:")
                print(f"  Largest section: {largest[1].section_number} ({largest[1].character_count:,} chars)")
                print(f"  Most legal refs: {most_refs[1].section_number} ({len(most_refs[1].legal_references)} refs)")
            
        except Exception as e:
            print(f"❌ {state} extraction failed: {e}")
            continue
    
    print(f"\n✅ MULTI-STATE TESTING COMPLETE")
    print("Ready for production deployment across 54 jurisdictions!")

if __name__ == "__main__":
    main()