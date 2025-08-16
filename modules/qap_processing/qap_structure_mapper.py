#!/usr/bin/env python3
"""
QAP Structure Mapper - M4 Strike Leader Phase 2
Maps complete California QAP outline structure for hierarchical parsing

Mission: Map complete QAP outline (§10300-§10337) with nested relationships
Target: Build foundation for correct section identification and complete extraction
"""

import pdfplumber
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

@dataclass
class QAPSection:
    """Represents a QAP section with hierarchical structure"""
    section_id: str
    full_citation: str
    title: str
    level: int
    parent_id: Optional[str]
    children: List[str]
    page_start: Optional[int]
    page_end: Optional[int]
    content: str
    subsections: Dict[str, Any]

class QAPStructureMapper:
    """Maps complete California QAP structure with hierarchical relationships"""
    
    def __init__(self):
        self.qap_pdf_paths = self._find_qap_pdfs()
        self.section_patterns = self._build_section_patterns()
        self.qap_structure = {}
        self.section_hierarchy = {}
        
    def _find_qap_pdfs(self) -> List[Path]:
        """Find all QAP PDF sections"""
        possible_locations = [
            Path(__file__).parent / "test_split",
            Path(__file__).parent.parent / "data_sets" / "QAPs",
            Path(__file__).parent
        ]
        
        pdf_files = []
        for location in possible_locations:
            if location.exists():
                pdf_files.extend(location.glob("*QAP*.pdf"))
        
        print(f"📚 Found {len(pdf_files)} QAP PDF files")
        for pdf in pdf_files:
            print(f"  - {pdf.name}")
        
        return sorted(pdf_files)
    
    def _build_section_patterns(self) -> Dict[str, re.Pattern]:
        """Build enhanced regex patterns for QAP section identification"""
        patterns = {
            # Main sections (§10300-§10337)
            'main_section': re.compile(r'§\s*(\d{5})\.\s*([^.]+?)\.', re.MULTILINE),
            
            # Subsections with letters (§10325(f))
            'letter_subsection': re.compile(r'§\s*(\d{5})\(([a-z])\)\s*([^.]+?)\.?', re.MULTILINE),
            
            # Numbered subsections (§10325(f)(7))
            'numbered_subsection': re.compile(r'§\s*(\d{5})\(([a-z])\)\((\d+)\)\s*([^.]+?)\.?', re.MULTILINE),
            
            # Letter-number details (§10325(f)(7)(A))
            'detail_subsection': re.compile(r'§\s*(\d{5})\(([a-z])\)\((\d+)\)\(([A-Z])\)\s*([^.]+?)\.?', re.MULTILINE),
            
            # Roman numeral details (§10325(f)(7)(M)(iv))
            'roman_subsection': re.compile(r'§\s*(\d{5})\(([a-z])\)\((\d+)\)\(([A-Z])\)\(([ivx]+)\)\s*([^.]+?)\.?', re.MULTILINE),
            
            # Special patterns for construction standards
            'construction_standards': re.compile(r'(?i)(minimum\s+construction\s+standards?)', re.MULTILINE),
            'basic_threshold': re.compile(r'(?i)(basic\s+threshold\s+requirements?)', re.MULTILINE),
            
            # Scoring section patterns
            'scoring_section': re.compile(r'(?i)(scoring|tie\s+breakers?)', re.MULTILINE),
            
            # Application requirements patterns  
            'application_req': re.compile(r'(?i)(application\s+requirements?)', re.MULTILINE)
        }
        
        return patterns
    
    def extract_pdf_structure(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract hierarchical structure from a QAP PDF"""
        print(f"🔍 Analyzing structure in: {pdf_path.name}")
        
        structure = {
            "pdf_file": pdf_path.name,
            "sections_found": [],
            "hierarchical_map": {},
            "page_mapping": {},
            "content_extraction": {}
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    # Find main sections (§10300-§10337)
                    main_matches = self.section_patterns['main_section'].findall(text)
                    for section_num, title in main_matches:
                        section_info = {
                            "section_id": section_num,
                            "full_citation": f"§{section_num}",
                            "title": title.strip(),
                            "page": page_num,
                            "level": 1,
                            "type": "main_section"
                        }
                        structure["sections_found"].append(section_info)
                        
                        # Special handling for complex sections
                        if section_num == "10325":
                            self._analyze_complex_section_10325(text, page_num, structure)
                    
                    # Find subsections and nested content
                    self._extract_subsection_structure(text, page_num, structure)
                    
                    # Look for specific content patterns
                    self._identify_content_patterns(text, page_num, structure)
                    
                    # Progress indicator for large files
                    if page_num % 20 == 0:
                        print(f"  📄 Processed {page_num}/{total_pages} pages...")
                
                print(f"  ✅ Completed {total_pages} pages")
                print(f"  📊 Found {len(structure['sections_found'])} sections")
                
        except Exception as e:
            structure["error"] = str(e)
            print(f"  ❌ Error processing {pdf_path.name}: {e}")
        
        return structure
    
    def _analyze_complex_section_10325(self, text: str, page_num: int, structure: Dict[str, Any]):
        """Special analysis for complex section 10325 with nested structure"""
        
        # Look for major subsections within 10325
        major_subsections = [
            ("scoring", r'(?i)\(c\)\s*scoring'),
            ("basic_threshold", r'(?i)\(f\)\s*basic\s+threshold\s+requirements'),
            ("additional_threshold", r'(?i)\(g\)\s*additional\s+threshold'),
            ("tie_breakers", r'(?i)\(9\)\s*tie\s+breakers')
        ]
        
        for subsection_name, pattern in major_subsections:
            matches = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if matches:
                section_info = {
                    "section_id": f"10325_{subsection_name}",
                    "parent_section": "10325",
                    "full_citation": f"§10325({subsection_name})",
                    "title": subsection_name.replace("_", " ").title(),
                    "page": page_num,
                    "level": 2,
                    "type": "complex_subsection"
                }
                structure["sections_found"].append(section_info)
        
        # Special focus on construction standards §10325(f)(7)
        construction_pattern = r'(?i)\(f\)\s*.*?\(7\)\s*minimum\s+construction\s+standards'
        construction_match = re.search(construction_pattern, text, re.MULTILINE | re.IGNORECASE)
        if construction_match:
            section_info = {
                "section_id": "10325_f_7",
                "parent_section": "10325_f",
                "full_citation": "§10325(f)(7) Minimum Construction Standards",
                "title": "Minimum Construction Standards",
                "page": page_num,
                "level": 3,
                "type": "construction_standards",
                "critical": True  # Mark as critical for mission success
            }
            structure["sections_found"].append(section_info)
            print(f"  🎯 CRITICAL: Found construction standards on page {page_num}")
    
    def _extract_subsection_structure(self, text: str, page_num: int, structure: Dict[str, Any]):
        """Extract hierarchical subsection structure"""
        
        # Letter subsections (a), (b), (c), etc.
        letter_matches = self.section_patterns['letter_subsection'].findall(text)
        for section_num, letter, title in letter_matches:
            section_info = {
                "section_id": f"{section_num}_{letter}",
                "parent_section": section_num,
                "full_citation": f"§{section_num}({letter})",
                "title": title.strip(),
                "page": page_num,
                "level": 2,
                "type": "letter_subsection"
            }
            structure["sections_found"].append(section_info)
        
        # Numbered subsections (1), (2), (3), etc.
        numbered_matches = self.section_patterns['numbered_subsection'].findall(text)
        for section_num, letter, number, title in numbered_matches:
            section_info = {
                "section_id": f"{section_num}_{letter}_{number}",
                "parent_section": f"{section_num}_{letter}",
                "full_citation": f"§{section_num}({letter})({number})",
                "title": title.strip(),
                "page": page_num,
                "level": 3,
                "type": "numbered_subsection"
            }
            structure["sections_found"].append(section_info)
    
    def _identify_content_patterns(self, text: str, page_num: int, structure: Dict[str, Any]):
        """Identify specific content patterns for better classification"""
        
        patterns_to_check = {
            "construction_standards": self.section_patterns['construction_standards'],
            "basic_threshold": self.section_patterns['basic_threshold'],
            "scoring_section": self.section_patterns['scoring_section'],
            "application_req": self.section_patterns['application_req']
        }
        
        for pattern_name, pattern in patterns_to_check.items():
            matches = pattern.findall(text)
            if matches:
                if pattern_name not in structure["content_extraction"]:
                    structure["content_extraction"][pattern_name] = []
                
                structure["content_extraction"][pattern_name].append({
                    "page": page_num,
                    "matches": matches,
                    "context": text[:200] + "..." if len(text) > 200 else text
                })
    
    def build_hierarchical_map(self, extracted_structures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build complete hierarchical map from all extracted structures"""
        print("🏗️ Building hierarchical QAP map...")
        
        hierarchical_map = {
            "qap_outline": {},
            "section_relationships": {},
            "critical_sections": {},
            "page_mapping": {},
            "content_classification": {}
        }
        
        all_sections = []
        for structure in extracted_structures:
            all_sections.extend(structure.get("sections_found", []))
        
        # Build main section outline (§10300-§10337)
        main_sections = [s for s in all_sections if s.get("type") == "main_section"]
        for section in sorted(main_sections, key=lambda x: x["section_id"]):
            section_id = section["section_id"]
            hierarchical_map["qap_outline"][section_id] = {
                "full_citation": section["full_citation"],
                "title": section["title"],
                "page": section["page"],
                "subsections": {}
            }
        
        # Build subsection relationships
        for section in all_sections:
            if section.get("parent_section"):
                parent_id = section["parent_section"]
                section_id = section["section_id"]
                
                if parent_id not in hierarchical_map["section_relationships"]:
                    hierarchical_map["section_relationships"][parent_id] = []
                
                hierarchical_map["section_relationships"][parent_id].append({
                    "child_id": section_id,
                    "full_citation": section["full_citation"],
                    "title": section["title"],
                    "page": section["page"],
                    "level": section["level"]
                })
        
        # Identify critical sections (construction standards, etc.)
        critical_sections = [s for s in all_sections if s.get("critical")]
        for section in critical_sections:
            hierarchical_map["critical_sections"][section["section_id"]] = section
        
        # Build content classification map
        for structure in extracted_structures:
            content_extraction = structure.get("content_extraction", {})
            for content_type, instances in content_extraction.items():
                if content_type not in hierarchical_map["content_classification"]:
                    hierarchical_map["content_classification"][content_type] = []
                
                hierarchical_map["content_classification"][content_type].extend(instances)
        
        print(f"✅ Built hierarchical map with {len(hierarchical_map['qap_outline'])} main sections")
        print(f"📊 Mapped {len(hierarchical_map['section_relationships'])} parent-child relationships")
        print(f"🎯 Identified {len(hierarchical_map['critical_sections'])} critical sections")
        
        return hierarchical_map
    
    def analyze_construction_standards_structure(self, hierarchical_map: Dict[str, Any]) -> Dict[str, Any]:
        """Detailed analysis of construction standards section structure"""
        print("🏗️ Analyzing construction standards structure...")
        
        analysis = {
            "target_section": "§10325(f)(7) Minimum Construction Standards",
            "expected_location": "Pages 66-69",
            "hierarchical_path": ["§10325", "(f) Basic Threshold Requirements", "(7) Minimum Construction Standards"],
            "found_instances": [],
            "structural_problems": [],
            "extraction_requirements": []
        }
        
        # Check if construction standards were found
        construction_content = hierarchical_map.get("content_classification", {}).get("construction_standards", [])
        if construction_content:
            analysis["found_instances"] = construction_content
            print(f"✅ Found construction standards content on {len(construction_content)} pages")
        else:
            analysis["structural_problems"].append("Construction standards content not detected")
        
        # Check for critical section identification
        critical_sections = hierarchical_map.get("critical_sections", {})
        if "10325_f_7" in critical_sections:
            critical_section = critical_sections["10325_f_7"]
            analysis["critical_section_found"] = critical_section
            print(f"🎯 Critical section found: {critical_section['full_citation']} on page {critical_section['page']}")
        else:
            analysis["structural_problems"].append("Critical construction standards section not identified")
        
        # Define extraction requirements for complete section
        analysis["extraction_requirements"] = [
            "Extract complete §10325(f)(7) from start to end",
            "Include all subsections (A) through (M)(iv)",
            "Preserve hierarchical structure and formatting",
            "Map to exact PDF pages (66-69)",
            "Maintain parent-child relationships with §10325(f)",
            "Distinguish from other sections (especially Tie Breakers)"
        ]
        
        return analysis
    
    def run_complete_structure_analysis(self) -> Dict[str, Any]:
        """Run complete QAP structure analysis for Phase 2"""
        print("🚀 M4 STRIKE LEADER - PHASE 2 STRUCTURE ANALYSIS")
        print("=" * 60)
        
        start_time = time.time()
        
        analysis_results = {
            "mission_phase": "Phase 2 - Structure Analysis",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "pdf_files_processed": [],
            "hierarchical_map": {},
            "construction_standards_analysis": {},
            "structural_insights": [],
            "phase_3_requirements": [],
            "overall_success": False
        }
        
        # Process all QAP PDF files
        extracted_structures = []
        for pdf_path in self.qap_pdf_paths:
            structure = self.extract_pdf_structure(pdf_path)
            extracted_structures.append(structure)
            analysis_results["pdf_files_processed"].append({
                "file": pdf_path.name,
                "sections_found": len(structure.get("sections_found", [])),
                "has_error": "error" in structure
            })
        
        # Build hierarchical map
        if extracted_structures:
            hierarchical_map = self.build_hierarchical_map(extracted_structures)
            analysis_results["hierarchical_map"] = hierarchical_map
            
            # Analyze construction standards specifically
            construction_analysis = self.analyze_construction_standards_structure(hierarchical_map)
            analysis_results["construction_standards_analysis"] = construction_analysis
            
            # Generate structural insights
            analysis_results["structural_insights"] = [
                f"Processed {len(self.qap_pdf_paths)} PDF files",
                f"Mapped {len(hierarchical_map.get('qap_outline', {}))} main QAP sections",
                f"Identified {len(hierarchical_map.get('section_relationships', {}))} parent-child relationships",
                f"Found {len(hierarchical_map.get('critical_sections', {}))} critical sections"
            ]
            
            # Define Phase 3 requirements
            analysis_results["phase_3_requirements"] = [
                "Build enhanced section parser using mapped structure",
                "Implement complete section extraction (§10325(f)(7))",
                "Create working verification system with correct IDs",
                "Add PDF page mapping for all sections",
                "Fix section classification (no more Tie Breakers mislabeling)"
            ]
            
            analysis_results["overall_success"] = True
        
        elapsed_time = time.time() - start_time
        print(f"\n⏱️ Analysis completed in {elapsed_time:.2f} seconds")
        print(f"🎯 Phase 2 Success: {analysis_results['overall_success']}")
        
        return analysis_results

if __name__ == "__main__":
    mapper = QAPStructureMapper()
    results = mapper.run_complete_structure_analysis()
    
    # Save results for milestone report
    output_path = Path(__file__).parent / "phase2_structure_analysis.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Structure analysis saved to: {output_path}")