#!/usr/bin/env python3
"""
Phase 2C All States - Process all 10 states with proven patterns
"""

import json
from pathlib import Path
from datetime import datetime
import time
import re

# Direct Docling import
from docling.document_converter import DocumentConverter

def process_all_states():
    """Process all 10 states with proven patterns"""
    
    print("🏛️ Phase 2C All States - Proven Patterns")
    print("=" * 50)
    
    # Target states
    target_states = ['TX', 'FL', 'NY', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI', 'WA']
    
    # Paths
    base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
    qap_data_dir = base_dir / "data_sets" / "QAP"
    output_dir = Path(__file__).parent / "definitions_output_phase2c_all"
    output_dir.mkdir(exist_ok=True)
    
    # Initialize Docling converter
    converter = DocumentConverter()
    
    # Tracking
    results = {}
    total_definitions = 0
    start_time = time.time()
    
    for state_code in target_states:
        print(f"\n🎯 Processing {state_code}...")
        state_start_time = time.time()
        
        try:
            # Find QAP file
            state_dir = qap_data_dir / state_code / "current"
            if not state_dir.exists():
                print(f"❌ {state_code}: No current directory")
                results[state_code] = {'success': False, 'error': 'No current directory', 'definitions_count': 0}
                continue
            
            # Find PDF files
            pdf_files = list(state_dir.glob("*.pdf"))
            if not pdf_files:
                print(f"❌ {state_code}: No PDF files found")
                results[state_code] = {'success': False, 'error': 'No PDF files', 'definitions_count': 0}
                continue
            
            # Use largest PDF file
            qap_file = max(pdf_files, key=lambda x: x.stat().st_size)
            print(f"📄 Found: {qap_file.name}")
            
            # Extract text with Docling
            result = converter.convert(str(qap_file))
            document = result.document
            text_content = document.export_to_markdown()
            print(f"📝 Extracted {len(text_content):,} characters")
            
            # Extract definitions with 3 proven patterns
            definitions = []
            definition_id_counter = 1
            
            # Pattern 1: Simple means
            simple_pattern = r'"([^"]+)"\s+means\s+([^.]+(?:\.[^.]*){0,2}\.)'
            simple_matches = re.findall(simple_pattern, text_content, re.IGNORECASE)
            
            for match in simple_matches:
                term = match[0].strip()
                definition_text = match[1].strip()
                
                if len(term) > 2 and len(definition_text) > 10:
                    definitions.append({
                        'definition_id': f"{state_code}_def_{definition_id_counter:04d}",
                        'state_code': state_code,
                        'term': term,
                        'definition': definition_text,
                        'pattern_used': 'simple_means'
                    })
                    definition_id_counter += 1
            
            # Pattern 2: Colon definitions
            colon_pattern = r'([A-Z][A-Za-z\s]{5,40}):\s*([A-Z][^.]{20,200}\.)'
            colon_matches = re.findall(colon_pattern, text_content)
            
            for match in colon_matches:
                term = match[0].strip()
                definition_text = match[1].strip()
                
                if len(term) > 5 and len(definition_text) > 20 and term not in [d['term'] for d in definitions]:
                    definitions.append({
                        'definition_id': f"{state_code}_def_{definition_id_counter:04d}",
                        'state_code': state_code,
                        'term': term,
                        'definition': definition_text,
                        'pattern_used': 'colon_definition'
                    })
                    definition_id_counter += 1
            
            # Pattern 3: Quoted explanations (filtered)
            quoted_pattern = r'"([^"]{3,30})"\s+([A-Za-z][^.]{10,150}\.)'
            quoted_matches = re.findall(quoted_pattern, text_content)
            
            for match in quoted_matches:
                term = match[0].strip()
                definition_text = match[1].strip()
                
                # Quality filter
                if (len(term) > 3 and len(definition_text) > 10 and 
                    term not in [d['term'] for d in definitions] and
                    not any(skip_word in definition_text.lower() for skip_word in ['see', 'refer to', 'pursuant to', 'section'])):
                    
                    definitions.append({
                        'definition_id': f"{state_code}_def_{definition_id_counter:04d}",
                        'state_code': state_code,
                        'term': term,
                        'definition': definition_text,
                        'pattern_used': 'quoted_explanation'
                    })
                    definition_id_counter += 1
            
            # Save results
            output_file = output_dir / f"{state_code}_definitions_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            output_data = {
                'state_code': state_code,
                'processing_date': datetime.now().isoformat(),
                'source_file': str(qap_file),
                'definitions_count': len(definitions),
                'text_length': len(text_content),
                'definitions': definitions,
                'processing_method': 'phase_2c_proven_patterns'
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            # Results
            processing_time = time.time() - state_start_time
            print(f"✅ {state_code}: {len(definitions)} definitions ({processing_time:.1f}s)")
            
            results[state_code] = {
                'success': True,
                'definitions_count': len(definitions),
                'processing_time': processing_time,
                'text_length': len(text_content)
            }
            
            total_definitions += len(definitions)
            
        except Exception as e:
            processing_time = time.time() - state_start_time
            print(f"❌ {state_code}: Error - {str(e)}")
            results[state_code] = {
                'success': False, 
                'error': str(e), 
                'definitions_count': 0,
                'processing_time': processing_time
            }
    
    # Final summary
    total_time = time.time() - start_time
    successful_states = [s for s, r in results.items() if r['success']]
    
    print(f"\n🏛️ PHASE 2C ALL STATES SUMMARY:")
    print(f"✅ Successfully processed: {len(successful_states)}/{len(target_states)} states")
    print(f"📖 Total definitions extracted: {total_definitions:,}")
    print(f"⏱️  Total processing time: {total_time:.1f} seconds")
    print(f"🚀 Phase 2B vs 2C Improvement: {total_definitions}x (Phase 2B: 1 definition)")
    
    # Top states
    print(f"\n🏅 Top Performing States:")
    top_states = sorted([(s, r['definitions_count']) for s, r in results.items() if r['success']], 
                       key=lambda x: x[1], reverse=True)
    
    for i, (state, count) in enumerate(top_states[:5]):
        print(f"  {i+1}. {state}: {count} definitions")
    
    # Save summary
    summary_file = output_dir / f"PHASE_2C_ALL_STATES_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary_data = {
        'processing_date': datetime.now().isoformat(),
        'total_states': len(target_states),
        'successful_states': len(successful_states),
        'total_definitions': total_definitions,
        'total_time': total_time,
        'improvement_factor': total_definitions,
        'results': results
    }
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Summary saved: {summary_file}")
    print(f"\n🏆 PHASE 2C ALL STATES COMPLETE!")

if __name__ == "__main__":
    process_all_states()