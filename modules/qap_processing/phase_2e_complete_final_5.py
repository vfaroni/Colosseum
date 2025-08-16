#!/usr/bin/env python3
"""
Phase 2E Final 5: Complete the missing jurisdictions
Process LA, MT, NV, GU, VI to achieve 100% coverage of all 54 US LIHTC jurisdictions
"""

import json
from pathlib import Path
from datetime import datetime
import time
from typing import Dict, List, Any
import logging

# Import our proven Phase 2D processor
from phase_2d_docling_plus import Phase2DDoclingPlus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase_2e_final_5.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Phase2EFinal5Processor:
    """Complete the final 5 jurisdictions for 100% coverage"""
    
    FINAL_5_JURISDICTIONS = ['LA', 'MT', 'NV', 'GU', 'VI']
    
    def __init__(self):
        """Initialize final 5 processor"""
        
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.qap_data_dir = self.base_dir / "data_sets" / "QAP"
        self.output_dir = Path(__file__).parent / "phase_2e_final_5_results"
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize proven Phase 2D processor
        self.processor = Phase2DDoclingPlus()
        
        logger.info("🎯 Phase 2E Final 5 initialized - completing 54-jurisdiction coverage")
        logger.info(f"📋 Target jurisdictions: {self.FINAL_5_JURISDICTIONS}")
    
    def find_best_qap_file(self, jurisdiction: str) -> Path:
        """Find the best available QAP file for jurisdiction"""
        
        current_dir = self.qap_data_dir / jurisdiction / "current"
        
        if not current_dir.exists():
            raise FileNotFoundError(f"No current directory for {jurisdiction}")
        
        # Find PDF files
        pdf_files = list(current_dir.glob("*.pdf"))
        
        if not pdf_files:
            raise FileNotFoundError(f"No PDF files found for {jurisdiction}")
        
        # Use largest PDF (usually the main QAP)
        best_pdf = max(pdf_files, key=lambda x: x.stat().st_size)
        
        logger.info(f"📄 {jurisdiction}: Selected {best_pdf.name} ({best_pdf.stat().st_size:,} bytes)")
        return best_pdf
    
    def process_single_jurisdiction(self, jurisdiction: str) -> Dict[str, Any]:
        """Process single jurisdiction with enhanced error handling"""
        
        start_time = time.time()
        logger.info(f"🏛️ Processing {jurisdiction}...")
        
        try:
            # Find best QAP file
            qap_file = self.find_best_qap_file(jurisdiction)
            
            # Process with Phase 2D intelligence
            result = self.processor.process_qap_with_definition_intelligence(
                str(qap_file), jurisdiction
            )
            
            # Enhanced success logging
            if result.get('success', True):
                processing_time = result.get('processing_time', time.time() - start_time)
                definitions_count = result.get('definitions_count', 0)
                cross_refs_count = len(result.get('cross_references', []))
                
                logger.info(f"✅ {jurisdiction}: {definitions_count} definitions, "
                          f"{cross_refs_count} cross-refs ({processing_time:.1f}s)")
                
                # Add file metadata
                result['source_file_size'] = qap_file.stat().st_size
                result['source_file_name'] = qap_file.name
                
            else:
                logger.error(f"❌ {jurisdiction}: Processing failed - {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Processing failed for {jurisdiction}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            return {
                'jurisdiction': jurisdiction,
                'success': False,
                'error': error_msg,
                'processing_time': processing_time,
                'phase': '2e_final_5'
            }
    
    def process_all_final_5(self) -> Dict[str, Any]:
        """Process all final 5 jurisdictions sequentially"""
        
        pipeline_start_time = time.time()
        
        logger.info("🏛️ PHASE 2E FINAL 5: COMPLETING 54-JURISDICTION COVERAGE")
        logger.info("=" * 70)
        logger.info(f"🎯 Target: Final {len(self.FINAL_5_JURISDICTIONS)} jurisdictions")
        logger.info(f"📊 Goal: 100% coverage of all 54 US LIHTC jurisdictions")
        
        results = {}
        successful_count = 0
        total_definitions = 0
        total_cross_references = 0
        
        # Process each jurisdiction
        for jurisdiction in self.FINAL_5_JURISDICTIONS:
            result = self.process_single_jurisdiction(jurisdiction)
            results[jurisdiction] = result
            
            # Track success metrics
            if result.get('success', True):
                successful_count += 1
                total_definitions += result.get('definitions_count', 0)
                total_cross_references += len(result.get('cross_references', []))
            
            # Save individual result
            individual_file = self.output_dir / f"{jurisdiction}_final_result.json"
            with open(individual_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Create comprehensive summary
        pipeline_time = time.time() - pipeline_start_time
        
        comprehensive_summary = {
            'processing_date': datetime.now().isoformat(),
            'processing_method': 'phase_2e_final_5_completion',
            'target_jurisdictions': self.FINAL_5_JURISDICTIONS,
            'successful_jurisdictions': successful_count,
            'failed_jurisdictions': len(self.FINAL_5_JURISDICTIONS) - successful_count,
            'success_rate': (successful_count / len(self.FINAL_5_JURISDICTIONS)) * 100,
            'total_definitions_final_5': total_definitions,
            'total_cross_references_final_5': total_cross_references,
            'total_processing_time': pipeline_time,
            'jurisdiction_results': results,
            
            # Project completion status
            'project_status': {
                'phase_2d_completed': 11,
                'phase_2e_batch_completed': 38,  # From previous Phase 2E run
                'phase_2e_final_5_completed': successful_count,
                'total_completed': 11 + 38 + successful_count,
                'target_total': 54,
                'completion_percentage': ((11 + 38 + successful_count) / 54) * 100
            }
        }
        
        # Save comprehensive summary
        summary_file = self.output_dir / f"PHASE_2E_FINAL_5_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_summary, f, indent=2, ensure_ascii=False)
        
        # Final reporting
        logger.info("\n" + "=" * 70)
        logger.info("🏆 PHASE 2E FINAL 5 COMPLETE!")
        logger.info("=" * 70)
        logger.info(f"✅ Successfully processed: {successful_count}/{len(self.FINAL_5_JURISDICTIONS)} jurisdictions")
        logger.info(f"📖 Final 5 definitions: {total_definitions}")
        logger.info(f"🔗 Final 5 cross-references: {total_cross_references}")
        logger.info(f"⏱️  Final 5 processing time: {pipeline_time:.1f} seconds")
        logger.info(f"🎯 Success rate: {comprehensive_summary['success_rate']:.1f}%")
        
        # Project completion status
        total_completed = comprehensive_summary['project_status']['total_completed']
        completion_pct = comprehensive_summary['project_status']['completion_percentage']
        
        logger.info(f"\n📊 OVERALL PROJECT STATUS:")
        logger.info(f"   Total jurisdictions completed: {total_completed}/54")
        logger.info(f"   Overall completion: {completion_pct:.1f}%")
        
        if total_completed == 54:
            logger.info(f"\n🏆 MILESTONE ACHIEVED: 100% COVERAGE OF ALL 54 US LIHTC JURISDICTIONS!")
            logger.info(f"⚔️ Complete Definition Intelligence System Ready! ⚔️")
        
        return comprehensive_summary

def main():
    """Execute Phase 2E Final 5 completion"""
    
    print("🎯 PHASE 2E FINAL 5: COMPLETING 54-JURISDICTION COVERAGE")
    print("=" * 70)
    print("📋 Target: LA, MT, NV, GU, VI")
    print("🏆 Goal: 100% coverage of all 54 US LIHTC jurisdictions")
    
    # Initialize and run final 5 processor
    processor = Phase2EFinal5Processor()
    results = processor.process_all_final_5()
    
    # Final celebration if 100% achieved
    total_completed = results['project_status']['total_completed']
    if total_completed == 54:
        print(f"\n🏆 BREAKTHROUGH ACHIEVED: 100% COVERAGE!")
        print(f"📊 All 54 US LIHTC jurisdictions processed with definition intelligence!")
        print(f"⚔️ The most comprehensive LIHTC database ever created is complete! ⚔️")
    else:
        print(f"\n📊 Progress: {total_completed}/54 jurisdictions completed ({results['project_status']['completion_percentage']:.1f}%)")

if __name__ == "__main__":
    main()