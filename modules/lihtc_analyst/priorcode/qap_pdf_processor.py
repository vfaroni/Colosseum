#!/usr/bin/env python3
"""
QAP PDF to JSON Chunking System with Metadata Preservation
Processes downloaded QAP PDFs into semantic chunks for RAG implementation
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import PyPDF2
import re
from dataclasses import dataclass, asdict
import pandas as pd

@dataclass
class QAPChunk:
    """Individual chunk of QAP content with metadata"""
    chunk_id: str
    state_code: str
    document_title: str
    document_year: int
    page_number: int
    section_title: str = ""
    content: str = ""
    content_type: str = "regulation"  # regulation, table, list, appendix
    program_type: str = "both"  # 9%, 4%, both
    chunk_size: int = 0
    entities: List[str] = None  # Extracted entities (dates, money, percentages)
    cross_references: List[str] = None  # References to other sections
    metadata: Dict = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = []
        if self.cross_references is None:
            self.cross_references = []
        if self.metadata is None:
            self.metadata = {}
        self.chunk_size = len(self.content)

class QAPPDFProcessor:
    """Process QAP PDFs into semantic chunks for RAG implementation"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.qap_dir = self.base_dir / "QAP"
        self.processed_dir = self.qap_dir / "_processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Processing results
        self.processing_stats = {
            'documents_processed': 0,
            'total_pages': 0,
            'total_chunks': 0,
            'by_state': {},
            'by_type': {},
            'errors': []
        }
    
    def find_downloaded_pdfs(self) -> List[Tuple[str, Path]]:
        """Find all downloaded PDF files"""
        pdf_files = []
        
        for state_dir in self.qap_dir.iterdir():
            if state_dir.is_dir() and len(state_dir.name) == 2:  # State code directories
                state_code = state_dir.name
                
                # Check all subdirectories for PDFs
                for subdir in ['current', 'archive', 'applications', 'awards', 'notices']:
                    pdf_dir = state_dir / subdir
                    if pdf_dir.exists():
                        for pdf_file in pdf_dir.glob('*.pdf'):
                            pdf_files.append((state_code, pdf_file))
        
        return pdf_files
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[Tuple[int, str]]:
        """Extract text from PDF with page numbers"""
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
    
    def detect_section_headers(self, text: str) -> List[str]:
        """Detect section headers in QAP text"""
        headers = []
        
        # Common QAP section patterns
        patterns = [
            r'Section\s+\d+[A-Z]*[\.\s]',  # Section 10325, Section 1.1
            r'SECTION\s+\d+[A-Z]*[\.\s]',
            r'Article\s+[IVX]+[\.\s]',      # Article I, Article II
            r'Chapter\s+\d+[\.\s]',        # Chapter 1
            r'Part\s+[IVX]+[\.\s]',        # Part I
            r'§\s*\d+[\.\d]*',             # § 10325.1
            r'^\d+\.\d+[\.\d]*\s+[A-Z]',   # 1.1 DEFINITIONS
            r'^[A-Z\s]{10,}$',             # ALL CAPS HEADERS
        ]
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        headers.append(line)
                        break
        
        return headers
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract key entities from text (dates, money, percentages, etc.)"""
        entities = []
        
        # Entity patterns
        patterns = {
            'dates': r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            'money': r'\$[\d,]+(?:\.\d{2})?(?:\s*million|\s*billion)?',
            'percentages': r'\b\d+(?:\.\d+)?%',
            'dcr_requirements': r'\b\d\.\d{2}\s*(?:DCR|debt coverage ratio)',
            'section_refs': r'Section\s+\d+[A-Z]*(?:\(\w+\))*',
            'years': r'\b20\d{2}\b',
            'ami_levels': r'\b\d{1,2}%\s*(?:of\s*)?(?:area\s*median\s*income|AMI)',
            'unit_counts': r'\b\d+\s*units?\b'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(f"{entity_type}:{match}")
        
        return entities
    
    def detect_program_type(self, text: str) -> str:
        """Detect if content applies to 9%, 4%, or both programs"""
        text_lower = text.lower()
        
        # Strong indicators
        if '9%' in text or 'nine percent' in text_lower or 'competitive' in text_lower:
            if '4%' in text or 'four percent' in text_lower or 'bond' in text_lower:
                return 'both'
            return '9%'
        elif '4%' in text or 'four percent' in text_lower or 'bond' in text_lower or 'tax-exempt' in text_lower:
            return '4%'
        
        # Context clues
        if any(term in text_lower for term in ['scoring', 'selection criteria', 'ranking', 'competitive']):
            return '9%'
        elif any(term in text_lower for term in ['bond financing', 'tax-exempt', 'non-competitive']):
            return '4%'
        
        return 'both'
    
    def create_semantic_chunks(self, pages: List[Tuple[int, str]], state_code: str, doc_title: str, doc_year: int) -> List[QAPChunk]:
        """Create semantic chunks from PDF pages"""
        chunks = []
        current_section = "Introduction"
        chunk_counter = 1
        
        for page_num, page_text in pages:
            # Detect section headers on this page
            headers = self.detect_section_headers(page_text)
            if headers:
                current_section = headers[0]  # Use first header found
            
            # Split page into logical chunks (by paragraphs or sections)
            paragraphs = self.split_into_paragraphs(page_text)
            
            for para in paragraphs:
                if len(para.strip()) < 50:  # Skip very short paragraphs
                    continue
                
                chunk_id = f"{state_code}_{doc_year}_chunk_{chunk_counter:04d}"
                
                chunk = QAPChunk(
                    chunk_id=chunk_id,
                    state_code=state_code,
                    document_title=doc_title,
                    document_year=doc_year,
                    page_number=page_num,
                    section_title=current_section,
                    content=para.strip(),
                    content_type=self.classify_content_type(para),
                    program_type=self.detect_program_type(para),
                    entities=self.extract_entities(para),
                    cross_references=self.extract_cross_references(para),
                    metadata={
                        'processed_date': datetime.now().isoformat(),
                        'source_file': doc_title,
                        'processing_version': '1.0'
                    }
                )
                
                chunks.append(chunk)
                chunk_counter += 1
        
        return chunks
    
    def split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into logical paragraphs"""
        # Split by double newlines or other paragraph indicators
        paragraphs = re.split(r'\n\s*\n|\r\n\s*\r\n', text)
        
        # Further split very long paragraphs
        result = []
        for para in paragraphs:
            para = para.strip()
            if len(para) > 2000:  # Split long paragraphs
                sentences = re.split(r'[.!?]\s+', para)
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk + sentence) > 1500:
                        if current_chunk:
                            result.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        current_chunk += sentence + ". "
                if current_chunk:
                    result.append(current_chunk.strip())
            else:
                result.append(para)
        
        return [p for p in result if p.strip()]
    
    def classify_content_type(self, text: str) -> str:
        """Classify the type of content"""
        text_lower = text.lower()
        
        if '|' in text or '\t' in text or re.search(r'\d+\s+\d+\s+\d+', text):
            return 'table'
        elif re.search(r'^\s*[•\-\*]\s+', text, re.MULTILINE):
            return 'list'
        elif any(word in text_lower for word in ['appendix', 'exhibit', 'attachment', 'schedule']):
            return 'appendix'
        elif any(word in text_lower for word in ['section', 'subsection', 'paragraph']):
            return 'regulation'
        else:
            return 'text'
    
    def extract_cross_references(self, text: str) -> List[str]:
        """Extract cross-references to other sections"""
        refs = []
        
        patterns = [
            r'Section\s+\d+[A-Z]*(?:\(\w+\))*',
            r'§\s*\d+[\.\d]*',
            r'see\s+(?:Section\s+)?\d+[A-Z]*',
            r'pursuant\s+to\s+Section\s+\d+[A-Z]*'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            refs.extend(matches)
        
        return list(set(refs))  # Remove duplicates
    
    def process_pdf(self, state_code: str, pdf_path: Path) -> List[QAPChunk]:
        """Process a single PDF file"""
        print(f"  📄 Processing: {pdf_path.name}")
        
        # Extract text from PDF
        pages = self.extract_text_from_pdf(pdf_path)
        if not pages:
            print(f"    ❌ No text extracted from {pdf_path.name}")
            return []
        
        print(f"    📑 Extracted {len(pages)} pages")
        
        # Determine document info
        doc_title = pdf_path.stem
        doc_year = 2025  # Default, could be extracted from filename or content
        
        # Extract year from filename if possible
        year_match = re.search(r'20\d{2}', doc_title)
        if year_match:
            doc_year = int(year_match.group())
        
        # Create semantic chunks
        chunks = self.create_semantic_chunks(pages, state_code, doc_title, doc_year)
        
        print(f"    📦 Created {len(chunks)} chunks")
        
        # Update stats
        self.processing_stats['total_pages'] += len(pages)
        self.processing_stats['total_chunks'] += len(chunks)
        self.processing_stats['by_state'][state_code] = self.processing_stats['by_state'].get(state_code, 0) + len(chunks)
        
        return chunks
    
    def save_chunks(self, chunks: List[QAPChunk], state_code: str):
        """Save chunks to JSON files"""
        if not chunks:
            return
        
        # Create state directory
        state_processed_dir = self.processed_dir / state_code
        state_processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Save individual chunk files
        chunks_dir = state_processed_dir / "chunks"
        chunks_dir.mkdir(parents=True, exist_ok=True)
        
        for chunk in chunks:
            chunk_file = chunks_dir / f"{chunk.chunk_id}.json"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(chunk), f, indent=2, ensure_ascii=False)
        
        # Save consolidated file
        consolidated_file = state_processed_dir / f"{state_code}_all_chunks.json"
        chunks_data = [asdict(chunk) for chunk in chunks]
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
        # Save summary metadata
        summary = {
            'state_code': state_code,
            'total_chunks': len(chunks),
            'documents_processed': len(set(chunk.document_title for chunk in chunks)),
            'total_content_size': sum(chunk.chunk_size for chunk in chunks),
            'program_breakdown': {
                '9%': len([c for c in chunks if c.program_type == '9%']),
                '4%': len([c for c in chunks if c.program_type == '4%']),
                'both': len([c for c in chunks if c.program_type == 'both'])
            },
            'content_types': {},
            'processed_date': datetime.now().isoformat()
        }
        
        # Count content types
        for chunk in chunks:
            summary['content_types'][chunk.content_type] = summary['content_types'].get(chunk.content_type, 0) + 1
        
        summary_file = state_processed_dir / f"{state_code}_processing_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"    💾 Saved to: {state_processed_dir}")
    
    def process_all_pdfs(self) -> Dict:
        """Process all downloaded PDFs"""
        pdf_files = self.find_downloaded_pdfs()
        
        print(f"🔍 Found {len(pdf_files)} PDF files to process")
        
        all_chunks = []
        
        for state_code, pdf_path in pdf_files:
            print(f"\n📋 Processing {state_code}: {pdf_path.name}")
            
            try:
                chunks = self.process_pdf(state_code, pdf_path)
                if chunks:
                    all_chunks.extend(chunks)
                    self.save_chunks(chunks, state_code)
                    self.processing_stats['documents_processed'] += 1
                else:
                    self.processing_stats['errors'].append(f"{state_code}: No chunks created from {pdf_path.name}")
                    
            except Exception as e:
                error_msg = f"{state_code}: Error processing {pdf_path.name} - {str(e)}"
                print(f"    ❌ {error_msg}")
                self.processing_stats['errors'].append(error_msg)
        
        # Save master index
        self.save_master_index(all_chunks)
        
        return self.processing_stats
    
    def save_master_index(self, all_chunks: List[QAPChunk]):
        """Save master index of all chunks for RAG system"""
        index_data = {
            'total_chunks': len(all_chunks),
            'states_processed': list(set(chunk.state_code for chunk in all_chunks)),
            'processing_date': datetime.now().isoformat(),
            'chunks_by_state': {},
            'chunks_by_program': {},
            'chunks_by_type': {}
        }
        
        # Organize by state
        for chunk in all_chunks:
            state = chunk.state_code
            if state not in index_data['chunks_by_state']:
                index_data['chunks_by_state'][state] = []
            index_data['chunks_by_state'][state].append({
                'chunk_id': chunk.chunk_id,
                'section_title': chunk.section_title,
                'program_type': chunk.program_type,
                'content_type': chunk.content_type,
                'chunk_size': chunk.chunk_size
            })
        
        # Organize by program type
        for chunk in all_chunks:
            prog = chunk.program_type
            if prog not in index_data['chunks_by_program']:
                index_data['chunks_by_program'][prog] = []
            index_data['chunks_by_program'][prog].append(chunk.chunk_id)
        
        # Organize by content type
        for chunk in all_chunks:
            ctype = chunk.content_type
            if ctype not in index_data['chunks_by_type']:
                index_data['chunks_by_type'][ctype] = []
            index_data['chunks_by_type'][ctype].append(chunk.chunk_id)
        
        # Save master index
        index_file = self.processed_dir / "master_chunk_index.json"
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
        
        print(f"\n📊 Master index saved: {index_file}")
    
    def generate_processing_report(self) -> str:
        """Generate comprehensive processing report"""
        report = f"""
=== QAP PDF PROCESSING REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL RESULTS:
- Documents Processed: {self.processing_stats['documents_processed']}
- Total Pages Extracted: {self.processing_stats['total_pages']}
- Total Chunks Created: {self.processing_stats['total_chunks']}
- Average Chunks per Document: {self.processing_stats['total_chunks'] / max(1, self.processing_stats['documents_processed']):.1f}

CHUNKS BY STATE:
"""
        
        for state, count in sorted(self.processing_stats['by_state'].items()):
            report += f"- {state}: {count} chunks\n"
        
        if self.processing_stats['errors']:
            report += f"""
PROCESSING ERRORS:
"""
            for error in self.processing_stats['errors']:
                report += f"- {error}\n"
        
        report += f"""
OUTPUT STRUCTURE:
- Master Index: {self.processed_dir}/master_chunk_index.json
- State Directories: {self.processed_dir}/[STATE]/
- Individual Chunks: {self.processed_dir}/[STATE]/chunks/
- Consolidated Files: {self.processed_dir}/[STATE]/[STATE]_all_chunks.json

NEXT STEPS:
1. Build vector database from processed chunks
2. Implement RAG search functionality
3. Create query interface for multi-state QAP search
"""
        
        return report

def main():
    """Process all downloaded QAP PDFs into semantic chunks"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    
    print("📄 Starting QAP PDF Processing...")
    
    processor = QAPPDFProcessor(base_dir)
    
    # Process all PDFs
    stats = processor.process_all_pdfs()
    
    # Generate and display report
    report = processor.generate_processing_report()
    print(report)
    
    # Save report
    report_file = processor.processed_dir / f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"💾 Report saved to: {report_file}")
    
    print("🎯 TASK COMPLETED: Create PDF to JSON chunking system with metadata preservation")

if __name__ == "__main__":
    main()