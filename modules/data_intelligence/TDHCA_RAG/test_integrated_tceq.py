#!/usr/bin/env python3
"""
Test Integrated TCEQ Environmental Screening - First 10 Sites
"""

from streamlined_comprehensive_analyzer import StreamlinedComprehensiveLIHTCAnalyzer
import pandas as pd

def test_integrated_tceq():
    print("🧪 TESTING INTEGRATED TCEQ ENVIRONMENTAL SCREENING - First 10 sites")
    print("=" * 70)
    
    analyzer = StreamlinedComprehensiveLIHTCAnalyzer()
    
    # Load base data and limit to first 10 sites
    df = pd.read_excel(analyzer.qct_dda_file)
    test_df = df.head(10).copy()
    
    print(f"📊 Testing TCEQ environmental screening with {len(test_df)} sites")
    
    # Load TCEQ datasets
    print("\n📊 Loading TCEQ environmental datasets...")
    tceq_datasets = analyzer.load_tceq_datasets()
    if tceq_datasets:
        dry_count = len(tceq_datasets['dry_cleaners'])
        enf_count = len(tceq_datasets['enforcement'])
        print(f"✅ Loaded {dry_count:,} dry cleaners + {enf_count:,} enforcement sites")
    
    # Initialize environmental columns
    test_df['Environmental_Risk_Level'] = 'UNDETERMINED'
    test_df['Environmental_Risk_Score'] = 8
    test_df['Environmental_DD_Cost'] = 5000
    test_df['Environmental_Concerns_Count'] = 0
    
    env_screened = 0
    
    for idx, site in test_df.iterrows():
        city = site.get('City', 'Unknown')
        lat = site.get('Latitude')
        lng = site.get('Longitude')
        
        print(f"\n   Site {idx}: {city}")
        print(f"      Coordinates: {lat:.4f}, {lng:.4f}" if pd.notna(lat) else "      No coordinates")
        
        if pd.notna(lat) and pd.notna(lng):
            env_result = analyzer.screen_environmental_concerns(lat, lng)
            
            test_df.loc[idx, 'Environmental_Risk_Level'] = env_result['overall_risk']
            test_df.loc[idx, 'Environmental_Risk_Score'] = env_result['risk_score']
            test_df.loc[idx, 'Environmental_DD_Cost'] = env_result['dd_cost']
            test_df.loc[idx, 'Environmental_Concerns_Count'] = env_result['total_concerns']
            
            env_screened += 1
            
            # Display results
            risk = env_result['overall_risk']
            score = env_result['risk_score']
            cost = env_result['dd_cost']
            concerns = env_result['total_concerns']
            
            print(f"      ✅ Risk: {risk} | Score: {score}/15 | DD Cost: ${cost:,} | Concerns: {concerns}")
        else:
            print(f"      ❌ Skipped - no coordinates")
    
    print(f"\n✅ TCEQ ENVIRONMENTAL TEST COMPLETE: {env_screened}/{len(test_df)} sites screened")
    
    # Show results summary
    print(f"\nENVIRONMENTAL SCREENING RESULTS:")
    for idx, site in test_df.iterrows():
        city = site.get('City', 'Unknown')
        risk = site.get('Environmental_Risk_Level', 'Unknown')
        score = site.get('Environmental_Risk_Score', 0)
        cost = site.get('Environmental_DD_Cost', 0)
        concerns = site.get('Environmental_Concerns_Count', 0)
        print(f"  {city}: {risk} | Score {score}/15 | ${cost:,} DD | {concerns} concerns")
    
    return test_df

if __name__ == "__main__":
    result = test_integrated_tceq()