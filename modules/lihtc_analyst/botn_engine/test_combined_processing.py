#!/usr/bin/env python3
"""
Test Enhanced BOTN Processing with Combined CostarExport Files

This script tests the enhanced BOTN processor with the combined
CostarExport-8-15 file to verify column preservation and functionality.

Author: VITOR WINGMAN
Date: 2025-08-16
"""

import pandas as pd
from pathlib import Path
from enhanced_botn_processor import EnhancedBOTNProcessor
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_enhanced_processing():
    """Test enhanced BOTN processing with combined file"""
    
    print("🏛️ ENHANCED BOTN PROCESSOR - COMBINED FILE TEST")
    print("=" * 60)
    
    # Find the combined file
    sites_dir = Path("/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/lihtc_analyst/botn_engine/Sites")
    
    # Look for the most recent combined file
    combined_files = list(sites_dir.glob("CostarExport_Combined_8-15_*.xlsx"))
    if not combined_files:
        print("❌ No combined CostarExport file found!")
        return
    
    # Use the most recent file
    combined_file = max(combined_files, key=lambda f: f.stat().st_mtime)
    print(f"📁 Using: {combined_file.name}")
    
    # Load original data for baseline
    print(f"\n📊 ORIGINAL DATA ANALYSIS")
    print("-" * 40)
    
    original_df = pd.read_excel(combined_file)
    print(f"Original file shape: {original_df.shape}")
    print(f"Original columns: {len(original_df.columns)}")
    
    # Show breakdown by source file
    if 'Source_File' in original_df.columns:
        source_counts = original_df['Source_File'].value_counts().sort_index()
        print(f"\nSource file breakdown:")
        total_sites = 0
        for source, count in source_counts.items():
            print(f"   {source}: {count:,} sites")
            total_sites += count
        print(f"   Total: {total_sites:,} sites")
    
    # Initialize enhanced processor
    print(f"\n🚀 ENHANCED BOTN PROCESSING")
    print("-" * 40)
    
    processor = EnhancedBOTNProcessor()
    
    # Test with a reasonable sample size
    test_sample_size = 20
    print(f"Processing sample of {test_sample_size} sites for testing...")
    
    # Process sites
    enhanced_df = processor.process_sites(str(combined_file), max_sites=test_sample_size)
    
    print(f"\n✅ PROCESSING COMPLETE")
    print("=" * 60)
    
    # Analyze results
    print(f"📊 RESULTS ANALYSIS")
    print("-" * 40)
    
    print(f"Enhanced file shape: {enhanced_df.shape}")
    print(f"Enhanced columns: {len(enhanced_df.columns)}")
    print(f"Sites processed: {len(enhanced_df)}")
    
    # Column preservation analysis
    print(f"\n📋 COLUMN PRESERVATION ANALYSIS")
    print("-" * 40)
    
    # Expected original columns
    expected_original = [
        'Property Address', 'Property Name', 'Land Area (AC)', 'Land Area (SF)',
        'Property Type', 'Secondary Type', 'Market Name', 'Submarket Name',
        'City', 'County Name', 'State', 'Zip', 'For Sale Price',
        'Sale Company Name', 'Sale Company Address', 'Sale Company City State Zip',
        'Sale Company Phone', 'Sale Company Fax', 'Sale Company Contact',
        'Zoning', 'Parcel Number 1(Min)', 'Parcel Number 2(Max)',
        'True Owner Address', 'True Owner City State Zip', 'True Owner Contact',
        'True Owner Name', 'True Owner Phone', 'Flood Risk Area',
        'Fema Flood Zone', 'FEMA Map Date', 'FEMA Map Identifier',
        'Days On Market', 'Closest Transit Stop', 'Closest Transit Stop Dist (mi)',
        'Closest Transit Stop Walk Time (min)', 'Latitude', 'Longitude'
    ]
    
    # Check preservation
    preserved_count = 0
    missing_columns = []
    
    for col in expected_original:
        if col in enhanced_df.columns:
            preserved_count += 1
            print(f"✅ {col}")
        else:
            missing_columns.append(col)
            print(f"❌ MISSING: {col}")
    
    preservation_rate = (preserved_count / len(expected_original)) * 100
    print(f"\nPreservation Rate: {preserved_count}/{len(expected_original)} ({preservation_rate:.1f}%)")
    
    # Enhancement columns
    expected_enhancements = [
        'hqta_qualified', 'hqta_points', 'hqta_method',
        'terrain_slope_percent', 'terrain_risk_category', 'terrain_suitable',
        'hard_costs_per_unit', 'soft_costs_per_unit', 'total_dev_cost_per_unit',
        'enhancement_timestamp'
    ]
    
    print(f"\n🔧 ENHANCEMENT COLUMNS")
    print("-" * 40)
    
    enhancement_count = 0
    for col in expected_enhancements:
        if col in enhanced_df.columns:
            enhancement_count += 1
            print(f"✅ {col}")
        else:
            print(f"❌ MISSING: {col}")
    
    print(f"\nEnhancement Completeness: {enhancement_count}/{len(expected_enhancements)} ({100*enhancement_count/len(expected_enhancements):.1f}%)")
    
    # Sample site analysis
    print(f"\n📍 SAMPLE SITE ANALYSIS")
    print("-" * 40)
    
    for idx in range(min(3, len(enhanced_df))):
        row = enhanced_df.iloc[idx]
        print(f"\nSite {idx + 1}: {row.get('Property Address', 'Unknown')}")
        print(f"   📍 Location: ({row.get('Latitude', 'N/A')}, {row.get('Longitude', 'N/A')})")
        print(f"   🏛️ County: {row.get('County Name', 'Unknown')}")
        print(f"   🚌 HQTA Qualified: {row.get('hqta_qualified', 'N/A')}")
        print(f"   🏔️ Terrain Risk: {row.get('terrain_risk_category', 'N/A')}")
        print(f"   📈 Slope: {row.get('terrain_slope_percent', 'N/A')}%")
        print(f"   ✅ Suitable: {row.get('terrain_suitable', 'N/A')}")
        print(f"   💰 Hard Costs: ${row.get('hard_costs_per_unit', 'N/A'):,}" if pd.notna(row.get('hard_costs_per_unit')) else "   💰 Hard Costs: N/A")
        print(f"   📋 Source: {row.get('Source_File', 'Unknown')}")
    
    # Performance analysis
    print(f"\n⚡ PERFORMANCE ANALYSIS")
    print("-" * 40)
    
    # Check for terrain analysis coverage
    terrain_analyzed = enhanced_df['terrain_slope_percent'].notna().sum()
    hqta_checked = enhanced_df['hqta_qualified'].notna().sum()
    
    print(f"Terrain analysis coverage: {terrain_analyzed}/{len(enhanced_df)} ({100*terrain_analyzed/len(enhanced_df):.1f}%)")
    print(f"HQTA analysis coverage: {hqta_checked}/{len(enhanced_df)} ({100*hqta_checked/len(enhanced_df):.1f}%)")
    
    # Terrain suitability breakdown
    if terrain_analyzed > 0:
        suitable_sites = enhanced_df['terrain_suitable'].sum()
        print(f"Terrain suitable sites: {suitable_sites}/{terrain_analyzed} ({100*suitable_sites/terrain_analyzed:.1f}%)")
        
        # Risk category breakdown
        risk_categories = enhanced_df['terrain_risk_category'].value_counts()
        print(f"Terrain risk categories:")
        for category, count in risk_categories.items():
            print(f"   {category}: {count} sites")
    
    # HQTA qualification breakdown
    if hqta_checked > 0:
        hqta_qualified = enhanced_df['hqta_qualified'].sum()
        print(f"HQTA qualified sites: {hqta_qualified}/{hqta_checked} ({100*hqta_qualified/hqta_checked:.1f}%)")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = sites_dir / f"Enhanced_BOTN_Test_Results_{timestamp}.xlsx"
    enhanced_df.to_excel(output_file, index=False)
    
    # Create test report
    test_report = {
        'test_timestamp': timestamp,
        'input_file': str(combined_file),
        'output_file': str(output_file),
        'original_shape': original_df.shape,
        'enhanced_shape': enhanced_df.shape,
        'column_preservation_rate': preservation_rate,
        'enhancement_completeness': 100*enhancement_count/len(expected_enhancements),
        'terrain_analysis_coverage': 100*terrain_analyzed/len(enhanced_df),
        'hqta_analysis_coverage': 100*hqta_checked/len(enhanced_df),
        'missing_columns': missing_columns,
        'test_sample_size': test_sample_size
    }
    
    report_file = sites_dir / f"Enhanced_BOTN_Test_Report_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump(test_report, f, indent=2, default=str)
    
    print(f"\n💾 RESULTS SAVED")
    print("-" * 40)
    print(f"Enhanced data: {output_file.name}")
    print(f"Test report: {report_file.name}")
    
    # Final assessment
    print(f"\n🎯 FINAL ASSESSMENT")
    print("=" * 60)
    
    success_criteria = {
        'Column Preservation': preservation_rate >= 95,
        'Enhancement Features': enhancement_count >= 8,
        'Terrain Analysis': terrain_analyzed >= len(enhanced_df) * 0.8,
        'HQTA Analysis': hqta_checked >= len(enhanced_df) * 0.8,
        'No Critical Errors': len(missing_columns) <= 2
    }
    
    all_passed = True
    for criterion, passed in success_criteria.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {criterion}: {status}")
        if not passed:
            all_passed = False
    
    overall_status = "🎉 OVERALL: SUCCESS" if all_passed else "⚠️ OVERALL: NEEDS ATTENTION"
    print(f"\n{overall_status}")
    
    return all_passed, test_report

if __name__ == "__main__":
    success, report = test_enhanced_processing()
    
    if success:
        print("\n🏛️ Enhanced BOTN processor ready for production!")
    else:
        print("\n⚠️ Review test results before deployment.")