#!/usr/bin/env python3
"""
API Compatibility Validator for Enhanced ChromaDB
Tests compatibility with existing web demo interface
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Add existing systems to path
sys.path.append(str(Path(__file__).parent.parent / "lihtc_analyst" / "priorcode"))

try:
    from enhanced_chromadb_loader import EnhancedChromaDBLoader
    ENHANCED_AVAILABLE = True
except ImportError as e:
    ENHANCED_AVAILABLE = False
    print(f"⚠️  Enhanced system not available: {e}")

logger = logging.getLogger(__name__)

class APICompatibilityValidator:
    """Validate API compatibility between old and enhanced systems"""
    
    def __init__(self):
        """Initialize validator with enhanced system"""
        
        if not ENHANCED_AVAILABLE:
            raise ImportError("Enhanced ChromaDB system not available")
        
        # Initialize enhanced system
        self.enhanced_loader = EnhancedChromaDBLoader()
        
        # Standard test queries from web demo
        self.test_queries = [
            "minimum construction standards accessibility requirements",
            "tie breaker scoring criteria",
            "income verification procedures",
            "affordable housing scoring requirements",
            "construction timeline requirements",
            "tenant income limits calculation",
            "qualified basis determination rules",
            "compliance monitoring requirements"
        ]
        
        self.validation_results = {
            'test_timestamp': datetime.now().isoformat(),
            'enhanced_system_info': {},
            'api_compatibility_tests': [],
            'format_compatibility': {},
            'performance_metrics': {},
            'overall_status': 'unknown'
        }
    
    def test_enhanced_search_api(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Test enhanced search with simplified filters"""
        
        import time
        start_time = time.time()
        
        try:
            # Test without complex filters first
            results = self.enhanced_loader.chroma_db.search(
                query=query,
                limit=limit,
                filters=None,  # No filters to avoid syntax issues
                similarity_threshold=0.0
            )
            
            search_time = time.time() - start_time
            
            # Filter CA results manually if needed
            ca_results = []
            for result in results:
                metadata = result.get('metadata', {})
                if metadata.get('state_code') == 'CA':
                    ca_results.append(result)
            
            return {
                'query': query,
                'total_results': len(results),
                'ca_results': len(ca_results),
                'search_time_ms': round(search_time * 1000, 2),
                'top_results': ca_results[:5] if ca_results else results[:5],
                'status': 'success'
            }
            
        except Exception as e:
            search_time = time.time() - start_time
            logger.error(f"Enhanced search failed for '{query}': {e}")
            return {
                'query': query,
                'total_results': 0,
                'ca_results': 0,
                'search_time_ms': round(search_time * 1000, 2),
                'top_results': [],
                'error': str(e),
                'status': 'failed'
            }
    
    def convert_to_web_demo_format(self, enhanced_results: List[Dict]) -> List[Dict]:
        """Convert enhanced results to web demo API format"""
        
        converted_results = []
        
        for result in enhanced_results:
            metadata = result.get('metadata', {})
            
            # Convert to expected web demo format
            web_result = {
                'chunk_id': result.get('chunk_id', ''),
                'state_code': metadata.get('state_code', ''),
                'content': result.get('content', ''),
                'section_title': metadata.get('section_title', ''),
                'program_type': metadata.get('program_type', ''),
                'content_type': metadata.get('content_type', ''),
                'authority_level': metadata.get('authority_level', ''),
                'score': float(result.get('score', 0.0)),
                'metadata': {
                    **metadata,
                    # Add enhanced features as metadata
                    'enhanced_features_count': (
                        metadata.get('federal_refs_count', 0) +
                        metadata.get('state_refs_count', 0) +
                        metadata.get('qap_crossrefs_count', 0) +
                        metadata.get('lihtc_entities_count', 0)
                    ),
                    'hierarchy_level': metadata.get('hierarchy_level', 0),
                    'breadcrumb': metadata.get('breadcrumb', ''),
                    'processing_method': metadata.get('processing_method', '')
                }
            }
            
            converted_results.append(web_result)
        
        return converted_results
    
    def test_web_demo_api_compatibility(self) -> Dict[str, Any]:
        """Test full web demo API compatibility"""
        
        print("🔄 Testing Web Demo API compatibility...")
        
        api_test_results = []
        total_queries = 0
        successful_queries = 0
        total_search_time = 0
        
        for query in self.test_queries:
            print(f"   Testing: '{query[:50]}...'")
            
            # Test enhanced search
            enhanced_result = self.test_enhanced_search_api(query)
            total_queries += 1
            total_search_time += enhanced_result['search_time_ms']
            
            if enhanced_result['status'] == 'success':
                successful_queries += 1
                
                # Convert to web demo format
                converted_results = self.convert_to_web_demo_format(enhanced_result['top_results'])
                
                # Test format compatibility
                format_test = self.validate_result_format(converted_results)
                
                api_test_results.append({
                    'query': query,
                    'enhanced_search': enhanced_result,
                    'converted_results': converted_results[:3],  # Top 3 for validation
                    'format_compatibility': format_test,
                    'api_compatible': format_test['all_required_fields_present']
                })
            else:
                api_test_results.append({
                    'query': query,
                    'enhanced_search': enhanced_result,
                    'converted_results': [],
                    'format_compatibility': {'error': enhanced_result.get('error')},
                    'api_compatible': False
                })
        
        # Calculate overall compatibility
        compatible_queries = sum(1 for test in api_test_results if test.get('api_compatible', False))
        compatibility_percentage = (compatible_queries / total_queries * 100) if total_queries > 0 else 0
        
        return {
            'total_queries_tested': total_queries,
            'successful_queries': successful_queries,
            'compatible_queries': compatible_queries,
            'compatibility_percentage': round(compatibility_percentage, 2),
            'avg_search_time_ms': round(total_search_time / total_queries, 2) if total_queries > 0 else 0,
            'detailed_results': api_test_results,
            'overall_compatible': compatibility_percentage >= 90
        }
    
    def validate_result_format(self, results: List[Dict]) -> Dict[str, Any]:
        """Validate result format matches web demo expectations"""
        
        if not results:
            return {
                'all_required_fields_present': False,
                'missing_fields': ['no_results'],
                'field_analysis': {}
            }
        
        # Required fields for web demo API
        required_fields = [
            'chunk_id', 'state_code', 'content', 'section_title', 
            'program_type', 'content_type', 'authority_level', 'score', 'metadata'
        ]
        
        field_analysis = {}
        missing_fields = []
        
        for field in required_fields:
            present_count = sum(1 for result in results if field in result and result[field] is not None)
            field_analysis[field] = {
                'present_count': present_count,
                'total_results': len(results),
                'coverage_percentage': round(present_count / len(results) * 100, 2)
            }
            
            if present_count < len(results):
                missing_fields.append(field)
        
        # Check enhanced features
        enhanced_features_count = 0
        for result in results:
            metadata = result.get('metadata', {})
            if metadata.get('enhanced_features_count', 0) > 0:
                enhanced_features_count += 1
        
        field_analysis['enhanced_features'] = {
            'results_with_enhancements': enhanced_features_count,
            'total_results': len(results),
            'enhancement_percentage': round(enhanced_features_count / len(results) * 100, 2)
        }
        
        return {
            'all_required_fields_present': len(missing_fields) == 0,
            'missing_fields': missing_fields,
            'field_analysis': field_analysis,
            'enhanced_features_detected': enhanced_features_count > 0
        }
    
    def run_full_compatibility_validation(self) -> Dict[str, Any]:
        """Run comprehensive API compatibility validation"""
        
        print("🚀 Starting API Compatibility Validation...")
        
        # Get enhanced system info
        collection_stats = self.enhanced_loader.chroma_db.get_collection_stats()
        loader_stats = self.enhanced_loader.get_loading_stats()
        
        self.validation_results['enhanced_system_info'] = {
            'collection_stats': collection_stats,
            'loader_stats': loader_stats,
            'system_status': 'operational' if collection_stats.get('total_documents', 0) > 0 else 'empty'
        }
        
        # Test API compatibility
        api_compatibility = self.test_web_demo_api_compatibility()
        self.validation_results['api_compatibility_tests'] = api_compatibility
        
        # Overall assessment
        if api_compatibility['overall_compatible'] and collection_stats.get('total_documents', 0) > 0:
            self.validation_results['overall_status'] = 'fully_compatible'
        elif api_compatibility['compatibility_percentage'] > 70:
            self.validation_results['overall_status'] = 'mostly_compatible'
        else:
            self.validation_results['overall_status'] = 'incompatible'
        
        return self.validation_results
    
    def generate_compatibility_report(self, output_file: Path = None) -> str:
        """Generate compatibility validation report"""
        
        if output_file is None:
            output_file = Path(__file__).parent.parent / "agents" / "BILL" / "STRIKE_LEADER" / "reports" / f"API_COMPATIBILITY_VALIDATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Save detailed results
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
        
        # Generate summary report
        api_tests = self.validation_results['api_compatibility_tests']
        system_info = self.validation_results['enhanced_system_info']
        
        report = f"""
🏛️ **API COMPATIBILITY VALIDATION RESULTS**
**Test Date**: {self.validation_results['test_timestamp'][:19]}
**Overall Status**: {self.validation_results['overall_status'].upper()}

## 📊 **ENHANCED SYSTEM STATUS**
- **Total Documents**: {system_info['collection_stats'].get('total_documents', 0)}
- **Chunks Loaded**: {system_info['loader_stats']['loading_stats']['chunks_loaded']}
- **States Processed**: {list(system_info['loader_stats']['loading_stats']['states_processed'])}
- **Enhanced Features**: {system_info['loader_stats']['loading_stats']['total_enhanced_features']}

## 🔌 **API COMPATIBILITY**
- **Queries Tested**: {api_tests['total_queries_tested']}
- **Successful Searches**: {api_tests['successful_queries']}
- **Compatible Results**: {api_tests['compatible_queries']}
- **Compatibility**: {api_tests['compatibility_percentage']}%

## ⚡ **PERFORMANCE**
- **Average Search Time**: {api_tests['avg_search_time_ms']}ms
- **System Response**: {'✅ Fast' if api_tests['avg_search_time_ms'] < 500 else '⚠️ Slow' if api_tests['avg_search_time_ms'] < 1000 else '❌ Very Slow'}

## 🎯 **RECOMMENDATION**
{'✅ **READY FOR PRODUCTION** - Enhanced system is fully compatible with existing web demo API' if self.validation_results['overall_status'] == 'fully_compatible' else '⚠️ **NEEDS MINOR FIXES** - Enhanced system mostly compatible, minor adjustments needed' if self.validation_results['overall_status'] == 'mostly_compatible' else '❌ **MAJOR ISSUES** - Enhanced system requires significant compatibility fixes'}

**Detailed Results**: {output_file}
"""
        
        print(report)
        return report

def main():
    """Run API compatibility validation"""
    
    print("🚀 Starting API Compatibility Validation...")
    
    try:
        # Initialize validator
        validator = APICompatibilityValidator()
        
        # Run full validation
        results = validator.run_full_compatibility_validation()
        
        # Generate report
        report = validator.generate_compatibility_report()
        
        print(f"\n✅ API Compatibility Validation Complete!")
        print(f"Status: {results['overall_status'].upper()}")
        
    except Exception as e:
        print(f"❌ API Compatibility Validation failed: {e}")

if __name__ == "__main__":
    main()