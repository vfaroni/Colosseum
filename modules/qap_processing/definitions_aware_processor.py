#!/usr/bin/env python3
"""
Definitions-Aware Enhanced Processor - Phase 2A
Combines enhanced chunking with definitions extraction and PDF page mapping
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, NamedTuple
from datetime import datetime
from dataclasses import dataclass

# Import base enhanced processor
from simple_enhanced_processor import SimpleEnhancedProcessor, ProcessingMetrics

# Import Docling
try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import PdfFormatOption
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

@dataclass
class Definition:
    """Structured definition with PDF page reference"""
    definition_id: str
    state_code: str
    term: str
    definition: str
    section_reference: str
    pdf_page: Optional[int]
    document_year: int
    source_chunk_id: str
    definition_type: str
    category: str
    extraction_confidence: float
    pattern_used: str
    cross_references: List[Dict[str, Any]]
    usage_locations: List[Dict[str, Any]]

@dataclass 
class ProcessingResult:
    """Complete processing result with definitions"""
    enhanced_chunks: List[Dict[str, Any]]
    definitions: List[Definition]
    page_mapping: Dict[str, int]
    processing_metrics: ProcessingMetrics

class DefinitionsAwareProcessor(SimpleEnhancedProcessor):
    """Enhanced processor with definitions extraction and PDF page mapping"""
    
    def __init__(self):
        super().__init__()
        
        # Definition extraction patterns for different QAP styles
        self.definition_patterns = {
            'ctcac_style': {
                'pattern': r'-\s*\(([a-z])\)\s+([A-Z][^.]*?)\.\s+([^-]+?)(?=\n\s*-\s*\([a-z]\)|$)',
                'groups': ['subsection', 'term', 'definition'],
                'confidence': 0.9
            },
            'means_style': {
                'pattern': r'"([^"]+)"\s+means\s+([^.]+\.)',
                'groups': ['term', 'definition'],
                'confidence': 0.85
            },
            'colon_style': {
                'pattern': r'([A-Z][^:]+):\s+([^.]+\.)',
                'groups': ['term', 'definition'],
                'confidence': 0.75
            },
            'numbered_style': {
                'pattern': r'(\d+)\.\s+([A-Z][^-]+)\s*-\s*([^.]+\.)',
                'groups': ['number', 'term', 'definition'],
                'confidence': 0.8
            }
        }
        
        # Definition categories
        self.definition_categories = {
            'housing_types': ['accessible', 'affordable', 'family', 'senior', 'supportive'],
            'income_requirements': ['ami', 'income', 'limits', 'verification', 'median'],
            'calculation': ['basis', 'credit', 'allocation', 'percentage', 'amount'],
            'compliance': ['compliance', 'monitoring', 'period', 'certification'],
            'general': ['default']
        }
    
    def extract_with_docling_and_pages(self, pdf_path: Path, state_code: str) -> ProcessingResult:
        """Enhanced extraction with PDF page mapping and definitions"""
        
        if not DOCLING_AVAILABLE:
            raise ImportError("Docling not available - install with: pip install docling")
        
        print(f"🔍 Processing {state_code} QAP with definitions extraction...")
        
        start_time = datetime.now()
        
        # Convert PDF with enhanced options for page mapping
        result = self.converter.convert(str(pdf_path))
        document = result.document
        
        # Extract page mapping
        page_mapping = self._extract_page_mapping(document)
        print(f"📄 Extracted page mapping for {len(page_mapping)} content sections")
        
        # Get enhanced chunks with page references
        strategy = self.classify_qap_strategy(state_code)
        enhanced_chunks = self._create_enhanced_chunks_with_pages(
            document.export_to_markdown(), state_code, strategy, page_mapping
        )
        
        # Extract definitions with page references
        definitions = self._extract_definitions(document, state_code, page_mapping)
        print(f"📖 Extracted {len(definitions)} definitions with page references")
        
        # Create processing metrics
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        metrics = ProcessingMetrics(
            processing_time_seconds=processing_time,
            total_chunks=len(enhanced_chunks),
            total_definitions=len(definitions),
            pages_processed=len(page_mapping),
            average_chunk_size=sum(len(chunk.get('content', '')) for chunk in enhanced_chunks) / len(enhanced_chunks) if enhanced_chunks else 0
        )
        
        return ProcessingResult(
            enhanced_chunks=enhanced_chunks,
            definitions=definitions,
            page_mapping=page_mapping,
            processing_metrics=metrics
        )
    
    def _extract_page_mapping(self, document) -> Dict[str, int]:
        """Extract page numbers for content sections using Docling's document structure"""
        
        page_mapping = {}
        
        try:
            # Try to extract page information from Docling document structure
            if hasattr(document, 'pages'):
                for page_num, page in enumerate(document.pages, 1):
                    if hasattr(page, 'text') and page.text:
                        # Map significant content chunks to page numbers
                        content_key = self._normalize_content_key(page.text[:300])
                        page_mapping[content_key] = page_num
            
            # Alternative: Extract from main text with page markers
            full_text = document.export_to_markdown()
            sections = full_text.split('\n## ')
            
            # Estimate page numbers based on content length and typical PDF structure
            chars_per_page = 2500  # Approximate characters per QAP page
            current_char = 0
            
            for section in sections:
                if section.strip():
                    section_key = self._normalize_content_key(section[:300])
                    estimated_page = max(1, current_char // chars_per_page + 1)
                    page_mapping[section_key] = estimated_page
                    current_char += len(section)
            
            print(f"📄 Page mapping created for {len(page_mapping)} sections")
            
        except Exception as e:
            print(f"⚠️  Page mapping extraction failed: {e}")
            # Fallback: Create basic page estimates
            full_text = document.export_to_markdown()
            chars_per_page = 2500
            total_pages = max(1, len(full_text) // chars_per_page)
            
            sections = full_text.split('\n## ')
            for i, section in enumerate(sections):
                if section.strip():
                    section_key = self._normalize_content_key(section[:300])
                    page_mapping[section_key] = min(total_pages, i + 1)
        
        return page_mapping
    
    def _normalize_content_key(self, content: str) -> str:
        """Normalize content for consistent page mapping"""
        # Remove extra whitespace and special characters
        normalized = re.sub(r'\s+', ' ', content.strip())
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return normalized.lower()[:200]  # Limit length for key
    
    def _create_enhanced_chunks_with_pages(self, text_content: str, state_code: str, 
                                         strategy: str, page_mapping: Dict[str, int]) -> List[Dict[str, Any]]:
        """Create enhanced chunks with PDF page references"""
        
        # Use existing chunking strategy
        base_chunks = self._create_enhanced_chunks(text_content, state_code, strategy)
        
        # Add page references to chunks
        enhanced_chunks = []
        for chunk in base_chunks:
            # Find page number for this chunk
            content_key = self._normalize_content_key(chunk.get('content', '')[:300])
            page_number = self._find_best_page_match(content_key, page_mapping)
            
            # Add page reference to metadata
            chunk_metadata = chunk.get('metadata', {})
            chunk_metadata['pdf_page'] = page_number
            chunk_metadata['page_mapping_confidence'] = 0.8 if page_number else 0.0
            
            chunk['metadata'] = chunk_metadata
            enhanced_chunks.append(chunk)
        
        return enhanced_chunks
    
    def _find_best_page_match(self, content_key: str, page_mapping: Dict[str, int]) -> Optional[int]:
        """Find best page number match for content"""
        
        # Direct match
        if content_key in page_mapping:
            return page_mapping[content_key]
        
        # Fuzzy match - find closest content key
        best_match = None
        best_score = 0
        
        for mapped_key, page_num in page_mapping.items():
            # Simple similarity based on common words
            content_words = set(content_key.split())
            mapped_words = set(mapped_key.split())
            
            if content_words and mapped_words:
                similarity = len(content_words & mapped_words) / len(content_words | mapped_words)
                if similarity > best_score and similarity > 0.3:  # Threshold for relevance
                    best_score = similarity
                    best_match = page_num
        
        return best_match
    
    def _extract_definitions(self, document, state_code: str, page_mapping: Dict[str, int]) -> List[Definition]:
        """Extract definitions with PDF page references"""
        
        definitions = []
        text_content = document.export_to_markdown()
        
        # Look for definitions sections
        definitions_sections = self._identify_definitions_sections(text_content)
        
        for section_info in definitions_sections:
            section_text = section_info['text']
            section_title = section_info['title']
            
            # Try each pattern to extract definitions
            for pattern_name, pattern_info in self.definition_patterns.items():
                extracted = self._extract_definitions_with_pattern(
                    section_text, pattern_info, state_code, section_title, page_mapping
                )
                definitions.extend(extracted)
                
                if extracted:
                    print(f"✅ Extracted {len(extracted)} definitions using {pattern_name}")
        
        # Remove duplicates and sort by term
        unique_definitions = self._deduplicate_definitions(definitions)
        unique_definitions.sort(key=lambda d: d.term.lower())
        
        return unique_definitions
    
    def _identify_definitions_sections(self, text_content: str) -> List[Dict[str, Any]]:
        """Identify sections that contain definitions"""
        
        definitions_sections = []
        
        # Look for explicit definitions sections
        definition_markers = [
            r'§?\s*\d+\.\s*Definitions',
            r'Section\s+\d+\.\s*Definitions',
            r'Article\s+[IVX]+\.\s*Definitions',
            r'Part\s+[A-Z]\.\s*Definitions',
            r'##\s*.*Definitions'
        ]
        
        for marker in definition_markers:
            matches = list(re.finditer(marker, text_content, re.IGNORECASE))
            for match in matches:
                # Extract section from match to next major section
                start = match.start()
                
                # Find end of definitions section
                next_section = re.search(r'\n##?\s*[A-Z]', text_content[start + 100:])
                end = start + 100 + next_section.start() if next_section else len(text_content)
                
                section_text = text_content[start:end]
                
                definitions_sections.append({
                    'title': match.group(),
                    'text': section_text,
                    'start_pos': start,
                    'confidence': 0.9
                })
        
        # If no explicit definitions section found, look for definition-rich content
        if not definitions_sections:
            # Look for sections with high density of definition patterns
            sections = text_content.split('\n## ')
            for section in sections:
                if self._has_definition_patterns(section):
                    definitions_sections.append({
                        'title': section.split('\n')[0] if section else 'Unknown Section',
                        'text': section,
                        'start_pos': 0,
                        'confidence': 0.6
                    })
        
        return definitions_sections
    
    def _has_definition_patterns(self, text: str) -> bool:
        """Check if text contains definition patterns"""
        
        definition_indicators = [
            r'\([a-z]\)\s+[A-Z][^.]*\.',  # (a) Term.
            r'"[^"]+"\s+means',           # "Term" means
            r'[A-Z][^:]+:\s+[A-Z]',       # Term: Definition
        ]
        
        pattern_count = 0
        for pattern in definition_indicators:
            matches = len(re.findall(pattern, text))
            pattern_count += matches
        
        # Consider it a definitions section if it has 3+ definition patterns
        return pattern_count >= 3
    
    def _extract_definitions_with_pattern(self, text: str, pattern_info: Dict, 
                                        state_code: str, section_title: str,
                                        page_mapping: Dict[str, int]) -> List[Definition]:
        """Extract definitions using a specific pattern"""
        
        definitions = []
        pattern = pattern_info['pattern']
        groups = pattern_info['groups']
        confidence = pattern_info['confidence']
        
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        
        for i, match in enumerate(matches):
            try:
                # Extract term and definition based on pattern groups
                if 'subsection' in groups:
                    subsection = match.group(1)
                    term = match.group(2).strip()
                    definition = match.group(3).strip()
                    section_ref = f"{section_title}({subsection})"
                else:
                    term = match.group(1).strip()
                    definition = match.group(2).strip()
                    section_ref = section_title
                
                # Clean up extracted text
                term = self._clean_definition_term(term)
                definition = self._clean_definition_text(definition)
                
                if term and definition and len(definition) > 10:  # Quality filter
                    
                    # Find page number for this definition
                    context = text[max(0, match.start()-100):match.start()+200]
                    content_key = self._normalize_content_key(context)
                    page_number = self._find_best_page_match(content_key, page_mapping)
                    
                    definition_obj = Definition(
                        definition_id=f"{state_code}_def_{len(definitions):04d}",
                        state_code=state_code,
                        term=term,
                        definition=definition,
                        section_reference=section_ref,
                        pdf_page=page_number,
                        document_year=2025,  # Current QAP year
                        source_chunk_id="",  # Will be linked later
                        definition_type="regulatory_definition",
                        category=self._categorize_definition(term, definition),
                        extraction_confidence=confidence,
                        pattern_used=list(self.definition_patterns.keys())[list(self.definition_patterns.values()).index(pattern_info)],
                        cross_references=[],  # Will be populated later
                        usage_locations=[]    # Will be populated later
                    )
                    
                    definitions.append(definition_obj)
                    
            except Exception as e:
                print(f"⚠️  Error extracting definition {i}: {e}")
                continue
        
        return definitions
    
    def _clean_definition_term(self, term: str) -> str:
        """Clean and normalize definition term"""
        # Remove extra whitespace and special characters
        cleaned = re.sub(r'\s+', ' ', term.strip())
        cleaned = re.sub(r'^[^\w]+|[^\w]+$', '', cleaned)  # Remove leading/trailing non-word chars
        return cleaned
    
    def _clean_definition_text(self, definition: str) -> str:
        """Clean and normalize definition text"""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', definition.strip())
        # Remove incomplete sentences at the end
        if not cleaned.endswith('.'):
            sentences = cleaned.split('.')
            if len(sentences) > 1:
                cleaned = '.'.join(sentences[:-1]) + '.'
        return cleaned
    
    def _categorize_definition(self, term: str, definition: str) -> str:
        """Categorize definition based on term and content"""
        
        term_lower = term.lower()
        definition_lower = definition.lower()
        combined_text = f"{term_lower} {definition_lower}"
        
        for category, keywords in self.definition_categories.items():
            if any(keyword in combined_text for keyword in keywords):
                return category
        
        return 'general'  # Default category
    
    def _deduplicate_definitions(self, definitions: List[Definition]) -> List[Definition]:
        """Remove duplicate definitions keeping the best quality one"""
        
        unique_definitions = {}
        
        for definition in definitions:
            key = definition.term.lower().strip()
            
            if key not in unique_definitions:
                unique_definitions[key] = definition
            else:
                # Keep the one with higher confidence
                existing = unique_definitions[key]
                if definition.extraction_confidence > existing.extraction_confidence:
                    unique_definitions[key] = definition
        
        return list(unique_definitions.values())
    
    def save_definitions_database(self, definitions: List[Definition], output_dir: Path) -> Path:
        """Save definitions as structured JSON database"""
        
        definitions_data = {
            'extraction_date': datetime.now().isoformat(),
            'total_definitions': len(definitions),
            'definitions': [self._definition_to_dict(d) for d in definitions]
        }
        
        output_file = output_dir / f"definitions_{definitions[0].state_code}_{datetime.now().strftime('%Y%m%d')}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(definitions_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(definitions)} definitions to {output_file}")
        return output_file
    
    def _definition_to_dict(self, definition: Definition) -> Dict[str, Any]:
        """Convert Definition object to dictionary"""
        return {
            'definition_id': definition.definition_id,
            'state_code': definition.state_code,
            'term': definition.term,
            'definition': definition.definition,
            'section_reference': definition.section_reference,
            'pdf_page': definition.pdf_page,
            'document_year': definition.document_year,
            'source_chunk_id': definition.source_chunk_id,
            'definition_type': definition.definition_type,
            'category': definition.category,
            'extraction_confidence': definition.extraction_confidence,
            'pattern_used': definition.pattern_used,
            'cross_references': definition.cross_references,
            'usage_locations': definition.usage_locations
        }

def main():
    """Test the definitions-aware processor"""
    
    print("🚀 Testing Definitions-Aware Processor (Phase 2A)...")
    
    try:
        # Initialize processor
        processor = DefinitionsAwareProcessor()
        
        # Test with CA QAP (we know it has Section 10302 definitions)
        ca_qap_path = Path("./test_data/CA_QAP_2025.pdf")  # Placeholder path
        
        if not ca_qap_path.exists():
            print(f"⚠️  Test file not found: {ca_qap_path}")
            print("📝 Create test_data directory and add CA QAP PDF for testing")
            return
        
        # Process with definitions extraction
        result = processor.extract_with_docling_and_pages(ca_qap_path, "CA")
        
        print(f"\n📊 **PROCESSING RESULTS**:")
        print(f"Enhanced Chunks: {len(result.enhanced_chunks)}")
        print(f"Definitions Extracted: {len(result.definitions)}")
        print(f"Page Mappings: {len(result.page_mapping)}")
        print(f"Processing Time: {result.processing_metrics.processing_time_seconds:.2f}s")
        
        # Show sample definitions
        if result.definitions:
            print(f"\n📖 **SAMPLE DEFINITIONS**:")
            for i, definition in enumerate(result.definitions[:3], 1):
                print(f"{i}. **{definition.term}**")
                print(f"   Definition: {definition.definition[:100]}...")
                print(f"   Section: {definition.section_reference}")
                print(f"   PDF Page: {definition.pdf_page}")
                print(f"   Confidence: {definition.extraction_confidence}")
                print()
        
        # Save definitions database
        output_dir = Path("./definitions_output")
        definitions_file = processor.save_definitions_database(result.definitions, output_dir)
        
        print(f"✅ Definitions-aware processing complete!")
        print(f"📁 Definitions saved to: {definitions_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()