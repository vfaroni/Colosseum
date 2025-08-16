#!/usr/bin/env python3
"""
Production Test Script for Unified LIHTC RAG System
Demonstrates advanced search capabilities with real-world LIHTC research queries
Tests authority hierarchies, cross-jurisdictional comparisons, and conflict resolution
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import traceback

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from unified_lihtc_rag_query import UnifiedLIHTCRAGQuery, QueryResult

class ProductionTestSuite:
    """Comprehensive test suite for LIHTC RAG system"""
    
    def __init__(self, base_dir: str, output_dir: str = None):
        """Initialize test suite with unified query system"""
        self.base_dir = Path(base_dir)
        self.output_dir = Path(output_dir) if output_dir else self.base_dir / "test_results"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize the unified query system
        self.query_system = UnifiedLIHTCRAGQuery(base_dir)
        
        # Test results tracking
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        # Real-world LIHTC research queries
        self.test_queries = [
            {
                'name': 'Federal Section 42 Compliance Monitoring',
                'query': 'What are the federal compliance monitoring requirements under Section 42?',
                'test_type': 'authority_based',
                'expected_authorities': ['statutory', 'regulatory'],
                'business_context': 'Property managers need to understand federal compliance requirements'
            },
            {
                'name': 'DCR Federal vs State Comparison',
                'query': 'Compare DCR requirements between federal regulations and California CTCAC',
                'test_type': 'cross_jurisdictional',
                'target_states': ['CA'],
                'business_context': 'Developers need to understand dual compliance requirements'
            },
            {
                'name': '2025 Per Capita Credit Inflation Adjustments',
                'query': 'What are the 2025 inflation adjustments for per capita credit?',
                'test_type': 'effective_date',
                'date_range': ('2024', '2025'),
                'business_context': 'Allocation agencies need current credit ceiling amounts'
            },
            {
                'name': 'Qualified Basis Rules Federal vs State',
                'query': 'How do federal qualified basis rules apply to state QAPs?',
                'test_type': 'federal_state_mapping',
                'business_context': 'Developers must understand basis calculation differences'
            },
            {
                'name': 'Income Limits Entity Search',
                'query': 'AMI limits and income restrictions',
                'test_type': 'entity_search',
                'entity_type': 'percentage',
                'business_context': 'Property managers need current income limit calculations'
            },
            {
                'name': 'Compliance Period Duration',
                'query': 'What is the compliance period for LIHTC properties?',
                'test_type': 'conflict_resolution',
                'business_context': 'Owners need to understand minimum compliance periods'
            },
            {
                'name': 'Placed-in-Service Requirements',
                'query': 'placed in service requirements and deadlines',
                'test_type': 'federal_authority',
                'business_context': 'Developers need to understand construction deadlines'
            },
            {
                'name': 'Basis Boost Percentage Limits',
                'query': 'What are the basis boost percentage limits for difficult development areas?',
                'test_type': 'entity_search',
                'entity_type': 'percentage',
                'business_context': 'Developers need to calculate maximum credit amounts'
            }
        ]
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        print("🚀 Starting Production Test Suite for Unified LIHTC RAG System")
        print(f"📊 Total test queries: {len(self.test_queries)}")
        print(f"📁 Output directory: {self.output_dir}")
        print("-" * 80)
        
        for i, test_query in enumerate(self.test_queries, 1):
            print(f"\n🔍 Test {i}/{len(self.test_queries)}: {test_query['name']}")
            print(f"   Query: {test_query['query']}")
            print(f"   Type: {test_query['test_type']}")
            print(f"   Business Context: {test_query['business_context']}")
            
            try:
                # Run the appropriate test based on type
                test_result = self.execute_test(test_query)
                
                # Track results
                self.test_results['total_tests'] += 1
                if test_result.get('success', False):
                    self.test_results['successful_tests'] += 1
                    print(f"   ✅ Test passed - {test_result.get('result_count', 0)} results")
                else:
                    self.test_results['failed_tests'] += 1
                    print(f"   ❌ Test failed - {test_result.get('error', 'Unknown error')}")
                
                self.test_results['test_details'].append(test_result)
                
            except Exception as e:
                error_msg = f"Test execution failed: {str(e)}"
                print(f"   ❌ {error_msg}")
                self.test_results['failed_tests'] += 1
                self.test_results['test_details'].append({
                    'test_name': test_query['name'],
                    'success': False,
                    'error': error_msg,
                    'traceback': traceback.format_exc()
                })
        
        # Generate summary report
        self.generate_summary_report()
        
        return self.test_results
    
    def execute_test(self, test_query: Dict) -> Dict[str, Any]:
        """Execute individual test based on type"""
        test_type = test_query['test_type']
        query = test_query['query']
        
        test_result = {
            'test_name': test_query['name'],
            'query': query,
            'test_type': test_type,
            'business_context': test_query['business_context'],
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'results': [],
            'analysis': {}
        }
        
        try:
            if test_type == 'authority_based':
                results = self.query_system.search_by_authority_level(
                    query, 
                    authority_levels=test_query.get('expected_authorities', None),
                    limit=10
                )
                
            elif test_type == 'cross_jurisdictional':
                comparison = self.query_system.cross_jurisdictional_comparison(
                    query,
                    comparison_type='federal_vs_states',
                    target_states=test_query.get('target_states', None)
                )
                results = comparison.get('federal_requirements', [])
                test_result['cross_jurisdictional_analysis'] = comparison
                
            elif test_type == 'effective_date':
                results = self.query_system.search_by_effective_date(
                    query,
                    date_range=test_query.get('date_range', None),
                    limit=10
                )
                
            elif test_type == 'federal_state_mapping':
                mappings = self.query_system.search_federal_state_mappings(query, limit=10)
                results = mappings
                test_result['federal_state_mappings'] = mappings
                
            elif test_type == 'entity_search':
                results = self.query_system.advanced_entity_search(
                    entity_type=test_query.get('entity_type', 'percentage'),
                    context_query=query,
                    limit=10
                )
                
            elif test_type == 'conflict_resolution':
                results = self.query_system.search_with_conflict_analysis(
                    query,
                    include_conflicts=True,
                    resolve_conflicts=True,
                    limit=10
                )
                
            elif test_type == 'federal_authority':
                results = self.query_system.search_by_authority_level(
                    query,
                    authority_levels=['statutory', 'regulatory'],
                    limit=10
                )
                
            else:
                # Default unified search
                results = self.query_system.semantic_search_unified(
                    query,
                    search_namespace='unified',
                    limit=10
                )
            
            # Process results
            if results:
                test_result['success'] = True
                test_result['result_count'] = len(results)
                
                # Extract key information from results
                processed_results = []
                for result in results[:5]:  # Show top 5 results
                    if isinstance(result, QueryResult):
                        processed_results.append({
                            'source': result.source,
                            'source_type': result.source_type,
                            'authority_level': result.authority_level,
                            'authority_score': result.authority_score,
                            'section_reference': result.section_reference,
                            'content_preview': result.content[:300] + "..." if len(result.content) > 300 else result.content,
                            'effective_date': result.effective_date,
                            'conflicts': result.conflicts,
                            'relevance_score': result.relevance_score
                        })
                    elif isinstance(result, dict):
                        # Handle mapping results
                        processed_results.append({
                            'federal_source_type': result.get('federal_source_type', ''),
                            'section_reference': result.get('section_reference', ''),
                            'implementing_states': result.get('implementing_states', []),
                            'state_count': result.get('state_count', 0),
                            'content_preview': result.get('federal_content_preview', '')[:300] + "...",
                            'relevance_score': result.get('relevance_score', 0)
                        })
                
                test_result['results'] = processed_results
                
                # Generate analysis
                test_result['analysis'] = self.analyze_results(results, test_query)
                
            else:
                test_result['success'] = False
                test_result['error'] = 'No results found'
                test_result['result_count'] = 0
            
        except Exception as e:
            test_result['success'] = False
            test_result['error'] = str(e)
            test_result['traceback'] = traceback.format_exc()
        
        return test_result
    
    def analyze_results(self, results: List, test_query: Dict) -> Dict[str, Any]:
        """Analyze test results for business insights"""
        analysis = {
            'total_results': len(results),
            'authority_distribution': {},
            'source_distribution': {},
            'average_relevance': 0,
            'business_insights': []
        }
        
        if not results:
            return analysis
        
        # Analyze authority levels
        authority_counts = {}
        source_counts = {}
        total_relevance = 0
        
        for result in results:
            if isinstance(result, QueryResult):
                # Authority distribution
                auth_level = result.authority_level
                authority_counts[auth_level] = authority_counts.get(auth_level, 0) + 1
                
                # Source distribution
                source = result.source_type
                source_counts[source] = source_counts.get(source, 0) + 1
                
                # Relevance
                total_relevance += result.relevance_score
            
            elif isinstance(result, dict):
                # Handle mapping results
                source = result.get('federal_source_type', 'Unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
                total_relevance += result.get('relevance_score', 0)
        
        analysis['authority_distribution'] = authority_counts
        analysis['source_distribution'] = source_counts
        analysis['average_relevance'] = total_relevance / len(results) if results else 0
        
        # Generate business insights
        insights = []
        
        if 'statutory' in authority_counts:
            insights.append(f"Found {authority_counts['statutory']} statutory sources - highest authority level")
        
        if 'regulatory' in authority_counts:
            insights.append(f"Found {authority_counts['regulatory']} regulatory sources - binding implementation")
        
        if len(source_counts) > 3:
            insights.append(f"Results span {len(source_counts)} different source types - comprehensive coverage")
        
        if test_query['test_type'] == 'cross_jurisdictional':
            insights.append("Cross-jurisdictional analysis reveals federal-state implementation patterns")
        
        analysis['business_insights'] = insights
        
        return analysis
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n" + "="*80)
        print("📋 PRODUCTION TEST SUMMARY REPORT")
        print("="*80)
        
        # Overall statistics
        print(f"📊 Test Statistics:")
        print(f"   Total Tests: {self.test_results['total_tests']}")
        print(f"   Successful: {self.test_results['successful_tests']}")
        print(f"   Failed: {self.test_results['failed_tests']}")
        success_rate = (self.test_results['successful_tests'] / self.test_results['total_tests']) * 100
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Test type breakdown
        test_types = {}
        for test in self.test_results['test_details']:
            test_type = test.get('test_type', 'unknown')
            test_types[test_type] = test_types.get(test_type, 0) + 1
        
        print(f"\n📈 Test Type Distribution:")
        for test_type, count in test_types.items():
            print(f"   {test_type}: {count} tests")
        
        # Business value demonstration
        print(f"\n💼 Business Value Demonstration:")
        successful_tests = [t for t in self.test_results['test_details'] if t.get('success', False)]
        
        total_results = sum(t.get('result_count', 0) for t in successful_tests)
        print(f"   Total Results Retrieved: {total_results}")
        
        authority_sources = set()
        for test in successful_tests:
            for result in test.get('results', []):
                if isinstance(result, dict) and 'authority_level' in result:
                    authority_sources.add(result['authority_level'])
        
        print(f"   Authority Levels Accessed: {len(authority_sources)}")
        print(f"   Source Types: {', '.join(authority_sources)}")
        
        # Export detailed results
        self.export_results()
    
    def export_results(self):
        """Export results in JSON and Markdown formats"""
        
        # Export JSON
        json_file = self.output_dir / f"production_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed results exported to: {json_file}")
        
        # Export Markdown
        md_file = self.output_dir / f"production_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        self.generate_markdown_report(md_file)
        
        print(f"📄 Markdown report exported to: {md_file}")
    
    def generate_markdown_report(self, md_file: Path):
        """Generate comprehensive markdown report"""
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# Unified LIHTC RAG System - Production Test Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
            f.write(f"**Test Suite:** Production Query Validation  \n")
            f.write(f"**Total Tests:** {self.test_results['total_tests']}  \n")
            f.write(f"**Success Rate:** {(self.test_results['successful_tests'] / self.test_results['total_tests']) * 100:.1f}%  \n\n")
            
            f.write("## Executive Summary\n\n")
            f.write("This report demonstrates the comprehensive capabilities of the Unified LIHTC RAG System ")
            f.write("for real-world Low-Income Housing Tax Credit research and compliance analysis.\n\n")
            
            f.write("### Key Capabilities Tested\n\n")
            f.write("- **Authority-Based Search**: Federal statutory vs regulatory hierarchies\n")
            f.write("- **Cross-Jurisdictional Analysis**: Federal vs state requirement comparisons\n")
            f.write("- **Effective Date Filtering**: Time-sensitive regulation searches\n")
            f.write("- **Entity Recognition**: Specific amounts, percentages, and deadlines\n")
            f.write("- **Conflict Resolution**: Automated federal-state conflict detection\n")
            f.write("- **Federal-State Mapping**: Implementation tracking across jurisdictions\n\n")
            
            f.write("## Test Results Detail\n\n")
            
            for i, test in enumerate(self.test_results['test_details'], 1):
                f.write(f"### {i}. {test['test_name']}\n\n")
                f.write(f"**Query:** {test['query']}  \n")
                f.write(f"**Type:** {test['test_type']}  \n")
                f.write(f"**Business Context:** {test['business_context']}  \n")
                f.write(f"**Status:** {'✅ PASSED' if test.get('success', False) else '❌ FAILED'}  \n")
                
                if test.get('success', False):
                    f.write(f"**Results Found:** {test.get('result_count', 0)}  \n\n")
                    
                    # Show sample results
                    if test.get('results'):
                        f.write("#### Sample Results\n\n")
                        for j, result in enumerate(test['results'][:3], 1):
                            f.write(f"**Result {j}:**\n")
                            if 'authority_level' in result:
                                f.write(f"- **Authority:** {result.get('authority_level', 'N/A')} (Score: {result.get('authority_score', 0)})\n")
                                f.write(f"- **Source:** {result.get('source_type', 'N/A')}\n")
                                f.write(f"- **Section:** {result.get('section_reference', 'N/A')}\n")
                                f.write(f"- **Content:** {result.get('content_preview', 'N/A')}\n\n")
                            else:
                                f.write(f"- **Federal Source:** {result.get('federal_source_type', 'N/A')}\n")
                                f.write(f"- **Implementing States:** {len(result.get('implementing_states', []))} states\n")
                                f.write(f"- **Content:** {result.get('content_preview', 'N/A')}\n\n")
                    
                    # Analysis insights
                    if test.get('analysis', {}).get('business_insights'):
                        f.write("#### Business Insights\n\n")
                        for insight in test['analysis']['business_insights']:
                            f.write(f"- {insight}\n")
                        f.write("\n")
                
                else:
                    f.write(f"**Error:** {test.get('error', 'Unknown error')}  \n\n")
                
                f.write("---\n\n")
            
            f.write("## Business Value Summary\n\n")
            f.write("### For LIHTC Professionals\n\n")
            f.write("1. **Compliance Officers**: Automated monitoring requirement lookups\n")
            f.write("2. **Property Managers**: Income limit and restriction verification\n")
            f.write("3. **Developers**: Basis calculation and timeline requirements\n")
            f.write("4. **Allocation Agencies**: Current credit ceiling and inflation adjustments\n")
            f.write("5. **Legal Counsel**: Authority hierarchy and conflict resolution\n\n")
            
            f.write("### System Capabilities\n\n")
            f.write("- **Multi-Source Integration**: Federal and state sources in unified search\n")
            f.write("- **Authority Ranking**: Automatic prioritization by legal hierarchy\n")
            f.write("- **Conflict Detection**: Identifies federal-state requirement differences\n")
            f.write("- **Time-Sensitive Search**: Effective date filtering for current regulations\n")
            f.write("- **Entity Recognition**: Specific amounts, percentages, and deadlines\n")
            f.write("- **Cross-Reference Mapping**: Related requirement identification\n\n")
            
            f.write("### Performance Metrics\n\n")
            successful_tests = [t for t in self.test_results['test_details'] if t.get('success', False)]
            total_results = sum(t.get('result_count', 0) for t in successful_tests)
            
            f.write(f"- **Total Results Retrieved:** {total_results}\n")
            f.write(f"- **Average Results per Query:** {total_results / len(successful_tests) if successful_tests else 0:.1f}\n")
            f.write(f"- **Success Rate:** {(self.test_results['successful_tests'] / self.test_results['total_tests']) * 100:.1f}%\n")
            f.write(f"- **Test Coverage:** {len(self.test_queries)} real-world scenarios\n\n")
            
            f.write("---\n\n")
            f.write("*Report generated by Unified LIHTC RAG Production Test Suite*  \n")
            f.write("*Structured Consultants LLC - Advanced LIHTC Technology Solutions*\n")

def main():
    """Main execution function"""
    
    # Configuration
    base_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets"
    output_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/test_results"
    
    print("🔧 Initializing Production Test Suite...")
    print(f"📁 Base directory: {base_dir}")
    print(f"📁 Output directory: {output_dir}")
    
    # Initialize and run test suite
    test_suite = ProductionTestSuite(base_dir, output_dir)
    
    try:
        results = test_suite.run_all_tests()
        
        print("\n" + "="*80)
        print("✅ Production Test Suite Completed Successfully!")
        print(f"📊 Final Results: {results['successful_tests']}/{results['total_tests']} tests passed")
        print(f"📁 Detailed reports saved to: {output_dir}")
        print("="*80)
        
        return results
        
    except Exception as e:
        print(f"\n❌ Test Suite Failed: {str(e)}")
        print(f"🔍 Error details: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    main()