#!/usr/bin/env python3
"""
Analyze all 195 Texas sites using pyforma wrapper
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add the parent directory to path so we can import our wrapper
sys.path.append('/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/pyforma_integration/projects/TX_land_analysis')
from pyforma_wrapper import PyformaWrapper

def load_all_195_sites():
    """Load the complete 195 sites dataset"""
    
    excel_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/FINAL_195_Sites_Complete_With_Poverty_20250621_213537.xlsx"
    
    print(f"Loading all 195 sites from: FINAL_195_Sites_Complete_With_Poverty")
    
    try:
        df = pd.read_excel(excel_file, sheet_name='All_195_Sites_Final')
        print(f"✅ Loaded {len(df)} sites with {len(df.columns)} columns")
        return df
    except Exception as e:
        print(f"❌ Error loading sites: {e}")
        return None

def analyze_all_sites():
    """Run pyforma analysis on all 195 sites"""
    
    print("ANALYZING ALL 195 TEXAS SITES WITH PYFORMA")
    print("=" * 60)
    
    # Load data
    df = load_all_195_sites()
    if df is None:
        return None
    
    # Initialize wrapper
    wrapper = PyformaWrapper()
    
    # Store results
    results = []
    
    print(f"\nProcessing {len(df)} sites...")
    
    for idx, site in df.iterrows():
        if idx % 25 == 0:  # Progress update every 25 sites
            print(f"  Processing site {idx+1}/{len(df)}: {site.get('Address', 'Unknown')}")
        
        try:
            # Analyze this site
            result = wrapper.analyze_texas_site(site)
            
            # Add original data for comparison
            result.update({
                'original_index': idx,
                'original_economic_score': site.get('Economic_Score', 0),
                'original_revenue_cost_ratio': site.get('Corrected_Revenue_Cost_Ratio', site.get('Revenue_Cost_Ratio', 0)),
                'original_ranking_4pct': site.get('Ranking_4pct', 'Unknown'),
                'original_ranking_9pct': site.get('Final_9pct_Ranking_With_Poverty', site.get('Ranking_9pct', 'Unknown')),
                'qct_dda_eligible': site.get('Federal_Basis_Boost_30pct', False),
                'poverty_bonus': site.get('Low_Poverty_Bonus_9pct', 0),
                'tdhca_fatal_competition': site.get('TDHCA_One_Mile_Fatal', False)
            })
            
            results.append(result)
            
        except Exception as e:
            print(f"    ❌ Error processing site {idx}: {e}")
            # Add minimal result for failed sites
            results.append({
                'original_index': idx,
                'site_address': site.get('Address', 'Unknown'),
                'county': site.get('County', 'Unknown'),
                'acres': site.get('Acres', 0),
                'total_revenue': 0,
                'total_cost': 0,
                'profit': 0,
                'revenue_cost_ratio': 0,
                'method': 'failed',
                'error': str(e)
            })
    
    print(f"✅ Completed analysis of {len(results)} sites")
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    return results_df, df

def enhance_with_comparisons(results_df, original_df):
    """Add comparisons between pyforma and original analysis"""
    
    print(f"\nEnhancing results with comparisons...")
    
    # Calculate improvement metrics
    results_df['revenue_cost_improvement'] = (
        results_df['revenue_cost_ratio'] - 
        results_df['original_revenue_cost_ratio']
    )
    
    results_df['revenue_cost_improvement_pct'] = (
        (results_df['revenue_cost_ratio'] - results_df['original_revenue_cost_ratio']) / 
        results_df['original_revenue_cost_ratio'].replace(0, np.nan) * 100
    )
    
    # Rank sites by new analysis
    results_df['pyforma_rank'] = results_df['revenue_cost_ratio'].rank(ascending=False, method='dense')
    
    # Create categories based on pyforma analysis
    def categorize_performance(ratio):
        if ratio >= 0.090:
            return 'Exceptional'
        elif ratio >= 0.080:
            return 'High Potential'
        elif ratio >= 0.070:
            return 'Good'
        elif ratio >= 0.060:
            return 'Fair'
        else:
            return 'Poor'
    
    results_df['pyforma_category'] = results_df['revenue_cost_ratio'].apply(categorize_performance)
    
    # Summary statistics
    print(f"Enhanced results:")
    print(f"  Sites analyzed: {len(results_df)}")
    print(f"  Average revenue/cost ratio: {results_df['revenue_cost_ratio'].mean():.3f}")
    print(f"  Exceptional sites (≥0.090): {sum(results_df['pyforma_category'] == 'Exceptional')}")
    print(f"  High potential sites (≥0.080): {sum(results_df['pyforma_category'] == 'High Potential')}")
    print(f"  Good sites (≥0.070): {sum(results_df['pyforma_category'] == 'Good')}")
    
    return results_df

def save_results(results_df, original_df):
    """Save enhanced results to Excel"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/pyforma_integration/projects/TX_land_analysis/outputs"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f"{output_dir}/Pyforma_Enhanced_195_Sites_{timestamp}.xlsx"
    
    print(f"\nSaving results to: {output_file}")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        # Main results with all data
        results_df.to_excel(writer, sheet_name='Pyforma_Analysis', index=False)
        
        # Top performers
        top_sites = results_df.nlargest(25, 'revenue_cost_ratio')
        top_sites.to_excel(writer, sheet_name='Top_25_Sites', index=False)
        
        # By category
        for category in ['Exceptional', 'High Potential', 'Good']:
            category_sites = results_df[results_df['pyforma_category'] == category]
            if len(category_sites) > 0:
                sheet_name = category.replace(' ', '_')
                category_sites.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Comparison with original rankings
        comparison_cols = [
            'site_address', 'county', 'acres',
            'revenue_cost_ratio', 'original_revenue_cost_ratio',
            'revenue_cost_improvement', 'revenue_cost_improvement_pct',
            'pyforma_rank', 'pyforma_category',
            'original_ranking_4pct', 'original_ranking_9pct',
            'qct_dda_eligible', 'poverty_bonus', 'tdhca_fatal_competition'
        ]
        
        comparison_df = results_df[comparison_cols].copy()
        comparison_df.to_excel(writer, sheet_name='Comparison_Summary', index=False)
        
        # Original data for reference
        original_df.to_excel(writer, sheet_name='Original_Data', index=False)
    
    print(f"✅ Results saved successfully")
    return output_file

def generate_summary_report(results_df):
    """Generate text summary report"""
    
    print(f"\n" + "="*60)
    print(f"PYFORMA ANALYSIS SUMMARY REPORT")
    print(f"="*60)
    
    # Overall statistics
    total_sites = len(results_df)
    successful_analyses = len(results_df[results_df['method'] != 'failed'])
    
    print(f"OVERALL STATISTICS:")
    print(f"  Total sites analyzed: {total_sites}")
    print(f"  Successful analyses: {successful_analyses}")
    print(f"  Success rate: {(successful_analyses/total_sites)*100:.1f}%")
    
    # Performance distribution
    print(f"\nPERFORMANCE DISTRIBUTION:")
    category_counts = results_df['pyforma_category'].value_counts()
    for category, count in category_counts.items():
        pct = (count / total_sites) * 100
        print(f"  {category}: {count} sites ({pct:.1f}%)")
    
    # Top performers
    print(f"\nTOP 10 PERFORMERS:")
    top_10 = results_df.nlargest(10, 'revenue_cost_ratio')
    for idx, site in top_10.iterrows():
        print(f"  {site['pyforma_rank']:2.0f}. {site['site_address'][:30]:30} | {site['county']:15} | Ratio: {site['revenue_cost_ratio']:.3f}")
    
    # Improvement analysis
    improvements = results_df['revenue_cost_improvement'].dropna()
    print(f"\nIMPROVEMENT ANALYSIS:")
    print(f"  Sites with better ratios than original: {sum(improvements > 0)}")
    print(f"  Sites with worse ratios than original: {sum(improvements < 0)}")
    print(f"  Average improvement: {improvements.mean():+.3f}")
    
    print(f"\n" + "="*60)

if __name__ == "__main__":
    # Run complete analysis
    results_df, original_df = analyze_all_sites()
    
    if results_df is not None:
        # Enhance with comparisons
        results_df = enhance_with_comparisons(results_df, original_df)
        
        # Save results
        output_file = save_results(results_df, original_df)
        
        # Generate summary
        generate_summary_report(results_df)
        
        print(f"\n🎉 Complete analysis finished!")
        print(f"📊 Results saved to: {output_file}")
        print(f"🚀 Ready for LIHTC investment decision making!")
    else:
        print(f"❌ Analysis failed to complete.")