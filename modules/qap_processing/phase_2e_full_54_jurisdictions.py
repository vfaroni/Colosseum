#!/usr/bin/env python3
"""
Phase 2E: Full 54-Jurisdiction Automated Pipeline
Scales Phase 2D proven success (420 definitions, 1,088 cross-references) to all US LIHTC jurisdictions
Priorities: 1) Accuracy/QA 2) Depth 3) Speed 4) Automation
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Import our proven Phase 2D processor
from phase_2d_docling_plus import Phase2DDoclingPlus

# Configure logging for automation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase_2e_full_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Phase2EFullPipeline:
    """
    Full 54-jurisdiction automated pipeline with proven Phase 2D intelligence
    Optimized for accuracy, depth, speed, and full automation
    """
    
    # Complete 54 US LIHTC jurisdictions
    ALL_54_JURISDICTIONS = [
        # States (50)
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
        # Federal Territories (4)
        'DC', 'PR', 'GU', 'VI'
    ]
    
    # Phase 2D completed jurisdictions
    PHASE_2D_COMPLETED = ['CA', 'TX', 'FL', 'NY', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI', 'WA']
    
    def __init__(self):
        """Initialize full pipeline with proven Phase 2D components"""
        
        # Base paths
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.qap_data_dir = self.base_dir / "data_sets" / "QAP"
        self.output_dir = Path(__file__).parent / "phase_2e_full_54_jurisdictions"
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize proven Phase 2D processor
        self.processor = Phase2DDoclingPlus()
        
        # Remaining jurisdictions to process
        self.remaining_jurisdictions = [
            j for j in self.ALL_54_JURISDICTIONS 
            if j not in self.PHASE_2D_COMPLETED
        ]
        
        # Quality assurance tracking
        self.qa_tracker = {
            'successful_processing': 0,
            'failed_processing': 0,
            'quality_checks_passed': 0,
            'quality_checks_failed': 0,
            'definitions_extracted': 0,
            'cross_references_created': 0,
            'processing_errors': []
        }
        
        logger.info(f"🏛️ Phase 2E Full Pipeline initialized")
        logger.info(f"✅ Building on Phase 2D success: 11 jurisdictions, 420 definitions")
        logger.info(f"🎯 Processing remaining {len(self.remaining_jurisdictions)} jurisdictions")
        logger.info(f"📊 Target: All 54 US LIHTC jurisdictions with definition intelligence")
    
    def find_qap_files(self, jurisdiction: str) -> List[Path]:
        """Find QAP files for jurisdiction with comprehensive search"""
        
        potential_paths = [
            self.qap_data_dir / jurisdiction / "current",
            self.qap_data_dir / jurisdiction,
            self.qap_data_dir / jurisdiction.lower() / "current", 
            self.qap_data_dir / jurisdiction.lower(),
        ]
        
        qap_files = []
        for path in potential_paths:
            if path.exists():
                # Find PDF files
                pdf_files = list(path.glob("*.pdf"))
                if pdf_files:
                    # Use largest PDF (usually the main QAP)
                    largest_pdf = max(pdf_files, key=lambda x: x.stat().st_size)
                    qap_files.append(largest_pdf)
                    break
        
        return qap_files
    
    def quality_assurance_check(self, result: Dict[str, Any], jurisdiction: str) -> Dict[str, Any]:
        """Comprehensive quality assurance for extracted data"""
        
        qa_result = {
            'jurisdiction': jurisdiction,
            'passed': True,
            'issues': [],
            'metrics': {},
            'recommendations': []
        }
        
        try:
            # Check 1: Basic processing success
            if not result.get('success', True):
                qa_result['passed'] = False
                qa_result['issues'].append('Processing failed')
                return qa_result
            
            # Check 2: Minimum definitions threshold
            definitions_count = result.get('definitions_count', 0)
            if definitions_count < 1:
                qa_result['issues'].append('No definitions extracted - possible format issue')
                qa_result['recommendations'].append('Review QAP format and patterns')
            
            # Check 3: Definition quality validation
            definitions = result.get('definitions', [])
            quality_issues = 0
            
            for defn in definitions:
                # Check for minimum term length
                if len(defn.get('term', '')) < 3:
                    quality_issues += 1
                
                # Check for minimum definition length
                if len(defn.get('definition', '')) < 10:
                    quality_issues += 1
                
                # Check for LIHTC relevance assessment
                if not defn.get('lihtc_relevance'):
                    quality_issues += 1
            
            if quality_issues > definitions_count * 0.3:  # More than 30% quality issues
                qa_result['issues'].append(f'High quality issues: {quality_issues}/{definitions_count} definitions')
            
            # Check 4: Cross-reference validation
            cross_refs = result.get('cross_references', [])
            if definitions_count > 5 and len(cross_refs) == 0:
                qa_result['issues'].append('No cross-references created - possible content issue')
            
            # Check 5: Processing time validation (efficiency check)
            processing_time = result.get('processing_time', 0)
            if processing_time > 300:  # More than 5 minutes
                qa_result['issues'].append('Long processing time - possible performance issue')
            
            # Compile metrics
            qa_result['metrics'] = {
                'definitions_count': definitions_count,
                'cross_references_count': len(cross_refs),
                'processing_time': processing_time,
                'quality_score': max(0, 100 - (quality_issues * 10)),  # Quality score out of 100
                'lihtc_relevance_distribution': self._analyze_lihtc_relevance(definitions)
            }
            
            # Overall QA pass/fail
            if len(qa_result['issues']) > 2:
                qa_result['passed'] = False
            
            # Update tracker
            if qa_result['passed']:
                self.qa_tracker['quality_checks_passed'] += 1
            else:
                self.qa_tracker['quality_checks_failed'] += 1
            
        except Exception as e:
            qa_result['passed'] = False
            qa_result['issues'].append(f'QA check failed: {str(e)}')
            logger.error(f"QA check failed for {jurisdiction}: {e}")
        
        return qa_result
    
    def _analyze_lihtc_relevance(self, definitions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze LIHTC relevance distribution"""
        
        relevance_counts = {}
        for definition in definitions:
            relevance = definition.get('lihtc_relevance', 'unknown')
            relevance_counts[relevance] = relevance_counts.get(relevance, 0) + 1
        
        return relevance_counts
    
    def process_single_jurisdiction(self, jurisdiction: str) -> Dict[str, Any]:
        """Process single jurisdiction with full QA and error handling"""
        
        start_time = time.time()
        logger.info(f"🏛️ Processing {jurisdiction}...")
        
        try:
            # Find QAP files
            qap_files = self.find_qap_files(jurisdiction)
            
            if not qap_files:
                error_result = {
                    'jurisdiction': jurisdiction,
                    'success': False,
                    'error': 'No QAP files found',
                    'processing_time': time.time() - start_time,
                    'phase': '2e_full_pipeline'
                }
                self.qa_tracker['failed_processing'] += 1
                self.qa_tracker['processing_errors'].append(f"{jurisdiction}: No QAP files found")
                return error_result
            
            # Process with Phase 2D intelligence
            qap_file = qap_files[0]
            logger.info(f"📄 Processing {jurisdiction}: {qap_file.name}")
            
            result = self.processor.process_qap_with_definition_intelligence(
                str(qap_file), jurisdiction
            )
            
            # Quality assurance check
            qa_result = self.quality_assurance_check(result, jurisdiction)
            result['qa_result'] = qa_result
            
            # Update tracking
            if result.get('success', True):
                self.qa_tracker['successful_processing'] += 1
                self.qa_tracker['definitions_extracted'] += result.get('definitions_count', 0)
                self.qa_tracker['cross_references_created'] += len(result.get('cross_references', []))
                
                logger.info(f"✅ {jurisdiction}: {result.get('definitions_count', 0)} definitions, "
                          f"{len(result.get('cross_references', []))} cross-refs "
                          f"({result.get('processing_time', 0):.1f}s) "
                          f"QA: {'PASS' if qa_result['passed'] else 'ISSUES'}")
            else:
                self.qa_tracker['failed_processing'] += 1
                self.qa_tracker['processing_errors'].append(f"{jurisdiction}: {result.get('error', 'Unknown error')}")
                logger.error(f"❌ {jurisdiction}: Processing failed - {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            error_result = {
                'jurisdiction': jurisdiction,
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time,
                'phase': '2e_full_pipeline'
            }
            self.qa_tracker['failed_processing'] += 1
            self.qa_tracker['processing_errors'].append(f"{jurisdiction}: Exception - {str(e)}")
            logger.error(f"❌ {jurisdiction}: Exception - {str(e)}")
            return error_result
    
    def process_batch_concurrent(self, jurisdictions: List[str], max_workers: int = 6) -> Dict[str, Any]:
        """Process batch of jurisdictions concurrently with optimal performance"""
        
        logger.info(f"🚀 Processing batch of {len(jurisdictions)} jurisdictions with {max_workers} workers")
        batch_start_time = time.time()
        
        batch_results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_jurisdiction = {
                executor.submit(self.process_single_jurisdiction, jurisdiction): jurisdiction
                for jurisdiction in jurisdictions
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_jurisdiction):
                jurisdiction = future_to_jurisdiction[future]
                try:
                    result = future.result()
                    batch_results[jurisdiction] = result
                except Exception as e:
                    logger.error(f"Concurrent processing failed for {jurisdiction}: {e}")
                    batch_results[jurisdiction] = {
                        'jurisdiction': jurisdiction,
                        'success': False,
                        'error': f'Concurrent processing failed: {str(e)}',
                        'phase': '2e_full_pipeline'
                    }
        
        batch_time = time.time() - batch_start_time
        logger.info(f"✅ Batch complete: {len(batch_results)} jurisdictions in {batch_time:.1f}s")
        
        return batch_results
    
    def run_full_54_pipeline(self) -> Dict[str, Any]:
        """Run complete 54-jurisdiction pipeline with automation and QA"""
        
        pipeline_start_time = time.time()
        
        logger.info("🏛️ PHASE 2E: FULL 54-JURISDICTION AUTOMATED PIPELINE")
        logger.info("=" * 80)
        logger.info(f"✅ Phase 2D completed: {len(self.PHASE_2D_COMPLETED)} jurisdictions")
        logger.info(f"🎯 Phase 2E target: {len(self.remaining_jurisdictions)} remaining jurisdictions")
        logger.info(f"📊 Total coverage: All 54 US LIHTC jurisdictions")
        
        # Load Phase 2D results
        phase_2d_results = self.load_phase_2d_results()
        
        # Process remaining jurisdictions in optimized batches
        batch_size = 10  # Process 10 jurisdictions at a time for optimal performance
        all_results = {}
        all_results.update(phase_2d_results)  # Include Phase 2D results
        
        remaining_batches = [
            self.remaining_jurisdictions[i:i + batch_size] 
            for i in range(0, len(self.remaining_jurisdictions), batch_size)
        ]
        
        logger.info(f"🚀 Processing {len(remaining_batches)} batches of remaining jurisdictions...")
        
        for batch_num, batch_jurisdictions in enumerate(remaining_batches, 1):
            logger.info(f"\n📦 BATCH {batch_num}/{len(remaining_batches)}: {batch_jurisdictions}")
            
            batch_results = self.process_batch_concurrent(batch_jurisdictions, max_workers=6)
            all_results.update(batch_results)
            
            # Save incremental results for fault tolerance
            self.save_incremental_results(all_results, f"batch_{batch_num}")
            
            logger.info(f"✅ Batch {batch_num} complete - Running total: {len(all_results)} jurisdictions")
        
        # Create comprehensive final results
        pipeline_time = time.time() - pipeline_start_time
        
        final_results = self.create_comprehensive_summary(all_results, pipeline_time)
        
        # Save final results
        self.save_final_results(final_results)
        
        # Generate quality assurance report
        qa_report = self.generate_qa_report(all_results)
        
        logger.info("\n" + "=" * 80)
        logger.info("🏆 PHASE 2E FULL 54-JURISDICTION PIPELINE COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"📊 Total jurisdictions: {final_results['total_jurisdictions']}")
        logger.info(f"✅ Successful: {final_results['successful_jurisdictions']}")
        logger.info(f"❌ Failed: {final_results['failed_jurisdictions']}")
        logger.info(f"📖 Total definitions: {final_results['total_definitions']:,}")
        logger.info(f"🔗 Total cross-references: {final_results['total_cross_references']:,}")
        logger.info(f"⏱️  Total pipeline time: {final_results['total_pipeline_time']:.1f} seconds")
        logger.info(f"🎯 Success rate: {final_results['success_rate']:.1f}%")
        logger.info(f"🏅 QA pass rate: {qa_report['qa_pass_rate']:.1f}%")
        
        return final_results
    
    def load_phase_2d_results(self) -> Dict[str, Any]:
        """Load existing Phase 2D results to avoid reprocessing"""
        
        phase_2d_results = {}
        
        # Look for Phase 2D result files
        phase_2d_dir = Path(__file__).parent / "phase_2d_all_states_intelligent"
        
        if phase_2d_dir.exists():
            for state_file in phase_2d_dir.glob("*_intelligent_*.json"):
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                        state_code = result.get('state_code')
                        if state_code in self.PHASE_2D_COMPLETED:
                            phase_2d_results[state_code] = result
                            logger.info(f"📁 Loaded Phase 2D result: {state_code}")
                except Exception as e:
                    logger.warning(f"Could not load Phase 2D result from {state_file}: {e}")
        
        logger.info(f"✅ Loaded {len(phase_2d_results)} Phase 2D results")
        return phase_2d_results
    
    def create_comprehensive_summary(self, all_results: Dict[str, Any], pipeline_time: float) -> Dict[str, Any]:
        """Create comprehensive summary of all 54 jurisdictions"""
        
        successful_results = {k: v for k, v in all_results.items() if v.get('success', True)}
        failed_results = {k: v for k, v in all_results.items() if not v.get('success', True)}
        
        total_definitions = sum(
            result.get('definitions_count', 0) 
            for result in successful_results.values()
        )
        
        total_cross_references = sum(
            len(result.get('cross_references', [])) 
            for result in successful_results.values()
        )
        
        # LIHTC relevance analysis across all jurisdictions
        relevance_totals = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'minimal': 0}
        for result in successful_results.values():
            for definition in result.get('definitions', []):
                relevance = definition.get('lihtc_relevance', 'unknown')
                if relevance in relevance_totals:
                    relevance_totals[relevance] += 1
        
        # Top performing jurisdictions
        top_performers = sorted(
            [(k, v.get('definitions_count', 0)) for k, v in successful_results.items()],
            key=lambda x: x[1], reverse=True
        )[:10]
        
        return {
            'processing_date': datetime.now().isoformat(),
            'processing_method': 'phase_2e_full_54_jurisdictions',
            'phase_evolution': {
                'phase_2b': 1,
                'phase_2c': 91,
                'phase_2d': 420,
                'phase_2e_final': total_definitions
            },
            
            # Coverage metrics
            'total_jurisdictions': len(all_results),
            'successful_jurisdictions': len(successful_results),
            'failed_jurisdictions': len(failed_results),
            'success_rate': (len(successful_results) / len(all_results)) * 100,
            
            # Content metrics
            'total_definitions': total_definitions,
            'total_cross_references': total_cross_references,
            'avg_definitions_per_jurisdiction': total_definitions / len(successful_results) if successful_results else 0,
            'avg_cross_refs_per_jurisdiction': total_cross_references / len(successful_results) if successful_results else 0,
            
            # Performance metrics
            'total_pipeline_time': pipeline_time,
            'avg_processing_time_per_jurisdiction': pipeline_time / len(all_results),
            
            # Quality metrics
            'qa_tracker': self.qa_tracker,
            
            # Analysis
            'lihtc_relevance_distribution_all_54': relevance_totals,
            'top_10_performing_jurisdictions': top_performers,
            
            # Detailed results
            'jurisdiction_results': all_results,
            'failed_jurisdictions_details': failed_results,
            
            # Automation metrics
            'automation_success': True,
            'concurrent_processing': True,
            'quality_assurance': True
        }
    
    def save_incremental_results(self, results: Dict[str, Any], batch_identifier: str):
        """Save incremental results for fault tolerance"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"phase_2e_incremental_{batch_identifier}_{timestamp}.json"
        output_file = self.output_dir / filename
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Incremental results saved: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save incremental results: {e}")
    
    def save_final_results(self, final_results: Dict[str, Any]):
        """Save final comprehensive results"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save comprehensive results
        comprehensive_file = self.output_dir / f"PHASE_2E_FULL_54_JURISDICTIONS_{timestamp}.json" 
        
        try:
            with open(comprehensive_file, 'w', encoding='utf-8') as f:
                json.dump(final_results, f, indent=2, ensure_ascii=False)
            logger.info(f"📁 Final results saved: {comprehensive_file}")
        except Exception as e:
            logger.error(f"Failed to save final results: {e}")
    
    def generate_qa_report(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive quality assurance report"""
        
        qa_passed = sum(1 for result in all_results.values() 
                       if result.get('qa_result', {}).get('passed', False))
        
        qa_report = {
            'total_jurisdictions_qa': len(all_results),
            'qa_passed': qa_passed,
            'qa_failed': len(all_results) - qa_passed,
            'qa_pass_rate': (qa_passed / len(all_results)) * 100 if all_results else 0,
            'quality_issues_summary': [],
            'recommendations': []
        }
        
        # Collect quality issues
        for jurisdiction, result in all_results.items():
            qa_result = result.get('qa_result', {})
            if qa_result.get('issues'):
                qa_report['quality_issues_summary'].append({
                    'jurisdiction': jurisdiction,
                    'issues': qa_result['issues']
                })
        
        # Generate recommendations
        if qa_report['qa_pass_rate'] < 90:
            qa_report['recommendations'].append('Review QAP file formats for failed jurisdictions')
        
        if self.qa_tracker['failed_processing'] > 5:
            qa_report['recommendations'].append('Investigate file discovery issues')
        
        logger.info(f"📋 QA Report: {qa_passed}/{len(all_results)} jurisdictions passed QA ({qa_report['qa_pass_rate']:.1f}%)")
        
        return qa_report

def main():
    """Execute Phase 2E Full 54-Jurisdiction Pipeline"""
    
    print("🏛️ PHASE 2E: FULL 54-JURISDICTION AUTOMATED PIPELINE")
    print("=" * 80)
    print("🎯 Priorities: 1) Accuracy/QA 2) Depth 3) Speed 4) Automation")
    print("✅ Building on Phase 2D success: 420 definitions, 1,088 cross-references")
    print("📊 Target: Complete coverage of all 54 US LIHTC jurisdictions")
    
    # Initialize and run pipeline
    pipeline = Phase2EFullPipeline()
    final_results = pipeline.run_full_54_pipeline()
    
    print(f"\n🏆 PHASE 2E COMPLETE: {final_results['total_definitions']:,} definitions across {final_results['successful_jurisdictions']} jurisdictions!")
    print(f"🚀 Evolution: 1 → 91 → 420 → {final_results['total_definitions']} definitions")
    print(f"⚔️ Full 54-Jurisdiction Definition Intelligence System Ready! ⚔️")

if __name__ == "__main__":
    main()