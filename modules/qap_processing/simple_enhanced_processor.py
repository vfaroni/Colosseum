#!/usr/bin/env python3
"""
Simple Enhanced QAP Processor - Working with proven Docling API
Based on successful M4 Beast tests, combines Docling text extraction with 4-strategy chunking
"""

import json
import time
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import psutil

from docling.document_converter import DocumentConverter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingMetrics:
    """Simple metrics for processing tracking"""
    state_code: str
    processing_time: float
    memory_used_mb: float
    pages_processed: int
    text_length: int
    chunks_created: int
    strategy_applied: str
    lihtc_terms_found: int
    federal_refs_found: int
    state_refs_found: int
    qap_crossrefs_found: int
    timestamp: str

class SimpleEnhancedProcessor:
    """
    Simple but powerful QAP processor using proven Docling API + 4-strategy chunking
    Focus on working functionality with M4 Beast optimization
    """
    
    # LIHTC terms for validation
    LIHTC_TERMS = {
        'lihtc', 'low-income housing tax credit', 'section 42', 'tax credit',
        'qualified basis', 'eligible basis', 'applicable percentage',
        '9% credit', '4% credit', 'competitive', 'non-competitive',
        'qap', 'qualified allocation plan', 'allocation', 'scoring',
        'compliance period', 'extended use', 'placed in service',
        'qct', 'qualified census tract', 'dda', 'difficult development area',
        'ami', 'area median income', 'maximum rent', 'income limits'
    }
    
    # Reference patterns
    FEDERAL_PATTERNS = [
        r'IRC\s*§?\s*(\d+)', r'Section\s*(\d+)', r'26\s*USC\s*(\d+)',
        r'26\s*CFR\s*[\d\.]+', r'Revenue\s*Procedure\s*\d+-\d+'
    ]
    
    QAP_PATTERNS = [
        r'Section\s*(\d+(?:\.\d+)*)', r'subsection\s*\(([a-z])\)',
        r'paragraph\s*\((\d+)\)'
    ]
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.data_path = self.base_path / "data_sets" / "QAP"
        self.output_path = self.base_path / "modules" / "qap_processing" / "enhanced_output"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Docling converter
        self.converter = DocumentConverter()
        
        logger.info(f"Simple Enhanced Processor initialized")
        logger.info(f"Data path: {self.data_path}")
        logger.info(f"Output path: {self.output_path}")
    
    def classify_qap_strategy(self, state_code: str) -> str:
        """Classify state into 4-strategy categories"""
        complex_states = ['CA', 'TX', 'NC', 'FL', 'NY', 'IL']
        simple_states = ['MA', 'WA', 'OR', 'VT', 'NH', 'ME']
        table_states = ['DE', 'NV', 'WY', 'ND']
        
        if state_code in complex_states:
            return "complex_outline"
        elif state_code in simple_states:
            return "simple_narrative"
        elif state_code in table_states:
            return "table_matrix"
        else:
            return "medium_complexity"
    
    def extract_with_docling(self, pdf_path: Path, state_code: str) -> Tuple[Dict[str, Any], ProcessingMetrics]:
        """Extract QAP content using proven Docling API"""
        start_time = time.time()
        start_memory = psutil.virtual_memory().used / (1024**2)
        
        logger.info(f"Processing {state_code} QAP: {pdf_path.name}")
        
        try:
            # Use proven Docling API
            result = self.converter.convert(str(pdf_path))
            
            if not result or not hasattr(result, 'document'):
                raise Exception("Docling conversion failed")
            
            # Extract text using working method
            document = result.document
            text_content = document.export_to_markdown()
            pages_count = len(document.pages) if hasattr(document, 'pages') and document.pages else 0
            
            # Apply strategy-based chunking
            strategy = self.classify_qap_strategy(state_code)
            chunks = self._create_enhanced_chunks(text_content, state_code, strategy)
            
            # Extract references and entities
            for chunk in chunks:
                self._add_references_and_entities(chunk)
            
            # Calculate metrics
            processing_time = time.time() - start_time
            memory_used = (psutil.virtual_memory().used / (1024**2)) - start_memory
            
            # Count reference types
            total_federal_refs = sum(len(chunk.get('federal_refs', [])) for chunk in chunks)
            total_state_refs = sum(len(chunk.get('state_refs', [])) for chunk in chunks)
            total_qap_refs = sum(len(chunk.get('qap_crossrefs', [])) for chunk in chunks)
            total_lihtc_terms = sum(len(chunk.get('lihtc_entities', [])) for chunk in chunks)
            
            metrics = ProcessingMetrics(
                state_code=state_code,
                processing_time=processing_time,
                memory_used_mb=memory_used,
                pages_processed=pages_count,
                text_length=len(text_content),
                chunks_created=len(chunks),
                strategy_applied=strategy,
                lihtc_terms_found=total_lihtc_terms,
                federal_refs_found=total_federal_refs,
                state_refs_found=total_state_refs,
                qap_crossrefs_found=total_qap_refs,
                timestamp=datetime.now().isoformat()
            )
            
            # Structure result
            result_data = {
                'state_code': state_code,
                'strategy': strategy,
                'processing_date': datetime.now().isoformat(),
                'docling_metadata': {
                    'pages_processed': pages_count,
                    'text_length': len(text_content),
                    'extraction_method': 'docling_markdown'
                },
                'enhanced_chunks': chunks,
                'metrics': asdict(metrics)
            }
            
            logger.info(f"✅ {state_code} processed: {len(chunks)} chunks, {processing_time:.2f}s")
            return result_data, metrics
            
        except Exception as e:
            logger.error(f"❌ Failed processing {state_code}: {e}")
            
            # Return error result
            error_metrics = ProcessingMetrics(
                state_code=state_code,
                processing_time=time.time() - start_time,
                memory_used_mb=0,
                pages_processed=0,
                text_length=0,
                chunks_created=0,
                strategy_applied="error",
                lihtc_terms_found=0,
                federal_refs_found=0,
                state_refs_found=0,
                qap_crossrefs_found=0,
                timestamp=datetime.now().isoformat()
            )
            
            return {'error': str(e), 'state_code': state_code}, error_metrics
    
    def _create_enhanced_chunks(self, text_content: str, state_code: str, strategy: str) -> List[Dict[str, Any]]:
        """Create enhanced chunks based on strategy"""
        chunks = []
        
        # Split text into sections based on common QAP patterns
        sections = self._split_into_sections(text_content)
        
        if strategy == "complex_outline":
            chunks = self._chunk_complex_outline(sections, state_code)
        elif strategy == "simple_narrative":
            chunks = self._chunk_simple_narrative(sections, state_code)
        elif strategy == "table_matrix":
            chunks = self._chunk_table_matrix(sections, state_code)
        else:  # medium_complexity
            chunks = self._chunk_medium_complexity(sections, state_code)
        
        return chunks
    
    def _split_into_sections(self, text_content: str) -> List[Dict[str, str]]:
        """Split text into logical sections"""
        sections = []
        
        # Split by common section headers
        section_patterns = [
            r'\n#+\s+(.+?)\n',  # Markdown headers
            r'\nSection\s+\d+[^\n]*\n',  # Section headers
            r'\n\d+\.\s+[A-Z][^\n]*\n',  # Numbered sections
            r'\n[A-Z\s]{10,}\n'  # All caps headings
        ]
        
        current_section = {"title": "Introduction", "content": ""}
        current_content = []
        
        lines = text_content.split('\n')
        for line in lines:
            # Check if this line is a section header
            is_header = False
            for pattern in section_patterns:
                if re.match(pattern.strip(), '\n' + line + '\n'):
                    is_header = True
                    break
            
            if is_header and current_content:
                # Save previous section
                current_section["content"] = '\n'.join(current_content).strip()
                if current_section["content"]:
                    sections.append(current_section.copy())
                
                # Start new section
                current_section = {"title": line.strip(), "content": ""}
                current_content = []
            else:
                current_content.append(line)
        
        # Add final section
        if current_content:
            current_section["content"] = '\n'.join(current_content).strip()
            if current_section["content"]:
                sections.append(current_section)
        
        # If no sections found, create one large section
        if not sections:
            sections = [{"title": "Complete Document", "content": text_content}]
        
        return sections
    
    def _chunk_complex_outline(self, sections: List[Dict], state_code: str) -> List[Dict]:
        """Complex outline chunking - one chunk per section"""
        chunks = []
        
        for i, section in enumerate(sections):
            if len(section['content'].strip()) < 50:  # Skip very short sections
                continue
                
            chunk = {
                'chunk_id': f"{state_code}_complex_{i:04d}",
                'state_code': state_code,
                'strategy': 'complex_outline',
                'section_title': section['title'],
                'content': section['content'],
                'hierarchy_level': self._detect_hierarchy_level(section['title']),
                'breadcrumb': self._create_breadcrumb(section['title']),
                'metadata': {
                    'processing_date': datetime.now().isoformat(),
                    'processor': 'simple_enhanced_docling',
                    'section_index': i,
                    'content_length': len(section['content'])
                }
            }
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_simple_narrative(self, sections: List[Dict], state_code: str) -> List[Dict]:
        """Simple narrative - combine multiple sections into larger chunks"""
        chunks = []
        
        # Combine sections into larger narrative chunks
        current_chunk_content = []
        current_titles = []
        chunk_count = 0
        
        for section in sections:
            current_chunk_content.append(section['content'])
            current_titles.append(section['title'])
            
            # Create chunk when we have enough content
            total_length = sum(len(content) for content in current_chunk_content)
            if len(current_chunk_content) >= 3 or total_length > 3000:
                chunk = {
                    'chunk_id': f"{state_code}_narrative_{chunk_count:04d}",
                    'state_code': state_code,
                    'strategy': 'simple_narrative',
                    'combined_titles': current_titles,
                    'content': '\n\n'.join(current_chunk_content),
                    'metadata': {
                        'processing_date': datetime.now().isoformat(),
                        'processor': 'simple_enhanced_docling',
                        'sections_combined': len(current_titles),
                        'content_length': total_length
                    }
                }
                chunks.append(chunk)
                
                current_chunk_content = []
                current_titles = []
                chunk_count += 1
        
        # Add remaining content
        if current_chunk_content:
            chunk = {
                'chunk_id': f"{state_code}_narrative_{chunk_count:04d}",
                'state_code': state_code,
                'strategy': 'simple_narrative',
                'combined_titles': current_titles,
                'content': '\n\n'.join(current_chunk_content),
                'metadata': {
                    'processing_date': datetime.now().isoformat(),
                    'processor': 'simple_enhanced_docling',
                    'sections_combined': len(current_titles)
                }
            }
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_table_matrix(self, sections: List[Dict], state_code: str) -> List[Dict]:
        """Table matrix chunking - focus on tables and scoring"""
        chunks = []
        
        for i, section in enumerate(sections):
            # Detect if section contains tables/scoring matrices
            has_table = self._detect_table_content(section['content'])
            
            chunk = {
                'chunk_id': f"{state_code}_matrix_{i:04d}",
                'state_code': state_code,
                'strategy': 'table_matrix',
                'section_title': section['title'],
                'content': section['content'],
                'contains_table': has_table,
                'is_scoring_matrix': has_table and 'point' in section['content'].lower(),
                'metadata': {
                    'processing_date': datetime.now().isoformat(),
                    'processor': 'simple_enhanced_docling',
                    'table_detected': has_table,
                    'content_length': len(section['content'])
                }
            }
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_medium_complexity(self, sections: List[Dict], state_code: str) -> List[Dict]:
        """Medium complexity - balanced approach"""
        chunks = []
        
        for i, section in enumerate(sections):
            if len(section['content'].strip()) < 100:  # Skip very short sections
                continue
                
            chunk = {
                'chunk_id': f"{state_code}_medium_{i:04d}",
                'state_code': state_code,
                'strategy': 'medium_complexity',
                'section_title': section['title'],
                'content': section['content'],
                'metadata': {
                    'processing_date': datetime.now().isoformat(),
                    'processor': 'simple_enhanced_docling',
                    'section_index': i,
                    'content_length': len(section['content'])
                }
            }
            chunks.append(chunk)
        
        return chunks
    
    def _detect_hierarchy_level(self, title: str) -> int:
        """Detect hierarchy level from title"""
        if re.match(r'#+\s', title):  # Markdown headers
            return len(re.match(r'#+', title.strip()).group(0))
        elif re.match(r'\d+\.\s', title):  # Numbered sections
            return 1
        elif re.match(r'\s*[a-z]\.\s', title):  # Lettered subsections
            return 2
        else:
            return 1
    
    def _create_breadcrumb(self, title: str) -> str:
        """Create breadcrumb from title"""
        # Extract section numbers for breadcrumb
        section_match = re.search(r'Section\s*(\d+(?:\.\d+)*)', title, re.IGNORECASE)
        if section_match:
            return f"Section {section_match.group(1)}"
        
        # Extract numbered sections
        number_match = re.search(r'^(\d+(?:\.\d+)*)', title.strip())
        if number_match:
            return f"Section {number_match.group(1)}"
        
        return title[:50] + "..." if len(title) > 50 else title
    
    def _detect_table_content(self, content: str) -> bool:
        """Detect if content contains table-like structures"""
        # Look for table indicators
        table_indicators = ['|', 'points', 'maximum', 'score', 'criteria', 'category']
        
        # Count lines that look like table rows
        lines = content.split('\n')
        table_like_lines = 0
        
        for line in lines:
            if '|' in line or re.search(r'\s+\d+\s+', line):
                table_like_lines += 1
        
        # If more than 20% of lines look like table content
        return table_like_lines > len(lines) * 0.2 and any(indicator in content.lower() for indicator in table_indicators)
    
    def _add_references_and_entities(self, chunk: Dict[str, Any]):
        """Add enhanced references and LIHTC entities to chunk"""
        content = chunk.get('content', '')
        
        # Extract federal references
        federal_refs = []
        for pattern in self.FEDERAL_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                federal_refs.append({
                    'type': 'federal_regulation',
                    'reference': match.group(0),
                    'authority_level': 'federal_statutory' if 'IRC' in match.group(0) or 'Section' in match.group(0) else 'federal_regulatory'
                })
        
        # Extract QAP cross-references
        qap_crossrefs = []
        for pattern in self.QAP_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                qap_crossrefs.append({
                    'type': 'qap_internal',
                    'reference': match.group(0),
                    'target_section': match.group(1) if match.groups() else match.group(0)
                })
        
        # Extract LIHTC entities
        lihtc_entities = []
        content_lower = content.lower()
        for term in self.LIHTC_TERMS:
            if term in content_lower:
                lihtc_entities.append({
                    'type': 'lihtc_term',
                    'value': term,
                    'category': self._categorize_lihtc_term(term)
                })
        
        # Add to chunk
        chunk['federal_refs'] = federal_refs
        chunk['state_refs'] = []  # Placeholder for state references
        chunk['qap_crossrefs'] = qap_crossrefs
        chunk['lihtc_entities'] = lihtc_entities
    
    def _categorize_lihtc_term(self, term: str) -> str:
        """Categorize LIHTC terms"""
        if term in ['qualified basis', 'eligible basis', 'applicable percentage']:
            return 'calculation'
        elif term in ['9% credit', '4% credit']:
            return 'credit_type'
        elif term in ['competitive', 'non-competitive']:
            return 'allocation_type'
        elif term in ['qct', 'dda']:
            return 'location_criteria'
        elif term in ['ami', 'area median income', 'maximum rent']:
            return 'income_requirements'
        else:
            return 'general'
    
    def save_results(self, results: Dict[str, Any], filename: str = None) -> Path:
        """Save processing results"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            state_code = results.get('state_code', 'unknown')
            filename = f"enhanced_qap_{state_code}_{timestamp}.json"
        
        output_file = self.output_path / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {output_file}")
        return output_file

def main():
    """Test the simple enhanced processor"""
    processor = SimpleEnhancedProcessor()
    
    # Test with California QAP
    ca_qap_path = processor.data_path / "CA" / "current" / "CA_2025_QAP_Regulations_Dec_2024.pdf"
    
    if ca_qap_path.exists():
        logger.info("Testing Simple Enhanced Processor with CA QAP...")
        
        results, metrics = processor.extract_with_docling(ca_qap_path, "CA")
        
        if 'error' not in results:
            print("\n" + "="*60)
            print("🏛️ SIMPLE ENHANCED PROCESSING RESULTS")
            print("="*60)
            print(f"State: {metrics.state_code}")
            print(f"Strategy: {metrics.strategy_applied}")
            print(f"Processing Time: {metrics.processing_time:.2f}s")
            print(f"Memory Used: {metrics.memory_used_mb:.2f}MB")
            print(f"Pages Processed: {metrics.pages_processed}")
            print(f"Text Length: {metrics.text_length:,} chars")
            print(f"Chunks Created: {metrics.chunks_created}")
            print(f"LIHTC Terms: {metrics.lihtc_terms_found}")
            print(f"Federal References: {metrics.federal_refs_found}")
            print(f"QAP Cross-refs: {metrics.qap_crossrefs_found}")
            
            # Save results
            output_file = processor.save_results(results)
            print(f"\n📁 Results saved to: {output_file}")
            
            # Show sample chunks
            chunks = results.get('enhanced_chunks', [])
            if chunks:
                print(f"\n📋 Sample chunks:")
                for i, chunk in enumerate(chunks[:3]):
                    print(f"  {i+1}. {chunk.get('section_title', 'No title')[:50]}...")
                    print(f"     Content: {len(chunk.get('content', ''))} chars")
                    print(f"     Federal refs: {len(chunk.get('federal_refs', []))}")
                    print(f"     QAP refs: {len(chunk.get('qap_crossrefs', []))}")
            
        else:
            print(f"❌ Processing failed: {results['error']}")
    
    else:
        logger.error(f"California QAP not found at {ca_qap_path}")

if __name__ == "__main__":
    main()