#!/usr/bin/env python3
"""
Apply Aubrey Rural MSA Correction to D'Marco Region 3 Analysis
Similar to Austin/Houston rural corrections we applied earlier

Author: LIHTC Analysis System
Date: 2025-06-25
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    code_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code")
    
    # Load the current Region 3 analysis
    input_file = "DMarco_Region3_Complete_Analysis_20250624_194250.xlsx"
    logger.info(f"Loading Region 3 analysis from: {input_file}")
    
    # Read all sheets
    all_sheets = pd.read_excel(code_path / input_file, sheet_name=None)
    df = all_sheets['All_Region3_Sites'].copy()
    
    # Apply Aubrey correction (17.3% over-valued)
    aubrey_correction_factor = 0.827  # Reduce by 17.3%
    
    # Identify Aubrey sites
    aubrey_mask = df['City'].str.upper() == 'AUBREY'
    aubrey_count = aubrey_mask.sum()
    logger.info(f"Found {aubrey_count} Aubrey sites to correct")
    
    # Apply corrections to Aubrey sites
    if aubrey_count > 0:
        # Reduce market achievable rent
        df.loc[aubrey_mask, 'Market_Achievable_Rent'] = (
            df.loc[aubrey_mask, 'Market_Achievable_Rent'] * aubrey_correction_factor
        )
        
        # Recalculate revenue/cost ratio
        df.loc[aubrey_mask, 'Revenue_Cost_Ratio'] = (
            df.loc[aubrey_mask, 'Market_Achievable_Rent'] * 12 / 950  # Annual revenue per SF
        ) / df.loc[aubrey_mask, 'Adjusted_Construction_Cost_SF']
        
        # Recalculate economic scores
        df.loc[aubrey_mask, 'Economic_Score_4pct'] = np.minimum(
            100, df.loc[aubrey_mask, 'Revenue_Cost_Ratio'] * 1000
        )
        df.loc[aubrey_mask, 'Economic_Score_9pct'] = np.minimum(
            100, df.loc[aubrey_mask, 'Revenue_Cost_Ratio'] * 800
        )
        
        # Add correction notes
        df.loc[aubrey_mask, 'Market_Correction_Applied'] = 'Aubrey Rural MSA: -17.3%'
    
    # Recalculate rankings for all sites
    logger.info("Recalculating rankings after Aubrey correction...")
    
    # 4% Rankings (all QCT/DDA eligible)
    eligible_4pct = df[df['Basis_Boost_Eligible'] == True].copy()
    eligible_4pct['4pct_Rank_Corrected'] = eligible_4pct['Economic_Score_4pct'].rank(
        ascending=False, method='min'
    )
    
    # 9% Rankings (QCT/DDA eligible AND no fatal competition)
    eligible_9pct = df[
        (df['Basis_Boost_Eligible'] == True) & 
        (df['Competition_Fatal_9pct'] == False)
    ].copy()
    eligible_9pct['9pct_Rank_Corrected'] = eligible_9pct['Economic_Score_9pct'].rank(
        ascending=False, method='min'
    )
    
    # Merge rankings back
    df = df.merge(
        eligible_4pct[['Property_Name', '4pct_Rank_Corrected']],
        on='Property_Name', how='left'
    )
    df = df.merge(
        eligible_9pct[['Property_Name', '9pct_Rank_Corrected']],
        on='Property_Name', how='left'
    )
    
    # Update tier classifications
    df['4pct_Tier_Corrected'] = pd.cut(
        df['Economic_Score_4pct'],
        bins=[0, 50, 65, 75, 100],
        labels=['Poor', 'Good', 'High Potential', 'Exceptional'],
        ordered=False
    )
    
    df['9pct_Tier_Corrected'] = df.apply(
        lambda x: 'Fatal Competition' if x['Competition_Fatal_9pct'] 
        else pd.cut(
            [x['Economic_Score_9pct']], 
            bins=[0, 40, 55, 70, 100],
            labels=['Poor', 'Good', 'High Potential', 'Exceptional']
        )[0],
        axis=1
    )
    
    # Update recommendations
    def get_corrected_recommendation(row):
        if not row['Basis_Boost_Eligible']:
            return "Not Eligible - No QCT/DDA"
        
        if row['Competition_Fatal_9pct']:
            if row['Economic_Score_4pct'] >= 65:
                return "Strong 4% Candidate - Fatal 9% Competition"
            else:
                return "Marginal 4% - Fatal 9% Competition"
        else:
            if row['Economic_Score_9pct'] >= 70 and row['Economic_Score_4pct'] >= 75:
                return "Exceptional - Both 4% and 9%"
            elif row['Economic_Score_9pct'] >= 55:
                return "Strong 9% Candidate"
            elif row['Economic_Score_4pct'] >= 65:
                return "Strong 4% Candidate"
            else:
                return "Marginal - Review Needed"
    
    df['Final_Recommendation_Corrected'] = df.apply(get_corrected_recommendation, axis=1)
    
    # Save corrected analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"DMarco_Region3_Aubrey_Corrected_{timestamp}.xlsx"
    
    with pd.ExcelWriter(code_path / output_file, engine='openpyxl') as writer:
        # All sites with corrections
        df.to_excel(writer, sheet_name='All_Sites_Corrected', index=False)
        
        # Summary of changes
        summary_data = {
            'Metric': [
                'Total Sites',
                'Sites Corrected (Aubrey)',
                'QCT/DDA Eligible',
                'Pre-Correction: Exceptional 4%',
                'Post-Correction: Exceptional 4%',
                'Pre-Correction: Exceptional 9%',
                'Post-Correction: Exceptional 9%'
            ],
            'Value': [
                len(df),
                aubrey_count,
                df['Basis_Boost_Eligible'].sum(),
                (df['4pct_Tier'] == 'Exceptional').sum() if '4pct_Tier' in df.columns else 'N/A',
                (df['4pct_Tier_Corrected'] == 'Exceptional').sum(),
                (df['9pct_Tier'] == 'Exceptional').sum() if '9pct_Tier' in df.columns else 'N/A',
                (df['9pct_Tier_Corrected'] == 'Exceptional').sum()
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Correction_Summary', index=False)
        
        # Aubrey sites specifically
        aubrey_sites = df[aubrey_mask]
        if len(aubrey_sites) > 0:
            aubrey_sites.to_excel(writer, sheet_name='Aubrey_Sites_Corrected', index=False)
        
        # Top opportunities after correction
        top_4pct = df[
            (df['Basis_Boost_Eligible'] == True) & 
            (df['Economic_Score_4pct'] >= 65)
        ].sort_values('Economic_Score_4pct', ascending=False)
        top_4pct.to_excel(writer, sheet_name='Top_4pct_Corrected', index=False)
        
        top_9pct = df[
            (df['Basis_Boost_Eligible'] == True) & 
            (df['Competition_Fatal_9pct'] == False) &
            (df['Economic_Score_9pct'] >= 55)
        ].sort_values('Economic_Score_9pct', ascending=False)
        top_9pct.to_excel(writer, sheet_name='Top_9pct_Corrected', index=False)
    
    # Print results
    print(f"\n=== Aubrey Rural MSA Correction Applied ===")
    print(f"Sites Corrected: {aubrey_count}")
    print(f"Correction Factor: {aubrey_correction_factor:.1%} (17.3% reduction)")
    
    if aubrey_count > 0:
        aubrey_sites = df[aubrey_mask]
        print(f"\nAubrey Sites After Correction:")
        for _, site in aubrey_sites.iterrows():
            print(f"  {site['Property_Name']}: 4% Score {site['Economic_Score_4pct']:.1f}, 9% Score {site['Economic_Score_9pct']:.1f}")
    
    print(f"\nResults saved to: {output_file}")
    
    return df, output_file


if __name__ == "__main__":
    main()