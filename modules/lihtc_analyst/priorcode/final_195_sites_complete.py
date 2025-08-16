#!/usr/bin/env python3
"""
Final 195 QCT/DDA Sites Complete Analysis
Takes the working CoStar analysis and properly adds D'Marco sites

Sources:
1. CoStar: 165 QCT/DDA sites (COMPLETE with working competition & broker data)
2. D'Marco Brent: 21 QCT/DDA sites (filtered from complete analysis)  
3. D'Marco Brian: 9 QCT/DDA sites (all eligible)

Total: 195 sites with rankings, competition analysis, and broker contacts

Author: Claude Code
Date: 2025-06-21
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

class Final195SitesComplete:
    """Final analyzer using working CoStar data as foundation"""
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.code_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code")
        self.base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects")
        
        # Load reference data
        self.load_tdhca_regions()
        self.load_hud_ami_data()
    
    def load_tdhca_regions(self):
        """Load TDHCA regional mapping"""
        region_file = self.base_path / "TDHCA_RAG/TDHCA_Regions/TDHCA_Regions.xlsx"
        try:
            self.tdhca_regions = pd.read_excel(region_file)
            # Clean column names (remove trailing spaces)
            self.tdhca_regions.columns = self.tdhca_regions.columns.str.strip()
            self.tdhca_regions['County'] = self.tdhca_regions['County'].str.upper()
            # Extract region number from "Region X" format
            self.tdhca_regions['Region'] = self.tdhca_regions['Region'].str.extract(r'(\d+)').astype(int)
            self.logger.info(f"Loaded TDHCA regions for {len(self.tdhca_regions)} counties")
        except Exception as e:
            self.logger.error(f"Error loading TDHCA regions: {e}")
            self.tdhca_regions = pd.DataFrame()
    
    def load_hud_ami_data(self):
        """Load HUD AMI rent data"""
        ami_file = self.base_path / "Lvg_Bond_Execution/Data Sets/HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx"
        try:
            self.hud_ami = pd.read_excel(ami_file)
            # Filter to Texas data only
            self.hud_ami = self.hud_ami[self.hud_ami['stusps'] == 'TX'].copy()
            # Create county name from County_Name field
            self.hud_ami['County'] = self.hud_ami['County_Name'].str.replace(' County', '').str.upper()
            # Rename rent columns for easier access
            self.hud_ami['rent_2br_60pct'] = self.hud_ami['2BR 60%']
            self.hud_ami['rent_1br_60pct'] = self.hud_ami['1BR 60%']
            self.hud_ami['rent_3br_60pct'] = self.hud_ami['3BR 60%']
            self.logger.info(f"Loaded AMI data for {len(self.hud_ami)} Texas counties")
        except Exception as e:
            self.logger.error(f"Error loading HUD AMI data: {e}")
            self.hud_ami = pd.DataFrame()
    
    def classify_market_type(self, city, county):
        """Classify market as Large City, Mid City, Suburban, or Rural"""
        if pd.isna(city):
            return 'Rural'
        
        city_upper = str(city).upper()
        county_upper = str(county).upper() if pd.notna(county) else ''
        
        # Large Cities (population > 500k)
        large_cities = [
            'HOUSTON', 'SAN ANTONIO', 'DALLAS', 'AUSTIN', 'FORT WORTH',
            'EL PASO', 'ARLINGTON', 'CORPUS CHRISTI', 'PLANO', 'LAREDO'
        ]
        
        # Mid Cities (population 100k-500k)
        mid_cities = [
            'LUBBOCK', 'GARLAND', 'IRVING', 'AMARILLO', 'GRAND PRAIRIE',
            'BROWNSVILLE', 'MCKINNEY', 'FRISCO', 'PASADENA', 'MESQUITE',
            'KILLEEN', 'CARROLLTON', 'MIDLAND', 'DENTON', 'ABILENE',
            'BEAUMONT', 'ROUND ROCK', 'ODESSA', 'WACO', 'RICHARDSON',
            'PEARLAND', 'COLLEGE STATION', 'LEAGUE CITY', 'SUGAR LAND',
            'LONGVIEW', 'TYLER', 'BRYAN', 'PHARR', 'TEMPLE'
        ]
        
        # Suburban areas (metro counties of large cities)
        suburban_counties = [
            'HARRIS', 'DALLAS', 'TARRANT', 'TRAVIS', 'BEXAR', 'COLLIN',
            'FORT BEND', 'DENTON', 'WILLIAMSON', 'MONTGOMERY', 'BRAZORIA',
            'GALVESTON', 'HAYS', 'ROCKWALL'
        ]
        
        if city_upper in large_cities:
            return 'Large City'
        elif city_upper in mid_cities:
            return 'Mid City'
        elif county_upper in suburban_counties:
            return 'Suburban'
        else:
            return 'Rural'
    
    def calculate_fema_cost_impact(self, fema_zone):
        """Calculate FEMA construction cost multiplier"""
        if pd.isna(fema_zone):
            return 1.0
        
        zone_str = str(fema_zone).upper()
        
        # High risk zones
        if any(zone in zone_str for zone in ['VE', 'V']):
            return 1.30  # 30% increase for velocity zones
        elif any(zone in zone_str for zone in ['AE', 'A']):
            return 1.20  # 20% increase for flood zones
        elif any(zone in zone_str for zone in ['X500', '0.2']):
            return 1.05  # 5% increase for moderate risk
        else:
            return 1.0   # No increase for low risk zones
    
    def calculate_comprehensive_economics(self, df):
        """Calculate comprehensive economic analysis"""
        df = df.copy()
        
        # Add TDHCA regions by county
        if not self.tdhca_regions.empty:
            # Ensure County column exists and is standardized
            if 'County' not in df.columns:
                if 'county_name' in df.columns:
                    df['County'] = df['county_name'].str.replace(' County', '').str.upper()
                else:
                    # Create county from city if needed
                    city_county_map = {
                        'AUSTIN': 'TRAVIS', 'HOUSTON': 'HARRIS', 'DALLAS': 'DALLAS',
                        'SAN ANTONIO': 'BEXAR', 'FORT WORTH': 'TARRANT', 'PLANO': 'COLLIN',
                        'IRVING': 'DALLAS', 'GARLAND': 'DALLAS', 'LUBBOCK': 'LUBBOCK',
                        'ARLINGTON': 'TARRANT', 'MCKINNEY': 'COLLIN', 'FRISCO': 'COLLIN'
                    }
                    df['County'] = df['City'].str.upper().map(city_county_map)
            
            # Clean and standardize county names
            df['County'] = df['County'].astype(str).str.upper().str.replace(' COUNTY', '')
            
            # Merge with regions
            df = df.merge(
                self.tdhca_regions[['County', 'Region']], 
                on='County', 
                how='left'
            )
            df.rename(columns={'Region': 'TDHCA_Region'}, inplace=True)
        
        # Classify market types
        df['Market_Type'] = df.apply(lambda row: self.classify_market_type(row.get('City'), row.get('County')), axis=1)
        
        # Calculate FEMA cost impact
        fema_col = 'FEMA_Flood_Zone' if 'FEMA_Flood_Zone' in df.columns else 'Flood_Zone'
        if fema_col in df.columns:
            df['FEMA_Cost_Multiplier'] = df[fema_col].apply(self.calculate_fema_cost_impact)
        else:
            df['FEMA_Cost_Multiplier'] = 1.0
        
        # Regional construction cost multipliers
        region_multipliers = {
            1: 0.95, 2: 0.95, 3: 1.15, 4: 1.05, 5: 0.95,
            6: 1.18, 7: 1.20, 8: 1.00, 9: 1.15, 10: 1.00,
            11: 1.10, 12: 0.95, 13: 1.05
        }
        
        # Market type construction multipliers
        market_multipliers = {
            'Large City': 1.25,
            'Mid City': 1.10,
            'Suburban': 1.05,
            'Rural': 0.95
        }
        
        # Get county-specific AMI rents
        if not self.hud_ami.empty:
            df = df.merge(
                self.hud_ami[['County', 'rent_2br_60pct', 'rent_1br_60pct', 'rent_3br_60pct']], 
                on='County', 
                how='left'
            )
        
        # Fallback rents by region if county data missing
        default_rents = {
            1: 1100, 2: 1150, 3: 1400, 4: 1200, 5: 1100,
            6: 1350, 7: 1600, 8: 1250, 9: 1300, 10: 1200,
            11: 1300, 12: 1100, 13: 1250
        }
        
        # Fill missing rent data
        for rent_col in ['rent_2br_60pct', 'rent_1br_60pct', 'rent_3br_60pct']:
            if rent_col not in df.columns:
                df[rent_col] = df['TDHCA_Region'].map(default_rents).fillna(1200)
            else:
                df[rent_col] = df[rent_col].fillna(df['TDHCA_Region'].map(default_rents).fillna(1200))
        
        # Calculate total construction cost multiplier
        df['Regional_Multiplier'] = df['TDHCA_Region'].map(region_multipliers).fillna(1.0)
        df['Market_Multiplier'] = df['Market_Type'].map(market_multipliers).fillna(1.0)
        df['Total_Construction_Multiplier'] = df['Regional_Multiplier'] * df['Market_Multiplier'] * df['FEMA_Cost_Multiplier']
        
        # Base construction costs
        df['Base_Construction_Cost_Per_SF'] = 150
        df['Adjusted_Construction_Cost_Per_SF'] = df['Base_Construction_Cost_Per_SF'] * df['Total_Construction_Multiplier']
        
        # Calculate land costs per unit (assuming 40-unit development on average)
        if 'Sale Price' in df.columns:
            df['Land_Cost_Per_Unit'] = pd.to_numeric(df['Sale Price'], errors='coerce') / 40
        elif 'Price Per AC Land' in df.columns and 'Land SF Gross' in df.columns:
            acres = pd.to_numeric(df['Land SF Gross'], errors='coerce') / 43560
            total_land_cost = pd.to_numeric(df['Price Per AC Land'], errors='coerce') * acres
            df['Land_Cost_Per_Unit'] = total_land_cost / 40
        else:
            df['Land_Cost_Per_Unit'] = 50000  # Default estimate
        
        # Construction cost per unit (assume 1000 SF average)
        df['Construction_Cost_Per_Unit'] = df['Adjusted_Construction_Cost_Per_SF'] * 1000
        
        # Total development cost per unit
        df['Total_Cost_Per_Unit'] = df['Land_Cost_Per_Unit'] + df['Construction_Cost_Per_Unit']
        
        # Annual rent revenue per unit
        df['Annual_Rent_Per_Unit'] = df['rent_2br_60pct'] * 12
        
        # Revenue to cost ratios
        df['Revenue_Cost_Ratio'] = df['Annual_Rent_Per_Unit'] / df['Total_Cost_Per_Unit']
        df['Land_Cost_Ratio'] = df['Land_Cost_Per_Unit'] / df['Total_Cost_Per_Unit']
        
        # Economic viability score (0-100)
        df['Economic_Score'] = np.clip(df['Revenue_Cost_Ratio'] * 500, 0, 100)
        
        # Cost per acre analysis
        if 'Land SF Gross' in df.columns:
            df['Acres'] = pd.to_numeric(df['Land SF Gross'], errors='coerce') / 43560
            if 'Sale Price' in df.columns:
                df['Cost_Per_Acre'] = pd.to_numeric(df['Sale Price'], errors='coerce') / df['Acres']
        
        return df
    
    def load_working_costar_data(self):
        """Load the working CoStar analysis with competition & broker data"""
        costar_file = self.code_path / "CoStar_Land_Analysis_With_Counties_20250617_223737.xlsx"
        
        if not costar_file.exists():
            self.logger.error(f"CoStar file not found: {costar_file}")
            return pd.DataFrame()
        
        df = pd.read_excel(costar_file)
        df['Source'] = 'CoStar'
        df['QCT_DDA_Eligible'] = True  # All CoStar sites are QCT/DDA eligible
        
        self.logger.info(f"Loaded {len(df)} CoStar sites with competition analysis and broker data")
        
        # Log working competition data
        fatal_count = df['TDHCA_One_Mile_Fatal'].sum() if 'TDHCA_One_Mile_Fatal' in df.columns else 0
        comp_count = (df['Competition_1Mile_Projects'] > 0).sum() if 'Competition_1Mile_Projects' in df.columns else 0
        broker_count = df['Listing Broker Phone'].notna().sum() if 'Listing Broker Phone' in df.columns else 0
        
        self.logger.info(f"Competition analysis preserved: {fatal_count} fatal, {comp_count} with competition")
        self.logger.info(f"Broker contacts preserved: {broker_count} phone numbers")
        
        return df
    
    def create_comprehensive_rankings(self, df):
        """Create rankings based on comprehensive economic analysis"""
        df = df.copy()
        
        # 4% Rankings (Non-competitive, based on economic viability)
        df['Ranking_4pct'] = 'Fair'
        
        # Use Revenue_Cost_Ratio and Economic_Score for rankings
        if 'Revenue_Cost_Ratio' in df.columns:
            # Calibrated thresholds based on actual data
            df.loc[df['Revenue_Cost_Ratio'] >= 0.090, 'Ranking_4pct'] = 'Exceptional'
            df.loc[(df['Revenue_Cost_Ratio'] >= 0.085) & (df['Revenue_Cost_Ratio'] < 0.090), 'Ranking_4pct'] = 'High Potential'
            df.loc[(df['Revenue_Cost_Ratio'] >= 0.078) & (df['Revenue_Cost_Ratio'] < 0.085), 'Ranking_4pct'] = 'Good'
            df.loc[df['Revenue_Cost_Ratio'] < 0.078, 'Ranking_4pct'] = 'Poor'
        elif 'Economic_Score' in df.columns:
            df.loc[df['Economic_Score'] >= 80, 'Ranking_4pct'] = 'Exceptional'
            df.loc[(df['Economic_Score'] >= 70) & (df['Economic_Score'] < 80), 'Ranking_4pct'] = 'High Potential'
            df.loc[(df['Economic_Score'] >= 60) & (df['Economic_Score'] < 70), 'Ranking_4pct'] = 'Good'
            df.loc[df['Economic_Score'] < 60, 'Ranking_4pct'] = 'Poor'
        
        # 9% Rankings (Competitive, based on TDHCA rules + economics)
        df['Ranking_9pct'] = 'Good'
        
        # Apply fatal competition rules first
        if 'TDHCA_One_Mile_Fatal' in df.columns:
            df.loc[df['TDHCA_One_Mile_Fatal'] == True, 'Ranking_9pct'] = 'Fatal'
        
        # Apply penalty rules
        if 'TDHCA_Two_Mile_Penalty' in df.columns:
            df.loc[(df['TDHCA_Two_Mile_Penalty'] == True) & (df['Ranking_9pct'] != 'Fatal'), 'Ranking_9pct'] = 'Fair'
        
        # Apply economic viability for non-fatal sites
        non_fatal_mask = df['Ranking_9pct'] != 'Fatal'
        
        if 'Revenue_Cost_Ratio' in df.columns:
            df.loc[non_fatal_mask & (df['Revenue_Cost_Ratio'] >= 0.090), 'Ranking_9pct'] = 'Exceptional'
            df.loc[non_fatal_mask & (df['Revenue_Cost_Ratio'] >= 0.085) & (df['Revenue_Cost_Ratio'] < 0.090), 'Ranking_9pct'] = 'High Potential'
            df.loc[non_fatal_mask & (df['Revenue_Cost_Ratio'] >= 0.078) & (df['Revenue_Cost_Ratio'] < 0.085), 'Ranking_9pct'] = 'Good'
            df.loc[non_fatal_mask & (df['Revenue_Cost_Ratio'] < 0.078), 'Ranking_9pct'] = 'Poor'
        elif 'Economic_Score' in df.columns:
            df.loc[non_fatal_mask & (df['Economic_Score'] >= 80), 'Ranking_9pct'] = 'Exceptional'
            df.loc[non_fatal_mask & (df['Economic_Score'] >= 70) & (df['Economic_Score'] < 80), 'Ranking_9pct'] = 'High Potential'
            df.loc[non_fatal_mask & (df['Economic_Score'] >= 60) & (df['Economic_Score'] < 70), 'Ranking_9pct'] = 'Good'
            df.loc[non_fatal_mask & (df['Economic_Score'] < 60), 'Ranking_9pct'] = 'Poor'
        
        return df
    
    def add_dmarco_brent_sites(self):
        """Add D'Marco Brent QCT/DDA sites - CORRECTED to use 21 from 65 total"""
        brent_file = self.code_path / "DMarco_Sites_Final_PositionStack_20250618_235606.xlsx"
        
        if not brent_file.exists():
            self.logger.warning(f"D'Marco Brent file not found: {brent_file}")
            return pd.DataFrame()
        
        # Read the QCT_DDA_Priority sheet which has the correct 21 sites
        qct_dda_df = pd.read_excel(brent_file, sheet_name='QCT_DDA_Priority')
        
        # Verify we got the right data
        total_df = pd.read_excel(brent_file, sheet_name='All_Sites_Final')
        
        # Standardize columns for integration
        qct_dda_df['Source'] = 'DMarco_Brent'
        qct_dda_df['QCT_DDA_Eligible'] = True  # All sites in this sheet are QCT/DDA eligible
        
        # Map columns if they exist
        if 'Property_Address' not in qct_dda_df.columns and 'Address' in qct_dda_df.columns:
            qct_dda_df['Property_Address'] = qct_dda_df['Address']
        
        # Simple rankings (D'Marco sites are generally good opportunities)
        qct_dda_df['Ranking_4pct'] = 'Good'
        qct_dda_df['Ranking_9pct'] = 'Good'
        
        # Add broker info if available
        if 'Broker' in qct_dda_df.columns:
            qct_dda_df['Listing_Broker_Name'] = qct_dda_df['Broker']
        if 'Phone' in qct_dda_df.columns:
            qct_dda_df['Listing_Broker_Phone'] = qct_dda_df['Phone']
        
        self.logger.info(f"Added {len(qct_dda_df)} D'Marco Brent QCT/DDA sites (from {len(total_df)} total)")
        
        return qct_dda_df
    
    def add_dmarco_brian_sites(self):
        """Add D'Marco Brian QCT/DDA sites"""
        brian_file = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/TDHCA_RAG/D'Marco_Sites/From_Brian_06202025.csv")
        
        if not brian_file.exists():
            self.logger.warning(f"D'Marco Brian file not found: {brian_file}")
            return pd.DataFrame()
        
        df = pd.read_csv(brian_file)
        df['Source'] = 'DMarco_Brian'
        df['QCT_DDA_Eligible'] = True  # All Brian sites are QCT/DDA
        
        # Standardize columns
        df['Property_Address'] = df['Address']
        df['Sale_Price'] = df['Price']
        
        # Simple rankings (all Brian sites are decent opportunities)
        df['Ranking_4pct'] = 'Good'
        df['Ranking_9pct'] = 'Good'
        
        self.logger.info(f"Added {len(df)} D'Marco Brian QCT/DDA sites")
        
        return df
    
    def combine_and_finalize(self, costar_df, brent_df, brian_df):
        """Combine all sources and create final analysis"""
        
        # Find common columns across all sources
        costar_cols = set(costar_df.columns)
        brent_cols = set(brent_df.columns) if not brent_df.empty else set()
        brian_cols = set(brian_df.columns) if not brian_df.empty else set()
        
        # Essential columns that must be present
        essential_cols = [
            'Source', 'QCT_DDA_Eligible', 'Ranking_4pct', 'Ranking_9pct',
            'Property_Address', 'City'
        ]
        
        # Add essential columns to all dataframes if missing
        for df_info in [(costar_df, 'CoStar'), (brent_df, 'Brent'), (brian_df, 'Brian')]:
            df, name = df_info
            if df.empty:
                continue
            for col in essential_cols:
                if col not in df.columns:
                    if col in ['Ranking_4pct', 'Ranking_9pct']:
                        df[col] = 'Good'
                    elif col == 'QCT_DDA_Eligible':
                        df[col] = True
                    else:
                        df[col] = ''
        
        # Combine dataframes
        all_dfs = [df for df in [costar_df, brent_df, brian_df] if not df.empty]
        
        if not all_dfs:
            self.logger.error("No data to combine")
            return pd.DataFrame()
        
        # Align columns - use CoStar as the base
        base_cols = costar_df.columns.tolist()
        
        aligned_dfs = []
        for df in all_dfs:
            aligned_df = pd.DataFrame()
            for col in base_cols:
                if col in df.columns:
                    aligned_df[col] = df[col]
                else:
                    aligned_df[col] = None
            aligned_dfs.append(aligned_df)
        
        # Combine
        combined_df = pd.concat(aligned_dfs, ignore_index=True)
        
        self.logger.info(f"Combined {len(combined_df)} total QCT/DDA sites")
        
        return combined_df
    
    def run_analysis(self):
        """Run the complete 195 sites analysis"""
        self.logger.info("Starting Final 195 QCT/DDA Sites Analysis...")
        
        # Load all data sources
        costar_df = self.load_working_costar_data()
        brent_df = self.add_dmarco_brent_sites()
        brian_df = self.add_dmarco_brian_sites()
        
        # Combine all sources
        all_sites = self.combine_and_finalize(costar_df, brent_df, brian_df)
        
        # Apply comprehensive economic analysis
        all_sites = self.calculate_comprehensive_economics(all_sites)
        
        # Create rankings based on comprehensive analysis
        all_sites = self.create_comprehensive_rankings(all_sites)
        
        # Generate timestamp and output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.code_path / f"Final_195_QCT_DDA_Complete_{timestamp}.xlsx"
        
        # Create comprehensive Excel output
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            
            # Executive Summary with Economic Metrics
            summary_data = {
                'Metric': [
                    'Total QCT/DDA Sites',
                    'CoStar Sites (with full data)',
                    'D\'Marco Brent Sites',
                    'D\'Marco Brian Sites',
                    'Sites with Fatal TDHCA Competition',
                    'Sites with Broker Contacts',
                    'Average Revenue/Cost Ratio',
                    'Large City Sites',
                    'Mid City Sites', 
                    'Suburban Sites',
                    'Rural Sites',
                    'Average FEMA Cost Impact',
                    'TDHCA Regions Represented',
                    '4% Exceptional Sites',
                    '9% Exceptional Sites',
                    '4% High Potential Sites',
                    '9% High Potential Sites'
                ],
                'Count': [
                    len(all_sites),
                    len(all_sites[all_sites['Source'] == 'CoStar']),
                    len(all_sites[all_sites['Source'] == 'DMarco_Brent']),
                    len(all_sites[all_sites['Source'] == 'DMarco_Brian']),
                    all_sites['TDHCA_One_Mile_Fatal'].sum() if 'TDHCA_One_Mile_Fatal' in all_sites.columns else 0,
                    all_sites['Listing Broker Phone'].notna().sum() if 'Listing Broker Phone' in all_sites.columns else 0,
                    f"{all_sites['Revenue_Cost_Ratio'].mean():.3f}" if 'Revenue_Cost_Ratio' in all_sites.columns else 'N/A',
                    len(all_sites[all_sites['Market_Type'] == 'Large City']) if 'Market_Type' in all_sites.columns else 0,
                    len(all_sites[all_sites['Market_Type'] == 'Mid City']) if 'Market_Type' in all_sites.columns else 0,
                    len(all_sites[all_sites['Market_Type'] == 'Suburban']) if 'Market_Type' in all_sites.columns else 0,
                    len(all_sites[all_sites['Market_Type'] == 'Rural']) if 'Market_Type' in all_sites.columns else 0,
                    f"{all_sites['FEMA_Cost_Multiplier'].mean():.2f}x" if 'FEMA_Cost_Multiplier' in all_sites.columns else 'N/A',
                    all_sites['TDHCA_Region'].nunique() if 'TDHCA_Region' in all_sites.columns else 0,
                    len(all_sites[all_sites['Ranking_4pct'] == 'Exceptional']),
                    len(all_sites[all_sites['Ranking_9pct'] == 'Exceptional']),
                    len(all_sites[all_sites['Ranking_4pct'] == 'High Potential']),
                    len(all_sites[all_sites['Ranking_9pct'] == 'High Potential'])
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
            
            # All sites
            all_sites.to_excel(writer, sheet_name='All_195_Sites', index=False)
            
            # 4% Rankings
            for ranking in ['Exceptional', 'High Potential', 'Good', 'Fair', 'Poor']:
                sites = all_sites[all_sites['Ranking_4pct'] == ranking]
                if len(sites) > 0:
                    sheet_name = f'4pct_{ranking.replace(" ", "_")}'
                    sites.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # 9% Rankings  
            for ranking in ['Exceptional', 'High Potential', 'Good', 'Fair', 'Poor', 'Fatal']:
                sites = all_sites[all_sites['Ranking_9pct'] == ranking]
                if len(sites) > 0:
                    sheet_name = f'9pct_{ranking.replace(" ", "_")}'
                    sites.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # CoStar sites with full broker data
            costar_only = all_sites[all_sites['Source'] == 'CoStar']
            if len(costar_only) > 0:
                costar_only.to_excel(writer, sheet_name='CoStar_Complete_Data', index=False)
            
            # Economic analysis sheets
            if 'Market_Type' in all_sites.columns:
                for market_type in ['Large City', 'Mid City', 'Suburban', 'Rural']:
                    market_sites = all_sites[all_sites['Market_Type'] == market_type]
                    if len(market_sites) > 0:
                        sheet_name = f'{market_type.replace(" ", "_")}_Markets'
                        market_sites.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # TDHCA Regional analysis
            if 'TDHCA_Region' in all_sites.columns:
                region_summary = all_sites.groupby('TDHCA_Region').agg({
                    'Source': 'count',
                    'Revenue_Cost_Ratio': 'mean',
                    'Total_Cost_Per_Unit': 'mean',
                    'Annual_Rent_Per_Unit': 'mean',
                    'Market_Type': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Unknown'
                }).round(3)
                region_summary.columns = ['Site_Count', 'Avg_Revenue_Cost_Ratio', 'Avg_Cost_Per_Unit', 'Avg_Rent_Per_Unit', 'Primary_Market_Type']
                region_summary.to_excel(writer, sheet_name='TDHCA_Regional_Analysis', index=True)
            
            # Competition analysis (CoStar sites with TDHCA competition)
            if 'TDHCA_One_Mile_Count' in all_sites.columns:
                comp_sites = all_sites[all_sites['TDHCA_One_Mile_Count'] > 0]
                if len(comp_sites) > 0:
                    comp_sites.to_excel(writer, sheet_name='TDHCA_Competition', index=False)
            
            # Economic performance analysis
            if 'Revenue_Cost_Ratio' in all_sites.columns:
                # Top economic performers
                top_performers = all_sites.nlargest(20, 'Revenue_Cost_Ratio')
                top_performers.to_excel(writer, sheet_name='Top_Economic_Performers', index=False)
                
                # Cost analysis
                cost_analysis = all_sites[['Source', 'Market_Type', 'TDHCA_Region', 'FEMA_Cost_Multiplier', 
                                         'Total_Construction_Multiplier', 'Cost_Per_Acre', 'Revenue_Cost_Ratio']].copy()
                cost_analysis.to_excel(writer, sheet_name='Cost_Analysis', index=False)
        
        self.logger.info(f"Analysis complete: {output_file}")
        
        # Print comprehensive summary
        print("\\n" + "="*80)
        print("FINAL 195 QCT/DDA SITES ANALYSIS COMPLETE")
        print("="*80)
        print(f"Total QCT/DDA Sites: {len(all_sites)}")
        print(f"  - CoStar (complete data): {len(all_sites[all_sites['Source'] == 'CoStar'])}")
        print(f"  - D'Marco Brent: {len(all_sites[all_sites['Source'] == 'DMarco_Brent'])}")
        print(f"  - D'Marco Brian: {len(all_sites[all_sites['Source'] == 'DMarco_Brian'])}")
        
        print(f"\\nCompetition Analysis (CoStar sites):")
        if 'TDHCA_One_Mile_Fatal' in all_sites.columns:
            fatal_count = all_sites['TDHCA_One_Mile_Fatal'].sum()
            print(f"  - Sites with Fatal TDHCA Competition: {fatal_count}")
        if 'Competition_1Mile_Projects' in all_sites.columns:
            comp_count = (all_sites['Competition_1Mile_Projects'] > 0).sum()
            print(f"  - Sites with General Competition: {comp_count}")
        
        print(f"\\nBroker Contact Information:")
        if 'Listing Broker Phone' in all_sites.columns:
            broker_count = all_sites['Listing Broker Phone'].notna().sum()
            print(f"  - Sites with Broker Phone Numbers: {broker_count}")
        
        print(f"\\n4% Tax-Exempt Bond Rankings:")
        ranking_4pct = all_sites['Ranking_4pct'].value_counts().sort_index()
        for rank, count in ranking_4pct.items():
            print(f"  - {rank}: {count}")
        
        print(f"\\n9% Competitive Tax Credit Rankings:")
        ranking_9pct = all_sites['Ranking_9pct'].value_counts().sort_index()
        for rank, count in ranking_9pct.items():
            print(f"  - {rank}: {count}")
        
        print(f"\\nOutput File: {output_file}")
        print("="*80)
        
        return output_file

def main():
    """Run the final 195 sites analyzer"""
    analyzer = Final195SitesComplete()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()