#!/usr/bin/env python3
"""
Simple Integration of All 218 LIHTC Sites
Combines existing 195 sites with new 23 Region 3 sites

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
    
    # Load existing 195 sites
    logger.info("Loading existing 195 sites analysis...")
    existing_file = code_path / "FINAL_195_Sites_Complete_With_Poverty_20250621_213537.xlsx"
    existing_df = pd.read_excel(existing_file, sheet_name='All_195_Sites_Final')
    
    # Load Region 3 sites
    logger.info("Loading Region 3 sites...")
    region3_file = code_path / "DMarco_Region3_Complete_Analysis_20250624_194250.xlsx"
    region3_df = pd.read_excel(region3_file, sheet_name='All_Region3_Sites')
    
    # Add source identifier to Region 3
    region3_df['Source'] = 'DMarco_Region3_Broker'
    
    # Ensure Property_Name exists in both
    if 'Property_Name' not in existing_df.columns and 'Property Name' in existing_df.columns:
        existing_df['Property_Name'] = existing_df['Property Name']
    if 'Property_Name' not in region3_df.columns and 'Property Name' in region3_df.columns:
        region3_df['Property_Name'] = region3_df['Property Name']
    
    # Map QCT_DDA_Eligible to Basis_Boost_Eligible for consistency
    if 'QCT_DDA_Eligible' in existing_df.columns:
        existing_df['Basis_Boost_Eligible'] = existing_df['QCT_DDA_Eligible']
    
    # Get essential columns that exist in both datasets
    essential_cols = [
        'Property_Name', 'Address', 'City', 'County', 'State', 
        'Latitude', 'Longitude', 'Source',
        'QCT_Status', 'DDA_Status', 'Basis_Boost_Eligible',
        'Economic_Score_4pct', 'Economic_Score_9pct',
        'Competition_Fatal_9pct', 'Poverty_Rate'
    ]
    
    # Add columns that might have different names
    score_cols = [col for col in existing_df.columns if 'Score' in col or 'score' in col]
    rank_cols = [col for col in existing_df.columns if 'Rank' in col or 'rank' in col]
    competition_cols = [col for col in existing_df.columns if 'Competition' in col or 'competition' in col]
    
    all_cols = essential_cols + score_cols + rank_cols + competition_cols
    
    # Keep only columns that exist
    existing_cols = [col for col in all_cols if col in existing_df.columns]
    region3_cols = [col for col in all_cols if col in region3_df.columns]
    
    # Find common columns
    common_cols = list(set(existing_cols) & set(region3_cols))
    
    # Add missing essential columns with None values
    for col in essential_cols:
        if col not in existing_df.columns:
            existing_df[col] = None
        if col not in region3_df.columns:
            region3_df[col] = None
    
    # Select final columns to keep
    final_cols = list(set(essential_cols + common_cols))
    
    # Combine datasets
    logger.info(f"Combining {len(existing_df)} existing sites with {len(region3_df)} Region 3 sites")
    all_sites = pd.concat([
        existing_df[final_cols],
        region3_df[final_cols]
    ], ignore_index=True)
    
    # Calculate summary statistics
    total_sites = len(all_sites)
    qct_dda_eligible = all_sites['Basis_Boost_Eligible'].sum()
    
    # Count by source
    source_counts = all_sites['Source'].value_counts()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"All_218_Sites_Simple_Integration_{timestamp}.xlsx"
    
    with pd.ExcelWriter(code_path / output_file, engine='openpyxl') as writer:
        # All sites
        all_sites.to_excel(writer, sheet_name='All_218_Sites', index=False)
        
        # Summary
        summary_data = {
            'Metric': [
                'Total Sites',
                'QCT/DDA Eligible',
                'CoStar Sites',
                'DMarco Brent Sites',
                'DMarco Brian Sites', 
                'DMarco Region 3 Sites'
            ],
            'Value': [
                total_sites,
                qct_dda_eligible,
                source_counts.get('CoStar', 0),
                source_counts.get('DMarco_Brent', 0),
                source_counts.get('DMarco_Brian', 0),
                source_counts.get('DMarco_Region3_Broker', 0)
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Region 3 sites only
        region3_only = all_sites[all_sites['Source'] == 'DMarco_Region3_Broker']
        region3_only.to_excel(writer, sheet_name='Region3_Sites', index=False)
    
    # Print summary
    print(f"\n=== All 218 Sites Integration Complete ===")
    print(f"Total Sites: {total_sites}")
    print(f"QCT/DDA Eligible: {qct_dda_eligible}")
    print(f"\nSites by Source:")
    for source, count in source_counts.items():
        print(f"  {source}: {count}")
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()