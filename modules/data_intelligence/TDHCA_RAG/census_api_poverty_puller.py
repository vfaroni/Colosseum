#!/usr/bin/env python3
"""
CENSUS API POVERTY PULLER
Pull REAL ACS poverty data for ALL sites using Census API key
"""

import pandas as pd
import requests
import time
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class CensusAPIPovertyPuller:
    """Pull real ACS poverty data for all sites using Census API"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
        self.qct_dda_file = self.base_dir / "D'Marco_Sites/Analysis_Results/MASTER_155_BoostEligible_Sites_20250731_223500.xlsx"
        
        # Census API key from the ACS integrator
        self.census_api_key = "06ece0121263282cd9ffd753215b007b8f9a3dfc"
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def extract_fips_components(self, full_fips_tract):
        """Extract state, county, and tract FIPS from full 11-digit code"""
        full_fips_str = str(int(full_fips_tract))
        
        if len(full_fips_str) == 11:
            state_fips = full_fips_str[:2]      # 48
            county_fips = full_fips_str[2:5]    # 121  
            tract_fips = full_fips_str[5:]      # 021750
            
            return state_fips, county_fips, tract_fips
        else:
            print(f"⚠️ Unexpected FIPS length: {full_fips_str} ({len(full_fips_str)} digits)")
            return None, None, None
    
    def get_acs_poverty_rate_from_api(self, state_fips, county_fips, tract_fips, site_address=""):
        """Pull REAL ACS poverty rate from Census API"""
        try:
            # ACS 5-Year Estimates API endpoint for 2022 data
            url = "https://api.census.gov/data/2022/acs/acs5"
            
            params = {
                'get': 'B17001_002E,B17001_001E',  # Poverty count, total population
                'for': f'tract:{tract_fips}',
                'in': f'state:{state_fips} county:{county_fips}',
                'key': self.census_api_key
            }
            
            print(f"   API call: tract {tract_fips} in county {county_fips}, state {state_fips}")
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if len(data) > 1:  # Header + data row
                    row = data[1]
                    poverty_count = float(row[0]) if row[0] and row[0] not in ['-999999999', 'null'] else 0
                    total_pop = float(row[1]) if row[1] and row[1] not in ['-999999999', 'null'] else 0
                    
                    if total_pop > 0:
                        poverty_rate = (poverty_count / total_pop) * 100
                        
                        return {
                            'acs_poverty_rate': round(poverty_rate, 2),
                            'poverty_count': int(poverty_count),
                            'total_population': int(total_pop),
                            'state_fips': state_fips,
                            'county_fips': county_fips,
                            'tract_fips': tract_fips,
                            'full_fips': f"{state_fips}{county_fips}{tract_fips}",
                            'data_source': 'CENSUS_API_ACS_2022_5_YEAR',
                            'api_status': 'SUCCESS'
                        }
                    else:
                        return {
                            'api_status': 'NO_POPULATION_DATA',
                            'error': f'Total population is {total_pop}'
                        }
                else:
                    return {
                        'api_status': 'NO_DATA_RETURNED',
                        'error': f'API returned {len(data)} rows'
                    }
            else:
                return {
                    'api_status': 'API_ERROR',
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'api_status': 'EXCEPTION',
                'error': str(e)
            }
    
    def pull_poverty_for_all_sites(self):
        """Pull ACS poverty data for ALL 155 sites"""
        print("🔄 Pulling REAL ACS poverty data for ALL sites...")
        
        # Load QCT sites
        try:
            qct_df = pd.read_excel(self.qct_dda_file)
            print(f"📊 Loaded {len(qct_df)} sites for Census API processing")
        except Exception as e:
            print(f"❌ Failed to load QCT data: {e}")
            return None
        
        # Add Census API result columns
        census_columns = [
            'ACS_Poverty_Rate_API', 'Poverty_Count', 'Total_Population',
            'State_FIPS', 'County_FIPS', 'Tract_FIPS', 'Full_FIPS_Constructed',
            'Census_API_Status', 'Census_API_Error', 'Census_Data_Source'
        ]
        
        for col in census_columns:
            qct_df[col] = 'PENDING'
        
        successful_pulls = 0
        failed_pulls = 0
        
        print(f"\n🎯 Starting Census API calls for {len(qct_df)} sites...")
        print("=" * 80)
        
        for idx, site in qct_df.iterrows():
            site_address = site.get('Address', 'Unknown')
            final_tract = site.get('FINAL_TRACT')
            
            print(f"\n📍 Site {idx + 1}/{len(qct_df)}: {site_address}")
            
            if final_tract and pd.notna(final_tract):
                # Extract FIPS components
                state_fips, county_fips, tract_fips = self.extract_fips_components(final_tract)
                
                if state_fips and county_fips and tract_fips:
                    print(f"   FIPS breakdown: State={state_fips}, County={county_fips}, Tract={tract_fips}")
                    
                    # Call Census API
                    api_result = self.get_acs_poverty_rate_from_api(
                        state_fips, county_fips, tract_fips, site_address
                    )
                    
                    if api_result.get('api_status') == 'SUCCESS':
                        # Success - populate all data
                        qct_df.loc[idx, 'ACS_Poverty_Rate_API'] = api_result['acs_poverty_rate']
                        qct_df.loc[idx, 'Poverty_Count'] = api_result['poverty_count']
                        qct_df.loc[idx, 'Total_Population'] = api_result['total_population']
                        qct_df.loc[idx, 'State_FIPS'] = api_result['state_fips']
                        qct_df.loc[idx, 'County_FIPS'] = api_result['county_fips']
                        qct_df.loc[idx, 'Tract_FIPS'] = api_result['tract_fips']
                        qct_df.loc[idx, 'Full_FIPS_Constructed'] = api_result['full_fips']
                        qct_df.loc[idx, 'Census_API_Status'] = 'SUCCESS'
                        qct_df.loc[idx, 'Census_API_Error'] = 'NONE'
                        qct_df.loc[idx, 'Census_Data_Source'] = api_result['data_source']
                        
                        successful_pulls += 1
                        print(f"   ✅ SUCCESS: {api_result['acs_poverty_rate']}% poverty ({api_result['poverty_count']}/{api_result['total_population']} people)")
                    else:
                        # Failed - record error
                        qct_df.loc[idx, 'ACS_Poverty_Rate_API'] = 'API_FAILED'
                        qct_df.loc[idx, 'Census_API_Status'] = api_result['api_status']
                        qct_df.loc[idx, 'Census_API_Error'] = api_result.get('error', 'Unknown error')
                        qct_df.loc[idx, 'Census_Data_Source'] = 'FAILED'
                        
                        failed_pulls += 1
                        print(f"   ❌ FAILED: {api_result['api_status']} - {api_result.get('error', 'Unknown error')}")
                else:
                    # FIPS extraction failed
                    qct_df.loc[idx, 'ACS_Poverty_Rate_API'] = 'FIPS_ERROR'
                    qct_df.loc[idx, 'Census_API_Status'] = 'FIPS_EXTRACTION_FAILED'
                    qct_df.loc[idx, 'Census_API_Error'] = f'Could not extract FIPS from {final_tract}'
                    failed_pulls += 1
                    print(f"   ❌ FIPS extraction failed for {final_tract}")
            else:
                # No census tract data
                qct_df.loc[idx, 'ACS_Poverty_Rate_API'] = 'NO_TRACT'
                qct_df.loc[idx, 'Census_API_Status'] = 'NO_FINAL_TRACT'
                qct_df.loc[idx, 'Census_API_Error'] = 'FINAL_TRACT missing or null'
                failed_pulls += 1
                print(f"   ❌ No FINAL_TRACT data")
            
            # Rate limiting - be respectful to Census API
            if (idx + 1) % 10 == 0:
                print(f"\n⏸️ Progress checkpoint: {idx + 1}/{len(qct_df)} sites processed")
                print(f"   ✅ Successful: {successful_pulls}, ❌ Failed: {failed_pulls}")
                time.sleep(2)  # Longer pause every 10 calls
            else:
                time.sleep(0.5)  # Short pause between calls
        
        print(f"\n" + "=" * 80)
        print(f"🎯 CENSUS API PROCESSING COMPLETE")
        print(f"   ✅ Successful API calls: {successful_pulls}/{len(qct_df)} ({successful_pulls/len(qct_df)*100:.1f}%)")
        print(f"   ❌ Failed API calls: {failed_pulls}/{len(qct_df)} ({failed_pulls/len(qct_df)*100:.1f}%)")
        
        if successful_pulls > 0:
            # Show poverty rate statistics
            successful_sites = qct_df[qct_df['Census_API_Status'] == 'SUCCESS']
            rates = pd.to_numeric(successful_sites['ACS_Poverty_Rate_API'], errors='coerce')
            unique_rates = rates.nunique()
            
            print(f"   📊 Poverty rate stats: {unique_rates} unique rates, {rates.min():.1f}% - {rates.max():.1f}%")
        
        return qct_df
    
    def save_census_api_results(self, results_df):
        """Save Census API results"""
        results_dir = self.base_dir / "D'Marco_Sites/Analysis_Results"
        
        excel_file = results_dir / f"CENSUS_API_POVERTY_PULL_{self.timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main results with all Census API data
            results_df.to_excel(writer, sheet_name='Census_API_Results', index=False)
            
            # Successfully pulled poverty data only
            successful_sites = results_df[results_df['Census_API_Status'] == 'SUCCESS']
            successful_sites.to_excel(writer, sheet_name='Successful_API_Pulls', index=False)
            
            # Failed pulls for debugging
            failed_sites = results_df[results_df['Census_API_Status'] != 'SUCCESS']
            failed_sites.to_excel(writer, sheet_name='Failed_API_Pulls', index=False)
            
            # API status summary
            status_summary = results_df['Census_API_Status'].value_counts()
            summary_df = pd.DataFrame({'API_Status': status_summary.index, 'Count': status_summary.values})
            summary_df.to_excel(writer, sheet_name='API_Status_Summary', index=False)
        
        print(f"\n💾 CENSUS API RESULTS SAVED:")
        print(f"   📊 Excel: {excel_file.name}")
        print(f"   📈 Total sites: {len(results_df)}")
        
        successful_count = (results_df['Census_API_Status'] == 'SUCCESS').sum()
        print(f"   ✅ Sites with REAL ACS poverty data: {successful_count}")
        
        return excel_file

def main():
    """Execute Census API poverty data pull"""
    print("🔄 CENSUS API POVERTY PULLER")
    print("🎯 OBJECTIVE: Pull REAL ACS poverty data for ALL 155 sites")
    print("📊 SOURCE: Census API with ACS 2022 5-Year Estimates")
    print("🔑 API KEY: Using configured Census API key")
    print("=" * 90)
    
    puller = CensusAPIPovertyPuller()
    
    # Pull poverty data for all sites
    results_df = puller.pull_poverty_for_all_sites()
    
    if results_df is None:
        print("❌ Census API pull failed")
        return
    
    # Save results
    excel_file = puller.save_census_api_results(results_df)
    
    successful_count = (results_df['Census_API_Status'] == 'SUCCESS').sum()
    
    print(f"\n✅ CENSUS API POVERTY PULL COMPLETE")
    print(f"📁 Results: {excel_file.name}")
    print(f"🎯 REAL ACS poverty data: {successful_count}/155 sites")
    print(f"\n🚀 NO MORE LIMITED POVERTY DATA - PULLED FRESH FROM CENSUS API")

if __name__ == "__main__":
    main()