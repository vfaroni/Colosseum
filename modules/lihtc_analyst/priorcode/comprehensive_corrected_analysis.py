#!/usr/bin/env python3
"""
Comprehensive Corrected Analysis
Applies market rent corrections while preserving 4% vs 9% deal analysis and competition rules
"""

import pandas as pd
import numpy as np
from datetime import datetime

def calculate_corrected_rankings(df):
    """Calculate both 4% and 9% rankings with corrected ratios"""
    
    # 4% Rankings (Non-competitive, based on economic viability only)
    def get_4pct_ranking(ratio):
        if pd.isna(ratio):
            return 'Unknown'
        elif ratio >= 0.090:
            return 'Exceptional'
        elif ratio >= 0.085:
            return 'High Potential'
        elif ratio >= 0.078:
            return 'Good'
        else:
            return 'Poor'
    
    # 9% Rankings (Competitive, includes TDHCA competition rules)
    def get_9pct_ranking(row):
        ratio = row['Corrected_Revenue_Cost_Ratio']
        
        # Apply fatal competition rules first
        if row.get('TDHCA_One_Mile_Fatal', False):
            return 'Fatal'
        
        # Apply economic viability for non-fatal sites
        if pd.isna(ratio):
            return 'Unknown'
        elif ratio >= 0.090:
            return 'Exceptional'
        elif ratio >= 0.085:
            return 'High Potential'
        elif ratio >= 0.078:
            return 'Good'
        else:
            return 'Poor'
    
    df['Corrected_4pct_Ranking'] = df['Corrected_Revenue_Cost_Ratio'].apply(get_4pct_ranking)
    df['Corrected_9pct_Ranking'] = df.apply(get_9pct_ranking, axis=1)
    
    return df

def main():
    # Market rent corrections for MSA counties only
    market_rent_corrections = {
        # Austin MSA
        'BASTROP': 1214,
        'CALDWELL': 1026,
        # Dallas MSA  
        'KAUFMAN': 1201,
        'PARKER': 1306,
        'ELLIS': 1520,
        # Houston MSA
        'WALLER': 989
    }

    # Load original analysis data
    analysis_file = 'Final_195_QCT_DDA_Complete_20250621_180310.xlsx'
    all_sites = pd.read_excel(analysis_file, sheet_name='All_195_Sites')

    print('=== COMPREHENSIVE CORRECTED ANALYSIS ===')
    print('Preserving 4% vs 9% deal analysis with MSA rural market rent corrections\n')

    # Create corrected dataset
    corrected_sites = all_sites.copy()
    lihtc_discount = 0.90  # 10% below market for tenant attraction

    sites_corrected = 0

    # Apply corrections to MSA rural sites only
    for county, market_rent in market_rent_corrections.items():
        mask = (corrected_sites['County'] == county) & (corrected_sites['Market_Type'] == 'Rural')
        county_sites = corrected_sites[mask]
        
        if len(county_sites) > 0:
            sites_corrected += len(county_sites)
            
            # Apply market rent correction with LIHTC discount
            realistic_monthly_rent = market_rent * lihtc_discount
            realistic_annual_rent = realistic_monthly_rent * 12
            
            # Update the corrected dataset
            corrected_sites.loc[mask, 'Corrected_Annual_Rent'] = realistic_annual_rent
            corrected_sites.loc[mask, 'Corrected_Revenue_Cost_Ratio'] = realistic_annual_rent / corrected_sites.loc[mask, 'Total_Cost_Per_Unit']
            
            print(f'{county} County: {len(county_sites)} sites corrected (${market_rent} -> ${realistic_monthly_rent:.0f}/month)')

    # For non-MSA sites, use original values
    non_msa_mask = ~((corrected_sites['County'].isin(market_rent_corrections.keys())) & 
                     (corrected_sites['Market_Type'] == 'Rural'))
    corrected_sites.loc[non_msa_mask, 'Corrected_Annual_Rent'] = corrected_sites.loc[non_msa_mask, 'Annual_Rent_Per_Unit']
    corrected_sites.loc[non_msa_mask, 'Corrected_Revenue_Cost_Ratio'] = corrected_sites.loc[non_msa_mask, 'Revenue_Cost_Ratio']

    # Calculate corrected rankings for both 4% and 9% deals
    corrected_sites = calculate_corrected_rankings(corrected_sites)

    print(f'\nTotal MSA rural sites corrected: {sites_corrected}')
    print(f'Non-MSA sites preserved: {len(all_sites) - sites_corrected}')

    # Analyze ranking changes
    print('\n=== 4% DEAL RANKING CHANGES ===')
    original_4pct = corrected_sites['Ranking_4pct'].value_counts()
    corrected_4pct = corrected_sites['Corrected_4pct_Ranking'].value_counts()
    
    rankings = ['Exceptional', 'High Potential', 'Good', 'Fair', 'Poor', 'Fatal']
    for ranking in rankings:
        orig = original_4pct.get(ranking, 0)
        corr = corrected_4pct.get(ranking, 0)
        change = corr - orig
        if orig > 0 or corr > 0:
            print(f'  {ranking}: {orig} -> {corr} ({change:+d})')

    print('\n=== 9% DEAL RANKING CHANGES ===')
    original_9pct = corrected_sites['Ranking_9pct'].value_counts()
    corrected_9pct = corrected_sites['Corrected_9pct_Ranking'].value_counts()
    
    for ranking in rankings:
        orig = original_9pct.get(ranking, 0)
        corr = corrected_9pct.get(ranking, 0)
        change = corr - orig
        if orig > 0 or corr > 0:
            print(f'  {ranking}: {orig} -> {corr} ({change:+d})')

    # Identify most impacted sites
    print('\n=== MOST IMPACTED SITES ===')
    
    # 4% Exceptional to Poor
    exceptional_to_poor_4pct = corrected_sites[
        (corrected_sites['Ranking_4pct'] == 'Exceptional') & 
        (corrected_sites['Corrected_4pct_Ranking'] == 'Poor')
    ]
    
    # 9% Exceptional to Poor
    exceptional_to_poor_9pct = corrected_sites[
        (corrected_sites['Ranking_9pct'] == 'Exceptional') & 
        (corrected_sites['Corrected_9pct_Ranking'] == 'Poor')
    ]
    
    print(f'4% Deals - Exceptional to Poor: {len(exceptional_to_poor_4pct)} sites')
    print(f'9% Deals - Exceptional to Poor: {len(exceptional_to_poor_9pct)} sites')
    
    if len(exceptional_to_poor_4pct) > 0:
        print('\n4% Exceptional -> Poor (Most Over-Valued):')
        for _, site in exceptional_to_poor_4pct.iterrows():
            ratio_change = ((site['Corrected_Revenue_Cost_Ratio'] / site['Revenue_Cost_Ratio']) - 1) * 100
            print(f"  {site['City']}, {site['County']}: {ratio_change:+.1f}% revenue impact")

    # Save comprehensive corrected analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'Comprehensive_Corrected_195_QCT_DDA_{timestamp}.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Executive Summary
        exec_summary = pd.DataFrame({
            'Metric': [
                'Total QCT/DDA Sites',
                'MSA Rural Sites Corrected',
                'Non-MSA Sites Preserved',
                'Sites with Fatal 9% Competition',
                'Corrected 4% Exceptional Sites',
                'Corrected 9% Exceptional Sites',
                'Sites Downgraded from Exceptional (4%)',
                'Sites Downgraded from Exceptional (9%)'
            ],
            'Count': [
                len(corrected_sites),
                sites_corrected,
                len(all_sites) - sites_corrected,
                corrected_9pct.get('Fatal', 0),
                corrected_4pct.get('Exceptional', 0),
                corrected_9pct.get('Exceptional', 0),
                len(exceptional_to_poor_4pct),
                len(exceptional_to_poor_9pct)
            ]
        })
        exec_summary.to_excel(writer, sheet_name='Executive_Summary', index=False)
        
        # All sites with corrections
        corrected_sites.to_excel(writer, sheet_name='All_195_Sites_Corrected', index=False)
        
        # 4% Deal Rankings
        corrected_4pct_exceptional = corrected_sites[corrected_sites['Corrected_4pct_Ranking'] == 'Exceptional']
        corrected_4pct_high = corrected_sites[corrected_sites['Corrected_4pct_Ranking'] == 'High Potential']
        corrected_4pct_good = corrected_sites[corrected_sites['Corrected_4pct_Ranking'] == 'Good']
        corrected_4pct_poor = corrected_sites[corrected_sites['Corrected_4pct_Ranking'] == 'Poor']
        
        corrected_4pct_exceptional.to_excel(writer, sheet_name='4pct_Exceptional_Corrected', index=False)
        corrected_4pct_high.to_excel(writer, sheet_name='4pct_High_Potential_Corrected', index=False)
        corrected_4pct_good.to_excel(writer, sheet_name='4pct_Good_Corrected', index=False)
        corrected_4pct_poor.to_excel(writer, sheet_name='4pct_Poor_Corrected', index=False)
        
        # 9% Deal Rankings
        corrected_9pct_exceptional = corrected_sites[corrected_sites['Corrected_9pct_Ranking'] == 'Exceptional']
        corrected_9pct_high = corrected_sites[corrected_sites['Corrected_9pct_Ranking'] == 'High Potential']
        corrected_9pct_good = corrected_sites[corrected_sites['Corrected_9pct_Ranking'] == 'Good']
        corrected_9pct_poor = corrected_sites[corrected_sites['Corrected_9pct_Ranking'] == 'Poor']
        corrected_9pct_fatal = corrected_sites[corrected_sites['Corrected_9pct_Ranking'] == 'Fatal']
        
        corrected_9pct_exceptional.to_excel(writer, sheet_name='9pct_Exceptional_Corrected', index=False)
        corrected_9pct_high.to_excel(writer, sheet_name='9pct_High_Potential_Corrected', index=False)
        corrected_9pct_good.to_excel(writer, sheet_name='9pct_Good_Corrected', index=False)
        corrected_9pct_poor.to_excel(writer, sheet_name='9pct_Poor_Corrected', index=False)
        corrected_9pct_fatal.to_excel(writer, sheet_name='9pct_Fatal_Competition', index=False)
        
        # Most impacted sites
        if len(exceptional_to_poor_4pct) > 0:
            exceptional_to_poor_4pct.to_excel(writer, sheet_name='4pct_Exceptional_to_Poor', index=False)
        if len(exceptional_to_poor_9pct) > 0:
            exceptional_to_poor_9pct.to_excel(writer, sheet_name='9pct_Exceptional_to_Poor', index=False)

    print(f'\nComprehensive corrected analysis saved to: {output_file}')
    return corrected_sites

if __name__ == "__main__":
    corrected_data = main()