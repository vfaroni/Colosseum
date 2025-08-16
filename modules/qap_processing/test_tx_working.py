#!/usr/bin/env python3
"""
Test Phase 2C Working Patterns on TX only
"""

import json
from pathlib import Path
from datetime import datetime
import re

# Direct Docling import
from docling.document_converter import DocumentConverter

def test_tx_working():
    """Test working patterns on TX QAP"""
    
    print("🏛️ Phase 2C Working Pattern Test - TX Only")
    print("=" * 50)
    
    # Initialize Docling converter
    converter = DocumentConverter()
    
    # Test with Texas QAP
    qap_file = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/data_sets/QAP/TX/current/TX_2025_QAP.pdf")
    
    if not qap_file.exists():
        print(f"❌ QAP file not found: {qap_file}")
        return
    
    print(f"📄 Processing: {qap_file.name}")
    
    # Extract text with Docling
    print(f"🔍 Extracting text with Docling...")
    result = converter.convert(str(qap_file))
    document = result.document
    text_content = document.export_to_markdown()
    
    print(f"📝 Extracted {len(text_content):,} characters")
    
    definitions = []
    definition_id_counter = 1
    
    # Pattern 1: Simple means pattern (Phase 2B success)
    print(f"\n🎯 Pattern 1: Simple Means...")
    simple_pattern = r'"([^"]+)"\s+means\s+([^.]+(?:\.[^.]*){0,2}\.)'
    simple_matches = re.findall(simple_pattern, text_content, re.IGNORECASE)
    print(f"Found {len(simple_matches)} simple matches")
    
    for match in simple_matches:
        term = match[0].strip()
        definition_text = match[1].strip()
        
        if len(term) > 2 and len(definition_text) > 10:
            definitions.append({
                'definition_id': f"TX_def_{definition_id_counter:04d}",
                'state_code': 'TX',
                'term': term,
                'definition': definition_text,
                'pattern_used': 'simple_means'
            })
            definition_id_counter += 1
    
    # Pattern 2: Colon definitions
    print(f"\n🎯 Pattern 2: Colon Definitions...")
    colon_pattern = r'([A-Z][A-Za-z\s]{5,40}):\s*([A-Z][^.]{20,200}\.)'
    colon_matches = re.findall(colon_pattern, text_content)
    print(f"Found {len(colon_matches)} colon matches")
    
    for match in colon_matches:
        term = match[0].strip()
        definition_text = match[1].strip()
        
        if len(term) > 5 and len(definition_text) > 20 and term not in [d['term'] for d in definitions]:
            definitions.append({
                'definition_id': f"TX_def_{definition_id_counter:04d}",
                'state_code': 'TX',
                'term': term,
                'definition': definition_text,
                'pattern_used': 'colon_definition'
            })
            definition_id_counter += 1
    
    # Pattern 3: Quoted explanations
    print(f"\n🎯 Pattern 3: Quoted Explanations...")
    quoted_pattern = r'"([^"]{3,30})"\s+([A-Za-z][^.]{10,150}\.)'
    quoted_matches = re.findall(quoted_pattern, text_content)
    print(f"Found {len(quoted_matches)} quoted matches")
    
    for match in quoted_matches:
        term = match[0].strip()
        definition_text = match[1].strip()
        
        # Filter quality and duplicates
        if (len(term) > 3 and len(definition_text) > 10 and 
            term not in [d['term'] for d in definitions] and
            not any(skip_word in definition_text.lower() for skip_word in ['see', 'refer to', 'pursuant to', 'section'])):
            
            definitions.append({
                'definition_id': f"TX_def_{definition_id_counter:04d}",
                'state_code': 'TX',
                'term': term,
                'definition': definition_text,
                'pattern_used': 'quoted_explanation'
            })
            definition_id_counter += 1
    
    # Results
    print(f"\n🏆 RESULTS:")
    print(f"Total Definitions Found: {len(definitions)}")
    print(f"Phase 2B vs 2C Improvement: {len(definitions)}x (Phase 2B: 1 definition)")
    
    # Show examples
    print(f"\n📋 Examples:")
    for i, defn in enumerate(definitions[:5]):
        print(f"  {i+1}. [{defn['pattern_used']}] '{defn['term']}' = {defn['definition'][:60]}...")
    
    # Save results
    output_file = Path(__file__).parent / "definitions_output_phase2c_working" / f"TX_working_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_file.parent.mkdir(exist_ok=True)
    
    output_data = {
        'state_code': 'TX',
        'processing_date': datetime.now().isoformat(),
        'definitions_count': len(definitions),
        'definitions': definitions,
        'processing_method': 'phase_2c_working_test'
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Saved to: {output_file}")

if __name__ == "__main__":
    test_tx_working()