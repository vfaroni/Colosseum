#!/usr/bin/env python3
"""
Integration Test for Land Use Analyzer in BOTN Pipeline

Tests the land use analyzer with real CoStar data to validate:
1. 90%+ accuracy requirement
2. California statewide coverage
3. Handles 200-350 sites efficiently
4. Integration with existing BOTN pipeline
"""

import sys
import pandas as pd
import numpy as np
import time
from pathlib import Path
from typing import Dict, Any, List

# Add the analyzers directory to path
sys.path.append(str(Path(__file__).parent))

from land_use_analyzer import LandUseAnalyzer, LandUseResult


class MockSiteInfo:
    """Mock SiteInfo class for testing"""
    def __init__(self, row):
        self.secondary_type = row.get('Secondary Type')
        self.zoning = row.get('Zoning')
        self.latitude = row.get('Latitude')
        self.longitude = row.get('Longitude')
        self.property_type = row.get('Property Type')
        self.property_address = row.get('Property Address', 'Unknown')
        self.city = row.get('City', 'Unknown')
        self.county = row.get('County Name', 'Unknown')


def test_land_use_accuracy(df: pd.DataFrame, analyzer: LandUseAnalyzer) -> Dict[str, Any]:
    """Test accuracy against known prohibited uses"""
    
    results = {
        'total_tested': 0,
        'industrial_sites': {'total': 0, 'correctly_flagged': 0, 'missed': []},
        'agricultural_sites': {'total': 0, 'correctly_flagged': 0, 'missed': []},
        'commercial_sites': {'total': 0, 'correctly_allowed': 0, 'false_positives': []},
        'residential_sites': {'total': 0, 'correctly_allowed': 0, 'false_positives': []},
        'accuracy_rate': 0.0,
        'processing_time': 0.0
    }
    
    start_time = time.time()
    
    for i, row in df.iterrows():
        site = MockSiteInfo(row)
        result = analyzer.analyze(site)
        results['total_tested'] += 1
        
        secondary_type = site.secondary_type
        if not secondary_type or pd.isna(secondary_type) or not isinstance(secondary_type, str):
            continue
            
        # Test Industrial sites (should be flagged as prohibited)
        if 'Industrial' in secondary_type:
            results['industrial_sites']['total'] += 1
            if not result['is_suitable']:
                results['industrial_sites']['correctly_flagged'] += 1
            else:
                results['industrial_sites']['missed'].append({
                    'address': site.property_address,
                    'secondary_type': secondary_type,
                    'result': result
                })
        
        # Test Agricultural sites (should be flagged as prohibited)
        elif 'Agricultural' in secondary_type:
            results['agricultural_sites']['total'] += 1
            if not result['is_suitable']:
                results['agricultural_sites']['correctly_flagged'] += 1
            else:
                results['agricultural_sites']['missed'].append({
                    'address': site.property_address,
                    'secondary_type': secondary_type,
                    'result': result
                })
        
        # Test Commercial sites (should generally be allowed)
        elif 'Commercial' in secondary_type:
            results['commercial_sites']['total'] += 1
            if result['is_suitable']:
                results['commercial_sites']['correctly_allowed'] += 1
            else:
                results['commercial_sites']['false_positives'].append({
                    'address': site.property_address,
                    'secondary_type': secondary_type,
                    'prohibited_uses': result.get('prohibited_uses', [])
                })
        
        # Test Residential sites (should be allowed)
        elif 'Residential' in secondary_type:
            results['residential_sites']['total'] += 1
            if result['is_suitable']:
                results['residential_sites']['correctly_allowed'] += 1
            else:
                results['residential_sites']['false_positives'].append({
                    'address': site.property_address,
                    'secondary_type': secondary_type,
                    'prohibited_uses': result.get('prohibited_uses', [])
                })
    
    results['processing_time'] = time.time() - start_time
    
    # Calculate accuracy rate
    correct_predictions = (
        results['industrial_sites']['correctly_flagged'] +
        results['agricultural_sites']['correctly_flagged'] +
        results['commercial_sites']['correctly_allowed'] +
        results['residential_sites']['correctly_allowed']
    )
    
    total_categorized = (
        results['industrial_sites']['total'] +
        results['agricultural_sites']['total'] +
        results['commercial_sites']['total'] +
        results['residential_sites']['total']
    )
    
    if total_categorized > 0:
        results['accuracy_rate'] = (correct_predictions / total_categorized) * 100
    
    return results


def test_performance_efficiency(df: pd.DataFrame, analyzer: LandUseAnalyzer) -> Dict[str, Any]:
    """Test processing efficiency for 200-350 sites"""
    
    # Test with different batch sizes
    batch_sizes = [50, 100, 200, 350]
    performance_results = {}
    
    for batch_size in batch_sizes:
        if batch_size > len(df):
            continue
            
        test_df = df.head(batch_size)
        start_time = time.time()
        
        # Process batch
        successful_analyses = 0
        failed_analyses = 0
        
        for i, row in test_df.iterrows():
            site = MockSiteInfo(row)
            try:
                result = analyzer.analyze(site)
                if 'error' not in result:
                    successful_analyses += 1
                else:
                    failed_analyses += 1
            except Exception as e:
                failed_analyses += 1
        
        processing_time = time.time() - start_time
        
        performance_results[batch_size] = {
            'total_sites': batch_size,
            'successful_analyses': successful_analyses,
            'failed_analyses': failed_analyses,
            'processing_time_seconds': processing_time,
            'sites_per_second': batch_size / processing_time if processing_time > 0 else 0,
            'success_rate': (successful_analyses / batch_size) * 100
        }
    
    return performance_results


def test_california_coverage(df: pd.DataFrame, analyzer: LandUseAnalyzer) -> Dict[str, Any]:
    """Test coverage across California counties"""
    
    coverage_results = {
        'total_counties': 0,
        'counties_tested': set(),
        'county_analysis_success': {},
        'coverage_issues': []
    }
    
    # Group by county
    if 'County Name' in df.columns:
        counties = df['County Name'].dropna().unique()
        coverage_results['total_counties'] = len(counties)
        
        for county in counties:
            county_df = df[df['County Name'] == county]
            coverage_results['counties_tested'].add(county)
            
            # Test a few sites from each county
            test_sites = county_df.head(3)
            successful = 0
            total = len(test_sites)
            
            for i, row in test_sites.iterrows():
                site = MockSiteInfo(row)
                try:
                    result = analyzer.analyze(site)
                    if 'error' not in result:
                        successful += 1
                except Exception as e:
                    coverage_results['coverage_issues'].append({
                        'county': county,
                        'address': row.get('Property Address', 'Unknown'),
                        'error': str(e)
                    })
            
            coverage_results['county_analysis_success'][county] = {
                'successful': successful,
                'total': total,
                'success_rate': (successful / total) * 100 if total > 0 else 0
            }
    
    return coverage_results


def run_comprehensive_test():
    """Run comprehensive integration test"""
    
    print("🏛️ COLOSSEUM LAND USE ANALYZER - COMPREHENSIVE INTEGRATION TEST")
    print("=" * 70)
    
    # Load CoStar data
    file_path = '/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/botn_engine/Sites/CostarExport_HighResource_Final_20250727_191447.xlsx'
    
    try:
        df = pd.read_excel(file_path)
        print(f"✅ Loaded CoStar dataset: {len(df)} sites")
    except Exception as e:
        print(f"❌ Failed to load CoStar data: {e}")
        return
    
    # Initialize analyzer
    analyzer = LandUseAnalyzer()
    print("✅ Land Use Analyzer initialized")
    
    print("\n📊 ACCURACY TEST")
    print("-" * 30)
    accuracy_results = test_land_use_accuracy(df, analyzer)
    
    print(f"Total sites tested: {accuracy_results['total_tested']}")
    print(f"Overall accuracy rate: {accuracy_results['accuracy_rate']:.1f}%")
    print(f"Processing time: {accuracy_results['processing_time']:.2f} seconds")
    
    # Industrial sites
    industrial = accuracy_results['industrial_sites']
    if industrial['total'] > 0:
        industrial_accuracy = (industrial['correctly_flagged'] / industrial['total']) * 100
        print(f"Industrial sites: {industrial['correctly_flagged']}/{industrial['total']} correctly flagged ({industrial_accuracy:.1f}%)")
        if industrial['missed']:
            print(f"  ⚠️  Missed {len(industrial['missed'])} industrial sites")
    
    # Agricultural sites
    agricultural = accuracy_results['agricultural_sites']
    if agricultural['total'] > 0:
        agricultural_accuracy = (agricultural['correctly_flagged'] / agricultural['total']) * 100
        print(f"Agricultural sites: {agricultural['correctly_flagged']}/{agricultural['total']} correctly flagged ({agricultural_accuracy:.1f}%)")
        if agricultural['missed']:
            print(f"  ⚠️  Missed {len(agricultural['missed'])} agricultural sites")
    
    # Commercial sites
    commercial = accuracy_results['commercial_sites']
    if commercial['total'] > 0:
        commercial_accuracy = (commercial['correctly_allowed'] / commercial['total']) * 100
        print(f"Commercial sites: {commercial['correctly_allowed']}/{commercial['total']} correctly allowed ({commercial_accuracy:.1f}%)")
        if commercial['false_positives']:
            print(f"  ⚠️  {len(commercial['false_positives'])} false positives")
    
    # Residential sites
    residential = accuracy_results['residential_sites']
    if residential['total'] > 0:
        residential_accuracy = (residential['correctly_allowed'] / residential['total']) * 100
        print(f"Residential sites: {residential['correctly_allowed']}/{residential['total']} correctly allowed ({residential_accuracy:.1f}%)")
        if residential['false_positives']:
            print(f"  ⚠️  {len(residential['false_positives'])} false positives")
    
    print(f"\n⚡ PERFORMANCE TEST")
    print("-" * 30)
    performance_results = test_performance_efficiency(df, analyzer)
    
    for batch_size, results in performance_results.items():
        print(f"Batch size {batch_size}:")
        print(f"  Processing time: {results['processing_time_seconds']:.2f}s")
        print(f"  Sites per second: {results['sites_per_second']:.1f}")
        print(f"  Success rate: {results['success_rate']:.1f}%")
    
    print(f"\n🗺️ CALIFORNIA COVERAGE TEST")
    print("-" * 30)
    coverage_results = test_california_coverage(df, analyzer)
    
    print(f"Total counties in dataset: {coverage_results['total_counties']}")
    print(f"Counties tested: {len(coverage_results['counties_tested'])}")
    
    if coverage_results['coverage_issues']:
        print(f"⚠️  Coverage issues found: {len(coverage_results['coverage_issues'])}")
        for issue in coverage_results['coverage_issues'][:3]:  # Show first 3
            print(f"  - {issue['county']}: {issue['error']}")
    
    print(f"\n🎯 FINAL ASSESSMENT")
    print("-" * 30)
    
    # Check if we meet requirements
    meets_accuracy = accuracy_results['accuracy_rate'] >= 90.0
    meets_performance = any(
        r['sites_per_second'] >= 10 for r in performance_results.values()
    )
    meets_coverage = len(coverage_results['counties_tested']) >= 10
    
    print(f"✅ 90%+ accuracy requirement: {'PASS' if meets_accuracy else 'FAIL'} ({accuracy_results['accuracy_rate']:.1f}%)")
    print(f"✅ Performance requirement: {'PASS' if meets_performance else 'FAIL'}")
    print(f"✅ California coverage: {'PASS' if meets_coverage else 'FAIL'} ({len(coverage_results['counties_tested'])} counties)")
    
    overall_pass = meets_accuracy and meets_performance and meets_coverage
    print(f"\n🏆 OVERALL RESULT: {'PASS - READY FOR PRODUCTION' if overall_pass else 'FAIL - NEEDS IMPROVEMENT'}")
    
    return {
        'accuracy_results': accuracy_results,
        'performance_results': performance_results,
        'coverage_results': coverage_results,
        'overall_pass': overall_pass
    }


if __name__ == "__main__":
    run_comprehensive_test()