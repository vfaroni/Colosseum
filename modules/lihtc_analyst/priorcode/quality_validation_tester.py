#!/usr/bin/env python3
"""
Quality Validation Tester for Enhanced Chunks
Tests search quality improvements after data quality enhancements
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests
import time

class QualityValidationTester:
    """Test data quality improvements"""
    
    def __init__(self, base_dir: str, api_base_url: str = "http://localhost:8000"):
        self.base_dir = Path(base_dir)
        self.enhanced_dir = self.base_dir / "QAP" / "_processed" / "_enhanced"
        self.api_base = api_base_url
        
        # Test queries for validation
        self.test_queries = [
            {
                'query': 'at-risk preservation set-aside requirements',
                'expected_jurisdictions': ['CA', 'TX', 'NY', 'WA'],
                'category': 'cross_state'
            },
            {
                'query': 'AMI income targeting requirements 60%',
                'expected_content': ['income', 'targeting', '60%', 'ami'],
                'category': 'regulatory'
            },
            {
                'query': 'qualified basis calculation rules',
                'expected_content': ['qualified basis', 'calculation', 'eligible'],
                'category': 'federal_compliance'
            },
            {
                'query': 'minimum set-aside requirements 9% credits',
                'expected_content': ['set-aside', '9%', 'minimum'],
                'category': 'program_specific'
            },
            {
                'query': 'compliance monitoring requirements',
                'expected_content': ['compliance', 'monitoring', 'reporting'],
                'category': 'operational'
            }
        ]
        
        self.results = {
            'test_timestamp': datetime.now().isoformat(),
            'enhanced_data_stats': {},
            'api_tests': {},
            'quality_metrics': {},
            'recommendations': []
        }
    
    def analyze_enhanced_data(self) -> None:
        """Analyze enhanced data statistics"""
        print("📊 Analyzing enhanced data...")
        
        master_index_file = self.enhanced_dir / "master_enhanced_index.json"
        if not master_index_file.exists():
            print("❌ Enhanced data not found!")
            return
        
        with open(master_index_file, 'r') as f:
            master_index = json.load(f)
        
        self.results['enhanced_data_stats'] = {
            'total_jurisdictions': master_index.get('total_jurisdictions', 0),
            'total_enhanced_chunks': master_index.get('total_enhanced_chunks', 0),
            'quality_improvements': master_index.get('quality_improvements', {}),
            'improvement_rate': 0
        }
        
        # Calculate improvement rate
        improvements = master_index.get('quality_improvements', {})
        if improvements.get('chunks_processed', 0) > 0:
            improvement_rate = (improvements.get('chunks_improved', 0) / 
                              improvements.get('chunks_processed', 1)) * 100
            self.results['enhanced_data_stats']['improvement_rate'] = improvement_rate
        
        print(f"   ✅ Enhanced chunks: {master_index.get('total_enhanced_chunks', 0):,}")
        print(f"   📈 Improvement rate: {improvement_rate:.1f}%")
        print(f"   🔧 Duplicates removed: {improvements.get('duplicates_removed', 0):,}")
        print(f"   ✏️  Sentences fixed: {improvements.get('sentences_fixed', 0):,}")
        print(f"   🔤 Encoding fixed: {improvements.get('encoding_fixed', 0):,}")
    
    def test_api_availability(self) -> bool:
        """Test if API is available"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ API available - {health_data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ API returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API not available: {e}")
            return False
    
    def run_search_test(self, test_case: Dict) -> Dict:
        """Run a single search test"""
        query = test_case['query']
        category = test_case['category']
        
        print(f"   🔍 Testing: {query}")
        
        try:
            # Test vector search
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/search",
                json={
                    "query": query,
                    "search_mode": "vector",
                    "limit": 10
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    'query': query,
                    'category': category,
                    'success': False,
                    'error': f"API returned {response.status_code}"
                }
            
            data = response.json()
            response_time = time.time() - start_time
            
            # Analyze results
            results = data.get('results', [])
            total_results = len(results)
            
            # Check expected content
            content_matches = 0
            if 'expected_content' in test_case:
                for result in results:
                    content_lower = result.get('content', '').lower()
                    matches = sum(1 for term in test_case['expected_content'] 
                                if term.lower() in content_lower)
                    content_matches += matches
            
            # Check jurisdiction coverage
            jurisdictions_found = set()
            for result in results:
                state = result.get('state_code', '')
                if state:
                    jurisdictions_found.add(state)
            
            jurisdiction_coverage = 0
            if 'expected_jurisdictions' in test_case:
                expected_jurisdictions = set(test_case['expected_jurisdictions'])
                jurisdiction_coverage = len(jurisdictions_found.intersection(expected_jurisdictions))
            
            # Calculate quality score
            quality_score = 0
            if total_results > 0:
                avg_score = sum(r.get('score', 0) for r in results) / total_results
                quality_score = avg_score * 100
            
            return {
                'query': query,
                'category': category,
                'success': True,
                'total_results': total_results,
                'response_time_ms': response_time * 1000,
                'content_matches': content_matches,
                'jurisdictions_found': len(jurisdictions_found),
                'jurisdiction_coverage': jurisdiction_coverage,
                'quality_score': quality_score,
                'top_results': results[:3]  # Store top 3 for analysis
            }
            
        except Exception as e:
            return {
                'query': query,
                'category': category,
                'success': False,
                'error': str(e)
            }
    
    def run_api_tests(self) -> None:
        """Run all API search tests"""
        print("\n🧪 Running API search tests...")
        
        if not self.test_api_availability():
            print("❌ Cannot run API tests - server unavailable")
            return
        
        test_results = []
        
        for test_case in self.test_queries:
            result = self.run_search_test(test_case)
            test_results.append(result)
            
            if result['success']:
                print(f"      ✅ {result['total_results']} results in {result['response_time_ms']:.1f}ms")
                print(f"         Quality: {result['quality_score']:.1f}%, Jurisdictions: {result['jurisdictions_found']}")
            else:
                print(f"      ❌ Failed: {result.get('error', 'Unknown error')}")
        
        self.results['api_tests'] = {
            'tests_run': len(test_results),
            'tests_passed': len([r for r in test_results if r['success']]),
            'average_response_time': sum(r.get('response_time_ms', 0) for r in test_results if r['success']) / max(1, len([r for r in test_results if r['success']])),
            'average_quality_score': sum(r.get('quality_score', 0) for r in test_results if r['success']) / max(1, len([r for r in test_results if r['success']])),
            'results': test_results
        }
    
    def calculate_quality_metrics(self) -> None:
        """Calculate overall quality metrics"""
        print("\n📈 Calculating quality metrics...")
        
        api_tests = self.results.get('api_tests', {})
        enhanced_stats = self.results.get('enhanced_data_stats', {})
        
        # Overall system health
        system_health = 100
        
        # Test success rate
        tests_passed = api_tests.get('tests_passed', 0)
        tests_run = api_tests.get('tests_run', 1)
        test_success_rate = (tests_passed / tests_run) * 100
        
        # Data quality improvements
        improvement_rate = enhanced_stats.get('improvement_rate', 0)
        
        # Response time score (target: <200ms)
        avg_response_time = api_tests.get('average_response_time', 1000)
        response_time_score = max(0, 100 - (avg_response_time - 200) / 10)
        
        # Search quality score
        search_quality_score = api_tests.get('average_quality_score', 0)
        
        self.results['quality_metrics'] = {
            'overall_score': (test_success_rate + improvement_rate + response_time_score + search_quality_score) / 4,
            'test_success_rate': test_success_rate,
            'data_improvement_rate': improvement_rate,
            'response_time_score': response_time_score,
            'search_quality_score': search_quality_score,
            'system_health': system_health if tests_passed == tests_run else 75
        }
        
        print(f"   🎯 Overall Score: {self.results['quality_metrics']['overall_score']:.1f}/100")
        print(f"   ✅ Test Success: {test_success_rate:.1f}%")
        print(f"   📊 Data Quality: {improvement_rate:.1f}%")
        print(f"   ⚡ Response Time: {response_time_score:.1f}/100")
        print(f"   🔍 Search Quality: {search_quality_score:.1f}/100")
    
    def generate_recommendations(self) -> None:
        """Generate recommendations based on test results"""
        recommendations = []
        
        quality_metrics = self.results.get('quality_metrics', {})
        api_tests = self.results.get('api_tests', {})
        
        # Test success rate recommendations
        if quality_metrics.get('test_success_rate', 0) < 100:
            recommendations.append({
                'priority': 'high',
                'category': 'api_stability',
                'issue': f"Only {quality_metrics.get('test_success_rate', 0):.1f}% of tests passed",
                'action': 'Investigate API failures and improve error handling'
            })
        
        # Response time recommendations
        if quality_metrics.get('response_time_score', 0) < 80:
            recommendations.append({
                'priority': 'medium',
                'category': 'performance',
                'issue': f"Average response time {api_tests.get('average_response_time', 0):.1f}ms",
                'action': 'Optimize vector search performance and caching'
            })
        
        # Search quality recommendations
        if quality_metrics.get('search_quality_score', 0) < 70:
            recommendations.append({
                'priority': 'high',
                'category': 'search_quality',
                'issue': f"Search quality score {quality_metrics.get('search_quality_score', 0):.1f}/100",
                'action': 'Review embedding model and similarity thresholds'
            })
        
        # Data quality recommendations
        improvement_rate = self.results.get('enhanced_data_stats', {}).get('improvement_rate', 0)
        if improvement_rate > 50:
            recommendations.append({
                'priority': 'medium',
                'category': 'data_processing',
                'issue': f"High improvement rate {improvement_rate:.1f}% indicates original data quality issues",
                'action': 'Review PDF extraction pipeline and preprocessing steps'
            })
        
        self.results['recommendations'] = recommendations
        
        print(f"\n💡 Generated {len(recommendations)} recommendations")
        for rec in recommendations:
            print(f"   🎯 {rec['priority'].upper()}: {rec['action']}")
    
    def save_validation_report(self, output_path: str = None) -> None:
        """Save validation report"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/mac_studio_rag/quality_validation_report_{timestamp}.json"
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Saved validation report: {output_path}")
    
    def run_full_validation(self) -> Dict:
        """Run complete validation suite"""
        print("🧪 QUALITY VALIDATION TESTING")
        print("=" * 60)
        
        # Analyze enhanced data
        self.analyze_enhanced_data()
        
        # Run API tests
        self.run_api_tests()
        
        # Calculate metrics
        self.calculate_quality_metrics()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Save report
        self.save_validation_report()
        
        return self.results

def main():
    """Run quality validation testing"""
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    tester = QualityValidationTester(base_dir)
    
    results = tester.run_full_validation()
    
    # Print executive summary
    print("\n" + "=" * 60)
    print("🏆 VALIDATION SUMMARY")
    print("=" * 60)
    
    quality_metrics = results.get('quality_metrics', {})
    enhanced_stats = results.get('enhanced_data_stats', {})
    
    print(f"Overall Quality Score: {quality_metrics.get('overall_score', 0):.1f}/100")
    print(f"Enhanced Chunks: {enhanced_stats.get('total_enhanced_chunks', 0):,}")
    print(f"Data Improvements: {enhanced_stats.get('improvement_rate', 0):.1f}%")
    print(f"API Test Success: {quality_metrics.get('test_success_rate', 0):.1f}%")
    print(f"Recommendations: {len(results.get('recommendations', []))}")

if __name__ == "__main__":
    main()