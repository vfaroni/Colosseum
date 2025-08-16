#!/usr/bin/env python3
"""
Comprehensive QAP Structure Analyzer
Identifies the 4 major organizational structures states use for QAPs
and creates framework for comprehensive LIHTC intelligence system
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import pandas as pd
from dataclasses import dataclass, asdict

# Use docling for better PDF parsing
try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

@dataclass
class SectionStructure:
    """Structure for a QAP section"""
    level: int
    number: str
    title: str
    content: str
    parent_section: str = ""
    subsections: List[str] = None
    cross_references: List[str] = None
    
    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []
        if self.cross_references is None:
            self.cross_references = []

@dataclass
class QAPStructure:
    """Complete QAP organizational structure"""
    state_code: str
    document_title: str
    organizational_type: str
    sections: List[SectionStructure]
    definitions: List[Dict[str, Any]]
    cross_references: List[Dict[str, Any]]
    regulatory_requirements: List[Dict[str, Any]]
    scoring_criteria: List[Dict[str, Any]]
    federal_references: List[str]
    state_law_references: List[str]

class ComprehensiveQAPAnalyzer:
    """Comprehensive QAP structure and content analyzer"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.qap_dir = self.base_dir / "data_sets" / "QAP"
        
        # Initialize structure patterns
        self.structure_patterns = self.init_structure_patterns()
        self.reference_patterns = self.init_reference_patterns()
        
        # Results storage
        self.analyzed_structures = {}
        
        print("🏛️ Comprehensive QAP Structure Analyzer Initialized")
        print(f"📁 QAP Directory: {self.qap_dir}")
    
    def init_structure_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for identifying organizational structures"""
        return {
            # Type 1: Traditional Legal/Regulatory Structure (California, Texas style)
            'legal_regulatory': [
                r'Section\s+\d+\.?\d*',
                r'§\s*\d+\.?\d*',
                r'subsection\s+\([a-z]\)',
                r'paragraph\s+\(\d+\)',
                r'subdivision\s+\([a-zA-Z]\)',
                r'Chapter\s+\d+',
                r'Article\s+[IVX]+',
                r'Part\s+[IVX]+',
            ],
            
            # Type 2: Administrative/Program Structure (HUD/HFA style)
            'administrative_program': [
                r'[IVX]+\.\s+[A-Z]',  # Roman numerals
                r'[A-Z]\.\s+[A-Z]',   # Letter sections
                r'Threshold\s+Requirements?',
                r'Scoring\s+Criteria',
                r'Selection\s+Process',
                r'Program\s+Requirements?',
                r'Allocation\s+Process',
            ],
            
            # Type 3: Outline/Numbered Structure (Simple numbered outline)
            'outline_numbered': [
                r'^\d+\.\s+',
                r'^\d+\.\d+\s+',
                r'^\d+\.\d+\.\d+\s+',
                r'[a-z]\)\s+',
                r'[i-v]+\)\s+',
                r'•\s+',
                r'-\s+',
            ],
            
            # Type 4: Hybrid/Complex Structure (Mixed approaches)
            'hybrid_complex': [
                r'PART\s+[IVX]+',
                r'SECTION\s+\d+',
                r'Tab\s+\d+',
                r'Exhibit\s+[A-Z]',
                r'Appendix\s+[A-Z]',
                r'Schedule\s+[A-Z]',
                r'Attachment\s+[A-Z]',
            ]
        }
    
    def init_reference_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for identifying cross-references"""
        return {
            'internal_qap': [
                r'Section\s+\d+[\.\d]*',
                r'§\s*\d+[\.\d]*',
                r'subsection\s+\([a-zA-Z0-9]+\)',
                r'paragraph\s+\([a-zA-Z0-9]+\)',
                r'Tab\s+\d+',
                r'Exhibit\s+[A-Z]',
                r'Appendix\s+[A-Z]',
                r'above|below|herein|hereof',
            ],
            
            'federal_irc_42': [
                r'IRC\s+Section\s+42',
                r'Section\s+42\([a-z]\)\(\d+\)',
                r'26\s+U\.?S\.?C\.?\s+§?\s*42',
                r'Internal\s+Revenue\s+Code\s+Section\s+42',
                r'26\s+CFR\s+§?\s*1\.42',
                r'Treasury\s+Regulation\s+1\.42',
                r'Rev\.\s*Proc\.\s*\d+-\d+',
                r'Revenue\s+Procedure\s+\d+-\d+',
            ],
            
            'state_law': [
                r'Health\s+and\s+Safety\s+Code\s+Section\s+\d+',
                r'H\s*&\s*S\s+Code\s+§?\s*\d+',
                r'Government\s+Code\s+Section\s+\d+',
                r'Revenue\s+and\s+Taxation\s+Code\s+Section\s+\d+',
                r'Civil\s+Code\s+Section\s+\d+',
                r'[A-Z][a-z]+\s+Code\s+§?\s*\d+',
                r'[A-Z][a-z]+\s+Statutes?\s+§?\s*\d+',
            ],
            
            'federal_regulations': [
                r'24\s+CFR\s+§?\s*\d+',
                r'Code\s+of\s+Federal\s+Regulations',
                r'CFR\s+§?\s*\d+\.\d+',
                r'Federal\s+Register',
                r'Fed\.\s*Reg\.',
            ]
        }
    
    def extract_pdf_content(self, pdf_path: Path) -> str:
        """Extract content from PDF using docling if available"""
        try:
            if DOCLING_AVAILABLE:
                converter = DocumentConverter()
                result = converter.convert(str(pdf_path))
                return result.document.export_to_markdown()
            else:
                # Fallback - return empty for now
                print(f"⚠️ Docling not available, skipping {pdf_path.name}")
                return ""
        except Exception as e:
            print(f"❌ Error extracting {pdf_path.name}: {e}")
            return ""
    
    def identify_organizational_structure(self, content: str) -> str:
        """Identify which of the 4 organizational structures the QAP uses"""
        structure_scores = {
            'legal_regulatory': 0,
            'administrative_program': 0,
            'outline_numbered': 0,
            'hybrid_complex': 0
        }
        
        # Count pattern matches for each structure type
        for structure_type, patterns in self.structure_patterns.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
                structure_scores[structure_type] += matches
        
        # Determine primary structure
        if not any(structure_scores.values()):
            return 'unidentified'
        
        primary_structure = max(structure_scores, key=structure_scores.get)
        
        # Check for hybrid if multiple types have high scores
        sorted_scores = sorted(structure_scores.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_scores) >= 2 and sorted_scores[1][1] >= sorted_scores[0][1] * 0.6:
            return 'hybrid_complex'
        
        return primary_structure
    
    def extract_sections(self, content: str, structure_type: str) -> List[SectionStructure]:
        """Extract hierarchical sections based on structure type"""
        sections = []
        
        if structure_type == 'legal_regulatory':
            # Extract sections using legal patterns
            section_pattern = r'(Section\s+(\d+\.?\d*)\.?\s*([^\n]+))\n(.*?)(?=Section\s+\d+|$)'
            matches = re.finditer(section_pattern, content, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                section = SectionStructure(
                    level=1,
                    number=match.group(2),
                    title=match.group(3).strip(),
                    content=match.group(4).strip()[:2000]  # Limit content length
                )
                sections.append(section)
        
        elif structure_type == 'administrative_program':
            # Extract using administrative patterns
            admin_pattern = r'([IVX]+)\.\s+([A-Z][^\n]+)\n(.*?)(?=[IVX]+\.|$)'
            matches = re.finditer(admin_pattern, content, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                section = SectionStructure(
                    level=1,
                    number=match.group(1),
                    title=match.group(2).strip(),
                    content=match.group(3).strip()[:2000]
                )
                sections.append(section)
        
        elif structure_type == 'outline_numbered':
            # Extract using numbered outline patterns
            outline_pattern = r'(\d+)\.(\d+)?\s+([^\n]+)\n(.*?)(?=\d+\.|$)'
            matches = re.finditer(outline_pattern, content, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                section_num = match.group(1)
                subsection_num = match.group(2) if match.group(2) else ""
                full_number = f"{section_num}.{subsection_num}" if subsection_num else section_num
                
                section = SectionStructure(
                    level=2 if subsection_num else 1,
                    number=full_number,
                    title=match.group(3).strip(),
                    content=match.group(4).strip()[:2000]
                )
                sections.append(section)
        
        elif structure_type == 'hybrid_complex':
            # Try multiple patterns for complex structures
            patterns = [
                r'(PART\s+[IVX]+)\s+([^\n]+)\n(.*?)(?=PART\s+[IVX]+|$)',
                r'(SECTION\s+\d+)\s+([^\n]+)\n(.*?)(?=SECTION\s+\d+|$)',
                r'(Tab\s+\d+)\s+([^\n]+)\n(.*?)(?=Tab\s+\d+|$)',
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    section = SectionStructure(
                        level=1,
                        number=match.group(1),
                        title=match.group(2).strip(),
                        content=match.group(3).strip()[:2000]
                    )
                    sections.append(section)
        
        return sections
    
    def extract_cross_references(self, content: str) -> List[Dict[str, Any]]:
        """Extract cross-references to internal, federal, and state sources"""
        references = []
        
        for ref_type, patterns in self.reference_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    references.append({
                        'type': ref_type,
                        'text': match.group(),
                        'position': match.start(),
                        'context': content[max(0, match.start()-50):match.end()+50]
                    })
        
        return references
    
    def extract_definitions(self, content: str) -> List[Dict[str, Any]]:
        """Extract definitions using enhanced patterns"""
        definitions = []
        
        # Pattern for colon definitions
        colon_pattern = r'([A-Z][^:\n]{2,50}):\s*([^.\n]+\.)'
        matches = re.finditer(colon_pattern, content)
        
        for match in matches:
            definitions.append({
                'term': match.group(1).strip(),
                'definition': match.group(2).strip(),
                'type': 'colon_definition',
                'position': match.start()
            })
        
        # Pattern for "means" definitions
        means_pattern = r'([A-Z][^.\n]{2,50})\s+means\s+([^.\n]+\.)'
        matches = re.finditer(means_pattern, content, re.IGNORECASE)
        
        for match in matches:
            definitions.append({
                'term': match.group(1).strip(),
                'definition': match.group(2).strip(),
                'type': 'means_definition',
                'position': match.start()
            })
        
        return definitions
    
    def extract_regulatory_requirements(self, content: str) -> List[Dict[str, Any]]:
        """Extract regulatory requirements and thresholds"""
        requirements = []
        
        # Threshold requirements
        threshold_pattern = r'(threshold\s+requirement[s]?[:\.]?\s*)([^.\n]+\.)'
        matches = re.finditer(threshold_pattern, content, re.IGNORECASE)
        
        for match in matches:
            requirements.append({
                'type': 'threshold_requirement',
                'description': match.group(2).strip(),
                'position': match.start()
            })
        
        # Eligibility requirements
        eligibility_pattern = r'(eligibility\s+requirement[s]?[:\.]?\s*)([^.\n]+\.)'
        matches = re.finditer(eligibility_pattern, content, re.IGNORECASE)
        
        for match in matches:
            requirements.append({
                'type': 'eligibility_requirement',
                'description': match.group(2).strip(),
                'position': match.start()
            })
        
        return requirements
    
    def extract_scoring_criteria(self, content: str) -> List[Dict[str, Any]]:
        """Extract scoring criteria and point allocations"""
        criteria = []
        
        # Point scoring patterns
        point_patterns = [
            r'(\d+)\s+point[s]?\s+for\s+([^.\n]+\.)',
            r'([^.\n]+)\s+\((\d+)\s+point[s]?\)',
            r'Maximum\s+(\d+)\s+point[s]?\s+([^.\n]+\.)',
        ]
        
        for pattern in point_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    criteria.append({
                        'points': match.group(1) if match.group(1).isdigit() else match.group(2),
                        'description': match.group(2) if match.group(1).isdigit() else match.group(1),
                        'position': match.start()
                    })
        
        return criteria
    
    def analyze_state_qap(self, state_code: str) -> QAPStructure:
        """Analyze a single state's QAP structure"""
        state_dir = self.qap_dir / state_code / "current"
        
        if not state_dir.exists():
            print(f"⚠️ No current directory for {state_code}")
            return None
        
        # Find the main QAP PDF
        qap_files = list(state_dir.glob("*.pdf"))
        if not qap_files:
            print(f"⚠️ No PDF files found for {state_code}")
            return None
        
        # Use the first PDF file (could be enhanced to pick the best one)
        qap_file = qap_files[0]
        print(f"📄 Analyzing {state_code}: {qap_file.name}")
        
        # Extract content
        content = self.extract_pdf_content(qap_file)
        if not content:
            print(f"⚠️ Could not extract content from {qap_file.name}")
            return None
        
        # Analyze structure
        structure_type = self.identify_organizational_structure(content)
        sections = self.extract_sections(content, structure_type)
        definitions = self.extract_definitions(content)
        cross_references = self.extract_cross_references(content)
        requirements = self.extract_regulatory_requirements(content)
        scoring = self.extract_scoring_criteria(content)
        
        # Extract federal and state references
        federal_refs = [ref['text'] for ref in cross_references if ref['type'] in ['federal_irc_42', 'federal_regulations']]
        state_refs = [ref['text'] for ref in cross_references if ref['type'] == 'state_law']
        
        structure = QAPStructure(
            state_code=state_code,
            document_title=qap_file.name,
            organizational_type=structure_type,
            sections=sections,
            definitions=definitions,
            cross_references=cross_references,
            regulatory_requirements=requirements,
            scoring_criteria=scoring,
            federal_references=federal_refs,
            state_law_references=state_refs
        )
        
        return structure
    
    def analyze_sample_states(self, states: List[str] = None) -> Dict[str, QAPStructure]:
        """Analyze a sample of states to identify organizational patterns"""
        if states is None:
            # Default sample representing different regions and sizes
            states = ['CA', 'TX', 'NY', 'FL', 'DE', 'AL', 'NE', 'MT']
        
        results = {}
        
        for state_code in states:
            print(f"\n🏛️ Analyzing {state_code}...")
            try:
                structure = self.analyze_state_qap(state_code)
                if structure:
                    results[state_code] = structure
                    print(f"✅ {state_code}: {structure.organizational_type} structure, {len(structure.sections)} sections")
            except Exception as e:
                print(f"❌ Error analyzing {state_code}: {e}")
        
        return results
    
    def generate_structure_report(self, results: Dict[str, QAPStructure]) -> str:
        """Generate comprehensive report on QAP organizational structures"""
        
        # Count structure types
        structure_counts = {}
        for structure in results.values():
            struct_type = structure.organizational_type
            structure_counts[struct_type] = structure_counts.get(struct_type, 0) + 1
        
        report = "# QAP ORGANIZATIONAL STRUCTURE ANALYSIS REPORT\n\n"
        report += f"**Analysis Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"**States Analyzed**: {len(results)}\n\n"
        
        report += "## ORGANIZATIONAL STRUCTURE DISTRIBUTION\n\n"
        for struct_type, count in sorted(structure_counts.items()):
            percentage = (count / len(results)) * 100
            report += f"- **{struct_type.replace('_', ' ').title()}**: {count} states ({percentage:.1f}%)\n"
        
        report += "\n## DETAILED STATE ANALYSIS\n\n"
        
        for state_code, structure in sorted(results.items()):
            report += f"### {state_code} - {structure.organizational_type.replace('_', ' ').title()}\n"
            report += f"- **Document**: {structure.document_title}\n"
            report += f"- **Sections**: {len(structure.sections)}\n"
            report += f"- **Definitions**: {len(structure.definitions)}\n"
            report += f"- **Cross-References**: {len(structure.cross_references)}\n"
            report += f"- **Requirements**: {len(structure.regulatory_requirements)}\n"
            report += f"- **Scoring Criteria**: {len(structure.scoring_criteria)}\n"
            report += f"- **Federal References**: {len(structure.federal_references)}\n"
            report += f"- **State Law References**: {len(structure.state_law_references)}\n\n"
            
            # Show top sections
            if structure.sections:
                report += f"**Top Sections**:\n"
                for i, section in enumerate(structure.sections[:3]):
                    report += f"  {i+1}. {section.number} - {section.title[:100]}...\n"
                report += "\n"
        
        report += "## RECOMMENDATIONS FOR COMPREHENSIVE SYSTEM\n\n"
        report += "1. **Structure Preservation**: Implement parsers for each of the 4 organizational types\n"
        report += "2. **Cross-Reference Resolution**: Build linkage system for internal/federal/state references\n"
        report += "3. **Content Enhancement**: Extract definitions, requirements, and scoring systematically\n"
        report += "4. **Fine-Tuned LLM**: Train specialized model on structured QAP content\n"
        
        return report
    
    def save_results(self, results: Dict[str, QAPStructure], output_dir: Path = None):
        """Save analysis results to JSON and report files"""
        if output_dir is None:
            output_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/qap_processing")
        
        # Save detailed JSON results
        json_results = {}
        for state_code, structure in results.items():
            json_results[state_code] = {
                'state_code': structure.state_code,
                'document_title': structure.document_title,
                'organizational_type': structure.organizational_type,
                'sections': [asdict(section) for section in structure.sections],
                'definitions': structure.definitions,
                'cross_references': structure.cross_references,
                'regulatory_requirements': structure.regulatory_requirements,
                'scoring_criteria': structure.scoring_criteria,
                'federal_references': structure.federal_references,
                'state_law_references': structure.state_law_references
            }
        
        json_file = output_dir / "qap_structure_analysis_results.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        # Save report
        report = self.generate_structure_report(results)
        report_file = output_dir / "qap_structure_analysis_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Results saved:")
        print(f"   📄 JSON: {json_file}")
        print(f"   📊 Report: {report_file}")

def main():
    """Run comprehensive QAP structure analysis"""
    
    print("🏛️ COMPREHENSIVE QAP STRUCTURE ANALYSIS")
    print("=" * 60)
    print("🎯 Identifying 4 major organizational structures states use")
    print("🔍 Preparing for comprehensive LIHTC intelligence system")
    print("")
    
    try:
        # Initialize analyzer
        analyzer = ComprehensiveQAPAnalyzer()
        
        # Analyze sample states
        print("📊 Analyzing representative states...")
        results = analyzer.analyze_sample_states()
        
        if results:
            print(f"\n✅ Successfully analyzed {len(results)} states")
            
            # Generate and save results
            analyzer.save_results(results)
            
            # Print summary
            structure_counts = {}
            for structure in results.values():
                struct_type = structure.organizational_type
                structure_counts[struct_type] = structure_counts.get(struct_type, 0) + 1
            
            print("\n📈 STRUCTURE DISTRIBUTION:")
            for struct_type, count in sorted(structure_counts.items()):
                print(f"   {struct_type.replace('_', ' ').title()}: {count} states")
            
            print("\n🎯 NEXT STEPS:")
            print("   1. Build structure-preserving parsers for each type")
            print("   2. Create cross-reference resolution system")
            print("   3. Design fine-tuned LLM architecture")
            print("   4. Develop comprehensive LIHTC intelligence system")
            
        else:
            print("❌ No states successfully analyzed")
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()