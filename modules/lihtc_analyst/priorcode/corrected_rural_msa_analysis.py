#!/usr/bin/env python3
"""
Corrected Rural MSA Analysis
Applies market rent corrections to MSA rural sites only, preserves Non-MSA county AMI assumptions
"""

import pandas as pd
import numpy as np
from datetime import datetime

def main():
    # Market rent corrections for MSA counties only (exclude Non-MSA)
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
        # Non-MSA counties (NAVARRO, LLANO) - keep original AMI assumptions
    }

    # Load analysis data
    analysis_file = 'Final_195_QCT_DDA_Complete_20250621_180310.xlsx'
    all_sites = pd.read_excel(analysis_file, sheet_name='All_195_Sites')

    print('=== CORRECTED ANALYSIS: MSA RURAL SITES ONLY ===')
    print('Applying market rent corrections to MSA rural sites, keeping Non-MSA AMI assumptions\n')

    # Create corrected dataset
    corrected_sites = all_sites.copy()

    # Apply LIHTC market discount (90% of market rate for tenant attraction)
    lihtc_discount = 0.90

    sites_corrected = 0
    total_ranking_changes = 0

    for county, market_rent in market_rent_corrections.items():
        # Get rural sites in MSA counties
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
            
            # Calculate new rankings
            def get_ranking(ratio):
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
            
            corrected_sites.loc[mask, 'Corrected_4pct_Ranking'] = corrected_sites.loc[mask, 'Corrected_Revenue_Cost_Ratio'].apply(get_ranking)
            
            # Count ranking changes for this county
            original_rankings = corrected_sites.loc[mask, 'Ranking_4pct'].values
            corrected_rankings = corrected_sites.loc[mask, 'Corrected_4pct_Ranking'].values
            county_changes = (original_rankings != corrected_rankings).sum()
            total_ranking_changes += county_changes
            
            print(f'{county} County:')
            print(f'  Sites corrected: {len(county_sites)}')
            print(f'  Market rent: ${market_rent}/month -> LIHTC achievable: ${realistic_monthly_rent:.0f}/month')
            print(f'  Original avg ratio: {county_sites["Revenue_Cost_Ratio"].mean():.4f}')
            print(f'  Corrected avg ratio: {corrected_sites.loc[mask, "Corrected_Revenue_Cost_Ratio"].mean():.4f}')
            print(f'  Ranking changes: {county_changes}/{len(county_sites)} sites\n')

    # For non-MSA sites, use original values
    non_msa_mask = ~((corrected_sites['County'].isin(market_rent_corrections.keys())) & 
                     (corrected_sites['Market_Type'] == 'Rural'))
    corrected_sites.loc[non_msa_mask, 'Corrected_Annual_Rent'] = corrected_sites.loc[non_msa_mask, 'Annual_Rent_Per_Unit']
    corrected_sites.loc[non_msa_mask, 'Corrected_Revenue_Cost_Ratio'] = corrected_sites.loc[non_msa_mask, 'Revenue_Cost_Ratio']
    corrected_sites.loc[non_msa_mask, 'Corrected_4pct_Ranking'] = corrected_sites.loc[non_msa_mask, 'Ranking_4pct']

    print('=== SUMMARY ===')
    print(f'MSA rural sites corrected: {sites_corrected}')
    print(f'Sites with ranking changes: {total_ranking_changes}')
    print(f'Non-MSA sites unchanged: {len(all_sites) - sites_corrected} (keeping county AMI assumptions)')

    print('\n=== NEW RANKING DISTRIBUTION ===')
    # Show corrected ranking distribution for rural sites
    rural_sites = corrected_sites[corrected_sites['Market_Type'] == 'Rural']
    original_dist = rural_sites['Ranking_4pct'].value_counts().sort_index()
    corrected_dist = rural_sites['Corrected_4pct_Ranking'].value_counts().sort_index()

    print('4% Deal Rankings (Rural Sites Only):')
    print('Original vs Corrected:')
    for ranking in ['Exceptional', 'High Potential', 'Good', 'Fair', 'Poor']:
        orig_count = original_dist.get(ranking, 0)
        corr_count = corrected_dist.get(ranking, 0)
        change = corr_count - orig_count
        print(f'  {ranking}: {orig_count} -> {corr_count} ({change:+d})')

    # Save corrected analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'Corrected_195_QCT_DDA_MSA_Rural_{timestamp}.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Main corrected dataset
        corrected_sites.to_excel(writer, sheet_name='Corrected_All_Sites', index=False)
        
        # Corrected rural sites only
        corrected_rural = corrected_sites[corrected_sites['Market_Type'] == 'Rural']
        corrected_rural.to_excel(writer, sheet_name='Corrected_Rural_Sites', index=False)
        
        # MSA sites that were corrected
        msa_corrected = corrected_sites[
            (corrected_sites['County'].isin(market_rent_corrections.keys())) & 
            (corrected_sites['Market_Type'] == 'Rural')
        ]
        msa_corrected.to_excel(writer, sheet_name='MSA_Rural_Corrected', index=False)
        
        # New exceptional sites
        new_exceptional = corrected_sites[corrected_sites['Corrected_4pct_Ranking'] == 'Exceptional']
        new_exceptional.to_excel(writer, sheet_name='New_Exceptional_Sites', index=False)

    print(f'\nCorrected analysis saved to: {output_file}')
    
    return corrected_sites

if __name__ == "__main__":
    corrected_data = main()