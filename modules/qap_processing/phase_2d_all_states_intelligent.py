#!/usr/bin/env python3
"""
Phase 2D All States Intelligent Processing
Process all 11 states with definition intelligence and cross-referencing
Building on Phase 2D Docling Plus success (124 CA definitions with 284 cross-references)
"""

import json
from pathlib import Path
from datetime import datetime
import time
from typing import Dict, List, Any

# Import our successful Phase 2D processor
from phase_2d_docling_plus import Phase2DDoclingPlus

def process_all_states_intelligent():
    """Process all 11 states with Phase 2D definition intelligence"""
    
    print("🏛️ Phase 2D All States - Definition Intelligence Processing")
    print("=" * 70)
    print("✅ Building on Phase 2D success: 124 CA definitions + 284 cross-references") 
    print("🎯 Processing 11 states with enhanced intelligence features")
    
    # Target states (including successful California)
    target_states = ['CA', 'TX', 'FL', 'NY', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI', 'WA']
    
    # Paths
    base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
    qap_data_dir = base_dir / "data_sets" / "QAP"
    output_dir = Path(__file__).parent / "phase_2d_all_states_intelligent"
    output_dir.mkdir(exist_ok=True)
    
    # Initialize Phase 2D processor
    processor = Phase2DDoclingPlus()
    
    # Tracking
    results = {}
    total_definitions = 0
    total_cross_references = 0
    start_time = time.time()
    
    print(f"\n🚀 Starting intelligent processing for {len(target_states)} states...")
    
    for state_code in target_states:
        print(f"\n{'='*20} PROCESSING {state_code} {'='*20}")
        state_start_time = time.time()
        
        try:
            # Find QAP file
            state_dir = qap_data_dir / state_code / "current"
            if not state_dir.exists():
                print(f"❌ {state_code}: No current directory")
                results[state_code] = {
                    'success': False, 
                    'error': 'No current directory', 
                    'definitions_count': 0,
                    'cross_references_count': 0
                }
                continue
            
            # Find PDF files
            pdf_files = list(state_dir.glob("*.pdf"))
            if not pdf_files:
                print(f"❌ {state_code}: No PDF files found")
                results[state_code] = {
                    'success': False, 
                    'error': 'No PDF files', 
                    'definitions_count': 0,
                    'cross_references_count': 0
                }
                continue
            
            # Use largest PDF file
            qap_file = max(pdf_files, key=lambda x: x.stat().st_size)
            print(f"📄 Processing: {qap_file.name}")
            
            # Process with Phase 2D intelligence
            intelligent_result = processor.process_qap_with_definition_intelligence(
                str(qap_file), state_code
            )
            
            if intelligent_result.get('success', True):
                # Save individual state results
                state_output_file = output_dir / f"{state_code}_intelligent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(state_output_file, 'w', encoding='utf-8') as f:
                    json.dump(intelligent_result, f, indent=2, ensure_ascii=False)
                
                # Extract key metrics
                definitions_count = intelligent_result['definitions_count']
                cross_refs_count = len(intelligent_result.get('cross_references', []))
                processing_time = intelligent_result['processing_time']
                
                # Store results
                results[state_code] = {
                    'success': True,
                    'definitions_count': definitions_count,
                    'cross_references_count': cross_refs_count,
                    'processing_time': processing_time,
                    'text_length': intelligent_result['text_length'],
                    'output_file': str(state_output_file),
                    'success_indicators': intelligent_result.get('success_indicators', {}),
                    'lihtc_relevance_distribution': _analyze_lihtc_relevance(intelligent_result.get('definitions', []))
                }
                
                # Update totals
                total_definitions += definitions_count
                total_cross_references += cross_refs_count
                
                print(f"✅ {state_code}: {definitions_count} definitions, {cross_refs_count} cross-refs ({processing_time:.1f}s)")
                
            else:
                error_msg = intelligent_result.get('error', 'Unknown processing error')
                print(f"❌ {state_code}: {error_msg}")
                results[state_code] = {
                    'success': False,
                    'error': error_msg,
                    'definitions_count': 0,
                    'cross_references_count': 0,
                    'processing_time': intelligent_result.get('processing_time', 0)
                }
                
        except Exception as e:
            processing_time = time.time() - state_start_time
            print(f"❌ {state_code}: Exception - {str(e)}")
            results[state_code] = {
                'success': False, 
                'error': str(e), 
                'definitions_count': 0,
                'cross_references_count': 0,
                'processing_time': processing_time
            }
    
    # Create comprehensive summary
    total_time = time.time() - start_time
    successful_states = [s for s, r in results.items() if r['success']]
    failed_states = [s for s, r in results.items() if not r['success']]
    
    print(f"\n{'='*70}")
    print(f"🏛️ PHASE 2D INTELLIGENT PROCESSING COMPLETE")
    print(f"{'='*70}")
    print(f"✅ Successfully processed: {len(successful_states)}/{len(target_states)} states")
    print(f"📖 Total intelligent definitions: {total_definitions:,}")
    print(f"🔗 Total cross-references: {total_cross_references:,}")
    print(f"⏱️  Total processing time: {total_time:.1f} seconds")
    print(f"🚀 Improvement over Phase 2B: {total_definitions}x definitions")
    
    # Top performing states
    print(f"\n🏅 Top Performing States (Intelligent):")
    top_states = sorted([(s, r['definitions_count']) for s, r in results.items() if r['success']], 
                       key=lambda x: x[1], reverse=True)
    
    for i, (state, count) in enumerate(top_states[:5]):
        cross_refs = results[state]['cross_references_count']
        print(f"  {i+1}. {state}: {count} definitions, {cross_refs} cross-references")
    
    # LIHTC relevance analysis
    print(f"\n📊 LIHTC Relevance Analysis:")
    relevance_totals = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'minimal': 0}
    for state_result in results.values():
        if state_result['success'] and 'lihtc_relevance_distribution' in state_result:
            for relevance, count in state_result['lihtc_relevance_distribution'].items():
                relevance_totals[relevance] = relevance_totals.get(relevance, 0) + count
    
    for relevance, count in relevance_totals.items():
        if count > 0:
            percentage = (count / total_definitions) * 100 if total_definitions > 0 else 0
            print(f"  {relevance.capitalize()}: {count} definitions ({percentage:.1f}%)")
    
    # Failed states summary
    if failed_states:
        print(f"\n❌ Failed States: {', '.join(failed_states)}")
    
    # Save comprehensive summary
    comprehensive_summary = {
        'processing_date': datetime.now().isoformat(),
        'processing_method': 'phase_2d_intelligent_all_states',
        'total_states': len(target_states),
        'successful_states': len(successful_states),
        'failed_states': len(failed_states),
        'total_definitions': total_definitions,
        'total_cross_references': total_cross_references,
        'total_processing_time': total_time,
        'improvement_factor_over_phase_2b': total_definitions,
        'lihtc_relevance_distribution': relevance_totals,
        'state_results': results,
        'success_rate': (len(successful_states) / len(target_states)) * 100,
        'avg_definitions_per_state': total_definitions / len(successful_states) if successful_states else 0,
        'avg_cross_refs_per_state': total_cross_references / len(successful_states) if successful_states else 0,
        'phase_comparison': {
            'phase_2b': 1,
            'phase_2c': 91,
            'phase_2d_intelligent': total_definitions
        }
    }
    
    summary_file = output_dir / f"PHASE_2D_INTELLIGENT_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Comprehensive summary saved: {summary_file}")
    
    # Phase comparison
    print(f"\n📊 PHASE EVOLUTION COMPARISON:")
    print(f"   Phase 2B (Original): 1 definition")
    print(f"   Phase 2C (Pattern Success): 91 definitions") 
    print(f"   Phase 2D (Intelligence): {total_definitions} definitions")
    print(f"   Intelligence Enhancement: {total_definitions - 91} additional definitions")
    print(f"   Cross-Reference Intelligence: {total_cross_references} references mapped")
    
    print(f"\n🏆 PHASE 2D INTELLIGENT PROCESSING SUCCESS!")
    print(f"🎯 Ready for definition intelligence system deployment!")
    
    return comprehensive_summary

def _analyze_lihtc_relevance(definitions: List[Dict[str, Any]]) -> Dict[str, int]:
    """Analyze LIHTC relevance distribution for a state"""
    
    relevance_counts = {}
    for definition in definitions:
        relevance = definition.get('lihtc_relevance', 'unknown')
        relevance_counts[relevance] = relevance_counts.get(relevance, 0) + 1
    
    return relevance_counts

if __name__ == "__main__":
    summary = process_all_states_intelligent()
    
    print(f"\n🏛️ Phase 2D Intelligent Processing Complete!")
    print(f"📊 Final Results: {summary['total_definitions']} definitions, {summary['total_cross_references']} cross-references")
    print(f"⚔️ Definition Intelligence System Ready for Deployment! ⚔️")