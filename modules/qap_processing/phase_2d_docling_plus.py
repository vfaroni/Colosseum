#!/usr/bin/env python3
"""
Phase 2D: Docling Plus - Targeted IBM Integration
Focused on definition extraction with PDF page mapping and cross-referencing
Building on Phase 2C success (175 definitions) with enhanced features
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import time
import re

# Enhanced Docling imports - using proven configuration
from docling.document_converter import DocumentConverter

class Phase2DDoclingPlus:
    """
    Docling Plus processor - targeted IBM integration for definition intelligence
    Builds on Phase 2C success with enhanced page mapping and cross-referencing
    """
    
    def __init__(self):
        """Initialize Docling Plus with proven configuration"""
        
        # Use proven Docling configuration from Phase 2C success
        # (Advanced IBM options not available in current version)
        self.converter = DocumentConverter()
        
        # Proven Phase 2C definition patterns
        self.definition_patterns = [
            {
                'name': 'simple_means',
                'regex': r'"([^"]+)"\s+means\s+([^.]+(?:\.[^.]*){0,2}\.)',
                'confidence': 0.8,
                'description': 'Phase 2B/2C proven pattern'
            },
            {
                'name': 'colon_definition', 
                'regex': r'([A-Z][A-Za-z\s]{5,40}):\s*([A-Z][^.]{20,200}\.)',
                'confidence': 0.85,
                'description': 'Phase 2C discovery - high yield'
            },
            {
                'name': 'section_subsection',
                'regex': r'\(([a-z]{1,3})\)\s+([A-Z][A-Za-z\s]{5,50})\.\s+([^.]+(?:\.[^.]*){0,3}\.)',
                'confidence': 0.95,
                'description': 'CTCAC Section 10302 format - CA success'
            },
            {
                'name': 'quoted_explanation',
                'regex': r'"([^"]{3,30})"\s+([A-Za-z][^.]{10,150}\.)',
                'confidence': 0.75,
                'description': 'Phase 2C filtered explanations'
            }
        ]
        
        print("🏛️ Phase 2D Docling Plus initialized")
        print("✅ Enhanced features: Page mapping, Definition intelligence, Cross-referencing")
        print("✅ Building on Phase 2C success: 175 definitions across 11 states")
    
    def process_qap_with_definition_intelligence(self, qap_file_path: str, state_code: str) -> Dict[str, Any]:
        """Process QAP with definition intelligence and page mapping"""
        
        start_time = time.time()
        print(f"\n🎯 Definition intelligence processing {state_code}: {Path(qap_file_path).name}")
        
        try:
            # Convert document with enhanced Docling
            print("🔍 Converting with enhanced Docling...")
            result = self.converter.convert(qap_file_path)
            document = result.document
            
            # Export text content
            text_content = document.export_to_markdown()
            print(f"📝 Extracted {len(text_content):,} characters")
            
            # Create comprehensive page mapping
            print("📄 Creating comprehensive page mapping...")
            page_mapping = self._create_comprehensive_page_mapping(document)
            print(f"📊 Mapped {len(page_mapping)} content elements to pages")
            
            # Extract definitions with page intelligence
            print("🎯 Extracting definitions with page intelligence...")
            intelligent_definitions = self._extract_definitions_with_intelligence(
                text_content, state_code, page_mapping, qap_file_path
            )
            print(f"✅ Extracted {len(intelligent_definitions)} definitions with page references")
            
            # Create cross-reference mapping
            print("🔗 Creating cross-reference mapping...")
            cross_references = self._create_cross_reference_mapping(
                intelligent_definitions, text_content, state_code
            )
            print(f"📋 Created {len(cross_references)} cross-references")
            
            # Extract enhanced tables with scoring intelligence
            print("📊 Extracting enhanced tables...")
            enhanced_tables = self._extract_enhanced_tables_with_intelligence(document)
            print(f"📊 Found {len(enhanced_tables)} enhanced tables")
            
            processing_time = time.time() - start_time
            
            # Create intelligent output
            intelligent_output = {
                'state_code': state_code,
                'processing_date': datetime.now().isoformat(),
                'source_file': qap_file_path,
                'processing_time': processing_time,
                'text_length': len(text_content),
                
                # Core definition intelligence
                'definitions_count': len(intelligent_definitions),
                'definitions': intelligent_definitions,
                'cross_references': cross_references,
                
                # Page mapping intelligence
                'page_mapping_count': len(page_mapping),
                'page_mapping': page_mapping,
                
                # Enhanced table intelligence
                'enhanced_tables_count': len(enhanced_tables),
                'enhanced_tables': enhanced_tables,
                
                # Processing metadata
                'processing_method': 'phase_2d_docling_plus',
                'base_phase': 'phase_2c_proven_patterns',
                'enhancement_features': [
                    'pdf_page_mapping',
                    'definition_intelligence', 
                    'cross_reference_mapping',
                    'enhanced_table_extraction',
                    'view_source_functionality'
                ],
                
                # Success metrics
                'success_indicators': {
                    'definitions_with_pages': len([d for d in intelligent_definitions if d.get('pdf_page')]),
                    'cross_references_mapped': len(cross_references),
                    'view_source_links': len([d for d in intelligent_definitions if d.get('pdf_source_link')])
                }
            }
            
            print(f"✅ Definition intelligence processing complete: {processing_time:.1f}s")
            return intelligent_output
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Definition intelligence processing failed for {state_code}: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'processing_time': processing_time,
                'state_code': state_code,
                'processing_method': 'phase_2d_docling_plus'
            }
    
    def _create_comprehensive_page_mapping(self, document) -> Dict[str, Dict[str, Any]]:
        """Create comprehensive page mapping for content elements"""
        
        page_mapping = {}
        
        try:
            # Map document elements with enhanced metadata
            for element in document.elements:
                if hasattr(element, 'text') and element.text:
                    content_key = element.text[:100].strip()
                    
                    if content_key and len(content_key) > 10:
                        # Get page number
                        page_num = None
                        if hasattr(element, 'prov') and element.prov:
                            for prov in element.prov:
                                if hasattr(prov, 'page_no') and prov.page_no is not None:
                                    page_num = int(prov.page_no)
                                    break
                        
                        # Create enhanced mapping entry
                        page_mapping[content_key] = {
                            'page_number': page_num,
                            'element_type': getattr(element, 'type', 'text'),
                            'bbox': getattr(element, 'bbox', None),
                            'confidence': getattr(element, 'confidence', 1.0),
                            'full_text': element.text[:500]  # Store more context
                        }
            
            # Also map text elements separately
            if hasattr(document, 'texts'):
                for text_element in document.texts:
                    if hasattr(text_element, 'text') and text_element.text:
                        content_key = text_element.text[:100].strip()
                        
                        if content_key and len(content_key) > 10 and content_key not in page_mapping:
                            page_num = None
                            if hasattr(text_element, 'prov') and text_element.prov:
                                for prov in text_element.prov:
                                    if hasattr(prov, 'page_no') and prov.page_no is not None:
                                        page_num = int(prov.page_no)
                                        break
                            
                            page_mapping[content_key] = {
                                'page_number': page_num,
                                'element_type': 'text',
                                'full_text': text_element.text[:500]
                            }
                            
        except Exception as e:
            print(f"⚠️ Page mapping warning: {str(e)}")
        
        return page_mapping
    
    def _extract_definitions_with_intelligence(self, text_content: str, state_code: str, 
                                             page_mapping: Dict[str, Dict], qap_file_path: str) -> List[Dict[str, Any]]:
        """Extract definitions with enhanced intelligence and page mapping"""
        
        definitions = []
        definition_id_counter = 1
        
        # Use proven Phase 2C patterns with intelligence enhancement
        for pattern in self.definition_patterns:
            matches = re.findall(pattern['regex'], text_content, re.IGNORECASE)
            
            for match in matches:
                # Extract term and definition based on pattern
                if pattern['name'] == 'section_subsection':
                    subsection, term, definition_text = match
                    section_ref = f"Section ({subsection})"
                elif pattern['name'] in ['simple_means', 'colon_definition', 'quoted_explanation']:
                    term, definition_text = match
                    section_ref = f"{pattern['name'].replace('_', ' ').title()}"
                else:
                    continue
                
                # Quality filters (from Phase 2C success)
                if (len(term) <= 3 or len(definition_text) <= 10 or 
                    term in [d['term'] for d in definitions]):
                    continue
                
                # Additional filter for quoted explanations
                if (pattern['name'] == 'quoted_explanation' and 
                    any(skip_word in definition_text.lower() for skip_word in ['see', 'refer to', 'pursuant to', 'section'])):
                    continue
                
                # Find page number with enhanced intelligence
                page_info = self._find_page_with_intelligence(term, definition_text, page_mapping)
                
                # Detect definition type for enhanced categorization
                definition_type = self._detect_definition_type(term, definition_text)
                
                # Create definition with enhanced intelligence
                definition = {
                    'definition_id': f"{state_code}_intel_{definition_id_counter:04d}",
                    'state_code': state_code,
                    'term': term.strip(),
                    'definition': definition_text.strip(),
                    'section_reference': section_ref,
                    
                    # Page intelligence
                    'pdf_page': page_info['page_number'],
                    'pdf_source_link': self._create_view_source_link(qap_file_path, page_info['page_number']),
                    'page_context': page_info['context'],
                    'page_confidence': page_info['confidence'],
                    
                    # Definition intelligence
                    'definition_type': definition_type,
                    'category': self._categorize_definition_enhanced(term, definition_text),
                    'lihtc_relevance': self._assess_lihtc_relevance(term, definition_text),
                    
                    # Processing metadata
                    'document_year': 2025,
                    'extraction_confidence': pattern['confidence'],
                    'pattern_used': pattern['name'],
                    'pattern_description': pattern['description'],
                    
                    # Cross-reference placeholders (filled later)
                    'federal_references': [],
                    'state_references': [],
                    'qap_references': [],
                    'usage_locations': [],
                    
                    # Enhancement metadata
                    'processing_phase': '2d_docling_plus',
                    'enhancement_date': datetime.now().isoformat()
                }
                
                definitions.append(definition)
                definition_id_counter += 1
        
        return definitions
    
    def _find_page_with_intelligence(self, term: str, definition: str, 
                                   page_mapping: Dict[str, Dict]) -> Dict[str, Any]:
        """Find page number with enhanced intelligence and context"""
        
        # Try multiple matching strategies
        best_match = {
            'page_number': None,
            'confidence': 0.0,
            'context': '',
            'match_method': 'none'
        }
        
        # Strategy 1: Direct term match
        for content_key, mapping_info in page_mapping.items():
            if term.lower() in content_key.lower():
                if mapping_info['page_number'] and mapping_info.get('confidence', 0) > best_match['confidence']:
                    best_match = {
                        'page_number': mapping_info['page_number'],
                        'confidence': 0.9,
                        'context': mapping_info.get('full_text', content_key),
                        'match_method': 'direct_term'
                    }
        
        # Strategy 2: Definition start match
        definition_start = definition[:100].lower()
        for content_key, mapping_info in page_mapping.items():
            if definition_start in content_key.lower():
                if mapping_info['page_number'] and best_match['confidence'] < 0.8:
                    best_match = {
                        'page_number': mapping_info['page_number'],
                        'confidence': 0.8,
                        'context': mapping_info.get('full_text', content_key),
                        'match_method': 'definition_start'
                    }
        
        # Strategy 3: Fuzzy content match
        if best_match['confidence'] < 0.5:
            for content_key, mapping_info in page_mapping.items():
                # Check for partial matches
                term_words = set(term.lower().split())
                content_words = set(content_key.lower().split())
                overlap = len(term_words & content_words)
                
                if overlap > 0 and len(term_words) > 0:
                    fuzzy_confidence = overlap / len(term_words) * 0.6
                    if fuzzy_confidence > best_match['confidence'] and mapping_info['page_number']:
                        best_match = {
                            'page_number': mapping_info['page_number'],
                            'confidence': fuzzy_confidence,
                            'context': mapping_info.get('full_text', content_key),
                            'match_method': 'fuzzy_content'
                        }
        
        return best_match
    
    def _create_view_source_link(self, qap_file_path: str, page_number: Optional[int]) -> Optional[str]:
        """Create view source link for PDF page"""
        
        if not page_number:
            return None
        
        qap_filename = Path(qap_file_path).name
        return f"view_pdf_page/{qap_filename}#page={page_number}"
    
    def _detect_definition_type(self, term: str, definition: str) -> str:
        """Detect the type of definition for enhanced intelligence"""
        
        term_lower = term.lower()
        definition_lower = definition.lower()
        
        # Regulatory definitions
        if any(word in definition_lower for word in ['shall', 'must', 'required', 'compliance']):
            return 'regulatory'
        
        # Calculation definitions
        if any(word in definition_lower for word in ['calculated', 'formula', 'percentage', 'ratio']):
            return 'calculation'
        
        # Process definitions
        if any(word in definition_lower for word in ['process', 'procedure', 'method', 'application']):
            return 'process'
        
        # Criteria definitions
        if any(word in definition_lower for word in ['criteria', 'requirements', 'standards', 'qualifies']):
            return 'criteria'
        
        # Geographic definitions
        if any(word in term_lower for word in ['area', 'region', 'zone', 'district']):
            return 'geographic'
        
        return 'descriptive'
    
    def _categorize_definition_enhanced(self, term: str, definition: str) -> str:
        """Enhanced categorization building on Phase 2C success"""
        
        term_lower = term.lower()
        definition_lower = definition.lower()
        
        # LIHTC program specific
        if any(word in term_lower for word in ['tax credit', 'lihtc', 'section 42', 'credit', 'allocation']):
            return 'lihtc_program'
        
        # Housing and units
        if any(word in term_lower for word in ['housing', 'unit', 'dwelling', 'apartment', 'accessible', 'bedroom']):
            return 'housing_types'
        
        # Income and AMI
        if any(word in term_lower for word in ['income', 'ami', 'median', 'eligible', 'qualification', 'rent']):
            return 'income_requirements'
        
        # Calculations and basis
        if any(word in term_lower for word in ['basis', 'credit', 'calculation', 'formula', 'percent', 'ratio']):
            return 'calculation'
        
        # Compliance and regulations
        if any(word in term_lower for word in ['compliance', 'requirement', 'standard', 'regulation', 'rule']):
            return 'compliance'
        
        # Geographic and location
        if any(word in term_lower for word in ['area', 'region', 'zone', 'district', 'county', 'city', 'qct', 'dda']):
            return 'geographic'
        
        # Financial terms
        if any(word in term_lower for word in ['debt', 'coverage', 'loan', 'financing', 'cost', 'fee']):
            return 'financial'
        
        # Agency and administrative
        if any(word in term_lower for word in ['agency', 'department', 'committee', 'authority', 'administration']):
            return 'agency_administrative'
        
        # Timeline and dates
        if any(word in term_lower for word in ['period', 'deadline', 'date', 'timeline', 'schedule']):
            return 'timeline'
        
        return 'general'
    
    def _assess_lihtc_relevance(self, term: str, definition: str) -> str:
        """Assess LIHTC relevance for prioritization"""
        
        combined_text = f"{term} {definition}".lower()
        
        # High relevance indicators
        high_indicators = [
            'tax credit', 'lihtc', 'section 42', 'qualified basis', 'eligible basis',
            'ami', 'area median income', 'compliance period', 'allocation'
        ]
        
        # Medium relevance indicators  
        medium_indicators = [
            'housing', 'unit', 'rent', 'income', 'affordable', 'development',
            'project', 'tenant', 'financing'
        ]
        
        # Count matches
        high_matches = sum(1 for indicator in high_indicators if indicator in combined_text)
        medium_matches = sum(1 for indicator in medium_indicators if indicator in combined_text)
        
        if high_matches >= 2:
            return 'critical'
        elif high_matches >= 1:
            return 'high'
        elif medium_matches >= 2:
            return 'medium'
        elif medium_matches >= 1:
            return 'low'
        else:
            return 'minimal'
    
    def _create_cross_reference_mapping(self, definitions: List[Dict], text_content: str, 
                                      state_code: str) -> List[Dict[str, Any]]:
        """Create cross-reference mapping for definitions"""
        
        cross_references = []
        
        for definition in definitions:
            term = definition['term'].lower()
            
            # Find where this term is used elsewhere in the QAP
            usage_pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
            usage_matches = list(usage_pattern.finditer(text_content))
            
            # Create cross-references for significant usage
            for i, match in enumerate(usage_matches[:10]):  # Limit to 10 to avoid spam
                context_start = max(0, match.start() - 100)
                context_end = min(len(text_content), match.end() + 100)
                context = text_content[context_start:context_end]
                
                # Skip if it's just the definition itself
                if definition['definition'][:50].lower() in context.lower():
                    continue
                
                cross_ref = {
                    'cross_ref_id': f"{state_code}_xref_{len(cross_references) + 1:04d}",
                    'source_definition_id': definition['definition_id'],
                    'source_term': definition['term'],
                    'usage_context': context.strip(),
                    'usage_position': match.start(),
                    'reference_type': 'internal_usage',
                    'relevance': 'medium'  # Could be enhanced with better analysis
                }
                
                cross_references.append(cross_ref)
        
        return cross_references
    
    def _extract_enhanced_tables_with_intelligence(self, document) -> List[Dict[str, Any]]:
        """Extract tables with enhanced intelligence for QAP processing"""
        
        enhanced_tables = []
        
        try:
            for element in document.elements:
                if hasattr(element, 'type') and element.type == "table":
                    # Get page number
                    page_num = None
                    if hasattr(element, 'prov') and element.prov:
                        for prov in element.prov:
                            if hasattr(prov, 'page_no') and prov.page_no is not None:
                                page_num = int(prov.page_no)
                                break
                    
                    # Extract and analyze table content
                    table_content = getattr(element, 'text', '')
                    table_type = self._classify_qap_table_type(table_content)
                    
                    # Create enhanced table data
                    table_data = {
                        'table_id': f"table_intel_{len(enhanced_tables) + 1:04d}",
                        'page_number': page_num,
                        'content': table_content,
                        'table_type': table_type,
                        'qap_relevance': self._assess_table_qap_relevance(table_content),
                        'bbox': getattr(element, 'bbox', None),
                        'extraction_method': 'enhanced_docling_plus',
                        'view_source_link': f"view_pdf_page/qap.pdf#page={page_num}" if page_num else None,
                        
                        # Intelligence metadata
                        'contains_scoring': 'score' in table_content.lower() or 'points' in table_content.lower(),
                        'contains_financial': '$' in table_content or 'cost' in table_content.lower(),
                        'contains_units': 'unit' in table_content.lower() or 'bedroom' in table_content.lower(),
                    }
                    
                    # Try to extract structured data if available
                    if hasattr(element, 'data') and element.data:
                        table_data['structured_data'] = element.data
                    
                    enhanced_tables.append(table_data)
                    
        except Exception as e:
            print(f"⚠️ Enhanced table extraction warning: {str(e)}")
        
        return enhanced_tables
    
    def _classify_qap_table_type(self, table_content: str) -> str:
        """Classify QAP table type with enhanced intelligence"""
        
        content_lower = table_content.lower()
        
        # Unit mix tables
        if any(term in content_lower for term in ['unit mix', 'bedroom', 'ami', 'rent', 'square feet']):
            return 'unit_mix'
        
        # Scoring matrices
        elif any(term in content_lower for term in ['score', 'points', 'criteria', 'maximum', 'weight']):
            return 'scoring_matrix'
        
        # Financial tables
        elif any(term in content_lower for term in ['cost', 'budget', 'financing', '$', 'basis', 'equity']):
            return 'financial'
        
        # Timeline/schedule tables
        elif any(term in content_lower for term in ['schedule', 'timeline', 'date', 'deadline', 'milestone']):
            return 'timeline'
        
        # Fee tables
        elif any(term in content_lower for term in ['fee', 'charge', 'payment', 'deposit']):
            return 'fee_schedule'
        
        # Set-aside tables
        elif any(term in content_lower for term in ['set aside', 'set-aside', 'allocation', 'priority']):
            return 'set_aside'
        
        else:
            return 'general'
    
    def _assess_table_qap_relevance(self, table_content: str) -> str:
        """Assess table relevance to QAP processing"""
        
        content_lower = table_content.lower()
        
        # Critical tables for LIHTC
        critical_terms = ['score', 'points', 'unit mix', 'ami', 'basis', 'allocation']
        critical_matches = sum(1 for term in critical_terms if term in content_lower)
        
        if critical_matches >= 3:
            return 'critical'
        elif critical_matches >= 2:
            return 'high'  
        elif critical_matches >= 1:
            return 'medium'
        else:
            return 'low'
    
    def save_intelligent_results(self, intelligent_output: Dict[str, Any], output_dir: Path) -> Path:
        """Save intelligent processing results with enhanced metadata"""
        
        output_dir.mkdir(exist_ok=True)
        
        # Create filename with timestamp and intelligence indicator
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{intelligent_output['state_code']}_docling_plus_intel_{timestamp}.json"
        output_file = output_dir / filename
        
        # Save complete intelligent results
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(intelligent_output, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Intelligent results saved: {output_file}")
        return output_file

def main():
    """Test Phase 2D Docling Plus with California QAP"""
    
    print("🏛️ Phase 2D Docling Plus - Definition Intelligence Test")
    print("=" * 70)
    
    # Initialize Docling Plus processor
    processor = Phase2DDoclingPlus()
    
    # Test with California QAP (our biggest success - 84 definitions)
    ca_qap_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/CA/current/CA_2025_QAP_Regulations_Dec_2024.pdf"
    
    if not Path(ca_qap_path).exists():
        print(f"❌ Test file not found: {ca_qap_path}")
        return
    
    # Process with definition intelligence
    result = processor.process_qap_with_definition_intelligence(ca_qap_path, "CA")
    
    if result.get('success', True):
        # Save intelligent results
        output_dir = Path(__file__).parent / "phase_2d_intelligent_output"
        saved_file = processor.save_intelligent_results(result, output_dir)
        
        # Enhanced summary
        print(f"\n🏆 DOCLING PLUS INTELLIGENCE SUCCESS:")
        print(f"✅ Definitions with intelligence: {result['definitions_count']}")
        print(f"✅ Definitions with page mapping: {result['success_indicators']['definitions_with_pages']}")
        print(f"✅ View source links created: {result['success_indicators']['view_source_links']}")
        print(f"✅ Cross-references mapped: {result['success_indicators']['cross_references_mapped']}")
        print(f"✅ Enhanced tables found: {result['enhanced_tables_count']}")
        print(f"⏱️  Processing time: {result['processing_time']:.1f}s")
        
        # Show examples of intelligent definitions
        print(f"\n📋 Intelligent Definition Examples:")
        for i, defn in enumerate(result['definitions'][:3]):
            page_info = f"Page {defn['pdf_page']}" if defn['pdf_page'] else "No page mapping"
            relevance = defn.get('lihtc_relevance', 'unknown')
            print(f"  {i+1}. '{defn['term']}' ({page_info}, {relevance} relevance)")
            print(f"      {defn['definition'][:80]}...")
            if defn.get('pdf_source_link'):
                print(f"      🔗 {defn['pdf_source_link']}")
        
        print(f"\n🎯 Phase 2D Docling Plus test complete!")
        print(f"📊 Ready for full 11-state processing with definition intelligence!")
        
    else:
        print(f"❌ Docling Plus processing failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()