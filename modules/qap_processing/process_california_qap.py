#!/usr/bin/env python3
"""
Process California QAP - Critical Gap Recovery
Add California definitions to complete Phase 2C coverage
"""

import json
from pathlib import Path
from datetime import datetime
import time
import re

# Direct Docling import
from docling.document_converter import DocumentConverter

def process_california_qap():
    """Process California QAP with proven Phase 2C patterns"""
    
    print("🏛️ California QAP Processing - Critical Gap Recovery")
    print("=" * 60)
    
    # Paths
    base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
    ca_qap_file = base_dir / "data_sets" / "QAP" / "CA" / "current" / "CA_2025_QAP_Regulations_Dec_2024.pdf"
    output_dir = Path(__file__).parent / "definitions_output_phase2d_california"
    output_dir.mkdir(exist_ok=True)
    
    if not ca_qap_file.exists():
        print(f"❌ California QAP not found: {ca_qap_file}")
        return
    
    print(f"📄 Processing: {ca_qap_file.name}")
    
    # Initialize Docling converter
    converter = DocumentConverter()
    start_time = time.time()
    
    try:
        # Extract text with Docling
        print(f"🔍 Extracting text with Docling...")
        result = converter.convert(str(ca_qap_file))
        document = result.document
        text_content = document.export_to_markdown()
        print(f"📝 Extracted {len(text_content):,} characters")
        
        # Extract definitions with 3 proven patterns from Phase 2C
        definitions = []
        definition_id_counter = 1
        
        print(f"🎯 Extracting definitions with 3 proven patterns...")
        
        # Pattern 1: Simple means (Phase 2B/2C success)
        simple_pattern = r'"([^"]+)"\s+means\s+([^.]+(?:\.[^.]*){0,2}\.)'
        simple_matches = re.findall(simple_pattern, text_content, re.IGNORECASE)
        print(f"   Simple means pattern: {len(simple_matches)} matches")
        
        for match in simple_matches:
            term = match[0].strip()
            definition_text = match[1].strip()
            
            if len(term) > 2 and len(definition_text) > 10:
                definitions.append({
                    'definition_id': f"CA_def_{definition_id_counter:04d}",
                    'state_code': 'CA',
                    'term': term,
                    'definition': definition_text,
                    'section_reference': "Simple Definition",
                    'pdf_page': None,
                    'document_year': 2025,
                    'category': _categorize_definition(term, definition_text),
                    'extraction_confidence': 0.8,
                    'pattern_used': 'simple_means'
                })
                definition_id_counter += 1
        
        # Pattern 2: Colon definitions (Phase 2C discovery)
        colon_pattern = r'([A-Z][A-Za-z\s]{5,40}):\s*([A-Z][^.]{20,200}\.)'
        colon_matches = re.findall(colon_pattern, text_content)
        print(f"   Colon definition pattern: {len(colon_matches)} matches")
        
        for match in colon_matches:
            term = match[0].strip()
            definition_text = match[1].strip()
            
            if len(term) > 5 and len(definition_text) > 20 and term not in [d['term'] for d in definitions]:
                definitions.append({
                    'definition_id': f"CA_def_{definition_id_counter:04d}",
                    'state_code': 'CA',
                    'term': term,
                    'definition': definition_text,
                    'section_reference': "Colon Definition", 
                    'pdf_page': None,
                    'document_year': 2025,
                    'category': _categorize_definition(term, definition_text),
                    'extraction_confidence': 0.85,
                    'pattern_used': 'colon_definition'
                })
                definition_id_counter += 1
        
        # Pattern 3: Quoted explanations (Phase 2C innovation)
        quoted_pattern = r'"([^"]{3,30})"\s+([A-Za-z][^.]{10,150}\.)'
        quoted_matches = re.findall(quoted_pattern, text_content)
        print(f"   Quoted explanation pattern: {len(quoted_matches)} raw matches")
        
        filtered_quoted = 0
        for match in quoted_matches:
            term = match[0].strip()
            definition_text = match[1].strip()
            
            # Quality filter (from Phase 2C)
            if (len(term) > 3 and len(definition_text) > 10 and 
                term not in [d['term'] for d in definitions] and
                not any(skip_word in definition_text.lower() for skip_word in ['see', 'refer to', 'pursuant to', 'section'])):
                
                definitions.append({
                    'definition_id': f"CA_def_{definition_id_counter:04d}",
                    'state_code': 'CA',
                    'term': term,
                    'definition': definition_text,
                    'section_reference': "Quoted Term",
                    'pdf_page': None,
                    'document_year': 2025,
                    'category': _categorize_definition(term, definition_text),
                    'extraction_confidence': 0.75,
                    'pattern_used': 'quoted_explanation'
                })
                definition_id_counter += 1
                filtered_quoted += 1
        
        print(f"   Quoted explanations (filtered): {filtered_quoted} high-quality matches")
        
        # CTCAC-specific pattern: Section 10302 definitions format
        # Pattern: (a) Term. Definition text...
        ctcac_pattern = r'\(([a-z]{1,3})\)\s+([A-Z][A-Za-z\s]{5,50})\.\s+([^.]+(?:\.[^.]*){0,3}\.)'
        ctcac_matches = re.findall(ctcac_pattern, text_content)
        print(f"   CTCAC Section 10302 pattern: {len(ctcac_matches)} matches")
        
        for match in ctcac_matches:
            subsection = match[0].strip()
            term = match[1].strip()
            definition_text = match[2].strip()
            
            if len(term) > 5 and len(definition_text) > 20 and term not in [d['term'] for d in definitions]:
                definitions.append({
                    'definition_id': f"CA_def_{definition_id_counter:04d}",
                    'state_code': 'CA',
                    'term': term,
                    'definition': definition_text,
                    'section_reference': f"Section 10302({subsection})",
                    'pdf_page': None,
                    'document_year': 2025,
                    'category': _categorize_definition(term, definition_text),
                    'extraction_confidence': 0.95,
                    'pattern_used': 'ctcac_section_10302'
                })
                definition_id_counter += 1
        
        # Save results
        processing_time = time.time() - start_time
        output_file = output_dir / f"CA_definitions_phase2d_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_data = {
            'state_code': 'CA',
            'processing_date': datetime.now().isoformat(),
            'source_file': str(ca_qap_file),
            'definitions_count': len(definitions),
            'text_length': len(text_content),
            'processing_time': processing_time,
            'definitions': definitions,
            'processing_method': 'phase_2d_california_recovery',
            'patterns_used': ['simple_means', 'colon_definition', 'quoted_explanation', 'ctcac_section_10302']
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Results
        print(f"\n🏆 CALIFORNIA PROCESSING COMPLETE:")
        print(f"✅ Definitions extracted: {len(definitions)}")
        print(f"⏱️  Processing time: {processing_time:.1f}s")
        print(f"📝 Text processed: {len(text_content):,} characters")
        print(f"📁 Saved to: {output_file}")
        
        # Pattern breakdown
        pattern_counts = {}
        for defn in definitions:
            pattern = defn['pattern_used']
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        print(f"\n📊 Pattern Breakdown:")
        for pattern, count in pattern_counts.items():
            print(f"   {pattern}: {count} definitions")
        
        # Update Phase 2C totals
        phase_2c_total = 91  # From previous Phase 2C summary
        new_total = phase_2c_total + len(definitions)
        
        print(f"\n🚀 UPDATED TOTALS:")
        print(f"   Phase 2C (10 states): {phase_2c_total} definitions")
        print(f"   California addition: {len(definitions)} definitions")
        print(f"   New total (11 states): {new_total} definitions")
        print(f"   Improvement factor: {new_total}x over original Phase 2B")
        
        # Top 5 examples
        print(f"\n📋 Top 5 California Definitions:")
        for i, defn in enumerate(definitions[:5]):
            print(f"   {i+1}. [{defn['pattern_used']}] '{defn['term']}' - {defn['definition'][:60]}...")
        
        return {
            'success': True,
            'definitions_count': len(definitions),
            'processing_time': processing_time,
            'text_length': len(text_content),
            'new_total': new_total,
            'output_file': str(output_file)
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"❌ California processing failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'processing_time': processing_time
        }

def _categorize_definition(term: str, definition: str) -> str:
    """Enhanced categorization for QAP-specific definitions"""
    
    term_lower = term.lower()
    definition_lower = definition.lower()
    
    # LIHTC-specific categories
    if any(word in term_lower for word in ['tax credit', 'lihtc', 'section 42', 'credit']):
        return 'lihtc_program'
    
    # Housing types
    if any(word in term_lower for word in ['housing', 'unit', 'dwelling', 'apartment', 'accessible']):
        return 'housing_types'
    
    # Income requirements  
    if any(word in term_lower for word in ['income', 'ami', 'median', 'eligible', 'qualification']):
        return 'income_requirements'
    
    # Calculations
    if any(word in term_lower for word in ['basis', 'credit', 'calculation', 'formula', 'percent', 'ratio']):
        return 'calculation'
    
    # Compliance
    if any(word in term_lower for word in ['compliance', 'requirement', 'standard', 'regulation', 'rule']):
        return 'compliance'
    
    # Geographic
    if any(word in term_lower for word in ['area', 'region', 'zone', 'district', 'county', 'city']):
        return 'geographic'
    
    # Financial
    if any(word in term_lower for word in ['debt', 'coverage', 'loan', 'financing', 'cost']):
        return 'financial'
    
    # CTCAC-specific
    if any(word in term_lower for word in ['ctcac', 'committee', 'allocation', 'reservation']):
        return 'ctcac_specific'
    
    return 'general'

if __name__ == "__main__":
    result = process_california_qap()
    
    if result['success']:
        print(f"\n🏛️ CALIFORNIA INTEGRATION COMPLETE!")
        print(f"🎯 Ready for IBM Components Research Review!")
        print(f"📊 Total System: {result['new_total']} definitions across 11 states")
    else:
        print(f"\n❌ California integration failed: {result.get('error', 'Unknown error')}")