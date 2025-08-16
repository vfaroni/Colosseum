#!/usr/bin/env python3
"""
Integrate All Four LIHTC Datasets
Combines:
1. CoStar: 165 QCT/DDA sites
2. D'Marco Brent: 21 QCT/DDA sites  
3. D'Marco Brian: 9 QCT/DDA sites
4. D'Marco Region 3 Broker List: 23 sites (new)

Total: 218 sites with complete analysis

Author: LIHTC Analysis System
Date: 2025-06-25
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

class IntegrateAllDatasets:
    """Integrates all four LIHTC datasets into master analysis"""
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.code_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code")
        
    def load_existing_195_analysis(self):
        """Load the most recent 195 sites analysis"""
        # Find the most recent FINAL analysis file
        final_files = list(self.code_path.glob("FINAL_195_Sites_Complete_With_Poverty_*.xlsx"))
        if not final_files:
            self.logger.error("No FINAL 195 sites analysis found!")
            return None
            
        latest_file = max(final_files, key=lambda x: x.stat().st_mtime)
        self.logger.info(f"Loading existing 195 sites from: {latest_file}")
        
        # Load all sheets into a dictionary
        all_sheets = pd.read_excel(latest_file, sheet_name=None)
        
        # Get the main dataset - it's specifically named 'All_195_Sites_Final'
        if 'All_195_Sites_Final' in all_sheets:
            existing_df = all_sheets['All_195_Sites_Final']
        else:
            self.logger.error("Could not find 'All_195_Sites_Final' sheet!")
            return None
        
        return existing_df
    
    def load_region3_analysis(self):
        """Load the D'Marco Region 3 analysis"""
        # Find the most recent Region 3 analysis
        region3_files = list(self.code_path.glob("DMarco_Region3_Complete_Analysis_*.xlsx"))
        if not region3_files:
            self.logger.error("No Region 3 analysis found!")
            return None
            
        latest_file = max(region3_files, key=lambda x: x.stat().st_mtime)
        self.logger.info(f"Loading Region 3 analysis from: {latest_file}")
        
        # Load the main sheet
        all_sheets = pd.read_excel(latest_file, sheet_name=None)
        
        # Get the all sites sheet
        if 'All_Region3_Sites' in all_sheets:
            region3_df = all_sheets['All_Region3_Sites']
        else:
            # Find the main sheet
            for sheet_name, df in all_sheets.items():
                if len(df) > 20:  # Should have ~23 rows
                    region3_df = df
                    break
        
        # Add source identifier
        region3_df['Source'] = 'DMarco_Region3_Broker'
        
        return region3_df
    
    def standardize_columns(self, df, source_name):
        """Standardize column names across datasets"""
        # Map common variations to standard names
        column_mapping = {
            # Property identification
            'Property Name': 'Property_Name',
            'Development Name': 'Property_Name',
            'Project Name': 'Property_Name',
            'Name': 'Property_Name',
            
            # Location
            'Project Address': 'Address',
            'Property Address': 'Address',
            'Street Address': 'Address',
            
            # Economic scores
            'Economic Score 4%': 'Economic_Score_4pct',
            'Economic Score 9%': 'Economic_Score_9pct',
            'Economic_Score_4%': 'Economic_Score_4pct',
            'Economic_Score_9%': 'Economic_Score_9pct',
            
            # Competition
            'One Mile Fatal 9%': 'One_Mile_Fatal_9pct',
            'Competition Fatal 9%': 'Competition_Fatal_9pct',
            
            # Poverty
            'Poverty Rate': 'Poverty_Rate',
            'Poverty_Rate_Percent': 'Poverty_Rate',
            
            # Construction costs
            'Construction Cost Multiplier': 'Construction_Cost_Multiplier',
            'Adjusted Construction Cost': 'Adjusted_Construction_Cost_SF',
            
            # Rankings
            '4% Rank': '4pct_Rank',
            '9% Rank': '9pct_Rank',
            '4pct Rank': '4pct_Rank',
            '9pct Rank': '9pct_Rank',
            
            # QCT/DDA eligibility
            'QCT_DDA_Eligible': 'Basis_Boost_Eligible',
            'QCT_DDA_Combined': 'Basis_Boost_Eligible'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Ensure source column exists
        if 'Source' not in df.columns:
            df['Source'] = source_name
            
        return df
    
    def combine_all_datasets(self):
        """Combine all four datasets"""
        
        # Load existing 195 sites
        existing_195 = self.load_existing_195_analysis()
        if existing_195 is None:
            self.logger.error("Failed to load existing 195 sites analysis")
            return None
            
        # Load Region 3 analysis
        region3_sites = self.load_region3_analysis()
        if region3_sites is None:
            self.logger.error("Failed to load Region 3 analysis")
            return None
        
        # Standardize columns
        existing_195 = self.standardize_columns(existing_195, 'Existing_Analysis')
        region3_sites = self.standardize_columns(region3_sites, 'DMarco_Region3_Broker')
        
        # Get common columns
        common_cols = list(set(existing_195.columns) & set(region3_sites.columns))
        
        # Add any missing essential columns to Region 3
        essential_cols = [
            'Property_Name', 'Address', 'City', 'County', 'State', 'Zip',
            'Latitude', 'Longitude', 'QCT_Status', 'DDA_Status', 
            'Basis_Boost_Eligible', 'Economic_Score_4pct', 'Economic_Score_9pct',
            'Competition_Fatal_9pct', 'Poverty_Rate', 'Source'
        ]
        
        for col in essential_cols:
            if col not in region3_sites.columns and col in existing_195.columns:
                region3_sites[col] = None
        
        # Combine datasets
        self.logger.info(f"Combining {len(existing_195)} existing sites with {len(region3_sites)} Region 3 sites")
        
        # Select relevant columns for merge
        cols_to_keep = list(set([col for col in common_cols if col in essential_cols or 
                       'Score' in col or 'Rank' in col or 'Competition' in col or 
                       'QCT' in col or 'DDA' in col or 'Poverty' in col]))
        
        # Ensure both dataframes have the same columns for concatenation
        for col in cols_to_keep:
            if col not in existing_195.columns:
                existing_195[col] = None
            if col not in region3_sites.columns:
                region3_sites[col] = None
        
        # Combine the datasets
        all_sites = pd.concat([
            existing_195[cols_to_keep],
            region3_sites[cols_to_keep]
        ], ignore_index=True)
        
        # Update rankings across all 218 sites
        self.logger.info("Recalculating rankings for all 218 sites...")
        
        # 4% Rankings (all QCT/DDA eligible)
        eligible_4pct = all_sites[all_sites['Basis_Boost_Eligible'] == True].copy()
        eligible_4pct['4pct_Rank_New'] = eligible_4pct['Economic_Score_4pct'].rank(
            ascending=False, method='min'
        )
        
        # 9% Rankings (QCT/DDA eligible AND no fatal competition)
        eligible_9pct = all_sites[
            (all_sites['Basis_Boost_Eligible'] == True) & 
            (all_sites['Competition_Fatal_9pct'] == False)
        ].copy()
        eligible_9pct['9pct_Rank_New'] = eligible_9pct['Economic_Score_9pct'].rank(
            ascending=False, method='min'
        )
        
        # Apply new rankings
        all_sites['4pct_Rank_Original'] = all_sites['4pct_Rank']
        all_sites['9pct_Rank_Original'] = all_sites['9pct_Rank']
        
        all_sites = all_sites.merge(
            eligible_4pct[['Property_Name', '4pct_Rank_New']], 
            on='Property_Name', how='left'
        )
        all_sites = all_sites.merge(
            eligible_9pct[['Property_Name', '9pct_Rank_New']], 
            on='Property_Name', how='left'
        )
        
        # Save integrated results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"All_218_Sites_Integrated_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # All sites
            all_sites.to_excel(writer, sheet_name='All_218_Sites', index=False)
            
            # Summary by source
            source_summary = all_sites.groupby('Source').agg({
                'Property_Name': 'count',
                'Basis_Boost_Eligible': 'sum',
                'Competition_Fatal_9pct': 'sum',
                'Economic_Score_4pct': 'mean',
                'Economic_Score_9pct': 'mean'
            }).round(2)
            source_summary.columns = ['Total_Sites', 'QCT_DDA_Eligible', 
                                     'Fatal_9pct_Competition', 'Avg_4pct_Score', 'Avg_9pct_Score']
            source_summary.to_excel(writer, sheet_name='Summary_By_Source')
            
            # Top 4% opportunities
            top_4pct = all_sites[
                (all_sites['Basis_Boost_Eligible'] == True) & 
                (all_sites['Economic_Score_4pct'] >= 70)
            ].sort_values('Economic_Score_4pct', ascending=False)
            top_4pct.to_excel(writer, sheet_name='Top_4pct_Opportunities', index=False)
            
            # Top 9% opportunities
            top_9pct = all_sites[
                (all_sites['Basis_Boost_Eligible'] == True) & 
                (all_sites['Competition_Fatal_9pct'] == False) &
                (all_sites['Economic_Score_9pct'] >= 60)
            ].sort_values('Economic_Score_9pct', ascending=False)
            top_9pct.to_excel(writer, sheet_name='Top_9pct_Opportunities', index=False)
            
            # Region 3 specific analysis
            region3_only = all_sites[all_sites['Source'] == 'DMarco_Region3_Broker']
            region3_only.to_excel(writer, sheet_name='Region3_Sites_Detail', index=False)
        
        self.logger.info(f"Integrated analysis saved to: {output_file}")
        
        return all_sites, output_file
    
    def print_summary(self, all_sites):
        """Print summary statistics"""
        print("\n=== All Four Datasets Integration Summary ===")
        print(f"Total Sites: {len(all_sites)}")
        
        print("\nSites by Source:")
        source_counts = all_sites['Source'].value_counts()
        for source, count in source_counts.items():
            qct_dda = all_sites[all_sites['Source'] == source]['Basis_Boost_Eligible'].sum()
            print(f"  {source}: {count} sites ({qct_dda} QCT/DDA eligible)")
        
        print(f"\nTotal QCT/DDA Eligible: {all_sites['Basis_Boost_Eligible'].sum()}")
        print(f"Sites with Fatal 9% Competition: {all_sites['Competition_Fatal_9pct'].sum()}")
        
        # Top opportunities
        top_4pct = all_sites[
            (all_sites['Basis_Boost_Eligible'] == True) & 
            (all_sites['Economic_Score_4pct'] >= 70)
        ]
        top_9pct = all_sites[
            (all_sites['Basis_Boost_Eligible'] == True) & 
            (all_sites['Competition_Fatal_9pct'] == False) &
            (all_sites['Economic_Score_9pct'] >= 60)
        ]
        
        print(f"\nHigh-Value Opportunities:")
        print(f"  4% Deals (Score >= 70): {len(top_4pct)}")
        print(f"  9% Deals (Score >= 60, No Competition): {len(top_9pct)}")


def main():
    """Main execution"""
    integrator = IntegrateAllDatasets()
    
    # Run the integration
    all_sites, output_file = integrator.combine_all_datasets()
    
    if all_sites is not None:
        integrator.print_summary(all_sites)
        print(f"\nIntegrated analysis saved to: {output_file}")
    else:
        print("Integration failed!")


if __name__ == "__main__":
    main()