#!/usr/bin/env python3
"""
Enhanced ChromaDB A/B Testing System
Compares old CA chunks vs new enhanced chunks for search quality
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

# Add existing RAG system to path
sys.path.append(str(Path(__file__).parent.parent / "lihtc_analyst" / "priorcode"))

try:
    from unified_lihtc_rag_query import UnifiedLIHTCRAGQuery
    from enhanced_chromadb_loader import EnhancedChromaDBLoader
    RAG_AVAILABLE = True
except ImportError as e:
    RAG_AVAILABLE = False
    print(f"⚠️  RAG system not available: {e}")

logger = logging.getLogger(__name__)

class EnhancedABTester:
    """A/B test old vs enhanced chunks for search quality"""
    
    def __init__(self, base_data_dir: str = None):
        """Initialize A/B tester with both old and enhanced systems"""
        
        if not RAG_AVAILABLE:
            raise ImportError("RAG system dependencies not available")
        
        # Initialize old RAG system (uses existing ChromaDB with old chunks)
        if base_data_dir is None:
            # Use structured consultants path for old system
            base_data_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
        
        print("🔄 Initializing old RAG system...")
        self.old_rag_system = UnifiedLIHTCRAGQuery(base_data_dir)
        
        # Initialize enhanced system
        print("🔄 Initializing enhanced ChromaDB system...")
        self.enhanced_loader = EnhancedChromaDBLoader()
        
        # Test queries for A/B comparison
        self.test_queries = [
            "minimum construction standards accessibility requirements",
            "qualified basis calculation requirements", 
            "income limits verification procedures",
            "tie breaker scoring criteria",
            "affordable housing scoring requirements",
            "construction timeline requirements",
            "compliance monitoring requirements",
            "developer fee limitations",
            "geographic preference points",
            "energy efficiency standards"
        ]
        
        self.ab_results = {
            'test_timestamp': datetime.now().isoformat(),
            'queries_tested': len(self.test_queries),
            'old_system_results': [],
            'enhanced_system_results': [],
            'comparison_metrics': {},
            'winner': 'unknown'
        }
    
    def run_old_system_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Run search on old RAG system"""
        
        start_time = time.time()
        
        try:
            # Search CA specifically in old system
            results = self.old_rag_system.semantic_search_unified(
                query=query,
                search_namespace='state',
                states=['CA'],
                limit=limit
            )
            
            search_time = time.time() - start_time
            
            # Analyze old system results
            analysis = {
                'query': query,
                'results_count': len(results),
                'search_time_ms': round(search_time * 1000, 2),
                'system_type': 'old_rag',
                'results': results[:5],  # Top 5 for comparison
                'quality_metrics': self._analyze_old_results_quality(results),
                'status': 'success'
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Old system search failed for '{query}': {e}")
            return {
                'query': query,
                'results_count': 0,
                'search_time_ms': 0,
                'system_type': 'old_rag',
                'results': [],
                'quality_metrics': {'error': str(e)},
                'status': 'failed'
            }
    
    def run_enhanced_system_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Run search on enhanced ChromaDB system"""
        
        start_time = time.time()
        
        try:
            # Search enhanced ChromaDB directly
            results = self.enhanced_loader.chroma_db.search(
                query=query,
                limit=limit,
                filters={'state_code': 'CA', 'content_type': 'enhanced_qap'}
            )
            
            search_time = time.time() - start_time
            
            # Analyze enhanced system results
            analysis = {
                'query': query,
                'results_count': len(results),
                'search_time_ms': round(search_time * 1000, 2),
                'system_type': 'enhanced_chromadb',
                'results': results[:5],  # Top 5 for comparison
                'quality_metrics': self._analyze_enhanced_results_quality(results),
                'status': 'success'
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Enhanced system search failed for '{query}': {e}")
            return {
                'query': query,
                'results_count': 0,
                'search_time_ms': 0,
                'system_type': 'enhanced_chromadb',
                'results': [],
                'quality_metrics': {'error': str(e)},
                'status': 'failed'
            }
    
    def _analyze_old_results_quality(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze quality metrics for old system results"""
        
        if not results:
            return {'total_score': 0, 'metrics': {}}
        
        metrics = {
            'avg_relevance_score': sum(r.get('score', 0) for r in results) / len(results),
            'content_coverage': sum(1 for r in results if len(r.get('content', '')) > 100),
            'metadata_completeness': sum(1 for r in results if r.get('metadata', {}).get('section_title')),
            'ca_results': sum(1 for r in results if r.get('state_code') == 'CA'),
            'reference_richness': 0  # Old system has minimal references
        }
        
        # Calculate total quality score (0-100)
        total_score = (
            (metrics['avg_relevance_score'] * 30) +
            (metrics['content_coverage'] / len(results) * 25) +
            (metrics['metadata_completeness'] / len(results) * 25) +
            (metrics['ca_results'] / len(results) * 20)
        )
        
        return {
            'total_score': round(total_score, 2),
            'metrics': metrics
        }
    
    def _analyze_enhanced_results_quality(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze quality metrics for enhanced system results"""
        
        if not results:
            return {'total_score': 0, 'metrics': {}}
        
        # Calculate enhanced features
        total_enhanced_features = 0
        hierarchical_results = 0
        breadcrumb_results = 0
        
        for result in results:
            metadata = result.get('metadata', {})
            total_enhanced_features += (
                metadata.get('federal_refs_count', 0) +
                metadata.get('state_refs_count', 0) +
                metadata.get('qap_crossrefs_count', 0) +
                metadata.get('lihtc_entities_count', 0)
            )
            
            if metadata.get('hierarchy_level', 0) > 0:
                hierarchical_results += 1
            
            if metadata.get('breadcrumb'):
                breadcrumb_results += 1
        
        metrics = {
            'avg_relevance_score': sum(r.get('score', 0) for r in results) / len(results),
            'content_coverage': sum(1 for r in results if len(r.get('content', '')) > 100),
            'metadata_completeness': sum(1 for r in results if r.get('metadata', {}).get('section_title')),
            'ca_results': sum(1 for r in results if r.get('metadata', {}).get('state_code') == 'CA'),
            'enhanced_features_avg': total_enhanced_features / len(results),
            'hierarchical_structure': hierarchical_results / len(results),
            'navigation_breadcrumbs': breadcrumb_results / len(results),
            'processing_method': sum(1 for r in results if r.get('metadata', {}).get('processing_method') == 'docling_4strategy')
        }
        
        # Calculate total quality score (0-100) with enhanced weighting
        total_score = (
            (metrics['avg_relevance_score'] * 25) +
            (metrics['content_coverage'] / len(results) * 20) +
            (metrics['metadata_completeness'] / len(results) * 15) +
            (metrics['ca_results'] / len(results) * 15) +
            (min(metrics['enhanced_features_avg'] / 10, 1.0) * 15) +  # Cap at 10 features
            (metrics['hierarchical_structure'] * 5) +
            (metrics['navigation_breadcrumbs'] * 5)
        )
        
        return {
            'total_score': round(total_score, 2),
            'metrics': metrics
        }
    
    def run_comprehensive_ab_test(self) -> Dict[str, Any]:
        """Run comprehensive A/B test comparing both systems"""
        
        print(f"🏁 Starting comprehensive A/B test with {len(self.test_queries)} queries...")
        
        # Test each query on both systems
        for i, query in enumerate(self.test_queries, 1):
            print(f"📊 Testing query {i}/{len(self.test_queries)}: '{query[:50]}...'")
            
            # Test old system
            old_result = self.run_old_system_search(query)
            self.ab_results['old_system_results'].append(old_result)
            
            # Test enhanced system  
            enhanced_result = self.run_enhanced_system_search(query)
            self.ab_results['enhanced_system_results'].append(enhanced_result)
            
            # Show quick comparison
            old_score = old_result['quality_metrics'].get('total_score', 0)
            enhanced_score = enhanced_result['quality_metrics'].get('total_score', 0)
            winner = "Enhanced" if enhanced_score > old_score else "Old" if old_score > enhanced_score else "Tie"
            
            print(f"   Old: {old_score:.1f} | Enhanced: {enhanced_score:.1f} | Winner: {winner}")
        
        # Calculate overall comparison metrics
        self._calculate_comparison_metrics()
        
        return self.ab_results
    
    def _calculate_comparison_metrics(self):
        """Calculate overall comparison metrics"""
        
        # Aggregate scores
        old_scores = [r['quality_metrics'].get('total_score', 0) for r in self.ab_results['old_system_results']]
        enhanced_scores = [r['quality_metrics'].get('total_score', 0) for r in self.ab_results['enhanced_system_results']]
        
        # Performance metrics
        old_times = [r['search_time_ms'] for r in self.ab_results['old_system_results']]
        enhanced_times = [r['search_time_ms'] for r in self.ab_results['enhanced_system_results']]
        
        # Count wins
        wins = {'old': 0, 'enhanced': 0, 'ties': 0}
        for old_score, enhanced_score in zip(old_scores, enhanced_scores):
            if enhanced_score > old_score:
                wins['enhanced'] += 1
            elif old_score > enhanced_score:
                wins['old'] += 1
            else:
                wins['ties'] += 1
        
        self.ab_results['comparison_metrics'] = {
            'quality_scores': {
                'old_avg': round(sum(old_scores) / len(old_scores), 2) if old_scores else 0,
                'enhanced_avg': round(sum(enhanced_scores) / len(enhanced_scores), 2) if enhanced_scores else 0,
                'improvement_percentage': round(((sum(enhanced_scores) - sum(old_scores)) / max(sum(old_scores), 1)) * 100, 2)
            },
            'performance': {
                'old_avg_time_ms': round(sum(old_times) / len(old_times), 2) if old_times else 0,
                'enhanced_avg_time_ms': round(sum(enhanced_times) / len(enhanced_times), 2) if enhanced_times else 0,
                'speed_change_percentage': round(((sum(old_times) - sum(enhanced_times)) / max(sum(old_times), 1)) * 100, 2)
            },
            'win_loss_record': wins,
            'statistical_significance': self._calculate_statistical_significance(old_scores, enhanced_scores)
        }
        
        # Determine overall winner
        if wins['enhanced'] > wins['old']:
            self.ab_results['winner'] = 'enhanced'
        elif wins['old'] > wins['enhanced']:
            self.ab_results['winner'] = 'old'
        else:
            self.ab_results['winner'] = 'tie'
    
    def _calculate_statistical_significance(self, old_scores: List[float], enhanced_scores: List[float]) -> Dict[str, Any]:
        """Calculate basic statistical significance"""
        
        if len(old_scores) != len(enhanced_scores) or len(old_scores) < 3:
            return {'significance': 'insufficient_data'}
        
        # Simple statistical analysis
        differences = [e - o for e, o in zip(enhanced_scores, old_scores)]
        avg_difference = sum(differences) / len(differences)
        
        # Basic confidence assessment
        positive_differences = sum(1 for d in differences if d > 0)
        confidence_level = positive_differences / len(differences)
        
        return {
            'avg_score_difference': round(avg_difference, 2),
            'positive_improvements': positive_differences,
            'total_comparisons': len(differences),
            'confidence_level': round(confidence_level * 100, 1),
            'significance': 'significant' if confidence_level > 0.7 else 'marginal' if confidence_level > 0.5 else 'not_significant'
        }
    
    def generate_ab_test_report(self, output_file: Path = None) -> str:
        """Generate comprehensive A/B test report"""
        
        if output_file is None:
            output_file = Path(__file__).parent.parent / "agents" / "BILL" / "STRIKE_LEADER" / "reports" / f"AB_TEST_RESULTS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Save detailed results
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.ab_results, f, indent=2, ensure_ascii=False)
        
        # Generate summary report
        metrics = self.ab_results['comparison_metrics']
        
        report = f"""
🏛️ **ENHANCED CHROMADB A/B TEST RESULTS**
**Test Date**: {self.ab_results['test_timestamp'][:19]}
**Queries Tested**: {self.ab_results['queries_tested']}

## 🏆 **OVERALL WINNER: {self.ab_results['winner'].upper()}**

### 📊 **QUALITY COMPARISON**
- **Old System Average**: {metrics['quality_scores']['old_avg']}/100
- **Enhanced System Average**: {metrics['quality_scores']['enhanced_avg']}/100  
- **Quality Improvement**: {metrics['quality_scores']['improvement_percentage']}%

### ⚡ **PERFORMANCE COMPARISON**
- **Old System Speed**: {metrics['performance']['old_avg_time_ms']}ms average
- **Enhanced System Speed**: {metrics['performance']['enhanced_avg_time_ms']}ms average
- **Speed Change**: {metrics['performance']['speed_change_percentage']}%

### 🥊 **WIN/LOSS RECORD**
- **Enhanced Wins**: {metrics['win_loss_record']['enhanced']}
- **Old Wins**: {metrics['win_loss_record']['old']}  
- **Ties**: {metrics['win_loss_record']['ties']}

### 📈 **STATISTICAL SIGNIFICANCE**
- **Confidence Level**: {metrics['statistical_significance']['confidence_level']}%
- **Significance**: {metrics['statistical_significance']['significance']}  
- **Average Score Difference**: {metrics['statistical_significance']['avg_score_difference']}

**Detailed Results**: {output_file}
"""
        
        print(report)
        return report

def main():
    """Run A/B test comparison"""
    
    print("🚀 Starting Enhanced ChromaDB A/B Testing...")
    
    try:
        # Initialize A/B tester
        ab_tester = EnhancedABTester()
        
        # Run comprehensive test
        results = ab_tester.run_comprehensive_ab_test()
        
        # Generate report
        report = ab_tester.generate_ab_test_report()
        
        print(f"\n✅ A/B Test Complete!")
        print(f"Winner: {results['winner'].upper()}")
        
    except Exception as e:
        print(f"❌ A/B Test failed: {e}")

if __name__ == "__main__":
    main()