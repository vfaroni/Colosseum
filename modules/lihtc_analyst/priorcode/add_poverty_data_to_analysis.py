#!/usr/bin/env python3
"""
Add Poverty Rate Data to 195 Sites Analysis
Integrates Census ACS poverty data for both 9% scoring and market area insights
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime
from pathlib import Path
import time
import logging

class PovertyDataIntegrator:
    """Add poverty rate data to existing analysis"""
    
    def __init__(self):
        self.api_key = '06ece0121263282cd9ffd753215b007b8f9a3dfc'
        self.base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects")
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def get_census_tract_poverty(self, lat, lon, county, state='TX'):
        """Get poverty rate for a specific location using Census API"""
        try:
            # First get the census tract for this location
            geo_url = f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
            params = {
                'x': lon,
                'y': lat,
                'benchmark': '2020',
                'vintage': '2020',
                'layers': '2020 Census Tracts',
                'format': 'json'
            }
            
            geo_response = requests.get(geo_url, params=params, timeout=10)
            
            if geo_response.status_code == 200:
                geo_data = geo_response.json()
                
                if geo_data['result']['geographies'].get('2020 Census Tracts'):
                    tract_info = geo_data['result']['geographies']['2020 Census Tracts'][0]
                    state_fips = tract_info['STATE']
                    county_fips = tract_info['COUNTY']
                    tract_fips = tract_info['TRACT']
                    
                    # Now get poverty data for this tract
                    # Using 2022 ACS 5-year estimates (most recent complete)
                    census_url = f'https://api.census.gov/data/2022/acs/acs5'
                    
                    # B17001_002E = Below poverty level
                    # B17001_001E = Total population for poverty determination
                    params = {
                        'get': 'B17001_002E,B17001_001E',
                        'for': f'tract:{tract_fips}',
                        'in': f'state:{state_fips} county:{county_fips}',
                        'key': self.api_key
                    }
                    
                    census_response = requests.get(census_url, params=params, timeout=10)
                    
                    if census_response.status_code == 200:
                        data = census_response.json()
                        if len(data) > 1:  # First row is headers
                            values = data[1]
                            below_poverty = float(values[0]) if values[0] and values[0] != 'null' else 0
                            total_pop = float(values[1]) if values[1] and values[1] != 'null' else 0
                            
                            if total_pop > 0:
                                poverty_rate = (below_poverty / total_pop) * 100
                                return {
                                    'poverty_rate': round(poverty_rate, 1),
                                    'census_tract': f"{state_fips}{county_fips}{tract_fips}",
                                    'total_population': int(total_pop),
                                    'below_poverty': int(below_poverty)
                                }
            
            time.sleep(0.1)  # Rate limit protection
            
        except Exception as e:
            self.logger.warning(f"Error getting poverty data: {e}")
        
        return {
            'poverty_rate': None,
            'census_tract': None,
            'total_population': None,
            'below_poverty': None
        }
    
    def add_poverty_to_sites(self, sites_df):
        """Add poverty data to all sites"""
        
        # Initialize poverty columns
        sites_df['Poverty_Rate'] = np.nan
        sites_df['Census_Tract'] = ''
        sites_df['Tract_Population'] = np.nan
        sites_df['Below_Poverty_Count'] = np.nan
        sites_df['Low_Poverty_Bonus_9pct'] = 0
        sites_df['Poverty_Category'] = ''
        
        # Process each site
        for idx, row in sites_df.iterrows():
            if idx % 10 == 0:
                self.logger.info(f"Processing poverty data: {idx}/{len(sites_df)} sites")
            
            # Get coordinates
            lat = row.get('Latitude', row.get('latitude'))
            lon = row.get('Longitude', row.get('longitude'))
            county = row.get('County', '')
            
            if pd.notna(lat) and pd.notna(lon):
                poverty_data = self.get_census_tract_poverty(lat, lon, county)
                
                if poverty_data['poverty_rate'] is not None:
                    sites_df.at[idx, 'Poverty_Rate'] = poverty_data['poverty_rate']
                    sites_df.at[idx, 'Census_Tract'] = poverty_data['census_tract']
                    sites_df.at[idx, 'Tract_Population'] = poverty_data['total_population']
                    sites_df.at[idx, 'Below_Poverty_Count'] = poverty_data['below_poverty']
                    
                    # Calculate 9% bonus (2 points if ≤20% poverty)
                    if poverty_data['poverty_rate'] <= 20.0:
                        sites_df.at[idx, 'Low_Poverty_Bonus_9pct'] = 2
                    
                    # Categorize poverty level for market insights
                    if poverty_data['poverty_rate'] <= 10.0:
                        sites_df.at[idx, 'Poverty_Category'] = 'Very Low (<10%)'
                    elif poverty_data['poverty_rate'] <= 20.0:
                        sites_df.at[idx, 'Poverty_Category'] = 'Low (10-20%)'
                    elif poverty_data['poverty_rate'] <= 30.0:
                        sites_df.at[idx, 'Poverty_Category'] = 'Moderate (20-30%)'
                    else:
                        sites_df.at[idx, 'Poverty_Category'] = 'High (>30%)'
        
        return sites_df
    
    def recalculate_9pct_rankings(self, sites_df):
        """Recalculate 9% rankings with poverty bonus"""
        
        # Create a scoring column for 9% deals
        sites_df['Total_9pct_Score'] = 0
        
        # Base score from revenue/cost ratio (scaled to points)
        # Assuming revenue/cost ratio contributes up to 10 points
        if 'Corrected_Revenue_Cost_Ratio' in sites_df.columns:
            sites_df['Economic_Score_9pct'] = np.clip(sites_df['Corrected_Revenue_Cost_Ratio'] * 100, 0, 10)
        else:
            sites_df['Economic_Score_9pct'] = np.clip(sites_df['Revenue_Cost_Ratio'] * 100, 0, 10)
        
        # Add poverty bonus
        sites_df['Total_9pct_Score'] = sites_df['Economic_Score_9pct'] + sites_df['Low_Poverty_Bonus_9pct']
        
        # Recalculate 9% rankings considering poverty bonus
        def get_9pct_ranking_with_poverty(row):
            # Fatal competition overrides everything
            if row.get('TDHCA_One_Mile_Fatal', False) or row.get('Corrected_9pct_Ranking') == 'Fatal':
                return 'Fatal'
            
            # Use total score including poverty bonus
            score = row['Total_9pct_Score']
            
            if score >= 9.5:  # Adjusted thresholds for poverty bonus
                return 'Exceptional'
            elif score >= 9.0:
                return 'High Potential'
            elif score >= 8.0:
                return 'Good'
            else:
                return 'Poor'
        
        sites_df['Updated_9pct_Ranking'] = sites_df.apply(get_9pct_ranking_with_poverty, axis=1)
        
        return sites_df
    
    def create_poverty_summary(self, sites_df):
        """Create summary statistics for poverty data"""
        
        summary = {
            'Total Sites Analyzed': len(sites_df),
            'Sites with Poverty Data': sites_df['Poverty_Rate'].notna().sum(),
            'Sites Missing Poverty Data': sites_df['Poverty_Rate'].isna().sum(),
            'Sites with Low Poverty Bonus (≤20%)': (sites_df['Low_Poverty_Bonus_9pct'] > 0).sum(),
            'Average Poverty Rate': sites_df['Poverty_Rate'].mean(),
            'Median Poverty Rate': sites_df['Poverty_Rate'].median()
        }
        
        # By source
        for source in sites_df['Source'].unique():
            source_data = sites_df[sites_df['Source'] == source]
            summary[f'{source} Avg Poverty Rate'] = source_data['Poverty_Rate'].mean()
            summary[f'{source} Low Poverty Sites'] = (source_data['Low_Poverty_Bonus_9pct'] > 0).sum()
        
        # By market type
        for market in sites_df['Market_Type'].unique():
            market_data = sites_df[sites_df['Market_Type'] == market]
            summary[f'{market} Avg Poverty Rate'] = market_data['Poverty_Rate'].mean()
        
        return summary
    
    def run_poverty_integration(self, input_file):
        """Main function to add poverty data to analysis"""
        
        self.logger.info("Starting poverty data integration...")
        
        # Load the corrected analysis
        all_sites = pd.read_excel(input_file, sheet_name='All_195_Sites_Corrected')
        
        # Add poverty data
        all_sites = self.add_poverty_to_sites(all_sites)
        
        # Recalculate 9% rankings with poverty bonus
        all_sites = self.recalculate_9pct_rankings(all_sites)
        
        # Create summary
        summary = self.create_poverty_summary(all_sites)
        
        # Save enhanced analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'Final_195_Sites_With_Poverty_{timestamp}.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Executive Summary with poverty stats
            exec_summary = pd.DataFrame([summary]).T.reset_index()
            exec_summary.columns = ['Metric', 'Value']
            exec_summary.to_excel(writer, sheet_name='Executive_Summary', index=False)
            
            # All sites with poverty data
            all_sites.to_excel(writer, sheet_name='All_Sites_With_Poverty', index=False)
            
            # Sites eligible for low poverty bonus
            low_poverty_sites = all_sites[all_sites['Low_Poverty_Bonus_9pct'] > 0]
            low_poverty_sites.to_excel(writer, sheet_name='Low_Poverty_Bonus_Sites', index=False)
            
            # Poverty analysis by source
            poverty_by_source = all_sites.groupby('Source').agg({
                'Poverty_Rate': ['mean', 'min', 'max', 'count'],
                'Low_Poverty_Bonus_9pct': 'sum'
            }).round(1)
            poverty_by_source.to_excel(writer, sheet_name='Poverty_By_Source')
            
            # Updated 9% rankings with poverty
            updated_9pct_exceptional = all_sites[all_sites['Updated_9pct_Ranking'] == 'Exceptional']
            updated_9pct_exceptional.to_excel(writer, sheet_name='9pct_Exceptional_With_Poverty', index=False)
            
            # Sites that improved due to poverty bonus
            improved_sites = all_sites[
                (all_sites.get('Corrected_9pct_Ranking', all_sites['Ranking_9pct']) != all_sites['Updated_9pct_Ranking']) &
                (all_sites['Low_Poverty_Bonus_9pct'] > 0)
            ]
            if len(improved_sites) > 0:
                improved_sites.to_excel(writer, sheet_name='Sites_Improved_By_Poverty', index=False)
        
        self.logger.info(f"Poverty analysis complete. Saved to: {output_file}")
        
        # Print summary
        print("\n=== POVERTY DATA INTEGRATION SUMMARY ===")
        for metric, value in summary.items():
            if isinstance(value, float):
                print(f"{metric}: {value:.1f}")
            else:
                print(f"{metric}: {value}")
        
        return all_sites, output_file

if __name__ == "__main__":
    integrator = PovertyDataIntegrator()
    
    # Use the most recent corrected analysis file
    input_file = 'Comprehensive_Corrected_195_QCT_DDA_20250621_202100.xlsx'
    
    enhanced_sites, output_path = integrator.run_poverty_integration(input_file)