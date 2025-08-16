#!/usr/bin/env python3
"""
Complete LIHTC Analysis for D'Marco Region 3 Broker List
Runs the full analysis pipeline including:
- QCT/DDA verification
- Competition analysis
- Economic viability
- Poverty rates
- FEMA flood zones
- Final rankings and recommendations

Author: LIHTC Analysis System
Date: 2025-06-25
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
import geopandas as gpd
from shapely.geometry import Point
import requests
import time
from geopy.distance import geodesic

# Import existing analyzers
from analyze_dmarco_region3_broker_list import DMarcoRegion3Analyzer
from final_poverty_analysis import FinalPovertyAnalyzer

class DMarcoRegion3FullAnalysis:
    """Complete analysis for D'Marco Region 3 sites"""
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Base paths
        self.code_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code")
        self.base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects")
        self.data_path = self.base_path / "Lvg_Bond_Execution/Data Sets"
        
        # Initialize components
        self.region3_analyzer = DMarcoRegion3Analyzer()
        self.poverty_analyzer = FinalPovertyAnalyzer()
        
        # Load reference data
        self.load_reference_data()
        
    def load_reference_data(self):
        """Load all necessary reference data"""
        
        # QCT/DDA shapefiles
        self.logger.info("Loading QCT/DDA shapefiles...")
        qct_path = self.data_path / "HUD DDA QCT/QUALIFIED_CENSUS_TRACTS_7341711606021821459.gpkg"
        dda_path = self.data_path / "HUD DDA QCT/Difficult_Development_Areas_-4200740390724245794.gpkg"
        
        self.qct_gdf = gpd.read_file(qct_path)
        self.dda_gdf = gpd.read_file(dda_path)
        
        # Convert to WGS84 for lat/lng comparison
        self.qct_gdf = self.qct_gdf.to_crs('EPSG:4326')
        self.dda_gdf = self.dda_gdf.to_crs('EPSG:4326')
        
        # TDHCA projects for competition analysis
        self.logger.info("Loading TDHCA projects...")
        tdhca_file = self.base_path / "Lvg_Bond_Execution/Data Sets/State Specific/TX/Project_List/TX_TDHCA_Project_List_05252025.xlsx"
        self.tdhca_projects = pd.read_excel(tdhca_file)
        
        # Filter to recent projects (2020+) with valid coordinates
        self.tdhca_projects = self.tdhca_projects[
            (self.tdhca_projects['Year'] >= 2020)
        ].copy()
        
        # Check for latitude/longitude columns
        if 'Latitude11' in self.tdhca_projects.columns:
            self.tdhca_projects['Latitude'] = self.tdhca_projects['Latitude11']
        if 'Longitude11' in self.tdhca_projects.columns:
            self.tdhca_projects['Longitude'] = self.tdhca_projects['Longitude11']
            
        # Clean up any string values in coordinates
        def clean_coordinate(val):
            if pd.isna(val):
                return None
            if isinstance(val, (int, float)):
                return float(val)
            # Handle string values with non-standard characters
            try:
                # Replace non-standard hyphens with regular hyphen
                val_str = str(val).replace('‐', '-').replace('−', '-').strip()
                return float(val_str)
            except:
                return None
        
        self.tdhca_projects['Latitude'] = self.tdhca_projects['Latitude'].apply(clean_coordinate)
        self.tdhca_projects['Longitude'] = self.tdhca_projects['Longitude'].apply(clean_coordinate)
            
        self.tdhca_projects = self.tdhca_projects[
            self.tdhca_projects['Latitude'].notna() & 
            self.tdhca_projects['Longitude'].notna()
        ].copy()
        
        # HUD AMI data
        self.logger.info("Loading HUD AMI data...")
        ami_file = self.data_path / "HUD AMI FMR/HUD2025_AMI_Rent_Data_Static.xlsx"
        self.hud_ami = pd.read_excel(ami_file)
        self.hud_ami = self.hud_ami[self.hud_ami['stusps'] == 'TX'].copy()
        self.hud_ami['County'] = self.hud_ami['County_Name'].str.replace(' County', '').str.upper()
        
        # TDHCA regions
        region_file = self.base_path / "TDHCA_RAG/TDHCA_Regions/TDHCA_Regions.xlsx"
        self.tdhca_regions = pd.read_excel(region_file)
        self.tdhca_regions.columns = self.tdhca_regions.columns.str.strip()
        self.tdhca_regions['County'] = self.tdhca_regions['County'].str.upper()
        
    def check_qct_dda_status(self, lat, lng):
        """Check if coordinates are in QCT or DDA"""
        point = Point(lng, lat)
        
        # Check QCT
        qct_status = self.qct_gdf.geometry.contains(point).any()
        
        # Check DDA
        dda_status = self.dda_gdf.geometry.contains(point).any()
        
        return {
            'QCT_Status': qct_status,
            'DDA_Status': dda_status,
            'QCT_DDA_Combined': qct_status or dda_status,
            'Basis_Boost_Eligible': qct_status or dda_status
        }
    
    def analyze_competition(self, lat, lng, county):
        """Analyze TDHCA competition within 1 and 2 miles"""
        
        # Filter to recent years for competition analysis
        recent_projects = self.tdhca_projects[
            (self.tdhca_projects['Year'] >= 2022)
        ].copy()
        
        one_mile_count = 0
        two_mile_count = 0
        one_mile_projects = []
        two_mile_projects = []
        
        site_point = (lat, lng)
        
        for idx, project in recent_projects.iterrows():
            project_point = (project['Latitude'], project['Longitude'])
            distance = geodesic(site_point, project_point).miles
            
            if distance <= 1.0:
                one_mile_count += 1
                one_mile_projects.append({
                    'name': project['Development Name'],
                    'distance': distance,
                    'year': project['Year']
                })
            elif distance <= 2.0:
                two_mile_count += 1
                two_mile_projects.append({
                    'name': project['Development Name'],
                    'distance': distance,
                    'year': project['Year']
                })
        
        # Determine if large county rules apply
        large_counties = ['HARRIS', 'DALLAS', 'TARRANT', 'BEXAR', 'TRAVIS', 'COLLIN', 'FORT BEND']
        large_county_rules = county.upper() in large_counties if county else False
        
        # Fatal flaw analysis
        one_mile_fatal_9pct = one_mile_count > 0  # Any project within 1 mile is fatal for 9%
        one_mile_risk_4pct = one_mile_count > 0   # Risk indicator for 4% (not fatal)
        two_mile_fatal_9pct = two_mile_count > 0 and large_county_rules  # Only in large counties
        
        return {
            'One_Mile_Competition_Count': one_mile_count,
            'One_Mile_Risk_4pct': one_mile_risk_4pct,
            'One_Mile_Fatal_9pct': one_mile_fatal_9pct,
            'Two_Mile_Competition_Count': two_mile_count,
            'Large_County_Rules_Apply': large_county_rules,
            'Two_Mile_Fatal_9pct': two_mile_fatal_9pct,
            'Competition_Fatal_9pct': one_mile_fatal_9pct or two_mile_fatal_9pct,
            'One_Mile_Projects': one_mile_projects[:3] if one_mile_projects else []  # Top 3 closest
        }
    
    def get_poverty_rate(self, lat, lng):
        """Get poverty rate using PositionStack for geocoding"""
        try:
            # Get census tract
            url = f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
            params = {
                'x': lng,
                'y': lat,
                'benchmark': '2020',
                'vintage': '2020',
                'layers': '10',  # Census tracts
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and 'geographies' in data['result']:
                    tracts = data['result']['geographies'].get('2020 Census Blocks', [])
                    if tracts:
                        tract = tracts[0]
                        state_fips = tract['STATE']
                        county_fips = tract['COUNTY']
                        tract_code = tract['TRACT']
                        
                        # Get poverty data from Census ACS
                        acs_url = "https://api.census.gov/data/2022/acs/acs5"
                        acs_params = {
                            'get': 'B17001_001E,B17001_002E',  # Total population, population in poverty
                            'for': f'tract:{tract_code}',
                            'in': f'state:{state_fips} county:{county_fips}'
                        }
                        
                        acs_response = requests.get(acs_url, params=acs_params, timeout=10)
                        if acs_response.status_code == 200:
                            poverty_data = acs_response.json()
                            if len(poverty_data) > 1:
                                total_pop = float(poverty_data[1][0]) if poverty_data[1][0] else 0
                                poverty_pop = float(poverty_data[1][1]) if poverty_data[1][1] else 0
                                
                                if total_pop > 0:
                                    poverty_rate = (poverty_pop / total_pop) * 100
                                    return round(poverty_rate, 2)
        except Exception as e:
            self.logger.warning(f"Error getting poverty rate: {e}")
        
        return None
    
    def calculate_economic_scores(self, row):
        """Calculate economic viability scores"""
        
        # Get region for construction cost multiplier
        county = row.get('County', '').upper()
        region_row = self.tdhca_regions[self.tdhca_regions['County'] == county]
        
        if not region_row.empty:
            region = f"Region {region_row.iloc[0]['Region']}"
            # Regional cost multipliers from prior analysis
            regional_cost_multipliers = {
                'Region 1': 0.90,   # Panhandle - Lower costs
                'Region 2': 0.95,   # North Central - Moderate costs
                'Region 3': 1.15,   # Dallas/Fort Worth - Higher costs
                'Region 4': 0.98,   # East Texas - Moderate costs
                'Region 5': 1.00,   # Southeast - Average costs
                'Region 6': 1.18,   # Houston - High costs
                'Region 7': 1.20,   # Austin - Highest costs
                'Region 8': 1.00,   # Central - Average costs
                'Region 9': 1.10,   # San Antonio - Above average
                'Region 10': 1.05,  # Coastal - Above average
                'Region 11': 0.92,  # Rio Grande Valley - Lower costs
                'Region 12': 1.12,  # West Texas - Above average (oil region)
                'Region 13': 1.08   # El Paso - Above average
            }
            construction_multiplier = regional_cost_multipliers.get(region, 1.0)
        else:
            construction_multiplier = 1.0
        
        # Base construction cost
        base_cost = 150  # $/SF
        adjusted_cost = base_cost * construction_multiplier
        
        # Get AMI rent
        ami_row = self.hud_ami[self.hud_ami['County'] == county]
        if not ami_row.empty:
            rent_2br_60pct = ami_row.iloc[0]['2BR 60%']
        else:
            rent_2br_60pct = 1200  # Default
        
        # Apply market discount for LIHTC
        market_achievable_rent = rent_2br_60pct * 0.9
        
        # Calculate revenue/cost ratio
        annual_revenue_per_sf = (market_achievable_rent * 12) / 950  # Assume 950 SF for 2BR
        revenue_cost_ratio = annual_revenue_per_sf / adjusted_cost
        
        # Economic scores (0-100 scale)
        # 4% deals need lower returns due to tax-exempt bonds
        economic_score_4pct = min(100, revenue_cost_ratio * 1000)  # More generous for 4%
        
        # 9% deals need higher returns due to competition
        economic_score_9pct = min(100, revenue_cost_ratio * 800)   # More stringent for 9%
        
        return {
            'Construction_Cost_Multiplier': construction_multiplier,
            'Adjusted_Construction_Cost_SF': adjusted_cost,
            'HUD_2BR_60pct_Rent': rent_2br_60pct,
            'Market_Achievable_Rent': market_achievable_rent,
            'Revenue_Cost_Ratio': revenue_cost_ratio,
            'Economic_Score_4pct': economic_score_4pct,
            'Economic_Score_9pct': economic_score_9pct
        }
    
    def run_full_analysis(self):
        """Run complete analysis on all Region 3 sites"""
        
        # Step 1: Prepare the sites
        self.logger.info("Step 1: Preparing Region 3 sites...")
        sites_df, prepared_file = self.region3_analyzer.process_sites()
        
        # Step 2: Run QCT/DDA analysis
        self.logger.info("Step 2: Checking QCT/DDA status...")
        for idx, row in sites_df.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                qct_dda = self.check_qct_dda_status(row['Latitude'], row['Longitude'])
                for key, value in qct_dda.items():
                    sites_df.at[idx, key] = value
        
        # Step 3: Competition analysis
        self.logger.info("Step 3: Running competition analysis...")
        for idx, row in sites_df.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                competition = self.analyze_competition(
                    row['Latitude'], 
                    row['Longitude'], 
                    row.get('County', '')
                )
                for key, value in competition.items():
                    if key != 'One_Mile_Projects':  # Skip detailed project list
                        sites_df.at[idx, key] = value
        
        # Step 4: Get poverty rates
        self.logger.info("Step 4: Getting poverty rates...")
        for idx, row in sites_df.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                poverty_rate = self.get_poverty_rate(row['Latitude'], row['Longitude'])
                sites_df.at[idx, 'Poverty_Rate'] = poverty_rate
                sites_df.at[idx, 'Low_Poverty_Bonus_Eligible'] = (
                    poverty_rate <= 20 if poverty_rate else False
                )
        
        # Step 5: Economic analysis
        self.logger.info("Step 5: Calculating economic scores...")
        for idx, row in sites_df.iterrows():
            economic = self.calculate_economic_scores(row)
            for key, value in economic.items():
                sites_df.at[idx, key] = value
        
        # Step 6: Final rankings
        self.logger.info("Step 6: Calculating final rankings...")
        
        # 4% Rankings (only QCT/DDA eligible sites, no fatal competition)
        eligible_4pct = sites_df[sites_df['Basis_Boost_Eligible'] == True].copy()
        eligible_4pct['4pct_Rank'] = eligible_4pct['Economic_Score_4pct'].rank(ascending=False, method='min')
        
        # 9% Rankings (QCT/DDA eligible AND no fatal competition)
        eligible_9pct = sites_df[
            (sites_df['Basis_Boost_Eligible'] == True) & 
            (sites_df['Competition_Fatal_9pct'] == False)
        ].copy()
        eligible_9pct['9pct_Rank'] = eligible_9pct['Economic_Score_9pct'].rank(ascending=False, method='min')
        
        # Apply rankings back
        sites_df['4pct_Rank'] = eligible_4pct['4pct_Rank']
        sites_df['9pct_Rank'] = eligible_9pct['9pct_Rank']
        
        # Categorize tiers
        sites_df['4pct_Tier'] = pd.cut(
            sites_df['Economic_Score_4pct'],
            bins=[0, 50, 65, 75, 100],
            labels=['Poor', 'Good', 'High Potential', 'Exceptional'],
            ordered=False
        )
        
        sites_df['9pct_Tier'] = sites_df.apply(
            lambda x: 'Fatal Competition' if x['Competition_Fatal_9pct'] 
            else pd.cut(
                [x['Economic_Score_9pct']], 
                bins=[0, 40, 55, 70, 100],
                labels=['Poor', 'Good', 'High Potential', 'Exceptional']
            )[0],
            axis=1
        )
        
        # Final recommendation
        sites_df['Final_Recommendation'] = sites_df.apply(
            lambda x: self.get_recommendation(x), axis=1
        )
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file = f"DMarco_Region3_Complete_Analysis_{timestamp}.xlsx"
        
        # Create Excel writer
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # All sites summary
            sites_df.to_excel(writer, sheet_name='All_Region3_Sites', index=False)
            
            # QCT/DDA eligible only
            qct_dda_eligible = sites_df[sites_df['Basis_Boost_Eligible'] == True]
            qct_dda_eligible.to_excel(writer, sheet_name='QCT_DDA_Eligible', index=False)
            
            # 4% opportunities
            opportunities_4pct = sites_df[
                (sites_df['Basis_Boost_Eligible'] == True) & 
                (sites_df['Economic_Score_4pct'] >= 65)
            ].sort_values('Economic_Score_4pct', ascending=False)
            opportunities_4pct.to_excel(writer, sheet_name='4pct_Opportunities', index=False)
            
            # 9% opportunities (no fatal competition)
            opportunities_9pct = sites_df[
                (sites_df['Basis_Boost_Eligible'] == True) & 
                (sites_df['Competition_Fatal_9pct'] == False) &
                (sites_df['Economic_Score_9pct'] >= 55)
            ].sort_values('Economic_Score_9pct', ascending=False)
            opportunities_9pct.to_excel(writer, sheet_name='9pct_Opportunities', index=False)
            
            # Summary statistics
            summary = pd.DataFrame([
                {'Metric': 'Total Sites', 'Value': len(sites_df)},
                {'Metric': 'QCT/DDA Eligible', 'Value': sites_df['Basis_Boost_Eligible'].sum()},
                {'Metric': 'Sites with Fatal 9% Competition', 'Value': sites_df['Competition_Fatal_9pct'].sum()},
                {'Metric': 'Viable 4% Opportunities', 'Value': len(opportunities_4pct)},
                {'Metric': 'Viable 9% Opportunities', 'Value': len(opportunities_9pct)},
                {'Metric': 'Low Poverty Bonus Eligible', 'Value': sites_df['Low_Poverty_Bonus_Eligible'].sum()}
            ])
            summary.to_excel(writer, sheet_name='Summary', index=False)
        
        self.logger.info(f"Analysis complete! Results saved to: {excel_file}")
        
        return sites_df, excel_file
    
    def get_recommendation(self, row):
        """Generate final recommendation for a site"""
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


def main():
    """Main execution"""
    analyzer = DMarcoRegion3FullAnalysis()
    
    # Run the complete analysis
    results_df, excel_file = analyzer.run_full_analysis()
    
    # Print summary
    print("\n=== D'Marco Region 3 Complete Analysis Summary ===")
    print(f"Total Sites Analyzed: {len(results_df)}")
    print(f"QCT/DDA Eligible: {results_df['Basis_Boost_Eligible'].sum()}")
    print(f"Sites with Fatal 9% Competition: {results_df['Competition_Fatal_9pct'].sum()}")
    print(f"\nViable 4% Opportunities: {len(results_df[(results_df['Basis_Boost_Eligible'] == True) & (results_df['Economic_Score_4pct'] >= 65)])}")
    print(f"Viable 9% Opportunities: {len(results_df[(results_df['Basis_Boost_Eligible'] == True) & (results_df['Competition_Fatal_9pct'] == False) & (results_df['Economic_Score_9pct'] >= 55)])}")
    print(f"\nResults saved to: {excel_file}")


if __name__ == "__main__":
    main()