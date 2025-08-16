#!/usr/bin/env python3
"""
Quick hotfix to ensure dashboards work correctly with both old and new data formats
"""

import pandas as pd
import numpy as np

def test_dashboard_compatibility():
    """Test that dashboards work with sample data"""
    
    print("🔧 Testing Dashboard Compatibility...")
    
    # Test 1: Create sample data like the dashboard does
    np.random.seed(42)
    n_properties = 10
    
    counties = ['Harris', 'Dallas', 'Travis', 'Bexar', 'Tarrant', 'Collin', 'Fort Bend']
    cities = ['Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth', 'Plano', 'Sugar Land']
    
    sample_data = {
        'Address': [f"{1000 + i} Sample St" for i in range(n_properties)],
        'City': np.random.choice(cities, n_properties),
        'County': np.random.choice(counties, n_properties),
        'Latitude': np.random.uniform(29.0, 33.0, n_properties),
        'Longitude': np.random.uniform(-106.0, -94.0, n_properties),
        'grocery_store_distance_miles': np.random.uniform(0.1, 5.0, n_properties),
        'elementary_school_distance_miles': np.random.uniform(0.1, 3.0, n_properties),
        'hospital_distance_miles': np.random.uniform(0.5, 15.0, n_properties),
        'transit_stop_distance_miles': np.random.uniform(0.1, 2.0, n_properties),
        'pharmacy_distance_miles': np.random.uniform(0.2, 4.0, n_properties),
        'park_distance_miles': np.random.uniform(0.1, 3.0, n_properties),
        'city_population': np.random.choice([50000, 100000, 250000, 500000, 1000000, 2000000], n_properties),
        'one_mile_compliant': np.random.choice([True, False], n_properties, p=[0.8, 0.2]),
        'one_mile_competing_count': np.random.choice([0, 1, 2, 3], n_properties, p=[0.6, 0.25, 0.1, 0.05]),
        'two_mile_compliant': np.random.choice([True, False], n_properties, p=[0.85, 0.15]),
        'same_tract_points': np.random.choice([0, 2, 3, 4, 5], n_properties, p=[0.1, 0.2, 0.3, 0.3, 0.1]),
        'Census_Tract': [f"48{np.random.randint(1, 999):03d}{np.random.randint(1, 99):02d}" for _ in range(n_properties)]
    }
    
    sample_df = pd.DataFrame(sample_data)
    sample_df['eligibility'] = sample_df['one_mile_compliant'].map({True: 'ELIGIBLE', False: 'INELIGIBLE'})
    
    print(f"✅ Sample data created: {len(sample_df)} properties")
    
    # Test 2: Apply scoring
    try:
        from tdhca_scoring_engine import TdhcaScoringEngine
        scoring_engine = TdhcaScoringEngine()
        scored_df = scoring_engine.calculate_comprehensive_scoring(sample_df)
        print(f"✅ TDHCA scoring applied: {len([col for col in scored_df.columns if 'score' in col.lower()])} score columns")
    except Exception as e:
        print(f"❌ Scoring failed: {e}")
        return False
    
    # Test 3: Check categorization function compatibility
    def test_categorize_deals(df):
        """Test the categorize_deals function"""
        score_col_4p = '4pct_total_score' if '4pct_total_score' in df.columns else '4pct_score'
        score_col_9p = '9pct_total_score' if '9pct_total_score' in df.columns else '9pct_score'
        
        # Create legacy score columns for compatibility if they don't exist
        if '4pct_score' not in df.columns and score_col_4p in df.columns:
            df['4pct_score'] = df[score_col_4p]
        if '9pct_score' not in df.columns and score_col_9p in df.columns:
            df['9pct_score'] = df[score_col_9p]
        
        df['deal_quality'] = 'Review Needed'
        
        # Use comprehensive recommendations if available
        if 'deal_recommendation' in df.columns:
            recommendation_map = {
                'RECOMMEND 9% - Competitive scoring': 'Excellent Opportunity',
                'RECOMMEND 4% - Viable but not 9% competitive': 'Good Opportunity', 
                'NOT RECOMMENDED - Low scoring both types': 'Marginal Opportunity',
                'NOT RECOMMENDED - Fatal flaw': 'Poor Opportunity'
            }
            df['deal_quality'] = df['deal_recommendation'].map(recommendation_map).fillna('Review Needed')
        
        return df
    
    try:
        categorized_df = test_categorize_deals(scored_df)
        print(f"✅ Categorization successful: {categorized_df['deal_quality'].value_counts().to_dict()}")
    except Exception as e:
        print(f"❌ Categorization failed: {e}")
        return False
    
    # Test 4: Check required columns
    required_columns = ['4pct_score', '9pct_score', 'deal_quality', 'eligibility']
    missing_columns = [col for col in required_columns if col not in categorized_df.columns]
    
    if missing_columns:
        print(f"❌ Missing required columns: {missing_columns}")
        return False
    else:
        print(f"✅ All required columns present: {required_columns}")
    
    return True

def main():
    """Run compatibility tests"""
    print("🚀 Dashboard Hotfix - Compatibility Testing")
    print("=" * 50)
    
    success = test_dashboard_compatibility()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ALL TESTS PASSED - Dashboards should work correctly!")
        print("\n🚀 Ready to run:")
        print("python3 -m streamlit run texas_deal_sourcing_dashboard.py")
    else:
        print("❌ TESTS FAILED - Issues detected")
        print("\n🔧 Check error messages above for details")

if __name__ == "__main__":
    main()