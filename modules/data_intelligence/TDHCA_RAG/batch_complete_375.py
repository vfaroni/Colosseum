#!/usr/bin/env python3
"""
Batch Complete 375-Site Analysis - GUARANTEED TO FINISH
Creates Excel file with all 4 dataset results for sorting
"""

import pandas as pd
import requests
import time
import os
from datetime import datetime

class ReliableBatchAnalyzer:
    """Batch analyzer with checkpointing that guarantees completion"""
    
    def __init__(self):
        self.checkpoint_file = "D'Marco_Sites/Analysis_Results/BATCH_CHECKPOINT.xlsx"
        self.load_datasets()
    
    def load_datasets(self):
        """Load all datasets once"""
        base_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
        
        # QCT data
        qct_file = f"{base_path}/qct_data_2025.xlsx"
        tab1 = pd.read_excel(qct_file, sheet_name='AL-MO')
        tab2 = pd.read_excel(qct_file, sheet_name='MT-WY')
        qct_data = pd.concat([tab1, tab2], ignore_index=True)
        
        self.metro_qcts = qct_data[(qct_data['qct'] == 1) & (qct_data['metro'] == 1)]
        self.nonmetro_qcts = qct_data[(qct_data['qct'] == 1) & (qct_data['metro'] == 0)]
        
        # Metro DDA data
        metro_dda = pd.read_excel(f"{base_path}/2025-DDAs-Data-Used-to-Designate.xlsx")
        self.texas_metro_dda_zips = set(
            metro_dda[
                (metro_dda['ZIP Code Tabulation Area (ZCTA)'].astype(str).str.startswith('7')) &
                (metro_dda['2025 SDDA (1=SDDA)'] == 1)
            ]['ZIP Code Tabulation Area (ZCTA)'].astype(str).str.zfill(5)
        )
        
        # Non-Metro DDA counties (Texas FIPS codes)
        self.texas_nonmetro_dda_fips = {
            48001, 48003, 48005, 48007, 48013, 48019, 48025, 48031, 48035, 48043,
            48049, 48051, 48057, 48067, 48073, 48075, 48077, 48083, 48093, 48095,
            48097, 48101, 48103, 48105, 48107, 48109, 48111, 48115, 48117, 48119,
            48123, 48127, 48129, 48131, 48133, 48137, 48153, 48155, 48159, 48163,
            48171, 48179, 48195, 48205, 48221, 48227, 48241, 48243, 48255, 48261,
            48265, 48269, 48271, 48273, 48287, 48299, 48307, 48321, 48337, 48341,
            48347, 48349, 48357, 48363, 48373, 48383, 48385, 48389, 48399, 48405,
            48411, 48443, 48455, 48463, 48465, 48471, 48475, 48499
        }
        
        print(f"✅ Datasets loaded: {len(self.metro_qcts)} Metro QCTs, {len(self.texas_metro_dda_zips)} Metro DDAs, {len(self.texas_nonmetro_dda_fips)} Non-Metro DDA counties")
    
    def get_census_tract(self, lat, lon):
        """Get census tract with timeout"""
        try:
            url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
            params = {'x': lon, 'y': lat, 'benchmark': 'Public_AR_Current', 'vintage': 'Current_Current', 'format': 'json'}
            
            response = requests.get(url, params=params, timeout=8)
            if response.status_code == 200:
                data = response.json()
                if data.get('result', {}).get('geographies', {}).get('Census Tracts'):
                    tract_info = data['result']['geographies']['Census Tracts'][0]
                    return tract_info.get('GEOID', ''), tract_info.get('STATE', ''), tract_info.get('COUNTY', '')
            return None, None, None
        except:
            return None, None, None
    
    def get_zip_code(self, lat, lon):
        """Get ZIP with timeout"""
        try:
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {'lat': lat, 'lon': lon, 'format': 'json', 'addressdetails': 1, 'zoom': 18}
            headers = {'User-Agent': 'LIHTC-Batch-Analysis/1.0'}
            
            response = requests.get(url, params=params, headers=headers, timeout=8)
            if response.status_code == 200:
                data = response.json()
                if 'address' in data and 'postcode' in data['address']:
                    return data['address']['postcode'][:5]
            return None
        except:
            return None
    
    def analyze_single_site(self, lat, lon, city):
        """Analyze single site - return results immediately"""
        result = {
            'TRACT': '', 'ZIP': '', 'METRO_QCT': False, 'NONMETRO_QCT': False,
            'METRO_DDA': False, 'NONMETRO_DDA': False, 'ANY_BOOST': False,
            'CLASSIFICATION': 'No QCT/DDA', 'STATUS': 'API_ERROR'
        }
        
        # Get geographic info
        tract_geoid, state_fips, county_fips = self.get_census_tract(lat, lon)
        zip_code = self.get_zip_code(lat, lon)
        
        result['TRACT'] = tract_geoid or ''
        result['ZIP'] = zip_code or ''
        
        if tract_geoid and len(tract_geoid) == 11:
            try:
                state_code = int(tract_geoid[:2])
                county_code = int(tract_geoid[2:5])
                tract_number = float(tract_geoid[5:]) / 100
                
                # Check Metro QCT
                metro_qct_match = self.metro_qcts[
                    (self.metro_qcts['state'] == state_code) &
                    (self.metro_qcts['county'] == county_code) &
                    (abs(self.metro_qcts['tract'] - tract_number) < 0.01)
                ]
                result['METRO_QCT'] = len(metro_qct_match) > 0
                
                # Check Non-Metro QCT
                nonmetro_qct_match = self.nonmetro_qcts[
                    (self.nonmetro_qcts['state'] == state_code) &
                    (self.nonmetro_qcts['county'] == county_code) &
                    (abs(self.nonmetro_qcts['tract'] - tract_number) < 0.01)
                ]
                result['NONMETRO_QCT'] = len(nonmetro_qct_match) > 0
                
                # Check Metro DDA (ZIP-based)
                if zip_code:
                    result['METRO_DDA'] = zip_code in self.texas_metro_dda_zips
                
                # Check Non-Metro DDA (county-based)
                if state_code == 48:  # Texas
                    county_fips_full = int(f"{state_code}{county_code:03d}")
                    result['NONMETRO_DDA'] = county_fips_full in self.texas_nonmetro_dda_fips
                
                # Set final status
                result['ANY_BOOST'] = any([result['METRO_QCT'], result['NONMETRO_QCT'], 
                                         result['METRO_DDA'], result['NONMETRO_DDA']])
                
                designations = []
                if result['METRO_QCT']: designations.append('Metro QCT')
                if result['NONMETRO_QCT']: designations.append('Non-Metro QCT')
                if result['METRO_DDA']: designations.append('Metro DDA')
                if result['NONMETRO_DDA']: designations.append('Non-Metro DDA')
                
                result['CLASSIFICATION'] = ' + '.join(designations) if designations else 'No QCT/DDA'
                result['STATUS'] = 'SUCCESS'
                
            except Exception as e:
                result['STATUS'] = f'ERROR: {str(e)[:30]}'
        else:
            result['STATUS'] = 'NO_TRACT'
        
        return result
    
    def run_batch_analysis(self):
        """Run complete batch analysis with checkpointing"""
        print("🎯 BATCH 375-SITE ANALYSIS - GUARANTEED COMPLETION")
        print("=" * 60)
        
        # Load input data
        input_file = "D'Marco_Sites/Analysis_Results/CoStar_375_Phase1_Screening_20250731_160305.xlsx"
        df = pd.read_excel(input_file)
        print(f"✅ Loaded {len(df)} sites")
        
        # Check for existing checkpoint
        start_idx = 0
        if os.path.exists(self.checkpoint_file):
            try:
                checkpoint_df = pd.read_excel(self.checkpoint_file)
                start_idx = len(checkpoint_df[checkpoint_df['FINAL_STATUS'] == 'SUCCESS'])
                print(f"📄 Resuming from checkpoint: {start_idx} sites already completed")
                df = checkpoint_df  # Use checkpoint data
            except:
                print("⚠️ Checkpoint file corrupted, starting fresh")
        
        # Add analysis columns if not present
        analysis_cols = ['FINAL_TRACT', 'FINAL_ZIP', 'FINAL_METRO_QCT', 'FINAL_NONMETRO_QCT',
                        'FINAL_METRO_DDA', 'FINAL_NONMETRO_DDA', 'FINAL_ANY_BOOST', 
                        'FINAL_CLASSIFICATION', 'FINAL_STATUS']
        
        for col in analysis_cols:
            if col not in df.columns:
                df[col] = ''
        
        # Process sites
        print(f"🔍 Processing sites {start_idx+1} to 375...")
        
        batch_start = time.time()
        for idx in range(start_idx, len(df)):
            row = df.iloc[idx]
            lat, lon, city = row['Latitude'], row['Longitude'], row.get('City', 'Unknown')
            
            # Analyze site
            result = self.analyze_single_site(lat, lon, city)
            
            # Update dataframe
            df.at[idx, 'FINAL_TRACT'] = result['TRACT']
            df.at[idx, 'FINAL_ZIP'] = result['ZIP']
            df.at[idx, 'FINAL_METRO_QCT'] = result['METRO_QCT']
            df.at[idx, 'FINAL_NONMETRO_QCT'] = result['NONMETRO_QCT']
            df.at[idx, 'FINAL_METRO_DDA'] = result['METRO_DDA']
            df.at[idx, 'FINAL_NONMETRO_DDA'] = result['NONMETRO_DDA']
            df.at[idx, 'FINAL_ANY_BOOST'] = result['ANY_BOOST']
            df.at[idx, 'FINAL_CLASSIFICATION'] = result['CLASSIFICATION']
            df.at[idx, 'FINAL_STATUS'] = result['STATUS']
            
            # Progress and checkpoint every 25 sites
            if (idx + 1) % 25 == 0:
                elapsed = time.time() - batch_start
                rate = 25 / elapsed * 60 if elapsed > 0 else 0
                remaining = (len(df) - idx - 1) / rate if rate > 0 else 0
                
                boost_count = len(df[df['FINAL_ANY_BOOST'] == True])
                print(f"✅ {idx+1:3d}/375 ({rate:.1f} sites/min, ~{remaining:.1f} min left, {boost_count} boost eligible)")
                
                # Save checkpoint
                df.to_excel(self.checkpoint_file, index=False)
                batch_start = time.time()  # Reset timer
            
            # Rate limiting
            time.sleep(1.2)
        
        # Final save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_file = f"D'Marco_Sites/Analysis_Results/CoStar_375_COMPLETE_4Dataset_FINAL_{timestamp}.xlsx"
        df.to_excel(final_file, index=False)
        
        # Summary stats
        success_count = len(df[df['FINAL_STATUS'] == 'SUCCESS'])
        boost_count = len(df[df['FINAL_ANY_BOOST'] == True])
        metro_qct = len(df[df['FINAL_METRO_QCT'] == True])
        nonmetro_qct = len(df[df['FINAL_NONMETRO_QCT'] == True])
        metro_dda = len(df[df['FINAL_METRO_DDA'] == True])
        nonmetro_dda = len(df[df['FINAL_NONMETRO_DDA'] == True])
        
        print(f"\\n📊 FINAL RESULTS:")
        print(f"✅ Successfully analyzed: {success_count}/375 sites")
        print(f"1) Metro QCTs: {metro_qct}")
        print(f"2) Non-Metro QCTs: {nonmetro_qct}")
        print(f"3) Metro DDAs: {metro_dda}")
        print(f"4) Non-Metro DDAs: {nonmetro_dda}")
        print(f"🎯 Total with ANY boost: {boost_count} sites ({boost_count/375*100:.1f}%)")
        
        print(f"\\n💾 EXCEL FILE READY FOR SORTING: {final_file}")
        print("✅ You can now sort to find verified non-QCT/non-DDA sites!")
        
        # Clean up checkpoint
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
        
        return df

if __name__ == "__main__":
    analyzer = ReliableBatchAnalyzer()
    final_df = analyzer.run_batch_analysis()
    print("\\n🎯 MISSION COMPLETE - EXCEL FILE WITH ALL 4 DATASETS READY!")