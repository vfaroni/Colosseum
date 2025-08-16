#!/usr/bin/env python3
"""
BATCH CENSUS API PULLER
Process all 155 sites in batches with progress tracking
"""

import pandas as pd
import requests
import time
import json
from datetime import datetime
from pathlib import Path

class BatchCensusAPIPuller:
    """Batch process Census API calls for all sites"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/data_intelligence/TDHCA_RAG")
        self.qct_dda_file = self.base_dir / "D'Marco_Sites/Analysis_Results/MASTER_155_BoostEligible_Sites_20250731_223500.xlsx"
        self.census_api_key = "06ece0121263282cd9ffd753215b007b8f9a3dfc"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Batch processing settings
        self.batch_size = 25
        self.batch_delay = 5  # seconds between batches
        self.call_delay = 0.5  # seconds between individual calls
        
    def get_acs_poverty_from_api(self, state_fips, county_fips, tract_fips):
        """Single API call to get ACS poverty data"""
        try:
            url = "https://api.census.gov/data/2022/acs/acs5"
            params = {
                'get': 'B17001_002E,B17001_001E',
                'for': f'tract:{tract_fips}',
                'in': f'state:{state_fips} county:{county_fips}',
                'key': self.census_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:
                    row = data[1]
                    poverty_count = float(row[0]) if row[0] not in ['-999999999', 'null'] else 0
                    total_pop = float(row[1]) if row[1] not in ['-999999999', 'null'] else 0
                    
                    if total_pop > 0:
                        poverty_rate = (poverty_count / total_pop) * 100
                        return {
                            'success': True,
                            'poverty_rate': round(poverty_rate, 2),
                            'poverty_count': int(poverty_count),
                            'total_population': int(total_pop)
                        }
                    else:
                        return {'success': False, 'error': 'No population data'}
                else:
                    return {'success': False, 'error': 'No data returned from API'}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_batch(self, sites_batch, batch_num, total_batches):
        """Process a batch of sites"""
        print(f"\n🔄 BATCH {batch_num}/{total_batches}: Processing {len(sites_batch)} sites")
        print("-" * 60)
        
        batch_results = []
        batch_successful = 0
        
        for i, (idx, site) in enumerate(sites_batch.iterrows()):
            address = site.get('Address', 'Unknown')
            final_tract = site.get('FINAL_TRACT')
            
            site_result = {
                'original_index': idx,
                'address': address,
                'final_tract': final_tract
            }
            
            print(f"  {i+1}/{len(sites_batch)}: {address[:50]}...")
            
            if final_tract and pd.notna(final_tract):
                # Extract FIPS components
                full_fips_str = str(int(final_tract))
                if len(full_fips_str) == 11:
                    state_fips = full_fips_str[:2]
                    county_fips = full_fips_str[2:5]
                    tract_fips = full_fips_str[5:]
                    
                    # Call Census API
                    api_result = self.get_acs_poverty_from_api(state_fips, county_fips, tract_fips)
                    
                    if api_result['success']:
                        site_result.update({
                            'api_status': 'SUCCESS',
                            'poverty_rate': api_result['poverty_rate'],
                            'poverty_count': api_result['poverty_count'],
                            'total_population': api_result['total_population'],
                            'state_fips': state_fips,
                            'county_fips': county_fips,
                            'tract_fips': tract_fips
                        })
                        batch_successful += 1
                        print(f"    ✅ {api_result['poverty_rate']}% poverty")
                    else:
                        site_result.update({
                            'api_status': 'FAILED',
                            'error': api_result['error']
                        })
                        print(f"    ❌ {api_result['error']}")
                else:
                    site_result.update({
                        'api_status': 'FIPS_ERROR',
                        'error': f'Invalid FIPS length: {len(full_fips_str)}'
                    })
                    print(f"    ❌ Invalid FIPS: {full_fips_str}")
            else:
                site_result.update({
                    'api_status': 'NO_TRACT',
                    'error': 'No FINAL_TRACT data'
                })
                print(f"    ❌ No census tract")
            
            batch_results.append(site_result)
            
            # Rate limiting between calls
            time.sleep(self.call_delay)
        
        print(f"  Batch complete: {batch_successful}/{len(sites_batch)} successful")
        return batch_results
    
    def process_all_sites_in_batches(self):
        """Process all 155 sites in batches"""
        print("🚀 BATCH CENSUS API PROCESSING")
        print("=" * 80)
        
        # Load sites
        try:
            qct_df = pd.read_excel(self.qct_dda_file)
            print(f"📊 Loaded {len(qct_df)} sites for batch processing")
        except Exception as e:
            print(f"❌ Failed to load sites: {e}")
            return None
        
        # Calculate batches
        total_sites = len(qct_df)
        num_batches = (total_sites + self.batch_size - 1) // self.batch_size
        
        print(f"🔢 Processing plan:")
        print(f"   Total sites: {total_sites}")
        print(f"   Batch size: {self.batch_size}")
        print(f"   Number of batches: {num_batches}")
        print(f"   Estimated time: {num_batches * (self.batch_size * self.call_delay + self.batch_delay) / 60:.1f} minutes")
        
        # Process in batches
        all_results = []
        total_successful = 0
        
        for batch_num in range(num_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min(start_idx + self.batch_size, total_sites)
            
            sites_batch = qct_df.iloc[start_idx:end_idx]
            
            batch_results = self.process_batch(sites_batch, batch_num + 1, num_batches)
            all_results.extend(batch_results)
            
            # Count successful in this batch
            batch_successful = sum(1 for r in batch_results if r.get('api_status') == 'SUCCESS')
            total_successful += batch_successful
            
            # Progress update
            processed_so_far = end_idx
            print(f"\n📊 PROGRESS UPDATE:")
            print(f"   Sites processed: {processed_so_far}/{total_sites} ({processed_so_far/total_sites*100:.1f}%)")
            print(f"   Total successful: {total_successful}")
            print(f"   Success rate: {total_successful/processed_so_far*100:.1f}%")
            
            # Delay between batches (except last batch)
            if batch_num < num_batches - 1:
                print(f"   ⏸️ Waiting {self.batch_delay} seconds before next batch...")
                time.sleep(self.batch_delay)
        
        print(f"\n🎯 BATCH PROCESSING COMPLETE!")
        print(f"   Total successful: {total_successful}/{total_sites} ({total_successful/total_sites*100:.1f}%)")
        
        return all_results, qct_df
    
    def integrate_api_results_with_sites(self, api_results, original_df):
        """Integrate API results back into original dataframe"""
        print("\n🔗 Integrating API results with original site data...")
        
        # Create results lookup by original index
        results_lookup = {r['original_index']: r for r in api_results}
        
        # Add Census API columns
        api_columns = [
            'Census_API_Poverty_Rate', 'Census_Poverty_Count', 'Census_Total_Population',
            'Census_State_FIPS', 'Census_County_FIPS', 'Census_Tract_FIPS',
            'Census_API_Status', 'Census_API_Error', 'Census_Data_Source'
        ]
        
        for col in api_columns:
            original_df[col] = 'MISSING'
        
        successful_integrations = 0
        
        for idx, site in original_df.iterrows():
            if idx in results_lookup:
                result = results_lookup[idx]
                
                if result.get('api_status') == 'SUCCESS':
                    original_df.loc[idx, 'Census_API_Poverty_Rate'] = result['poverty_rate']
                    original_df.loc[idx, 'Census_Poverty_Count'] = result['poverty_count']
                    original_df.loc[idx, 'Census_Total_Population'] = result['total_population']
                    original_df.loc[idx, 'Census_State_FIPS'] = result['state_fips']
                    original_df.loc[idx, 'Census_County_FIPS'] = result['county_fips']
                    original_df.loc[idx, 'Census_Tract_FIPS'] = result['tract_fips']
                    original_df.loc[idx, 'Census_API_Status'] = 'SUCCESS'
                    original_df.loc[idx, 'Census_API_Error'] = 'NONE'
                    original_df.loc[idx, 'Census_Data_Source'] = 'CENSUS_API_ACS_2022_5_YEAR'
                    successful_integrations += 1
                else:
                    original_df.loc[idx, 'Census_API_Status'] = result.get('api_status', 'UNKNOWN')
                    original_df.loc[idx, 'Census_API_Error'] = result.get('error', 'Unknown error')
        
        print(f"✅ Integrated {successful_integrations} successful API results")
        return original_df
    
    def save_batch_results(self, integrated_df, api_results):
        """Save batch processing results"""
        results_dir = self.base_dir / "D'Marco_Sites/Analysis_Results"
        
        excel_file = results_dir / f"BATCH_CENSUS_API_POVERTY_{self.timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main integrated results
            integrated_df.to_excel(writer, sheet_name='Sites_with_Census_API_Data', index=False)
            
            # Successful API pulls only
            successful_sites = integrated_df[integrated_df['Census_API_Status'] == 'SUCCESS']
            successful_sites.to_excel(writer, sheet_name='Successful_Census_API_Pulls', index=False)
            
            # API results summary
            api_df = pd.DataFrame(api_results)
            api_df.to_excel(writer, sheet_name='Raw_API_Results', index=False)
            
            # Status summary
            status_counts = integrated_df['Census_API_Status'].value_counts()
            summary_df = pd.DataFrame({'Status': status_counts.index, 'Count': status_counts.values})
            summary_df.to_excel(writer, sheet_name='API_Status_Summary', index=False)
        
        successful_count = (integrated_df['Census_API_Status'] == 'SUCCESS').sum()
        
        print(f"\n💾 BATCH CENSUS API RESULTS SAVED:")
        print(f"   📊 Excel: {excel_file.name}")
        print(f"   📈 Total sites: {len(integrated_df)}")
        print(f"   ✅ Successful API pulls: {successful_count}")
        print(f"   🎯 Success rate: {successful_count/len(integrated_df)*100:.1f}%")
        
        if successful_count > 0:
            rates = pd.to_numeric(successful_sites['Census_API_Poverty_Rate'], errors='coerce')
            unique_rates = rates.nunique()
            print(f"   📊 Poverty rates: {unique_rates} unique, {rates.min():.1f}% - {rates.max():.1f}%")
        
        return excel_file

def main():
    """Execute batch Census API processing"""
    print("🚀 BATCH CENSUS API POVERTY PULLER")
    print("🎯 OBJECTIVE: Get REAL ACS poverty data for ALL 155 sites")
    print("⚡ METHOD: Batch processing with rate limiting")
    
    puller = BatchCensusAPIPuller()
    
    # Process all sites in batches
    api_results, original_df = puller.process_all_sites_in_batches()
    
    if not api_results:
        print("❌ Batch processing failed")
        return
    
    # Integrate results
    integrated_df = puller.integrate_api_results_with_sites(api_results, original_df)
    
    # Save results  
    excel_file = puller.save_batch_results(integrated_df, api_results)
    
    print(f"\n✅ BATCH CENSUS API PROCESSING COMPLETE")
    print(f"📁 Results: {excel_file.name}")
    print(f"\n🚀 ALL 155 SITES NOW HAVE REAL OR FLAGGED POVERTY DATA")

if __name__ == "__main__":
    main()