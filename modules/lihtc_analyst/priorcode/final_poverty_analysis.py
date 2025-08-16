#!/usr/bin/env python3
"""
Final Poverty Analysis - Fixed Census API Calls
Uses correct Census API endpoints for tract-level poverty data
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time
import logging

class FinalPovertyAnalyzer:
    """Final poverty analysis with working Census API calls"""
    
    def __init__(self):
        self.census_api_key = '06ece0121263282cd9ffd753215b007b8f9a3dfc'
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        
    def get_tract_poverty_direct(self, lat, lon, state='48'):
        """Get poverty data using direct Census tract lookup"""
        
        cache_key = f"{lat:.6f},{lon:.6f}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Method 1: Use FCC API to get tract, then Census for poverty
            fcc_url = f"https://geo.fcc.gov/api/census/area"
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json'
            }
            
            response = requests.get(fcc_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and data['results']:
                    tract_fips = data['results'][0]['block_fips'][:11]  # First 11 digits = state+county+tract
                    state_fips = tract_fips[:2]
                    county_fips = tract_fips[2:5] 
                    tract_code = tract_fips[5:11]
                    
                    # Get poverty data from ACS
                    census_url = 'https://api.census.gov/data/2022/acs/acs5'
                    census_params = {
                        'get': 'B17001_002E,B17001_001E,NAME',
                        'for': f'tract:{tract_code}',
                        'in': f'state:{state_fips} county:{county_fips}',
                        'key': self.census_api_key
                    }
                    
                    census_response = requests.get(census_url, params=census_params, timeout=30)
                    
                    if census_response.status_code == 200:
                        census_data = census_response.json()
                        if len(census_data) > 1:
                            values = census_data[1]
                            below_poverty = float(values[0]) if values[0] not in ['null', None, '', '-666666666'] else 0
                            total_pop = float(values[1]) if values[1] not in ['null', None, '', '-666666666'] else 0
                            
                            if total_pop > 0:
                                poverty_rate = (below_poverty / total_pop) * 100
                                result = {
                                    'poverty_rate': round(poverty_rate, 1),
                                    'census_tract': tract_fips,
                                    'tract_name': values[2] if len(values) > 2 else '',
                                    'total_population': int(total_pop),
                                    'below_poverty': int(below_poverty),
                                    'state_fips': state_fips,
                                    'county_fips': county_fips,
                                    'tract_code': tract_code,
                                    'success': True
                                }
                                self.cache[cache_key] = result
                                return result
            
            time.sleep(0.2)  # Rate limiting
            
        except Exception as e:
            self.logger.warning(f"Error getting poverty data for {lat}, {lon}: {str(e)}")
        
        # Return failure
        result = {
            'poverty_rate': None,
            'census_tract': None,
            'tract_name': None,
            'total_population': None,
            'below_poverty': None,
            'success': False
        }
        self.cache[cache_key] = result
        return result
    
    def add_complete_poverty_data(self, sites_df):
        """Add poverty data to all sites with coordinates"""
        
        # Initialize poverty columns
        sites_df['Poverty_Rate_Pct'] = np.nan
        sites_df['Census_Tract_FIPS'] = ''
        sites_df['Tract_Name'] = ''
        sites_df['Tract_Population'] = np.nan
        sites_df['Below_Poverty_Count'] = np.nan
        sites_df['Low_Poverty_Bonus_9pct'] = 0
        sites_df['Poverty_Category'] = ''
        sites_df['Poverty_Data_Source'] = ''
        
        success_count = 0
        total_attempts = 0
        
        # Process sites with coordinates
        sites_with_coords = sites_df[sites_df['Latitude'].notna() & sites_df['Longitude'].notna()]
        self.logger.info(f"Processing poverty data for {len(sites_with_coords)} sites with coordinates")
        
        for idx, row in sites_with_coords.iterrows():
            if total_attempts % 25 == 0:
                self.logger.info(f"Progress: {total_attempts}/{len(sites_with_coords)} (Success: {success_count})")
            
            lat = row['Latitude']
            lon = row['Longitude']
            city = row.get('City', 'Unknown')
            
            poverty_data = self.get_tract_poverty_direct(lat, lon)
            total_attempts += 1
            
            if poverty_data['success'] and poverty_data['poverty_rate'] is not None:
                sites_df.at[idx, 'Poverty_Rate_Pct'] = poverty_data['poverty_rate']
                sites_df.at[idx, 'Census_Tract_FIPS'] = poverty_data['census_tract']
                sites_df.at[idx, 'Tract_Name'] = poverty_data['tract_name']
                sites_df.at[idx, 'Tract_Population'] = poverty_data['total_population']
                sites_df.at[idx, 'Below_Poverty_Count'] = poverty_data['below_poverty']
                sites_df.at[idx, 'Poverty_Data_Source'] = 'Census ACS 2022'
                
                # Calculate 9% Low Poverty Bonus (≤20% poverty rate)
                if poverty_data['poverty_rate'] <= 20.0:
                    sites_df.at[idx, 'Low_Poverty_Bonus_9pct'] = 2
                
                # Categorize poverty level
                if poverty_data['poverty_rate'] <= 10.0:
                    sites_df.at[idx, 'Poverty_Category'] = 'Very Low (<10%)'
                elif poverty_data['poverty_rate'] <= 20.0:
                    sites_df.at[idx, 'Poverty_Category'] = 'Low (10-20%)'
                elif poverty_data['poverty_rate'] <= 30.0:
                    sites_df.at[idx, 'Poverty_Category'] = 'Moderate (20-30%)'
                else:
                    sites_df.at[idx, 'Poverty_Category'] = 'High (>30%)'
                
                success_count += 1
                self.logger.debug(f"Success: {city} - {poverty_data['poverty_rate']}% poverty")
            else:
                self.logger.debug(f"Failed: {city} at {lat}, {lon}")
        
        self.logger.info(f"Poverty data collection complete: {success_count}/{len(sites_with_coords)} successful")
        return sites_df
    
    def update_rankings_with_poverty(self, sites_df):
        """Update 9% rankings considering low poverty bonus"""
        
        # Create final ranking column
        sites_df['Final_9pct_Ranking_With_Poverty'] = sites_df.get('Corrected_9pct_Ranking', 
                                                                   sites_df.get('Ranking_9pct', 'Unknown'))
        
        improvements = 0
        
        # Apply poverty bonus improvements
        for idx, row in sites_df.iterrows():
            if row['Low_Poverty_Bonus_9pct'] > 0:  # Has poverty bonus
                current_ranking = row['Final_9pct_Ranking_With_Poverty']
                
                # Don't improve Fatal rankings
                if current_ranking != 'Fatal':
                    # Poverty bonus can improve ranking by one tier
                    new_ranking = current_ranking
                    
                    if current_ranking == 'Poor':
                        new_ranking = 'Good'
                        improvements += 1
                    elif current_ranking == 'Good':
                        new_ranking = 'High Potential'
                        improvements += 1
                    elif current_ranking == 'High Potential':
                        # Only move to Exceptional if economically strong too
                        ratio = row.get('Corrected_Revenue_Cost_Ratio', row.get('Revenue_Cost_Ratio', 0))
                        if ratio >= 0.085:  # Close to exceptional threshold
                            new_ranking = 'Exceptional'
                            improvements += 1
                    
                    sites_df.at[idx, 'Final_9pct_Ranking_With_Poverty'] = new_ranking
        
        self.logger.info(f"Poverty bonus improved {improvements} sites' 9% rankings")
        return sites_df
    
    def create_final_summary(self, sites_df):
        """Create comprehensive final summary"""
        
        sites_with_poverty = sites_df[sites_df['Poverty_Rate_Pct'].notna()]
        
        summary = {
            # Basic counts
            'Total Sites': len(sites_df),
            'Sites with Coordinates': sites_df['Latitude'].notna().sum(),
            'Sites with Poverty Data': len(sites_with_poverty),
            'Data Success Rate (%)': (len(sites_with_poverty) / sites_df['Latitude'].notna().sum()) * 100 if sites_df['Latitude'].notna().sum() > 0 else 0,
            
            # Poverty statistics
            'Sites with Low Poverty Bonus': (sites_df['Low_Poverty_Bonus_9pct'] > 0).sum(),
            'Overall Avg Poverty Rate (%)': sites_with_poverty['Poverty_Rate_Pct'].mean() if len(sites_with_poverty) > 0 else 0,
            'Median Poverty Rate (%)': sites_with_poverty['Poverty_Rate_Pct'].median() if len(sites_with_poverty) > 0 else 0,
            
            # By poverty category
            'Very Low Poverty Sites (<10%)': (sites_df['Poverty_Category'] == 'Very Low (<10%)').sum(),
            'Low Poverty Sites (10-20%)': (sites_df['Poverty_Category'] == 'Low (10-20%)').sum(),
            'Moderate Poverty Sites (20-30%)': (sites_df['Poverty_Category'] == 'Moderate (20-30%)').sum(),
            'High Poverty Sites (>30%)': (sites_df['Poverty_Category'] == 'High (>30%)').sum(),
        }
        
        # By source
        for source in ['CoStar', 'DMarco_Brent', 'DMarco_Brian']:
            source_data = sites_with_poverty[sites_with_poverty['Source'] == source]
            if len(source_data) > 0:
                summary[f'{source} Avg Poverty (%)'] = source_data['Poverty_Rate_Pct'].mean()
                summary[f'{source} Low Poverty Bonus Count'] = (source_data['Low_Poverty_Bonus_9pct'] > 0).sum()
                summary[f'{source} Sites with Data'] = len(source_data)
        
        # By market type
        for market in ['Rural', 'Large City', 'Suburban', 'Mid City']:
            market_data = sites_with_poverty[sites_with_poverty['Market_Type'] == market]
            if len(market_data) > 0:
                summary[f'{market} Avg Poverty (%)'] = market_data['Poverty_Rate_Pct'].mean()
                summary[f'{market} Low Poverty Bonus Count'] = (market_data['Low_Poverty_Bonus_9pct'] > 0).sum()
        
        # Rankings comparison
        if 'Final_9pct_Ranking_With_Poverty' in sites_df.columns:
            final_rankings = sites_df['Final_9pct_Ranking_With_Poverty'].value_counts()
            for ranking in ['Exceptional', 'High Potential', 'Good', 'Poor', 'Fatal']:
                summary[f'Final 9% {ranking} Sites'] = final_rankings.get(ranking, 0)
        
        return summary
    
    def run_final_analysis(self, input_file):
        """Run the final comprehensive poverty analysis"""
        
        self.logger.info("Starting final poverty analysis...")
        
        # Load the most recent file with coordinates
        all_sites = pd.read_excel(input_file, sheet_name='All_195_Sites_Complete')
        
        # Add poverty data
        all_sites = self.add_complete_poverty_data(all_sites)
        
        # Update 9% rankings with poverty bonus
        all_sites = self.update_rankings_with_poverty(all_sites)
        
        # Create final summary
        summary = self.create_final_summary(all_sites)
        
        # Save final results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'FINAL_195_Sites_Complete_With_Poverty_{timestamp}.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Executive Summary
            exec_df = pd.DataFrame([summary]).T.reset_index()
            exec_df.columns = ['Metric', 'Value']
            exec_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
            
            # Complete dataset
            all_sites.to_excel(writer, sheet_name='All_195_Sites_Final', index=False)
            
            # Sites by poverty category
            for category in ['Very Low (<10%)', 'Low (10-20%)', 'Moderate (20-30%)', 'High (>30%)']:
                category_sites = all_sites[all_sites['Poverty_Category'] == category]
                if len(category_sites) > 0:
                    sheet_name = f"Poverty_{category.split('(')[0].strip().replace(' ', '_')}"
                    category_sites.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Low poverty bonus sites (for 9% deals)
            low_poverty_bonus = all_sites[all_sites['Low_Poverty_Bonus_9pct'] > 0].sort_values('Poverty_Rate_Pct')
            if len(low_poverty_bonus) > 0:
                low_poverty_bonus.to_excel(writer, sheet_name='Low_Poverty_Bonus_9pct', index=False)
            
            # Final 9% rankings with poverty
            final_exceptional = all_sites[all_sites['Final_9pct_Ranking_With_Poverty'] == 'Exceptional']
            if len(final_exceptional) > 0:
                final_exceptional.to_excel(writer, sheet_name='Final_9pct_Exceptional', index=False)
            
            # D'Marco analysis with poverty
            dmarco_all = all_sites[all_sites['Source'].isin(['DMarco_Brent', 'DMarco_Brian'])]
            dmarco_all.to_excel(writer, sheet_name='DMarco_With_Poverty', index=False)
            
            # Source comparison
            source_comparison = all_sites.groupby('Source').agg({
                'Poverty_Rate_Pct': ['count', 'mean', 'min', 'max'],
                'Low_Poverty_Bonus_9pct': 'sum'
            }).round(1)
            source_comparison.to_excel(writer, sheet_name='Source_Poverty_Comparison')
            
            # Market type comparison
            market_comparison = all_sites.groupby('Market_Type').agg({
                'Poverty_Rate_Pct': ['count', 'mean', 'min', 'max'],
                'Low_Poverty_Bonus_9pct': 'sum'
            }).round(1)
            market_comparison.to_excel(writer, sheet_name='Market_Poverty_Comparison')
        
        self.logger.info(f"Final analysis complete. Saved to: {output_file}")
        
        # Print summary
        print("\\n=== FINAL POVERTY ANALYSIS SUMMARY ===")
        for metric, value in summary.items():
            if isinstance(value, float):
                if any(word in metric for word in ['Rate', 'Poverty', '%']):
                    print(f"{metric}: {value:.1f}%")
                else:
                    print(f"{metric}: {value:.1f}")
            else:
                print(f"{metric}: {value}")
        
        return all_sites, output_file

if __name__ == "__main__":
    analyzer = FinalPovertyAnalyzer()
    
    # Use the file with coordinates added
    input_file = 'Complete_195_Sites_With_Poverty_20250621_213017.xlsx'
    
    final_sites, final_output = analyzer.run_final_analysis(input_file)