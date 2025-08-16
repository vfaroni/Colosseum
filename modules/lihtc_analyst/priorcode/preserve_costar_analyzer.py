#!/usr/bin/env python3
"""
Preserve CoStar Analyzer - Maintains ALL original CoStar data including broker info and competition
Focuses on preserving the working competition analysis from the original CoStar file

Author: Claude Code  
Date: 2025-06-21
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

class PreserveCoStarAnalyzer:
    """Analyzer that preserves all CoStar data including broker contacts and working competition"""
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.code_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code")
        
    def load_and_preserve_costar_data(self):
        """Load CoStar data preserving ALL columns including broker info and competition"""
        costar_file = self.code_path / "CoStar_Land_Analysis_With_Counties_20250617_223737.xlsx"
        
        if not costar_file.exists():
            self.logger.error(f"CoStar file not found: {costar_file}")
            return pd.DataFrame()
        
        # Load ALL columns - don't filter anything
        df = pd.read_excel(costar_file)
        self.logger.info(f"Loaded complete CoStar data: {len(df)} properties with {len(df.columns)} columns")
        
        # Add source identifier
        df['Data_Source'] = 'CoStar'
        
        # Verify competition data is present
        comp_cols = ['TDHCA_One_Mile_Fatal', 'TDHCA_One_Mile_Count', 'Competition_1Mile_Projects']
        for col in comp_cols:
            if col in df.columns:
                if df[col].dtype == 'bool':
                    count = df[col].sum()
                    self.logger.info(f"Competition data preserved - {col}: {count} sites affected")
                elif df[col].dtype in ['int64', 'float64']:
                    count = (df[col] > 0).sum()
                    self.logger.info(f"Competition data preserved - {col}: {count} sites with data")
        
        # Verify broker data is present
        broker_cols = ['Listing Broker Agent First Name', 'Listing Broker Agent Last Name', 
                      'Listing Broker Company', 'Listing Broker Phone']
        broker_data_count = 0
        for col in broker_cols:
            if col in df.columns:
                non_empty = df[col].notna().sum()
                broker_data_count += non_empty
                self.logger.info(f"Broker data preserved - {col}: {non_empty} records")
        
        self.logger.info(f"Total broker contact data points preserved: {broker_data_count}")
        
        return df
    
    def create_summary_rankings(self, df):
        """Create investment rankings based on existing analysis"""
        df = df.copy()
        
        # Use existing TDHCA competition analysis for 9% deals
        df['Deal_9pct_Ranking'] = 'Good'
        df.loc[df['TDHCA_One_Mile_Fatal'] == True, 'Deal_9pct_Ranking'] = 'Fatal'
        df.loc[df['TDHCA_Two_Mile_Penalty'] == True, 'Deal_9pct_Ranking'] = 'Penalty'
        
        # Use existing federal basis boost for 4% deals
        df['Deal_4pct_Ranking'] = 'Good'
        df.loc[df['Federal_Basis_Boost_30pct'] == False, 'Deal_4pct_Ranking'] = 'No_Boost'
        
        # Create investment summary
        df['Investment_Summary'] = df.apply(self._create_investment_summary, axis=1)
        
        return df
    
    def _create_investment_summary(self, row):
        """Create investment summary preserving all key data"""
        summary = []
        
        # QCT/DDA status
        if row.get('Federal_Basis_Boost_30pct', False):
            summary.append("30% Federal Basis Boost Eligible")
        
        # Competition issues
        if row.get('TDHCA_One_Mile_Fatal', False):
            summary.append(f"FATAL: {row.get('TDHCA_One_Mile_Count', 0)} TDHCA projects within 1 mile")
        elif row.get('TDHCA_Two_Mile_Penalty', False):
            summary.append(f"PENALTY: {row.get('TDHCA_Two_Mile_Count', 0)} TDHCA projects within 2 miles")
        
        # General competition
        comp_1mile = row.get('Competition_1Mile_Projects', 0)
        if comp_1mile > 0:
            summary.append(f"{comp_1mile} total projects within 1 mile")
        
        # Price info
        if pd.notna(row.get('Sale Price')):
            price = row['Sale Price']
            if price > 0:
                summary.append(f"${price:,.0f} asking price")
        
        # Land size
        if pd.notna(row.get('Land SF Gross')):
            acres = row['Land SF Gross'] / 43560
            if acres > 0:
                summary.append(f"{acres:.1f} acres")
        
        return "; ".join(summary) if summary else "Standard site"
    
    def create_broker_contact_sheet(self, df):
        """Create focused broker contact sheet for deal sourcing"""
        broker_cols = [
            'Address', 'City', 'county_name', 'Sale Price', 'Land SF Gross',
            'Listing Broker Agent First Name', 'Listing Broker Agent Last Name',
            'Listing Broker Company', 'Listing Broker Phone', 'Listing Broker Address',
            'Deal_9pct_Ranking', 'Deal_4pct_Ranking', 'Investment_Summary',
            'TDHCA_One_Mile_Fatal', 'TDHCA_One_Mile_Count', 'Competition_1Mile_Projects'
        ]
        
        # Filter to columns that exist
        available_cols = [col for col in broker_cols if col in df.columns]
        broker_df = df[available_cols].copy()
        
        # Calculate acres
        if 'Land SF Gross' in broker_df.columns:
            broker_df['Land_Acres'] = pd.to_numeric(broker_df['Land SF Gross'], errors='coerce') / 43560
        
        # Sort by investment attractiveness (non-fatal first, then by competition)
        broker_df['Sort_Priority'] = 0
        broker_df.loc[broker_df['TDHCA_One_Mile_Fatal'] == True, 'Sort_Priority'] = 999
        broker_df.loc[broker_df['Competition_1Mile_Projects'] > 0, 'Sort_Priority'] += 10
        
        broker_df = broker_df.sort_values(['Sort_Priority', 'Sale Price'])
        
        return broker_df
    
    def run_analysis(self):
        """Run complete analysis preserving all CoStar data"""
        self.logger.info("Starting Preserve CoStar Analysis...")
        
        # Load data preserving everything
        df = self.load_and_preserve_costar_data()
        if df.empty:
            self.logger.error("No data loaded")
            return
        
        # Add rankings based on existing analysis
        df = self.create_summary_rankings(df)
        
        # Create broker contact sheet
        broker_df = self.create_broker_contact_sheet(df)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.code_path / f"CoStar_Complete_With_Broker_Competition_{timestamp}.xlsx"
        
        # Save to Excel with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Complete data with all columns
            df.to_excel(writer, sheet_name='Complete_CoStar_Data', index=False)
            
            # Broker contact focused sheet
            broker_df.to_excel(writer, sheet_name='Broker_Contacts', index=False)
            
            # Competition analysis sheet
            comp_sites = df[df['TDHCA_One_Mile_Count'] > 0]
            if len(comp_sites) > 0:
                comp_sites.to_excel(writer, sheet_name='Competition_Issues', index=False)
            
            # Fatal sites for 9% deals
            fatal_sites = df[df['TDHCA_One_Mile_Fatal'] == True]
            if len(fatal_sites) > 0:
                fatal_sites.to_excel(writer, sheet_name='Fatal_9pct_Deals', index=False)
        
        self.logger.info(f"Analysis complete: {output_file}")
        
        # Print summary
        print("\\n" + "="*80)
        print("COSTAR DATA PRESERVATION ANALYSIS COMPLETE")
        print("="*80)
        print(f"Total Properties: {len(df)}")
        print(f"Properties with TDHCA Fatal Competition: {(df['TDHCA_One_Mile_Fatal'] == True).sum()}")
        print(f"Properties with General Competition: {(df['Competition_1Mile_Projects'] > 0).sum()}")
        print(f"Properties with Broker Contact Info: {df['Listing Broker Phone'].notna().sum()}")
        print(f"\\nOutput File: {output_file}")
        print("="*80)
        
        return output_file

def main():
    """Run the preserve CoStar analyzer"""
    analyzer = PreserveCoStarAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()