#!/usr/bin/env python3
"""
CTCAC QAP OCR Extractor with RAG Optimization and 9%/4% Program Tagging
Extracts and formats the December 11, 2024 QAP Regulations PDF
"""

import sys
import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Try to import pdfplumber first (best quality)
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    print("Warning: pdfplumber not installed. Install with: pip install pdfplumber")
    PDF_AVAILABLE = False

class CTCACQAPExtractor:
    """Extract and format CTCAC QAP with RAG optimization"""
    
    def __init__(self, pdf_path: str, output_dir: str):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.sections_dir = self.output_dir / "sections"
        self.chunks_dir = self.output_dir / "chunks"  
        self.metadata_dir = self.output_dir / "metadata"
        
        for dir in [self.sections_dir, self.chunks_dir, self.metadata_dir]:
            dir.mkdir(exist_ok=True)
        
        # Section mappings for 9% vs 4%
        self.program_mappings = {
            "10325": {"programs": ["9%"], "title": "Application Selection Criteria"},
            "10326": {"programs": ["4%"], "title": "Tax-Exempt Bond Projects"},
            "10327": {"programs": ["9%", "4%"], "title": "Building Requirements"},
            "10322": {"programs": ["9%", "4%"], "title": "Application Requirements"},
            "10300": {"programs": ["9%", "4%"], "title": "General"},
            "10301": {"programs": ["9%", "4%"], "title": "Definitions"},
            "10302": {"programs": ["9%", "4%"], "title": "Definitions (continued)"},
        }
        
        # Track entities and relationships
        self.entities = []
        self.relationships = []
        self.qa_pairs = []
        self.chunks = []
        
    def extract_pdf(self) -> List[Tuple[int, str]]:
        """Extract text from PDF"""
        text_pages = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"Extracting {total_pages} pages...")
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                text_pages.append((i + 1, text))
                
                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{total_pages} pages...")
                    
        return text_pages
    
    def identify_section_program(self, section_num: str, content: str) -> List[str]:
        """Identify which program(s) a section applies to"""
        # Check known mappings
        if section_num in self.program_mappings:
            return self.program_mappings[section_num]["programs"]
        
        # Look for program indicators in content
        indicators_9_only = [
            "competitive allocation",
            "competitive tax credit",
            "set-aside",
            "tiebreaker",
            "scoring",
            "point",
            "competitive round"
        ]
        
        indicators_4_only = [
            "tax-exempt bond",
            "bond project",
            "private activity bond",
            "bond allocation"
        ]
        
        content_lower = content.lower()
        
        has_9 = any(ind in content_lower for ind in indicators_9_only)
        has_4 = any(ind in content_lower for ind in indicators_4_only)
        
        if has_9 and not has_4:
            return ["9%"]
        elif has_4 and not has_9:
            return ["4%"]
        else:
            return ["9%", "4%"]
    
    def format_header(self, total_pages: int) -> str:
        """Create document header"""
        return f"""################################################################################
# CALIFORNIA TAX CREDIT ALLOCATION COMMITTEE REGULATIONS
# Title 4, Division 17, Chapter 1
# Implementing Health and Safety Code Sections 50199.4-50199.22
# 
# SOURCE DOCUMENT: December_11_2024_QAP_Regulations_FINAL.pdf
# EFFECTIVE DATE: December 11, 2024
# OCR CONVERSION DATE: {datetime.now().strftime('%Y-%m-%d')}
# TOTAL PAGES: {total_pages}
#
# IMPORTANT: This is an OCR conversion. For legal purposes, refer to the
# official PDF version available at www.treasurer.ca.gov/ctcac/
#
# RAG OPTIMIZATION: This document includes semantic chunking, entity tagging,
# and program applicability markers (9% vs 4%) for AI retrieval systems.
################################################################################

"""
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract entities from text"""
        entities = []
        
        # Extract percentages
        for match in re.finditer(r'\b(\d+(?:\.\d+)?)\s*%', text):
            entities.append({
                "type": "PERCENT",
                "value": match.group(1),
                "context": text[max(0, match.start()-20):match.end()+20]
            })
        
        # Extract money amounts
        for match in re.finditer(r'\$[\d,]+(?:\.\d{2})?', text):
            entities.append({
                "type": "MONEY", 
                "value": match.group(0),
                "context": text[max(0, match.start()-20):match.end()+20]
            })
        
        # Extract section references
        for match in re.finditer(r'Section\s+(\d+)(?:\(([a-z])\)(?:\((\d+)\))?)?', text):
            entities.append({
                "type": "SECTION_REF",
                "value": match.group(0),
                "section": match.group(1),
                "subsection": match.group(2),
                "paragraph": match.group(3)
            })
        
        # Extract dates
        for match in re.finditer(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}', text):
            entities.append({
                "type": "DATE",
                "value": match.group(0)
            })
            
        return entities
    
    def create_chunk(self, text: str, section: str, programs: List[str], 
                    chunk_type: str = "general", start_pos: int = 0) -> Dict:
        """Create a semantic chunk with metadata"""
        chunk_id = f"ctcac_qap_2025_chunk_{len(self.chunks):04d}"
        
        # Extract key topics from chunk
        topics = []
        topic_keywords = {
            "at-risk": ["at-risk", "at risk", "preservation"],
            "developer-fee": ["developer fee", "consultant fee"],
            "scoring": ["points", "scoring", "score"],
            "set-aside": ["set-aside", "set aside", "allocation"],
            "tiebreaker": ["tiebreaker", "tie breaker", "tie-breaker"],
            "basis": ["eligible basis", "qualified basis", "basis boost"],
            "qct-dda": ["QCT", "DDA", "qualified census tract", "difficult development"]
        }
        
        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        
        chunk = {
            "chunk_id": chunk_id,
            "text": text,
            "metadata": {
                "source_section": section,
                "program_applicability": programs,
                "topics": topics,
                "chunk_type": chunk_type,
                "char_count": len(text),
                "word_count": len(text.split()),
                "position": start_pos,
                "entities": self.extract_entities(text)
            }
        }
        
        # Add program-specific warnings
        if len(programs) == 1:
            if programs[0] == "9%":
                chunk["metadata"]["warning"] = "This section only applies to 9% competitive tax credit projects"
            elif programs[0] == "4%":
                chunk["metadata"]["warning"] = "This section only applies to 4% tax-exempt bond projects"
                
        return chunk
    
    def process_section(self, section_num: str, title: str, content: str, 
                       programs: List[str], page_num: int) -> str:
        """Process a section with RAG enhancements"""
        output = []
        
        # Section header with metadata
        output.append(f"\n{'='*80}")
        output.append(f"[Page {page_num}]")
        output.append(f"SECTION {section_num}. {title}")
        
        # Program applicability
        if len(programs) == 1:
            output.append(f"[APPLICABILITY: {programs[0]} ONLY]")
            other_program = "4%" if programs[0] == "9%" else "9%"
            if section_num == "10325":
                output.append(f"[NOT_APPLICABLE: {other_program} Tax-Exempt Bond Projects - See Section 10326]")
            elif section_num == "10326":
                output.append(f"[NOT_APPLICABLE: {other_program} Competitive Projects - See Section 10325]")
        else:
            output.append(f"[APPLICABILITY: BOTH 9% AND 4% WITH VARIATIONS]")
        
        # Metadata block
        output.append("[METADATA]")
        output.append(f"- Section ID: {section_num}")
        output.append(f"- Title: {title}")
        output.append(f"- Program Type: {', '.join(programs)} Credits")
        output.append(f"- Last Updated: December 11, 2024")
        output.append("[END METADATA]")
        output.append('='*80)
        
        # Anchor tag
        output.append(f"\n<<SECTION_{section_num}>>")
        
        # Process content with inline tags
        processed_content = self.add_inline_tags(content, programs)
        output.append(processed_content)
        
        # Create chunks from this section
        self.create_section_chunks(section_num, content, programs)
        
        return '\n'.join(output)
    
    def add_inline_tags(self, content: str, programs: List[str]) -> str:
        """Add inline program tags and entity markers"""
        # Add program tags for subsections
        if len(programs) > 1:
            # Look for program-specific language
            content = re.sub(
                r'(for (?:competitive |)(?:tax credit|9%) projects)',
                r'<<PROGRAM:9%>>\1',
                content,
                flags=re.IGNORECASE
            )
            content = re.sub(
                r'(for (?:tax-exempt |)bond projects)',
                r'<<PROGRAM:4%>>\1', 
                content,
                flags=re.IGNORECASE
            )
        
        # Add entity tags
        content = re.sub(
            r'\b(\d+(?:\.\d+)?)\s*%',
            r'<<ENTITY:PERCENT>>\1%<</ENTITY:PERCENT>>',
            content
        )
        
        content = re.sub(
            r'(\$[\d,]+(?:\.\d{2})?)',
            r'<<ENTITY:MONEY>>\1<</ENTITY:MONEY>>',
            content
        )
        
        # Add cross-reference tags
        content = re.sub(
            r'Section\s+(\d+)(?:\(([a-z])\)(?:\((\d+)\))?)?',
            lambda m: f'Section {m.group(1)}{"(" + m.group(2) + ")" if m.group(2) else ""}{"(" + m.group(3) + ")" if m.group(3) else ""} <<XREF:{m.group(1)}{"_" + m.group(2) if m.group(2) else ""}{"_" + m.group(3) if m.group(3) else ""}>>',
            content
        )
        
        return content
    
    def create_section_chunks(self, section_num: str, content: str, programs: List[str]):
        """Create semantic chunks from section content"""
        # Split into paragraphs
        paragraphs = re.split(r'\n\s*\n', content)
        
        for i, para in enumerate(paragraphs):
            if len(para.strip()) > 50:  # Skip very short paragraphs
                chunk = self.create_chunk(
                    text=para.strip(),
                    section=section_num,
                    programs=programs,
                    chunk_type="paragraph",
                    start_pos=i
                )
                self.chunks.append(chunk)
                
                # Save individual chunk file
                chunk_file = self.chunks_dir / f"{chunk['chunk_id']}.json"
                with open(chunk_file, 'w') as f:
                    json.dump(chunk, f, indent=2)
    
    def generate_qa_pairs(self, text: str, section: str, programs: List[str]) -> List[Dict]:
        """Generate Q&A pairs from text"""
        qa_pairs = []
        
        # Pattern matching for common regulatory patterns
        patterns = [
            # Developer fee pattern
            (r'developer fee.*?shall not exceed\s+(.+?)(?:percent|%)', 
             "What is the developer fee limit for {program} projects?",
             "The developer fee limit is {match}"),
            
            # Deadline pattern
            (r'applications? (?:must|shall) be (?:submitted|received) by\s+([^.]+)',
             "When is the application deadline?",
             "Applications must be submitted by {match}"),
            
            # Minimum requirement pattern
            (r'minimum (?:of\s+)?(.+?)\s+(?:is|shall be)\s+(.+?)(?:\.|,)',
             "What is the minimum {group1}?",
             "The minimum {group1} is {group2}")
        ]
        
        for pattern, q_template, a_template in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                for program in programs:
                    qa = {
                        "question": q_template.format(
                            program=program,
                            group1=match.group(1) if match.lastindex >= 1 else "",
                            match=match.group(0)
                        ),
                        "answer": a_template.format(
                            match=match.group(0),
                            group1=match.group(1) if match.lastindex >= 1 else "",
                            group2=match.group(2) if match.lastindex >= 2 else ""
                        ),
                        "section": section,
                        "program": program
                    }
                    qa_pairs.append(qa)
                    
        return qa_pairs
    
    def save_metadata(self):
        """Save all metadata files"""
        # Save entities
        with open(self.metadata_dir / "entities.json", 'w') as f:
            json.dump(self.entities, f, indent=2)
        
        # Save relationships  
        with open(self.metadata_dir / "relationships.json", 'w') as f:
            json.dump(self.relationships, f, indent=2)
        
        # Save Q&A pairs
        with open(self.metadata_dir / "qa_pairs.json", 'w') as f:
            json.dump(self.qa_pairs, f, indent=2)
        
        # Save chunk index
        chunk_index = {
            "total_chunks": len(self.chunks),
            "chunks_by_section": {},
            "chunks_by_program": {"9%": [], "4%": [], "both": []},
            "chunks_by_topic": {}
        }
        
        for chunk in self.chunks:
            section = chunk["metadata"]["source_section"]
            if section not in chunk_index["chunks_by_section"]:
                chunk_index["chunks_by_section"][section] = []
            chunk_index["chunks_by_section"][section].append(chunk["chunk_id"])
            
            # By program
            programs = chunk["metadata"]["program_applicability"]
            if len(programs) == 1:
                chunk_index["chunks_by_program"][programs[0]].append(chunk["chunk_id"])
            else:
                chunk_index["chunks_by_program"]["both"].append(chunk["chunk_id"])
            
            # By topic
            for topic in chunk["metadata"]["topics"]:
                if topic not in chunk_index["chunks_by_topic"]:
                    chunk_index["chunks_by_topic"][topic] = []
                chunk_index["chunks_by_topic"][topic].append(chunk["chunk_id"])
        
        with open(self.metadata_dir / "chunk_index.json", 'w') as f:
            json.dump(chunk_index, f, indent=2)
        
        # Save program mapping
        with open(self.metadata_dir / "program_mapping.json", 'w') as f:
            json.dump(self.program_mappings, f, indent=2)
    
    def run(self):
        """Run the complete extraction process"""
        print(f"Starting CTCAC QAP extraction from: {self.pdf_path}")
        
        if not os.path.exists(self.pdf_path):
            print(f"Error: PDF not found at {self.pdf_path}")
            return
            
        if not PDF_AVAILABLE:
            print("Error: pdfplumber not installed")
            return
        
        # Extract PDF
        text_pages = self.extract_pdf()
        total_pages = len(text_pages)
        
        # Create main output file
        output_file = self.output_dir / "CTCAC_QAP_2025_OCR_RAG.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write(self.format_header(total_pages))
            
            current_section = None
            section_content = []
            
            for page_num, text in text_pages:
                # Look for section headers
                section_match = re.search(r'Section\s+(\d+)\.\s+([^\n]+)', text)
                
                if section_match:
                    # Process previous section if exists
                    if current_section:
                        section_num, title = current_section
                        content = '\n'.join(section_content)
                        programs = self.identify_section_program(section_num, content)
                        
                        section_text = self.process_section(
                            section_num, title, content, programs, page_num
                        )
                        f.write(section_text)
                        
                        # Save individual section file
                        section_file = self.sections_dir / f"{section_num}_{title.replace(' ', '_')}.txt"
                        with open(section_file, 'w') as sf:
                            sf.write(section_text)
                    
                    # Start new section
                    current_section = (section_match.group(1), section_match.group(2).strip())
                    section_content = [text]
                    
                    # Extract entities from this page
                    self.entities.extend(self.extract_entities(text))
                    
                else:
                    # Continue current section
                    if current_section:
                        section_content.append(text)
                    else:
                        # Pre-section content
                        f.write(f"\n[Page {page_num}]\n")
                        f.write(text)
                
                # Add page break
                if page_num < total_pages:
                    f.write(f"\n\n---PAGE BREAK--- [Page {page_num + 1}]\n")
            
            # Process final section
            if current_section:
                section_num, title = current_section
                content = '\n'.join(section_content)
                programs = self.identify_section_program(section_num, content)
                
                section_text = self.process_section(
                    section_num, title, content, programs, total_pages
                )
                f.write(section_text)
        
        # Save all metadata
        self.save_metadata()
        
        print(f"\nExtraction complete!")
        print(f"Main file: {output_file}")
        print(f"Total pages: {total_pages}")
        print(f"Sections extracted: {len(list(self.sections_dir.glob('*.txt')))}")
        print(f"Chunks created: {len(self.chunks)}")
        print(f"Entities found: {len(self.entities)}")
        
        # Generate summary report
        summary = {
            "extraction_date": datetime.now().isoformat(),
            "source_pdf": self.pdf_path,
            "total_pages": total_pages,
            "sections_extracted": len(list(self.sections_dir.glob('*.txt'))),
            "chunks_created": len(self.chunks),
            "entities_found": len(self.entities),
            "output_structure": {
                "main_ocr": str(output_file),
                "sections_dir": str(self.sections_dir),
                "chunks_dir": str(self.chunks_dir),
                "metadata_dir": str(self.metadata_dir)
            }
        }
        
        with open(self.output_dir / "extraction_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nFor RAG usage, see extraction_summary.json")

def main():
    pdf_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CA_9p_2025_R2_Perris/CTCAC_Rules/December_11_2024_QAP_Regulations_FINAL.pdf"
    output_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/CTCAC_QAP_2025_RAG"
    
    extractor = CTCACQAPExtractor(pdf_path, output_dir)
    extractor.run()

if __name__ == "__main__":
    main()