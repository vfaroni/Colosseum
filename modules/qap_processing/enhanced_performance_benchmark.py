#!/usr/bin/env python3
"""
Enhanced ChromaDB Performance Benchmark
Direct performance testing of enhanced chunk system
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging

try:
    from enhanced_chromadb_loader import EnhancedChromaDBLoader
    ENHANCED_AVAILABLE = True
except ImportError as e:
    ENHANCED_AVAILABLE = False
    print(f"⚠️  Enhanced system not available: {e}")

logger = logging.getLogger(__name__)

class EnhancedPerformanceBenchmark:
    """Benchmark enhanced ChromaDB system performance"""
    
    def __init__(self):
        """Initialize benchmark system"""
        
        if not ENHANCED_AVAILABLE:
            raise ImportError("Enhanced ChromaDB system not available")
        
        # Initialize enhanced system
        self.enhanced_loader = EnhancedChromaDBLoader()
        
        # Comprehensive test queries
        self.benchmark_queries = [
            "minimum construction standards accessibility requirements",
            "qualified basis calculation requirements", 
            "income limits verification procedures",
            "tie breaker scoring criteria",
            "affordable housing scoring requirements",
            "construction timeline requirements",
            "compliance monitoring requirements",
            "developer fee limitations",
            "geographic preference points",
            "energy efficiency standards",
            "tenant income limits calculation",
            "qualified basis determination rules",
            "accessibility compliance standards",
            "environmental review requirements",
            "prevailing wage requirements"
        ]
        
        self.benchmark_results = {
            'test_timestamp': datetime.now().isoformat(),
            'system_info': {},
            'performance_tests': [],
            'aggregate_metrics': {},
            'enhanced_features_analysis': {},
            'overall_grade': 'unknown'
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get enhanced system information"""
        
        collection_stats = self.enhanced_loader.chroma_db.get_collection_stats()
        loader_stats = self.enhanced_loader.get_loading_stats()
        
        return {
            'collection_name': collection_stats.get('collection_name', ''),
            'total_documents': collection_stats.get('total_documents', 0),
            'embedding_model': collection_stats.get('embedding_model', ''),
            'chunks_loaded': loader_stats['loading_stats']['chunks_loaded'],
            'states_processed': list(loader_stats['loading_stats']['states_processed']),
            'total_enhanced_features': loader_stats['loading_stats']['total_enhanced_features'],
            'avg_features_per_chunk': loader_stats['performance']['avg_enhanced_features_per_chunk'],
            'system_status': loader_stats['status']
        }
    
    def benchmark_single_query(self, query: str, iterations: int = 3) -> Dict[str, Any]:
        """Benchmark a single query with multiple iterations"""
        
        search_times = []
        result_counts = []
        enhanced_features_found = []
        ca_results_found = []
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                # Direct ChromaDB search
                results = self.enhanced_loader.chroma_db.search(
                    query=query,
                    limit=20,
                    filters=None,
                    similarity_threshold=0.0
                )
                
                search_time = (time.time() - start_time) * 1000  # Convert to ms
                search_times.append(search_time)
                result_counts.append(len(results))
                
                # Analyze enhanced features
                ca_count = 0
                total_enhanced_features = 0
                
                for result in results:
                    metadata = result.get('metadata', {})
                    if metadata.get('state_code') == 'CA':
                        ca_count += 1
                    
                    enhanced_count = (
                        metadata.get('federal_refs_count', 0) +
                        metadata.get('state_refs_count', 0) +
                        metadata.get('qap_crossrefs_count', 0) +
                        metadata.get('lihtc_entities_count', 0)
                    )
                    total_enhanced_features += enhanced_count
                
                ca_results_found.append(ca_count)
                enhanced_features_found.append(total_enhanced_features)
                
            except Exception as e:
                logger.error(f"Query '{query}' failed on iteration {i+1}: {e}")
                search_times.append(0)
                result_counts.append(0)
                ca_results_found.append(0)
                enhanced_features_found.append(0)
        
        # Calculate averages
        avg_search_time = sum(search_times) / len(search_times) if search_times else 0
        avg_results = sum(result_counts) / len(result_counts) if result_counts else 0
        avg_ca_results = sum(ca_results_found) / len(ca_results_found) if ca_results_found else 0
        avg_enhanced_features = sum(enhanced_features_found) / len(enhanced_features_found) if enhanced_features_found else 0
        
        return {
            'query': query,
            'iterations': iterations,
            'avg_search_time_ms': round(avg_search_time, 2),
            'min_search_time_ms': round(min(search_times) if search_times else 0, 2),
            'max_search_time_ms': round(max(search_times) if search_times else 0, 2),
            'avg_results_count': round(avg_results, 1),
            'avg_ca_results': round(avg_ca_results, 1),
            'avg_enhanced_features': round(avg_enhanced_features, 1),
            'performance_grade': self._calculate_performance_grade(avg_search_time, avg_results, avg_enhanced_features),
            'all_iterations_successful': all(t > 0 for t in search_times)
        }
    
    def _calculate_performance_grade(self, search_time_ms: float, results_count: float, enhanced_features: float) -> str:
        """Calculate performance grade A-F"""
        
        # Speed grade (0-40 points)
        if search_time_ms <= 50:
            speed_points = 40
        elif search_time_ms <= 100:
            speed_points = 35
        elif search_time_ms <= 200:
            speed_points = 30
        elif search_time_ms <= 500:
            speed_points = 20
        else:
            speed_points = 10
        
        # Results grade (0-30 points)
        if results_count >= 15:
            results_points = 30
        elif results_count >= 10:
            results_points = 25
        elif results_count >= 5:
            results_points = 20
        elif results_count >= 1:
            results_points = 15
        else:
            results_points = 0
        
        # Enhanced features grade (0-30 points)
        if enhanced_features >= 50:
            features_points = 30
        elif enhanced_features >= 25:
            features_points = 25
        elif enhanced_features >= 10:
            features_points = 20
        elif enhanced_features >= 5:
            features_points = 15
        elif enhanced_features >= 1:
            features_points = 10
        else:
            features_points = 0
        
        total_score = speed_points + results_points + features_points
        
        if total_score >= 90:
            return 'A'
        elif total_score >= 80:
            return 'B'
        elif total_score >= 70:
            return 'C'
        elif total_score >= 60:
            return 'D'
        else:
            return 'F'
    
    def run_comprehensive_benchmark(self, iterations: int = 3) -> Dict[str, Any]:
        """Run comprehensive performance benchmark"""
        
        print(f"🏁 Starting comprehensive performance benchmark...")
        print(f"📊 Queries: {len(self.benchmark_queries)} × {iterations} iterations = {len(self.benchmark_queries) * iterations} total searches")
        
        # Get system info
        self.benchmark_results['system_info'] = self.get_system_info()
        
        # Test each query
        for i, query in enumerate(self.benchmark_queries, 1):
            print(f"⚡ Testing {i}/{len(self.benchmark_queries)}: '{query[:50]}...'")
            
            query_result = self.benchmark_single_query(query, iterations)
            self.benchmark_results['performance_tests'].append(query_result)
            
            # Show quick results
            grade = query_result['performance_grade']
            time_ms = query_result['avg_search_time_ms']
            features = query_result['avg_enhanced_features']
            
            print(f"   Grade: {grade} | Time: {time_ms}ms | Enhanced Features: {features}")
        
        # Calculate aggregate metrics
        self._calculate_aggregate_metrics()
        
        return self.benchmark_results
    
    def _calculate_aggregate_metrics(self):
        """Calculate overall performance metrics"""
        
        tests = self.benchmark_results['performance_tests']
        
        if not tests:
            self.benchmark_results['aggregate_metrics'] = {'error': 'No test results'}
            return
        
        # Performance metrics
        search_times = [t['avg_search_time_ms'] for t in tests]
        result_counts = [t['avg_results_count'] for t in tests]
        enhanced_features = [t['avg_enhanced_features'] for t in tests]
        grades = [t['performance_grade'] for t in tests]
        
        # Grade distribution
        grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for grade in grades:
            grade_counts[grade] += 1
        
        # Overall grade (most common grade)
        overall_grade = max(grade_counts, key=grade_counts.get)
        
        self.benchmark_results['aggregate_metrics'] = {
            'total_queries_tested': len(tests),
            'successful_queries': sum(1 for t in tests if t['all_iterations_successful']),
            'avg_search_time_ms': round(sum(search_times) / len(search_times), 2),
            'min_search_time_ms': round(min(search_times), 2),
            'max_search_time_ms': round(max(search_times), 2),
            'avg_results_per_query': round(sum(result_counts) / len(result_counts), 1),
            'avg_enhanced_features_per_query': round(sum(enhanced_features) / len(enhanced_features), 1),
            'total_enhanced_features_found': sum(enhanced_features),
            'grade_distribution': grade_counts,
            'overall_performance_grade': overall_grade,
            'queries_per_second': round(1000 / (sum(search_times) / len(search_times)), 2) if search_times else 0
        }
        
        self.benchmark_results['overall_grade'] = overall_grade
        
        # Enhanced features analysis
        self.benchmark_results['enhanced_features_analysis'] = {
            'queries_with_enhanced_features': sum(1 for f in enhanced_features if f > 0),
            'percentage_with_enhancements': round(sum(1 for f in enhanced_features if f > 0) / len(enhanced_features) * 100, 1),
            'max_features_in_single_query': max(enhanced_features) if enhanced_features else 0,
            'enhanced_features_detection_rate': 'high' if sum(enhanced_features) > len(tests) * 10 else 'medium' if sum(enhanced_features) > len(tests) * 5 else 'low'
        }
    
    def generate_performance_report(self, output_file: Path = None) -> str:
        """Generate comprehensive performance report"""
        
        if output_file is None:
            output_file = Path(__file__).parent.parent / "agents" / "BILL" / "STRIKE_LEADER" / "reports" / f"ENHANCED_PERFORMANCE_BENCHMARK_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Save detailed results (convert sets to lists for JSON serialization)
        serializable_results = json.loads(json.dumps(self.benchmark_results, default=str))
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        # Generate summary report
        system_info = self.benchmark_results['system_info']
        metrics = self.benchmark_results['aggregate_metrics']
        features = self.benchmark_results['enhanced_features_analysis']
        
        report = f"""
🏛️ **ENHANCED CHROMADB PERFORMANCE BENCHMARK**
**Test Date**: {self.benchmark_results['test_timestamp'][:19]}
**Overall Grade**: {self.benchmark_results['overall_grade']}

## 🏆 **SYSTEM INFORMATION**
- **Total Documents**: {system_info['total_documents']:,}
- **Enhanced Chunks**: {system_info['chunks_loaded']}
- **States Processed**: {', '.join(system_info['states_processed'])}
- **Total Enhanced Features**: {system_info['total_enhanced_features']:,}
- **Avg Features/Chunk**: {system_info['avg_features_per_chunk']:.1f}

## ⚡ **PERFORMANCE METRICS**
- **Queries Tested**: {metrics['total_queries_tested']}
- **Success Rate**: {metrics['successful_queries']}/{metrics['total_queries_tested']} ({round(metrics['successful_queries']/metrics['total_queries_tested']*100, 1)}%)
- **Average Search Time**: {metrics['avg_search_time_ms']}ms
- **Speed Range**: {metrics['min_search_time_ms']}ms - {metrics['max_search_time_ms']}ms
- **Queries Per Second**: {metrics['queries_per_second']}

## 📊 **SEARCH QUALITY**
- **Avg Results/Query**: {metrics['avg_results_per_query']}
- **Enhanced Features/Query**: {metrics['avg_enhanced_features_per_query']}
- **Total Features Found**: {metrics['total_enhanced_features_found']:,}
- **Feature Detection Rate**: {features['enhanced_features_detection_rate'].upper()}

## 🎯 **GRADE DISTRIBUTION**
- **A Grade**: {metrics['grade_distribution']['A']} queries
- **B Grade**: {metrics['grade_distribution']['B']} queries  
- **C Grade**: {metrics['grade_distribution']['C']} queries
- **D Grade**: {metrics['grade_distribution']['D']} queries
- **F Grade**: {metrics['grade_distribution']['F']} queries

## 🚀 **PRODUCTION READINESS**
{'✅ **EXCELLENT** - Ready for high-volume production deployment' if self.benchmark_results['overall_grade'] in ['A', 'B'] else '⚠️ **GOOD** - Ready for production with monitoring' if self.benchmark_results['overall_grade'] == 'C' else '❌ **NEEDS IMPROVEMENT** - Optimization required before production'}

**M4 Beast Status**: {'🦾 Fully Optimized' if metrics['avg_search_time_ms'] < 100 else '⚡ Well Optimized' if metrics['avg_search_time_ms'] < 200 else '🔧 Needs Optimization'}

**Detailed Results**: {output_file}
"""
        
        print(report)
        return report

def main():
    """Run enhanced performance benchmark"""
    
    print("🚀 Starting Enhanced ChromaDB Performance Benchmark...")
    
    try:
        # Initialize benchmark
        benchmark = EnhancedPerformanceBenchmark()
        
        # Run comprehensive benchmark
        results = benchmark.run_comprehensive_benchmark(iterations=3)
        
        # Generate report
        report = benchmark.generate_performance_report()
        
        print(f"\n✅ Performance Benchmark Complete!")
        print(f"Overall Grade: {results['overall_grade']}")
        
    except Exception as e:
        print(f"❌ Performance Benchmark failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()