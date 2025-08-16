#!/usr/bin/env python3
"""
Complete Poverty Analysis with PositionStack Geocoding
Uses PositionStack for missing coordinates, then adds poverty data for all 195 sites
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime
from pathlib import Path
import time
import logging

class CompletePovertyAnalyzer:
    """Complete poverty analysis with geocoding and Census data"""
    
    def __init__(self):
        self.census_api_key = '06ece0121263282cd9ffd753215b007b8f9a3dfc'
        self.positionstack_key = '41b80ed51d92978904592126d2bb8f7e'  # From handoff doc
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        
    def geocode_with_positionstack(self, address):
        """Geocode address using PositionStack API"""
        try:
            url = "http://api.positionstack.com/v1/forward"
            params = {
                'access_key': self.positionstack_key,
                'query': address,
                'limit': 1,
                'region': 'Texas',
                'country': 'US'
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    result = data['data'][0]
                    return {
                        'latitude': result.get('latitude'),
                        'longitude': result.get('longitude'),
                        'formatted_address': result.get('label', address)
                    }
            
            time.sleep(0.2)  # Rate limiting
            
        except Exception as e:
            self.logger.warning(f"PositionStack geocoding failed for {address}: {e}")
        
        return None
    
    def add_missing_coordinates(self, sites_df):
        """Add coordinates for sites missing them using PositionStack"""
        
        missing_coords = sites_df[sites_df['Latitude'].isna() | sites_df['Longitude'].isna()]
        self.logger.info(f"Geocoding {len(missing_coords)} sites with missing coordinates")
        
        for idx, row in missing_coords.iterrows():
            address = row.get('Address', '')
            city = row.get('City', '')
            state = row.get('State', 'TX')
            
            # Create full address
            if address:
                full_address = f"{address}, {city}, {state}"
            else:
                full_address = f"{city}, {state}"
            
            self.logger.info(f"Geocoding: {full_address}")
            
            coords = self.geocode_with_positionstack(full_address)
            
            if coords and coords['latitude'] and coords['longitude']:
                sites_df.at[idx, 'Latitude'] = coords['latitude']
                sites_df.at[idx, 'Longitude'] = coords['longitude']
                sites_df.at[idx, 'Geocoded_Address'] = coords['formatted_address']
                self.logger.info(f"Success: {coords['latitude']}, {coords['longitude']}")
            else:
                self.logger.warning(f"Failed to geocode: {full_address}")
        
        return sites_df
    
    def get_census_tract_poverty(self, lat, lon):
        """Get poverty rate using Census API with improved error handling"""
        
        cache_key = f"{lat:.6f},{lon:.6f}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Step 1: Get census tract
            geo_url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
            params = {
                'x': lon,
                'y': lat,
                'benchmark': '2020',
                'vintage': '2020',
                'layers': '10',  # Census Tracts
                'format': 'json'
            }
            
            response = requests.get(geo_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Navigate response structure
                result = data.get('result', {})
                geographies = result.get('geographies', {})
                
                # Find tract data
                tract_data = None
                for key, value in geographies.items():
                    if 'tract' in key.lower() and value:
                        tract_data = value[0]
                        break
                
                if tract_data:
                    state_fips = tract_data.get('STATE', '48')
                    county_fips = tract_data.get('COUNTY')
                    tract_fips = tract_data.get('TRACT')
                    
                    if county_fips and tract_fips:
                        # Step 2: Get poverty data
                        census_url = 'https://api.census.gov/data/2022/acs/acs5'
                        census_params = {
                            'get': 'B17001_002E,B17001_001E,NAME',
                            'for': f'tract:{tract_fips}',
                            'in': f'state:{state_fips} county:{county_fips}',
                            'key': self.census_api_key
                        }
                        
                        census_response = requests.get(census_url, params=census_params, timeout=30)
                        
                        if census_response.status_code == 200:
                            census_data = census_response.json()
                            if len(census_data) > 1:
                                values = census_data[1]
                                below_poverty = float(values[0]) if values[0] not in ['null', None, ''] else 0
                                total_pop = float(values[1]) if values[1] not in ['null', None, ''] else 0
                                
                                if total_pop > 0:
                                    poverty_rate = (below_poverty / total_pop) * 100
                                    result = {
                                        'poverty_rate': round(poverty_rate, 1),
                                        'census_tract': f"{state_fips}{county_fips}{tract_fips}",
                                        'tract_name': values[2] if len(values) > 2 else '',
                                        'total_population': int(total_pop),
                                        'below_poverty': int(below_poverty),
                                        'success': True
                                    }
                                    self.cache[cache_key] = result
                                    return result
            
            time.sleep(0.3)  # Rate limiting
            
        except Exception as e:
            self.logger.warning(f"Census API error for {lat}, {lon}: {e}")
        
        # Return failed result
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
    
    def add_poverty_data(self, sites_df):
        """Add poverty data to all sites"""
        
        # Initialize columns
        sites_df['Poverty_Rate_Pct'] = np.nan
        sites_df['Census_Tract'] = ''
        sites_df['Tract_Name'] = ''
        sites_df['Tract_Population'] = np.nan
        sites_df['Below_Poverty_Count'] = np.nan
        sites_df['Low_Poverty_Bonus_9pct'] = 0
        sites_df['Poverty_Category'] = ''
        
        success_count = 0
        total_with_coords = 0
        
        for idx, row in sites_df.iterrows():
            if idx % 20 == 0:
                self.logger.info(f"Processing poverty data: {idx}/{len(sites_df)} (Success: {success_count}/{total_with_coords})")
            
            lat = row.get('Latitude')
            lon = row.get('Longitude')
            
            if pd.notna(lat) and pd.notna(lon):
                total_with_coords += 1
                poverty_data = self.get_census_tract_poverty(lat, lon)
                
                if poverty_data['success'] and poverty_data['poverty_rate'] is not None:
                    sites_df.at[idx, 'Poverty_Rate_Pct'] = poverty_data['poverty_rate']
                    sites_df.at[idx, 'Census_Tract'] = poverty_data['census_tract']
                    sites_df.at[idx, 'Tract_Name'] = poverty_data['tract_name']
                    sites_df.at[idx, 'Tract_Population'] = poverty_data['total_population']
                    sites_df.at[idx, 'Below_Poverty_Count'] = poverty_data['below_poverty']
                    
                    # 9% Low Poverty Bonus (≤20% poverty rate)
                    if poverty_data['poverty_rate'] <= 20.0:
                        sites_df.at[idx, 'Low_Poverty_Bonus_9pct'] = 2
                    
                    # Categorize for market insights
                    if poverty_data['poverty_rate'] <= 10.0:
                        sites_df.at[idx, 'Poverty_Category'] = 'Very Low (<10%)'
                    elif poverty_data['poverty_rate'] <= 20.0:
                        sites_df.at[idx, 'Poverty_Category'] = 'Low (10-20%)'
                    elif poverty_data['poverty_rate'] <= 30.0:
                        sites_df.at[idx, 'Poverty_Category'] = 'Moderate (20-30%)'
                    else:
                        sites_df.at[idx, 'Poverty_Category'] = 'High (>30%)'
                    
                    success_count += 1
            else:
                city = row.get('City', 'Unknown')
                self.logger.debug(f"No coordinates for {city}")
        
        self.logger.info(f"Poverty data complete: {success_count}/{total_with_coords} sites with coordinates successful")
        return sites_df
    
    def update_9pct_rankings_with_poverty(self, sites_df):
        """Update 9% rankings considering poverty bonus"""
        
        sites_df['Final_9pct_Ranking'] = sites_df.get('Corrected_9pct_Ranking', sites_df.get('Ranking_9pct', 'Unknown'))
        
        # Track improvements
        improvements = 0
        
        for idx, row in sites_df.iterrows():
            if row['Low_Poverty_Bonus_9pct'] > 0:
                current = row['Final_9pct_Ranking']
                
                # Don't change Fatal rankings
                if current != 'Fatal':
                    # Poverty bonus can improve ranking by one tier
                    if current == 'Poor':
                        sites_df.at[idx, 'Final_9pct_Ranking'] = 'Good'
                        improvements += 1
                    elif current == 'Good':
                        sites_df.at[idx, 'Final_9pct_Ranking'] = 'High Potential'
                        improvements += 1
                    elif current == 'High Potential':
                        # Only move to exceptional if very close economically
                        ratio = row.get('Corrected_Revenue_Cost_Ratio', row.get('Revenue_Cost_Ratio', 0))
                        if ratio >= 0.085:
                            sites_df.at[idx, 'Final_9pct_Ranking'] = 'Exceptional'
                            improvements += 1
        
        self.logger.info(f"Poverty bonus improved {improvements} sites' 9% rankings")
        return sites_df
    
    def create_comprehensive_summary(self, sites_df):
        """Create comprehensive poverty analysis summary"""
        
        sites_with_poverty = sites_df[sites_df['Poverty_Rate_Pct'].notna()]
        
        summary = {
            'Total Sites': len(sites_df),
            'Sites with Coordinates': sites_df['Latitude'].notna().sum(),
            'Sites with Poverty Data': len(sites_with_poverty),
            'Sites with Low Poverty Bonus': (sites_df['Low_Poverty_Bonus_9pct'] > 0).sum(),
            'Overall Avg Poverty Rate': sites_with_poverty['Poverty_Rate_Pct'].mean() if len(sites_with_poverty) > 0 else 0
        }
        
        # Analysis by source
        for source in ['CoStar', 'DMarco_Brent', 'DMarco_Brian']:
            source_data = sites_with_poverty[sites_with_poverty['Source'] == source]
            if len(source_data) > 0:
                summary[f'{source} Avg Poverty'] = source_data['Poverty_Rate_Pct'].mean()
                summary[f'{source} Low Poverty Bonus'] = (source_data['Low_Poverty_Bonus_9pct'] > 0).sum()
                summary[f'{source} Total with Data'] = len(source_data)
        
        # Analysis by market type
        for market in ['Rural', 'Large City', 'Suburban', 'Mid City']:
            market_data = sites_with_poverty[sites_with_poverty['Market_Type'] == market]
            if len(market_data) > 0:
                summary[f'{market} Avg Poverty'] = market_data['Poverty_Rate_Pct'].mean()
                summary[f'{market} Low Poverty Bonus'] = (market_data['Low_Poverty_Bonus_9pct'] > 0).sum()
        
        return summary
    
    def run_complete_analysis(self, input_file):
        """Run complete poverty analysis"""
        
        self.logger.info("Starting complete poverty analysis with geocoding...")
        
        # Load data
        all_sites = pd.read_excel(input_file, sheet_name='All_195_Sites_Corrected')
        
        # Step 1: Add missing coordinates
        all_sites = self.add_missing_coordinates(all_sites)
        
        # Step 2: Add poverty data
        all_sites = self.add_poverty_data(all_sites)
        
        # Step 3: Update 9% rankings with poverty bonus
        all_sites = self.update_9pct_rankings_with_poverty(all_sites)
        
        # Step 4: Create summary
        summary = self.create_comprehensive_summary(all_sites)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'Complete_195_Sites_With_Poverty_{timestamp}.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Executive Summary
            exec_df = pd.DataFrame([summary]).T.reset_index()
            exec_df.columns = ['Metric', 'Value']
            exec_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
            
            # All sites with poverty
            all_sites.to_excel(writer, sheet_name='All_195_Sites_Complete', index=False)
            
            # Low poverty bonus sites (≤20% poverty)
            low_poverty = all_sites[all_sites['Low_Poverty_Bonus_9pct'] > 0].sort_values('Poverty_Rate_Pct')
            if len(low_poverty) > 0:
                low_poverty.to_excel(writer, sheet_name='Low_Poverty_Bonus_Sites', index=False)
            
            # D'Marco sites poverty analysis
            dmarco_all = all_sites[all_sites['Source'].isin(['DMarco_Brent', 'DMarco_Brian'])]
            dmarco_all.to_excel(writer, sheet_name='DMarco_Poverty_Analysis', index=False)
            
            # Brian sites specifically
            brian_sites = all_sites[all_sites['Source'] == 'DMarco_Brian']
            brian_sites.to_excel(writer, sheet_name='DMarco_Brian_Complete', index=False)
            
            # Final 9% exceptional with poverty
            final_9pct_exceptional = all_sites[all_sites['Final_9pct_Ranking'] == 'Exceptional']
            if len(final_9pct_exceptional) > 0:
                final_9pct_exceptional.to_excel(writer, sheet_name='Final_9pct_Exceptional', index=False)
            
            # Sites improved by poverty bonus
            original_col = 'Corrected_9pct_Ranking' if 'Corrected_9pct_Ranking' in all_sites.columns else 'Ranking_9pct'
            improved = all_sites[
                (all_sites[original_col] != all_sites['Final_9pct_Ranking']) &
                (all_sites['Low_Poverty_Bonus_9pct'] > 0)
            ]
            if len(improved) > 0:
                improved.to_excel(writer, sheet_name='Improved_By_Poverty_Bonus', index=False)
            
            # Poverty statistics by category
            poverty_stats = all_sites.groupby(['Source', 'Market_Type', 'Poverty_Category']).size().reset_index(name='Count')
            poverty_stats.to_excel(writer, sheet_name='Poverty_Category_Stats', index=False)
        
        self.logger.info(f"Complete analysis saved to: {output_file}")
        
        # Print summary
        print("\\n=== COMPLETE POVERTY ANALYSIS SUMMARY ===")
        for metric, value in summary.items():
            if isinstance(value, float):
                if 'Poverty' in metric or 'Avg' in metric:
                    print(f"{metric}: {value:.1f}%")
                else:
                    print(f"{metric}: {value:.1f}")
            else:
                print(f"{metric}: {value}")
        
        return all_sites, output_file

if __name__ == "__main__":
    analyzer = CompletePovertyAnalyzer()
    input_file = 'Comprehensive_Corrected_195_QCT_DDA_20250621_202100.xlsx'
    
    enhanced_sites, output_path = analyzer.run_complete_analysis(input_file)