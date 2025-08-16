#!/usr/bin/env python3
"""
Test Phase 2 Environmental Screening with First 5 Sites
"""

import pandas as pd
from ultimate_comprehensive_lihtc_analyzer import UltimateComprehensiveLIHTCAnalyzer

def test_environmental():
    print("🧪 TESTING PHASE 2: Environmental Screening (First 5 sites)")
    print("=" * 60)
    
    analyzer = UltimateComprehensiveLIHTCAnalyzer()
    
    # Load base data
    base_df = analyzer.load_base_data()
    if base_df is None:
        print("❌ Failed to load base data")
        return
    
    # Test with first 5 sites only
    test_df = base_df.head(5).copy()
    print(f"📊 Testing environmental screening with {len(test_df)} sites")
    
    # Run environmental screening
    result_df = analyzer.phase2_environmental_screening(test_df)
    
    # Show results
    print("\n📊 Environmental Screening Results:")
    for idx, site in result_df.iterrows():
        risk = site.get('Environmental_Risk_Level', 'UNKNOWN')
        distance = site.get('Closest_Contamination_Distance', 'None')
        cost = site.get('Environmental_DD_Cost', 0)
        address = site.get('Address', 'Unknown')[:40]
        
        print(f"   {address}: {risk} risk, {distance:.2f} mi, ${cost:,} DD cost" if distance != 'None' else f"   {address}: {risk} risk, No contamination nearby")
    
    return result_df

if __name__ == "__main__":
    test_environmental()