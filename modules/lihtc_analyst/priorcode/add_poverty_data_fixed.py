#!/usr/bin/env python3
"""
Add Poverty Rate Data to 195 Sites Analysis - Fixed Version
Integrates Census ACS poverty data for both 9% scoring and market area insights
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime
from pathlib import Path
import time
import logging
import json

class PovertyDataIntegrator:
    """Add poverty rate data to existing analysis"""
    
    def __init__(self):
        self.api_key = '06ece0121263282cd9ffd753215b007b8f9a3dfc'
        self.base_path = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects")
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.cache = {}  # Cache to avoid duplicate API calls
        
    def get_census_tract_poverty(self, lat, lon, state='TX'):
        """Get poverty rate for a specific location using Census API"""
        
        # Check cache first
        cache_key = f"{lat:.6f},{lon:.6f}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Get census tract using Census geocoder
            geo_url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
            params = {
                'x': lon,
                'y': lat,
                'benchmark': 'Public_AR_Current',
                'vintage': 'Current_Current',
                'layers': '10',  # Census Tracts
                'format': 'json'
            }
            
            self.logger.debug(f"Geocoding: {lat}, {lon}")
            response = requests.get(geo_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'result' in data and 'geographies' in data['result']:
                    geographies = data['result']['geographies']
                    
                    # Look for Census Tracts in the response
                    tract_data = None
                    for key in geographies:
                        if 'Tract' in key or 'tract' in key:
                            if geographies[key]:
                                tract_data = geographies[key][0]
                                break
                    
                    if tract_data:
                        state_fips = tract_data.get('STATE', '48')  # Default to Texas
                        county_fips = tract_data['COUNTY']
                        tract_fips = tract_data['TRACT']
                        
                        # Get poverty data from ACS
                        census_url = 'https://api.census.gov/data/2022/acs/acs5'
                        
                        census_params = {
                            'get': 'B17001_002E,B17001_001E,NAME',
                            'for': f'tract:{tract_fips}',
                            'in': f'state:{state_fips} county:{county_fips}',
                            'key': self.api_key
                        }
                        
                        census_response = requests.get(census_url, params=census_params, timeout=30)
                        
                        if census_response.status_code == 200:
                            census_data = census_response.json()
                            if len(census_data) > 1:
                                values = census_data[1]
                                below_poverty = float(values[0]) if values[0] and values[0] != 'null' else 0
                                total_pop = float(values[1]) if values[1] and values[1] != 'null' else 0
                                
                                if total_pop > 0:
                                    poverty_rate = (below_poverty / total_pop) * 100
                                    result = {
                                        'poverty_rate': round(poverty_rate, 1),
                                        'census_tract': f"{state_fips}{county_fips}{tract_fips}",
                                        'tract_name': values[2] if len(values) > 2 else '',
                                        'total_population': int(total_pop),
                                        'below_poverty': int(below_poverty)
                                    }
                                    self.cache[cache_key] = result
                                    return result
            
            time.sleep(0.2)  # Rate limiting
            
        except Exception as e:
            self.logger.warning(f"Error getting poverty data for {lat}, {lon}: {str(e)}")
        
        # Return None values if failed
        result = {
            'poverty_rate': None,
            'census_tract': None,
            'tract_name': None,
            'total_population': None,
            'below_poverty': None
        }
        self.cache[cache_key] = result
        return result
    
    def add_poverty_to_sites(self, sites_df):
        """Add poverty data to all sites"""
        
        # Initialize poverty columns
        sites_df['Poverty_Rate'] = np.nan
        sites_df['Census_Tract'] = ''
        sites_df['Tract_Name'] = ''
        sites_df['Tract_Population'] = np.nan
        sites_df['Below_Poverty_Count'] = np.nan
        sites_df['Low_Poverty_Bonus_9pct'] = 0
        sites_df['Poverty_Category'] = ''
        
        successful = 0
        failed = 0
        
        # Process each site with coordinates
        for idx, row in sites_df.iterrows():
            if idx % 10 == 0:
                self.logger.info(f"Processing poverty data: {idx}/{len(sites_df)} sites (Success: {successful}, Failed: {failed})")
            
            # Get coordinates - use capital L for Latitude/Longitude
            lat = row.get('Latitude')
            lon = row.get('Longitude')
            
            if pd.notna(lat) and pd.notna(lon):
                poverty_data = self.get_census_tract_poverty(lat, lon)
                
                if poverty_data['poverty_rate'] is not None:
                    sites_df.at[idx, 'Poverty_Rate'] = poverty_data['poverty_rate']
                    sites_df.at[idx, 'Census_Tract'] = poverty_data['census_tract']
                    sites_df.at[idx, 'Tract_Name'] = poverty_data['tract_name']
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
                    
                    successful += 1
                else:
                    failed += 1
            else:
                self.logger.debug(f"No coordinates for site at index {idx}: {row.get('City', 'Unknown')}")
        
        self.logger.info(f"Poverty data collection complete. Success: {successful}, Failed: {failed}")
        return sites_df
    
    def recalculate_9pct_rankings(self, sites_df):
        """Recalculate 9% rankings with poverty bonus"""
        
        # Create new ranking column that includes poverty bonus
        sites_df['Updated_9pct_Ranking'] = sites_df['Corrected_9pct_Ranking'].copy()
        
        # For sites with low poverty bonus, potentially improve their ranking
        for idx, row in sites_df.iterrows():
            if row['Low_Poverty_Bonus_9pct'] > 0:
                current_ranking = row.get('Corrected_9pct_Ranking', row.get('Ranking_9pct', 'Unknown'))
                
                # Don't change Fatal rankings
                if current_ranking != 'Fatal':
                    # Poverty bonus can move sites up one tier
                    if current_ranking == 'Poor':
                        sites_df.at[idx, 'Updated_9pct_Ranking'] = 'Good'
                    elif current_ranking == 'Good':
                        sites_df.at[idx, 'Updated_9pct_Ranking'] = 'High Potential'
                    elif current_ranking == 'High Potential':
                        # Check if revenue/cost ratio is close to exceptional threshold
                        ratio = row.get('Corrected_Revenue_Cost_Ratio', row.get('Revenue_Cost_Ratio', 0))
                        if ratio >= 0.085:  # Close enough with poverty bonus
                            sites_df.at[idx, 'Updated_9pct_Ranking'] = 'Exceptional'
        
        return sites_df
    
    def create_poverty_summary(self, sites_df):
        """Create summary statistics for poverty data"""
        
        sites_with_data = sites_df[sites_df['Poverty_Rate'].notna()]
        
        summary = {
            'Total Sites Analyzed': len(sites_df),
            'Sites with Poverty Data': len(sites_with_data),
            'Sites Missing Poverty Data': len(sites_df) - len(sites_with_data),
            'Sites with Low Poverty Bonus (≤20%)': (sites_df['Low_Poverty_Bonus_9pct'] > 0).sum(),
            'Average Poverty Rate': sites_with_data['Poverty_Rate'].mean() if len(sites_with_data) > 0 else 0,
            'Median Poverty Rate': sites_with_data['Poverty_Rate'].median() if len(sites_with_data) > 0 else 0
        }
        
        # By source
        for source in sites_df['Source'].unique():
            source_data = sites_with_data[sites_with_data['Source'] == source]
            if len(source_data) > 0:
                summary[f'{source} Avg Poverty Rate'] = source_data['Poverty_Rate'].mean()
                summary[f'{source} Low Poverty Sites'] = (source_data['Low_Poverty_Bonus_9pct'] > 0).sum()
                summary[f'{source} Sites with Data'] = len(source_data)
        
        # By market type
        for market in ['Rural', 'Large City', 'Suburban', 'Mid City']:
            if market in sites_df['Market_Type'].values:
                market_data = sites_with_data[sites_with_data['Market_Type'] == market]
                if len(market_data) > 0:
                    summary[f'{market} Avg Poverty Rate'] = market_data['Poverty_Rate'].mean()
                    summary[f'{market} Low Poverty Sites'] = (market_data['Low_Poverty_Bonus_9pct'] > 0).sum()
        
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
            # Executive Summary
            exec_summary = pd.DataFrame([summary]).T.reset_index()
            exec_summary.columns = ['Metric', 'Value']
            exec_summary.to_excel(writer, sheet_name='Executive_Summary', index=False)
            
            # All sites with poverty data
            all_sites.to_excel(writer, sheet_name='All_Sites_With_Poverty', index=False)
            
            # Low poverty bonus sites
            low_poverty_sites = all_sites[all_sites['Low_Poverty_Bonus_9pct'] > 0].sort_values('Poverty_Rate')
            if len(low_poverty_sites) > 0:
                low_poverty_sites.to_excel(writer, sheet_name='Low_Poverty_Bonus_Sites', index=False)
            
            # Poverty by source
            poverty_by_source = all_sites.groupby('Source').agg({
                'Poverty_Rate': ['mean', 'min', 'max', 'count'],
                'Low_Poverty_Bonus_9pct': 'sum'
            }).round(1)
            poverty_by_source.to_excel(writer, sheet_name='Poverty_By_Source')
            
            # Updated 9% rankings
            updated_9pct_exceptional = all_sites[all_sites['Updated_9pct_Ranking'] == 'Exceptional']
            if len(updated_9pct_exceptional) > 0:
                updated_9pct_exceptional.to_excel(writer, sheet_name='9pct_Exceptional_With_Poverty', index=False)
            
            # Sites improved by poverty bonus
            original_ranking_col = 'Corrected_9pct_Ranking' if 'Corrected_9pct_Ranking' in all_sites.columns else 'Ranking_9pct'
            improved_sites = all_sites[
                (all_sites[original_ranking_col] != all_sites['Updated_9pct_Ranking']) &
                (all_sites['Low_Poverty_Bonus_9pct'] > 0)
            ]
            if len(improved_sites) > 0:
                improved_sites.to_excel(writer, sheet_name='Sites_Improved_By_Poverty', index=False)
            
            # D'Marco sites poverty analysis
            dmarco_sites = all_sites[all_sites['Source'].isin(['DMarco_Brent', 'DMarco_Brian'])]
            if len(dmarco_sites) > 0:
                dmarco_sites.to_excel(writer, sheet_name='DMarco_Poverty_Analysis', index=False)
        
        self.logger.info(f"Poverty analysis complete. Saved to: {output_file}")
        
        # Print summary
        print("\n=== POVERTY DATA INTEGRATION SUMMARY ===")
        for metric, value in summary.items():
            if isinstance(value, (int, float)):
                if 'Rate' in metric or 'Avg' in metric:
                    print(f"{metric}: {value:.1f}%")
                else:
                    print(f"{metric}: {int(value)}")
            else:
                print(f"{metric}: {value}")
        
        return all_sites, output_file

if __name__ == "__main__":
    integrator = PovertyDataIntegrator()
    
    # Use the comprehensive corrected analysis file
    input_file = 'Comprehensive_Corrected_195_QCT_DDA_20250621_202100.xlsx'
    
    enhanced_sites, output_path = integrator.run_poverty_integration(input_file)