#!/usr/bin/env python3
"""
Federal LIHTC Sources Processing System with Enhanced Metadata
Processes federal LIHTC documents (IRC, CFR, Revenue Procedures, etc.) into semantic chunks for RAG implementation
Integrates with existing 49-state QAP RAG system
"""

import os
import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
import PyPDF2
import re
from dataclasses import dataclass, asdict
import pandas as pd
from urllib.parse import urlparse

@dataclass
class FederalLIHTCChunk:
    """Individual chunk of federal LIHTC content with enhanced metadata"""
    chunk_id: str
    source_type: str  # "IRC", "CFR", "Rev_Proc", "PLR", "Rev_Rul", "Fed_Reg"
    authority_level: str  # "statutory", "regulatory", "guidance", "interpretive"
    section_reference: str  # e.g., "26 USC §42(d)(3)", "26 CFR §1.42-5(c)"
    document_title: str
    effective_date: str = ""
    superseded_by: str = ""
    page_number: int = 0
    content: str = ""
    content_type: str = "regulation"  # regulation, statute, guidance, interpretation
    chunk_size: int = 0
    entities: List[str] = None  # Federal-specific entities
    cross_references: List[str] = None  # References to other federal sections
    state_applications: List[str] = None  # Which states cite/implement this
    metadata: Dict = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = []
        if self.cross_references is None:
            self.cross_references = []
        if self.state_applications is None:
            self.state_applications = []
        if self.metadata is None:
            self.metadata = {}
        self.chunk_size = len(self.content)

class FederalLIHTCProcessor:
    """Process federal LIHTC documents into semantic chunks for RAG implementation"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.federal_dir = self.base_dir / "federal" / "LIHTC_Federal_Sources"
        self.processed_dir = self.federal_dir / "_processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for processed content
        (self.processed_dir / "chunks").mkdir(exist_ok=True)
        (self.processed_dir / "_indexes").mkdir(exist_ok=True)
        
        # Processing results
        self.processing_stats = {
            'documents_processed': 0,
            'total_pages': 0,
            'total_chunks': 0,
            'by_source_type': {},
            'by_authority_level': {},
            'errors': []
        }
        
        # Federal source type mapping
        self.source_type_mapping = {
            'IRC_Section_42': {'type': 'IRC', 'authority': 'statutory'},
            'Treasury_Regulations': {'type': 'CFR', 'authority': 'regulatory'},
            'Revenue_Procedures': {'type': 'Rev_Proc', 'authority': 'guidance'},
            'Revenue_Rulings': {'type': 'Rev_Rul', 'authority': 'guidance'},
            'Private_Letter_Rulings': {'type': 'PLR', 'authority': 'interpretive'},
            'Federal_Register': {'type': 'Fed_Reg', 'authority': 'regulatory'}
        }
    
    def find_federal_documents(self) -> List[Tuple[str, str, Path]]:
        """Find all federal documents for processing"""
        documents = []
        
        current_dir = self.federal_dir / "current"
        if not current_dir.exists():
            print(f"⚠️  Federal sources directory not found: {current_dir}")
            return documents
        
        for source_dir in current_dir.iterdir():
            if source_dir.is_dir() and source_dir.name in self.source_type_mapping:
                source_info = self.source_type_mapping[source_dir.name]
                
                # Find PDF, HTML, TXT files
                for file_path in source_dir.glob('*'):
                    if file_path.suffix.lower() in ['.pdf', '.html', '.txt']:
                        documents.append((
                            source_info['type'], 
                            source_info['authority'], 
                            file_path
                        ))
        
        return documents
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[Tuple[int, str]]:
        """Extract text from PDF with page numbers (inherited from QAP system)"""
        pages = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        text = page.extract_text()
                        if text.strip():  # Only include pages with text
                            pages.append((page_num, text))
                    except Exception as e:
                        print(f"    ⚠️  Error extracting page {page_num}: {e}")
                        
        except Exception as e:
            print(f"    ❌ Error reading PDF: {e}")
            
        return pages
    
    def extract_text_from_html(self, html_path: Path) -> List[Tuple[int, str]]:
        """Extract text from HTML files (for online sources)"""
        try:
            with open(html_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Basic HTML cleaning (remove tags, scripts, styles)
            import re
            content = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL)
            content = re.sub(r'<style.*?</style>', '', content, flags=re.DOTALL)
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\s+', ' ', content).strip()
            
            # For HTML, treat as single "page"
            return [(1, content)]
            
        except Exception as e:
            print(f"    ❌ Error reading HTML: {e}")
            return []
    
    def extract_text_from_txt(self, txt_path: Path) -> List[Tuple[int, str]]:
        """Extract text from TXT files"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # For TXT, treat as single "page"
            return [(1, content)]
            
        except Exception as e:
            print(f"    ❌ Error reading TXT: {e}")
            return []
    
    def detect_federal_section_headers(self, text: str, source_type: str) -> List[str]:
        """Detect section headers in federal documents"""
        headers = []
        
        # Federal-specific section patterns
        patterns = {
            'IRC': [
                r'§\s*42\([a-z]\)(?:\(\d+\))*',  # § 42(a), § 42(b)(1)
                r'Section\s+42\([a-z]\)(?:\(\d+\))*',
                r'subsection\s+\([a-z]\)(?:\(\d+\))*',
            ],
            'CFR': [
                r'§\s*1\.42-\d+[a-z]*(?:\([a-z]\))*(?:\(\d+\))*',  # § 1.42-5(c)(1)
                r'26\s+CFR\s+1\.42-\d+',
                r'Reg\.\s*§\s*1\.42-\d+',
            ],
            'Rev_Proc': [
                r'Section\s+\d+[\.\s]',  # Section 3. SCOPE
                r'SECTION\s+\d+[\.\s]',
                r'^\d+\.\s+[A-Z][A-Z\s]+$',  # 3. BACKGROUND
            ],
            'Fed_Reg': [
                r'§\s*\d+\.\d+',  # § 1.42-5
                r'Section\s+\d+\.\d+',
                r'Part\s+[IVX]+',
            ]
        }
        
        # Use source-specific patterns, fall back to general patterns
        source_patterns = patterns.get(source_type, [])
        if not source_patterns:
            source_patterns = patterns['Rev_Proc']  # Default patterns
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                for pattern in source_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        headers.append(line)
                        break
        
        return headers
    
    def extract_federal_entities(self, text: str, source_type: str) -> List[str]:
        """Extract federal-specific entities from text"""
        entities = []
        
        # Federal-specific entity patterns
        patterns = {
            'usc_references': r'26\s+U\.?S\.?C\.?\s*§\s*42(?:\([a-z]\))*(?:\(\d+\))*',
            'cfr_references': r'26\s+CFR\s*§?\s*1\.42-\d+[a-z]*(?:\([a-z]\))*(?:\(\d+\))*',
            'section_42_refs': r'[Ss]ection\s+42(?:\([a-z]\))*(?:\(\d+\))*',
            'effective_dates': r'effective\s+(?:on\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            'transition_rules': r'(?:transition|grandfather|effective)\s+(?:rule|period|date)',
            'money_amounts': r'\$[\d,]+(?:\.\d{2})?(?:\s*million|\s*billion)?',
            'percentages': r'\b\d+(?:\.\d+)?%',
            'ami_references': r'area\s+median\s+income|AMI',
            'dcr_requirements': r'\b\d\.\d{2}\s*(?:DCR|debt\s+coverage\s+ratio)',
            'credit_rates': r'(?:applicable\s+)?(?:credit\s+)?(?:rate|percentage)\s+of\s+\d+(?:\.\d+)?%',
            'compliance_periods': r'\b(?:15|30)\s*year\s*(?:compliance\s*)?period',
            'recapture_events': r'recapture|noncompliance|disposition',
            'qualified_basis': r'qualified\s+basis|eligible\s+basis',
            'placed_in_service': r'placed\s+in\s+service',
            'revenue_proc_refs': r'Rev\.?\s*Proc\.?\s*\d{4}-\d+',
            'revenue_ruling_refs': r'Rev\.?\s*Rul\.?\s*\d{4}-\d+',
            'treasury_decisions': r'T\.D\.?\s*\d+',
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(f"{entity_type}:{match}")
        
        return entities
    
    def determine_authority_hierarchy_score(self, authority_level: str) -> int:
        """Assign numerical scores for authority hierarchy"""
        hierarchy = {
            'statutory': 100,    # IRC Section 42
            'regulatory': 80,    # CFR regulations
            'guidance': 60,      # Revenue Procedures
            'interpretive': 40   # PLRs, Revenue Rulings
        }
        return hierarchy.get(authority_level, 0)
    
    def split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into logical paragraphs for chunking"""
        # Split on double newlines, then filter out very short segments
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if len(p.strip()) > 100]
    
    def classify_federal_content_type(self, text: str, source_type: str) -> str:
        """Classify the type of federal content"""
        text_lower = text.lower()
        
        # Source-specific classification
        if source_type == 'IRC':
            if any(term in text_lower for term in ['definition', 'means', 'includes']):
                return 'definition'
            elif 'shall' in text_lower or 'must' in text_lower:
                return 'requirement'
            else:
                return 'statute'
        
        elif source_type == 'CFR':
            if 'example' in text_lower:
                return 'example'
            elif 'table' in text_lower or 'schedule' in text_lower:
                return 'table'
            else:
                return 'regulation'
        
        elif source_type in ['Rev_Proc', 'Rev_Rul']:
            if 'background' in text_lower:
                return 'background'
            elif 'holding' in text_lower or 'conclusion' in text_lower:
                return 'holding'
            else:
                return 'guidance'
        
        else:
            return 'federal_document'
    
    def create_semantic_chunks(self, pages: List[Tuple[int, str]], source_type: str, 
                             authority_level: str, file_path: Path) -> List[FederalLIHTCChunk]:
        """Create semantic chunks from federal document pages"""
        chunks = []
        current_section = "Introduction"
        chunk_counter = 1
        
        # Extract document metadata
        doc_title = file_path.stem
        effective_date = self.extract_effective_date(pages)
        
        for page_num, page_text in pages:
            # Detect section headers on this page
            headers = self.detect_federal_section_headers(page_text, source_type)
            if headers:
                current_section = headers[0]  # Use first header found
            
            # Split page into logical chunks
            paragraphs = self.split_into_paragraphs(page_text)
            
            for para in paragraphs:
                if len(para.strip()) < 100:  # Skip very short paragraphs
                    continue
                
                chunk_id = f"FED_{source_type}_{chunk_counter:04d}"
                
                chunk = FederalLIHTCChunk(
                    chunk_id=chunk_id,
                    source_type=source_type,
                    authority_level=authority_level,
                    section_reference=self.extract_primary_section_ref(para, source_type),
                    document_title=doc_title,
                    effective_date=effective_date,
                    page_number=page_num,
                    content=para.strip(),
                    content_type=self.classify_federal_content_type(para, source_type),
                    entities=self.extract_federal_entities(para, source_type),
                    cross_references=self.extract_cross_references(para),
                    metadata={
                        'file_path': str(file_path),
                        'section_title': current_section,
                        'authority_score': self.determine_authority_hierarchy_score(authority_level),
                        'processing_date': datetime.now().isoformat(),
                    }
                )
                
                chunks.append(chunk)
                chunk_counter += 1
        
        return chunks
    
    def extract_effective_date(self, pages: List[Tuple[int, str]]) -> str:
        """Extract effective date from document"""
        for page_num, text in pages:
            # Look for effective date patterns
            patterns = [
                r'effective\s+(?:on\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
                r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(0)
        
        return ""
    
    def extract_primary_section_ref(self, text: str, source_type: str) -> str:
        """Extract the primary section reference for this chunk"""
        if source_type == 'IRC':
            match = re.search(r'26\s+U\.?S\.?C\.?\s*§\s*42(?:\([a-z]\))*(?:\(\d+\))*', text, re.IGNORECASE)
            if match:
                return match.group(0)
            
        elif source_type == 'CFR':
            match = re.search(r'26\s+CFR\s*§?\s*1\.42-\d+[a-z]*(?:\([a-z]\))*(?:\(\d+\))*', text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return ""
    
    def extract_cross_references(self, text: str) -> List[str]:
        """Extract cross-references to other sections"""
        refs = []
        
        patterns = [
            r'[Ss]ection\s+42\([a-z]\)(?:\(\d+\))*',
            r'26\s+CFR\s*§?\s*1\.42-\d+',
            r'Rev\.?\s*Proc\.?\s*\d{4}-\d+',
            r'see\s+also|cf\.|compare',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            refs.extend(matches)
        
        return refs
    
    def process_federal_document(self, source_type: str, authority_level: str, file_path: Path) -> List[FederalLIHTCChunk]:
        """Process a single federal document"""
        print(f"  📄 Processing {source_type}: {file_path.name}")
        
        # Extract text based on file type
        if file_path.suffix.lower() == '.pdf':
            pages = self.extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() == '.html':
            pages = self.extract_text_from_html(file_path)
        elif file_path.suffix.lower() == '.txt':
            pages = self.extract_text_from_txt(file_path)
        else:
            print(f"    ⚠️  Unsupported file type: {file_path.suffix}")
            return []
        
        if not pages:
            print(f"    ⚠️  No content extracted from {file_path.name}")
            return []
        
        # Create semantic chunks
        chunks = self.create_semantic_chunks(pages, source_type, authority_level, file_path)
        
        # Update statistics
        self.processing_stats['documents_processed'] += 1
        self.processing_stats['total_pages'] += len(pages)
        self.processing_stats['total_chunks'] += len(chunks)
        
        if source_type not in self.processing_stats['by_source_type']:
            self.processing_stats['by_source_type'][source_type] = 0
        self.processing_stats['by_source_type'][source_type] += len(chunks)
        
        if authority_level not in self.processing_stats['by_authority_level']:
            self.processing_stats['by_authority_level'][authority_level] = 0
        self.processing_stats['by_authority_level'][authority_level] += len(chunks)
        
        print(f"    ✅ Created {len(chunks)} chunks from {len(pages)} pages")
        return chunks
    
    def save_chunks_to_json(self, chunks: List[FederalLIHTCChunk], filename: str):
        """Save chunks to JSON file"""
        output_path = self.processed_dir / "chunks" / f"{filename}.json"
        
        # Convert chunks to dictionaries for JSON serialization
        chunks_data = []
        for chunk in chunks:
            chunk_dict = asdict(chunk)
            chunk_dict['processing_timestamp'] = datetime.now().isoformat()
            chunks_data.append(chunk_dict)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
        print(f"    💾 Saved {len(chunks)} chunks to {output_path}")
    
    def process_all_federal_sources(self):
        """Process all federal documents in the sources directory"""
        print("🇺🇸 Starting Federal LIHTC Sources Processing")
        print(f"📁 Source directory: {self.federal_dir}")
        
        # Find all federal documents
        documents = self.find_federal_documents()
        print(f"📋 Found {len(documents)} federal documents to process")
        
        all_chunks = []
        
        for source_type, authority_level, file_path in documents:
            try:
                chunks = self.process_federal_document(source_type, authority_level, file_path)
                all_chunks.extend(chunks)
                
                # Save chunks for each document separately
                filename = f"federal_{source_type}_{file_path.stem}"
                self.save_chunks_to_json(chunks, filename)
                
            except Exception as e:
                error_msg = f"Error processing {file_path}: {e}"
                print(f"    ❌ {error_msg}")
                self.processing_stats['errors'].append(error_msg)
        
        # Save combined chunks
        if all_chunks:
            self.save_chunks_to_json(all_chunks, "federal_lihtc_all_sources")
        
        # Save processing statistics
        self.save_processing_report()
        
        print(f"\n✅ Federal processing complete!")
        print(f"📊 Total: {len(all_chunks)} chunks from {len(documents)} documents")
        print(f"📈 Success rate: {((len(documents) - len(self.processing_stats['errors'])) / len(documents) * 100):.1f}%")
    
    def save_processing_report(self):
        """Save processing statistics and report"""
        report_path = self.processed_dir / f"federal_processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.processing_stats, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Processing report saved: {report_path}")

def main():
    """Main execution function"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    processor = FederalLIHTCProcessor(base_dir)
    processor.process_all_federal_sources()

if __name__ == "__main__":
    main()