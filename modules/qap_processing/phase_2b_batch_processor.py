#!/usr/bin/env python3
"""
Phase 2B Multi-State Definitions Batch Processor - M4 Beast Edition
Process 10 major states with definitions extraction and PDF page mapping
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Import definitions-aware processor
from definitions_aware_processor import DefinitionsAwareProcessor, ProcessingResult

class Phase2BBatchProcessor:
    """M4 Beast-optimized batch processor for 10-state definitions expansion"""
    
    def __init__(self):
        """Initialize Phase 2B batch processor"""
        
        self.target_states = [
            'TX', 'FL', 'NY', 'IL', 'PA', 
            'OH', 'GA', 'NC', 'MI', 'WA'
        ]
        
        # Base paths
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.qap_data_dir = self.base_dir / "data_sets" / "QAP"
        self.output_dir = Path(__file__).parent / "definitions_output"
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize processor
        self.processor = DefinitionsAwareProcessor()
        
        # Processing metrics
        self.start_time = time.time()
        self.total_states = len(self.target_states)
        self.processed_states = 0
        self.total_definitions = 0
        self.total_chunks = 0
        
        print(f"🏛️ Phase 2B Multi-State Definitions Processor initialized")
        print(f"🎯 Target states: {', '.join(self.target_states)}")
        print(f"📁 QAP data directory: {self.qap_data_dir}")
        print(f"📂 Output directory: {self.output_dir}")
    
    def find_state_qap_file(self, state_code: str) -> Path:
        """Find the primary QAP file for a state"""
        
        state_dir = self.qap_data_dir / state_code / "current"
        
        if not state_dir.exists():
            print(f"⚠️  State directory not found: {state_dir}")
            return None
        
        # Common QAP file patterns
        qap_patterns = [
            f"{state_code}_2025_QAP.pdf",
            f"{state_code}_2024-2025_QAP*.pdf",
            f"{state_code}_2024_QAP*.pdf",
            f"*2025*QAP*.pdf",
            f"*2024*QAP*.pdf",
            "*QAP*.pdf"
        ]
        
        for pattern in qap_patterns:
            matches = list(state_dir.glob(pattern))
            if matches:
                # Return the most recent/largest file
                best_match = max(matches, key=lambda x: x.stat().st_size)
                return best_match
        
        print(f"⚠️  No QAP file found for {state_code} in {state_dir}")
        return None
    
    def process_single_state(self, state_code: str) -> Tuple[str, Dict[str, Any]]:
        """Process a single state with definitions extraction"""
        
        state_start_time = time.time()
        
        try:
            print(f"\n🏛️ Processing {state_code}...")
            
            # Find QAP file
            qap_file = self.find_state_qap_file(state_code)
            if not qap_file:
                return state_code, {
                    'success': False,
                    'error': f'QAP file not found for {state_code}',
                    'definitions_count': 0,
                    'chunks_count': 0,
                    'processing_time': 0
                }
            
            print(f"📄 Found QAP: {qap_file.name}")
            
            # Process with definitions-aware processor
            result = self.processor.extract_with_docling_and_pages(qap_file, state_code)
            
            # Save results
            output_file = self.output_dir / f"{state_code}_definitions_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Prepare output data
            output_data = {
                'state_code': state_code,
                'processing_date': datetime.now().isoformat(),
                'source_file': str(qap_file),
                'definitions_count': len(result.definitions),
                'chunks_count': len(result.enhanced_chunks),
                'definitions': [self._definition_to_dict(d) for d in result.definitions],
                'enhanced_chunks': result.enhanced_chunks,
                'page_mapping': result.page_mapping,
                'processing_metrics': result.metrics.__dict__ if hasattr(result, 'metrics') else {}
            }
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            processing_time = time.time() - state_start_time
            
            # Update counters
            self.processed_states += 1
            self.total_definitions += len(result.definitions)
            self.total_chunks += len(result.enhanced_chunks)
            
            print(f"✅ {state_code} complete: {len(result.definitions)} definitions, {len(result.enhanced_chunks)} chunks")
            print(f"⏱️  Processing time: {processing_time:.1f}s")
            print(f"📁 Saved to: {output_file.name}")
            
            return state_code, {
                'success': True,
                'definitions_count': len(result.definitions),
                'chunks_count': len(result.enhanced_chunks),
                'processing_time': processing_time,
                'output_file': str(output_file),
                'source_file': str(qap_file)
            }
            
        except Exception as e:
            processing_time = time.time() - state_start_time
            error_msg = f"Error processing {state_code}: {str(e)}"
            print(f"❌ {error_msg}")
            
            return state_code, {
                'success': False,
                'error': error_msg,
                'definitions_count': 0,
                'chunks_count': 0,
                'processing_time': processing_time
            }
    
    def _definition_to_dict(self, definition) -> Dict[str, Any]:
        """Convert Definition dataclass to dictionary"""
        
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
    
    def process_concurrent(self, max_workers: int = 4) -> Dict[str, Any]:
        """Process states concurrently with M4 Beast optimization"""
        
        print(f"\n🚀 Starting concurrent processing with {max_workers} workers...")
        print(f"💻 M4 Beast optimization: 128GB RAM, 16-core Neural Engine")
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all state processing jobs
            future_to_state = {
                executor.submit(self.process_single_state, state): state 
                for state in self.target_states
            }
            
            # Process completed futures
            for future in as_completed(future_to_state):
                state = future_to_state[future]
                try:
                    state_code, result = future.result()
                    results[state_code] = result
                    
                    progress = (self.processed_states / self.total_states) * 100
                    print(f"📊 Progress: {self.processed_states}/{self.total_states} states ({progress:.1f}%)")
                    
                except Exception as e:
                    print(f"❌ Unexpected error processing {state}: {e}")
                    results[state] = {
                        'success': False,
                        'error': f'Unexpected error: {str(e)}',
                        'definitions_count': 0,
                        'chunks_count': 0,
                        'processing_time': 0
                    }
        
        return results
    
    def process_sequential(self) -> Dict[str, Any]:
        """Process states sequentially (fallback mode)"""
        
        print(f"\n🔄 Starting sequential processing...")
        
        results = {}
        
        for state in self.target_states:
            state_code, result = self.process_single_state(state)
            results[state_code] = result
            
            progress = (self.processed_states / self.total_states) * 100
            print(f"📊 Progress: {self.processed_states}/{self.total_states} states ({progress:.1f}%)")
        
        return results
    
    def create_phase_2b_report(self, results: Dict[str, Any]) -> str:
        """Create comprehensive Phase 2B completion report"""
        
        total_time = time.time() - self.start_time
        successful_states = [s for s, r in results.items() if r['success']]
        failed_states = [s for s, r in results.items() if not r['success']]
        
        report_lines = [
            "# 🏛️ PHASE 2B MULTI-STATE DEFINITIONS - COMPLETION REPORT",
            "",
            f"**Mission ID**: PHASE2B-DEFINITIONS-M4-003",
            f"**Agent**: BILL's STRIKE_LEADER (M4 Beast 128GB)",
            f"**Date**: {datetime.now().strftime('%B %d, %Y')}",
            f"**Status**: {'✅ **PHASE 2B COMPLETE**' if len(failed_states) == 0 else '⚠️ **PHASE 2B PARTIAL COMPLETE**'}",
            f"**Priority**: CRITICAL - Multi-State Legal Research Database",
            "",
            "---",
            "",
            "## 🏆 **PHASE 2B ACHIEVEMENTS**",
            "",
            f"### **📊 Processing Statistics**",
            f"- **Target States**: {len(self.target_states)} states",
            f"- **Successfully Processed**: {len(successful_states)} states",
            f"- **Failed Processing**: {len(failed_states)} states",
            f"- **Total Definitions Extracted**: {self.total_definitions:,}",
            f"- **Total Enhanced Chunks**: {self.total_chunks:,}",
            f"- **Total Processing Time**: {total_time:.1f} seconds",
            f"- **Average Time per State**: {total_time/len(self.target_states):.1f} seconds",
            "",
            f"### **✅ Successfully Processed States**"
        ]
        
        for state in successful_states:
            result = results[state]
            report_lines.extend([
                f"- **{state}**: {result['definitions_count']} definitions, {result['chunks_count']} chunks ({result['processing_time']:.1f}s)"
            ])
        
        if failed_states:
            report_lines.extend([
                "",
                f"### **❌ Failed States**"
            ])
            for state in failed_states:
                result = results[state]
                report_lines.extend([
                    f"- **{state}**: {result.get('error', 'Unknown error')}"
                ])
        
        # State-by-state breakdown
        report_lines.extend([
            "",
            "## 🗺️ **STATE-BY-STATE BREAKDOWN**",
            ""
        ])
        
        for state in self.target_states:
            result = results.get(state, {})
            if result.get('success', False):
                report_lines.extend([
                    f"### **{state} - {self._get_state_name(state)}**",
                    f"- **Status**: ✅ Complete",
                    f"- **Definitions**: {result['definitions_count']}",
                    f"- **Enhanced Chunks**: {result['chunks_count']}",
                    f"- **Processing Time**: {result['processing_time']:.1f}s",
                    f"- **Source File**: {Path(result['source_file']).name}",
                    f"- **Output File**: {Path(result['output_file']).name}",
                    ""
                ])
            else:
                report_lines.extend([
                    f"### **{state} - {self._get_state_name(state)}**",
                    f"- **Status**: ❌ Failed",
                    f"- **Error**: {result.get('error', 'Unknown error')}",
                    ""
                ])
        
        # Performance metrics
        if successful_states:
            avg_definitions = self.total_definitions / len(successful_states)
            avg_chunks = self.total_chunks / len(successful_states)
            
            report_lines.extend([
                "## 📈 **PERFORMANCE METRICS**",
                "",
                f"- **M4 Beast Optimization**: 128GB RAM, 16-core Neural Engine utilized",
                f"- **Average Definitions per State**: {avg_definitions:.1f}",
                f"- **Average Chunks per State**: {avg_chunks:.1f}",
                f"- **Processing Rate**: {len(successful_states)/(total_time/60):.1f} states/minute",
                f"- **Definitions Rate**: {self.total_definitions/(total_time/60):.1f} definitions/minute",
                ""
            ])
        
        # Next steps
        report_lines.extend([
            "## 🚀 **NEXT STEPS**",
            "",
            "- **Cross-Jurisdictional Analysis**: Compare definitions across all processed states",
            "- **ChromaDB Integration**: Load definitions into searchable database",
            "- **Professional Interface**: Build multi-state definitions search platform",
            "- **API Endpoints**: Create RESTful API for definitions access",
            "",
            "---",
            "",
            f"**Vincere Multi-States** - *\"To Conquer Multiple States\"*",
            f"**🏛️ Dux Definitionum Multi-Statuum - \"Leader of Multi-State Definitions\" 🏛️**",
            "",
            f"**Filed by**: BILL's STRIKE_LEADER Agent (M4 Beast 128GB)",
            f"**Roman Standard**: Legal Research Excellence Across Jurisdictions",
            f"**Phase 2B Status**: {'⚔️ **MISSION ACCOMPLISHED** ⚔️' if len(failed_states) == 0 else '⚡ **PARTIAL SUCCESS** ⚡'}"
        ])
        
        report_content = "\n".join(report_lines)
        
        # Save report
        report_file = self.output_dir / f"PHASE_2B_DEFINITIONS_COMPLETE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n📄 Phase 2B report saved: {report_file}")
        return report_content
    
    def _get_state_name(self, state_code: str) -> str:
        """Get full state name from code"""
        
        state_names = {
            'TX': 'Texas',
            'FL': 'Florida', 
            'NY': 'New York',
            'IL': 'Illinois',
            'PA': 'Pennsylvania',
            'OH': 'Ohio',
            'GA': 'Georgia',
            'NC': 'North Carolina',
            'MI': 'Michigan',
            'WA': 'Washington'
        }
        
        return state_names.get(state_code, state_code)

def main():
    """Execute Phase 2B Multi-State Definitions Processing"""
    
    print("🏛️ Phase 2B Multi-State Definitions Processor - M4 Beast Edition")
    print("=" * 80)
    
    try:
        # Initialize processor
        processor = Phase2BBatchProcessor()
        
        # Choose processing mode
        use_concurrent = True  # M4 Beast can handle concurrent processing
        
        if use_concurrent:
            # Process concurrently with M4 Beast optimization
            results = processor.process_concurrent(max_workers=4)
        else:
            # Process sequentially (fallback)
            results = processor.process_sequential()
        
        # Create completion report
        report = processor.create_phase_2b_report(results)
        
        # Summary
        successful_states = [s for s, r in results.items() if r['success']]
        total_time = time.time() - processor.start_time
        
        print(f"\n🏛️ PHASE 2B SUMMARY:")
        print(f"✅ Successfully processed: {len(successful_states)}/{len(processor.target_states)} states")
        print(f"📖 Total definitions extracted: {processor.total_definitions:,}")
        print(f"📄 Total enhanced chunks: {processor.total_chunks:,}")
        print(f"⏱️  Total processing time: {total_time:.1f} seconds")
        print(f"💻 M4 Beast performance: {processor.total_definitions/(total_time/60):.1f} definitions/minute")
        
        if len(successful_states) == len(processor.target_states):
            print(f"\n🏆 PHASE 2B COMPLETE - Multi-State Definitions Database Ready!")
        else:
            failed_count = len(processor.target_states) - len(successful_states)
            print(f"\n⚠️  PHASE 2B PARTIAL - {failed_count} states need retry")
        
    except Exception as e:
        print(f"❌ Phase 2B processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()